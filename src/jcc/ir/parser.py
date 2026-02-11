"""Centralized LLVM IR parsing.

This module orchestrates parsing of LLVM IR into typed instruction objects.
It uses:
- patterns module for all regex-based string parsing
- LLVMValue wrapper for typed llvmlite access

No other module should use regex on LLVM IR or interact directly with llvmlite.
"""

from typing import cast

from jcc.ir.errors import ParseError
from jcc.ir.instructions import (
    AllocaInst,
    BinaryInst,
    BinaryOp,
    BranchInst,
    CallInst,
    CastInst,
    CastOp,
    GEPInst,
    ICmpInst,
    ICmpPred,
    Instruction,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    UnreachableInst,
)
from jcc.ir.llvm import LLVMValue
from jcc.ir.values import (
    Const,
    GlobalRef,
    InlineGEP,
    Null,
    Value,
    SSARef,
    Undef,
)
from jcc.ir import patterns
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName, map_llvm_type


# Known opcodes we handle explicitly
_BINARY_OPS: frozenset[str] = frozenset(
    ["add", "sub", "mul", "sdiv", "udiv", "srem", "urem", "and", "or", "xor", "shl", "ashr", "lshr"]
)

_CAST_OPS: frozenset[str] = frozenset(["trunc", "sext", "zext", "bitcast", "ptrtoint", "inttoptr"])


class LLVMParser:
    """Parses LLVM IR into typed instruction objects.

    Uses patterns module for regex-based text extraction and
    LLVMValue typed wrappers for llvmlite access.

    Usage:
        parser = LLVMParser()
        for instr in block.instructions:
            parsed = parser.parse_instruction(instr)
    """

    def __init__(self) -> None:
        self._func_name: str | None = None
        self._block_label: BlockLabel | None = None

    # === Context Management ===

    def set_context(self, func_name: str | None, block_label: BlockLabel | None = None) -> None:
        """Set context for error messages."""
        self._func_name = func_name
        self._block_label = block_label

    def parse_instruction(self, instr: LLVMValue) -> Instruction:
        """Parse LLVM instruction into typed representation."""
        opcode = instr.opcode

        try:
            # Handle known opcodes explicitly
            if opcode in _BINARY_OPS:
                return self._parse_binary(instr, cast(BinaryOp, opcode))
            if opcode == "icmp":
                return self._parse_icmp(instr)
            if opcode == "load":
                return self._parse_load(instr)
            if opcode == "store":
                return self._parse_store(instr)
            if opcode == "getelementptr":
                return self._parse_gep(instr)
            if opcode == "br":
                return self._parse_branch(instr)
            if opcode == "ret":
                return self._parse_return(instr)
            if opcode == "switch":
                return self._parse_switch(instr)
            if opcode == "phi":
                return self._parse_phi(instr)
            if opcode == "call":
                return self._parse_call(instr)
            if opcode in _CAST_OPS:
                return self._parse_cast(instr, cast(CastOp, opcode))
            if opcode == "freeze":
                # freeze stops undef/poison propagation — no-op for us
                return self._parse_cast(instr, "freeze")
            if opcode == "select":
                return self._parse_select(instr)
            if opcode == "unreachable":
                return UnreachableInst()
            if opcode == "alloca":
                return self._parse_alloca(instr)

            # Unknown opcode - fail fast
            raise ParseError(
                f"Unsupported opcode: {opcode}",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=str(instr),
            )

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(
                f"Failed to parse instruction: {e}",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=str(instr),
            ) from e

    # === Binary Operations ===

    def _parse_binary(self, instr: LLVMValue, op: BinaryOp) -> BinaryInst:
        """Parse binary arithmetic/logic instruction."""
        result = self._get_result_name(instr)
        operands = list(instr.operands)
        assert len(operands) == 2, f"Binary op expects 2 operands, got {len(operands)}"
        left = self._parse_operand(operands[0])
        right = self._parse_operand(operands[1])
        ty = self._map_type(operands[0].type)
        return BinaryInst(result=result, op=op, left=left, right=right, ty=ty)

    # === Comparison ===

    def _parse_icmp(self, instr: LLVMValue) -> ICmpInst:
        """Parse icmp instruction, handling LLVM 19+ modifiers."""
        instr_str = str(instr)

        pred_str = patterns.parse_icmp_predicate(instr_str)
        if not pred_str:
            raise ParseError(
                "Cannot parse icmp predicate",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=instr_str,
            )
        pred = cast(ICmpPred, pred_str)

        result = self._get_result_name(instr)
        operands = list(instr.operands)
        assert len(operands) == 2, f"icmp expects 2 operands, got {len(operands)}"
        left = self._parse_operand(operands[0])
        right = self._parse_operand(operands[1])
        ty = self._map_type(operands[0].type)

        return ICmpInst(result=result, pred=pred, left=left, right=right, ty=ty)

    # === Memory ===

    def _parse_load(self, instr: LLVMValue) -> LoadInst:
        """Parse load instruction."""
        result = self._get_result_name(instr)
        operands = list(instr.operands)
        ptr = self._parse_operand(operands[0])
        ty = self._map_type(instr.type)
        return LoadInst(result=result, ptr=ptr, ty=ty)

    def _parse_store(self, instr: LLVMValue) -> StoreInst:
        """Parse store instruction."""
        operands = list(instr.operands)
        assert len(operands) == 2, f"store expects 2 operands, got {len(operands)}"
        value = self._parse_operand(operands[0])
        ptr = self._parse_operand(operands[1])
        ty = self._map_type(operands[0].type)
        return StoreInst(value=value, ptr=ptr, ty=ty)

    def _parse_gep(self, instr: LLVMValue) -> GEPInst:
        """Parse getelementptr instruction."""
        instr_str = str(instr)

        source_type = patterns.parse_gep_source_type(instr_str)
        result = self._get_result_name(instr)
        operands = list(instr.operands)
        base = self._parse_operand(operands[0])
        indices = tuple(self._parse_operand(op) for op in operands[1:])
        inbounds = patterns.has_keyword(instr_str, "inbounds")

        return GEPInst(
            result=result,
            base=base,
            indices=indices,
            source_type=LLVMType(source_type),
            inbounds=inbounds,
        )

    # === Control Flow ===

    def _parse_branch(self, instr: LLVMValue) -> BranchInst:
        """Parse branch instruction (conditional or unconditional)."""
        operands = list(instr.operands)

        if len(operands) == 1:
            # Unconditional branch
            label = self._extract_label(operands[0])
            return BranchInst(cond=None, true_label=label, false_label=None)
        else:
            # Conditional branch
            # llvmlite operand order: [0] = cond, [1] = false dest, [2] = true dest
            cond = self._parse_operand(operands[0])
            true_label = self._extract_label(operands[2])
            false_label = self._extract_label(operands[1])
            return BranchInst(cond=cond, true_label=true_label, false_label=false_label)

    def _parse_return(self, instr: LLVMValue) -> ReturnInst:
        """Parse return instruction."""
        operands = list(instr.operands)
        if operands:
            value = self._parse_operand(operands[0])
            ty = self._map_type(operands[0].type)
            return ReturnInst(value=value, ty=ty)
        else:
            return ReturnInst(value=None, ty=JCType.VOID)

    def _parse_switch(self, instr: LLVMValue) -> SwitchInst:
        """Parse switch instruction."""
        instr_str = str(instr)
        operands = list(instr.operands)

        value = self._parse_operand(operands[0])
        ty = self._map_type(operands[0].type)
        default = self._extract_label(operands[1])
        cases = tuple(patterns.parse_switch_cases(instr_str))

        return SwitchInst(value=value, default=default, cases=cases, ty=ty)

    # === Phi ===

    def _parse_phi(self, instr: LLVMValue) -> PhiInst:
        """Parse phi with preserved block labels."""
        instr_str = str(instr)
        result = self._get_result_name(instr)
        ty = self._map_type(instr.type)

        incoming_raw = patterns.parse_phi_incoming(instr_str)
        if not incoming_raw:
            raise ParseError(
                "No incoming values found in phi",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=instr_str,
            )

        incoming: list[tuple[Value, BlockLabel]] = []
        for value_str, label_str in incoming_raw:
            value = self._parse_value_from_string(value_str, ty)
            label = BlockLabel(label_str)
            incoming.append((value, label))

        return PhiInst(result=result, incoming=tuple(incoming), ty=ty)

    # === Calls ===

    def _parse_call(self, instr: LLVMValue) -> CallInst:
        """Parse function call."""
        instr_str = str(instr)

        func_name = patterns.parse_call_func_name(instr_str)
        if not func_name:
            raise ParseError(
                "Cannot extract function name from call",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=instr_str,
            )

        result: SSAName | None = None
        ty = self._map_type(instr.type)
        if ty != JCType.VOID:
            result = self._get_result_name(instr)

        operands = list(instr.operands)
        # The last operand is the function itself, skip it
        args = tuple(self._parse_operand(op) for op in operands[:-1])

        return CallInst(result=result, func_name=func_name, args=args, ty=ty)

    # === Casts ===

    def _parse_cast(self, instr: LLVMValue, op: CastOp) -> CastInst:
        """Parse cast instruction, capturing flags like 'nneg'."""
        instr_str = str(instr)
        result = self._get_result_name(instr)
        operands = list(instr.operands)
        operand = self._parse_operand(operands[0])
        from_ty = self._map_type(operands[0].type)
        to_ty = self._map_type(instr.type)

        flags: set[str] = set()
        if op == "zext" and patterns.has_keyword(instr_str, "nneg"):
            flags.add("nneg")
        if op == "sext" and str(operands[0].type).strip() == "i1":
            flags.add("from_i1")

        return CastInst(
            result=result,
            op=op,
            operand=operand,
            from_ty=from_ty,
            to_ty=to_ty,
            flags=frozenset(flags),
        )

    # === Select ===

    def _parse_select(self, instr: LLVMValue) -> SelectInst:
        """Parse select instruction."""
        result = self._get_result_name(instr)
        operands = list(instr.operands)
        assert len(operands) == 3, f"select expects 3 operands, got {len(operands)}"
        cond = self._parse_operand(operands[0])
        true_val = self._parse_operand(operands[1])
        false_val = self._parse_operand(operands[2])
        ty = self._map_type(operands[1].type)
        return SelectInst(
            result=result,
            cond=cond,
            true_val=true_val,
            false_val=false_val,
            ty=ty,
        )

    # === Alloca ===

    def _parse_alloca(self, instr: LLVMValue) -> AllocaInst:
        """Parse alloca instruction.

        Allocas are parsed here but normalized to synthetic globals
        during module construction.
        """
        instr_str = str(instr)
        result = self._get_result_name(instr)

        alloc_type = patterns.parse_alloca_type(instr_str)
        if not alloc_type:
            raise ParseError(
                "Cannot parse alloca type",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=instr_str,
            )

        return AllocaInst(result=result, alloc_type=LLVMType(alloc_type))

    # === Helper Methods ===

    def _get_result_name(self, instr: LLVMValue) -> SSAName:
        """Extract the result SSA name from an instruction."""
        instr_str = str(instr)
        name = patterns.extract_ssa_def(instr_str)
        if not name:
            raise ParseError(
                "Cannot extract result name",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=instr_str,
            )
        return name

    def _parse_operand(self, op: LLVMValue) -> Value:
        """Parse an operand from an LLVMValue object.

        Uses llvmlite API methods when available, with string parsing as fallback.
        The string representation may have type prefixes like 'ptr %foo' or 'i32 42',
        so we use regex extraction methods that find patterns anywhere in the string.

        For parsing clean value strings (like phi incoming values), use
        _parse_value_from_string instead.
        """
        op_str = str(op)

        # Check for SSA definition first - handles cases where str(op) returns
        # the full instruction like "%21 = getelementptr..." for a GEP result
        ssa_name = patterns.extract_ssa_def(op_str)
        if ssa_name:
            return SSARef(name=ssa_name)

        # Check for unsupported constant expressions, GEPs, globals, typed ints
        result = self._parse_value_core(op_str)
        if result is not None:
            return result

        # Try API-based extraction (preferred when available)
        const_val = op.get_constant_value()
        if const_val is not None:
            ty = self._map_type(op.type)
            return Const(value=const_val, ty=ty)

        # Try name-based SSA extraction
        name = op.name
        if name:
            ssa = SSAName("%" + name if not name.startswith("%") else name)
            return SSARef(name=ssa)

        # Try regex-based SSA extraction
        ssa_ref = patterns.extract_ssa_ref(op_str)
        if ssa_ref:
            return SSARef(name=ssa_ref)

        # Special constants (as keywords since string may have type prefix)
        if patterns.has_keyword(op_str, "true"):
            return Const(value=1, ty=JCType.BYTE)
        if patterns.has_keyword(op_str, "false"):
            return Const(value=0, ty=JCType.BYTE)
        if patterns.has_keyword(op_str, "undef") or patterns.has_keyword(op_str, "poison"):
            ty = self._map_type(op.type)
            return Undef(ty=ty)
        if patterns.has_keyword(op_str, "null"):
            return Null()

        raise ParseError(
            f"Cannot parse operand: {op_str[:100]}",
            func_name=self._func_name,
            block_label=self._block_label,
        )

    def _parse_value_from_string(self, s: str, ty: JCType) -> Value:
        """Parse a value from a clean string representation.

        Used for phi incoming values which are extracted via balanced parsing
        and are clean values like '%foo', '@bar', '42', 'null' - NOT type-prefixed
        like 'ptr %foo'. For type-prefixed strings from llvmlite, use _parse_operand.

        Args:
            s: The value string to parse
            ty: The expected type (from phi instruction or context)
        """
        s = s.strip()

        # Try shared string-based parsing
        result = self._parse_value_core(s)
        if result is not None:
            return result

        # Try parsing as plain integer (phi values may be bare numbers)
        try:
            return Const(value=int(s), ty=ty)
        except ValueError:
            pass

        # Special constants (exact match for clean strings)
        if s == "true":
            return Const(value=1, ty=JCType.BYTE)
        if s == "false":
            return Const(value=0, ty=JCType.BYTE)
        if s in ("undef", "poison"):
            return Undef(ty=ty)
        if s == "null":
            return Null()

        raise ParseError(
            f"Cannot parse operand: {s[:100]}",
            func_name=self._func_name,
            block_label=self._block_label,
        )

    def _parse_value_core(self, s: str) -> Value | None:
        """Core value parsing from string. Returns None if can't parse.

        Handles patterns common to both clean strings and type-prefixed strings:
        - SSA references (%name)
        - Global references (@name)
        - Inline GEP constant expressions
        - Unsupported constant expressions
        - Integer constants with type prefix (i32 42)
        """
        # SSA reference
        if s.startswith("%"):
            return SSARef(name=SSAName(s))

        # Global reference
        if s.startswith("@"):
            global_name = patterns.extract_global_ref(s)
            if global_name:
                return GlobalRef(name=global_name)
            return None

        # Inline GEP constant expression
        # Handle both "getelementptr ..." and "ptr getelementptr ..." forms
        if s.startswith("getelementptr"):
            return self._parse_inline_gep(s)
        if s.startswith("ptr getelementptr"):
            # Strip the "ptr " prefix and parse the GEP
            return self._parse_inline_gep(s[4:])

        # Unsupported constant expressions - fail fast
        unsupported = patterns.contains_unsupported_const_expr(s)
        if unsupported:
            raise ParseError(
                f"Unsupported constant expression: {unsupported}",
                func_name=self._func_name,
                block_label=self._block_label,
                instruction=s[:100],
            )

        # Integer constant with type prefix (i32 42)
        typed_const = patterns.extract_typed_const(s)
        if typed_const is not None:
            type_str, value = typed_const
            ty = self._map_type(LLVMType(type_str))
            return Const(value=value, ty=ty)

        return None

    def _parse_inline_gep(self, op_str: str) -> InlineGEP:
        """Parse an inline GEP constant expression using recursive descent.

        Parses components in order: source_type, base, indices.
        If base is itself a GEP, we recurse naturally.
        """
        source_type = patterns.parse_gep_source_type(op_str)

        # Extract and parse the base expression
        base_expr, base_end = self._extract_gep_base(op_str)
        base: GlobalName | InlineGEP

        if base_expr.startswith("@"):
            global_name = patterns.extract_global_ref(base_expr)
            if not global_name:
                raise ParseError(
                    f"Cannot parse global in GEP base: {base_expr[:50]}",
                    func_name=self._func_name,
                    block_label=self._block_label,
                )
            base = global_name
        elif base_expr.startswith("getelementptr"):
            # Recursive case: base is another GEP
            base = self._parse_inline_gep(base_expr)
        else:
            raise ParseError(
                f"Cannot parse GEP base: {base_expr[:50]}",
                func_name=self._func_name,
                block_label=self._block_label,
            )

        indices = tuple(patterns.parse_inline_gep_indices(op_str, base_end))
        return InlineGEP(base=base, indices=indices, source_type=LLVMType(source_type))

    def _extract_gep_base(self, op_str: str) -> tuple[str, int]:
        """Extract the base expression from an inline GEP.

        Returns (base_expr, end_position).
        Handles both global refs (@name) and nested GEPs.
        """
        base_start = patterns.find_gep_base_start(op_str)
        if base_start is None:
            raise ParseError(
                f"Cannot find 'ptr' in GEP: {op_str[:50]}",
                func_name=self._func_name,
                block_label=self._block_label,
            )

        rest = op_str[base_start:]

        if rest.startswith("@"):
            # Global reference - ends at comma or close paren
            for i, c in enumerate(rest):
                if c in ",)":
                    return rest[:i].strip(), base_start + i
            # No delimiter found - take the whole thing
            return rest.strip(), len(op_str)

        elif rest.startswith("getelementptr"):
            # Nested GEP - find balanced parens
            paren_start = rest.find("(")
            if paren_start == -1:
                raise ParseError(
                    f"Malformed nested GEP (no open paren): {rest[:50]}",
                    func_name=self._func_name,
                    block_label=self._block_label,
                )

            paren_count = 0
            for i, c in enumerate(rest[paren_start:], paren_start):
                if c == "(":
                    paren_count += 1
                elif c == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        end = i + 1
                        return rest[:end], base_start + end

            raise ParseError(
                f"Unbalanced parens in nested GEP: {rest[:50]}",
                func_name=self._func_name,
                block_label=self._block_label,
            )

        else:
            raise ParseError(
                f"Unknown GEP base expression: {rest[:50]}",
                func_name=self._func_name,
                block_label=self._block_label,
            )

    def _extract_label(self, op: LLVMValue) -> BlockLabel:
        """Extract a block label from a basic block operand."""
        # Try named block first
        name = op.name
        if name:
            return BlockLabel(name)

        # Try to extract from string (for numeric labels)
        op_str = str(op)
        label = patterns.extract_block_label(op_str)
        if label:
            return label

        raise ParseError(
            f"Cannot extract label from operand: {op_str[:50]}",
            func_name=self._func_name,
            block_label=self._block_label,
        )

    def _map_type(self, ty: LLVMType) -> JCType:
        """Map LLVM type to JCType."""
        result = map_llvm_type(ty)
        if result is None:
            raise ParseError(
                f"Unsupported type: {ty}",
                func_name=self._func_name,
                block_label=self._block_label,
            )
        return result
