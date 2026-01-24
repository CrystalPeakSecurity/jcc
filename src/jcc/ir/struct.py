"""IR data structures for JCA code representation."""

from dataclasses import dataclass, field

from jcc.aid import AID


@dataclass
class Instruction:
    opcode: str
    operands: list[str | int] = field(default_factory=list)
    comment: str | None = None
    pops: int = 0
    pushes: int = 0

    @property
    def stack_effect(self) -> int:
        return self.pushes - self.pops

    def emit(self) -> str:
        parts = [self.opcode]
        for op in self.operands:
            parts.append(str(op))
        result = " ".join(parts) + ";"
        if self.comment:
            result += f"\t\t// {self.comment}"
        return result


@dataclass(frozen=True)
class Op:
    """Instruction type - callable to create Instruction instances."""

    opcode: str
    pops: int
    pushes: int

    def __call__(self, *operands: str | int, comment: str | None = None) -> Instruction:
        return Instruction(self.opcode, list(operands), comment, self.pops, self.pushes)


@dataclass
class Label:
    name: str


@dataclass
class SourceComment:
    """A source line comment to be emitted in the JCA output."""

    line: int
    text: str


@dataclass
class Method:
    access: str
    name: str
    signature: str
    index: int | None = None
    stack: int = 2
    locals: int = 0
    descriptor: tuple[str, str] | None = None
    code: list[Instruction | Label] = field(default_factory=list)

    def emit(self, indent: str = "\t\t") -> str:
        from jcc.ir.util import optimize_labels, peephole_optimize

        if self.index is not None:
            lines = [f"{indent}.method {self.access} {self.name}{self.signature} {self.index} {{"]
        else:
            lines = [f"{indent}.method {self.access} {self.name}{self.signature} {{"]
        lines.append(f"{indent}\t.stack {self.stack};")
        lines.append(f"{indent}\t.locals {self.locals};")

        if self.descriptor:
            lines.append("")
            lines.append(f"{indent}\t.descriptor\t{self.descriptor[0]}\t{self.descriptor[1]};")

        lines.append("")

        optimized_code = optimize_labels(peephole_optimize(self.code))

        # Track pending source comment (only keep the most recent one)
        pending_comment: str | None = None
        # Track if last emitted item was a label (instruction goes on same line)
        last_was_label = False

        for item in optimized_code:
            if isinstance(item, Label):
                lines.append(f"{indent}\t\t{item.name}:\t")
                last_was_label = True
            elif isinstance(item, SourceComment):
                # Only keep the most recent source comment
                pending_comment = f"{item.line}: {item.text}"
            else:
                # Emit instruction with pending source comment (if any)
                instr_line = item.emit()
                if pending_comment:
                    if item.comment:
                        instr_line = instr_line.replace(f"// {item.comment}", f"// {pending_comment} | {item.comment}")
                    else:
                        instr_line = instr_line.rstrip(";") + f";\t\t// {pending_comment}"
                    pending_comment = None

                if last_was_label:
                    lines[-1] += instr_line
                else:
                    lines.append(f"{indent}\t\t\t{instr_line}")
                last_was_label = False

        lines.append(f"{indent}}}")
        return "\n".join(lines)


@dataclass
class Field:
    access: str
    type: str
    name: str
    index: int | None = None
    value: int | None = None
    initial_values: list[int] | None = None
    comment: str | None = None

    def emit(self) -> str:
        parts = [self.access, self.type, self.name]
        if self.index is not None:
            parts.append(str(self.index))
        if self.value is not None:
            parts.append(f"= {self.value}")
        if self.initial_values is not None:
            vals = ", ".join(str(v) for v in self.initial_values)
            parts.append(f"= {{ {vals} }}")
        result = " ".join(parts) + ";"
        if self.comment:
            result += f"\t\t// {self.comment}"
        return result


@dataclass
class ConstantPoolEntry:
    kind: str
    value: str
    comment: str | None = None
    index: int | None = None
    # List of (type_name, import.class) tuples for external class references
    # e.g., [("Ljava/lang/Object;", "2.0")] for java/lang/Object in import 2, class 0
    descriptors: list[tuple[str, str]] | None = None

    def emit(self) -> str:
        lines = []
        if self.index is not None:
            lines.append(f"\t\t// {self.index}")
        entry = f"\t\t{self.kind} {self.value};"
        if self.comment:
            entry += f"\t\t// {self.comment}"
        lines.append(entry)
        # Add .descriptor entries for external class references
        if self.descriptors:
            for type_name, import_class in self.descriptors:
                lines.append(f"\t\t\t.descriptor\t{type_name}\t{import_class};")
        return "\n".join(lines)


@dataclass
class MethodTableEntry:
    signature: str
    index: int


@dataclass
class Class:
    access: str
    name: str
    index: int
    extends: str
    extends_comment: str | None = None
    implements: list[tuple[str, str]] = field(default_factory=list)  # [(import_ref, comment), ...]
    fields: list[Field] = field(default_factory=list)
    public_method_table: list[MethodTableEntry] = field(default_factory=list)
    public_method_table_base: int = 0
    public_method_table_count: int = 0
    package_method_table: list[MethodTableEntry] = field(default_factory=list)
    package_method_table_base: int = 0
    methods: list[Method] = field(default_factory=list)

    def emit(self, indent: str = "\t") -> str:
        extends_str = f"extends {self.extends}"
        if self.extends_comment:
            extends_str += f" {{\t\t// {self.extends_comment}"
        else:
            extends_str += " {"

        lines = [f"{indent}.class {self.access} {self.name} {self.index} {extends_str}"]
        lines.append("")

        if self.fields:
            lines.append(f"{indent}\t.fields {{")
            for f in self.fields:
                lines.append(f"{indent}\t\t{f.emit()}")
            lines.append(f"{indent}\t}}")
            lines.append("")

        # Use classic format (no count, no indices) for compatibility with older cards
        lines.append(f"{indent}\t.publicMethodTable {self.public_method_table_base} {{")
        for entry in self.public_method_table:
            lines.append(f"{indent}\t\t{entry.signature};")
        lines.append(f"{indent}\t}}")
        lines.append("")

        lines.append(f"{indent}\t.packageMethodTable {self.package_method_table_base} {{")
        for entry in self.package_method_table:
            lines.append(f"{indent}\t\t{entry.signature};")
        lines.append(f"{indent}\t}}")

        # implementedInterfaceInfoTable must come after method tables
        if self.implements:
            lines.append("")
            lines.append(f"{indent}\t.implementedInterfaceInfoTable {{")
            for impl_ref, impl_comment in self.implements:
                if impl_comment:
                    lines.append(f"{indent}\t\t.interface {impl_ref} {{\t\t// {impl_comment}")
                else:
                    lines.append(f"{indent}\t\t.interface {impl_ref} {{")
                lines.append(f"{indent}\t\t}}")
            lines.append(f"{indent}\t}}")

        for method in self.methods:
            lines.append("")
            lines.append(method.emit(indent + "\t"))

        lines.append(f"{indent}}}")
        return "\n".join(lines)


@dataclass
class Import:
    aid: AID | str
    version: str
    comment: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.aid, str):
            object.__setattr__(self, "aid", AID.parse(self.aid))


@dataclass
class AppletEntry:
    aid: AID | str
    class_name: str

    def __post_init__(self) -> None:
        if isinstance(self.aid, str):
            object.__setattr__(self, "aid", AID.parse(self.aid))


@dataclass
class Package:
    name: str
    aid: AID | str
    version: str = "1.0"
    imports: list[Import] = field(default_factory=list)
    applets: list[AppletEntry] = field(default_factory=list)
    constant_pool: list[ConstantPoolEntry] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.aid, str):
            object.__setattr__(self, "aid", AID.parse(self.aid))

    def emit(self) -> str:
        aid_str = self.aid.to_jca() if isinstance(self.aid, AID) else self.aid
        lines = [f".package {self.name} {{"]
        lines.append(f"\t.aid {aid_str};")
        lines.append(f"\t.version {self.version};")
        lines.append("")

        if self.imports:
            lines.append("\t.imports {")
            for imp in self.imports:
                imp_aid = imp.aid.to_jca() if isinstance(imp.aid, AID) else imp.aid
                entry = f"\t\t{imp_aid} {imp.version};"
                if imp.comment:
                    entry += f"\t\t//{imp.comment}"
                lines.append(entry)
            lines.append("\t}")
            lines.append("")

        if self.applets:
            lines.append("\t.applet {")
            for app in self.applets:
                app_aid = app.aid.to_jca() if isinstance(app.aid, AID) else app.aid
                lines.append(f"\t\t{app_aid} {app.class_name};")
            lines.append("\t}")
            lines.append("")

        if self.constant_pool:
            lines.append("\t.constantPool {")
            for i, entry in enumerate(self.constant_pool):
                entry.index = i
                lines.append(entry.emit())
            lines.append("\t}")
            lines.append("")

        for cls in self.classes:
            lines.append(cls.emit())
            lines.append("")

        lines.append("}")
        return "\n".join(lines)
