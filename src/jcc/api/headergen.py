"""Generate C header files from JavaCard SDK export files.

Produces version-specific headers (e.g., 3.0.4/javacard/framework.h)
with extern declarations and #define aliases for all public API methods.
"""

from pathlib import Path

from jcc.api.types import APIRegistry, ClassInfo, MethodInfo


# JVM type descriptor -> C type
_TYPE_MAP = {
    "B": "char",
    "Z": "char",
    "S": "short",
    "I": "int",
    "V": "void",
}


def parse_descriptor(descriptor: str) -> tuple[list[str], str]:
    """Parse a JVM method descriptor into C parameter types and return type.

    Args:
        descriptor: JVM descriptor like "(SB)[B" or "()V".

    Returns:
        (param_types, return_type) where each is a C type string.

    Examples:
        "(SB)V" -> (["short", "byte"], "void")
        "()[B"  -> ([], "byte*")
        "(Ljavacard/framework/APDU;S)V" -> (["void*", "short"], "void")
    """
    # Split at ')' to get params and return
    paren_idx = descriptor.index(")")
    params_str = descriptor[1:paren_idx]
    ret_str = descriptor[paren_idx + 1:]

    params = _parse_type_list(params_str)
    ret = _parse_single_type(ret_str)

    return params, ret


def _parse_type_list(s: str) -> list[str]:
    """Parse a sequence of JVM type descriptors."""
    types: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == "[":
            # Array type — consume element type
            i += 1
            if i < len(s) and s[i] in _TYPE_MAP:
                types.append(_TYPE_MAP[s[i]] + "*")
                i += 1
            elif i < len(s) and s[i] == "L":
                # Array of objects
                end = s.index(";", i)
                class_name = s[i + 1:end].rsplit("/", 1)[-1]
                types.append(f"{class_name}*")
                i = end + 1
            else:
                types.append("void*")
                i += 1
        elif s[i] == "L":
            end = s.index(";", i)
            class_name = s[i + 1:end].rsplit("/", 1)[-1]
            types.append(class_name)
            i = end + 1
        elif s[i] in _TYPE_MAP:
            types.append(_TYPE_MAP[s[i]])
            i += 1
        else:
            i += 1
    return types


def _parse_single_type(s: str) -> str:
    """Parse a single JVM return type descriptor to C type."""
    if not s:
        return "void"
    if s[0] == "[":
        # Array return
        if len(s) > 1 and s[1] in _TYPE_MAP:
            return _TYPE_MAP[s[1]] + "*"
        if len(s) > 1 and s[1] == "L":
            class_name = s[2:s.index(";")].rsplit("/", 1)[-1]
            return f"{class_name}*"
        return "void*"
    if s[0] == "L":
        class_name = s[1:s.index(";")].rsplit("/", 1)[-1]
        return class_name
    return _TYPE_MAP.get(s[0], "void")


def _collect_ref_types(descriptor: str) -> set[str]:
    """Collect all class names referenced in a descriptor."""
    refs: set[str] = set()
    i = 0
    while i < len(descriptor):
        if descriptor[i] == "L":
            end = descriptor.index(";", i)
            refs.add(descriptor[i + 1:end].rsplit("/", 1)[-1])
            i = end + 1
        else:
            i += 1
    return refs


def generate_header(registry: APIRegistry, package_name: str) -> str:
    """Generate a C header file for one JavaCard package.

    Args:
        registry: API registry with parsed class/method info.
        package_name: Package name like "javacard/framework".

    Returns:
        Complete C header file content as a string.
    """
    # Collect classes belonging to this package
    classes = sorted(
        (cls for cls in registry.classes.values() if cls.package_name == package_name),
        key=lambda c: c.name,
    )

    if not classes:
        return ""

    pkg_underscored = package_name.replace("/", "_")

    # Collect all referenced class types for typedefs
    all_ref_types: set[str] = set()
    for cls in classes:
        simple_name = cls.name.rsplit("/", 1)[-1]
        all_ref_types.add(simple_name)
        for method_name, overloads in cls.methods.items():
            if method_name == "<init>":
                continue
            for method in overloads:
                all_ref_types |= _collect_ref_types(method.descriptor)

    lines: list[str] = []
    lines.append("#pragma once")
    lines.append("")

    # Emit guarded typedefs for all referenced class types
    for name in sorted(all_ref_types):
        guard = f"_JCC_{name.upper()}_DEFINED"
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append(f"typedef void* {name};")
        lines.append(f"#endif")
    lines.append("")

    for cls in classes:
        simple_name = cls.name.rsplit("/", 1)[-1]
        lines.append(f"// {simple_name}")

        # Collect all methods, skip constructors
        all_methods: list[tuple[str, MethodInfo, str]] = []
        for method_name, overloads in sorted(cls.methods.items()):
            if method_name == "<init>":
                continue
            for idx, method in enumerate(overloads):
                if len(overloads) > 1 and idx > 0:
                    suffix = f"_{idx}"
                else:
                    suffix = ""
                alias = f"{simple_name}_{method_name}{suffix}"
                all_methods.append((alias, method, suffix))

        for alias, method, suffix in all_methods:
            params, ret = parse_descriptor(method.descriptor)

            # Instance methods get self as first param (typed to class)
            if not method.is_static:
                params = [f"{simple_name} self"] + [
                    f"{t} {_param_name(i)}" for i, t in enumerate(params)
                ]
            else:
                params = [f"{t} {_param_name(i)}" for i, t in enumerate(params)]

            param_str = ", ".join(params) if params else "void"
            linkage = f"__java_{pkg_underscored}_{method.class_name.rsplit('/', 1)[-1]}_{method.method_name}{suffix}"

            # Pad return type for alignment
            ret_padded = ret.ljust(6) if len(ret) < 6 else ret + " "
            lines.append(f"extern {ret_padded} {linkage}({param_str});")

        lines.append("")

        # #define aliases
        for alias, method, suffix in all_methods:
            linkage = f"__java_{pkg_underscored}_{method.class_name.rsplit('/', 1)[-1]}_{method.method_name}{suffix}"
            lines.append(f"#define {alias} {linkage}")

        lines.append("")

    return "\n".join(lines)


def _param_name(index: int) -> str:
    """Generate a parameter name from index: a, b, c, ..."""
    return chr(ord("a") + index)


def generate_all_headers(registry: APIRegistry, output_dir: Path) -> list[Path]:
    """Generate header files for all packages in the registry.

    Args:
        registry: API registry with parsed class/method info.
        output_dir: Root output directory (e.g., data/include/3.0.4/).

    Returns:
        List of paths to generated header files.
    """
    # Collect unique package names
    package_names: set[str] = set()
    for cls in registry.classes.values():
        if cls.package_name:
            package_names.add(cls.package_name)

    generated: list[Path] = []
    for package_name in sorted(package_names):
        content = generate_header(registry, package_name)
        if not content:
            continue

        # Package path: javacard/framework -> javacard/framework.h
        header_path = output_dir / (package_name + ".h")
        header_path.parent.mkdir(parents=True, exist_ok=True)
        header_path.write_text(content)
        generated.append(header_path)

    return generated
