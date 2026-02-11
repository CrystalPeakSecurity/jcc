"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


# === Corpus Directory ===

CORPUS_DIR = Path(__file__).parent.parent / "corpus"


@pytest.fixture
def corpus_dir() -> Path:
    """Path to the corpus directory containing .ll files."""
    if not CORPUS_DIR.exists():
        pytest.skip("Corpus directory not found")
    return CORPUS_DIR


@pytest.fixture
def example_ll_files(corpus_dir: Path) -> list[Path]:
    """List of all .ll files in the corpus."""
    return sorted(corpus_dir.glob("*.ll"))


@pytest.fixture
def minimal_ll(corpus_dir: Path) -> Path:
    """Path to the minimal example's .ll file."""
    ll_path = corpus_dir / "minimal.ll"
    if not ll_path.exists():
        pytest.skip("minimal.ll not found in corpus")
    return ll_path


@pytest.fixture
def alloca_debug_ll(corpus_dir: Path) -> Path:
    """Path to the alloca test file with debug info."""
    ll_path = corpus_dir / "alloca_test_with_dbg.ll"
    if not ll_path.exists():
        pytest.skip("alloca_test_with_dbg.ll not found in corpus")
    return ll_path


@pytest.fixture
def global_debug_ll(corpus_dir: Path) -> Path:
    """Path to the global test file with debug info."""
    ll_path = corpus_dir / "debug_test_with_dbg.ll"
    if not ll_path.exists():
        pytest.skip("debug_test_with_dbg.ll not found in corpus")
    return ll_path


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests that use corpus .ll files",
    )
