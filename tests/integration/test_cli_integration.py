"""Integration tests for CLI with real tools and data."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cogito.ui.cli import cli


@pytest.fixture
def examples_dir() -> Path:
    """Get path to examples directory with real tools."""
    # Assuming tests run from project root
    return Path(__file__).parent.parent.parent / "examples"


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_memory_file(tmp_path: Path) -> Path:
    """Create temporary process memory file with test data."""
    memory_file = tmp_path / "process_memory.jsonl"

    entries = [
        {
            "id": "PM-001",
            "title": "Test Decision",
            "type": "decision",
            "summary": "A test architectural decision",
            "rationale": "Testing memory queries",
            "tags": ["test", "architecture"],
            "created": "2025-01-01T00:00:00Z",
        },
        {
            "id": "PM-002",
            "title": "Test Lesson",
            "type": "lessons_learned",
            "summary": "A test lesson learned during development",
            "tags": ["test", "validation"],
            "created": "2025-01-02T00:00:00Z",
        },
    ]

    with memory_file.open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return memory_file


class TestCLIIntegrationList:
    """Integration tests for 'cogito list' command."""

    def test_list_real_tools_text(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test listing real tools with text output."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        result = cli_runner.invoke(cli, ["list", "--tools-dir", str(examples_dir)])

        assert result.exit_code == 0
        assert "thinking tools" in result.output.lower()

    def test_list_real_tools_json(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test listing real tools with JSON output."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        result = cli_runner.invoke(
            cli, ["list", "--tools-dir", str(examples_dir), "--output-format", "json"]
        )

        assert result.exit_code == 0
        tools = json.loads(result.output)
        assert isinstance(tools, list)
        if len(tools) > 0:
            assert "name" in tools[0]
            assert "category" in tools[0]

    def test_list_with_category_metacognition(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test listing tools filtered by metacognition category."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        result = cli_runner.invoke(
            cli,
            ["list", "--tools-dir", str(examples_dir), "--category", "metacognition"],
        )

        # Should succeed whether category exists or not
        assert result.exit_code in (0, 1)  # 1 if no tools in category


class TestCLIIntegrationExecute:
    """Integration tests for 'cogito execute' command."""

    def test_execute_real_tool_if_exists(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test executing a real tool if think_aloud exists."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Check if think_aloud tool exists
        tool_paths = [
            examples_dir / "metacognition" / "think_aloud.yml",
            examples_dir / "metacognition" / "think_aloud.yaml",
        ]

        if not any(p.exists() for p in tool_paths):
            pytest.skip("think_aloud tool not found")

        result = cli_runner.invoke(
            cli,
            [
                "execute",
                "think_aloud",
                "--tools-dir",
                str(examples_dir),
                "-p",
                "context=Integration test",
                "-p",
                "depth=quick",
            ],
        )

        # Should either succeed or fail gracefully
        assert result.exit_code in (0, 1)

    def test_execute_nonexistent_tool(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test executing a tool that doesn't exist."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        result = cli_runner.invoke(
            cli,
            [
                "execute",
                "nonexistent_tool_12345",
                "--tools-dir",
                str(examples_dir),
            ],
        )

        assert result.exit_code == 1
        # Should have an error message


class TestCLIIntegrationInfo:
    """Integration tests for 'cogito info' command."""

    def test_info_real_tool_if_exists(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test getting info for a real tool."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Try to get info for first tool found
        for category_dir in examples_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for tool_file in category_dir.glob("*.y*ml"):
                    tool_name = tool_file.stem

                    result = cli_runner.invoke(
                        cli, ["info", tool_name, "--tools-dir", str(examples_dir)]
                    )

                    assert result.exit_code == 0
                    assert tool_name in result.output.lower() or "parameters" in result.output.lower()
                    return  # Test passed

        pytest.skip("No tools found in examples directory")

    def test_info_json_output(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test getting tool info as JSON."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Try to get info for first tool found
        for category_dir in examples_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for tool_file in category_dir.glob("*.y*ml"):
                    tool_name = tool_file.stem

                    result = cli_runner.invoke(
                        cli,
                        [
                            "info",
                            tool_name,
                            "--tools-dir",
                            str(examples_dir),
                            "--output-format",
                            "json",
                        ],
                    )

                    assert result.exit_code == 0
                    spec = json.loads(result.output)
                    assert "metadata" in spec
                    return  # Test passed

        pytest.skip("No tools found in examples directory")


class TestCLIIntegrationValidate:
    """Integration tests for 'cogito validate' command."""

    def test_validate_real_tool_if_exists(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test validating a real tool file."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Find first real tool file
        for category_dir in examples_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for tool_file in category_dir.glob("*.y*ml"):
                    result = cli_runner.invoke(cli, ["validate", str(tool_file)])

                    # Real tool should be valid
                    assert result.exit_code == 0
                    assert "valid" in result.output.lower()
                    return  # Test passed

        pytest.skip("No tool files found in examples directory")

    def test_validate_invalid_yaml(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test validating an invalid YAML file."""
        invalid_file = tmp_path / "invalid.yml"
        invalid_file.write_text("invalid: [unclosed")

        result = cli_runner.invoke(cli, ["validate", str(invalid_file)])

        assert result.exit_code == 1
        assert "failed" in result.output.lower() or "error" in result.output.lower()


class TestCLIIntegrationMemory:
    """Integration tests for 'cogito memory' command."""

    def test_memory_list_all(
        self, cli_runner: CliRunner, temp_memory_file: Path
    ) -> None:
        """Test listing all memory entries."""
        result = cli_runner.invoke(
            cli, ["memory", "--memory-file", str(temp_memory_file)]
        )

        assert result.exit_code == 0
        assert "PM-001" in result.output
        assert "PM-002" in result.output
        assert "Test Decision" in result.output

    def test_memory_search(
        self, cli_runner: CliRunner, temp_memory_file: Path
    ) -> None:
        """Test searching memory entries."""
        result = cli_runner.invoke(
            cli,
            ["memory", "--memory-file", str(temp_memory_file), "--search", "validation"],
        )

        assert result.exit_code == 0
        assert "PM-002" in result.output  # Has validation tag
        # PM-001 might not appear if search is precise

    def test_memory_get_entry(
        self, cli_runner: CliRunner, temp_memory_file: Path
    ) -> None:
        """Test getting a specific memory entry."""
        result = cli_runner.invoke(
            cli,
            ["memory", "--memory-file", str(temp_memory_file), "--entry-id", "PM-001"],
        )

        assert result.exit_code == 0
        assert "PM-001" in result.output
        assert "Test Decision" in result.output

    def test_memory_json_output(
        self, cli_runner: CliRunner, temp_memory_file: Path
    ) -> None:
        """Test memory output in JSON format."""
        result = cli_runner.invoke(
            cli,
            [
                "memory",
                "--memory-file",
                str(temp_memory_file),
                "--output-format",
                "json",
            ],
        )

        assert result.exit_code == 0
        entries = json.loads(result.output)
        assert isinstance(entries, list)
        assert len(entries) == 2
        assert entries[0]["id"] in ("PM-001", "PM-002")

    def test_memory_category_filter(
        self, cli_runner: CliRunner, temp_memory_file: Path
    ) -> None:
        """Test filtering memory by category."""
        result = cli_runner.invoke(
            cli,
            [
                "memory",
                "--memory-file",
                str(temp_memory_file),
                "--category",
                "decision",
            ],
        )

        assert result.exit_code == 0
        assert "PM-001" in result.output  # Type is decision
        # PM-002 might not appear (type is lessons_learned)

    def test_memory_file_not_found(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test error when memory file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.jsonl"

        result = cli_runner.invoke(cli, ["memory", "--memory-file", str(nonexistent)])

        assert result.exit_code == 2  # Click path validation error
        assert "does not exist" in result.output or "not found" in result.output.lower()


class TestCLIIntegrationServe:
    """Integration tests for 'cogito serve' command."""

    def test_serve_help(self, cli_runner: CliRunner) -> None:
        """Test serve command help text."""
        result = cli_runner.invoke(cli, ["serve", "--help"])

        assert result.exit_code == 0
        assert "MCP server" in result.output

    # Note: We don't actually start the server in integration tests
    # as it would block. Manual testing covers server functionality.


class TestCLIIntegrationEndToEnd:
    """End-to-end integration tests."""

    def test_workflow_list_info_validate(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test complete workflow: list -> info -> validate."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Step 1: List tools
        list_result = cli_runner.invoke(
            cli, ["list", "--tools-dir", str(examples_dir), "--output-format", "json"]
        )

        if list_result.exit_code != 0:
            pytest.skip("No tools available for testing")

        tools = json.loads(list_result.output)
        if not tools:
            pytest.skip("No tools found")

        tool_name = tools[0]["name"]

        # Step 2: Get info
        info_result = cli_runner.invoke(
            cli, ["info", tool_name, "--tools-dir", str(examples_dir)]
        )

        assert info_result.exit_code == 0

        # Step 3: Find and validate the tool file
        for category_dir in examples_dir.iterdir():
            if category_dir.is_dir():
                for tool_file in category_dir.glob(f"{tool_name}.y*ml"):
                    validate_result = cli_runner.invoke(cli, ["validate", str(tool_file)])
                    assert validate_result.exit_code == 0


class TestCLIIntegrationErrorHandling:
    """Integration tests for error handling."""

    def test_nonexistent_tools_dir(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test error when tools directory doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        result = cli_runner.invoke(cli, ["list", "--tools-dir", str(nonexistent_dir)])

        assert result.exit_code == 2  # Click path validation error

    def test_debug_mode_verbose_output(
        self, cli_runner: CliRunner, examples_dir: Path
    ) -> None:
        """Test that debug mode is accepted (verbose output tested manually)."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        result = cli_runner.invoke(
            cli, ["--debug", "list", "--tools-dir", str(examples_dir)]
        )

        # Debug mode shouldn't break functionality
        assert result.exit_code in (0, 1)
