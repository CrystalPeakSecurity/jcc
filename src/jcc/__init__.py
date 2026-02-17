"""jcc: LLVM IR to JavaCard bytecode compiler."""

import importlib.metadata
from pathlib import Path

try:
    _metadata = importlib.metadata.metadata(__package__ or __name__)
    __version__ = _metadata["Version"]
except importlib.metadata.PackageNotFoundError:
    import tomllib

    with open(Path(__file__).parent.parent.parent / "pyproject.toml", "rb") as _fh:
        __version__ = tomllib.load(_fh)["project"]["version"]
