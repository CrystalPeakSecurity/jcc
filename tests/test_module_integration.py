"""Integration tests for module parsing with real .ll files."""

from pathlib import Path

import pytest

from jcc.ir.module import (
    parse_module,
    parse_module_from_file,
)
from jcc.ir.llvm import LLVMModule
from jcc.ir.instructions import (
    AllocaInst,
    BranchInst,
    GEPInst,
    LoadInst,
    ReturnInst,
    StoreInst,
    SwitchInst,
    UnreachableInst,
)
from jcc.ir.values import GlobalRef
from jcc.ir.types import GlobalName


class TestParseMinimalExample:
    """Test parsing the minimal example file."""

    @pytest.mark.integration
    def test_parse_minimal_module(self, minimal_ll: Path) -> None:
        """Parse minimal.ll into a typed module."""
        module = parse_module_from_file(minimal_ll)

        # Should have at least one function
        assert len(module.functions) > 0

    @pytest.mark.integration
    def test_module_has_functions(self, minimal_ll: Path) -> None:
        """Verify module has expected functions."""
        module = parse_module_from_file(minimal_ll)

        # Should have jcc_main or similar entry function
        func_names = list(module.functions.keys())
        assert len(func_names) > 0
        # Filter out LLVM intrinsics
        user_funcs = [f for f in func_names if not f.startswith("llvm.")]
        assert len(user_funcs) > 0

    @pytest.mark.integration
    def test_functions_have_blocks(self, minimal_ll: Path) -> None:
        """Verify all functions have at least one block."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            assert len(func.blocks) > 0
            assert func.entry_block is not None

    @pytest.mark.integration
    def test_blocks_have_terminators(self, minimal_ll: Path) -> None:
        """Verify all blocks have terminators."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            for block in func.blocks:
                assert block.terminator is not None
                assert isinstance(
                    block.terminator, (BranchInst, ReturnInst, SwitchInst, UnreachableInst)
                )


class TestParseAllExamples:
    """Test parsing all example .ll files."""

    @pytest.mark.integration
    def test_parse_all_ll_files(self, example_ll_files: list[Path]) -> None:
        """Parse all example .ll files without errors."""
        results: dict[str, str] = {}

        for ll_path in example_ll_files:
            try:
                module = parse_module_from_file(ll_path)
                results[ll_path.name] = f"OK: {len(module.functions)} functions"
            except Exception as e:
                results[ll_path.name] = f"ERROR: {e}"

        # Print summary for debugging
        for name, result in sorted(results.items()):
            print(f"{name}: {result}")

        # All files should parse
        errors = [n for n, r in results.items() if r.startswith("ERROR")]
        assert len(errors) == 0, f"Failed to parse: {errors}"


class TestPhiBlockLabels:
    """Test that phi block labels are correctly preserved and validated."""

    @pytest.mark.integration
    def test_phi_labels_in_module(self, example_ll_files: list[Path]) -> None:
        """Verify phi labels reference valid blocks in all examples."""
        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)

            for func in module.functions.values():
                block_labels = {b.label for b in func.blocks}

                for block in func.blocks:
                    for phi in block.phi_instructions:
                        for _, label in phi.incoming:
                            # Validation happens during parsing, but double-check
                            assert label in block_labels, (
                                f"{ll_path.name}: phi in {func.name}/{block.label} "
                                f"references unknown block {label}"
                            )


class TestModuleStructure:
    """Test module structure properties."""

    @pytest.mark.integration
    def test_module_globals(self, example_ll_files: list[Path]) -> None:
        """Test that globals are parsed."""
        has_globals = False

        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)
            if module.globals:
                has_globals = True
                for name, gv in module.globals.items():
                    # All globals should have names starting with @
                    assert name.startswith("@"), f"Global {name} doesn't start with @"
                    # llvm_type should not be empty
                    assert gv.llvm_type, f"Global {name} has empty type"

        # At least some examples should have globals
        assert has_globals, "No globals found in any example"

    @pytest.mark.integration
    def test_function_parameters(self, example_ll_files: list[Path]) -> None:
        """Test that function parameters are parsed."""
        has_params = False

        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)

            for func in module.functions.values():
                if func.params:
                    has_params = True
                    for param in func.params:
                        # Parameter name should start with %
                        assert param.name.startswith("%")

        # At least some functions should have parameters
        assert has_params, "No function parameters found in any example"


class TestBlockMap:
    """Test block map functionality."""

    @pytest.mark.integration
    def test_block_map_complete(self, minimal_ll: Path) -> None:
        """Test that block_map contains all blocks."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            block_map = func.block_map
            assert len(block_map) == len(func.blocks)

            for block in func.blocks:
                assert block.label in block_map
                assert block_map[block.label] == block

    @pytest.mark.integration
    def test_block_map_lookup(self, minimal_ll: Path) -> None:
        """Test block_map lookup."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            for block in func.blocks:
                retrieved = func.block_map[block.label]
                assert retrieved == block


class TestModuleFromLLVMModule:
    """Test parsing from LLVMModule directly."""

    @pytest.mark.integration
    def test_parse_from_llvm_module(self, minimal_ll: Path) -> None:
        """Test parse_module with LLVMModule."""
        llvm_module = LLVMModule.parse_file(minimal_ll)
        module = parse_module(llvm_module)

        assert len(module.functions) > 0


class TestPhiValidation:
    """Test phi validation catches errors."""

    def test_phi_validation_runs(self) -> None:
        """Test that phi validation is part of module parsing."""
        # This is tested implicitly by all the integration tests above
        # If phi validation fails, parsing would raise ModuleError
        pass


class TestGlobalInitializers:
    """Test global initializer parsing."""

    @pytest.mark.integration
    def test_global_initializers(self, example_ll_files: list[Path]) -> None:
        """Test that global initializers are parsed."""
        from jcc.ir.module import (
            IntArrayInit,
            ZeroInit,
        )

        init_types: dict[str, int] = {
            "ZeroInit": 0,
            "IntArrayInit": 0,
            "ByteStringInit": 0,
            "None": 0,
        }

        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)

            for gv in module.globals.values():
                if gv.initializer is None:
                    init_types["None"] += 1
                elif isinstance(gv.initializer, ZeroInit):
                    init_types["ZeroInit"] += 1
                elif isinstance(gv.initializer, IntArrayInit):
                    init_types["IntArrayInit"] += 1
                else:  # ByteStringInit
                    init_types["ByteStringInit"] += 1

        # Print summary
        print(f"Initializer types found: {init_types}")

        # Most common should be ZeroInit or None
        total = sum(init_types.values())
        if total > 0:
            # Just verify we're parsing something
            assert init_types["ZeroInit"] + init_types["None"] > 0


class TestControlFlow:
    """Test control flow structure parsing."""

    @pytest.mark.integration
    def test_branch_targets_valid(self, example_ll_files: list[Path]) -> None:
        """Test that all branch targets are valid blocks."""
        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)

            for func in module.functions.values():
                block_labels = {b.label for b in func.blocks}

                for block in func.blocks:
                    term = block.terminator
                    if isinstance(term, BranchInst):
                        assert term.true_label in block_labels
                        if term.false_label:
                            assert term.false_label in block_labels
                    elif isinstance(term, SwitchInst):
                        assert term.default in block_labels
                        for _, target in term.cases:
                            assert target in block_labels

    @pytest.mark.integration
    def test_entry_block_is_first(self, example_ll_files: list[Path]) -> None:
        """Test that entry block is always the first block."""
        for ll_path in example_ll_files:
            module = parse_module_from_file(ll_path)

            for func in module.functions.values():
                # Entry block should be accessible
                entry = func.entry_block
                # And should be the first block
                assert entry == func.blocks[0]


class TestAllocaNormalization:
    """Test alloca normalization to synthetic globals."""

    def test_alloca_becomes_synthetic_global(self) -> None:
        """Test that allocas become synthetic globals with scoped names."""
        ir = """
        define void @test_func() {
            %buffer = alloca [64 x i8], align 1
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # Synthetic global should exist with scoped name
        expected_name = GlobalName("@test_func.buffer")
        assert expected_name in module.globals

        # Check the global properties
        gv = module.globals[expected_name]
        assert gv.llvm_type == "[64 x i8]"
        assert gv.is_constant is False

    def test_alloca_not_in_final_instructions(self) -> None:
        """Test that AllocaInst is filtered out of final block instructions."""
        ir = """
        define void @test_func() {
            %x = alloca i32, align 4
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # No AllocaInst should exist in the parsed instructions
        for func in module.functions.values():
            for block in func.blocks:
                for instr in block.all_instructions:
                    assert not isinstance(instr, AllocaInst), (
                        f"AllocaInst should not be in parsed module: {instr}"
                    )

    def test_gep_references_synthetic_global(self) -> None:
        """Test that GEPs referencing allocas now reference synthetic globals."""
        ir = """
        define void @test_func() {
            %buffer = alloca [64 x i8], align 1
            %ptr = getelementptr inbounds [64 x i8], ptr %buffer, i64 0, i64 0
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # Find the GEP instruction
        func = module.functions["test_func"]
        gep_instr = None
        for block in func.blocks:
            for instr in block.instructions:
                if isinstance(instr, GEPInst):
                    gep_instr = instr
                    break

        assert gep_instr is not None, "GEP instruction not found"

        # The base should now be a GlobalRef to the synthetic global
        assert isinstance(gep_instr.base, GlobalRef), (
            f"GEP base should be GlobalRef, got {type(gep_instr.base)}"
        )
        assert gep_instr.base.name == GlobalName("@test_func.buffer")

    def test_multiple_allocas_same_function(self) -> None:
        """Test multiple allocas in same function get unique globals."""
        ir = """
        define void @test_func() {
            %a = alloca i32
            %b = alloca i16
            %c = alloca [10 x i8]
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # All three synthetic globals should exist
        assert GlobalName("@test_func.a") in module.globals
        assert GlobalName("@test_func.b") in module.globals
        assert GlobalName("@test_func.c") in module.globals

        # Each should have correct type
        assert module.globals[GlobalName("@test_func.a")].llvm_type == "i32"
        assert module.globals[GlobalName("@test_func.b")].llvm_type == "i16"
        assert module.globals[GlobalName("@test_func.c")].llvm_type == "[10 x i8]"

    def test_allocas_in_different_functions(self) -> None:
        """Test allocas in different functions get correctly scoped names."""
        ir = """
        define void @func1() {
            %buf = alloca [32 x i8]
            ret void
        }

        define void @func2() {
            %buf = alloca [64 x i8]
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # Both should exist with scoped names
        assert GlobalName("@func1.buf") in module.globals
        assert GlobalName("@func2.buf") in module.globals

        # They should have different types
        assert module.globals[GlobalName("@func1.buf")].llvm_type == "[32 x i8]"
        assert module.globals[GlobalName("@func2.buf")].llvm_type == "[64 x i8]"

    def test_synthetic_globals_have_zero_init(self) -> None:
        """Test that synthetic globals from allocas have ZeroInit."""
        from jcc.ir.module import ZeroInit

        ir = """
        define void @test_func() {
            %x = alloca i32
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        gv = module.globals[GlobalName("@test_func.x")]
        assert isinstance(gv.initializer, ZeroInit)

    def test_load_from_alloca_replaced(self) -> None:
        """Test that loads from allocas reference synthetic globals."""
        ir = """
        define i32 @test_func() {
            %x = alloca i32
            %val = load i32, ptr %x
            ret i32 %val
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # Find the load instruction
        func = module.functions["test_func"]
        load_instr = None
        for block in func.blocks:
            for instr in block.instructions:
                if isinstance(instr, LoadInst):
                    load_instr = instr
                    break

        assert load_instr is not None
        assert isinstance(load_instr.ptr, GlobalRef)
        assert load_instr.ptr.name == GlobalName("@test_func.x")

    def test_store_to_alloca_replaced(self) -> None:
        """Test that stores to allocas reference synthetic globals."""
        ir = """
        define void @test_func() {
            %x = alloca i32
            store i32 42, ptr %x
            ret void
        }
        """
        llvm_module = LLVMModule.parse_string(ir)
        module = parse_module(llvm_module)

        # Find the store instruction
        func = module.functions["test_func"]
        store_instr = None
        for block in func.blocks:
            for instr in block.instructions:
                if isinstance(instr, StoreInst):
                    store_instr = instr
                    break

        assert store_instr is not None
        assert isinstance(store_instr.ptr, GlobalRef)
        assert store_instr.ptr.name == GlobalName("@test_func.x")
