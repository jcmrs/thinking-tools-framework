"""Tool registry with auto-discovery, caching, and hot-reload support.

Implements PM-004 (Hot-Reload Capability) for developer experience.
"""

from pathlib import Path
from typing import Any

import yaml

from cogito.processing.validator import SchemaValidator


class ToolDiscoveryError(Exception):
    """Raised when tool discovery fails."""

    pass


class ToolLoadError(Exception):
    """Raised when loading a specific tool fails."""

    def __init__(self, message: str, tool_path: str | None = None) -> None:
        """Initialize tool load error with context.

        Args:
            message: Human-readable error message
            tool_path: Path to the tool that failed to load
        """
        self.tool_path = tool_path
        super().__init__(message)


class ToolRegistry:
    """Registry for discovering, loading, and caching thinking tools.

    Implements PM-004 (Hot-Reload Capability) with:
    - Auto-discovery via file system scan
    - Tool caching for performance
    - Category-based organization
    - Hot-reload support (validation + atomic swap)

    Tools are discovered by scanning directories for YAML files matching
    the thinking tool schema.
    """

    def __init__(
        self,
        tool_dirs: list[Path] | None = None,
        enable_validation: bool = True,
    ) -> None:
        """Initialize tool registry.

        Args:
            tool_dirs: Directories to scan for tools. If None, uses default.
            enable_validation: Whether to validate tools during discovery.
        """
        self._tool_dirs = tool_dirs or []
        self._enable_validation = enable_validation
        self._validator = SchemaValidator() if enable_validation else None

        # Cache: tool_name -> tool_spec
        self._tools: dict[str, dict[str, Any]] = {}

        # Metadata: tool_name -> file_path
        self._tool_paths: dict[str, Path] = {}

        # Category index: category -> list[tool_name]
        self._categories: dict[str, list[str]] = {}

    def discover_tools(self, scan_dirs: list[Path] | None = None) -> int:
        """Discover and load all tools from configured directories.

        Scans directories recursively for YAML files, validates them as
        thinking tools, and adds valid tools to the registry.

        Args:
            scan_dirs: Directories to scan. If None, uses configured dirs.

        Returns:
            Number of tools successfully discovered and loaded

        Raises:
            ToolDiscoveryError: If discovery process fails critically
        """
        dirs_to_scan = scan_dirs or self._tool_dirs

        if not dirs_to_scan:
            raise ToolDiscoveryError("No directories configured for tool discovery")

        tools_discovered = 0

        for scan_dir in dirs_to_scan:
            if not scan_dir.exists():
                continue

            # Recursively find all .yml and .yaml files
            for tool_file in scan_dir.rglob("*.yml"):
                try:
                    self.load_tool(tool_file)
                    tools_discovered += 1
                except ToolLoadError:
                    # Skip invalid tools during discovery
                    continue

            for tool_file in scan_dir.rglob("*.yaml"):
                try:
                    self.load_tool(tool_file)
                    tools_discovered += 1
                except ToolLoadError:
                    # Skip invalid tools during discovery
                    continue

        return tools_discovered

    def load_tool(self, tool_path: Path) -> dict[str, Any]:
        """Load a single tool from a YAML file.

        Validates the tool spec and adds it to the registry cache.

        Args:
            tool_path: Path to tool YAML file

        Returns:
            Loaded and validated tool specification

        Raises:
            ToolLoadError: If tool loading or validation fails
        """
        try:
            with open(tool_path, encoding="utf-8") as f:
                tool_spec = yaml.safe_load(f)
                if not isinstance(tool_spec, dict):
                    raise ToolLoadError(
                        "Tool spec must be a dictionary",
                        tool_path=str(tool_path),
                    )
        except ToolLoadError:
            raise
        except Exception as e:
            raise ToolLoadError(
                f"Failed to load tool from {tool_path}: {e}",
                tool_path=str(tool_path),
            ) from e

        # Validate tool spec if validation enabled
        if self._validator:
            try:
                validation_result = self._validator.validate_tool_spec(tool_spec)
                if not validation_result["valid"]:
                    raise ToolLoadError(
                        f"Tool validation failed: {validation_result['errors']}",
                        tool_path=str(tool_path),
                    )
            except Exception as e:
                raise ToolLoadError(
                    f"Tool validation error: {e}",
                    tool_path=str(tool_path),
                ) from e

        # Extract tool name from metadata
        if "metadata" not in tool_spec or "name" not in tool_spec["metadata"]:
            raise ToolLoadError(
                "Tool missing metadata.name field",
                tool_path=str(tool_path),
            )

        tool_name = tool_spec["metadata"]["name"]

        # Add to cache
        self._tools[tool_name] = tool_spec
        self._tool_paths[tool_name] = tool_path

        # Update category index
        category = tool_spec.get("metadata", {}).get("category", "uncategorized")
        if category not in self._categories:
            self._categories[category] = []
        if tool_name not in self._categories[category]:
            self._categories[category].append(tool_name)

        return tool_spec

    def get_tool(self, tool_name: str) -> dict[str, Any] | None:
        """Get a tool by name from the registry.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool specification dict, or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> list[str]:
        """List all tool names in the registry.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def list_categories(self) -> list[str]:
        """List all categories in the registry.

        Returns:
            List of category names
        """
        return list(self._categories.keys())

    def get_tools_by_category(self, category: str) -> list[str]:
        """Get all tool names in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of tool names in the category
        """
        return self._categories.get(category, [])

    def reload_tool(self, tool_name: str) -> dict[str, Any]:
        """Reload a specific tool from disk (hot-reload).

        Implements PM-004 hot-reload with validation and atomic swap.
        If validation fails, the old tool spec remains in cache.

        Args:
            tool_name: Name of tool to reload

        Returns:
            Reloaded tool specification

        Raises:
            ToolLoadError: If tool reload fails
        """
        if tool_name not in self._tool_paths:
            raise ToolLoadError(f"Tool '{tool_name}' not found in registry")

        tool_path = self._tool_paths[tool_name]

        # Load and validate new spec (without updating cache yet)
        try:
            with open(tool_path, encoding="utf-8") as f:
                new_spec = yaml.safe_load(f)
                if not isinstance(new_spec, dict):
                    raise ToolLoadError("Tool spec must be a dictionary")

            # Validate if enabled
            if self._validator:
                validation_result = self._validator.validate_tool_spec(new_spec)
                if not validation_result["valid"]:
                    raise ToolLoadError(f"Reload validation failed: {validation_result['errors']}")

            # Atomic swap: only update cache if validation passed
            self._tools[tool_name] = new_spec

            return new_spec

        except ToolLoadError:
            raise
        except Exception as e:
            raise ToolLoadError(
                f"Failed to reload tool '{tool_name}': {e}",
                tool_path=str(tool_path),
            ) from e

    def clear_cache(self) -> None:
        """Clear all cached tools from the registry."""
        self._tools.clear()
        self._tool_paths.clear()
        self._categories.clear()

    def get_tool_count(self) -> int:
        """Get total number of tools in registry.

        Returns:
            Number of cached tools
        """
        return len(self._tools)

    def get_tool_path(self, tool_name: str) -> Path | None:
        """Get the file path for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Path to tool file, or None if not found
        """
        return self._tool_paths.get(tool_name)
