"""Unit tests for ToolRegistry class.

Tests auto-discovery, caching, category organization, and hot-reload.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml

from cogito.orchestration.registry import (
    ToolDiscoveryError,
    ToolLoadError,
    ToolRegistry,
)


@pytest.fixture
def minimal_tool_spec() -> dict[str, Any]:
    """Minimal valid tool spec for testing."""
    return {
        "metadata": {
            "name": "test_tool",
            "display_name": "Test Tool",
            "description": "A test tool",
            "category": "test",
            "version": "1.0.0",
        },
        "template": {"source": "Test template"},
    }


@pytest.fixture
def tool_with_category() -> dict[str, Any]:
    """Tool spec with specific category."""
    return {
        "metadata": {
            "name": "categorized_tool",
            "display_name": "Categorized Tool",
            "description": "Tool with category",
            "category": "metacognition",
            "version": "1.0.0",
        },
        "template": {"source": "Categorized template"},
    }


@pytest.fixture
def temp_tool_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test tools."""
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    return tool_dir


class TestToolRegistryInit:
    """Test ToolRegistry initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        registry = ToolRegistry()
        assert registry._tool_dirs == []
        assert registry._enable_validation is True
        assert registry._validator is not None
        assert registry._tools == {}
        assert registry._tool_paths == {}
        assert registry._categories == {}

    def test_init_with_custom_dirs(self) -> None:
        """Test initialization with custom tool directories."""
        dirs = [Path("/path/to/tools"), Path("/another/path")]
        registry = ToolRegistry(tool_dirs=dirs)
        assert registry._tool_dirs == dirs

    def test_init_with_validation_disabled(self) -> None:
        """Test initialization with validation disabled."""
        registry = ToolRegistry(enable_validation=False)
        assert registry._enable_validation is False
        assert registry._validator is None


class TestToolRegistryLoadTool:
    """Test tool loading functionality."""

    def test_load_valid_tool(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test loading a valid tool from YAML file."""
        tool_file = temp_tool_dir / "test_tool.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        loaded_spec = registry.load_tool(tool_file)

        assert loaded_spec == minimal_tool_spec
        assert registry.get_tool("test_tool") == minimal_tool_spec
        assert registry._tool_paths["test_tool"] == tool_file

    def test_load_tool_updates_category_index(
        self, temp_tool_dir: Path, tool_with_category: dict[str, Any]
    ) -> None:
        """Test that loading a tool updates category index."""
        tool_file = temp_tool_dir / "categorized.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(tool_with_category, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        assert "metacognition" in registry._categories
        assert "categorized_tool" in registry._categories["metacognition"]

    def test_load_tool_with_missing_metadata(self, temp_tool_dir: Path) -> None:
        """Test loading tool without metadata raises error."""
        invalid_spec = {"template": {"source": "Test"}}
        tool_file = temp_tool_dir / "invalid.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(invalid_spec, f)

        registry = ToolRegistry(enable_validation=False)
        with pytest.raises(ToolLoadError) as exc_info:
            registry.load_tool(tool_file)

        assert "missing metadata.name field" in str(exc_info.value).lower()
        assert exc_info.value.tool_path == str(tool_file)

    def test_load_tool_with_missing_name(self, temp_tool_dir: Path) -> None:
        """Test loading tool without name raises error."""
        invalid_spec = {
            "metadata": {"description": "No name"},
            "template": {"source": "Test"},
        }
        tool_file = temp_tool_dir / "invalid.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(invalid_spec, f)

        registry = ToolRegistry(enable_validation=False)
        with pytest.raises(ToolLoadError) as exc_info:
            registry.load_tool(tool_file)

        assert "missing metadata.name field" in str(exc_info.value).lower()

    def test_load_tool_with_invalid_yaml(self, temp_tool_dir: Path) -> None:
        """Test loading tool with invalid YAML raises error."""
        tool_file = temp_tool_dir / "invalid.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: syntax: error:")

        registry = ToolRegistry(enable_validation=False)
        with pytest.raises(ToolLoadError) as exc_info:
            registry.load_tool(tool_file)

        assert "failed to load tool" in str(exc_info.value).lower()
        assert exc_info.value.tool_path == str(tool_file)

    def test_load_tool_with_validation_failure(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test loading tool that fails validation raises error."""
        tool_file = temp_tool_dir / "invalid_tool.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=True)

        # Mock validator to return validation failure
        registry._validator = MagicMock()
        registry._validator.validate_tool_spec.return_value = {
            "valid": False,
            "errors": ["Schema validation failed"],
        }

        with pytest.raises(ToolLoadError) as exc_info:
            registry.load_tool(tool_file)

        assert "validation failed" in str(exc_info.value).lower()

    def test_load_tool_with_uncategorized_default(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that tools without category get 'uncategorized' default."""
        spec_no_category = minimal_tool_spec.copy()
        spec_no_category["metadata"] = spec_no_category["metadata"].copy()
        del spec_no_category["metadata"]["category"]

        tool_file = temp_tool_dir / "uncategorized.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(spec_no_category, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        assert "uncategorized" in registry._categories
        assert "test_tool" in registry._categories["uncategorized"]


class TestToolRegistryDiscoverTools:
    """Test auto-discovery functionality."""

    def test_discover_tools_no_dirs_raises_error(self) -> None:
        """Test discovery with no configured directories raises error."""
        registry = ToolRegistry(tool_dirs=[])
        with pytest.raises(ToolDiscoveryError) as exc_info:
            registry.discover_tools()

        assert "no directories configured" in str(exc_info.value).lower()

    def test_discover_tools_with_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test discovery skips nonexistent directories."""
        nonexistent = tmp_path / "does_not_exist"
        registry = ToolRegistry(tool_dirs=[nonexistent])
        count = registry.discover_tools()

        assert count == 0

    def test_discover_tools_finds_yml_files(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test discovery finds .yml files."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        count = registry.discover_tools()

        assert count == 1
        assert "test_tool" in registry.list_tools()

    def test_discover_tools_finds_yaml_files(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test discovery finds .yaml files."""
        tool_file = temp_tool_dir / "test.yaml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        count = registry.discover_tools()

        assert count == 1
        assert "test_tool" in registry.list_tools()

    def test_discover_tools_recursive(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test discovery scans subdirectories recursively."""
        subdir = temp_tool_dir / "category" / "subcategory"
        subdir.mkdir(parents=True)

        tool_file = subdir / "nested.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        count = registry.discover_tools()

        assert count == 1
        assert "test_tool" in registry.list_tools()

    def test_discover_tools_skips_invalid_tools(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test discovery skips invalid tools and continues."""
        # Create one valid and one invalid tool
        valid_file = temp_tool_dir / "valid.yml"
        with open(valid_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        invalid_file = temp_tool_dir / "invalid.yml"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: syntax:")

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        count = registry.discover_tools()

        assert count == 1
        assert "test_tool" in registry.list_tools()

    def test_discover_tools_with_multiple_dirs(
        self, tmp_path: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test discovery scans multiple directories."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        spec1 = minimal_tool_spec.copy()
        spec1["metadata"] = spec1["metadata"].copy()
        spec1["metadata"]["name"] = "tool1"

        spec2 = minimal_tool_spec.copy()
        spec2["metadata"] = spec2["metadata"].copy()
        spec2["metadata"]["name"] = "tool2"

        with open(dir1 / "tool1.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec1, f)
        with open(dir2 / "tool2.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec2, f)

        registry = ToolRegistry(tool_dirs=[dir1, dir2], enable_validation=False)
        count = registry.discover_tools()

        assert count == 2
        assert "tool1" in registry.list_tools()
        assert "tool2" in registry.list_tools()


class TestToolRegistryGetMethods:
    """Test registry query methods."""

    def test_get_tool_existing(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test getting an existing tool."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        assert registry.get_tool("test_tool") == minimal_tool_spec

    def test_get_tool_nonexistent(self) -> None:
        """Test getting a nonexistent tool returns None."""
        registry = ToolRegistry(enable_validation=False)
        assert registry.get_tool("does_not_exist") is None

    def test_list_tools(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test listing all tool names."""
        spec1 = minimal_tool_spec.copy()
        spec1["metadata"] = spec1["metadata"].copy()
        spec1["metadata"]["name"] = "tool1"

        spec2 = minimal_tool_spec.copy()
        spec2["metadata"] = spec2["metadata"].copy()
        spec2["metadata"]["name"] = "tool2"

        with open(temp_tool_dir / "tool1.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec1, f)
        with open(temp_tool_dir / "tool2.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec2, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        registry.discover_tools()

        tools = registry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert len(tools) == 2

    def test_list_categories(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test listing all categories."""
        spec1 = minimal_tool_spec.copy()
        spec1["metadata"] = spec1["metadata"].copy()
        spec1["metadata"]["name"] = "tool1"
        spec1["metadata"]["category"] = "metacognition"

        spec2 = minimal_tool_spec.copy()
        spec2["metadata"] = spec2["metadata"].copy()
        spec2["metadata"]["name"] = "tool2"
        spec2["metadata"]["category"] = "review"

        with open(temp_tool_dir / "tool1.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec1, f)
        with open(temp_tool_dir / "tool2.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec2, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        registry.discover_tools()

        categories = registry.list_categories()
        assert "metacognition" in categories
        assert "review" in categories
        assert len(categories) == 2

    def test_get_tools_by_category(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test getting tools filtered by category."""
        spec1 = minimal_tool_spec.copy()
        spec1["metadata"] = spec1["metadata"].copy()
        spec1["metadata"]["name"] = "meta_tool"
        spec1["metadata"]["category"] = "metacognition"

        spec2 = minimal_tool_spec.copy()
        spec2["metadata"] = spec2["metadata"].copy()
        spec2["metadata"]["name"] = "review_tool"
        spec2["metadata"]["category"] = "review"

        with open(temp_tool_dir / "tool1.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec1, f)
        with open(temp_tool_dir / "tool2.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec2, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        registry.discover_tools()

        meta_tools = registry.get_tools_by_category("metacognition")
        assert "meta_tool" in meta_tools
        assert "review_tool" not in meta_tools

    def test_get_tools_by_nonexistent_category(self) -> None:
        """Test getting tools for nonexistent category returns empty list."""
        registry = ToolRegistry(enable_validation=False)
        tools = registry.get_tools_by_category("nonexistent")
        assert tools == []

    def test_get_tool_count(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test getting total number of tools."""
        spec1 = minimal_tool_spec.copy()
        spec1["metadata"] = spec1["metadata"].copy()
        spec1["metadata"]["name"] = "tool1"

        spec2 = minimal_tool_spec.copy()
        spec2["metadata"] = spec2["metadata"].copy()
        spec2["metadata"]["name"] = "tool2"

        with open(temp_tool_dir / "tool1.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec1, f)
        with open(temp_tool_dir / "tool2.yml", "w", encoding="utf-8") as f:
            yaml.dump(spec2, f)

        registry = ToolRegistry(tool_dirs=[temp_tool_dir], enable_validation=False)
        assert registry.get_tool_count() == 0

        registry.discover_tools()
        assert registry.get_tool_count() == 2

    def test_get_tool_path(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test getting file path for a tool."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        assert registry.get_tool_path("test_tool") == tool_file

    def test_get_tool_path_nonexistent(self) -> None:
        """Test getting path for nonexistent tool returns None."""
        registry = ToolRegistry(enable_validation=False)
        assert registry.get_tool_path("does_not_exist") is None


class TestToolRegistryHotReload:
    """Test hot-reload functionality (PM-004)."""

    def test_reload_tool_success(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test successful tool reload with validation."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        # Modify the tool file
        updated_spec = minimal_tool_spec.copy()
        updated_spec["metadata"] = updated_spec["metadata"].copy()
        updated_spec["metadata"]["version"] = "2.0.0"

        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(updated_spec, f)

        # Reload the tool
        reloaded = registry.reload_tool("test_tool")

        assert reloaded["metadata"]["version"] == "2.0.0"
        assert registry.get_tool("test_tool")["metadata"]["version"] == "2.0.0"

    def test_reload_tool_not_found(self) -> None:
        """Test reloading nonexistent tool raises error."""
        registry = ToolRegistry(enable_validation=False)
        with pytest.raises(ToolLoadError) as exc_info:
            registry.reload_tool("does_not_exist")

        assert "not found in registry" in str(exc_info.value).lower()

    def test_reload_tool_validation_failure_preserves_old_spec(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that failed reload preserves old spec (atomic swap)."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=True)
        registry.load_tool(tool_file)

        original_version = minimal_tool_spec["metadata"]["version"]

        # Write invalid spec to file
        with open(tool_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: syntax:")

        # Mock validator to simulate validation failure
        registry._validator = MagicMock()

        # Reload should fail but preserve old spec
        with pytest.raises(ToolLoadError):
            registry.reload_tool("test_tool")

        # Verify old spec is still in cache
        cached_spec = registry.get_tool("test_tool")
        assert cached_spec is not None
        assert cached_spec["metadata"]["version"] == original_version

    def test_reload_tool_with_validation_enabled(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test reload with validation enabled."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=True)

        # Mock validator for initial load
        registry._validator = MagicMock()
        registry._validator.validate_tool_spec.return_value = {
            "valid": True,
            "errors": [],
        }
        registry.load_tool(tool_file)

        # Update file
        updated_spec = minimal_tool_spec.copy()
        updated_spec["metadata"] = updated_spec["metadata"].copy()
        updated_spec["metadata"]["version"] = "2.0.0"

        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(updated_spec, f)

        # Reload with validation passing
        registry._validator.validate_tool_spec.return_value = {
            "valid": True,
            "errors": [],
        }
        reloaded = registry.reload_tool("test_tool")

        assert reloaded["metadata"]["version"] == "2.0.0"


class TestToolRegistryCacheMethods:
    """Test cache management methods."""

    def test_clear_cache(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test clearing all cached tools."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)

        assert registry.get_tool_count() > 0
        assert len(registry.list_tools()) > 0

        registry.clear_cache()

        assert registry.get_tool_count() == 0
        assert len(registry.list_tools()) == 0
        assert len(registry.list_categories()) == 0

    def test_cache_prevents_duplicate_category_entries(
        self, temp_tool_dir: Path, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that loading same tool twice doesn't duplicate category entries."""
        tool_file = temp_tool_dir / "test.yml"
        with open(tool_file, "w", encoding="utf-8") as f:
            yaml.dump(minimal_tool_spec, f)

        registry = ToolRegistry(enable_validation=False)
        registry.load_tool(tool_file)
        registry.load_tool(tool_file)  # Load again

        category = minimal_tool_spec["metadata"]["category"]
        tools_in_category = registry.get_tools_by_category(category)

        # Should only appear once even though loaded twice
        assert tools_in_category.count("test_tool") == 1
