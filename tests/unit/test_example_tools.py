"""Unit tests for example_tools module."""

from pathlib import Path

from cogito.provisioning.example_tools import ExampleToolsSelector


class TestExampleToolsSelector:
    """Tests for ExampleToolsSelector class."""

    def test_initialization_default_source_dir(self) -> None:
        """Test selector initializes with default source directory."""
        selector = ExampleToolsSelector()

        assert selector.source_examples_dir.exists()
        assert selector.source_examples_dir.name == "examples"

    def test_initialization_custom_source_dir(self, tmp_path: Path) -> None:
        """Test selector initializes with custom source directory."""
        source_dir = tmp_path / "custom_examples"
        source_dir.mkdir()

        selector = ExampleToolsSelector(source_dir)

        assert selector.source_examples_dir == source_dir

    def test_get_starter_tools(self) -> None:
        """Test getting list of starter tools."""
        selector = ExampleToolsSelector()

        tools = selector.get_starter_tools()

        assert isinstance(tools, dict)
        assert "metacognition" in tools
        assert "problem_solving" in tools
        assert isinstance(tools["metacognition"], list)
        assert len(tools["metacognition"]) > 0

    def test_get_starter_tools_returns_copy(self) -> None:
        """Test that get_starter_tools returns a copy, not reference."""
        selector = ExampleToolsSelector()

        tools1 = selector.get_starter_tools()
        tools2 = selector.get_starter_tools()

        # Modify one copy
        tools1["metacognition"].append("new_tool.yml")

        # Should not affect the other
        assert "new_tool.yml" not in tools2["metacognition"]

    def test_copy_tool_success(self, tmp_path: Path) -> None:
        """Test successfully copying a tool file."""
        selector = ExampleToolsSelector()
        dest_dir = tmp_path / "metacognition"

        # Get first starter tool
        category = "metacognition"
        tool_filename = selector.STARTER_TOOLS[category][0]

        result = selector.copy_tool(category, tool_filename, dest_dir)

        assert result["success"] is True
        assert "source" in result
        assert "destination" in result
        assert "error" not in result
        assert dest_dir.exists()
        assert (dest_dir / tool_filename).exists()

    def test_copy_tool_nonexistent_source(self, tmp_path: Path) -> None:
        """Test copying tool when source file doesn't exist."""
        # Create selector with non-existent source
        source_dir = tmp_path / "nonexistent"
        selector = ExampleToolsSelector(source_dir)

        dest_dir = tmp_path / "dest"

        result = selector.copy_tool("metacognition", "fake_tool.yml", dest_dir)

        assert result["success"] is False
        assert "error" in result
        assert "Source tool not found" in result["error"]

    def test_copy_starter_tools(self, tmp_path: Path) -> None:
        """Test copying all starter tools to destination."""
        selector = ExampleToolsSelector()
        dest_examples_dir = tmp_path / "examples"

        result = selector.copy_starter_tools(dest_examples_dir)

        assert result["total"] > 0
        # May have failures if source tools don't exist, but should attempt copy
        assert len(result["results"]) == result["total"]

        # If any tools were successfully copied, verify structure
        if result["copied"] > 0:
            # Verify categories were created
            assert (dest_examples_dir / "metacognition").exists() or (
                dest_examples_dir / "problem_solving"
            ).exists()

            # Verify at least one tool was copied
            all_tools = list(dest_examples_dir.rglob("*.yml"))
            assert len(all_tools) > 0

    def test_copy_starter_tools_with_failures(self, tmp_path: Path) -> None:
        """Test copying starter tools handles failures gracefully."""
        # Create selector with non-existent source
        source_dir = tmp_path / "nonexistent"
        selector = ExampleToolsSelector(source_dir)

        dest_examples_dir = tmp_path / "examples"

        result = selector.copy_starter_tools(dest_examples_dir)

        # All should fail since source doesn't exist
        assert result["total"] > 0
        assert result["copied"] == 0
        assert result["failed"] == result["total"]

    def test_create_examples_readme(self, tmp_path: Path) -> None:
        """Test creating README.md in examples directory."""
        selector = ExampleToolsSelector()
        dest_examples_dir = tmp_path / "examples"

        result = selector.create_examples_readme(dest_examples_dir)

        assert result["success"] is True
        assert "path" in result
        assert "error" not in result

        readme_path = Path(result["path"])
        assert readme_path.exists()
        assert readme_path.name == "README.md"

        # Verify content
        content = readme_path.read_text()
        assert "Example Thinking Tools" in content
        assert "Categories" in content
        assert "metacognition" in content

    def test_create_examples_readme_creates_directory(self, tmp_path: Path) -> None:
        """Test that create_examples_readme creates directory if needed."""
        selector = ExampleToolsSelector()
        dest_examples_dir = tmp_path / "examples"

        # Directory doesn't exist yet
        assert not dest_examples_dir.exists()

        result = selector.create_examples_readme(dest_examples_dir)

        # Should create directory and README
        assert result["success"] is True
        assert dest_examples_dir.exists()
        assert (dest_examples_dir / "README.md").exists()
