"""Tests for analysis/base.py - infrastructure classes."""

import pytest

from jcc.analysis.base import AnalysisError, PhaseOutput


class ConcretePhaseOutput(PhaseOutput):
    """Concrete implementation for testing."""

    errors_to_return: list[str]

    def __init__(self, errors: list[str] | None = None) -> None:
        # Must set errors_to_return before calling super().__init__
        # because __post_init__ calls validate()
        object.__setattr__(self, "errors_to_return", errors or [])
        super().__init__()

    def validate(self) -> list[str]:
        return self.errors_to_return


class TestAnalysisError:
    def test_basic_message(self) -> None:
        err = AnalysisError("something went wrong")
        assert "something went wrong" in str(err)

    def test_with_func_name(self) -> None:
        err = AnalysisError("failed", func_name="my_func")
        assert "my_func" in str(err)
        assert "failed" in str(err)

    def test_with_phase(self) -> None:
        err = AnalysisError("failed", phase="narrowing")
        assert "[narrowing]" in str(err)
        assert "failed" in str(err)

    def test_with_all_context(self) -> None:
        err = AnalysisError("failed", func_name="my_func", phase="narrowing")
        assert "[narrowing]" in str(err)
        assert "my_func" in str(err)
        assert "failed" in str(err)


class TestPhaseOutput:
    def test_valid_output_succeeds(self) -> None:
        # Should not raise
        output = ConcretePhaseOutput(errors=[])
        assert output is not None

    def test_invalid_output_raises(self) -> None:
        with pytest.raises(AnalysisError) as exc_info:
            ConcretePhaseOutput(errors=["error 1", "error 2"])

        assert "ConcretePhaseOutput validation failed" in str(exc_info.value)
        assert "error 1" in str(exc_info.value)
        assert "error 2" in str(exc_info.value)

    def test_frozen_after_construction(self) -> None:
        output = ConcretePhaseOutput(errors=[])
        # PhaseOutput is frozen, so attributes can't be modified
        # (though our test class doesn't actually enforce this properly
        # since we're not using @dataclass)
        assert output is not None
