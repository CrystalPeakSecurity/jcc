"""Applet packager - generates complete JCA packages from analyzed C code."""

from jcc.analysis.symbol import FrameSize, FunctionDef, SymbolTable
from jcc.codegen.context import CodeGenContext, CPEntry
from jcc.codegen.stmt_gen import gen_stmt
from jcc.frontend.pycparser_adapter import translate_stmt
from jcc.debug import get_debug_context, logger_codegen
from jcc.types.memory import MemArray, MEM_ARRAYS, STACK_ARRAYS
from jcc.config import DISABLE_MEMSET_SHORT, ProjectConfig, get_import_versions
from jcc.ir import ops
from jcc.ir.struct import (
    AppletEntry,
    Class,
    ConstantPoolEntry,
    Field,
    Import,
    Instruction,
    Label,
    Method,
    MethodTableEntry,
    Package,
)
from jcc.ir.util import (
    JAVACARD_FRAMEWORK_AID,
    JAVA_LANG_AID,
    JAVACARDX_APDU_AID,
    JAVACARDX_INTX_AID,
    JAVACARDX_UTIL_AID,
    calculate_max_stack,
)
from jcc.types.typed_value import LogicalType


class ImportRegistry:
    """Tracks imported packages and their indices."""

    FRAMEWORK = "framework"  # javacard/framework - always index 0
    JAVA_LANG = "java_lang"  # java/lang - always index 1
    APDU_EXT = "apdu_ext"  # javacardx/apdu - optional
    UTIL = "util"  # javacardx/framework/util - optional (for ArrayLogic)
    INTX = "intx"  # javacardx/framework/util/intx - optional

    def __init__(self):
        self._imports: list[Import] = []
        self._indices: dict[str, int] = {}

    def add(self, key: str, import_obj: Import) -> int:
        """Add an import and return its index."""
        idx = len(self._imports)
        self._imports.append(import_obj)
        self._indices[key] = idx
        return idx

    def get_index(self, key: str) -> int:
        """Get the index for a registered import."""
        return self._indices[key]

    def has(self, key: str) -> bool:
        """Check if an import is registered."""
        return key in self._indices

    def get_imports(self) -> list[Import]:
        """Get the list of imports."""
        return self._imports


# Slot assignments in process() wrapper method
_SLOT_THIS = 0  # 'this' reference (hidden, not user-accessible)
_SLOT_APDU = 1  # APDU parameter passed to process
_SLOT_LENGTH = 2  # Received length from setIncomingAndReceive


class PackageBuilder:
    def __init__(self, symbols: SymbolTable, config: ProjectConfig, source_path: "Path | None" = None):
        # Validate intrinsics registry early (catches missing imports)
        from jcc.intrinsics import validate_registry
        from pathlib import Path

        validate_registry()

        self.symbols = symbols
        self.config = config
        self.cp_entries: list[ConstantPoolEntry] = []
        self.cp_index = 0
        # Consolidated constant pool indices (set in _build_constant_pool)
        self.cp: dict[CPEntry, int] = {}
        # User function CP indices (separate since keys are strings)
        self.cp_user_funcs: dict[str, int] = {}
        # Const array CP indices (array name -> CP index)
        self.cp_const_arrays: dict[str, int] = {}
        # Warnings collected during code generation
        self.warnings: list[str] = []
        # Actual frame sizes after code generation
        # Used for post-codegen stack validation
        self.frame_sizes: dict[str, FrameSize] = {}

    def _add_cp(
        self,
        kind: str,
        value: str,
        comment: str | None = None,
        descriptors: list[tuple[str, str]] | None = None,
    ) -> int:
        idx = self.cp_index
        self.cp_entries.append(ConstantPoolEntry(kind, value, comment, descriptors=descriptors))
        self.cp_index += 1
        return idx

    def _get_make_transient_ref(self, mem: MemArray, registry: ImportRegistry) -> str:
        """Get the makeTransient method reference for a memory array type."""
        if mem in (MemArray.INT, MemArray.STACK_I):
            intx_idx = registry.get_index(ImportRegistry.INTX)
            return f"{intx_idx}.0.4(SB)[I"
        return mem.make_transient_ref

    def _has_user_code(self) -> bool:
        """Check if there's any user code that might use APDU/exception intrinsics."""
        if not self._is_process_empty():
            return True
        for func_name, func_def in self.symbols.functions.items():
            if func_name != "process" and func_def.body is not None:
                return True
        return False

    def _build_constant_pool(self, registry: ImportRegistry) -> None:
        # Applet lifecycle methods (always needed)
        self.cp[CPEntry.APPLET_INIT] = self._add_cp(
            "staticMethodRef", "0.3.0()V", "javacard/framework/Applet.<init>()V"
        )
        self.cp[CPEntry.REGISTER] = self._add_cp("virtualMethodRef", "0.3.1()V", "register()V")
        self.cp[CPEntry.CLASS_REF] = self._add_cp(".classRef", self.config.applet.class_name)
        self.cp[CPEntry.OUR_INIT] = self._add_cp("staticMethodRef", f"{self.config.applet.class_name}/<init>()V")

        # Only add APDU/exception/util entries if there's user code that might use them
        if self._has_user_code():
            self.cp[CPEntry.SELECTING_APPLET] = self._add_cp("virtualMethodRef", "0.3.3()Z", "selectingApplet()Z")

            # APDU methods
            self.cp[CPEntry.APDU_GET_BUFFER] = self._add_cp("virtualMethodRef", "0.10.1()[B", "getBuffer()[B")
            self.cp[CPEntry.APDU_RECEIVE] = self._add_cp("virtualMethodRef", "0.10.6()S", "setIncomingAndReceive()S")
            self.cp[CPEntry.SET_OUTGOING] = self._add_cp("virtualMethodRef", "0.10.7()S", "setOutgoing()S")
            self.cp[CPEntry.SET_OUTGOING_LENGTH] = self._add_cp(
                "virtualMethodRef", "0.10.9(S)V", "setOutgoingLength(S)V"
            )
            self.cp[CPEntry.SEND_BYTES] = self._add_cp("virtualMethodRef", "0.10.4(SS)V", "sendBytes(SS)V")
            self.cp[CPEntry.SEND_BYTES_LONG] = self._add_cp("virtualMethodRef", "0.10.5([BSS)V", "sendBytesLong([BSS)V")

            # Exceptions
            self.cp[CPEntry.ISO_EXCEPTION_THROWIT] = self._add_cp(
                "staticMethodRef", "0.7.1(S)V", "ISOException.throwIt(S)V"
            )

            # Util methods (javacard.framework.Util - class 16 in import 0)
            self.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = self._add_cp(
                "staticMethodRef", "0.16.3([BSSB)S", "Util.arrayFillNonAtomic([BSSB)S"
            )

            # ArrayLogic methods (javacardx.framework.util.ArrayLogic - class 0 in util import)
            if registry.has(ImportRegistry.UTIL):
                util_idx = registry.get_index(ImportRegistry.UTIL)
                java_lang_idx = registry.get_index(ImportRegistry.JAVA_LANG)
                # java/lang/Object is class 0 in java/lang package
                object_ref = f"{java_lang_idx}.0"
                self.cp[CPEntry.ARRAY_LOGIC_FILL_GENERIC] = self._add_cp(
                    "staticMethodRef",
                    f"{util_idx}.0.2(Ljava/lang/Object;SSLjava/lang/Object;S)S",
                    "ArrayLogic.arrayFillGenericNonAtomic",
                    descriptors=[
                        ("Ljava/lang/Object;", object_ref),
                        ("Ljava/lang/Object;", object_ref),
                    ],
                )

        # Transient array methods and memory array fields (only if used)
        # First handle MEM_* arrays (global/static storage)
        for mem in MEM_ARRAYS:
            size = self.symbols.mem_sizes[mem]
            if size > 0:
                make_transient_ref = self._get_make_transient_ref(mem, registry)
                self.cp[mem.make_transient_cp_entry] = self._add_cp(
                    "staticMethodRef", make_transient_ref, mem.make_transient_comment
                )
                self.cp[mem.cp_entry] = self._add_cp(
                    "staticFieldRef",
                    f"{mem.field_type_str} {self.config.applet.class_name}/{mem.value}",
                    f"{mem.field_type_str[:-2]}[{size}]",
                )

        # Handle STACK_* arrays (offload stack storage)
        for stack_mem in STACK_ARRAYS:
            size = self.symbols.offload_stack_sizes.get(stack_mem, 0)
            if size > 0:
                if stack_mem.make_transient_cp_entry not in self.cp:
                    make_transient_ref = self._get_make_transient_ref(stack_mem, registry)
                    self.cp[stack_mem.make_transient_cp_entry] = self._add_cp(
                        "staticMethodRef", make_transient_ref, stack_mem.make_transient_comment
                    )
                # Add the STACK_* field ref
                self.cp[stack_mem.cp_entry] = self._add_cp(
                    "staticFieldRef",
                    f"{stack_mem.field_type_str} {self.config.applet.class_name}/{stack_mem.value}",
                    f"{stack_mem.field_type_str[:-2]}[{size}]",
                )
                # Add the SP_* field ref (static short for stack pointer)
                sp_name = f"SP_{stack_mem.value[-1]}"  # SP_B, SP_S, or SP_I
                self.cp[stack_mem.sp_cp_entry] = self._add_cp(
                    "staticFieldRef",
                    f"short {self.config.applet.class_name}/{sp_name}",
                    f"stack pointer for {stack_mem.value}",
                )

        # User functions
        for func_name, func_def in self.symbols.functions.items():
            if func_name == "process":
                continue
            if func_def.body is None:
                continue
            sig = self._get_jca_signature(func_def)
            self.cp_user_funcs[func_name] = self._add_cp(
                "staticMethodRef", f"{self.config.applet.class_name}/{func_name}{sig}"
            )

        # Const arrays
        for glob_name, glob in self.symbols.globals.items():
            if glob.is_const and glob.initial_values is not None:
                if glob.type is None:
                    raise ValueError(f"Const global '{glob_name}' has no type information")
                # glob.type.value already includes [] for array types (e.g., "byte[]")
                field_type = glob.type.value
                self.cp_const_arrays[glob_name] = self._add_cp(
                    "staticFieldRef",
                    f"{field_type} {self.config.applet.class_name}/{glob_name.upper()}",
                    f"const {field_type}[{len(glob.initial_values)}]",
                )

        # Const struct array fields
        # Use '$' separator for CP keys to avoid collision with regular const array names
        for array_name, fields in self.symbols.const_struct_array_fields.items():
            for field_name, csaf in fields.items():
                jca_field_name = f"{array_name.upper()}_{field_name.upper()}"
                field_type = csaf.element_type.to_array().value  # e.g., "short[]"
                cp_key = f"{array_name}${field_name}"  # Must match CodeGenContext.const_struct_field_cp_key
                self.cp_const_arrays[cp_key] = self._add_cp(
                    "staticFieldRef",
                    f"{field_type} {self.config.applet.class_name}/{jca_field_name}",
                    f"const {field_type}[{len(csaf.initial_values)}]",
                )

    def _build_imports(self) -> ImportRegistry:
        """Build imports registry with all needed packages."""
        registry = ImportRegistry()

        # Get version-specific import versions
        framework_version, lang_version = get_import_versions(self.config.analysis.javacard_version)

        # Always present
        registry.add(
            ImportRegistry.FRAMEWORK, Import(JAVACARD_FRAMEWORK_AID, framework_version, comment="javacard/framework")
        )
        registry.add(ImportRegistry.JAVA_LANG, Import(JAVA_LANG_AID, lang_version, comment="java/lang"))

        # Optional: extended APDU support
        if self.config.analysis.extended_apdu:
            registry.add(ImportRegistry.APDU_EXT, Import(JAVACARDX_APDU_AID, "1.0", comment="javacardx/apdu"))

        # Optional: util package (for ArrayLogic.arrayFillGenericNonAtomic)
        # See config.DISABLE_MEMSET_SHORT - currently broken on some cards
        if not DISABLE_MEMSET_SHORT and self.symbols.mem_sizes[MemArray.SHORT] > 0:
            registry.add(ImportRegistry.UTIL, Import(JAVACARDX_UTIL_AID, "1.1", comment="javacardx/framework/util"))

        # Optional: int support (intx package) - needed if MEM_I or STACK_I is used
        # When has_intx=False, ints are stored as short pairs in MEM_S/STACK_S instead
        needs_native_int = (
            self.symbols.mem_sizes[MemArray.INT] > 0 or self.symbols.offload_stack_sizes.get(MemArray.STACK_I, 0) > 0
        )
        if needs_native_int and self.config.analysis.has_intx:
            registry.add(
                ImportRegistry.INTX, Import(JAVACARDX_INTX_AID, "1.1", comment="javacardx/framework/util/intx")
            )

        return registry

    def _get_jca_signature(self, func: FunctionDef) -> str:
        params = "".join(p.type.jca_sig for p in func.params)
        return f"({params}){func.return_type.jca_sig}"

    def _build_fields(self) -> list[Field]:
        # Private static fields don't need explicit token (capgen assigns 0xFF)
        fields = []

        # MEM_* arrays (global/static storage)
        for mem in MEM_ARRAYS:
            size = self.symbols.mem_sizes[mem]
            if size > 0:
                fields.append(
                    Field(
                        access="private static",
                        type=mem.field_type_str,
                        name=mem.value,
                        comment=f"{mem.field_type_str[:-2]}[{size}]",
                    )
                )

        # STACK_* arrays (offload stack storage)
        for stack_mem in STACK_ARRAYS:
            size = self.symbols.offload_stack_sizes.get(stack_mem, 0)
            if size > 0:
                fields.append(
                    Field(
                        access="private static",
                        type=stack_mem.field_type_str,
                        name=stack_mem.value,
                        comment=f"offload stack {stack_mem.field_type_str[:-2]}[{size}]",
                    )
                )
                # SP_* field (stack pointer as static short)
                sp_name = f"SP_{stack_mem.value[-1]}"
                fields.append(
                    Field(
                        access="private static",
                        type="short",
                        name=sp_name,
                        comment=f"stack pointer for {stack_mem.value}",
                    )
                )

        # Const array fields (stored in EEPROM with initializers)
        for glob_name, glob in self.symbols.globals.items():
            if glob.is_const and glob.initial_values is not None:
                if glob.type is None:
                    raise ValueError(f"Const global '{glob_name}' has no type information")
                fields.append(
                    Field(
                        access="private static final",
                        type=glob.type.value,
                        name=glob_name.upper(),
                        initial_values=glob.initial_values,
                    )
                )

        # Const struct array fields (each field becomes a separate static final array)
        for array_name, struct_fields in self.symbols.const_struct_array_fields.items():
            for field_name, csaf in struct_fields.items():
                jca_field_name = f"{array_name.upper()}_{field_name.upper()}"
                fields.append(
                    Field(
                        access="private static final",
                        type=csaf.element_type.to_array().value,
                        name=jca_field_name,
                        initial_values=csaf.initial_values,
                    )
                )

        return fields

    def _build_init_method(self) -> Method:
        code: list[Instruction | Label] = [ops.label("L0")]
        code.append(ops.aload(0))
        code.append(ops.invokespecial(self.cp[CPEntry.APPLET_INIT], comment="Applet.<init>()V"))

        # Initialize transient memory arrays (MEM_*)
        for mem in MEM_ARRAYS:
            size = self.symbols.mem_sizes[mem]
            if size > 0:
                code.append(ops.sconst(size))
                code.append(ops.sconst(1))  # CLEAR_ON_RESET
                code.append(ops.invokestatic(self.cp[mem.make_transient_cp_entry], comment=mem.make_transient_comment))
                code.append(ops.putstatic_a(self.cp[mem.cp_entry], comment=mem.value))

        # Initialize offload stack arrays (STACK_*)
        for stack_mem in STACK_ARRAYS:
            size = self.symbols.offload_stack_sizes.get(stack_mem, 0)
            if size > 0:
                code.append(ops.sconst(size))
                code.append(ops.sconst(1))  # CLEAR_ON_RESET
                code.append(
                    ops.invokestatic(
                        self.cp[stack_mem.make_transient_cp_entry], comment=stack_mem.make_transient_comment
                    )
                )
                code.append(ops.putstatic_a(self.cp[stack_mem.cp_entry], comment=stack_mem.value))
                # SP_* is automatically initialized to 0 (default for static short)

        code.append(ops.aload(0))
        code.append(ops.invokevirtual(self.cp[CPEntry.REGISTER], comment="register()V"))
        code.append(ops.return_())

        # Calculate stack based on whether arrays need initialization
        has_arrays = any(self.symbols.mem_sizes[mem] > 0 for mem in MEM_ARRAYS)
        has_offload = any(self.symbols.offload_stack_sizes.get(m, 0) > 0 for m in STACK_ARRAYS)
        # Stack: 1 for aload_0, +2 if makeTransient*Array calls are needed
        stack = 3 if (has_arrays or has_offload) else 1

        return Method(
            access="protected",
            name="<init>",
            signature="()V",
            index=0,
            stack=stack,
            locals=0,
            code=code,
        )

    def _build_install_method(self) -> Method:
        code = [
            ops.label("L0"),
            ops.new(self.cp[CPEntry.CLASS_REF], comment=self.config.applet.class_name),
            ops.dup(),
            ops.invokespecial(self.cp[CPEntry.OUR_INIT], comment=f"{self.config.applet.class_name}.<init>()V"),
            ops.pop(),
            ops.return_(),
        ]
        return Method(
            access="public static",
            name="install",
            signature="([BSB)V",
            index=1,
            stack=2,
            locals=0,
            code=code,
        )

    def _is_process_empty(self) -> bool:
        """Check if user's process() function has an empty body."""
        user_process = self.symbols.functions.get("process")
        if user_process is None or user_process.body is None:
            return True
        return user_process.body.block_items is None or len(user_process.body.block_items) == 0

    def _build_process_wrapper(self) -> Method:
        user_process = self.symbols.functions.get("process")

        # Generate minimal process() if user didn't define one or has empty body
        if user_process is None or self._is_process_empty():
            # Minimal process matching official converter output
            code = [
                ops.label("L0"),
                ops.return_(),
            ]
            return Method(
                access="public",
                name="process",
                signature="(Ljavacard/framework/APDU;)V",
                index=7,
                stack=0,
                locals=0,
                descriptor=("Ljavacard/framework/APDU;", "0.10"),
                code=code,
            )

        # New simplified wrapper:
        # - Check selectingApplet
        # - Call setIncomingAndReceive to get length
        # - Pass APDU object and length to userProcess
        code: list[Instruction | Label] = [ops.label("L0")]
        code.append(ops.aload(0))
        code.append(ops.invokevirtual(self.cp[CPEntry.SELECTING_APPLET], comment="selectingApplet()Z"))
        code.append(ops.ifeq("L1"))
        code.append(ops.return_())
        code.append(ops.label("L1"))
        # Call setIncomingAndReceive to get length
        code.append(ops.aload(_SLOT_APDU))
        code.append(ops.invokevirtual(self.cp[CPEntry.APDU_RECEIVE], comment="setIncomingAndReceive()S"))
        code.append(ops.sstore(_SLOT_LENGTH))
        # Pass APDU and length to userProcess
        code.append(ops.aload(_SLOT_APDU))
        code.append(ops.sload(_SLOT_LENGTH))

        user_process_cp = self._add_cp(
            "staticMethodRef", f"{self.config.applet.class_name}/userProcess(Ljavacard/framework/APDU;S)V"
        )
        code.append(ops.invokestatic(user_process_cp, comment="userProcess"))
        code.append(ops.return_())

        return Method(
            access="public",
            name="process",
            signature="(Ljavacard/framework/APDU;)V",
            index=7,
            stack=2,
            locals=2,
            descriptor=("Ljavacard/framework/APDU;", "0.10"),
            code=code,
        )

    def _gen_offload_sp_adjust(self, func: FunctionDef, increment: bool) -> list[Instruction]:
        """Generate code to adjust stack pointers for offload frame.

        Args:
            func: Function definition with offload_usage
            increment: True for prologue (allocate), False for epilogue (deallocate)
        """
        code: list[Instruction] = []
        op = ops.sadd if increment else ops.ssub
        symbol = "+=" if increment else "-="

        for stack_mem in STACK_ARRAYS:
            count = func.offload_usage.get(stack_mem, 0)
            if count > 0 and stack_mem.cp_entry in self.cp:
                sp_cp = self.cp[stack_mem.sp_cp_entry]
                sp_name = f"SP_{stack_mem.value[-1]}"
                code.append(ops.getstatic_s(sp_cp, comment=sp_name))
                code.append(ops.sconst(count))
                code.append(op())
                code.append(ops.putstatic_s(sp_cp, comment=f"{sp_name} {symbol} {count}"))

        return code

    def _insert_epilogue_before_returns(
        self, code: list[Instruction | Label], epilogue: list[Instruction]
    ) -> list[Instruction | Label]:
        """Insert epilogue code before every return instruction.

        Handles all return variants: return, sreturn, ireturn, areturn.
        """
        if not epilogue:
            return code

        return_opcodes = {"return", "sreturn", "ireturn", "areturn"}
        result: list[Instruction | Label] = []
        for item in code:
            if isinstance(item, Instruction) and item.opcode in return_opcodes:
                # Insert epilogue before return
                result.extend(epilogue)
            result.append(item)
        return result

    def _make_codegen_context(self, func: FunctionDef) -> CodeGenContext:
        """Create a CodeGenContext with all CP indices set."""
        ctx = CodeGenContext(symbols=self.symbols)
        ctx.current_func = func
        ctx.func_cp_map = self.cp_user_funcs.copy()
        ctx.const_array_cp = self.cp_const_arrays.copy()

        # Copy relevant CP entries to CodeGenContext
        # (only the entries needed for code generation, not packaging)
        codegen_entries = [
            # Memory arrays (globals/statics)
            CPEntry.MEM_B,
            CPEntry.MEM_S,
            CPEntry.MEM_I,
            # Offload stack arrays
            CPEntry.STACK_B,
            CPEntry.STACK_S,
            CPEntry.STACK_I,
            # Stack pointers
            CPEntry.SP_B,
            CPEntry.SP_S,
            CPEntry.SP_I,
            # APDU methods
            CPEntry.APDU_GET_BUFFER,
            CPEntry.APDU_RECEIVE,
            CPEntry.SET_OUTGOING,
            CPEntry.SET_OUTGOING_LENGTH,
            CPEntry.SEND_BYTES,
            CPEntry.SEND_BYTES_LONG,
            # Exceptions
            CPEntry.ISO_EXCEPTION_THROWIT,
            # Util methods
            CPEntry.UTIL_ARRAY_FILL_BYTE,
            CPEntry.ARRAY_LOGIC_FILL_GENERIC,
        ]
        for entry in codegen_entries:
            if entry in self.cp:
                ctx.cp[entry] = self.cp[entry]

        return ctx

    def _build_user_process(self) -> Method | None:
        user_process = self.symbols.functions.get("process")
        if user_process is None or user_process.body is None:
            return None
        # Skip generating userProcess if body is empty
        if self._is_process_empty():
            return None

        # Validate new signature: process(APDU apdu, short len)
        if len(user_process.params) != 2:
            raise ValueError(f"process() must have 2 parameters (APDU apdu, short len), got {len(user_process.params)}")
        if user_process.params[0].type != LogicalType.REF:
            raise ValueError(f"process() first parameter must be APDU (void*), got {user_process.params[0].type}")
        if user_process.params[1].type.is_array or user_process.params[1].type != LogicalType.SHORT:
            raise ValueError(f"process() second parameter must be short, got {user_process.params[1].type}")

        ctx = self._make_codegen_context(user_process)
        # No hidden params - APDU is at slot 0, len at slot 1
        ctx.slot_offset = 0
        # Initialize temp allocation for array reference caching
        ctx.init_temp_allocation(user_process.total_slots)
        # Enable array caching if pragma is present
        ctx.array_caching_enabled = user_process.enable_array_caching

        code: list[Instruction | Label] = [ops.label("L0")]

        # Generate prologue (bump stack pointers)
        prologue = self._gen_offload_sp_adjust(user_process, increment=True)
        code.extend(prologue)

        ir_body = translate_stmt(user_process.body)
        body_code = list(gen_stmt(ir_body, ctx))
        code.extend(body_code)

        # Collect warnings from this context
        self.warnings.extend(ctx.warnings)

        if not code or not isinstance(code[-1], Instruction) or code[-1].opcode != "return":
            code.append(ops.return_())

        # Insert epilogue before every return
        epilogue = self._gen_offload_sp_adjust(user_process, increment=False)
        code = self._insert_epilogue_before_returns(code, epilogue)

        max_stack = calculate_max_stack(code, debug=get_debug_context().verbose, func_name="userProcess")
        # Use max locals including any temps allocated for array reference caching
        locals_slots = ctx.max_locals_with_temps
        self.frame_sizes["process"] = FrameSize(max_stack, locals_slots)

        return Method(
            access="private static",
            name="userProcess",
            signature="(Ljavacard/framework/APDU;S)V",
            stack=max_stack,
            locals=locals_slots,
            code=code,
        )

    def _build_user_methods(self) -> list[Method]:
        methods = []

        for func_name, func_def in self.symbols.functions.items():
            if func_name == "process":
                continue
            if func_def.body is None:
                continue

            ctx = self._make_codegen_context(func_def)
            # Initialize temp allocation for array reference caching
            ctx.init_temp_allocation(func_def.total_slots)
            # Enable array caching if pragma is present
            ctx.array_caching_enabled = func_def.enable_array_caching

            code: list[Instruction | Label] = [ops.label("L0")]

            # Generate prologue (bump stack pointers)
            prologue = self._gen_offload_sp_adjust(func_def, increment=True)
            code.extend(prologue)

            ir_body = translate_stmt(func_def.body)
            body_code = list(gen_stmt(ir_body, ctx))
            code.extend(body_code)

            # Collect warnings from this context
            self.warnings.extend(ctx.warnings)

            # Add trailing return for void functions that don't end with one
            if func_def.return_type == LogicalType.VOID:
                if not code or not isinstance(code[-1], Instruction) or code[-1].opcode != "return":
                    code.append(ops.return_())

            # Insert epilogue before every return
            epilogue = self._gen_offload_sp_adjust(func_def, increment=False)
            code = self._insert_epilogue_before_returns(code, epilogue)

            if get_debug_context().trace_codegen:
                logger_codegen.debug("\n=== %s ===", func_name)
                # Dump slot map
                logger_codegen.debug("  Params:")
                slot = 0
                for p in func_def.params:
                    if p.type.slot_size == 2:
                        logger_codegen.debug("    %s (%s) @ slots %d-%d", p.name, p.type.name, slot, slot + 1)
                    else:
                        logger_codegen.debug("    %s (%s) @ slot %d", p.name, p.type.name, slot)
                    slot += p.type.slot_size
                logger_codegen.debug("  Locals:")
                for loc in func_def.locals:
                    if loc.type.slot_size == 2:
                        logger_codegen.debug(
                            "    %s (%s) @ slots %d-%d", loc.name, loc.type.name, loc.slot, loc.slot + 1
                        )
                    else:
                        logger_codegen.debug("    %s (%s) @ slot %d", loc.name, loc.type.name, loc.slot)

            sig = self._get_jca_signature(func_def)
            max_stack = calculate_max_stack(code, debug=get_debug_context().verbose, func_name=func_name)
            # Use max locals including any temps allocated for array reference caching
            locals_slots = ctx.max_locals_with_temps
            self.frame_sizes[func_name] = FrameSize(max_stack, locals_slots)

            methods.append(
                Method(
                    access="private static",
                    name=func_name,
                    signature=sig,
                    stack=max_stack,
                    locals=locals_slots,
                    code=code,
                )
            )

        return methods

    def build(self) -> Package:
        # Ensure call graph analysis has been run to populate offload_stack_sizes
        if not self.symbols.offload_stack_sizes:
            from jcc.analysis.callgraph import analyze_call_graph

            analyze_call_graph(self.symbols, max_stack_slots=self.config.analysis.max_stack_slots)

        # Build imports first (needed for constant pool indices)
        registry = self._build_imports()
        self._build_constant_pool(registry)
        fields = self._build_fields()

        methods = [
            self._build_init_method(),
            self._build_install_method(),
            self._build_process_wrapper(),
        ]

        user_process = self._build_user_process()
        if user_process:
            methods.append(user_process)
        methods.extend(self._build_user_methods())

        # Build implements list for ExtendedLength interface
        implements: list[tuple[str, str]] = []
        if registry.has(ImportRegistry.APDU_EXT):
            # ExtendedLength is interface token 0 in javacardx/apdu
            extended_apdu_idx = registry.get_index(ImportRegistry.APDU_EXT)
            implements.append((f"{extended_apdu_idx}.0", "javacardx/apdu/ExtendedLength"))

        applet_class = Class(
            access="public",
            name=self.config.applet.class_name,
            index=0,
            extends="0.3",
            extends_comment="extends javacard/framework/Applet",
            implements=implements,
            fields=fields,
            public_method_table_base=7,
            public_method_table_count=8,
            public_method_table=[
                MethodTableEntry("equals(Ljava/lang/Object;)Z", 0),
                MethodTableEntry("register()V", 1),
                MethodTableEntry("register([BSB)V", 2),
                MethodTableEntry("selectingApplet()Z", 3),
                MethodTableEntry("deselect()V", 4),
                MethodTableEntry(
                    "getShareableInterfaceObject(Ljavacard/framework/AID;B)Ljavacard/framework/Shareable;", 5
                ),
                MethodTableEntry("select()Z", 6),
                MethodTableEntry("process(Ljavacard/framework/APDU;)V", 7),
            ],
            package_method_table_base=0,
            package_method_table=[],
            methods=methods,
        )

        return Package(
            name=self.config.package.name,
            aid=self.config.package.aid,
            version=self.config.package.version,
            imports=registry.get_imports(),
            applets=[
                AppletEntry(self.config.applet.aid, self.config.applet.class_name),
            ],
            constant_pool=self.cp_entries,
            classes=[applet_class],
        )
