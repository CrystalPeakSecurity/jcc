#!/usr/bin/env python3
"""
Check if JCC compiler is optimizing constant arithmetic operations.
"""

import re
from pathlib import Path
from collections import defaultdict


def check_const_arithmetic(jca_path):
    """Find constant arithmetic operations and check if they're optimized."""

    mul_div_patterns = {
        "mul_by_const": [],
        "div_by_const": [],
        "mul_by_power_of_2": [],
        "div_by_power_of_2": [],
        "shift_operations": [],
    }

    with open(jca_path, "r") as f:
        lines = f.readlines()

    for i in range(len(lines) - 1):
        curr = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        # Look for constant followed by mul
        if ("const" in curr or "push" in curr) and ("smul" in next_line or "imul" in next_line):
            # Extract constant value
            match = re.search(r"(?:const[_\s]+|push\s+)(-?\d+)", curr)
            if match:
                val = int(match.group(1))
                is_power_of_2 = val > 0 and (val & (val - 1)) == 0

                mul_type = "imul" if "imul" in next_line else "smul"

                if is_power_of_2:
                    shift_amount = val.bit_length() - 1
                    mul_div_patterns["mul_by_power_of_2"].append(
                        {
                            "line": i + 1,
                            "value": val,
                            "shift": shift_amount,
                            "type": mul_type,
                            "context": [lines[max(0, i - 1)].strip(), curr, next_line],
                        }
                    )
                else:
                    mul_div_patterns["mul_by_const"].append(
                        {"line": i + 1, "value": val, "type": mul_type, "context": [curr, next_line]}
                    )

        # Look for constant followed by div
        if ("const" in curr or "push" in curr) and ("sdiv" in next_line or "idiv" in next_line):
            match = re.search(r"(?:const[_\s]+|push\s+)(-?\d+)", curr)
            if match:
                val = int(match.group(1))
                is_power_of_2 = val > 0 and (val & (val - 1)) == 0

                div_type = "idiv" if "idiv" in next_line else "sdiv"

                if is_power_of_2:
                    shift_amount = val.bit_length() - 1
                    mul_div_patterns["div_by_power_of_2"].append(
                        {
                            "line": i + 1,
                            "value": val,
                            "shift": shift_amount,
                            "type": div_type,
                            "context": [lines[max(0, i - 1)].strip(), curr, next_line],
                        }
                    )
                else:
                    mul_div_patterns["div_by_const"].append(
                        {"line": i + 1, "value": val, "type": div_type, "context": [curr, next_line]}
                    )

        # Look for shift operations (to see if compiler IS using them)
        if "shl" in curr or "shr" in curr:
            match = re.search(r"(i|s)(shl|shr|ushr)", curr)
            if match:
                mul_div_patterns["shift_operations"].append(
                    {
                        "line": i + 1,
                        "instr": curr,
                        "context": [lines[max(0, i - 2)].strip(), lines[max(0, i - 1)].strip(), curr],
                    }
                )

    return mul_div_patterns


def main():
    jca_path = Path(__file__).parent.parent / "build" / "applet.jca"

    if not jca_path.exists():
        print(f"Error: {jca_path} not found. Run 'just compile' first.")
        return

    print("=" * 80)
    print("CONSTANT ARITHMETIC OPTIMIZATION CHECK")
    print("=" * 80)

    patterns = check_const_arithmetic(jca_path)

    print(f"\nShift operations found: {len(patterns['shift_operations'])}")
    print(f"Multiplication by constant: {len(patterns['mul_by_const'])}")
    print(f"Division by constant: {len(patterns['div_by_const'])}")
    print(f"Multiplication by power of 2: {len(patterns['mul_by_power_of_2'])}")
    print(f"Division by power of 2: {len(patterns['div_by_power_of_2'])}")

    # Analyze shift operations to see what they're being used for
    print("\n" + "=" * 80)
    print("SHIFT OPERATION ANALYSIS")
    print("=" * 80)

    shift_by_type = defaultdict(int)
    for shift in patterns["shift_operations"]:
        instr = shift["instr"]
        if "sshl" in instr:
            shift_by_type["sshl"] += 1
        elif "ishl" in instr:
            shift_by_type["ishl"] += 1
        elif "sshr" in instr:
            shift_by_type["sshr"] += 1
        elif "ishr" in instr:
            shift_by_type["ishr"] += 1
        elif "iushr" in instr:
            shift_by_type["iushr"] += 1
        elif "sushr" in instr:
            shift_by_type["sushr"] += 1

    print("\nShift instruction breakdown:")
    for shift_type, count in sorted(shift_by_type.items()):
        print(f"  {shift_type:10s}: {count:4d}")

    # Show examples of shift operations
    print("\nExample shift operations (first 5):")
    for i, shift in enumerate(patterns["shift_operations"][:5], 1):
        print(f"\n  Example {i} (line {shift['line']}):")
        for line in shift["context"]:
            print(f"    {line}")

    # Check for unoptimized multiplications
    if patterns["mul_by_power_of_2"]:
        print("\n" + "=" * 80)
        print("⚠ UNOPTIMIZED: MULTIPLICATION BY POWER OF 2")
        print("=" * 80)
        print(f"\nFound {len(patterns['mul_by_power_of_2'])} multiplications that could be shifts:\n")

        # Group by value
        by_value = defaultdict(list)
        for item in patterns["mul_by_power_of_2"]:
            by_value[item["value"]].append(item)

        for val in sorted(by_value.keys()):
            items = by_value[val]
            shift_amount = items[0]["shift"]
            print(f"  Multiply by {val} (could be << {shift_amount}): {len(items)} occurrences")

            # Show first example
            print(f"    Example (line {items[0]['line']}):")
            for line in items[0]["context"]:
                print(f"      {line}")
            print()

    # Check for unoptimized divisions
    if patterns["div_by_power_of_2"]:
        print("\n" + "=" * 80)
        print("⚠ UNOPTIMIZED: DIVISION BY POWER OF 2")
        print("=" * 80)
        print(f"\nFound {len(patterns['div_by_power_of_2'])} divisions that could be shifts:\n")

        by_value = defaultdict(list)
        for item in patterns["div_by_power_of_2"]:
            by_value[item["value"]].append(item)

        for val in sorted(by_value.keys()):
            items = by_value[val]
            shift_amount = items[0]["shift"]
            print(f"  Divide by {val} (could be >> {shift_amount}): {len(items)} occurrences")

            # Show first example
            print(f"    Example (line {items[0]['line']}):")
            for line in items[0]["context"]:
                print(f"      {line}")
            print()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_shift_opportunities = len(patterns["mul_by_power_of_2"]) + len(patterns["div_by_power_of_2"])
    actual_shifts = len(patterns["shift_operations"])

    print(f"\nActual shift operations in code: {actual_shifts}")
    print(f"Missed optimization opportunities: {total_shift_opportunities}")

    if total_shift_opportunities > 0:
        print("\n❌ COMPILER NOT OPTIMIZING POWER-OF-2 ARITHMETIC")
        print(f"   This is a JCC compiler issue that should be fixed.")
        print(f"   Potential savings: ~{total_shift_opportunities * 2} instructions")
        print(f"   (mul/div are multi-cycle, shifts are single-cycle)")
    else:
        print("\n✓ No obvious power-of-2 arithmetic optimization opportunities found")
        print(f"  Compiler appears to be handling this correctly")

    if patterns["mul_by_const"] or patterns["div_by_const"]:
        print(f"\nOther constant arithmetic:")
        if patterns["mul_by_const"]:
            print(f"  Multiply by non-power-of-2: {len(patterns['mul_by_const'])} (expected)")
        if patterns["div_by_const"]:
            print(f"  Divide by non-power-of-2: {len(patterns['div_by_const'])} (expected)")


if __name__ == "__main__":
    main()
