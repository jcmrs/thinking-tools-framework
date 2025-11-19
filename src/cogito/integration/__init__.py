"""Integration layer for external tool access.

Provides MCP server implementation for thinking tools framework,
enabling integration with AI assistants like Claude Code and Serena.
"""

from cogito.integration.mcp_server import create_server, mcp

__all__ = [
    "create_server",
    "mcp",
]
