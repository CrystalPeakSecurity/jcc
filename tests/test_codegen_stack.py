"""Tests for codegen/stack.py - CFG-based stack analysis."""

from jcc.codegen import ops
from jcc.codegen.stack import compute_max_stack
from jcc.ir.types import BlockLabel


class TestComputeMaxStackBasic:
    """Test basic max_stack computation."""

    def test_empty_instructions(self) -> None:
        result = compute_max_stack([])
        assert result == 2  # Minimum safety margin

    def test_single_const(self) -> None:
        instrs = [ops.sconst(1)]
        result = compute_max_stack(instrs)
        assert result == 1 + 2  # depth 1 + safety margin

    def test_add_two_consts(self) -> None:
        instrs = [
            ops.sconst(1),  # depth 1
            ops.sconst(2),  # depth 2 (max)
            ops.sadd(),  # depth 1
        ]
        result = compute_max_stack(instrs)
        assert result == 2 + 2  # max depth 2 + safety margin

    def test_load_store_sequence(self) -> None:
        instrs = [
            ops.sload(0),  # depth 1
            ops.sstore(1),  # depth 0
            ops.sload(1),  # depth 1
            ops.sload(2),  # depth 2
            ops.sadd(),  # depth 1
            ops.sstore(0),  # depth 0
        ]
        result = compute_max_stack(instrs)
        assert result == 2 + 2  # max depth 2 + safety margin

    def test_int_operations(self) -> None:
        # INT values are 2 slots each
        instrs = [
            ops.iconst(1),  # depth 2
            ops.iconst(2),  # depth 4 (max)
            ops.iadd(),  # depth 2
        ]
        result = compute_max_stack(instrs)
        assert result == 4 + 2  # max depth 4 + safety margin


class TestComputeMaxStackBranching:
    """Test max_stack with control flow."""

    def test_simple_branch(self) -> None:
        # Unconditional branch - stack should be correct
        label = BlockLabel("target")
        instrs = [
            ops.sconst(1),  # depth 1
            ops.goto(label),
            ops.label(label),
            ops.sconst(2),  # depth 2
            ops.sadd(),  # depth 1
        ]
        result = compute_max_stack(instrs)
        assert result == 2 + 2  # max depth 2

    def test_conditional_branch_both_paths(self) -> None:
        # Conditional branch - both paths should be tracked
        else_label = BlockLabel("else")
        end_label = BlockLabel("end")
        instrs = [
            ops.sconst(1),  # depth 1 (condition)
            ops.ifeq(else_label),  # depth 0
            # True path
            ops.sconst(10),  # depth 1
            ops.goto(end_label),
            # False path
            ops.label(else_label),
            ops.sconst(20),  # depth 1
            # End
            ops.label(end_label),
        ]
        result = compute_max_stack(instrs)
        # Both paths peak at depth 1 (not counting the condition which is consumed)
        assert result == 1 + 2

    def test_comparison_pattern(self) -> None:
        """Test the comparison pattern (like CompareExpr emits)."""
        else_label = BlockLabel("else")
        end_label = BlockLabel("end")
        instrs = [
            ops.sconst(1),  # depth 1
            ops.sconst(2),  # depth 2 (max for operands)
            ops.if_scmpne(else_label),  # depth 0
            ops.sconst(1),  # depth 1 (true path: push 1)
            ops.goto(end_label),
            ops.label(else_label),
            ops.sconst(0),  # depth 1 (false path: push 0)
            ops.label(end_label),
            # End: depth 1
        ]
        result = compute_max_stack(instrs)
        # Max depth is 2 (when both operands are on stack before compare)
        # NOT 2 (from overcounting both branches)
        assert result == 2 + 2

    def test_select_pattern(self) -> None:
        """Test the select pattern (like SelectExpr emits)."""
        else_label = BlockLabel("else")
        end_label = BlockLabel("end")
        instrs = [
            ops.sconst(1),  # depth 1 (condition)
            ops.ifeq(else_label),  # depth 0
            ops.sconst(10),  # depth 1 (then value)
            ops.goto(end_label),
            ops.label(else_label),
            ops.sconst(20),  # depth 1 (else value)
            ops.label(end_label),
            # End: depth 1 (one value on stack)
        ]
        result = compute_max_stack(instrs)
        # Max depth is 1, not 2 (branches are mutually exclusive)
        assert result == 1 + 2


class TestComputeMaxStackReturn:
    """Test max_stack with return statements."""

    def test_void_return(self) -> None:
        instrs = [
            ops.sconst(1),
            ops.sstore(0),
            ops.return_(),
        ]
        result = compute_max_stack(instrs)
        assert result == 1 + 2

    def test_value_return(self) -> None:
        instrs = [
            ops.sload(0),
            ops.sreturn(),
        ]
        result = compute_max_stack(instrs)
        assert result == 1 + 2


class TestComputeMaxStackCalls:
    """Test max_stack with method calls."""

    def test_invokestatic(self) -> None:
        # Call that takes 2 args and returns 1
        instrs = [
            ops.sconst(1),  # depth 1
            ops.sconst(2),  # depth 2 (max)
            ops.invokestatic(cp_index=10, nargs=2, nret=1),  # depth 1
        ]
        result = compute_max_stack(instrs)
        assert result == 2 + 2

    def test_void_call(self) -> None:
        # Call that takes 2 args and returns void
        instrs = [
            ops.sconst(1),  # depth 1
            ops.sconst(2),  # depth 2 (max)
            ops.invokestatic(cp_index=10, nargs=2, nret=0),  # depth 0
        ]
        result = compute_max_stack(instrs)
        assert result == 2 + 2


class TestComputeMaxStackSwitch:
    """Test max_stack with switch statements."""

    def test_tableswitch(self) -> None:
        case0 = BlockLabel("case0")
        case1 = BlockLabel("case1")
        default = BlockLabel("default")
        end = BlockLabel("end")
        instrs = [
            ops.sconst(1),
            ops.stableswitch(default, 0, 1, (case0, case1)),
            ops.label(case0),
            ops.sconst(10),
            ops.goto(end),
            ops.label(case1),
            ops.sconst(20),
            ops.goto(end),
            ops.label(default),
            ops.sconst(0),
            ops.label(end),
        ]
        result = compute_max_stack(instrs)
        # All paths peak at depth 1
        assert result == 1 + 2

    def test_lookupswitch(self) -> None:
        case0 = BlockLabel("case0")
        case5 = BlockLabel("case5")
        default = BlockLabel("default")
        instrs = [
            ops.sconst(1),
            ops.slookupswitch(default, ((0, case0), (5, case5))),
            ops.label(case0),
            ops.sconst(10),
            ops.sreturn(),
            ops.label(case5),
            ops.sconst(20),
            ops.sreturn(),
            ops.label(default),
            ops.sconst(0),
            ops.sreturn(),
        ]
        result = compute_max_stack(instrs)
        # All paths peak at depth 1
        assert result == 1 + 2
