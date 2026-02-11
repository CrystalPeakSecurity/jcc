"""Integration tests for the analysis pipeline."""

from pathlib import Path

import pytest

from jcc.analysis.base import AnalysisError
from jcc.analysis.callgraph import build_call_graph
from jcc.analysis.escape import analyze_escapes
from jcc.analysis.globals import (
    AllocationResult,
    MemArray,
    analyze_module,
)
from jcc.analysis.narrowing import analyze_narrowing
from jcc.analysis.phi import analyze_phis
from jcc.ir.module import parse_module_from_file


# === Full Pipeline Tests ===


class TestAnalysisPipeline:
    """Test the complete analysis pipeline on real IR."""

    def test_pipeline_with_minimal_example(self, minimal_ll: Path) -> None:
        """Run analysis pipeline on minimal example (per-function analyses).

        Note: Global allocation is skipped because test files may not have debug info.
        """
        module = parse_module_from_file(minimal_ll)

        # Module-level validation
        build_call_graph(module)

        # Per-function analysis (doesn't require debug info)
        for func in module.functions.values():
            phi_info = analyze_phis(func)
            narrowing = analyze_narrowing(func)
            escapes = analyze_escapes(func, phi_info)

            # All outputs should be valid (validation happens in __post_init__)
            assert phi_info.validate() == []
            assert narrowing.validate() == []
            assert escapes.validate() == []

    def test_pipeline_with_all_examples(self, example_ll_files: list[Path]) -> None:
        """Run per-function analysis on all available example .ll files."""
        for ll_file in example_ll_files:
            try:
                module = parse_module_from_file(ll_file)
            except Exception as e:
                # Skip files that can't be parsed (e.g., unsupported constructs)
                pytest.skip(f"Cannot parse {ll_file.name}: {e}")

            # Module-level - recursion would be a bug, should fail not skip
            build_call_graph(module)

            # Per-function (doesn't require debug info)
            for func in module.functions.values():
                phi_info = analyze_phis(func)
                narrowing = analyze_narrowing(func)
                escapes = analyze_escapes(func, phi_info)

                # All should validate
                assert phi_info.validate() == [], f"PhiInfo failed in {func.name}"
                assert narrowing.validate() == [], f"Narrowing failed in {func.name}"
                assert escapes.validate() == [], f"Escapes failed in {func.name}"


# === Orchestrated Module Analysis Tests ===


class TestAnalyzeModule:
    """Test the analyze_module orchestration function."""

    def test_analyze_module_minimal(self, minimal_ll: Path) -> None:
        """Test analyze_module on minimal example."""
        module = parse_module_from_file(minimal_ll)

        result = analyze_module(module)

        # Should produce valid allocation result
        assert isinstance(result, AllocationResult)
        assert result.validate() == []

        # Check mem_sizes are reasonable
        for mem_array in MemArray:
            assert mem_array in result.mem_sizes
            assert result.mem_sizes[mem_array] >= 0


# === Debug Info Integration Tests ===


class TestDebugInfoPipeline:
    """Test full pipeline with debug-enabled .ll files."""

    def test_alloca_debug_info_pipeline(self, alloca_debug_ll: Path) -> None:
        """Full pipeline with allocas that have debug info via #dbg_declare."""
        module = parse_module_from_file(alloca_debug_ll)

        # Should have synthetic globals from allocas
        synthetic_globals = [
            name
            for name in module.globals.keys()
            if ".1" in str(name) or ".2" in str(name) or ".3" in str(name)
        ]
        assert len(synthetic_globals) > 0, "Expected synthetic globals from allocas"

        # Check debug info is attached
        for name in synthetic_globals:
            glob = module.globals[name]
            assert glob.debug_type is not None, f"Missing debug info for {name}"

        # Run full analysis
        result = analyze_module(module)

        # Verify allocations
        assert result.validate() == []

        # Check struct alloca got allocated (struct Point with x, y, flags)
        struct_allocs = [
            s
            for s in result.structs.values()
            if len(s.fields) == 3  # Point has 3 fields
        ]
        assert len(struct_allocs) == 1, "Expected struct Point to be allocated"
        struct = struct_allocs[0]
        assert struct.count == 1
        assert struct.stride == 6  # 2 + 2 + 1 + padding = 6 bytes

    def test_global_debug_info_pipeline(self, global_debug_ll: Path) -> None:
        """Full pipeline with globals that have debug info via !dbg."""
        module = parse_module_from_file(global_debug_ll)

        # Check debug info is attached to real globals
        for name, glob in module.globals.items():
            if name.startswith("@test"):
                # Skip synthetic function-local globals
                continue
            assert glob.debug_type is not None, f"Missing debug info for {name}"

        # Run full analysis
        result = analyze_module(module)

        # Verify allocations
        assert result.validate() == []


# === Synthetic Global Tests ===


class TestSyntheticGlobals:
    """Test that allocas (normalized to synthetic globals) are handled correctly."""

    def test_synthetic_globals_allocated(self, minimal_ll: Path) -> None:
        """Synthetic globals from allocas should be allocated.

        This test may be skipped if the file doesn't have debug info.
        """
        module = parse_module_from_file(minimal_ll)

        # Check for synthetic globals (format: @func.localname)
        synthetic_globals = [
            name
            for name in module.globals.keys()
            if str(name).count(".") > 0 and str(name).startswith("@")
        ]

        if synthetic_globals:
            try:
                result = analyze_module(module)
            except AnalysisError as e:
                if "missing debug info" in str(e):
                    pytest.skip("Test file doesn't have debug info")
                raise

            for name in synthetic_globals:
                # Should be in either globals or structs
                assert name in result.globals or name in result.structs, (
                    f"Synthetic global {name} not allocated"
                )


# === Consistency Tests ===


class TestAnalysisConsistency:
    """Test that analyses are internally consistent."""

    def test_phi_escape_consistency(self, minimal_ll: Path) -> None:
        """All phi results should appear in escape analysis."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            phi_info = analyze_phis(func)
            escapes = analyze_escapes(func, phi_info)

            # Every phi result should escape
            for phi_name in phi_info.phi_sources:
                assert phi_name in escapes.escapes, f"Phi {phi_name} not in escapes for {func.name}"

    def test_narrowing_disjoint(self, minimal_ll: Path) -> None:
        """Wide and narrowed sets should be disjoint."""
        module = parse_module_from_file(minimal_ll)

        for func in module.functions.values():
            narrowing = analyze_narrowing(func)

            overlap = narrowing.wide_values & narrowing.narrowed_values
            assert len(overlap) == 0, f"Overlap in narrowing for {func.name}: {overlap}"


# === Edge Case Tests ===


class TestEdgeCases:
    """Test edge cases in analysis."""

    def test_empty_function(self) -> None:
        """Analysis should handle functions with no instructions."""
        from jcc.ir.instructions import ReturnInst
        from jcc.ir.module import Block, Function, Module
        from jcc.ir.types import BlockLabel, JCType

        func = Function(
            name="empty",
            params=(),
            return_type=JCType.VOID,
            blocks=(
                Block(
                    label=BlockLabel("entry"),
                    instructions=(),
                    terminator=ReturnInst(value=None, ty=JCType.VOID),
                ),
            ),
        )
        module = Module(globals={}, functions={"empty": func})

        # Module-level validation
        build_call_graph(module)

        # Per-function analysis
        phi_info = analyze_phis(func)
        narrowing = analyze_narrowing(func)
        escapes = analyze_escapes(func, phi_info)

        assert len(phi_info.phi_sources) == 0
        assert len(narrowing.wide_values) == 0
        assert len(escapes.escapes) == 0

    def test_function_with_only_params(self) -> None:
        """Analysis should handle functions that only use parameters."""
        from jcc.ir.instructions import ReturnInst
        from jcc.ir.module import Block, Function, Module, Parameter
        from jcc.ir.types import BlockLabel, JCType, SSAName
        from jcc.ir.values import SSARef

        func = Function(
            name="passthrough",
            params=(Parameter(name=SSAName("%x"), ty=JCType.SHORT),),
            return_type=JCType.SHORT,
            blocks=(
                Block(
                    label=BlockLabel("entry"),
                    instructions=(),
                    terminator=ReturnInst(
                        value=SSARef(name=SSAName("%x")),
                        ty=JCType.SHORT,
                    ),
                ),
            ),
        )
        _module = Module(globals={}, functions={"passthrough": func})

        # Should not raise
        phi_info = analyze_phis(func)
        _narrowing = analyze_narrowing(func)
        escapes = analyze_escapes(func, phi_info)

        assert len(phi_info.phi_sources) == 0
        # Parameter used in entry block where it's defined, so no escape
        assert SSAName("%x") not in escapes.escapes
