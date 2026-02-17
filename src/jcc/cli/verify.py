"""Verify: bytecode verification with JCA correlation."""

import re
import sys
from pathlib import Path


def _build_branch_sources(disasm) -> dict[int, list[int]]:
    """Build map of target PC -> list of source PCs that branch there."""
    from jcc.cap.opcodes import is_branch_opcode

    sources: dict[int, list[int]] = {}
    for instr in disasm.instructions:
        if not is_branch_opcode(instr.opcode):
            continue
        for match in re.finditer(r'L_([0-9A-Fa-f]+)', instr.operand_str):
            target = int(match.group(1), 16)
            sources.setdefault(target, []).append(instr.offset)
    return sources


def _load_registry_index() -> dict | None:
    """Load API registry from .exp files and build token-indexed lookup."""
    try:
        from jcc.api.loader import load_api_registry
        from jcc.cap.framework_sigs import build_registry_index
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
    return [pkg.aid.hex().upper() for pkg in cap.imports.packages]


def _run_custom_verify(cap_file: Path, strict: bool, trace: int) -> bool:
    """Run the custom bytecode verifier. Returns True if all methods pass."""
    from jcc.cap.disasm import disassemble_method
    from jcc.cap.jca_map import find_method_map, parse_jca_file
    from jcc.cap.parse import parse_cap
    from jcc.cap.verify import format_verify_error, verify_method

    try:
        cap = parse_cap(cap_file)
    except Exception as e:
        print(f"Error parsing CAP file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse JCA file (same name as CAP)
    jca_maps = {}
    jca_path = cap_file.with_suffix(".jca")
    jca_loaded = False
    if jca_path.exists():
        try:
            jca_maps = parse_jca_file(jca_path)
            jca_loaded = True
        except Exception as e:
            print(f"Warning: Failed to parse JCA file: {e}", file=sys.stderr)

    registry_index = _load_registry_index()
    import_aids = _get_import_aids(cap)

    print(f"Verifying: {cap_file}")
    if cap.header and cap.header.package_info:
        print(f"Package:   {cap.header.package_info.aid_hex}")
    if jca_loaded:
        print(f"JCA:       {jca_path}")
    print()

    if not cap.method:
        print("No Method component found in CAP file")
        return True

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

    if not errors_list:
        return True

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

            disasm = disassemble_method(method, cap.constant_pool)
            branch_sources = _build_branch_sources(disasm)

            print()
            print("  Disassembly:")
            for instr in disasm.instructions:
                if abs(instr.offset - error.pc) <= 12:
                    marker = ">>>" if instr.offset == error.pc else "   "
                    operands = f" {instr.operand_str}" if instr.operand_str else ""
                    instr_str = f"{instr.mnemonic}{operands}"
                    source_str = ""
                    if instr.offset in branch_sources:
                        srcs = branch_sources[instr.offset]
                        source_str = f"  ; from {', '.join(str(s) for s in srcs)}"
                    print(f"    {marker} {instr.offset:4d}: {instr_str:30s}{source_str}")

    return False


def _run_oracle_verify(cap_file: Path) -> bool:
    """Run Oracle's verifycap tool. Returns True on success."""
    try:
        from jcc.jcdk import get_jcdk
        from jcc.output.capgen import run_verifycap

        jcdk = get_jcdk("3.0.5")
        run_verifycap(jcdk, cap_file)
        print("\nOracle verifycap: PASS")
        return True
    except Exception as e:
        print(f"\nOracle verifycap: FAIL\n{e}", file=sys.stderr)
        return False


def run_verify(
    cap_file: Path,
    *,
    strict: bool = False,
    skip_oracle: bool = False,
) -> None:
    """Verify a CAP file's bytecode."""
    if not cap_file.exists():
        print(f"Error: CAP file not found: {cap_file}", file=sys.stderr)
        sys.exit(1)

    custom_ok = _run_custom_verify(cap_file, strict, trace=10)

    oracle_ok = True
    if not skip_oracle:
        oracle_ok = _run_oracle_verify(cap_file)

    if not custom_ok or not oracle_ok:
        sys.exit(1)
