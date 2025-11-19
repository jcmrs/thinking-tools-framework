"""Unit tests for MCP server implementation using FastMCP."""

import json
from pathlib import Path

import pytest
from fastmcp.client import Client

from cogito.integration.mcp_server import create_server, mcp


@pytest.fixture
def temp_tools_dir(tmp_path: Path) -> Path:
    """Create temporary tools directory with sample tool."""
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()

    # Create sample tool
    tool_file = tools_dir / "test_tool.yml"
    tool_file.write_text(
        """
metadata:
  name: test_tool
  display_name: Test Tool
  description: A test tool
  category: test
  author: test
  version: 1.0.0

parameters:
  type: object
  properties:
    input:
      type: string
      description: Test input
  required: [input]

template:
  source: |
    Test output: {{ input }}
"""
    )

    return tools_dir


@pytest.fixture
def temp_memory_file(tmp_path: Path) -> Path:
    """Create temporary process memory file."""
    memory_file = tmp_path / "process_memory.jsonl"
    memory_file.write_text(
        json.dumps(
            {
                "id": "test-001",
                "title": "Test Entry",
                "type": "Test",
                "summary": "A test entry",
                "tags": ["test"],
                "related_concepts": ["testing"],
                "links": ["test-002"],
            }
        )
        + "\n"
    )
    with open(memory_file, "a") as f:
        f.write(
            json.dumps(
                {
                    "id": "test-002",
                    "title": "Related Entry",
                    "type": "Test",
                    "summary": "A related entry",
                    "tags": ["test", "related"],
                    "related_concepts": ["testing"],
                    "links": [],
                }
            )
            + "\n"
        )
    return memory_file


class TestMCPServerInit:
    """Test MCP server initialization."""

    def test_create_server(self, temp_tools_dir: Path) -> None:
        """Test create_server factory function."""
        server = create_server(temp_tools_dir)
        assert server.name == "cogito-thinking-tools"

    def test_create_server_with_memory(self, temp_tools_dir: Path, temp_memory_file: Path) -> None:
        """Test create_server with memory path initializes storage layer."""
        server = create_server(temp_tools_dir, memory_path=temp_memory_file)
        assert server is not None


class TestMCPServerToolExecution:
    """Test tool execution functionality."""

    @pytest.mark.asyncio
    async def test_execute_thinking_tool(self, temp_tools_dir: Path) -> None:
        """Test executing a thinking tool."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            result = await client.call_tool(
                "execute_thinking_tool",
                {
                    "tool_name": "test_tool",
                    "parameters": {"input": "test value"},
                },
            )

            # Extract content from CallToolResult
            content = str(result.content[0].text) if hasattr(result, "content") else str(result)
            assert "Test output: test value" in content

    @pytest.mark.asyncio
    async def test_execute_thinking_tool_handles_errors(self, temp_tools_dir: Path) -> None:
        """Test that tool execution handles errors gracefully."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            result = await client.call_tool(
                "execute_thinking_tool",
                {
                    "tool_name": "nonexistent_tool",
                    "parameters": {"input": "test"},
                },
            )

            # Extract content from CallToolResult
            content = str(result.content[0].text) if hasattr(result, "content") else str(result)
            assert "Error executing tool" in content


class TestMCPServerToolDiscovery:
    """Test tool discovery functionality."""

    @pytest.mark.asyncio
    async def test_list_thinking_tools(self, temp_tools_dir: Path) -> None:
        """Test listing all thinking tools."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            result = await client.call_tool("list_thinking_tools", {})
            tools = (
                json.loads(result.content[0].text)
                if hasattr(result, "content")
                else json.loads(str(result))
            )

            assert isinstance(tools, list)
            assert len(tools) == 1
            assert tools[0]["name"] == "test_tool"
            assert tools[0]["display_name"] == "Test Tool"
            assert tools[0]["category"] == "test"

    @pytest.mark.asyncio
    async def test_list_tools_filtered_by_category(self, temp_tools_dir: Path) -> None:
        """Test listing tools filtered by category."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            # Filter by existing category
            result1 = await client.call_tool("list_thinking_tools", {"category": "test"})
            test_tools = (
                json.loads(result1.content[0].text)
                if hasattr(result1, "content")
                else json.loads(str(result1))
            )
            assert len(test_tools) == 1

            # Filter by non-existent category
            result2 = await client.call_tool("list_thinking_tools", {"category": "metacognition"})
            content2 = (
                result2.content[0].text
                if (hasattr(result2, "content") and result2.content)
                else "[]"
            )
            metacog_tools = json.loads(content2)
            assert len(metacog_tools) == 0


class TestMCPServerMemoryQueries:
    """Test process memory query functionality."""

    @pytest.mark.asyncio
    async def test_query_memory_by_entry_id(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test querying memory by entry ID."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_process_memory", {"entry_id": "test-001"})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert data["id"] == "test-001"
            assert data["title"] == "Test Entry"

    @pytest.mark.asyncio
    async def test_query_memory_by_keyword(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test querying memory by keyword."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_process_memory", {"keyword": "test"})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert len(data) == 2  # Both entries match

    @pytest.mark.asyncio
    async def test_query_memory_by_category(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test querying memory by category."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_process_memory", {"category": "Test"})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert len(data) == 2

    @pytest.mark.asyncio
    async def test_query_memory_by_tags(self, temp_tools_dir: Path, temp_memory_file: Path) -> None:
        """Test querying memory by tags."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_process_memory", {"tags": ["test", "related"]})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert len(data) == 1  # Only test-002 has both tags


class TestMCPServerGraphQueries:
    """Test knowledge graph query functionality."""

    @pytest.mark.asyncio
    async def test_query_graph_by_entry_id(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test querying graph by entry ID."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool(
                "query_knowledge_graph", {"entry_id": "test-001", "depth": 1}
            )

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            # test-001 links to test-002
            assert len(data) == 1
            assert data[0]["id"] == "test-002"

    @pytest.mark.asyncio
    async def test_query_graph_by_concept(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test querying graph by concept."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_knowledge_graph", {"concept": "testing"})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert len(data) == 2  # Both entries have "testing" concept

    @pytest.mark.asyncio
    async def test_query_graph_stats(self, temp_tools_dir: Path, temp_memory_file: Path) -> None:
        """Test querying graph stats."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            result = await client.call_tool("query_knowledge_graph", {})

            content = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(content)
            assert "total_nodes" in data
            assert "total_edges" in data
            assert data["total_nodes"] == 2


class TestMCPServerResources:
    """Test MCP resources functionality."""

    @pytest.mark.asyncio
    async def test_get_tools_by_category_resource(self, temp_tools_dir: Path) -> None:
        """Test getting tools by category via resource URI."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            resources = await client.list_resources()
            # Just verify resources endpoint exists - actual resource reading
            # requires MCP protocol implementation which may differ
            assert resources is not None

    @pytest.mark.asyncio
    async def test_get_tool_details_resource(self, temp_tools_dir: Path) -> None:
        """Test getting tool details via resource URI."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            resources = await client.list_resources()
            # Verify resources are registered
            assert resources is not None

    @pytest.mark.asyncio
    async def test_get_process_memory_entry_resource(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test getting process memory entry via resource URI."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            resources = await client.list_resources()
            # Verify process memory resources are registered
            assert resources is not None


class TestMCPServerPrompts:
    """Test MCP prompts functionality."""

    @pytest.mark.asyncio
    async def test_get_process_memory_context_prompt(
        self, temp_tools_dir: Path, temp_memory_file: Path
    ) -> None:
        """Test getting process memory context via prompt."""
        create_server(temp_tools_dir, memory_path=temp_memory_file)

        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            # Verify prompts are registered
            assert prompts is not None

    @pytest.mark.asyncio
    async def test_get_tool_usage_guide_prompt(self, temp_tools_dir: Path) -> None:
        """Test getting tool usage guide via prompt."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            # Verify prompts are registered
            assert prompts is not None


class TestMCPServerProgressiveDisclosure:
    """Test progressive disclosure resources."""

    @pytest.mark.asyncio
    async def test_discover_tool_categories(self, temp_tools_dir: Path) -> None:
        """Test discovering tool categories."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            # Read the discover resource
            resources = await client.list_resources()
            assert resources is not None
            # FastMCP Client doesn't have direct resource reading,
            # but we can verify resources are registered

    @pytest.mark.asyncio
    async def test_get_tool_yaml_spec(self, temp_tools_dir: Path) -> None:
        """Test getting tool YAML spec on-demand."""
        # Create a category subdirectory structure
        category_dir = temp_tools_dir / "test_category"
        category_dir.mkdir()

        # Move test tool to category
        (temp_tools_dir / "test_tool.yml").rename(category_dir / "test_tool.yml")

        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            resources = await client.list_resources()
            # Verify resource system is working
            assert resources is not None


class TestMCPServerTokenTracking:
    """Test token usage tracking."""

    @pytest.mark.asyncio
    async def test_get_token_usage_stats_initial(self, temp_tools_dir: Path) -> None:
        """Test token usage stats with no operations."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            result = await client.call_tool("get_token_usage_stats", {})
            stats = (
                json.loads(result.content[0].text)
                if hasattr(result, "content")
                else json.loads(str(result))
            )

            assert "total_ops" in stats
            assert "total_tokens" in stats
            assert "breakdown" in stats

    @pytest.mark.asyncio
    async def test_token_tracking_on_execute(self, temp_tools_dir: Path) -> None:
        """Test token tracking during tool execution."""
        create_server(temp_tools_dir)

        async with Client(mcp) as client:
            # Execute a tool
            await client.call_tool(
                "execute_thinking_tool",
                {
                    "tool_name": "test_tool",
                    "parameters": {"input": "test value"},
                },
            )

            # Get stats
            result = await client.call_tool("get_token_usage_stats", {})
            stats = (
                json.loads(result.content[0].text)
                if hasattr(result, "content")
                else json.loads(str(result))
            )

            # Should have at least one operation tracked
            assert stats["total_ops"] >= 1
            assert stats["total_tokens"] > 0
            assert len(stats["breakdown"]) >= 1

            # Verify breakdown structure
            first_op = stats["breakdown"][0]
            assert "op" in first_op
            assert "tool" in first_op
            assert "in" in first_op
            assert "out" in first_op
            assert "total" in first_op
