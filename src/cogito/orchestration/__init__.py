"""Orchestration layer for tool discovery and execution.

This module implements Layer 2 (Orchestration) of the five-layer architecture.
Provides tool registry, discovery, caching, and execution coordination.
"""

from cogito.orchestration.executor import ToolExecutor
from cogito.orchestration.registry import ToolRegistry

__all__ = [
    "ToolRegistry",
    "ToolExecutor",
]
