"""Tests for output/lifecycle.py - Applet lifecycle method generation."""

import pytest

from jcc.analysis.globals import AllocationResult, MemArray
from jcc.codegen.emit import FunctionCode
from jcc.output.constant_pool import ConstantPool
from jcc.output.lifecycle import (
    build_init_method,
    build_install_method,
    build_process_wrapper,
)


@pytest.fixture
def empty_allocation() -> AllocationResult:
    """Allocation with no memory arrays."""
    return AllocationResult(
        globals={},
        structs={},
        mem_sizes={},
        const_values={},
    )


@pytest.fixture
def allocation_with_arrays() -> AllocationResult:
    """Allocation with memory arrays."""
    return AllocationResult(
        globals={},
        structs={},
        mem_sizes={
            MemArray.MEM_B: 64,
            MemArray.MEM_S: 32,
        },
        const_values={},
    )


def _make_mock_cp(
    mem_arrays: dict[MemArray, int] | None = None,
    make_transient: dict[MemArray, int] | None = None,
) -> ConstantPool:
    """Create a mock ConstantPool with required indices."""
    return ConstantPool(
        _entries=(),
        _packages_used=(),
        _applet_class_idx=0,
        _applet_init_idx=1,
        _register_idx=2,
        _our_class_idx=3,
        _our_init_idx=4,
        _selecting_applet_idx=5,
        _set_incoming_and_receive_idx=6,
        _mem_array_idx=mem_arrays or {},
        _make_transient_idx=make_transient or {},
        _api_method_idx={},
        _user_method_idx={"process": 30},
        _user_method_desc={"process": "(Ljavacard/framework/APDU;S)V"},
        _scalar_field_idx={},
        _api=None,
        _user_functions=frozenset(["process"]),
    )


@pytest.fixture
def mock_cp() -> ConstantPool:
    """Create a mock constant pool with required indices."""
    return _make_mock_cp(
        mem_arrays={
            MemArray.MEM_B: 10,
            MemArray.MEM_S: 11,
        },
        make_transient={
            MemArray.MEM_B: 20,
            MemArray.MEM_S: 21,
        },
    )


class TestBuildInitMethod:
    """Tests for build_init_method()."""

    def test_returns_function_code(
        self, mock_cp: ConstantPool, empty_allocation: AllocationResult
    ) -> None:
        """Returns a FunctionCode instance."""
        code = build_init_method(mock_cp, empty_allocation)
        assert isinstance(code, FunctionCode)

    def test_max_locals_is_one(
        self, mock_cp: ConstantPool, empty_allocation: AllocationResult
    ) -> None:
        """Init method has only 'this' local."""
        code = build_init_method(mock_cp, empty_allocation)
        assert code.max_locals == 1

    def test_ends_with_return(
        self, mock_cp: ConstantPool, empty_allocation: AllocationResult
    ) -> None:
        """Method ends with return instruction."""
        code = build_init_method(mock_cp, empty_allocation)
        assert code.instructions[-1].mnemonic == "return"

    def test_calls_super_init(
        self, mock_cp: ConstantPool, empty_allocation: AllocationResult
    ) -> None:
        """Calls super.<init>()."""
        code = build_init_method(mock_cp, empty_allocation)
        mnemonics = [i.mnemonic for i in code.instructions]
        assert "aload_0" in mnemonics
        assert "invokespecial" in mnemonics

    def test_allocates_arrays(
        self, mock_cp: ConstantPool, allocation_with_arrays: AllocationResult
    ) -> None:
        """Allocates transient arrays when needed."""
        code = build_init_method(mock_cp, allocation_with_arrays)
        mnemonics = [i.mnemonic for i in code.instructions]

        # Should call makeTransient*Array and putstatic_a
        assert "invokestatic" in mnemonics
        assert "putstatic_a" in mnemonics


class TestBuildInstallMethod:
    """Tests for build_install_method()."""

    def test_returns_function_code(self, mock_cp: ConstantPool) -> None:
        """Returns a FunctionCode instance."""
        code = build_install_method(mock_cp)
        assert isinstance(code, FunctionCode)

    def test_max_locals_is_three(self, mock_cp: ConstantPool) -> None:
        """Install has 3 params: bArray, bOffset, bLength."""
        code = build_install_method(mock_cp)
        assert code.max_locals == 3

    def test_max_stack_computed(self, mock_cp: ConstantPool) -> None:
        """Install needs stack for new + dup (max 2, plus safety margin)."""
        code = build_install_method(mock_cp)
        # Actual max is 2, but compute_max_stack adds +2 safety margin
        assert code.max_stack == 4

    def test_creates_new_instance(self, mock_cp: ConstantPool) -> None:
        """Creates new instance with 'new'."""
        code = build_install_method(mock_cp)
        mnemonics = [i.mnemonic for i in code.instructions]
        assert "new" in mnemonics

    def test_calls_constructor(self, mock_cp: ConstantPool) -> None:
        """Calls constructor with invokespecial."""
        code = build_install_method(mock_cp)
        mnemonics = [i.mnemonic for i in code.instructions]
        assert "invokespecial" in mnemonics


class TestBuildProcessWrapper:
    """Tests for build_process_wrapper()."""

    def test_returns_function_code(self, mock_cp: ConstantPool) -> None:
        """Returns a FunctionCode instance."""
        code = build_process_wrapper(mock_cp)
        assert isinstance(code, FunctionCode)

    def test_max_locals_is_two(self, mock_cp: ConstantPool) -> None:
        """Process wrapper has 2 locals: this, apdu."""
        code = build_process_wrapper(mock_cp)
        assert code.max_locals == 2

    def test_checks_selecting_applet(self, mock_cp: ConstantPool) -> None:
        """Calls selectingApplet() and branches."""
        code = build_process_wrapper(mock_cp)
        mnemonics = [i.mnemonic for i in code.instructions]

        # Should have invokevirtual for selectingApplet
        assert "invokevirtual" in mnemonics
        # Should have conditional branch
        assert "ifne" in mnemonics

    def test_calls_user_process(self, mock_cp: ConstantPool) -> None:
        """Calls user's process function."""
        code = build_process_wrapper(mock_cp)
        mnemonics = [i.mnemonic for i in code.instructions]

        # Should have invokestatic for userProcess
        invoke_count = mnemonics.count("invokestatic")
        assert invoke_count >= 1

    def test_has_return_label(self, mock_cp: ConstantPool) -> None:
        """Has a return label for early exit."""
        code = build_process_wrapper(mock_cp)
        labels = [i for i in code.instructions if i.mnemonic == "label"]
        assert len(labels) >= 1
