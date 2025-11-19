"""Entry point for running cogito MCP server."""

from pathlib import Path

from cogito.integration.mcp_server import create_server, mcp


def main() -> None:
    """Start the cogito MCP server.

    Initializes the server with default paths and runs via FastMCP's
    built-in stdio transport.
    """
    # Default paths - look for examples directory
    examples_dir = Path(__file__).parent.parent.parent / "examples"

    # Initialize server with discovered tools
    create_server(
        tools_directory=examples_dir,
        memory_path=None,  # Memory can be added later
    )

    # Run server using FastMCP's built-in run method
    mcp.run()


if __name__ == "__main__":
    main()
