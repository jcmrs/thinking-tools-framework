"""MCP server for thinking tools framework.

Exposes thinking tools via Model Context Protocol (MCP) for integration
with AI assistants like Claude Code and Serena.

Implements three MCP primitives:
1. Tools - Execute and list thinking tools
2. Resources - Access tool specifications and process memory
3. Prompts - Provide contextual guidance
"""

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from cogito.orchestration.executor import ToolExecutor
from cogito.orchestration.registry import ToolRegistry
from cogito.storage.knowledge_graph import KnowledgeGraph
from cogito.storage.process_memory import ProcessMemoryStore

# Initialize FastMCP server
mcp = FastMCP("cogito-thinking-tools")

# Global components (initialized by create_server)
_registry: ToolRegistry | None = None
_executor: ToolExecutor | None = None
_memory_store: ProcessMemoryStore | None = None
_knowledge_graph: KnowledgeGraph | None = None
_tools_directory: Path | None = None


# ============================================================================
# Token Tracking System
# ============================================================================


class SimpleTokenTracker:
    """Simple token usage tracker for MCP operations.

    Tracks estimated token usage for tool executions and provides
    summary statistics for optimization analysis.
    """

    def __init__(self) -> None:
        """Initialize token tracker."""
        self.operations: list[dict[str, Any]] = []

    def track(
        self,
        operation: str,
        input_est: int,
        output_est: int,
        tool_name: str | None = None,
    ) -> None:
        """Track a token-consuming operation.

        Args:
            operation: Type of operation (e.g., 'execute_tool', 'list_tools')
            input_est: Estimated input tokens
            output_est: Estimated output tokens
            tool_name: Optional tool name for tool-specific tracking
        """
        self.operations.append(
            {
                "op": operation,
                "tool": tool_name,
                "in": input_est,
                "out": output_est,
                "total": input_est + output_est,
            }
        )

    def summary(self) -> dict[str, Any]:
        """Get token usage summary statistics.

        Returns:
            Dictionary with total operations, total tokens, and breakdown
        """
        return {
            "total_ops": len(self.operations),
            "total_tokens": sum(op["total"] for op in self.operations),
            "breakdown": self.operations,
        }

    def reset(self) -> None:
        """Reset token tracking statistics."""
        self.operations = []


_token_tracker = SimpleTokenTracker()


def _get_registry() -> ToolRegistry:
    """Get ToolRegistry instance (raises if not initialized)."""
    if _registry is None:
        raise RuntimeError("MCP server not initialized. Call create_server() first.")
    return _registry


def _get_executor() -> ToolExecutor:
    """Get ToolExecutor instance (raises if not initialized)."""
    if _executor is None:
        raise RuntimeError("MCP server not initialized. Call create_server() first.")
    return _executor


def _get_memory_store() -> ProcessMemoryStore:
    """Get ProcessMemoryStore instance (raises if not initialized)."""
    if _memory_store is None:
        raise RuntimeError("Process memory not available. Initialize with memory_path.")
    return _memory_store


def _get_knowledge_graph() -> KnowledgeGraph:
    """Get KnowledgeGraph instance (raises if not initialized)."""
    if _knowledge_graph is None:
        raise RuntimeError("Knowledge graph not available. Initialize with memory_path.")
    return _knowledge_graph


# ============================================================================
# MCP Tools - Executable functions
# ============================================================================


@mcp.tool()
def execute_thinking_tool(tool_name: str, parameters: dict[str, Any]) -> str:
    """Execute a thinking tool with the given parameters.

    Args:
        tool_name: Name of the thinking tool (e.g., 'think_aloud', 'code_review_checklist')
        parameters: Tool-specific parameters as key-value pairs

    Returns:
        Rendered thinking tool output with prompts and guidance
    """
    registry = _get_registry()
    executor = _get_executor()

    # Estimate input tokens (rough: chars / 4)
    input_est = len(str(parameters)) // 4

    try:
        result = executor.execute_by_name(tool_name, registry, parameters)

        # Estimate output tokens and track
        output_est = len(result) // 4
        _token_tracker.track("execute_tool", input_est, output_est, tool_name)

        return result
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {e}"
        output_est = len(error_msg) // 4
        _token_tracker.track("execute_tool_error", input_est, output_est, tool_name)
        return error_msg


@mcp.tool()
def list_thinking_tools(category: str | None = None) -> list[dict[str, Any]]:
    """List all available thinking tools, optionally filtered by category.

    Args:
        category: Optional category filter (metacognition, review, handoff, debugging)

    Returns:
        List of tool metadata dictionaries
    """
    registry = _get_registry()

    try:
        tool_names = registry.list_tools()
        tools = []

        for tool_name in tool_names:
            tool_spec = registry.get_tool(tool_name)
            if tool_spec is not None:
                metadata = tool_spec.get("metadata", {})

                # Filter by category if specified
                if category and metadata.get("category") != category:
                    continue

                tools.append(
                    {
                        "name": metadata.get("name", "unknown"),
                        "display_name": metadata.get("display_name", ""),
                        "description": metadata.get("description", ""),
                        "category": metadata.get("category", ""),
                        "tags": metadata.get("tags", []),
                    }
                )

        return tools
    except Exception as e:
        return [{"error": f"Failed to list tools: {e}"}]


@mcp.tool()
def query_process_memory(
    entry_id: str | None = None,
    keyword: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Query process memory entries by ID, keyword, category, or tags.

    Args:
        entry_id: Specific entry ID to retrieve
        keyword: Keyword to search in title, summary, tags
        category: Filter by entry type/category
        tags: Filter by tags (must have all)

    Returns:
        JSON string containing query results
    """
    memory_store = _get_memory_store()

    try:
        # Get specific entry
        if entry_id:
            entry = memory_store.get_entry(entry_id)
            if entry:
                return json.dumps(entry, indent=2)
            return json.dumps({"error": f"Entry {entry_id} not found"})

        # Search by keyword
        if keyword:
            results = memory_store.search_entries(keyword)
            return json.dumps(results, indent=2)

        # List by category/tags
        entries = memory_store.list_entries(category=category, tags=tags or [])
        return json.dumps(entries, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error querying memory: {e}"})


@mcp.tool()
def query_knowledge_graph(
    entry_id: str | None = None,
    concept: str | None = None,
    depth: int = 1,
) -> str:
    """Query knowledge graph for related entries, dependencies, concepts.

    Args:
        entry_id: Entry ID to find related entries for
        concept: Concept to search for in related_concepts
        depth: Depth for relationship traversal (default: 1)

    Returns:
        JSON string containing query results
    """
    knowledge_graph = _get_knowledge_graph()

    try:
        # Get related entries
        if entry_id:
            related = knowledge_graph.get_related(entry_id, depth=depth)
            return json.dumps(related, indent=2)

        # Find by concept
        if concept:
            results = knowledge_graph.find_by_concept(concept)
            return json.dumps(results, indent=2)

        # Get graph stats
        stats = knowledge_graph.get_graph_stats()
        return json.dumps(stats, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error querying graph: {e}"})


@mcp.tool()
def get_token_usage_stats() -> dict[str, Any]:
    """Get token usage statistics for this MCP session.

    Provides estimated token consumption broken down by operation type
    and tool name. Useful for optimization analysis.

    Returns:
        Dictionary with total operations, total tokens, and breakdown
    """
    return _token_tracker.summary()


# ============================================================================
# MCP Resources - Structured data access
# ============================================================================


@mcp.resource("thinking-tools://discover")
def discover_tool_categories() -> str:
    """List available tool categories and their tools.

    Enables progressive disclosure - client explores categories
    and loads specific tools on-demand instead of loading all
    tool schemas upfront.

    URI Pattern: thinking-tools://discover

    Returns:
        JSON mapping of category names to tool lists
    """
    if _tools_directory is None:
        return json.dumps({"error": "Tools directory not initialized"})

    try:
        categories: dict[str, list[str]] = {}

        # Scan tool directory for category subdirectories
        for category_dir in _tools_directory.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                # Get all YAML files in this category
                tools = sorted(
                    [f.stem for f in category_dir.glob("*.yml")]
                    + [f.stem for f in category_dir.glob("*.yaml")]
                )
                if tools:
                    categories[category_dir.name] = tools

        return json.dumps(categories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error discovering categories: {e}"})


@mcp.resource("thinking-tools://tool-spec/{category}/{tool_name}")
def get_tool_yaml_spec(category: str, tool_name: str) -> str:
    """Get tool YAML specification on-demand.

    Allows clients to load tool spec only when needed, enabling
    progressive disclosure and significant token savings.

    URI Pattern: thinking-tools://tool-spec/metacognition/think_aloud

    Args:
        category: Tool category (e.g., 'metacognition', 'review')
        tool_name: Tool name without extension

    Returns:
        YAML specification as string
    """
    if _tools_directory is None:
        return "Error: Tools directory not initialized"

    try:
        # Try .yml first, then .yaml
        tool_path = _tools_directory / category / f"{tool_name}.yml"
        if not tool_path.exists():
            tool_path = _tools_directory / category / f"{tool_name}.yaml"

        if not tool_path.exists():
            return f"Error: Tool '{category}/{tool_name}' not found"

        with tool_path.open() as f:
            return f.read()
    except Exception as e:
        return f"Error reading tool spec: {e}"


@mcp.resource("thinking-tools://category/{category_name}")
def get_tools_by_category(category_name: str) -> str:
    """Get all thinking tools in a specific category.

    URI Pattern: thinking-tools://category/metacognition
    """
    registry = _get_registry()

    try:
        tool_names = registry.list_tools()
        tools_in_category = []

        for tool_name in tool_names:
            tool_spec = registry.get_tool(tool_name)
            if tool_spec is not None:
                metadata = tool_spec.get("metadata", {})
                if metadata.get("category") == category_name:
                    tools_in_category.append(
                        f"# {metadata.get('display_name', tool_name)}\n"
                        f"{metadata.get('description', '')}\n"
                        f"Tags: {', '.join(metadata.get('tags', []))}\n"
                    )

        if not tools_in_category:
            return f"No tools found in category '{category_name}'"

        return "\n\n".join(tools_in_category)
    except Exception as e:
        return f"Error retrieving tools: {e}"


@mcp.resource("thinking-tools://tool/{tool_name}")
def get_tool_details(tool_name: str) -> str:
    """Get complete specification for a specific thinking tool.

    URI Pattern: thinking-tools://tool/think_aloud
    """
    registry = _get_registry()

    try:
        tool_spec = registry.get_tool(tool_name)
        if tool_spec is None:
            return json.dumps({"error": f"Tool '{tool_name}' not found"})

        return json.dumps(tool_spec, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving tool: {e}"})


@mcp.resource("process-memory://entry/{entry_id}")
def get_process_memory_entry(entry_id: str) -> str:
    """Retrieve a specific process memory entry by ID.

    URI Pattern: process-memory://entry/PM-002
    """
    memory_store = _get_memory_store()

    try:
        entry = memory_store.get_entry(entry_id)
        if entry:
            return json.dumps(entry, indent=2)
        return json.dumps({"error": f"Entry {entry_id} not found"})
    except Exception as e:
        return json.dumps({"error": f"Error retrieving entry: {e}"})


# ============================================================================
# MCP Prompts - Contextual guidance
# ============================================================================


@mcp.prompt()
def get_process_memory_context(concept: str) -> str:
    """Retrieve process memory entries relevant to a specific concept.

    Useful for understanding design rationale and architectural decisions.

    Args:
        concept: Search term (e.g., 'validation', 'security', 'sandboxing')
    """
    memory_store = _get_memory_store()

    try:
        entries = memory_store.search_entries(concept)

        if not entries:
            return f"# Process Memory: {concept}\n\nNo entries found."

        context = f"# Process Memory: {concept}\n\n"
        for entry in entries:
            context += f"## {entry['id']}: {entry['title']}\n"
            context += f"{entry['summary']}\n\n"
            if "rationale" in entry and entry["rationale"]:
                context += f"**Rationale:** {entry['rationale']}\n\n"

        return context
    except Exception as e:
        return f"Error: {e}"


@mcp.prompt()
def get_tool_usage_guide(tool_name: str) -> str:
    """Generate a usage guide for a specific thinking tool.

    Includes tool description, parameter explanations, and usage patterns.

    Args:
        tool_name: Name of the thinking tool
    """
    registry = _get_registry()

    try:
        tool_spec = registry.get_tool(tool_name)
        if tool_spec is None:
            return f"Tool '{tool_name}' not found"

        metadata = tool_spec.get("metadata", {})
        parameters = tool_spec.get("parameters", {})

        guide = f"# {metadata.get('display_name', tool_name)}\n\n"
        guide += f"{metadata.get('description', '')}\n\n"
        guide += f"**Category:** {metadata.get('category', 'unknown')}\n"
        guide += f"**Tags:** {', '.join(metadata.get('tags', []))}\n\n"
        guide += "## Parameters\n\n"

        for param_name, param_schema in parameters.get("properties", {}).items():
            required = param_name in parameters.get("required", [])
            guide += f"- **{param_name}**"
            if required:
                guide += " (required)"
            guide += f": {param_schema.get('description', 'No description')}\n"

        return guide
    except Exception as e:
        return f"Error: {e}"


# ============================================================================
# Server initialization
# ============================================================================


def create_server(
    tools_directory: Path,
    memory_path: Path | None = None,
) -> FastMCP:
    """Factory function to create and initialize MCP server instance.

    Args:
        tools_directory: Path to directory containing YAML tool specs
        memory_path: Optional path to process_memory.jsonl

    Returns:
        Configured FastMCP server instance
    """
    global _registry, _executor, _memory_store, _knowledge_graph, _tools_directory

    # Store tools directory for progressive disclosure
    _tools_directory = tools_directory

    # Initialize orchestration layer
    _registry = ToolRegistry([tools_directory])
    _registry.discover_tools()
    _executor = ToolExecutor()

    # Initialize storage layer (if memory path provided)
    if memory_path and memory_path.exists():
        _memory_store = ProcessMemoryStore(memory_path)
        _knowledge_graph = KnowledgeGraph(_memory_store)

    return mcp
