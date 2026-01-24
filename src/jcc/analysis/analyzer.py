"""Semantic analyzer - builds symbol table and memory layout."""

from pycparser import c_ast

from jcc.consteval import eval_binary_op, eval_unary_op, wrap_int32
from jcc.types.typed_value import LogicalType
from jcc.analysis.helper import (
    AnalysisError,
    get_array_size,
    get_canonical_type,
    get_type_name,
    is_unsigned_type,
)
from jcc.analysis.symbol import (
    ConstStructArrayField,
    FunctionDef,
    FunctionParam,
    GlobalVar,
    LocalVar,
    OffloadLocal,
    StructArrayField,
    StructDef,
    StructField,
    SymbolTable,
)
from jcc.types.memory import MemArray


class Analyzer(c_ast.NodeVisitor):
    def __init__(self, has_intx: bool = False):
        self.symbols = SymbolTable()
        self.errors: list[str] = []
        self._current_function: FunctionDef | None = None
        self._has_intx = has_intx  # True only for cards with javacardx.framework.util.intx (3.0.4+)

    def _check_pragma_in_preceding_lines(self, node: c_ast.Node, pragma_marker: str, max_lines_back: int = 5) -> bool:
        """Check if pragma marker appears in the lines before a node.

        Looks up to max_lines_back lines before the node's coordinate.
        Returns True if pragma found, False otherwise.

        This is used for function-level pragmas like:
            // jcc:cache-array-refs
            void foo(void) { ... }
        """
        if not node.coord:
            return False

        from pathlib import Path

        try:
            lines = Path(node.coord.file).read_text().splitlines()
        except (FileNotFoundError, OSError):
            return False

        # Check lines before the node (up to max_lines_back)
        for offset in range(1, max_lines_back + 1):
            check_line = node.coord.line - offset
            if check_line < 1:
                break
            if check_line - 1 < len(lines):  # 1-indexed to 0-indexed
                if pragma_marker in lines[check_line - 1]:
                    return True

        return False

    def _reject_unsigned(self, type_name: str, context: str) -> bool:
        """Check for unsigned type and record error if found. Returns True if unsigned."""
        if is_unsigned_type(type_name):
            self.errors.append(f"Unsigned types not supported: '{type_name}' in {context}")
            return True
        return False

    def _check_name_available(self, name: str, context: str) -> bool:
        """Check if name is available (not already used). Returns False if conflict."""
        if name in self.symbols.globals:
            self.errors.append(f"{context}: name '{name}' conflicts with existing global")
            return False
        return True

    def _check_no_shadow(self, name: str, context: str) -> bool:
        """Check that name doesn't shadow globals or params. Returns False if shadows."""
        if name in self.symbols.globals:
            self.errors.append(f"{context}: '{name}' shadows global variable")
            return False
        if self._current_function:
            for param in self._current_function.params:
                if param.name == name:
                    self.errors.append(f"{context}: '{name}' shadows parameter")
                    return False
        return True

    def analyze(self, ast: c_ast.FileAST) -> SymbolTable:
        for node in ast.ext:
            if isinstance(node, c_ast.Decl) and isinstance(node.type, c_ast.Struct):
                self._analyze_struct(node.type)

        for node in ast.ext:
            if isinstance(node, c_ast.Decl):
                if isinstance(node.type, c_ast.FuncDecl):
                    self._analyze_function_decl(node)
                elif not isinstance(node.type, c_ast.Struct):
                    self._analyze_global(node)
            elif isinstance(node, c_ast.FuncDef):
                self._analyze_function_def(node)

        if self.errors:
            raise AnalysisError("\n".join(self.errors))

        return self.symbols

    def _analyze_struct(self, node: c_ast.Struct) -> None:
        if node.name is None:
            return
        if node.decls is None:
            return

        fields = []
        for decl in node.decls:
            array_size: int | None = None
            if isinstance(decl.type, c_ast.ArrayDecl):
                array_size = get_array_size(decl.type)
                if array_size is None:
                    self.errors.append(f"Array field {node.name}.{decl.name} must have explicit size")
                    continue

            type_name = get_type_name(decl.type)

            if self._reject_unsigned(type_name, f"struct field {node.name}.{decl.name}"):
                continue

            canonical = get_canonical_type(type_name)

            if not isinstance(canonical, LogicalType) or not canonical.is_primitive:
                self.errors.append(f"Unsupported field type '{type_name}' in struct {node.name}")
                continue

            fields.append(StructField(name=decl.name, type=canonical, array_size=array_size))

        self.symbols.structs[node.name] = StructDef(name=node.name, fields=fields)

    def _analyze_global(self, node: c_ast.Decl) -> None:
        if node.name is None:
            return

        if node.storage and "extern" in node.storage:
            return

        if isinstance(node.type, c_ast.ArrayDecl):
            self._analyze_global_array(node)
        elif isinstance(node.type, c_ast.TypeDecl):
            self._analyze_global_scalar(node)
        elif isinstance(node.type, c_ast.PtrDecl):
            self.errors.append(f"Pointers not supported: {node.name}")
        else:
            self.errors.append(f"Unsupported global declaration: {node.name}")

    def _analyze_global_scalar(self, node: c_ast.Decl) -> None:
        type_name = get_type_name(node.type)

        if self._reject_unsigned(type_name, f"global '{node.name}'"):
            return

        canonical = get_canonical_type(type_name)

        if isinstance(canonical, str) and canonical in self.symbols.structs:
            self._analyze_struct_array(node.name, canonical, 1)
            return

        if not isinstance(canonical, LogicalType) or not canonical.is_primitive:
            self.errors.append(f"Unsupported global type '{type_name}' for {node.name}")
            return

        if not self._check_name_available(node.name, "Global variable"):
            return

        # For INT without intx, store as 2 shorts in MEM_S instead of 1 int in MEM_I
        emulated_int = canonical == LogicalType.INT and not self._has_intx
        if emulated_int:
            mem_array = MemArray.SHORT
            offset = self.symbols.mem_sizes[mem_array]
            self.symbols.mem_sizes[mem_array] += 2  # 2 shorts per int
        else:
            mem_array, offset = self.symbols.allocate_mem(canonical)

        self.symbols.globals[node.name] = GlobalVar(
            name=node.name,
            type=canonical,
            struct_type=None,
            array_size=None,
            mem_array=mem_array,
            offset=offset,
            emulated_int=emulated_int,
        )

    def _analyze_global_array(self, node: c_ast.Decl) -> None:
        array_decl = node.type
        array_size = get_array_size(array_decl)
        is_const = "const" in (node.quals or [])

        if is_const:
            self._analyze_const_array(node, array_decl, array_size)
            return

        if array_size is None:
            if node.init is None:
                self.errors.append(f"Array '{node.name}' must have explicit size or initializer")
                return
            init_values = self._extract_init_values(node.init, node.name)
            if init_values is None:
                return
            array_size = len(init_values)
        elif node.init is not None:
            init_values = self._extract_init_values(node.init, node.name)
            if init_values is not None and len(init_values) != array_size:
                self.errors.append(
                    f"Array '{node.name}' size mismatch: declared {array_size}, got {len(init_values)} values"
                )
                return

        elem_type = array_decl.type
        if isinstance(elem_type, c_ast.TypeDecl):
            type_name = get_type_name(elem_type)

            if self._reject_unsigned(type_name, f"array '{node.name}'"):
                return

            canonical = get_canonical_type(type_name)

            if isinstance(canonical, str) and canonical in self.symbols.structs:
                self._analyze_struct_array(node.name, canonical, array_size)
            elif isinstance(canonical, LogicalType) and canonical.is_primitive:
                if not self._check_name_available(node.name, "Global array"):
                    return

                # For INT arrays without intx, store as 2 shorts per int in MEM_S
                emulated_int = canonical == LogicalType.INT and not self._has_intx
                if emulated_int:
                    mem_array = MemArray.SHORT
                    offset = self.symbols.mem_sizes[mem_array]
                    self.symbols.mem_sizes[mem_array] += array_size * 2
                else:
                    mem_array, offset = self.symbols.allocate_mem(canonical, array_size)

                self.symbols.globals[node.name] = GlobalVar(
                    name=node.name,
                    type=canonical.to_array(),
                    struct_type=None,
                    array_size=array_size,
                    mem_array=mem_array,
                    offset=offset,
                    emulated_int=emulated_int,
                )
            else:
                self.errors.append(f"Unsupported array element type '{type_name}' for {node.name}")
        else:
            self.errors.append(f"Unsupported array type for {node.name}")

    def _analyze_const_array(self, node: c_ast.Decl, array_decl: c_ast.ArrayDecl, explicit_size: int | None) -> None:
        if node.init is None:
            self.errors.append(f"const array '{node.name}' requires an initializer")
            return

        elem_type = array_decl.type
        if not isinstance(elem_type, c_ast.TypeDecl):
            self.errors.append(f"Unsupported const array type for {node.name}")
            return

        type_name = get_type_name(elem_type)
        if self._reject_unsigned(type_name, f"const array '{node.name}'"):
            return

        canonical = get_canonical_type(type_name)

        if isinstance(canonical, str) and canonical in self.symbols.structs:
            self._analyze_const_struct_array(node, array_decl, explicit_size, canonical)
            return

        # Primitive type - extract flat initializer values
        initial_values = self._extract_init_values(node.init, node.name)
        if initial_values is None:
            return

        if explicit_size is not None:
            if explicit_size != len(initial_values):
                self.errors.append(
                    f"const array '{node.name}' size mismatch: declared {explicit_size}, got {len(initial_values)} values"
                )
                return
            array_size = explicit_size
        else:
            array_size = len(initial_values)

        if not isinstance(canonical, LogicalType) or not canonical.is_primitive:
            self.errors.append(f"Unsupported const array element type '{type_name}' for {node.name}")
            return

        if not self._check_name_available(node.name, "Const array"):
            return

        self.symbols.globals[node.name] = GlobalVar(
            name=node.name,
            type=canonical.to_array(),
            struct_type=None,
            array_size=array_size,
            mem_array=None,
            offset=0,
            is_const=True,
            initial_values=initial_values,
        )

    def _extract_init_values(self, init: c_ast.Node, array_name: str) -> list[int] | None:
        if not isinstance(init, c_ast.InitList):
            self.errors.append(f"const array '{array_name}' initializer must be a list")
            return None

        values = []
        for expr in init.exprs:
            value = self._eval_const_expr(expr, array_name)
            if value is None:
                return None
            values.append(value)
        return values

    def _eval_const_expr(self, expr: c_ast.Node, context: str) -> int | None:
        """Evaluate a constant expression at compile time.

        Supports: integer literals, unary ops (-, ~, +), binary ops (+, -, *, /, %, |, &, ^, <<, >>)
        Results are wrapped to 32-bit signed range to match C/JCVM overflow semantics.
        """
        if isinstance(expr, c_ast.Constant):
            try:
                value_str = expr.value
                if value_str.startswith("0x") or value_str.startswith("0X"):
                    return wrap_int32(int(value_str, 16))
                elif value_str.startswith("0") and len(value_str) > 1 and value_str[1].isdigit():
                    return wrap_int32(int(value_str, 8))
                else:
                    return wrap_int32(int(value_str))
            except ValueError:
                self.errors.append(f"Invalid constant in '{context}': {expr.value}")
                return None
        elif isinstance(expr, c_ast.UnaryOp):
            inner = self._eval_const_expr(expr.expr, context)
            if inner is None:
                return None
            result = eval_unary_op(expr.op, inner)
            if result is None:
                self.errors.append(f"Unsupported unary operator '{expr.op}' in '{context}'")
            return result
        elif isinstance(expr, c_ast.BinaryOp):
            left = self._eval_const_expr(expr.left, context)
            right = self._eval_const_expr(expr.right, context)
            if left is None or right is None:
                return None
            result = eval_binary_op(expr.op, left, right)
            if result is None:
                if expr.op in ("/", "%") and right == 0:
                    self.errors.append(f"Division by zero in '{context}'")
                else:
                    self.errors.append(f"Unsupported binary operator '{expr.op}' in '{context}'")
            return result
        else:
            self.errors.append(f"Unsupported constant expression in '{context}'")
            return None

    def _analyze_const_struct_array(
        self, node: c_ast.Decl, array_decl: c_ast.ArrayDecl, explicit_size: int | None, struct_name: str
    ) -> None:
        """Analyze a const struct array with initializers."""
        if node.init is None:
            self.errors.append(f"const struct array '{node.name}' requires an initializer")
            return

        struct_def = self.symbols.structs[struct_name]

        # Extract nested initializers
        struct_values = self._extract_struct_init_values(node.init, node.name, struct_def)
        if struct_values is None:
            return

        # Validate/infer array size
        if explicit_size is not None:
            if explicit_size != len(struct_values):
                self.errors.append(
                    f"const struct array '{node.name}' size mismatch: "
                    f"declared {explicit_size}, got {len(struct_values)} values"
                )
                return
            array_size = explicit_size
        else:
            array_size = len(struct_values)

        if not self._check_name_available(node.name, "Const struct array"):
            return

        # Decompose to SOA and create field entries
        self.symbols.const_struct_array_fields[node.name] = {}

        for field_def in struct_def.fields:
            field_array_size = field_def.array_size if field_def.array_size else 1
            # Collect values for this field across all structs
            field_values = []
            for struct_init in struct_values:
                field_values.extend(struct_init[field_def.name])

            self.symbols.const_struct_array_fields[node.name][field_def.name] = ConstStructArrayField(
                struct_name=node.name,
                field_name=field_def.name,
                element_type=field_def.type,
                count=array_size,
                initial_values=field_values,
                field_array_size=field_array_size,
            )

        # Create marker GlobalVar (no mem_array since it's const)
        self.symbols.globals[node.name] = GlobalVar(
            name=node.name,
            type=None,
            struct_type=struct_name,
            array_size=array_size,
            mem_array=None,
            offset=0,
            is_const=True,
        )

    def _extract_struct_init_values(
        self, init: c_ast.Node, array_name: str, struct_def: StructDef
    ) -> list[dict[str, list[int]]] | None:
        """Extract initializer values for a struct array, returning per-struct field values."""
        if not isinstance(init, c_ast.InitList):
            self.errors.append(f"const struct array '{array_name}' initializer must be a list")
            return None

        result = []
        for i, struct_init in enumerate(init.exprs):
            if not isinstance(struct_init, c_ast.InitList):
                self.errors.append(f"Element {i} of '{array_name}' must be a struct initializer")
                return None

            field_values = self._extract_single_struct_init(struct_init, f"{array_name}[{i}]", struct_def)
            if field_values is None:
                return None
            result.append(field_values)

        return result

    def _extract_single_struct_init(
        self, init: c_ast.InitList, context: str, struct_def: StructDef
    ) -> dict[str, list[int]] | None:
        """Extract field values from a single struct initializer."""
        # Check for designated initializers (e.g., {.x = 1, .y = 2}) which we don't support
        for expr in init.exprs:
            if isinstance(expr, c_ast.NamedInitializer):
                self.errors.append(
                    f"Designated initializers not supported in '{context}'. "
                    f"Use positional initialization instead (e.g., {{1, 2}} not {{.x = 1, .y = 2}})"
                )
                return None

        if len(init.exprs) != len(struct_def.fields):
            self.errors.append(
                f"Struct initializer '{context}' has {len(init.exprs)} values, expected {len(struct_def.fields)}"
            )
            return None

        result = {}
        for expr, field_def in zip(init.exprs, struct_def.fields):
            if field_def.array_size:
                # Array field: expect nested InitList
                if not isinstance(expr, c_ast.InitList):
                    self.errors.append(f"Field '{field_def.name}' in '{context}' requires array initializer")
                    return None
                values = self._extract_init_values(expr, f"{context}.{field_def.name}")
                if values is None:
                    return None
                if len(values) != field_def.array_size:
                    self.errors.append(f"Array field '{field_def.name}' in '{context}' size mismatch")
                    return None
                result[field_def.name] = values
            else:
                # Scalar field
                value = self._eval_const_expr(expr, f"{context}.{field_def.name}")
                if value is None:
                    return None
                result[field_def.name] = [value]

        return result

    def _analyze_struct_array(self, name: str, struct_name: str, array_size: int) -> None:
        if not self._check_name_available(name, "Struct array"):
            return

        struct_def = self.symbols.structs[struct_name]
        self.symbols.struct_array_fields[name] = {}

        for struct_field in struct_def.fields:
            field_array_size = struct_field.array_size if struct_field.array_size else 1
            total_count = array_size * field_array_size

            # Handle emulated int fields (INT stored as 2 shorts when intx not available)
            emulated_int = struct_field.type == LogicalType.INT and not self._has_intx
            if emulated_int:
                mem_array = MemArray.SHORT
                offset = self.symbols.mem_sizes[mem_array]
                self.symbols.mem_sizes[mem_array] += total_count * 2  # 2 shorts per int
            else:
                mem_array, offset = self.symbols.allocate_mem(struct_field.type, total_count)

            self.symbols.struct_array_fields[name][struct_field.name] = StructArrayField(
                struct_name=name,
                field_name=struct_field.name,
                mem_array=mem_array,
                offset=offset,
                count=array_size,
                field_array_size=field_array_size,
                emulated_int=emulated_int,
            )

        self.symbols.globals[name] = GlobalVar(
            name=name,
            type=None,
            struct_type=struct_name,
            array_size=array_size,
            mem_array=None,
            offset=0,
        )

    def _analyze_function_decl(self, node: c_ast.Decl) -> None:
        if node.storage and "extern" in node.storage:
            return

        func_decl = node.type
        func_name = node.name

        ret_type = get_type_name(func_decl.type)

        if self._reject_unsigned(ret_type, f"return type of '{func_name}'"):
            return

        ret_canonical = get_canonical_type(ret_type)

        if not isinstance(ret_canonical, LogicalType) or not ret_canonical.is_return_type:
            self.errors.append(f"Unsupported return type '{ret_type}' for function {func_name}")
            return

        params = self._analyze_params(func_decl.args)

        # Don't overwrite an existing function definition with a forward declaration
        if func_name in self.symbols.functions and self.symbols.functions[func_name].body is not None:
            return

        self.symbols.functions[func_name] = FunctionDef(
            name=func_name,
            return_type=ret_canonical,
            params=params,
            body=None,
        )

    def _analyze_function_def(self, node: c_ast.FuncDef) -> None:
        func_name = node.decl.name
        func_decl = node.decl.type

        ret_type = get_type_name(func_decl.type)

        if self._reject_unsigned(ret_type, f"return type of '{func_name}'"):
            return

        ret_canonical = get_canonical_type(ret_type)

        if not isinstance(ret_canonical, LogicalType) or not ret_canonical.is_return_type:
            self.errors.append(f"Unsupported return type '{ret_type}' for function {func_name}")
            return

        params = self._analyze_params(func_decl.args)

        # Check for array caching pragma
        enable_array_caching = self._check_pragma_in_preceding_lines(node, "jcc:cache-array-refs")

        func_def = FunctionDef(
            name=func_name,
            return_type=ret_canonical,
            params=params,
            body=node.body,
            enable_array_caching=enable_array_caching,
        )

        self._current_function = func_def
        self._analyze_locals(node.body, func_def)
        self._current_function = None

        self.symbols.functions[func_name] = func_def

    def _analyze_params(self, params: c_ast.ParamList | None) -> list[FunctionParam]:
        result = []
        if params is None:
            return result

        seen_names: set[str] = set()

        for param in params.params:
            if isinstance(param, c_ast.EllipsisParam):
                self.errors.append("Variadic functions not supported")
                continue

            if param.name is None:
                continue

            if param.name in seen_names:
                self.errors.append(f"Duplicate parameter name: '{param.name}'")
                continue
            seen_names.add(param.name)

            if param.name in self.symbols.globals:
                self.errors.append(f"Parameter '{param.name}' shadows global variable")
                continue

            if isinstance(param.type, c_ast.ArrayDecl):
                elem_type = get_type_name(param.type.type)
                if self._reject_unsigned(elem_type, f"parameter '{param.name}'"):
                    continue
                canonical = get_canonical_type(elem_type)
                if isinstance(canonical, LogicalType) and canonical.is_primitive:
                    result.append(
                        FunctionParam(
                            name=param.name,
                            type=canonical.to_array(),
                        )
                    )
                else:
                    self.errors.append(f"Unsupported array parameter type: {elem_type}")
            elif isinstance(param.type, c_ast.PtrDecl):
                ptr_type_name = get_type_name(param.type)

                # Only void* and APDU are REF (opaque references)
                if ptr_type_name in ("void*", "APDU"):
                    result.append(
                        FunctionParam(
                            name=param.name,
                            type=LogicalType.REF,
                        )
                    )
                else:
                    # Other pointers (byte*, short*, etc.) are arrays
                    elem_type = get_type_name(param.type.type)
                    if self._reject_unsigned(elem_type, f"parameter '{param.name}'"):
                        continue
                    canonical = get_canonical_type(elem_type)
                    if isinstance(canonical, LogicalType) and canonical.is_primitive:
                        result.append(
                            FunctionParam(
                                name=param.name,
                                type=canonical.to_array(),
                            )
                        )
                    else:
                        self.errors.append(f"Unsupported pointer parameter type: {elem_type}")
            else:
                type_name = get_type_name(param.type)
                if self._reject_unsigned(type_name, f"parameter '{param.name}'"):
                    continue
                canonical = get_canonical_type(type_name)
                if canonical == LogicalType.REF:
                    result.append(
                        FunctionParam(
                            name=param.name,
                            type=LogicalType.REF,
                        )
                    )
                elif isinstance(canonical, LogicalType) and canonical.is_primitive:
                    result.append(
                        FunctionParam(
                            name=param.name,
                            type=canonical,
                        )
                    )
                else:
                    self.errors.append(f"Unsupported parameter type: {type_name}")

        return result

    def _collect_all_decls(self, node: c_ast.Node) -> list[c_ast.Decl]:
        decls: list[c_ast.Decl] = []

        if isinstance(node, c_ast.Decl):
            decls.append(node)
        elif isinstance(node, c_ast.Compound):
            if node.block_items:
                for item in node.block_items:
                    decls.extend(self._collect_all_decls(item))
        elif isinstance(node, c_ast.If):
            if node.iftrue:
                decls.extend(self._collect_all_decls(node.iftrue))
            if node.iffalse:
                decls.extend(self._collect_all_decls(node.iffalse))
        elif isinstance(node, c_ast.For):
            if node.init and isinstance(node.init, c_ast.DeclList):
                for decl in node.init.decls:
                    decls.append(decl)
            if node.stmt:
                decls.extend(self._collect_all_decls(node.stmt))
        elif isinstance(node, c_ast.While):
            if node.stmt:
                decls.extend(self._collect_all_decls(node.stmt))
        elif isinstance(node, c_ast.DoWhile):
            if node.stmt:
                decls.extend(self._collect_all_decls(node.stmt))
        elif isinstance(node, c_ast.Switch):
            if node.stmt:
                decls.extend(self._collect_all_decls(node.stmt))
        elif isinstance(node, c_ast.Case):
            if node.stmts:
                for stmt in node.stmts:
                    decls.extend(self._collect_all_decls(stmt))
        elif isinstance(node, c_ast.Default):
            if node.stmts:
                for stmt in node.stmts:
                    decls.extend(self._collect_all_decls(stmt))

        return decls

    def _get_offload_mem_array(self, logical_type: LogicalType) -> MemArray:
        """Map a logical type to its corresponding offload stack array."""
        return {
            LogicalType.BYTE: MemArray.STACK_B,
            LogicalType.SHORT: MemArray.STACK_S,
            LogicalType.INT: MemArray.STACK_I,
        }[logical_type]

    def _analyze_locals(self, body: c_ast.Compound, func: FunctionDef) -> None:
        if body.block_items is None:
            return
        next_slot = sum(p.type.slot_size for p in func.params)

        # Track offload offsets per type
        offload_offsets: dict[MemArray, int] = {
            MemArray.STACK_B: 0,
            MemArray.STACK_S: 0,
            MemArray.STACK_I: 0,
        }

        all_decls = self._collect_all_decls(body)

        for item in all_decls:
            if isinstance(item, c_ast.Decl):
                if item.name is None:
                    continue

                # Check for storage classes and type qualifiers
                is_static = item.storage and "static" in item.storage
                is_offload = item.quals and "volatile" in item.quals

                # Detect conflicting storage classes
                if is_static and is_offload:
                    self.errors.append(f"Cannot combine 'static' and 'offload' on variable: {item.name}")
                    continue

                if is_static:
                    # Static locals are stored in global memory arrays
                    if isinstance(item.type, c_ast.PtrDecl):
                        self.errors.append(f"Static local pointers not supported: {item.name}")
                        continue

                    mangled_name = f"{func.name}${item.name}"

                    if not self._check_no_shadow(item.name, "Static local"):
                        continue

                    if isinstance(item.type, c_ast.ArrayDecl):
                        # Static local array
                        array_size = get_array_size(item.type)
                        if array_size is None:
                            self.errors.append(f"Static local array '{item.name}' must have explicit size")
                            continue

                        elem_type = item.type.type
                        if isinstance(elem_type, c_ast.TypeDecl):
                            type_name = get_type_name(elem_type)
                            if self._reject_unsigned(type_name, f"static local array '{item.name}'"):
                                continue
                            canonical = get_canonical_type(type_name)
                            if isinstance(canonical, LogicalType) and canonical.is_primitive:
                                # For INT arrays without intx, store as 2 shorts per int in MEM_S
                                emulated_int = canonical == LogicalType.INT and not self._has_intx
                                if emulated_int:
                                    mem_array = MemArray.SHORT
                                    offset = self.symbols.mem_sizes[mem_array]
                                    self.symbols.mem_sizes[mem_array] += array_size * 2
                                else:
                                    mem_array, offset = self.symbols.allocate_mem(canonical, array_size)

                                self.symbols.globals[mangled_name] = GlobalVar(
                                    name=mangled_name,
                                    type=canonical.to_array(),
                                    struct_type=None,
                                    array_size=array_size,
                                    mem_array=mem_array,
                                    offset=offset,
                                    emulated_int=emulated_int,
                                )
                                func.static_locals[item.name] = mangled_name
                            else:
                                self.errors.append(f"Unsupported static local array element type '{type_name}'")
                        else:
                            self.errors.append(f"Unsupported static local array type for {item.name}")
                        continue

                    # Static local scalar
                    type_name = get_type_name(item.type)
                    if self._reject_unsigned(type_name, f"static local '{item.name}'"):
                        continue

                    canonical = get_canonical_type(type_name)
                    if not isinstance(canonical, LogicalType) or not canonical.is_primitive:
                        self.errors.append(f"Unsupported static local type '{type_name}' for {item.name}")
                        continue

                    # Allocate in global memory with mangled name
                    # For INT without intx, store as 2 shorts in MEM_S
                    emulated_int = canonical == LogicalType.INT and not self._has_intx
                    if emulated_int:
                        mem_array = MemArray.SHORT
                        offset = self.symbols.mem_sizes[mem_array]
                        self.symbols.mem_sizes[mem_array] += 2
                    else:
                        mem_array, offset = self.symbols.allocate_mem(canonical)

                    self.symbols.globals[mangled_name] = GlobalVar(
                        name=mangled_name,
                        type=canonical,
                        struct_type=None,
                        array_size=None,
                        mem_array=mem_array,
                        offset=offset,
                        emulated_int=emulated_int,
                    )
                    func.static_locals[item.name] = mangled_name
                    continue

                # Pointer locals (array references) always go on JCVM stack (register)
                if isinstance(item.type, c_ast.PtrDecl):
                    elem_type = get_type_name(item.type.type)
                    if self._reject_unsigned(elem_type, f"local '{item.name}'"):
                        continue
                    canonical = get_canonical_type(elem_type)
                    if isinstance(canonical, LogicalType) and canonical.is_primitive:
                        if not self._check_no_shadow(item.name, "Local variable"):
                            continue
                        func.locals.append(
                            LocalVar(
                                name=item.name,
                                type=canonical.to_array(),
                                slot=next_slot,
                            )
                        )
                        next_slot += 1
                    else:
                        self.errors.append(f"Unsupported local pointer type '{elem_type}' for {item.name}")
                    continue
                if isinstance(item.type, c_ast.ArrayDecl):
                    self.errors.append(f"Local arrays not supported: {item.name}")
                    continue

                type_name = get_type_name(item.type)

                if self._reject_unsigned(type_name, f"local '{item.name}'"):
                    continue

                canonical = get_canonical_type(type_name)

                if not isinstance(canonical, LogicalType) or not canonical.is_primitive:
                    self.errors.append(f"Unsupported local variable type '{type_name}' for {item.name}")
                    continue

                if not self._check_no_shadow(item.name, "Local variable"):
                    continue

                if is_offload:
                    # Explicit offload: use STACK_* array
                    # For INT without intx, use STACK_S with 2 slots per int
                    emulated_int = canonical == LogicalType.INT and not self._has_intx
                    if emulated_int:
                        offload_mem = MemArray.STACK_S
                        offset = offload_offsets[offload_mem]
                        offload_offsets[offload_mem] += 2  # 2 shorts per int
                    else:
                        offload_mem = self._get_offload_mem_array(canonical)
                        offset = offload_offsets[offload_mem]
                        offload_offsets[offload_mem] += 1

                    func.offload_locals.append(
                        OffloadLocal(
                            name=item.name,
                            type=canonical,
                            mem_array=offload_mem,
                            offset=offset,
                            emulated_int=emulated_int,
                        )
                    )
                else:
                    # Default: JCVM stack (fast)
                    func.locals.append(
                        LocalVar(
                            name=item.name,
                            type=canonical,
                            slot=next_slot,
                        )
                    )
                    next_slot += canonical.slot_size
