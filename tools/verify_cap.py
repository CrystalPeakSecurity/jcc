#!/usr/bin/env python3
"""Custom bytecode verifier for JavaCard CAP files.

Provides actionable error messages with JCA source correlation,
based on Xavier Leroy's "Bytecode verification on Java smart cards" paper.

Usage:
    tools/verify_cap.py examples/rusty/build/main.cap
    tools/verify_cap.py main.cap --jca main.jca
    tools/verify_cap.py main.cap --strict
"""

import re
import sys
from pathlib import Path

import cyclopts

# Add tools to path for cap module imports, and src for jcc imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cap.parse import parse_cap
from cap.verify import verify_method, format_verify_error
from cap.jca_map import parse_jca_file, find_method_map
from cap.disasm import disassemble_method
from cap.opcodes import is_branch_opcode
from cap.framework_sigs import build_registry_index

app = cyclopts.App(
    name="verify_cap",
    help="Verify JavaCard CAP file bytecode with detailed error messages",
)


def _build_branch_sources(disasm) -> dict[int, list[int]]:
    """Build map of target PC -> list of source PCs that branch there."""
    sources: dict[int, list[int]] = {}
    for instr in disasm.instructions:
        if not is_branch_opcode(instr.opcode):
            continue
        # Parse targets from operand_str (format: L_XXXX or value:L_XXXX)
        for match in re.finditer(r'L_([0-9A-Fa-f]+)', instr.operand_str):
            target = int(match.group(1), 16)
            sources.setdefault(target, []).append(instr.offset)
    return sources


def _load_registry_index() -> dict | None:
    """Load API registry from .exp files and build token-indexed lookup."""
    try:
        from jcc.api.loader import load_api_registry
        from jcc.jcdk import get_jcdk

        jcdk = get_jcdk("3.0.5")
        registry = load_api_registry(jcdk)
        return build_registry_index(registry)
    except Exception as e:
        print(f"Warning: Could not load API registry: {e}", file=sys.stderr)
        return None


def _get_import_aids(cap) -> list[str]:
    """Extract package AID hex strings from CAP import component."""
    if not cap.imports:
        return []
    aids = []
    for pkg in cap.imports.packages:
        aids.append(pkg.aid.hex().upper())
    return aids


@app.default
def main(
    cap_file: Path,
    jca: Path | None = None,
    strict: bool = False,
    trace: int = 10,
) -> None:
    """Verify a CAP file's bytecode.

    Args:
        cap_file: CAP file to verify
        jca: JCA file for source correlation (default: same path with .jca extension)
        strict: Use Leroy's strict on-card verifier rules (R1: empty stack at branches)
        trace: Number of stack trace entries to show (default: 10)
    """
    if not cap_file.exists():
        print(f"Error: CAP file not found: {cap_file}", file=sys.stderr)
        sys.exit(1)

    try:
        cap = parse_cap(cap_file)
    except Exception as e:
        print(f"Error parsing CAP file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse JCA file (default: same name as CAP)
    jca_maps = {}
    jca_path = jca if jca else cap_file.with_suffix(".jca")
    jca_loaded = False
    if jca_path.exists():
        try:
            jca_maps = parse_jca_file(jca_path)
            jca_loaded = True
        except Exception as e:
            print(f"Warning: Failed to parse JCA file: {e}", file=sys.stderr)

    # Load API registry for external method signature resolution
    registry_index = _load_registry_index()
    import_aids = _get_import_aids(cap)

    # Header
    print(f"Verifying: {cap_file}")
    if cap.header and cap.header.package_info:
        print(f"Package:   {cap.header.package_info.aid_hex}")
    if jca_loaded:
        print(f"JCA:       {jca_path}")
    print()

    if not cap.method:
        print("No Method component found in CAP file")
        sys.exit(0)

    # Verify each method
    methods = cap.method.methods
    passed = 0
    failed = 0
    errors_list = []

    for method in methods:
        jca_map = find_method_map(jca_maps, method.bytecode)
        result = verify_method(
            method, cap.constant_pool, cap.descriptor, jca_map, strict=strict,
            registry_index=registry_index, import_aids=import_aids,
        )

        if result.success:
            passed += 1
        else:
            failed += 1
            errors_list.append((method, result))
            print(f"  [FAIL] Method {method.index} at offset {method.offset}")

    print()
    print(f"Results: {passed}/{len(methods)} methods passed")

    # Print detailed errors
    if not errors_list:
        sys.exit(0)

    print()
    print("=" * 70)
    print("ERRORS")
    print("=" * 70)

    for method, result in errors_list:
        jca_map = find_method_map(jca_maps, method.bytecode)
        method_name = (
            f"{jca_map.method_name}{jca_map.method_signature}"
            if jca_map
            else f"method_{method.index}"
        )

        for error in result.errors:
            print()
            print(f"--- {method_name} " + "-" * (50 - len(method_name)))
            print()
            print(format_verify_error(error, verbose=True, trace_count=trace))

            # Disassembly context
            disasm = disassemble_method(method, cap.constant_pool)
            branch_sources = _build_branch_sources(disasm)

            print()
            print("  Disassembly:")
            for instr in disasm.instructions:
                if abs(instr.offset - error.pc) <= 12:
                    # Marker for error location
                    marker = ">>>" if instr.offset == error.pc else "   "

                    # Format instruction
                    operands = f" {instr.operand_str}" if instr.operand_str else ""
                    instr_str = f"{instr.mnemonic}{operands}"

                    # Branch source annotation
                    source_str = ""
                    if instr.offset in branch_sources:
                        srcs = branch_sources[instr.offset]
                        source_str = f"  ; from {', '.join(str(s) for s in srcs)}"

                    print(f"    {marker} {instr.offset:4d}: {instr_str:30s}{source_str}")

    sys.exit(1)


if __name__ == "__main__":
    app()
