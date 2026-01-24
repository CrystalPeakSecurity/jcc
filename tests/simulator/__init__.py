"""Simulator test infrastructure for JCC.

This package provides fixtures and utilities for running end-to-end tests
against the JavaCard simulator.
"""

from tests.simulator.docker import DockerSimulator
from tests.simulator.java_bridge import JavaBridge, AppletInfo

__all__ = [
    "DockerSimulator",
    "JavaBridge",
    "AppletInfo",
]
