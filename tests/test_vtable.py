"""Tests for output/vtable.py - VTable extraction."""

import pytest

from jcc.api.types import APIRegistry, ClassInfo, MethodInfo
from jcc.output.vtable import (
    VTableError,
    extract_vtable,
    find_vtable_index,
)


def _make_method(
    class_name: str,
    method_name: str,
    token: int,
    is_static: bool = False,
    descriptor: str = "()V",
) -> MethodInfo:
    """Helper to create MethodInfo."""
    return MethodInfo(
        class_name=class_name,
        class_token=0,
        method_name=method_name,
        method_token=token,
        descriptor=descriptor,
        is_static=is_static,
        return_type=None,
    )


def _make_applet_class() -> ClassInfo:
    """Create mock Applet class with typical methods."""
    # Methods are now stored as tuples of overloads
    methods = {
        "equals": (_make_method("javacard/framework/Applet", "equals", 0, is_static=False),),
        "register": (_make_method("javacard/framework/Applet", "register", 1, is_static=False),),
        "selectingApplet": (
            _make_method("javacard/framework/Applet", "selectingApplet", 3, is_static=False),
        ),
        "deselect": (_make_method("javacard/framework/Applet", "deselect", 4, is_static=False),),
        "select": (_make_method("javacard/framework/Applet", "select", 6, is_static=False),),
        "process": (_make_method("javacard/framework/Applet", "process", 7, is_static=False),),
        # Static method should not appear in vtable
        "install": (_make_method("javacard/framework/Applet", "install", 99, is_static=True),),
    }
    return ClassInfo(
        name="javacard/framework/Applet",
        token=5,
        methods=methods,
    )


@pytest.fixture
def api() -> APIRegistry:
    """Create mock API registry."""
    classes = {
        "javacard/framework/Applet": _make_applet_class(),
    }
    return APIRegistry(classes=classes)


class TestExtractVtable:
    """Tests for extract_vtable()."""

    def test_extracts_virtual_methods(self, api: APIRegistry) -> None:
        """Extracts only non-static methods."""
        vtable = extract_vtable(api, "javacard/framework/Applet")

        # Should not include static 'install'
        names = {e.name for e in vtable}
        assert "install" not in names
        assert "process" in names
        assert "register" in names

    def test_sorted_by_token(self, api: APIRegistry) -> None:
        """VTable is sorted by method token."""
        vtable = extract_vtable(api, "javacard/framework/Applet")

        tokens = [e.index for e in vtable]
        assert tokens == sorted(tokens)

    def test_entries_have_correct_fields(self, api: APIRegistry) -> None:
        """VTableEntry has correct index, name, descriptor."""
        vtable = extract_vtable(api, "javacard/framework/Applet")

        process_entry = next(e for e in vtable if e.name == "process")
        assert process_entry.index == 7
        assert process_entry.name == "process"
        assert process_entry.descriptor == "()V"

    def test_class_not_found(self, api: APIRegistry) -> None:
        """Raises VTableError if class not in registry."""
        with pytest.raises(VTableError, match="not found"):
            extract_vtable(api, "com/example/NonExistent")


class TestFindVtableIndex:
    """Tests for find_vtable_index()."""

    def test_finds_process(self, api: APIRegistry) -> None:
        """Find process method index."""
        vtable = extract_vtable(api, "javacard/framework/Applet")
        idx = find_vtable_index(vtable, "process")
        assert idx == 7

    def test_finds_register(self, api: APIRegistry) -> None:
        """Find register method index."""
        vtable = extract_vtable(api, "javacard/framework/Applet")
        idx = find_vtable_index(vtable, "register")
        assert idx == 1

    def test_method_not_found(self, api: APIRegistry) -> None:
        """Raises VTableError if method not in vtable."""
        vtable = extract_vtable(api, "javacard/framework/Applet")
        with pytest.raises(VTableError, match="not found in vtable"):
            find_vtable_index(vtable, "nonexistent")
