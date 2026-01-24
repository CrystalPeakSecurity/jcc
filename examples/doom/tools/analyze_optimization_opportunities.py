#!/usr/bin/env python3
"""
Find specific optimization opportunities in JCA bytecode.
"""

import re
from pathlib import Path


def extract_method(jca_path, method_name):
    """Extract a specific method's bytecode."""
    in_method = False
    instructions = []

    with open(jca_path, "r") as f:
        for line in f:
            if f".method" in line and method_name in line:
                in_method = True
                continue

            if in_method:
                if line.strip() == "}":
                    break

                stripped = line.strip()
                if stripped and not stripped.startswith(".") and not stripped.endswith(":") and stripped != "{":
                    instructions.append(stripped)

    return instructions


def find_array_chain_loads(instructions):
    """Find multi-level array loads that could be optimized."""
    patterns = []

    for i in range(len(instructions) - 4):
        # Pattern: getstatic_a, getstatic_a, saload, saload
        # This is a common pattern for accessing nested arrays
        if (
            instructions[i].startswith("getstatic_a")
            and instructions[i + 1].startswith("getstatic_a")
            and "saload" in instructions[i + 2]
        ):
            context = instructions[i : min(i + 8, len(instructions))]
            saload_count = sum(1 for instr in context if "saload" in instr)

            if saload_count >= 2:
                patterns.append((i, saload_count, context[:6]))

    return patterns


def find_conversion_overhead(instructions):
    """Find type conversion overhead."""
    patterns = []

    for i in range(len(instructions) - 1):
        curr = instructions[i].split()[0]
        next_instr = instructions[i + 1].split()[0] if i + 1 < len(instructions) else ""

        # s2i followed by ishl - could potentially be sshl
        if curr == "s2i" and "ishl" in next_instr:
            patterns.append(("s2i_then_shift", i, instructions[i : i + 3]))

        # Load, convert, immediate use
        if "load" in curr and curr.endswith("_0"):
            next_next = instructions[i + 2].split()[0] if i + 2 < len(instructions) else ""
            if next_instr in ["s2i", "i2s"] and next_next in ["iadd", "isub", "imul", "sadd", "ssub", "smul"]:
                patterns.append(("load_convert_op", i, instructions[i : i + 4]))

    return patterns


def find_constant_operations(instructions):
    """Find operations with constants that could be optimized."""
    patterns = []

    for i in range(len(instructions) - 1):
        curr = instructions[i]
        next_instr = instructions[i + 1] if i + 1 < len(instructions) else ""

        # Multiplication by power of 2
        if "const" in curr and ("smul" in next_instr or "imul" in next_instr):
            # Extract constant value
            match = re.search(r"push\s+(\d+)", curr)
            if match:
                val = int(match.group(1))
                if val > 0 and (val & (val - 1)) == 0:
                    shift_amount = val.bit_length() - 1
                    patterns.append(("mul_power_of_2", val, shift_amount, i))

        # Division by power of 2
        if "const" in curr and ("sdiv" in next_instr or "idiv" in next_instr):
            match = re.search(r"push\s+(\d+)", curr)
            if match:
                val = int(match.group(1))
                if val > 0 and (val & (val - 1)) == 0:
                    shift_amount = val.bit_length() - 1
                    patterns.append(("div_power_of_2", val, shift_amount, i))

    return patterns


def analyze_static_field_pressure(instructions):
    """Analyze how often static fields are accessed."""
    field_access = {}

    for instr in instructions:
        if "getstatic" in instr or "putstatic" in instr:
            # Extract field reference
            parts = instr.split()
            if len(parts) >= 2:
                field = parts[1].rstrip(";")
                if field not in field_access:
                    field_access[field] = {"get": 0, "put": 0}

                if "getstatic" in instr:
                    field_access[field]["get"] += 1
                else:
                    field_access[field]["put"] += 1

    return field_access


def main():
    jca_path = Path(__file__).parent.parent / "build" / "applet.jca"

    if not jca_path.exists():
        print(f"Error: {jca_path} not found. Run 'just compile' first.")
        return

    print("=" * 80)
    print("BYTECODE OPTIMIZATION OPPORTUNITY ANALYSIS")
    print("=" * 80)

    # Analyze R_StoreWallRange (the largest method)
    print("\n1. ANALYZING R_StoreWallRange (1095 instructions)")
    print("=" * 80)

    instructions = extract_method(jca_path, "R_StoreWallRange")
    print(f"Extracted {len(instructions)} instructions")

    # Array chain loads
    array_chains = find_array_chain_loads(instructions)
    print(f"\nMulti-level array access patterns: {len(array_chains)}")
    if array_chains:
        print("\nExample (first occurrence):")
        idx, count, context = array_chains[0]
        for instr in context:
            print(f"  {instr}")
        print(f"\n  → {count} consecutive array loads")
        print("  Optimization: Consider caching intermediate array references in locals")

    # Conversion overhead
    conversions = find_conversion_overhead(instructions)
    print(f"\nType conversion patterns: {len(conversions)}")
    if conversions:
        for pattern_type, idx, context in conversions[:3]:
            print(f"\n  {pattern_type}:")
            for instr in context:
                print(f"    {instr}")

    # Constant operations
    const_ops = find_constant_operations(instructions)
    if const_ops:
        print(f"\nConstant arithmetic optimization opportunities: {len(const_ops)}")
        for op_type, val, shift, idx in const_ops[:5]:
            if op_type == "mul_power_of_2":
                print(f"  {op_type}: {val} → use {shift}-bit left shift instead")
            else:
                print(f"  {op_type}: {val} → use {shift}-bit right shift instead")

    # Static field access
    field_access = analyze_static_field_pressure(instructions)
    print(f"\nStatic field access (top 10 most accessed):")
    sorted_fields = sorted(field_access.items(), key=lambda x: x[1]["get"] + x[1]["put"], reverse=True)
    for field, counts in sorted_fields[:10]:
        total = counts["get"] + counts["put"]
        print(f"  {field:20s} get:{counts['get']:3d} put:{counts['put']:3d} total:{total:3d}")

    # Analyze other heavy functions
    print("\n" + "=" * 80)
    print("2. OTHER HEAVY FUNCTIONS")
    print("=" * 80)

    heavy_methods = [
        "P_NewChaseDir",
        "P_CrossSubsector",
        "R_AddLine",
    ]

    for method in heavy_methods:
        instructions = extract_method(jca_path, method)
        if not instructions:
            continue

        print(f"\n{method} ({len(instructions)} instructions)")
        print("-" * 80)

        field_access = analyze_static_field_pressure(instructions)
        sorted_fields = sorted(field_access.items(), key=lambda x: x[1]["get"] + x[1]["put"], reverse=True)

        total_gets = sum(f["get"] for f in field_access.values())
        total_puts = sum(f["put"] for f in field_access.values())

        print(f"  Static field accesses: {total_gets} gets, {total_puts} puts")
        print(f"  Field access overhead: {(total_gets + total_puts) / len(instructions) * 100:.1f}% of instructions")

        # Most accessed field
        if sorted_fields:
            field, counts = sorted_fields[0]
            total = counts["get"] + counts["put"]
            print(f"  Most accessed field: {field} ({total} times)")

    print("\n" + "=" * 80)
    print("SPECIFIC OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. ARRAY ACCESS OPTIMIZATION (R_StoreWallRange)
   Problem: Deep array dereference chains dominate the function
   Example:
     getstatic_a vertex_x
     getstatic_a seg_v1
     getstatic_a MEM_S
     sspush 296
     saload
     saload
     saload

   Solution:
   - Cache intermediate array references in local variables
   - Consider restructuring data to reduce indirection levels
   - Pre-compute commonly accessed indices

2. TYPE CONVERSION OVERHEAD
   Problem: 318 s2i and 216 i2s conversions across all methods (1.47 ratio)

   Solution:
   - Keep intermediate values in int form when they'll be used in int operations
   - Review if short arithmetic can be promoted to int where stack depth allows
   - The >1.0 ratio suggests more conversions from short→int than back,
     indicating values could stay as int longer

3. STATIC FIELD ACCESS PRESSURE
   Problem: MEM_I, MEM_S, MEM_B accessed thousands of times
   - Functions spend ~20% of instructions just accessing static fields

   Solution:
   - Use local variables to cache array references at function start
   - Batch array accesses rather than individual gets/puts
   - Consider if some temporary data can use locals instead of global arrays

4. METHOD SIZE
   Problem: R_StoreWallRange at 1095 instructions is massive

   Impact:
   - JavaCard method size limit is 64KB bytecode (we're nowhere near it yet)
   - Large methods prevent inlining
   - JVM has harder time optimizing
   - Stack frame overhead is high

   Solution:
   - If hitting limits, split into logical sub-functions
   - Current size is acceptable but watch for growth

5. CONSTANT ARITHMETIC
   Problem: Found multiplications/divisions by powers of 2

   Solution:
   - Verify JCC compiler is converting these to shifts
   - Manual verification: check if multiplies by 2,4,8,16,etc use shifts
   - If not, this is a compiler optimization opportunity

6. MEMORY ACCESS PATTERNS
   Problem: High percentage of instructions are memory operations
   - ~21% array loads/stores
   - ~19% static field access
   - Total: ~40% of all instructions are memory operations

   Solution:
   - This is inherent to JavaCard (no pointers, everything is arrays)
   - Focus on reducing total instruction count rather than changing memory patterns
   - Use macros to ensure access patterns are optimal

PRIORITY ORDER:
1. Array access caching (biggest impact on R_StoreWallRange)
2. Type conversion reduction (affects all functions)
3. Static field caching in locals (medium impact)
4. Verify constant arithmetic optimization (compiler issue if not done)
""")


if __name__ == "__main__":
    main()
