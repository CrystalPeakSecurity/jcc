#!/usr/bin/env python3
"""
Analyze JCA file for optimization opportunities.
"""

import re
from collections import defaultdict
from pathlib import Path


def parse_jca(jca_path):
    """Parse JCA file and extract method statistics."""

    methods = []
    current_method = None
    instruction_count = 0
    instructions = []
    in_method = False

    with open(jca_path, "r") as f:
        for line in f:
            line = line.rstrip()

            # Method definition: .method <flags> <name>(<sig>)<ret>
            if ".method " in line:
                if current_method is not None:
                    # Save previous method
                    methods.append(
                        {
                            "name": current_method,
                            "instruction_count": instruction_count,
                            "instructions": instructions.copy(),
                        }
                    )

                # Extract method name from line like ".method private static finesine(S)I {"
                # or "\t\t.method private static finesine(S)I {"
                parts = line.strip().split()
                method_sig = None
                for part in parts:
                    if "(" in part:
                        method_sig = part
                        break

                if method_sig:
                    current_method = method_sig.split("(")[0]
                else:
                    current_method = "unknown"

                instruction_count = 0
                instructions = []
                in_method = True

            elif in_method and line.strip() == "}":
                # End of method
                if current_method is not None:
                    methods.append(
                        {
                            "name": current_method,
                            "instruction_count": instruction_count,
                            "instructions": instructions.copy(),
                        }
                    )
                    current_method = None
                    instruction_count = 0
                    instructions = []
                    in_method = False

            elif in_method and current_method is not None:
                stripped = line.strip()
                # Skip blank lines, labels (end with :), directives (start with .)
                # and opening braces
                if stripped and not stripped.startswith(".") and not stripped.endswith(":") and stripped != "{":
                    # Extract instruction (first token before any comment or semicolon)
                    instr = stripped.split(";")[0].strip()
                    if instr:
                        instruction_count += 1
                        instructions.append(instr)

    return methods


def analyze_redundant_ops(instructions):
    """Find redundant push/pop and load/store patterns."""
    patterns = {
        "push_pop": 0,
        "dup_pop": 0,
        "load_store_same": 0,
        "redundant_conversion": 0,
    }

    for i in range(len(instructions) - 1):
        curr = instructions[i].strip()
        next_instr = instructions[i + 1].strip() if i + 1 < len(instructions) else ""

        # Push followed by pop
        if curr.startswith("s") and curr.endswith("push") and next_instr == "pop":
            patterns["push_pop"] += 1

        # Dup followed by pop
        if curr == "dup" and next_instr == "pop":
            patterns["dup_pop"] += 1

        # Load followed by store to same location
        if curr.startswith("sload") and next_instr.startswith("sstore"):
            curr_idx = curr.split("_")[-1] if "_" in curr else curr.split()[-1] if " " in curr else ""
            next_idx = (
                next_instr.split("_")[-1] if "_" in next_instr else next_instr.split()[-1] if " " in next_instr else ""
            )
            if curr_idx == next_idx:
                patterns["load_store_same"] += 1

        # s2i followed by i2s or vice versa
        if (curr == "s2i" and next_instr == "i2s") or (curr == "i2s" and next_instr == "s2i"):
            patterns["redundant_conversion"] += 1

    return patterns


def analyze_arithmetic(instructions):
    """Find inefficient arithmetic patterns."""
    patterns = {
        "mul_by_power_of_2": 0,
        "div_by_power_of_2": 0,
        "add_zero": 0,
        "mul_one": 0,
    }

    for i, instr in enumerate(instructions):
        instr = instr.strip()

        # Look for constant multiplication by power of 2
        if instr in ["smul", "imul"] and i > 0:
            prev = instructions[i - 1].strip()
            if prev.startswith("sconst") or prev.startswith("iconst"):
                # Extract constant value
                match = re.search(r"const[_\s]+(\d+)", prev)
                if match:
                    val = int(match.group(1))
                    if val > 0 and (val & (val - 1)) == 0:  # Power of 2
                        patterns["mul_by_power_of_2"] += 1

        # Look for constant division by power of 2
        if instr in ["sdiv", "idiv"] and i > 0:
            prev = instructions[i - 1].strip()
            if prev.startswith("sconst") or prev.startswith("iconst"):
                match = re.search(r"const[_\s]+(\d+)", prev)
                if match:
                    val = int(match.group(1))
                    if val > 0 and (val & (val - 1)) == 0:  # Power of 2
                        patterns["div_by_power_of_2"] += 1

        # Add zero
        if instr in ["sadd", "iadd"] and i > 0:
            prev = instructions[i - 1].strip()
            if "const_0" in prev or prev.endswith("const 0"):
                patterns["add_zero"] += 1

        # Multiply by one
        if instr in ["smul", "imul"] and i > 0:
            prev = instructions[i - 1].strip()
            if "const_1" in prev or prev.endswith("const 1"):
                patterns["mul_one"] += 1

    return patterns


def count_method_calls(instructions):
    """Count invokestatic/invokevirtual calls."""
    static_calls = 0
    virtual_calls = 0

    for instr in instructions:
        if "invokestatic" in instr:
            static_calls += 1
        elif "invokevirtual" in instr:
            virtual_calls += 1

    return static_calls, virtual_calls


def main():
    jca_path = Path(__file__).parent.parent / "build" / "applet.jca"

    if not jca_path.exists():
        print(f"Error: {jca_path} not found. Run 'just compile' first.")
        return

    print(f"Analyzing {jca_path}...")
    print(f"File size: {jca_path.stat().st_size / 1024:.1f} KB\n")

    methods = parse_jca(jca_path)

    # Sort by instruction count
    methods_sorted = sorted(methods, key=lambda m: m["instruction_count"], reverse=True)

    print("=" * 80)
    print("TOP 10 MOST INSTRUCTION-HEAVY FUNCTIONS")
    print("=" * 80)

    for i, method in enumerate(methods_sorted[:10], 1):
        name = method["name"]
        count = method["instruction_count"]
        instructions = method["instructions"]

        # Analyze patterns
        redundant = analyze_redundant_ops(instructions)
        arithmetic = analyze_arithmetic(instructions)
        static_calls, virtual_calls = count_method_calls(instructions)

        print(f"\n{i}. {name}")
        print(f"   Instructions: {count}")
        print(f"   Method calls: {static_calls} static, {virtual_calls} virtual")

        if any(redundant.values()):
            print(f"   Redundant ops: {dict(redundant)}")

        if any(arithmetic.values()):
            print(f"   Inefficient arithmetic: {dict(arithmetic)}")

    print("\n" + "=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)

    total_instructions = sum(m["instruction_count"] for m in methods)
    total_methods = len(methods)

    print(f"Total methods: {total_methods}")
    print(f"Total instructions: {total_instructions}")
    if total_methods > 0:
        print(f"Average instructions per method: {total_instructions / total_methods:.1f}")
    else:
        print("No methods found!")

    # Aggregate patterns
    all_redundant = defaultdict(int)
    all_arithmetic = defaultdict(int)
    total_static_calls = 0
    total_virtual_calls = 0

    for method in methods:
        redundant = analyze_redundant_ops(method["instructions"])
        arithmetic = analyze_arithmetic(method["instructions"])
        static_calls, virtual_calls = count_method_calls(method["instructions"])

        for k, v in redundant.items():
            all_redundant[k] += v
        for k, v in arithmetic.items():
            all_arithmetic[k] += v

        total_static_calls += static_calls
        total_virtual_calls += virtual_calls

    print(f"\nTotal method calls: {total_static_calls} static, {total_virtual_calls} virtual")
    print(f"\nRedundant operations found:")
    for pattern, count in all_redundant.items():
        if count > 0:
            print(f"  {pattern}: {count}")

    print(f"\nInefficient arithmetic patterns:")
    for pattern, count in all_arithmetic.items():
        if count > 0:
            print(f"  {pattern}: {count}")

    # Find methods with high call density
    print("\n" + "=" * 80)
    print("METHODS WITH HIGH CALL DENSITY (>30% calls)")
    print("=" * 80)

    high_call_methods = []
    for method in methods:
        if method["instruction_count"] > 20:  # Only consider non-trivial methods
            static_calls, virtual_calls = count_method_calls(method["instructions"])
            total_calls = static_calls + virtual_calls
            call_ratio = total_calls / method["instruction_count"]

            if call_ratio > 0.3:
                high_call_methods.append((method["name"], method["instruction_count"], total_calls, call_ratio))

    high_call_methods.sort(key=lambda x: x[3], reverse=True)

    for name, instr_count, calls, ratio in high_call_methods[:10]:
        print(f"{name:40s} {instr_count:4d} instructions, {calls:3d} calls ({ratio * 100:.1f}%)")

    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. INLINE CANDIDATES: Methods with high call density could benefit from inlining
   their helper functions to reduce call overhead.

2. ARITHMETIC OPTIMIZATION: Use shift operations instead of multiplication/division
   by powers of 2 (compiler should handle this, but verify).

3. REDUNDANT OPERATIONS: Review push/pop and conversion patterns - these suggest
   unnecessary type coercion or temporary value handling.

4. CALL OVERHEAD: JavaCard method calls are expensive. Consider:
   - Inlining small utility functions
   - Using macros for simple calculations
   - Batching operations to reduce call depth

5. STACK OPERATIONS: Excessive dup/pop suggests inefficient value reuse patterns.
   Consider restructuring to keep values on stack when needed multiple times.
""")


if __name__ == "__main__":
    main()
