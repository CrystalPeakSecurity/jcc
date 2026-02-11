"""Tests for analysis/function.py - per-function analysis orchestration."""

from jcc.analysis.callgraph import build_call_graph
from jcc.analysis.function import analyze_all_functions, analyze_function
from jcc.analysis.locals import Limits
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
    ICmpInst,
    Instruction,
    PhiInst,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Module, Parameter
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.values import Const, SSARef


# === Test Helpers ===


def make_function(
    name: str,
    blocks: list[Block],
    params: list[Parameter] | None = None,
    return_type: JCType = JCType.VOID,
) -> Function:
    """Create a function for testing."""
    return Function(
        name=name,
        params=tuple(params or []),
        return_type=return_type,
        blocks=tuple(blocks),
    )


def make_block(
    label: str,
    instructions: list[Instruction],
    terminator: BranchInst | ReturnInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


# === Orchestrator Tests ===


class TestAnalyzeFunction:
    def test_simple_function(self) -> None:
        """Orchestrator handles simple function with no locals."""
        func = make_function(
            "test",
            [make_block("entry", [])],
        )

        result = analyze_function(func)

        assert result.locals.first_temp_slot == 0

    def test_function_with_escaping_value(self) -> None:
        """Orchestrator assigns slots to escaping values."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        result = analyze_function(func)

        # %x escapes (used across blocks), should have slot
        assert result.locals.has_slot(SSAName("%x"))
        assert result.locals.first_temp_slot >= 1

    def test_function_with_phi(self) -> None:
        """Orchestrator handles phis and can coalesce."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
                ),
                make_block(
                    "loop",
                    [
                        PhiInst(
                            result=SSAName("%i"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%i.next")), BlockLabel("loop")),
                            ),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%i.next"),
                            op="add",
                            left=SSARef(name=SSAName("%i")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
                ),
            ],
        )

        result = analyze_function(func)

        # Phi result should have slot
        assert result.locals.has_slot(SSAName("%i"))
        # Phi increment source should have slot
        assert result.locals.has_slot(SSAName("%i.next"))
        # They should share slots (coalesced) since they don't interfere
        i_slot = result.locals.get_slot(SSAName("%i"))
        next_slot = result.locals.get_slot(SSAName("%i.next"))
        assert i_slot == next_slot

    def test_custom_limits(self) -> None:
        """Orchestrator respects custom limits."""
        func = make_function(
            "test",
            [make_block("entry", [])],
        )

        custom_limits = Limits(
            max_locals_soft=32,
            max_locals_hard=128,
        )

        result = analyze_function(func, limits=custom_limits)

        # Should succeed with 0 locals
        assert result.locals.first_temp_slot == 0

    def test_non_escaping_value_no_slot(self) -> None:
        """Values used only in same block don't get slots."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        # %x used in same block
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=3, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        result = analyze_function(func)

        # %x is not escaping, shouldn't have slot
        assert not result.locals.has_slot(SSAName("%x"))
        assert result.locals.first_temp_slot == 0

    def test_narrowing_applied(self) -> None:
        """Orchestrator applies narrowing to i32 values."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # Small constant - can be narrowed
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        result = analyze_function(func)

        # %x should have slot
        assert result.locals.has_slot(SSAName("%x"))
        # Original type is INT
        assert result.locals.get_value_type(SSAName("%x")) == JCType.INT
        # Storage type should be SHORT (narrowed)
        assert result.locals.get_register_type(SSAName("%x")) == JCType.SHORT


# === Module-Level Orchestration Tests ===


def make_module(functions: list[Function]) -> Module:
    """Create a module for testing."""
    return Module(
        globals={},
        functions={f.name: f for f in functions},
    )


class TestAnalyzeAllFunctions:
    def test_single_function(self) -> None:
        """Analyzes a single function correctly."""
        func = make_function("test", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        results = analyze_all_functions(module, graph)

        assert "test" in results

    def test_topological_order_used(self) -> None:
        """Functions analyzed in topological order (callees first)."""
        callee = make_function("callee", [make_block("entry", [])])
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="callee", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([caller, callee])
        graph = build_call_graph(module)

        results = analyze_all_functions(module, graph)

        # Both should be analyzed
        assert "caller" in results
        assert "callee" in results
        # Callee should be before caller in topological order
        assert graph.topological_order.index("callee") < graph.topological_order.index("caller")

    def test_inter_procedural_narrowing(self) -> None:
        """Caller's arg narrows when callee's param is narrowable."""
        # Callee: param only used in add (narrowable)
        callee = make_function(
            "callee",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        # Caller: passes %x to callee
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        CallInst(
                            result=None,
                            func_name="callee",
                            args=(SSARef(name=SSAName("%x")),),
                            ty=JCType.VOID,
                        ),
                    ],
                    # Need to use %x across blocks to make it escape
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        module = make_module([caller, callee])
        graph = build_call_graph(module)
        results = analyze_all_functions(module, graph)

        # Caller's %x should be narrowed (callee's param is narrowable)
        assert results["caller"].locals.get_register_type(SSAName("%x")) == JCType.SHORT

    def test_inter_procedural_stays_wide(self) -> None:
        """Caller's arg stays wide when callee's param needs full i32."""
        # Callee: param used in icmp (must be wide)
        callee = make_function(
            "callee",
            [
                make_block(
                    "entry",
                    [
                        ICmpInst(
                            result=SSAName("%cmp"),
                            pred="eq",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        # Caller: passes %x to callee
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        CallInst(
                            result=None,
                            func_name="callee",
                            args=(SSARef(name=SSAName("%x")),),
                            ty=JCType.VOID,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        module = make_module([caller, callee])
        graph = build_call_graph(module)
        results = analyze_all_functions(module, graph)

        # Caller's %x should stay INT (callee's param is wide)
        assert results["caller"].locals.get_register_type(SSAName("%x")) == JCType.INT
