#!/usr/bin/env python3
"""Analyze JCA output for stack depth — detect potential JCVM stack overflows.

Parses method declarations (.stack, .locals) and invokestatic calls from JCA,
builds a call graph, and computes the maximum stack depth from the entry point.

JCVM stack model:
- Each method frame = .locals (params + local variables) + .stack (operand stack)
- At a call site, the caller's operand stack holds arguments (popped by callee)
- Total stack depth along a call chain = sum of .locals along path) + leaf .stack

Usage:
    python tools/stack_analysis.py <path/to/Applet.jca> [--limit N]
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Method:
    name: str
    locals: int
    stack: int
    callees: set[str] = field(default_factory=set)

    @property
    def total(self) -> int:
        return self.locals + self.stack


def parse_jca(jca_path: Path) -> dict[str, Method]:
    """Parse JCA file line-by-line, return dict of method name -> Method."""
    lines = jca_path.read_text().splitlines()

    # Step 1: Build constant pool index -> user method name mapping
    cp_to_name: dict[int, str] = {}
    for line in lines:
        m = re.match(r"\s*//\s*(\d+)\s*//\s*user:(\w+)", line)
        if m:
            cp_to_name[int(m.group(1))] = m.group(2)

    # Step 2: Parse methods by tracking state
    methods: dict[str, Method] = {}
    current_name: str | None = None
    current_stack = 0
    current_locals = 0
    current_callees: set[str] = set()
    brace_depth = 0
    in_method = False

    for line in lines:
        stripped = line.strip()

        # Detect method start
        mm = re.match(r"\.method\s+.+\s+(\w+)\(", stripped)
        if mm and "{" in stripped:
            # Save previous method if any
            if in_method and current_name:
                methods[current_name] = Method(
                    name=current_name,
                    locals=current_locals,
                    stack=current_stack,
                    callees=current_callees,
                )

            current_name = mm.group(1)
            current_stack = 0
            current_locals = 0
            current_callees = set()
            in_method = True
            brace_depth = 1
            continue

        if not in_method:
            continue

        # Track braces for method end
        brace_depth += stripped.count("{") - stripped.count("}")
        if brace_depth <= 0:
            # Method ended
            if current_name:
                methods[current_name] = Method(
                    name=current_name,
                    locals=current_locals,
                    stack=current_stack,
                    callees=current_callees,
                )
            in_method = False
            current_name = None
            continue

        # Parse .stack
        sm = re.match(r"\.stack\s+(\d+)", stripped)
        if sm:
            current_stack = int(sm.group(1))

        # Parse .locals
        lm = re.match(r"\.locals\s+(\d+)", stripped)
        if lm:
            current_locals = int(lm.group(1))

        # Parse invokestatic
        im = re.match(r"invokestatic\s+(\d+)", stripped)
        if im:
            cp_idx = int(im.group(1))
            if cp_idx in cp_to_name:
                current_callees.add(cp_to_name[cp_idx])

    # Save last method
    if in_method and current_name:
        methods[current_name] = Method(
            name=current_name,
            locals=current_locals,
            stack=current_stack,
            callees=current_callees,
        )

    return methods


def find_max_depth(
    methods: dict[str, Method], entry: str
) -> tuple[int, list[str]]:
    """Compute max stack depth from entry point.

    Returns (depth, path) where depth = sum(.locals along path) + leaf .stack.
    """
    memo: dict[str, tuple[int, list[str]]] = {}
    in_progress: set[str] = set()  # cycle detection

    def compute(name: str) -> tuple[int, list[str]]:
        if name not in methods:
            return 0, []
        if name in memo:
            return memo[name]
        if name in in_progress:
            return 0, []  # cycle — break it

        in_progress.add(name)
        method = methods[name]

        # Find deepest callee path
        max_callee_depth = 0
        max_callee_path: list[str] = []

        for callee in sorted(method.callees):
            d, p = compute(callee)
            if d > max_callee_depth:
                max_callee_depth = d
                max_callee_path = p

        if not max_callee_path:
            # Leaf: locals + stack
            result = (method.locals + method.stack, [name])
        else:
            # Non-leaf: locals + deepest callee (callee includes leaf stack)
            result = (method.locals + max_callee_depth, [name] + max_callee_path)

        in_progress.discard(name)
        memo[name] = result
        return result

    return compute(entry)


def main():
    limit = 64
    args = sys.argv[1:]

    if not args:
        print("Usage: python tools/stack_analysis.py <Applet.jca> [--limit N]")
        sys.exit(1)

    jca_path = Path(args[0])
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])

    methods = parse_jca(jca_path)
    print(f"Parsed {len(methods)} methods\n")

    # Find entry point — try userProcess first (jcc wraps process() as userProcess)
    entry = "userProcess"
    if entry not in methods:
        entry = "process"
    if entry not in methods:
        print("No entry point found (tried 'userProcess', 'process')")
        sys.exit(1)

    depth, path = find_max_depth(methods, entry)

    status = "OK" if depth <= limit else "OVERFLOW"
    pct = depth / limit * 100

    print(f"Max stack depth: {depth}/{limit} slots ({pct:.0f}%) [{status}]")
    print(f"Deepest call chain ({len(path)} functions):\n")

    # Show breakdown
    cumulative = 0
    for i, name in enumerate(path):
        m = methods[name]
        is_leaf = i == len(path) - 1
        if is_leaf:
            frame = m.locals + m.stack
            detail = f".locals={m.locals} + .stack={m.stack}"
        else:
            frame = m.locals
            detail = f".locals={m.locals} (stack={m.stack})"
        cumulative += frame
        print(f"  {i + 1:2}. {name:40s} {frame:3d} slots  cumul={cumulative:3d}  ({detail})")

    # Show top functions by frame size
    print(f"\nTop 15 functions by total frame size (.locals + .stack):")
    ranked = sorted(methods.values(), key=lambda m: m.total, reverse=True)
    for i, m in enumerate(ranked[:15]):
        in_path = "*" if m.name in path else " "
        print(f"  {in_path} {m.name:40s} {m.total:3d} (.locals={m.locals}, .stack={m.stack})")


if __name__ == "__main__":
    main()
