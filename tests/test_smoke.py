"""Smoke tests - basic sanity checks that the package loads."""

import pytest


class TestImports:
    """Test that modules import correctly."""

    def test_import_jcc(self) -> None:
        """Can import the main package."""
        import jcc

        assert jcc.__version__ == "0.1.0"

    def test_import_ir_types(self) -> None:
        """Can import IR types."""
        from jcc.ir.types import SSAName, BlockLabel, GlobalName, JCType

        # Verify imports exist
        assert SSAName is not None
        assert BlockLabel is not None
        assert GlobalName is not None
        assert JCType is not None

    def test_import_cli(self) -> None:
        """Can import the CLI module."""
        from jcc import cli

        assert callable(cli.main)


class TestTypes:
    """Test the type system."""

    def test_jctype_slots(self) -> None:
        """JCType.slots returns correct values."""
        from jcc.ir.types import JCType

        assert JCType.BYTE.slots == 1
        assert JCType.SHORT.slots == 1
        assert JCType.INT.slots == 2
        assert JCType.REF.slots == 1
        assert JCType.VOID.slots == 0

        # LONG must be transformed before use
        with pytest.raises(ValueError, match="LONG is not supported"):
            _ = JCType.LONG.slots

    def test_jctype_byte_size(self) -> None:
        """JCType.byte_size returns LLVM memory sizes."""
        from jcc.ir.types import JCType

        assert JCType.BYTE.byte_size == 1
        assert JCType.SHORT.byte_size == 2
        assert JCType.INT.byte_size == 4
        assert JCType.REF.byte_size == 4
        assert JCType.VOID.byte_size == 0

        # LONG must be transformed before use
        with pytest.raises(ValueError, match="LONG is not supported"):
            _ = JCType.LONG.byte_size


class TestCLI:
    """Test the CLI."""

    def test_cli_can_import(self) -> None:
        """CLI app can be imported."""
        from jcc.cli import app, run

        assert app is not None
        assert callable(run)
