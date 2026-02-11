"""Unit tests for ir/module.py."""

import pytest

from jcc.ir.errors import ModuleError
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    PhiInst,
    ReturnInst,
    SwitchInst,
)
from jcc.ir.module import (
    Block,
    ByteStringInit,
    Function,
    Global,
    IntArrayInit,
    Module,
    Parameter,
    ZeroInit,
    validate_block_terminators,
    validate_phi_labels,
)
from jcc.ir.patterns import decode_llvm_string
from jcc.ir.values import Const, SSARef
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName


class TestParameter:
    def test_parameter_creation(self) -> None:
        """Test basic parameter creation."""
        param = Parameter(name=SSAName("%buf"), ty=JCType.REF)
        assert param.name == SSAName("%buf")
        assert param.ty == JCType.REF

    def test_parameter_frozen(self) -> None:
        """Test that parameters are immutable."""
        param = Parameter(name=SSAName("%x"), ty=JCType.INT)
        with pytest.raises(AttributeError):
            param.ty = JCType.SHORT  # type: ignore[misc]


class TestBlock:
    def test_block_creation(self) -> None:
        """Test basic block creation."""
        block = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        assert block.label == BlockLabel("entry")
        assert len(block.instructions) == 0

    def test_block_all_instructions(self) -> None:
        """Test all_instructions includes terminator."""
        add_instr = BinaryInst(
            result=SSAName("%0"),
            op="add",
            left=SSARef(SSAName("%a")),
            right=Const(1, JCType.SHORT),
            ty=JCType.INT,
        )
        ret_instr = ReturnInst(value=SSARef(SSAName("%0")), ty=JCType.INT)

        block = Block(
            label=BlockLabel("entry"),
            instructions=(add_instr,),
            terminator=ret_instr,
        )

        all_instrs = list(block.all_instructions)
        assert len(all_instrs) == 2
        assert all_instrs[0] == add_instr
        assert all_instrs[1] == ret_instr

    def test_block_phi_instructions(self) -> None:
        """Test phi_instructions filters correctly."""
        phi1 = PhiInst(
            result=SSAName("%i"),
            incoming=(
                (Const(0, JCType.SHORT), BlockLabel("entry")),
                (SSARef(SSAName("%i.next")), BlockLabel("loop")),
            ),
            ty=JCType.INT,
        )
        phi2 = PhiInst(
            result=SSAName("%sum"),
            incoming=(
                (Const(0, JCType.SHORT), BlockLabel("entry")),
                (SSARef(SSAName("%sum.next")), BlockLabel("loop")),
            ),
            ty=JCType.INT,
        )
        add_instr = BinaryInst(
            result=SSAName("%i.next"),
            op="add",
            left=SSARef(SSAName("%i")),
            right=Const(1, JCType.SHORT),
            ty=JCType.INT,
        )

        block = Block(
            label=BlockLabel("loop"),
            instructions=(phi1, phi2, add_instr),
            terminator=BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
        )

        phis = list(block.phi_instructions)
        assert len(phis) == 2
        assert phis[0] == phi1
        assert phis[1] == phi2


class TestFunction:
    def test_function_creation(self) -> None:
        """Test basic function creation."""
        block = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test_func",
            params=(Parameter(SSAName("%x"), JCType.INT),),
            return_type=JCType.VOID,
            blocks=(block,),
        )
        assert func.name == "test_func"
        assert len(func.params) == 1
        assert func.return_type == JCType.VOID

    def test_function_entry_block(self) -> None:
        """Test entry_block property."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=BranchInst(cond=None, true_label=BlockLabel("exit"), false_label=None),
        )
        exit_block = Block(
            label=BlockLabel("exit"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry, exit_block),
        )

        assert func.entry_block.label == BlockLabel("entry")

    def test_function_block_map(self) -> None:
        """Test block_map property."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=BranchInst(cond=None, true_label=BlockLabel("exit"), false_label=None),
        )
        exit_block = Block(
            label=BlockLabel("exit"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry, exit_block),
        )

        block_map = func.block_map
        assert BlockLabel("entry") in block_map
        assert BlockLabel("exit") in block_map
        assert block_map[BlockLabel("entry")] == entry

    def test_block_map_lookup(self) -> None:
        """Test block_map lookup."""
        block = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(block,),
        )

        assert func.block_map[BlockLabel("entry")] == block

    def test_block_map_missing_raises_keyerror(self) -> None:
        """Test block_map raises KeyError for missing block."""
        block = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(block,),
        )

        with pytest.raises(KeyError):
            _ = func.block_map[BlockLabel("missing")]


class TestGlobal:
    def test_global_creation(self) -> None:
        """Test basic global creation."""
        gv = Global(
            name=GlobalName("@array"),
            llvm_type=LLVMType("[100 x i16]"),
            is_constant=False,
            initializer=ZeroInit(),
        )
        assert gv.name == GlobalName("@array")
        assert gv.llvm_type == "[100 x i16]"
        assert not gv.is_constant
        assert isinstance(gv.initializer, ZeroInit)


class TestGlobalInit:
    def test_zero_init(self) -> None:
        """Test ZeroInit."""
        init = ZeroInit()
        assert isinstance(init, ZeroInit)

    def test_int_array_init(self) -> None:
        """Test IntArrayInit."""
        init = IntArrayInit(values=(1, 2, 3), elem_type=JCType.SHORT)
        assert init.values == (1, 2, 3)
        assert init.elem_type == JCType.SHORT

    def test_byte_string_init(self) -> None:
        """Test ByteStringInit."""
        init = ByteStringInit(data=b"hello\x00")
        assert init.data == b"hello\x00"


class TestDecodeLLVMString:
    def test_decode_simple(self) -> None:
        """Test decoding simple string."""
        assert decode_llvm_string("hello") == b"hello"

    def test_decode_with_escapes(self) -> None:
        """Test decoding with hex escapes."""
        assert decode_llvm_string("hello\\00") == b"hello\x00"
        assert decode_llvm_string("\\0A\\0D") == b"\n\r"

    def test_decode_mixed(self) -> None:
        """Test decoding mixed content."""
        assert decode_llvm_string("a\\00b\\FFc") == b"a\x00b\xffc"


class TestModule:
    def test_module_creation(self) -> None:
        """Test basic module creation."""
        gv = Global(
            name=GlobalName("@x"),
            llvm_type=LLVMType("i32"),
            is_constant=False,
            initializer=None,
        )
        block = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="main",
            params=(),
            return_type=JCType.VOID,
            blocks=(block,),
        )
        module = Module(
            globals={GlobalName("@x"): gv},
            functions={"main": func},
        )

        assert GlobalName("@x") in module.globals
        assert "main" in module.functions


class TestValidatePhiLabels:
    def _make_func_with_phi(
        self,
        phi_incoming: tuple[tuple[Const | SSARef, BlockLabel], ...],
        block_labels: list[str],
        branches: dict[str, list[str]],
    ) -> Function:
        """Helper to create a function with a phi node for testing."""
        blocks: list[Block] = []

        for label_str in block_labels:
            label = BlockLabel(label_str)

            if label_str == "loop":
                # The loop block has the phi
                phi = PhiInst(
                    result=SSAName("%i"),
                    incoming=phi_incoming,
                    ty=JCType.INT,
                )
                instructions: tuple[PhiInst, ...] = (phi,)
            else:
                instructions = ()

            # Create terminator based on branches
            if label_str in branches:
                targets = branches[label_str]
                if len(targets) == 1:
                    terminator: ReturnInst | BranchInst = BranchInst(
                        cond=None,
                        true_label=BlockLabel(targets[0]),
                        false_label=None,
                    )
                else:
                    terminator = BranchInst(
                        cond=SSARef(SSAName("%cond")),
                        true_label=BlockLabel(targets[0]),
                        false_label=BlockLabel(targets[1]),
                    )
            else:
                terminator = ReturnInst(value=None, ty=JCType.VOID)

            blocks.append(Block(label=label, instructions=instructions, terminator=terminator))

        return Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=tuple(blocks),
        )

    def test_valid_phi_labels(self) -> None:
        """Test that valid phi labels pass validation."""
        func = self._make_func_with_phi(
            phi_incoming=(
                (Const(0, JCType.SHORT), BlockLabel("entry")),
                (SSARef(SSAName("%i.next")), BlockLabel("loop")),
            ),
            block_labels=["entry", "loop", "exit"],
            branches={
                "entry": ["loop"],
                "loop": ["loop", "exit"],
            },
        )

        # Should not raise
        validate_phi_labels(func)

    def test_phi_references_unknown_block(self) -> None:
        """Test that phi referencing unknown block fails."""
        func = self._make_func_with_phi(
            phi_incoming=(
                (Const(0, JCType.SHORT), BlockLabel("nonexistent")),  # Bad!
                (SSARef(SSAName("%i.next")), BlockLabel("loop")),
            ),
            block_labels=["entry", "loop"],
            branches={
                "entry": ["loop"],
                "loop": ["loop"],
            },
        )

        with pytest.raises(ModuleError, match="unknown block"):
            validate_phi_labels(func)

    def test_phi_references_non_predecessor(self) -> None:
        """Test that phi referencing non-predecessor block fails."""
        func = self._make_func_with_phi(
            phi_incoming=(
                (Const(0, JCType.SHORT), BlockLabel("entry")),
                (SSARef(SSAName("%i.next")), BlockLabel("exit")),  # exit doesn't branch to loop
            ),
            block_labels=["entry", "loop", "exit"],
            branches={
                "entry": ["loop"],
                "loop": ["exit"],  # loop -> exit, not exit -> loop
            },
        )

        with pytest.raises(ModuleError, match="not a predecessor"):
            validate_phi_labels(func)


class TestValidateBlockTerminators:
    def test_valid_branch_targets(self) -> None:
        """Test that valid branch targets pass validation."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=BranchInst(
                cond=SSARef(SSAName("%cond")),
                true_label=BlockLabel("then"),
                false_label=BlockLabel("else"),
            ),
        )
        then_block = Block(
            label=BlockLabel("then"),
            instructions=(),
            terminator=BranchInst(cond=None, true_label=BlockLabel("exit"), false_label=None),
        )
        else_block = Block(
            label=BlockLabel("else"),
            instructions=(),
            terminator=BranchInst(cond=None, true_label=BlockLabel("exit"), false_label=None),
        )
        exit_block = Block(
            label=BlockLabel("exit"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry, then_block, else_block, exit_block),
        )

        # Should not raise
        validate_block_terminators(func)

    def test_branch_to_unknown_block(self) -> None:
        """Test that branch to unknown block fails."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=BranchInst(cond=None, true_label=BlockLabel("missing"), false_label=None),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry,),
        )

        with pytest.raises(ModuleError, match="unknown block"):
            validate_block_terminators(func)

    def test_switch_targets(self) -> None:
        """Test switch validation."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=SwitchInst(
                value=SSARef(SSAName("%x")),
                default=BlockLabel("default"),
                cases=((0, BlockLabel("case0")), (1, BlockLabel("case1"))),
                ty=JCType.SHORT,
            ),
        )
        default = Block(
            label=BlockLabel("default"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        case0 = Block(
            label=BlockLabel("case0"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        case1 = Block(
            label=BlockLabel("case1"),
            instructions=(),
            terminator=ReturnInst(value=None, ty=JCType.VOID),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry, default, case0, case1),
        )

        # Should not raise
        validate_block_terminators(func)

    def test_switch_unknown_default(self) -> None:
        """Test switch with unknown default fails."""
        entry = Block(
            label=BlockLabel("entry"),
            instructions=(),
            terminator=SwitchInst(
                value=SSARef(SSAName("%x")),
                default=BlockLabel("missing"),
                cases=(),
                ty=JCType.SHORT,
            ),
        )
        func = Function(
            name="test",
            params=(),
            return_type=JCType.VOID,
            blocks=(entry,),
        )

        with pytest.raises(ModuleError, match="unknown block"):
            validate_block_terminators(func)


class TestModuleError:
    def test_module_error_formatting(self) -> None:
        """Test ModuleError string formatting."""
        err = ModuleError(
            message="Phi references unknown block",
            func_name="test_func",
            block_label=BlockLabel("loop"),
        )
        err_str = str(err)
        assert "Phi references unknown block" in err_str
        assert "test_func" in err_str
        assert "loop" in err_str

    def test_module_error_minimal(self) -> None:
        """Test ModuleError with minimal info."""
        err = ModuleError(message="Something went wrong")
        assert str(err) == "Something went wrong"
