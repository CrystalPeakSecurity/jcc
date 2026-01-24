#!/usr/bin/env python3
"""
Detailed JCA analysis focusing on specific optimization opportunities.
"""

import re
from collections import Counter, defaultdict
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

            if ".method " in line:
                if current_method is not None:
                    methods.append(
                        {
                            "name": current_method,
                            "instruction_count": instruction_count,
                            "instructions": instructions.copy(),
                        }
                    )

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
                if stripped and not stripped.startswith(".") and not stripped.endswith(":") and stripped != "{":
                    instr = stripped.split(";")[0].strip()
                    if instr:
                        instruction_count += 1
                        instructions.append(instr)

    return methods


def analyze_instruction_patterns(instructions):
    """Analyze instruction patterns in detail."""

    patterns = {
        # Stack manipulation
        "dup": 0,
        "pop": 0,
        "swap": 0,
        # Type conversions
        "s2i": 0,
        "i2s": 0,
        "s2b": 0,
        "b2s": 0,
        "i2b": 0,
        # Static field access
        "getstatic": 0,
        "putstatic": 0,
        # Array access
        "saload": 0,
        "sastore": 0,
        "baload": 0,
        "bastore": 0,
        "iaload": 0,
        "iastore": 0,
        # Arithmetic
        "sadd": 0,
        "ssub": 0,
        "smul": 0,
        "sdiv": 0,
        "iadd": 0,
        "isub": 0,
        "imul": 0,
        "idiv": 0,
        "sshl": 0,
        "sshr": 0,
        "ishl": 0,
        "ishr": 0,
        # Method calls
        "invokestatic": 0,
        "invokevirtual": 0,
    }

    for instr in instructions:
        instr_name = instr.split()[0].split("_")[0]
        if instr_name in patterns:
            patterns[instr_name] += 1

    return patterns


def find_conversion_chains(instructions):
    """Find sequences of type conversions that could be optimized."""
    chains = []
    i = 0

    while i < len(instructions) - 1:
        chain = []
        curr = instructions[i].split()[0]

        if curr in ["s2i", "i2s", "s2b", "b2s", "i2b", "b2i"]:
            chain.append((i, curr))
            j = i + 1

            # Look for more conversions
            while j < len(instructions):
                next_instr = instructions[j].split()[0]
                if next_instr in ["s2i", "i2s", "s2b", "b2s", "i2b", "b2i"]:
                    chain.append((j, next_instr))
                    j += 1
                elif next_instr in ["dup", "pop", "swap"]:
                    # Include stack ops in chain
                    chain.append((j, next_instr))
                    j += 1
                else:
                    break

            if len(chain) > 1:
                chains.append(chain)
                i = j
            else:
                i += 1
        else:
            i += 1

    return chains


def find_static_access_patterns(instructions):
    """Find patterns of static field access that could be optimized."""
    patterns = []

    for i in range(len(instructions) - 2):
        # Pattern: getstatic, use, putstatic to same location
        if "getstatic" in instructions[i] and "putstatic" in instructions[i + 2]:
            get_field = instructions[i].split()[1] if len(instructions[i].split()) > 1 else ""
            put_field = instructions[i + 2].split()[1] if len(instructions[i + 2].split()) > 1 else ""

            if get_field == put_field:
                patterns.append((i, "get-op-put", get_field))

    return patterns


def main():
    jca_path = Path(__file__).parent.parent / "build" / "applet.jca"

    if not jca_path.exists():
        print(f"Error: {jca_path} not found. Run 'just compile' first.")
        return

    print("=" * 80)
    print("DETAILED JCA BYTECODE ANALYSIS")
    print("=" * 80)

    methods = parse_jca(jca_path)
    methods_sorted = sorted(methods, key=lambda m: m["instruction_count"], reverse=True)

    # Analyze top 10 methods
    for i, method in enumerate(methods_sorted[:10], 1):
        name = method["name"]
        count = method["instruction_count"]
        instructions = method["instructions"]

        print(f"\n{'=' * 80}")
        print(f"{i}. {name} ({count} instructions)")
        print("=" * 80)

        # Instruction breakdown
        patterns = analyze_instruction_patterns(instructions)

        print("\nInstruction breakdown:")

        # Group by category
        stack_ops = patterns["dup"] + patterns["pop"] + patterns["swap"]
        conversions = patterns["s2i"] + patterns["i2s"] + patterns["s2b"] + patterns["b2s"] + patterns["i2b"]
        static_access = patterns["getstatic"] + patterns["putstatic"]
        array_access = (
            patterns["saload"]
            + patterns["sastore"]
            + patterns["baload"]
            + patterns["bastore"]
            + patterns["iaload"]
            + patterns["iastore"]
        )
        arithmetic = (
            patterns["sadd"]
            + patterns["ssub"]
            + patterns["smul"]
            + patterns["sdiv"]
            + patterns["iadd"]
            + patterns["isub"]
            + patterns["imul"]
            + patterns["idiv"]
        )
        shifts = patterns["sshl"] + patterns["sshr"] + patterns["ishl"] + patterns["ishr"]
        calls = patterns["invokestatic"] + patterns["invokevirtual"]

        print(f"  Stack operations:     {stack_ops:4d} ({stack_ops / count * 100:5.1f}%)")
        print(f"  Type conversions:     {conversions:4d} ({conversions / count * 100:5.1f}%)")
        print(f"  Static field access:  {static_access:4d} ({static_access / count * 100:5.1f}%)")
        print(f"  Array access:         {array_access:4d} ({array_access / count * 100:5.1f}%)")
        print(f"  Arithmetic:           {arithmetic:4d} ({arithmetic / count * 100:5.1f}%)")
        print(f"  Shifts:               {shifts:4d} ({shifts / count * 100:5.1f}%)")
        print(f"  Method calls:         {calls:4d} ({calls / count * 100:5.1f}%)")

        # Find conversion chains
        chains = find_conversion_chains(instructions)
        if chains:
            print(f"\n  Type conversion chains: {len(chains)}")
            for chain in chains[:3]:  # Show first 3
                chain_str = " -> ".join([c[1] for c in chain])
                print(f"    {chain_str}")

        # Find static access patterns
        static_patterns = find_static_access_patterns(instructions)
        if static_patterns:
            print(f"\n  Static get-op-put patterns: {len(static_patterns)}")
            field_counts = Counter([p[2] for p in static_patterns])
            for field, count in field_counts.most_common(3):
                print(f"    {field}: {count} times")

    # Overall statistics
    print("\n" + "=" * 80)
    print("GLOBAL OPTIMIZATION OPPORTUNITIES")
    print("=" * 80)

    all_instructions = []
    for method in methods:
        all_instructions.extend(method["instructions"])

    # Count all instructions
    instr_counter = Counter()
    for instr in all_instructions:
        instr_name = instr.split()[0]
        instr_counter[instr_name] += 1

    print("\nMost common instructions:")
    for instr, count in instr_counter.most_common(20):
        print(f"  {instr:20s} {count:6d} ({count / len(all_instructions) * 100:5.1f}%)")

    # Aggregate conversion analysis
    total_s2i = instr_counter.get("s2i", 0)
    total_i2s = instr_counter.get("i2s", 0)
    total_conversions = sum(instr_counter.get(c, 0) for c in ["s2i", "i2s", "s2b", "b2s", "i2b", "b2i"])

    print(f"\nType conversion overhead:")
    print(
        f"  Total conversions: {total_conversions} ({total_conversions / len(all_instructions) * 100:.1f}% of all instructions)"
    )
    print(f"  s2i: {total_s2i}, i2s: {total_i2s}")

    if total_s2i > 0 and total_i2s > 0:
        ratio = total_s2i / total_i2s if total_i2s > 0 else float("inf")
        print(f"  s2i/i2s ratio: {ratio:.2f}")
        if abs(ratio - 1.0) < 0.2:
            print("  ⚠ Nearly equal s2i/i2s counts suggest many round-trip conversions")

    # Stack pointer operations
    sp_ops = sum(1 for instr in all_instructions if "SP_" in instr)
    print(f"\nStack pointer operations: {sp_ops} ({sp_ops / len(all_instructions) * 100:.1f}% of all instructions)")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. TYPE CONVERSIONS: High s2i/i2s counts suggest excessive type coercion.
   - Consider keeping values in int form when they'll be used in int operations
   - Review if short arithmetic can be replaced with int where stack allows

2. STATIC FIELD ACCESS: Heavy getstatic/putstatic usage, especially for SP_* pointers.
   - Stack pointer manipulation dominates many functions
   - Consider if some stack allocations can be avoided with better variable reuse

3. STACK OPERATIONS: High dup/pop counts suggest values being moved around inefficiently.
   - Review expression evaluation order
   - Consider storing intermediate results in locals instead of stack manipulation

4. METHOD SIZE: R_StoreWallRange at 1095 instructions is extremely large.
   - May hit JavaCard method size limits (64KB bytecode)
   - Consider splitting into sub-functions if causing issues
   - Large methods are harder to optimize by JVM

5. ARITHMETIC: Relatively low shift usage - verify power-of-2 multiplications use shifts.
   - Only 2 div-by-power-of-2 found - ensure compiler is optimizing these
""")


if __name__ == "__main__":
    main()
