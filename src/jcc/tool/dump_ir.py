"""Dump parsed IR in a readable format for debugging.

Usage:
    python -m jcc.tool.dump_ir <file.ll> [-f <function_name>]
"""

import argparse
from pathlib import Path

from jcc.ir.module import Block, Function, Global, Module
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    Instruction,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    UnreachableInst,
)
from jcc.ir.values import (
    Const,
    GlobalRef,
    InlineGEP,
    Null,
    Value,
    SSARef,
    Undef,
)


def dump_module(module: Module) -> str:
    """Dump entire module."""
    lines: list[str] = []

    if module.globals:
        lines.append("=== Globals ===")
        for gv in module.globals.values():
            lines.append(dump_global(gv))
        lines.append("")

    lines.append(f"=== Functions ({len(module.functions)}) ===")
    for func in module.functions.values():
        lines.append(dump_function(func))
        lines.append("")

    return "\n".join(lines)


def dump_global(gv: Global) -> str:
    """Dump a global variable."""
    const = "constant" if gv.is_constant else "global"
    init = ""
    if gv.initializer:
        init = f" = {type(gv.initializer).__name__}"
    return f"  {gv.name}: {const} {gv.llvm_type}{init}"


def dump_function(func: Function) -> str:
    """Dump a function."""
    lines: list[str] = []

    # Signature
    params = ", ".join(f"{p.name}: {p.ty.name}" for p in func.params)
    lines.append(f"fn {func.name}({params}) -> {func.return_type.name} {{")

    # Blocks
    for block in func.blocks:
        lines.append(dump_block(block, indent=2))

    lines.append("}")
    return "\n".join(lines)


def dump_block(block: Block, indent: int = 0) -> str:
    """Dump a basic block."""
    pad = " " * indent
    lines: list[str] = []

    lines.append(f"{pad}{block.label}:")

    for instr in block.instructions:
        lines.append(f"{pad}  {dump_instruction(instr)}")

    lines.append(f"{pad}  {dump_instruction(block.terminator)}")

    return "\n".join(lines)


def dump_instruction(instr: Instruction) -> str:
    """Dump a single instruction."""
    match instr:
        case BinaryInst(result=r, op=op, left=l, right=ri, ty=t):
            return f"{r} = {op} {t.name} {dump_value(l)}, {dump_value(ri)}"

        case ICmpInst(result=r, pred=p, left=l, right=ri, ty=t):
            return f"{r} = icmp {p} {t.name} {dump_value(l)}, {dump_value(ri)}"

        case LoadInst(result=r, ptr=p, ty=t):
            return f"{r} = load {t.name}, {dump_value(p)}"

        case StoreInst(value=v, ptr=p, ty=t):
            return f"store {t.name} {dump_value(v)}, {dump_value(p)}"

        case GEPInst(result=r, base=b, indices=idx, source_type=st):
            indices_str = ", ".join(dump_value(i) for i in idx)
            return f"{r} = gep {st}, {dump_value(b)}, {indices_str}"

        case BranchInst(cond=None, true_label=t):
            return f"br {t}"

        case BranchInst(cond=c, true_label=t, false_label=f) if c is not None:
            return f"br {dump_value(c)}, {t}, {f}"

        case ReturnInst(value=None):
            return "ret void"

        case ReturnInst(value=v, ty=t) if v is not None:
            return f"ret {t.name} {dump_value(v)}"

        case SwitchInst(value=v, default=d, cases=cases):
            cases_str = ", ".join(f"{val}: {lbl}" for val, lbl in cases)
            return f"switch {dump_value(v)}, default={d} [{cases_str}]"

        case UnreachableInst():
            return "unreachable"

        case PhiInst(result=r, incoming=inc, ty=t):
            pairs = ", ".join(f"[{dump_value(v)}, {lbl}]" for v, lbl in inc)
            return f"{r} = phi {t.name} {pairs}"

        case CallInst(result=None, func_name=fn, args=args):
            args_str = ", ".join(dump_value(a) for a in args)
            return f"call {fn}({args_str})"

        case CallInst(result=r, func_name=fn, args=args, ty=t) if r is not None:
            args_str = ", ".join(dump_value(a) for a in args)
            return f"{r} = call {t.name} {fn}({args_str})"

        case CastInst(result=r, op=op, operand=o, from_ty=ft, to_ty=tt):
            return f"{r} = {op} {ft.name} {dump_value(o)} to {tt.name}"

        case SelectInst(result=r, cond=c, true_val=tv, false_val=fv, ty=t):
            return f"{r} = select {dump_value(c)}, {t.name} {dump_value(tv)}, {dump_value(fv)}"

        case _:
            return f"<unknown: {type(instr).__name__}>"


def dump_value(val: Value) -> str:
    """Dump a value."""
    match val:
        case SSARef(name=n):
            return str(n)
        case Const(value=v):
            return str(v)
        case GlobalRef(name=n):
            return str(n)
        case InlineGEP(base=b, indices=idx):
            return f"gep({b}, {idx})"
        case Undef():
            return "undef"
        case Null():
            return "null"
        case _:
            return f"<{type(val).__name__}>"


def main() -> None:
    """CLI entry point."""
    from jcc.ir.module import parse_module_from_file

    parser = argparse.ArgumentParser(description="Dump parsed LLVM IR")
    parser.add_argument("file", type=Path, help="Path to .ll file")
    parser.add_argument("-f", "--function", help="Dump only this function")
    args = parser.parse_args()

    module = parse_module_from_file(args.file)

    if args.function:
        if args.function not in module.functions:
            available = ", ".join(sorted(module.functions.keys()))
            print(f"Function '{args.function}' not found. Available: {available}")
            raise SystemExit(1)
        print(dump_function(module.functions[args.function]))
    else:
        print(dump_module(module))


if __name__ == "__main__":
    main()
