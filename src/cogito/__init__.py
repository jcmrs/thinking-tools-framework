"""Cogito: Thinking Tools Framework.

A Python framework for AI-augmented metacognition tools using parameterized
YAML prompt templates with Jinja2 rendering.

Five-layer clean architecture:
- Layer 1: UI (CLI, interfaces)
- Layer 2: Orchestration (tool discovery, execution)
- Layer 3: Processing (template rendering, validation)
- Layer 4: Storage (process memory, caching)
- Layer 5: Integration (MCP server, external integrations)
"""

__version__ = "0.1.0"

# Export Layer 5 Integration API for convenience
from cogito.integration import create_server, mcp

__all__ = [
    "create_server",
    "mcp",
    "integration",
    "orchestration",
    "processing",
    "storage",
]
