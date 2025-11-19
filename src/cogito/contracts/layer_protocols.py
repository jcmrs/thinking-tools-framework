"""Protocol definitions for five-layer architecture.

Defines formal interfaces using Python's typing.Protocol to enforce
architectural boundaries and enable compile-time type checking with mypy.

Layer Structure:
- Layer 1: UI (command-line interfaces, user interaction)
- Layer 2: Orchestration (tool discovery, execution coordination)
- Layer 3: Processing (template rendering, validation)
- Layer 4: Storage (process memory, knowledge graph)
- Layer 5: Integration (MCP server, external integrations)

Dependencies flow downward only: UI → Orchestration → Processing → Storage ← Integration
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


# Layer 2: Orchestration Protocols
@runtime_checkable
class OrchestrationProtocol(Protocol):
    """Protocol for tool execution operations.

    Implementation: ToolExecutor
    Used by: UI layer (cli.py), MCP server
    """

    def execute(
        self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None
    ) -> str:
        """Execute a thinking tool with given parameters.

        Args:
            tool_spec: Tool specification dictionary
            parameters: User-provided parameters (may be incomplete)

        Returns:
            Rendered tool output as string
        """
        ...

    def execute_by_name(
        self,
        tool_name: str,
        tool_registry: Any,
        parameters: dict[str, Any] | None = None,
    ) -> str:
        """Execute a tool by name from a registry.

        Args:
            tool_name: Name of the tool to execute
            tool_registry: ToolRegistry instance to look up tool
            parameters: User-provided parameters

        Returns:
            Rendered tool output
        """
        ...


@runtime_checkable
class ToolRegistryProtocol(Protocol):
    """Protocol for tool registry operations.

    Implementation: ToolRegistry
    Used by: UI layer (cli.py), ToolExecutor
    """

    def discover_tools(self, scan_dirs: list[Path] | None = None) -> int:
        """Discover and load all tools from configured directories.

        Args:
            scan_dirs: Directories to scan. If None, uses configured dirs.

        Returns:
            Number of tools successfully discovered and loaded
        """
        ...

    def load_tool(self, tool_path: Path) -> dict[str, Any]:
        """Load a single tool from a YAML file.

        Args:
            tool_path: Path to tool YAML file

        Returns:
            Loaded and validated tool specification
        """
        ...

    def get_tool(self, tool_name: str) -> dict[str, Any] | None:
        """Get a tool by name from the registry.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool specification dict, or None if not found
        """
        ...

    def list_tools(self) -> list[str]:
        """List all tool names in the registry.

        Returns:
            List of tool names
        """
        ...


# Layer 3: Processing Protocols
@runtime_checkable
class ProcessingProtocol(Protocol):
    """Protocol for template rendering operations.

    Implementation: TemplateRenderer
    Used by: Orchestration layer (executor.py)
    """

    def render(
        self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None
    ) -> str:
        """Render thinking tool template with provided parameters.

        Args:
            tool_spec: Complete tool specification from YAML
            parameters: Parameter values to substitute in template

        Returns:
            Rendered template as string
        """
        ...

    def validate_template_syntax(self, template_source: str) -> bool:
        """Validate Jinja2 template syntax without rendering.

        Args:
            template_source: Raw Jinja2 template string

        Returns:
            True if template syntax is valid
        """
        ...


@runtime_checkable
class ValidationProtocol(Protocol):
    """Protocol for parameter validation.

    Implementation: ParameterValidator
    Used by: Orchestration layer (executor.py)
    """

    def validate_parameters(
        self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate and apply defaults to parameters.

        Args:
            tool_spec: Tool specification with parameter schema
            parameters: User-provided parameters (may be incomplete)

        Returns:
            Validated parameters with defaults applied
        """
        ...


@runtime_checkable
class SchemaValidationProtocol(Protocol):
    """Protocol for tool spec schema validation.

    Implementation: SchemaValidator
    Used by: Tool registry (registry.py)
    """

    def validate_tool_spec(self, tool_spec: dict[str, Any]) -> dict[str, Any]:
        """Validate a complete tool specification against schema.

        Args:
            tool_spec: Tool specification to validate

        Returns:
            Validation result with 'valid' and 'errors' keys
        """
        ...


# Layer 4: Storage Protocols
@runtime_checkable
class StorageProtocol(Protocol):
    """Protocol for process memory operations.

    Implementation: ProcessMemoryStore
    Used by: All layers for persistent storage
    """

    def append_entry(self, entry: dict[str, Any]) -> None:
        """Append a new entry to process memory.

        Args:
            entry: Process memory entry to append
        """
        ...

    def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Get a specific process memory entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            Process memory entry, or None if not found
        """
        ...

    def search_entries(
        self,
        keyword: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search process memory entries.

        Args:
            keyword: Keyword to search in title/summary
            category: Filter by entry type/category
            tags: Filter by tags (must have all)

        Returns:
            List of matching entries
        """
        ...


@runtime_checkable
class KnowledgeGraphProtocol(Protocol):
    """Protocol for knowledge graph operations.

    Implementation: KnowledgeGraph
    Used by: Integration layer (MCP server)
    """

    def build_graph(self) -> None:
        """Build knowledge graph from process memory entries."""
        ...

    def get_related(
        self, entry_id: str, depth: int = 1, include_reverse: bool = False
    ) -> list[dict[str, Any]]:
        """Get entries related to a given entry.

        Args:
            entry_id: Entry to find related entries for
            depth: Depth for relationship traversal
            include_reverse: Include reverse links

        Returns:
            List of related entries
        """
        ...


# Layer 5: Integration Protocol
@runtime_checkable
class IntegrationProtocol(Protocol):
    """Protocol for MCP server and external integrations.

    Implementation: MCPServer
    Used by: External clients via MCP protocol
    """

    async def execute_thinking_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> str:
        """Execute a thinking tool via MCP.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Rendered tool output
        """
        ...

    async def list_thinking_tools(
        self, category: str | None = None
    ) -> list[dict[str, Any]]:
        """List available thinking tools.

        Args:
            category: Optional category filter

        Returns:
            List of tool metadata
        """
        ...

    async def query_process_memory(
        self,
        entry_id: str | None = None,
        keyword: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Query process memory via MCP.

        Args:
            entry_id: Specific entry ID
            keyword: Keyword search
            category: Category filter
            tags: Tag filter

        Returns:
            JSON string with query results
        """
        ...


# Layer 1: UI Protocol
@runtime_checkable
class UIProtocol(Protocol):
    """Protocol for command-line interface operations.

    Implementations: CLI commands in cli.py
    Used by: External invocation (command line)
    """

    def execute_command(self, args: list[str]) -> int:
        """Execute a CLI command.

        Args:
            args: Command-line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        ...

    def list_available_tools(
        self, orchestrator: OrchestrationProtocol, category: str | None = None
    ) -> None:
        """List available thinking tools.

        Args:
            orchestrator: Orchestration layer instance
            category: Optional category filter
        """
        ...

    def execute_tool_by_name(
        self,
        orchestrator: OrchestrationProtocol,
        tool_name: str,
        parameters: dict[str, Any],
    ) -> None:
        """Execute a tool by name.

        Args:
            orchestrator: Orchestration layer instance
            tool_name: Name of tool to execute
            parameters: Tool parameters
        """
        ...
