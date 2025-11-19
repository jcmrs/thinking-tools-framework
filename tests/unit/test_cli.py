"""Unit tests for CLI interface."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from cogito.ui.cli import cli


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_registry() -> Mock:
    """Create mock ToolRegistry."""
    registry = Mock()
    registry.discover_tools.return_value = 3
    registry.list_tools.return_value = ["tool1", "tool2", "tool3"]
    registry.get_tool.return_value = {
        "metadata": {
            "name": "test_tool",
            "display_name": "Test Tool",
            "description": "A test tool",
            "category": "testing",
            "author": "Test Author",
            "version": "1.0.0",
            "tags": ["test", "example"],
        },
        "parameters": {
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Input parameter",
                }
            },
            "required": ["input"],
        },
    }
    return registry


@pytest.fixture
def mock_executor() -> Mock:
    """Create mock ToolExecutor."""
    executor = Mock()
    executor.execute_by_name.return_value = "# Test Output\n\nTool executed successfully."
    return executor


@pytest.fixture
def mock_validator() -> Mock:
    """Create mock SchemaValidator."""
    validator = Mock()
    validator.validate_tool_spec.return_value = None
    return validator


@pytest.fixture
def mock_memory_store() -> Mock:
    """Create mock ProcessMemoryStore."""
    store = Mock()
    store.list_entries.return_value = [
        {
            "id": "PM-001",
            "title": "Test Entry",
            "type": "decision",
            "summary": "A test decision",
            "tags": ["test"],
        }
    ]
    store.search_entries.return_value = [
        {
            "id": "PM-002",
            "title": "Search Result",
            "type": "lesson",
            "summary": "A search result",
            "tags": ["search"],
        }
    ]
    store.get_entry.return_value = {
        "id": "PM-001",
        "title": "Specific Entry",
        "type": "decision",
        "summary": "A specific entry",
        "tags": ["specific"],
    }
    return store


class TestCLIList:
    """Test 'cogito list' command."""

    @patch("cogito.ui.cli.ToolRegistry")
    def test_list_text_output(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test list command with text output."""
        mock_registry_class.return_value.discover_tools.return_value = 2
        mock_registry_class.return_value.list_tools.return_value = ["tool1", "tool2"]
        mock_registry_class.return_value.get_tool.return_value = {
            "metadata": {
                "name": "tool1",
                "display_name": "Tool One",
                "description": "First tool",
                "category": "test",
                "tags": ["example"],
            }
        }

        result = cli_runner.invoke(cli, ["list", "--tools-dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "Tool One" in result.output
        assert "First tool" in result.output

    @patch("cogito.ui.cli.ToolRegistry")
    def test_list_json_output(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test list command with JSON output."""
        mock_registry_class.return_value.discover_tools.return_value = 1
        mock_registry_class.return_value.list_tools.return_value = ["tool1"]
        mock_registry_class.return_value.get_tool.return_value = {
            "metadata": {
                "name": "tool1",
                "display_name": "Tool One",
                "description": "First tool",
                "category": "test",
                "tags": ["example"],
            }
        }

        result = cli_runner.invoke(
            cli, ["list", "--tools-dir", str(tmp_path), "--output-format", "json"]
        )

        assert result.exit_code == 0
        tools = json.loads(result.output)
        assert isinstance(tools, list)
        assert len(tools) == 1
        assert tools[0]["name"] == "tool1"

    @patch("cogito.ui.cli.ToolRegistry")
    def test_list_with_category_filter(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test list command with category filter."""
        mock_registry_class.return_value.discover_tools.return_value = 2
        mock_registry_class.return_value.list_tools.return_value = ["tool1", "tool2"]

        def get_tool_side_effect(name: str) -> dict:
            if name == "tool1":
                return {
                    "metadata": {
                        "name": "tool1",
                        "display_name": "Tool One",
                        "description": "First tool",
                        "category": "metacognition",
                        "tags": [],
                    }
                }
            return {
                "metadata": {
                    "name": "tool2",
                    "display_name": "Tool Two",
                    "description": "Second tool",
                    "category": "review",
                    "tags": [],
                }
            }

        mock_registry_class.return_value.get_tool.side_effect = get_tool_side_effect

        result = cli_runner.invoke(
            cli, ["list", "--tools-dir", str(tmp_path), "--category", "metacognition"]
        )

        assert result.exit_code == 0
        assert "Tool One" in result.output
        assert "Tool Two" not in result.output

    @patch("cogito.ui.cli.ToolRegistry")
    def test_list_no_tools_found(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test list command when no tools are found."""
        mock_registry_class.return_value.discover_tools.return_value = 0

        result = cli_runner.invoke(cli, ["list", "--tools-dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "No tools found" in result.output


class TestCLIExecute:
    """Test 'cogito execute' command."""

    @patch("cogito.ui.cli.ToolExecutor")
    @patch("cogito.ui.cli.ToolRegistry")
    def test_execute_with_params(
        self,
        mock_registry_class: MagicMock,
        mock_executor_class: MagicMock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test execute command with parameters."""
        mock_registry_class.return_value.discover_tools.return_value = 1
        mock_executor_class.return_value.execute_by_name.return_value = "# Test Result\n\nSuccess"

        result = cli_runner.invoke(
            cli,
            [
                "execute",
                "test_tool",
                "--tools-dir",
                str(tmp_path),
                "-p",
                "context=Testing",
                "-p",
                "depth=standard",
            ],
        )

        assert result.exit_code == 0
        assert "Test Result" in result.output
        mock_executor_class.return_value.execute_by_name.assert_called_once()

    @patch("cogito.ui.cli.ToolRegistry")
    def test_execute_invalid_param_format(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test execute command with invalid parameter format."""
        result = cli_runner.invoke(
            cli,
            [
                "execute",
                "test_tool",
                "--tools-dir",
                str(tmp_path),
                "-p",
                "invalid_no_equals",
            ],
        )

        assert result.exit_code == 1  # Click.UsageError wrapped in try-except
        assert "Invalid parameter format" in result.output

    @patch("cogito.ui.cli.ToolExecutor")
    @patch("cogito.ui.cli.ToolRegistry")
    def test_execute_markdown_output(
        self,
        mock_registry_class: MagicMock,
        mock_executor_class: MagicMock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test execute command with markdown output format."""
        mock_executor_class.return_value.execute_by_name.return_value = "# Markdown\n\n**Bold**"

        result = cli_runner.invoke(
            cli,
            [
                "execute",
                "test_tool",
                "--tools-dir",
                str(tmp_path),
                "--output-format",
                "markdown",
            ],
        )

        assert result.exit_code == 0
        assert "# Markdown" in result.output


class TestCLIInfo:
    """Test 'cogito info' command."""

    @patch("cogito.ui.cli.ToolRegistry")
    def test_info_text_output(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test info command with text output."""
        mock_registry_class.return_value.discover_tools.return_value = 1
        mock_registry_class.return_value.get_tool.return_value = {
            "metadata": {
                "name": "test_tool",
                "display_name": "Test Tool",
                "description": "A test tool",
                "category": "testing",
                "author": "Test Author",
                "version": "1.0.0",
                "tags": ["test", "example"],
            },
            "parameters": {
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input parameter",
                    }
                },
                "required": ["input"],
            },
        }

        result = cli_runner.invoke(
            cli, ["info", "test_tool", "--tools-dir", str(tmp_path)]
        )

        assert result.exit_code == 0
        assert "Test Tool" in result.output
        assert "A test tool" in result.output
        assert "Test Author" in result.output
        assert "input (required)" in result.output

    @patch("cogito.ui.cli.ToolRegistry")
    def test_info_json_output(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test info command with JSON output."""
        tool_spec = {
            "metadata": {
                "name": "test_tool",
                "display_name": "Test Tool",
                "description": "A test tool",
                "category": "testing",
                "author": "Test Author",
                "version": "1.0.0",
                "tags": ["test"],
            },
            "parameters": {"properties": {}, "required": []},
        }
        mock_registry_class.return_value.discover_tools.return_value = 1
        mock_registry_class.return_value.get_tool.return_value = tool_spec

        result = cli_runner.invoke(
            cli,
            ["info", "test_tool", "--tools-dir", str(tmp_path), "--output-format", "json"],
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["metadata"]["name"] == "test_tool"

    @patch("cogito.ui.cli.ToolRegistry")
    def test_info_tool_not_found(
        self, mock_registry_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test info command when tool is not found."""
        mock_registry_class.return_value.discover_tools.return_value = 0
        mock_registry_class.return_value.get_tool.return_value = None

        result = cli_runner.invoke(
            cli, ["info", "nonexistent", "--tools-dir", str(tmp_path)]
        )

        assert result.exit_code == 1
        assert "not found" in result.output


class TestCLIValidate:
    """Test 'cogito validate' command."""

    @patch("cogito.ui.cli.SchemaValidator")
    @patch("builtins.open", create=True)
    @patch("yaml.safe_load")
    def test_validate_success(
        self,
        mock_yaml_load: MagicMock,
        mock_open: MagicMock,
        mock_validator_class: MagicMock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test validate command with valid tool."""
        test_file = tmp_path / "test_tool.yml"
        test_file.write_text("metadata:\n  name: test")

        mock_yaml_load.return_value = {"metadata": {"name": "test"}}
        mock_validator_class.return_value.validate_tool_spec.return_value = None

        result = cli_runner.invoke(cli, ["validate", str(test_file)])

        assert result.exit_code == 0
        assert "is valid" in result.output

    @patch("cogito.ui.cli.SchemaValidator")
    @patch("builtins.open", create=True)
    @patch("yaml.safe_load")
    def test_validate_failure(
        self,
        mock_yaml_load: MagicMock,
        mock_open: MagicMock,
        mock_validator_class: MagicMock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test validate command with invalid tool."""
        test_file = tmp_path / "invalid_tool.yml"
        test_file.write_text("invalid: yaml")

        mock_yaml_load.return_value = {"invalid": "yaml"}
        mock_validator_class.return_value.validate_tool_spec.side_effect = Exception(
            "Schema validation failed"
        )

        result = cli_runner.invoke(cli, ["validate", str(test_file)])

        assert result.exit_code == 1
        assert "Validation failed" in result.output


class TestCLIMemory:
    """Test 'cogito memory' command."""

    @patch("cogito.ui.cli.ProcessMemoryStore")
    def test_memory_list_all(
        self, mock_store_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test memory command listing all entries."""
        memory_file = tmp_path / "process_memory.jsonl"
        memory_file.write_text("")

        mock_store_class.return_value.list_entries.return_value = [
            {
                "id": "PM-001",
                "title": "Test Entry",
                "type": "decision",
                "summary": "A test decision",
                "tags": ["test"],
            }
        ]

        result = cli_runner.invoke(cli, ["memory", "--memory-file", str(memory_file)])

        if result.exit_code != 0:
            print(f"\nCLI Output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert "PM-001" in result.output
        assert "Test Entry" in result.output

    @patch("cogito.ui.cli.ProcessMemoryStore")
    def test_memory_search(
        self, mock_store_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test memory command with search."""
        memory_file = tmp_path / "process_memory.jsonl"
        memory_file.write_text("")

        mock_store_class.return_value.search_entries.return_value = [
            {
                "id": "PM-002",
                "title": "Search Result",
                "type": "lesson",
                "summary": "Found via search",
                "tags": [],
            }
        ]

        result = cli_runner.invoke(
            cli, ["memory", "--memory-file", str(memory_file), "--search", "validation"]
        )

        assert result.exit_code == 0
        assert "PM-002" in result.output

    @patch("cogito.ui.cli.ProcessMemoryStore")
    def test_memory_json_output(
        self, mock_store_class: MagicMock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test memory command with JSON output."""
        memory_file = tmp_path / "process_memory.jsonl"
        memory_file.write_text("")

        entries = [
            {
                "id": "PM-001",
                "title": "Test",
                "type": "decision",
                "summary": "Test entry",
                "tags": [],
            }
        ]
        mock_store_class.return_value.list_entries.return_value = entries

        result = cli_runner.invoke(
            cli,
            ["memory", "--memory-file", str(memory_file), "--output-format", "json"],
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert len(output) == 1
        assert output[0]["id"] == "PM-001"


class TestCLIServe:
    """Test 'cogito serve' command."""

    @patch("cogito.integration.mcp_server.mcp")
    @patch("cogito.integration.mcp_server.create_server")
    def test_serve_default_paths(
        self,
        mock_create_server: MagicMock,
        mock_mcp: MagicMock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test serve command with default paths."""
        # Mock mcp.run() to not actually start the server
        mock_mcp.run.side_effect = KeyboardInterrupt()

        result = cli_runner.invoke(cli, ["serve", "--tools-dir", str(tmp_path)])

        # Should exit with 1 due to KeyboardInterrupt, but that's expected
        mock_create_server.assert_called_once()
        assert "Starting MCP server" in result.output


class TestCLIDebugMode:
    """Test CLI debug mode."""

    def test_debug_flag(self, cli_runner: CliRunner) -> None:
        """Test --debug flag is accepted."""
        result = cli_runner.invoke(cli, ["--debug", "--help"])
        assert result.exit_code == 0


class TestCLIVersion:
    """Test CLI version display."""

    def test_version_option(self, cli_runner: CliRunner) -> None:
        """Test --version option."""
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
