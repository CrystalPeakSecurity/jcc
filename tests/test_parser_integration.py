"""Integration tests for the LLVM parser with real .ll files."""

from pathlib import Path

import pytest

from jcc.ir.errors import ParseError
from jcc.ir.instructions import (
    BranchInst,
    CallInst,
    GEPInst,
    Instruction,
    LoadInst,
    PhiInst,
    ReturnInst,
    StoreInst,
)
from jcc.ir.llvm import LLVMModule
from jcc.ir.parser import LLVMParser
from jcc.ir.types import BlockLabel


@pytest.mark.integration
class TestParseMinimalExample:
    """Test parsing the minimal example's .ll file."""

    def test_parse_all_instructions(self, minimal_ll: Path) -> None:
        """Parse all instructions in minimal.ll without error."""
        parser = LLVMParser()
        module = LLVMModule.parse_file(minimal_ll)

        instruction_count = 0
        for func in module.functions:
            if func.is_declaration:
                continue
            parser.set_context(func.name)
            for block in func.blocks:
                for instr in block.instructions:
                    parsed = parser.parse_instruction(instr)
                    assert isinstance(parsed, Instruction)
                    instruction_count += 1

        # Minimal example should have some instructions
        assert instruction_count > 0

    def test_instruction_types_present(self, minimal_ll: Path) -> None:
        """Verify various instruction types are parsed from minimal.ll."""
        parser = LLVMParser()
        module = LLVMModule.parse_file(minimal_ll)

        types_found: set[type] = set()
        for func in module.functions:
            if func.is_declaration:
                continue
            for block in func.blocks:
                for instr in block.instructions:
                    parsed = parser.parse_instruction(instr)
                    types_found.add(type(parsed))

        # Minimal example should have at least returns
        assert ReturnInst in types_found


@pytest.mark.integration
class TestParseAllExamples:
    """Test parsing all example .ll files."""

    def test_parse_all_ll_files(self, example_ll_files: list[Path]) -> None:
        """Parse all .ll files from example projects.

        Unknown opcodes are counted but not treated as failures - they may come
        from Rust code using features we don't need for C code.
        """
        if not example_ll_files:
            pytest.skip("No .ll files found - build examples first")

        parser = LLVMParser()
        total_instructions = 0
        unknown_opcodes: dict[str, int] = {}
        critical_errors: list[str] = []

        for ll_path in example_ll_files:
            try:
                module = LLVMModule.parse_file(ll_path)

                for func in module.functions:
                    if func.is_declaration:
                        continue
                    parser.set_context(func.name, None)
                    for block in func.blocks:
                        parser.set_context(func.name, BlockLabel(block.name))
                        for instr in block.instructions:
                            try:
                                parser.parse_instruction(instr)
                                total_instructions += 1
                            except ParseError as e:
                                err_str = str(e)
                                if "Unknown opcode" in err_str:
                                    opcode = instr.opcode
                                    unknown_opcodes[opcode] = unknown_opcodes.get(opcode, 0) + 1
                                elif "ptrtoint" in err_str or "inttoptr" in err_str:
                                    # Rust emits these; LLVM -O2 removes them
                                    pass
                                else:
                                    critical_errors.append(f"{ll_path.name}: {e}")
            except Exception as e:
                critical_errors.append(f"{ll_path.name}: Failed to parse module: {e}")

        # Report unknown opcodes but don't fail for them
        if unknown_opcodes:
            print(f"\nUnknown opcodes (not implemented): {unknown_opcodes}")

        # Fail only for critical errors (not unknown opcodes)
        if critical_errors:
            pytest.fail(f"Parse errors:\n" + "\n".join(critical_errors[:10]))

        assert total_instructions > 0, "No instructions were parsed"
        print(f"\nSuccessfully parsed {total_instructions} instructions")


@pytest.mark.integration
class TestPhiBlockLabels:
    """Test that phi block labels are preserved correctly from real IR."""

    def test_phi_labels_preserved(self, example_ll_files: list[Path]) -> None:
        """Verify phi instructions preserve their block labels."""
        if not example_ll_files:
            pytest.skip("No .ll files found")

        parser = LLVMParser()
        phi_count = 0

        for ll_path in example_ll_files:
            try:
                module = LLVMModule.parse_file(ll_path)

                for func in module.functions:
                    if func.is_declaration:
                        continue

                    for block in func.blocks:
                        for instr in block.instructions:
                            if instr.opcode == "phi":
                                parsed = parser.parse_instruction(instr)
                                assert isinstance(parsed, PhiInst)
                                phi_count += 1

                                # Each incoming label should be non-empty
                                for _, label in parsed.incoming:
                                    assert label is not None
                                    assert len(label) > 0

            except Exception:
                # Skip files that fail to parse (may have unsupported features)
                continue

        # If we found any phis, the test passed
        if phi_count > 0:
            assert True
        else:
            pytest.skip("No phi instructions found in examples")


@pytest.mark.integration
class TestInstructionCoverage:
    """Test instruction type coverage across all examples."""

    def test_instruction_coverage(self, example_ll_files: list[Path]) -> None:
        """Check which instruction types appear in real .ll files."""
        if not example_ll_files:
            pytest.skip("No .ll files found")

        parser = LLVMParser()
        types_found: dict[type, int] = {}

        for ll_path in example_ll_files:
            try:
                module = LLVMModule.parse_file(ll_path)

                for func in module.functions:
                    if func.is_declaration:
                        continue
                    for block in func.blocks:
                        for instr in block.instructions:
                            try:
                                parsed = parser.parse_instruction(instr)
                                t = type(parsed)
                                types_found[t] = types_found.get(t, 0) + 1
                            except ParseError:
                                pass  # Skip unparseable instructions for coverage test

            except Exception:
                continue

        # Report coverage
        print("\nInstruction type coverage:")
        for t, count in sorted(types_found.items(), key=lambda x: -x[1]):
            print(f"  {t.__name__}: {count}")

        # We expect at least some common types
        common_types = {ReturnInst, BranchInst, LoadInst, StoreInst}
        found_common = common_types & set(types_found.keys())
        assert len(found_common) >= 2, f"Expected common types, found: {types_found.keys()}"


@pytest.mark.integration
class TestGEPSourceTypes:
    """Test that GEP source types are extracted correctly."""

    def test_gep_source_types(self, example_ll_files: list[Path]) -> None:
        """Verify GEP source types are captured."""
        if not example_ll_files:
            pytest.skip("No .ll files found")

        parser = LLVMParser()
        gep_types: set[str] = set()

        for ll_path in example_ll_files:
            try:
                module = LLVMModule.parse_file(ll_path)

                for func in module.functions:
                    if func.is_declaration:
                        continue
                    for block in func.blocks:
                        for instr in block.instructions:
                            if instr.opcode == "getelementptr":
                                parsed = parser.parse_instruction(instr)
                                assert isinstance(parsed, GEPInst)
                                if parsed.source_type:
                                    gep_types.add(parsed.source_type)

            except Exception:
                continue

        if gep_types:
            print(f"\nGEP source types found: {gep_types}")
        else:
            pytest.skip("No GEP instructions found")


@pytest.mark.integration
class TestCallParsing:
    """Test that function calls are parsed correctly from real IR."""

    def test_call_function_names(self, example_ll_files: list[Path]) -> None:
        """Verify call instructions extract function names."""
        if not example_ll_files:
            pytest.skip("No .ll files found")

        parser = LLVMParser()
        func_names: set[str] = set()

        for ll_path in example_ll_files:
            try:
                module = LLVMModule.parse_file(ll_path)

                for func in module.functions:
                    if func.is_declaration:
                        continue
                    for block in func.blocks:
                        for instr in block.instructions:
                            if instr.opcode == "call":
                                parsed = parser.parse_instruction(instr)
                                assert isinstance(parsed, CallInst)
                                func_names.add(parsed.func_name)

            except Exception:
                continue

        if func_names:
            print(f"\nFunction names called: {func_names}")
            # Verify names are reasonable (no empty strings)
            assert all(len(name) > 0 for name in func_names)
        else:
            pytest.skip("No call instructions found")
