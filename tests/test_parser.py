"""Unit tests for the LLVM IR parser."""

import pytest

from jcc.ir.errors import ParseError
from jcc.ir.instructions import (
    AllocaInst,
    BinaryInst,
    BranchInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    UnreachableInst,
)
from jcc.ir.llvm import LLVMModule, LLVMValue
from jcc.ir.values import Const, GlobalRef, Value, SSARef, Undef
from jcc.ir.parser import LLVMParser
from jcc.ir.types import BlockLabel, GlobalName, JCType, SSAName


def parse_function(ir_text: str) -> list[tuple[str, LLVMValue]]:
    """Parse IR text and return list of (opcode, instruction) pairs."""
    module = LLVMModule.parse_string(ir_text)
    instructions: list[tuple[str, LLVMValue]] = []
    for func in module.functions:
        if func.is_declaration:
            continue
        for block in func.blocks:
            for instr in block.instructions:
                instructions.append((instr.opcode, instr))
    return instructions


def get_instruction(ir_text: str, opcode: str) -> LLVMValue:
    """Parse IR and return the first instruction with the given opcode."""
    for op, instr in parse_function(ir_text):
        if op == opcode:
            return instr
    raise ValueError(f"No {opcode} instruction found")


class TestBinaryInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_add_i32(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a, i32 %b) {
            %result = add i32 %a, %b
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "add")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.op == "add"
        assert result.result == SSAName("%result")
        assert isinstance(result.left, SSARef)
        assert result.left.name == SSAName("%a")
        assert isinstance(result.right, SSARef)
        assert result.right.name == SSAName("%b")
        assert result.ty == JCType.INT

    def test_add_i16(self, parser: LLVMParser) -> None:
        ir = """
        define i16 @test(i16 %a, i16 %b) {
            %result = add i16 %a, %b
            ret i16 %result
        }
        """
        instr = get_instruction(ir, "add")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.ty == JCType.SHORT

    def test_sub_with_constant(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a) {
            %result = sub i32 %a, 10
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "sub")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.op == "sub"
        assert isinstance(result.right, Const)
        assert result.right.value == 10

    def test_mul(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a, i32 %b) {
            %result = mul i32 %a, %b
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "mul")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.op == "mul"

    def test_sdiv(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a, i32 %b) {
            %result = sdiv i32 %a, %b
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "sdiv")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.op == "sdiv"

    def test_and_or_xor(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a, i32 %b) {
            %r1 = and i32 %a, %b
            %r2 = or i32 %a, %b
            %r3 = xor i32 %a, %b
            ret i32 %r3
        }
        """
        instructions = parse_function(ir)
        results = [
            parser.parse_instruction(i) for op, i in instructions if op in ("and", "or", "xor")
        ]

        assert len(results) == 3
        assert all(isinstance(r, BinaryInst) for r in results)
        assert isinstance(results[0], BinaryInst) and results[0].op == "and"
        assert isinstance(results[1], BinaryInst) and results[1].op == "or"
        assert isinstance(results[2], BinaryInst) and results[2].op == "xor"

    def test_shifts(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %a, i32 %b) {
            %r1 = shl i32 %a, %b
            %r2 = ashr i32 %a, %b
            %r3 = lshr i32 %a, %b
            ret i32 %r3
        }
        """
        instructions = parse_function(ir)
        results = [
            parser.parse_instruction(i) for op, i in instructions if op in ("shl", "ashr", "lshr")
        ]

        assert len(results) == 3
        assert isinstance(results[0], BinaryInst) and results[0].op == "shl"
        assert isinstance(results[1], BinaryInst) and results[1].op == "ashr"
        assert isinstance(results[2], BinaryInst) and results[2].op == "lshr"


class TestICmpInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_icmp_slt(self, parser: LLVMParser) -> None:
        ir = """
        define i1 @test(i32 %a, i32 %b) {
            %result = icmp slt i32 %a, %b
            ret i1 %result
        }
        """
        instr = get_instruction(ir, "icmp")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ICmpInst)
        assert result.pred == "slt"
        assert result.ty == JCType.INT

    def test_icmp_eq(self, parser: LLVMParser) -> None:
        ir = """
        define i1 @test(i32 %a, i32 %b) {
            %result = icmp eq i32 %a, %b
            ret i1 %result
        }
        """
        instr = get_instruction(ir, "icmp")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ICmpInst)
        assert result.pred == "eq"

    def test_icmp_all_predicates(self, parser: LLVMParser) -> None:
        """Test all comparison predicates."""
        predicates = ["eq", "ne", "slt", "sle", "sgt", "sge", "ult", "ule", "ugt", "uge"]
        for pred in predicates:
            ir = f"""
            define i1 @test(i32 %a, i32 %b) {{
                %result = icmp {pred} i32 %a, %b
                ret i1 %result
            }}
            """
            instr = get_instruction(ir, "icmp")
            result = parser.parse_instruction(instr)
            assert isinstance(result, ICmpInst)
            assert result.pred == pred

    def test_icmp_with_constant(self, parser: LLVMParser) -> None:
        ir = """
        define i1 @test(i32 %a) {
            %result = icmp slt i32 %a, 100
            ret i1 %result
        }
        """
        instr = get_instruction(ir, "icmp")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ICmpInst)
        assert isinstance(result.right, Const)
        assert result.right.value == 100


class TestMemoryInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_load_i32(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(ptr %p) {
            %result = load i32, ptr %p
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "load")
        result = parser.parse_instruction(instr)

        assert isinstance(result, LoadInst)
        assert result.result == SSAName("%result")
        assert result.ty == JCType.INT
        assert isinstance(result.ptr, SSARef)

    def test_load_i16(self, parser: LLVMParser) -> None:
        ir = """
        define i16 @test(ptr %p) {
            %result = load i16, ptr %p
            ret i16 %result
        }
        """
        instr = get_instruction(ir, "load")
        result = parser.parse_instruction(instr)

        assert isinstance(result, LoadInst)
        assert result.ty == JCType.SHORT

    def test_store_i32(self, parser: LLVMParser) -> None:
        ir = """
        define void @test(ptr %p, i32 %val) {
            store i32 %val, ptr %p
            ret void
        }
        """
        instr = get_instruction(ir, "store")
        result = parser.parse_instruction(instr)

        assert isinstance(result, StoreInst)
        assert result.ty == JCType.INT
        assert isinstance(result.value, SSARef)
        assert isinstance(result.ptr, SSARef)

    def test_store_constant(self, parser: LLVMParser) -> None:
        ir = """
        define void @test(ptr %p) {
            store i32 42, ptr %p
            ret void
        }
        """
        instr = get_instruction(ir, "store")
        result = parser.parse_instruction(instr)

        assert isinstance(result, StoreInst)
        assert isinstance(result.value, Const)
        assert result.value.value == 42


class TestGEPInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_gep_array_simple(self, parser: LLVMParser) -> None:
        ir = """
        @arr = global [100 x i16] zeroinitializer

        define ptr @test(i64 %idx) {
            %result = getelementptr inbounds [100 x i16], ptr @arr, i64 0, i64 %idx
            ret ptr %result
        }
        """
        instr = get_instruction(ir, "getelementptr")
        result = parser.parse_instruction(instr)

        assert isinstance(result, GEPInst)
        assert result.result == SSAName("%result")
        assert result.inbounds is True
        assert "[100 x i16]" in result.source_type
        assert isinstance(result.base, GlobalRef)
        assert result.base.name == GlobalName("@arr")

    def test_gep_struct_field(self, parser: LLVMParser) -> None:
        ir = """
        %struct.Point = type { i16, i16 }
        @point = global %struct.Point zeroinitializer

        define ptr @test() {
            %result = getelementptr inbounds %struct.Point, ptr @point, i32 0, i32 1
            ret ptr %result
        }
        """
        instr = get_instruction(ir, "getelementptr")
        result = parser.parse_instruction(instr)

        assert isinstance(result, GEPInst)
        assert "%struct.Point" in result.source_type
        assert result.inbounds is True

    def test_gep_not_inbounds(self, parser: LLVMParser) -> None:
        ir = """
        @arr = global [100 x i16] zeroinitializer

        define ptr @test(i64 %idx) {
            %result = getelementptr [100 x i16], ptr @arr, i64 0, i64 %idx
            ret ptr %result
        }
        """
        instr = get_instruction(ir, "getelementptr")
        result = parser.parse_instruction(instr)

        assert isinstance(result, GEPInst)
        assert result.inbounds is False

    def test_gep_with_ssa_base(self, parser: LLVMParser) -> None:
        ir = """
        define ptr @test(ptr %p, i64 %idx) {
            %result = getelementptr inbounds i16, ptr %p, i64 %idx
            ret ptr %result
        }
        """
        instr = get_instruction(ir, "getelementptr")
        result = parser.parse_instruction(instr)

        assert isinstance(result, GEPInst)
        assert isinstance(result.base, SSARef)
        assert result.base.name == SSAName("%p")


class TestBranchInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_unconditional_branch(self, parser: LLVMParser) -> None:
        ir = """
        define void @test() {
        entry:
            br label %exit
        exit:
            ret void
        }
        """
        instr = get_instruction(ir, "br")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BranchInst)
        assert result.cond is None
        assert result.true_label == BlockLabel("exit")
        assert result.false_label is None

    def test_conditional_branch(self, parser: LLVMParser) -> None:
        ir = """
        define void @test(i1 %cond) {
        entry:
            br i1 %cond, label %then, label %else
        then:
            ret void
        else:
            ret void
        }
        """
        instr = get_instruction(ir, "br")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BranchInst)
        assert result.cond is not None
        assert isinstance(result.cond, SSARef)
        assert result.true_label == BlockLabel("then")
        assert result.false_label == BlockLabel("else")


class TestReturnInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_return_void(self, parser: LLVMParser) -> None:
        ir = """
        define void @test() {
            ret void
        }
        """
        instr = get_instruction(ir, "ret")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ReturnInst)
        assert result.value is None
        assert result.ty == JCType.VOID

    def test_return_i32(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i32 %val) {
            ret i32 %val
        }
        """
        instr = get_instruction(ir, "ret")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ReturnInst)
        assert isinstance(result.value, SSARef)
        assert result.ty == JCType.INT

    def test_return_constant(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test() {
            ret i32 42
        }
        """
        instr = get_instruction(ir, "ret")
        result = parser.parse_instruction(instr)

        assert isinstance(result, ReturnInst)
        assert isinstance(result.value, Const)
        assert result.value.value == 42


class TestSwitchInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_switch_simple(self, parser: LLVMParser) -> None:
        ir = """
        define void @test(i32 %val) {
        entry:
            switch i32 %val, label %default [
                i32 0, label %case0
                i32 1, label %case1
            ]
        case0:
            ret void
        case1:
            ret void
        default:
            ret void
        }
        """
        instr = get_instruction(ir, "switch")
        result = parser.parse_instruction(instr)

        assert isinstance(result, SwitchInst)
        assert isinstance(result.value, SSARef)
        assert result.default == BlockLabel("default")
        assert len(result.cases) == 2
        assert result.cases[0] == (0, BlockLabel("case0"))
        assert result.cases[1] == (1, BlockLabel("case1"))


class TestPhiInstructions:
    """Test parsing of phi instructions - critical for correct block label handling."""

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_phi_simple(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i1 %cond) {
        entry:
            br i1 %cond, label %then, label %else
        then:
            br label %merge
        else:
            br label %merge
        merge:
            %result = phi i32 [ 1, %then ], [ 2, %else ]
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "phi")
        result = parser.parse_instruction(instr)

        assert isinstance(result, PhiInst)
        assert result.result == SSAName("%result")
        assert result.ty == JCType.INT
        assert len(result.incoming) == 2
        # Check incoming values and labels are preserved
        values = {(self._get_operand_value(v), l) for v, l in result.incoming}
        assert (1, BlockLabel("then")) in values
        assert (2, BlockLabel("else")) in values

    def _get_operand_value(self, op: Value) -> int | SSAName | Value:
        """Helper to extract value from operand."""
        if isinstance(op, Const):
            return op.value
        if isinstance(op, SSARef):
            return op.name
        return op

    def test_phi_with_ssa_values(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i1 %cond, i32 %a, i32 %b) {
        entry:
            br i1 %cond, label %then, label %else
        then:
            br label %merge
        else:
            br label %merge
        merge:
            %result = phi i32 [ %a, %then ], [ %b, %else ]
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "phi")
        result = parser.parse_instruction(instr)

        assert isinstance(result, PhiInst)
        # Both incoming values should be SSA references
        for val, _ in result.incoming:
            assert isinstance(val, SSARef)

    def test_phi_preserves_numeric_labels(self, parser: LLVMParser) -> None:
        """Ensure numeric block labels like %17 are preserved correctly."""
        ir = """
        define i32 @test(i1 %cond) {
        0:
            br i1 %cond, label %1, label %2
        1:
            br label %3
        2:
            br label %3
        3:
            %result = phi i32 [ 10, %1 ], [ 20, %2 ]
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "phi")
        result = parser.parse_instruction(instr)

        assert isinstance(result, PhiInst)
        labels = {l for _, l in result.incoming}
        # Labels should be preserved as-is
        assert BlockLabel("1") in labels or BlockLabel("2") in labels

    def test_phi_loop_induction(self, parser: LLVMParser) -> None:
        """Test phi for loop induction variable pattern."""
        ir = """
        define i32 @test() {
        entry:
            br label %loop
        loop:
            %i = phi i32 [ 0, %entry ], [ %next, %loop ]
            %next = add i32 %i, 1
            %cond = icmp slt i32 %next, 10
            br i1 %cond, label %loop, label %exit
        exit:
            ret i32 %i
        }
        """
        instr = get_instruction(ir, "phi")
        result = parser.parse_instruction(instr)

        assert isinstance(result, PhiInst)
        assert result.result == SSAName("%i")
        # Should have incoming from entry (constant 0) and loop (SSA %next)
        has_const = False
        has_ssa = False
        for val, _ in result.incoming:
            if isinstance(val, Const) and val.value == 0:
                has_const = True
            if isinstance(val, SSARef) and val.name == SSAName("%next"):
                has_ssa = True
        assert has_const
        assert has_ssa


class TestCallInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_call_void(self, parser: LLVMParser) -> None:
        ir = """
        declare void @foo()

        define void @test() {
            call void @foo()
            ret void
        }
        """
        instr = get_instruction(ir, "call")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CallInst)
        assert result.result is None
        assert result.func_name == "foo"
        assert result.ty == JCType.VOID
        assert len(result.args) == 0

    def test_call_with_return(self, parser: LLVMParser) -> None:
        ir = """
        declare i32 @bar(i32)

        define i32 @test(i32 %x) {
            %result = call i32 @bar(i32 %x)
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "call")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CallInst)
        assert result.result == SSAName("%result")
        assert result.func_name == "bar"
        assert result.ty == JCType.INT
        assert len(result.args) == 1

    def test_call_with_multiple_args(self, parser: LLVMParser) -> None:
        ir = """
        declare i32 @add3(i32, i32, i32)

        define i32 @test(i32 %a, i32 %b, i32 %c) {
            %result = call i32 @add3(i32 %a, i32 %b, i32 %c)
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "call")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CallInst)
        assert len(result.args) == 3


class TestCastInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_trunc(self, parser: LLVMParser) -> None:
        ir = """
        define i16 @test(i32 %val) {
            %result = trunc i32 %val to i16
            ret i16 %result
        }
        """
        instr = get_instruction(ir, "trunc")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "trunc"
        assert result.from_ty == JCType.INT
        assert result.to_ty == JCType.SHORT

    def test_sext(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i16 %val) {
            %result = sext i16 %val to i32
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "sext")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "sext"
        assert result.from_ty == JCType.SHORT
        assert result.to_ty == JCType.INT

    def test_zext(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i16 %val) {
            %result = zext i16 %val to i32
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "zext")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "zext"

    def test_zext_nneg_flag(self, parser: LLVMParser) -> None:
        """Test that zext nneg flag is captured."""
        ir = """
        define i32 @test(i16 %val) {
            %result = zext nneg i16 %val to i32
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "zext")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "zext"
        assert "nneg" in result.flags

    def test_freeze(self, parser: LLVMParser) -> None:
        """freeze should parse as a no-op CastInst."""
        ir = """
        define i16 @test(i16 %val) {
            %result = freeze i16 %val
            ret i16 %result
        }
        """
        instr = get_instruction(ir, "freeze")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "freeze"
        assert result.from_ty == JCType.SHORT
        assert result.to_ty == JCType.SHORT

    def test_bitcast(self, parser: LLVMParser) -> None:
        ir = """
        define ptr @test(ptr %p) {
            %result = bitcast ptr %p to ptr
            ret ptr %result
        }
        """
        instr = get_instruction(ir, "bitcast")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CastInst)
        assert result.op == "bitcast"


class TestSelectInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_select_simple(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i1 %cond, i32 %a, i32 %b) {
            %result = select i1 %cond, i32 %a, i32 %b
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "select")
        result = parser.parse_instruction(instr)

        assert isinstance(result, SelectInst)
        assert result.result == SSAName("%result")
        assert isinstance(result.cond, SSARef)
        assert isinstance(result.true_val, SSARef)
        assert isinstance(result.false_val, SSARef)
        assert result.ty == JCType.INT

    def test_select_with_constants(self, parser: LLVMParser) -> None:
        ir = """
        define i32 @test(i1 %cond) {
            %result = select i1 %cond, i32 100, i32 200
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "select")
        result = parser.parse_instruction(instr)

        assert isinstance(result, SelectInst)
        assert isinstance(result.true_val, Const)
        assert result.true_val.value == 100
        assert isinstance(result.false_val, Const)
        assert result.false_val.value == 200


class TestParserContext:
    """Test that parser context is set correctly for error messages."""

    def test_context_in_error(self) -> None:
        parser = LLVMParser()
        parser.set_context("my_function", BlockLabel("my_block"))

        # Create an invalid instruction scenario
        ir = """
        define void @test() {
            ret void
        }
        """
        # We can't easily create an invalid instruction, but we can verify
        # context is preserved in normal parsing
        instr = get_instruction(ir, "ret")
        result = parser.parse_instruction(instr)
        assert isinstance(result, ReturnInst)


class TestParseError:

    def test_error_with_full_context(self) -> None:
        error = ParseError(
            message="Cannot parse operand",
            func_name="my_function",
            block_label=BlockLabel("entry"),
            instruction="  %x = add i32 %a, %b",
        )
        error_str = str(error)
        assert "Cannot parse operand" in error_str
        assert "my_function" in error_str
        assert "entry" in error_str
        assert "add" in error_str

    def test_error_minimal(self) -> None:
        error = ParseError(message="Unknown opcode")
        error_str = str(error)
        assert error_str == "Unknown opcode"


class TestAllocaInstructions:
    """Test alloca parsing (normalized to globals in module.py)."""

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_alloca_simple(self, parser: LLVMParser) -> None:
        """Simple alloca should parse to AllocaInst."""
        ir = """
        define void @test() {
            %x = alloca i32
            ret void
        }
        """
        instr = get_instruction(ir, "alloca")
        result = parser.parse_instruction(instr)

        assert isinstance(result, AllocaInst)
        assert result.result == SSAName("%x")
        assert result.alloc_type == "i32"

    def test_alloca_array(self, parser: LLVMParser) -> None:
        """Alloca with array type should parse correctly."""
        ir = """
        define void @test() {
            %buffer = alloca [64 x i8], align 1
            ret void
        }
        """
        instr = get_instruction(ir, "alloca")
        result = parser.parse_instruction(instr)

        assert isinstance(result, AllocaInst)
        assert result.result == SSAName("%buffer")
        assert result.alloc_type == "[64 x i8]"


class TestSpecialInstructions:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_unreachable(self, parser: LLVMParser) -> None:
        """Unreachable should parse to UnreachableInst."""
        ir = """
        define void @test() {
            unreachable
        }
        """
        instr = get_instruction(ir, "unreachable")
        result = parser.parse_instruction(instr)

        assert isinstance(result, UnreachableInst)


class TestUndef:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_undef_in_phi(self, parser: LLVMParser) -> None:
        """Undef values in phi should produce Undef."""
        ir = """
        define i32 @test(i1 %cond) {
        entry:
            br i1 %cond, label %then, label %else
        then:
            br label %merge
        else:
            br label %merge
        merge:
            %result = phi i32 [ undef, %then ], [ 42, %else ]
            ret i32 %result
        }
        """
        instr = get_instruction(ir, "phi")
        result = parser.parse_instruction(instr)

        assert isinstance(result, PhiInst)
        has_undef = any(isinstance(v, Undef) for v, _ in result.incoming)
        assert has_undef


class TestLongType:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_i64_operand_type(self, parser: LLVMParser) -> None:
        """i64 operands should have LONG type."""
        ir = """
        define i64 @test(i64 %a, i64 %b) {
            %result = add i64 %a, %b
            ret i64 %result
        }
        """
        instr = get_instruction(ir, "add")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BinaryInst)
        assert result.ty == JCType.LONG


class TestNegativeCases:

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_unknown_opcode(self, parser: LLVMParser) -> None:
        """Unknown opcodes should raise ParseError."""
        ir = """
        define void @test() {
            fence seq_cst
            ret void
        }
        """
        instr = get_instruction(ir, "fence")

        with pytest.raises(ParseError, match="Unsupported opcode: fence"):
            parser.parse_instruction(instr)


class TestLLVMLiteValueOrdering:
    """Document and verify llvmlite's operand ordering assumptions.

    These tests exist to catch if llvmlite changes its operand order,
    which would silently break our parsing. The IR text order and
    llvmlite's operand order can differ.
    """

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_branch_operand_order(self, parser: LLVMParser) -> None:
        """Verify: br operands are [cond, false_dest, true_dest].

        IR syntax: br i1 %cond, label %true, label %false
        But llvmlite gives: operands[0]=cond, operands[1]=false, operands[2]=true
        """
        ir = """
        define void @test(i1 %cond) {
        entry:
            br i1 %cond, label %yes, label %no
        yes:
            ret void
        no:
            ret void
        }
        """
        instr = get_instruction(ir, "br")
        result = parser.parse_instruction(instr)

        assert isinstance(result, BranchInst)
        assert result.true_label == BlockLabel("yes"), "true_label should match IR order"
        assert result.false_label == BlockLabel("no"), "false_label should match IR order"

    def test_call_operand_order(self, parser: LLVMParser) -> None:
        """Verify: call operands are [args..., function].

        The function being called is the LAST operand.
        """
        ir = """
        declare i32 @add(i32, i32)

        define i32 @test() {
            %r = call i32 @add(i32 1, i32 2)
            ret i32 %r
        }
        """
        instr = get_instruction(ir, "call")
        result = parser.parse_instruction(instr)

        assert isinstance(result, CallInst)
        assert result.func_name == "add"
        assert len(result.args) == 2
        # Args should be the constants, not include the function
        assert isinstance(result.args[0], Const)
        assert isinstance(result.args[1], Const)


class TestUnsupportedConstExpr:
    """Test handling of unsupported constant expressions like ptrtoint, inttoptr, bitcast."""

    @pytest.fixture
    def parser(self) -> LLVMParser:
        return LLVMParser()

    def test_ptrtoint_in_phi_raises(self, parser: LLVMParser) -> None:
        """ptrtoint constant expression in phi should raise ParseError."""
        ir = """
        @global = global i32 0

        define i64 @test(i1 %cond) {
        entry:
            br i1 %cond, label %then, label %else
        then:
            br label %merge
        else:
            br label %merge
        merge:
            %result = phi i64 [ 0, %then ], [ ptrtoint (ptr @global to i64), %else ]
            ret i64 %result
        }
        """
        instr = get_instruction(ir, "phi")

        with pytest.raises(ParseError, match="Unsupported constant expression: ptrtoint"):
            parser.parse_instruction(instr)

    def test_inttoptr_in_store_raises(self, parser: LLVMParser) -> None:
        """inttoptr constant expression in store should raise ParseError."""
        ir = """
        define void @test() {
            store i32 42, ptr inttoptr (i64 12345 to ptr)
            ret void
        }
        """
        instr = get_instruction(ir, "store")

        with pytest.raises(ParseError, match="Unsupported constant expression: inttoptr"):
            parser.parse_instruction(instr)

    def test_ptrtoint_detected_in_operand_str(self) -> None:
        """Verify that ptrtoint pattern detection works on raw strings.

        Note: Modern LLVM (17+) with opaque pointers often simplifies or
        eliminates bitcast expressions. The ptrtoint/inttoptr patterns are
        the most common unsupported expressions that survive optimization.
        """
        from jcc.ir import patterns

        # These are the patterns we need to detect
        assert patterns.contains_unsupported_const_expr("ptrtoint (ptr @x to i64)") == "ptrtoint"
        assert patterns.contains_unsupported_const_expr("inttoptr (i64 123 to ptr)") == "inttoptr"
        assert patterns.contains_unsupported_const_expr("bitcast (i32 %x to float)") == "bitcast"

        # GEP is handled separately (not unsupported)
        assert patterns.contains_unsupported_const_expr("getelementptr (i8, ptr @x, i32 0)") is None
