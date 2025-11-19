"""Example thinking tools selector for bootstrap package.

This module selects and copies example thinking tools from the thinking-tools-framework
to new project instances, providing working examples for users.
"""

import shutil
from pathlib import Path
from typing import Any


class ExampleToolsSelector:
    """Selects and copies example thinking tools to new projects."""

    # Curated list of starter tools (most representative from each category)
    STARTER_TOOLS: dict[str, list[str]] = {
        "metacognition": [
            "think_aloud.yml",
            "fresh_eyes.yml",
            "context_preservation.yml",
        ],
        "problem_solving": [
            "assumption_challenger.yml",
            "decision_journal.yml",
        ],
    }

    def __init__(self, source_examples_dir: Path | None = None) -> None:
        """Initialize the example tools selector.

        Args:
            source_examples_dir: Directory containing source example tools.
                                Defaults to examples/ in current framework.
        """
        if source_examples_dir is None:
            # Default to examples/ directory in current framework
            package_root = Path(__file__).parent.parent.parent.parent
            source_examples_dir = package_root / "examples"

        self.source_examples_dir = source_examples_dir

    def get_starter_tools(self) -> dict[str, list[str]]:
        """Get the list of starter tools to include in new projects.

        Returns:
            Dictionary mapping categories to lists of tool filenames
        """
        # Deep copy to ensure lists are also copied
        return {k: v.copy() for k, v in self.STARTER_TOOLS.items()}

    def copy_tool(
        self, category: str, tool_filename: str, dest_category_dir: Path
    ) -> dict[str, Any]:
        """Copy a single tool file to destination project.

        Args:
            category: Tool category (e.g., 'metacognition')
            tool_filename: Tool YAML filename (e.g., 'think_aloud.yml')
            dest_category_dir: Destination category directory in new project

        Returns:
            Dictionary with copy results:
                - success: True if copy succeeded
                - source: Source file path
                - destination: Destination file path
                - error: Error message if copy failed
        """
        source_file = self.source_examples_dir / category / tool_filename
        dest_file = dest_category_dir / tool_filename

        result: dict[str, Any] = {
            "success": False,
            "source": str(source_file),
            "destination": str(dest_file),
        }

        # Check if source file exists
        if not source_file.exists():
            result["error"] = f"Source tool not found: {source_file}"
            return result

        # Ensure destination directory exists
        try:
            dest_category_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            result["error"] = f"Failed to create destination directory: {e}"
            return result

        # Copy the file
        try:
            shutil.copy2(source_file, dest_file)
            result["success"] = True
        except Exception as e:
            result["error"] = f"Failed to copy file: {e}"

        return result

    def copy_starter_tools(
        self, dest_examples_dir: Path
    ) -> dict[str, Any]:
        """Copy all starter tools to destination project.

        Args:
            dest_examples_dir: Destination examples/ directory in new project

        Returns:
            Dictionary with copy results:
                - total: Total number of tools to copy
                - copied: Number of tools successfully copied
                - failed: Number of tools that failed to copy
                - results: List of individual copy results
        """
        results: dict[str, Any] = {
            "total": 0,
            "copied": 0,
            "failed": 0,
            "results": [],
        }

        for category, tool_filenames in self.STARTER_TOOLS.items():
            dest_category_dir = dest_examples_dir / category

            for tool_filename in tool_filenames:
                results["total"] += 1
                copy_result = self.copy_tool(category, tool_filename, dest_category_dir)
                results["results"].append(copy_result)

                if copy_result["success"]:
                    results["copied"] += 1
                else:
                    results["failed"] += 1

        return results

    def create_examples_readme(self, dest_examples_dir: Path) -> dict[str, Any]:
        """Create README.md in examples directory explaining the tools.

        Args:
            dest_examples_dir: Destination examples/ directory

        Returns:
            Dictionary with creation result:
                - success: True if README created
                - path: Path to created README
                - error: Error message if creation failed
        """
        readme_path = dest_examples_dir / "README.md"
        result: dict[str, Any] = {
            "success": False,
            "path": str(readme_path),
        }

        readme_content = """# Example Thinking Tools

This directory contains example thinking tools that demonstrate the capabilities
of the Thinking Tools Framework.

## Categories

- **metacognition**: Tools for self-reflection, planning, and systematic thinking
- **problem_solving**: Tools for analyzing problems and making decisions

## Creating New Tools

To create a new thinking tool:

1. Choose a category (or create a new one)
2. Create a YAML file following the schema in `schemas/thinking-tool-v1.0.schema.json`
3. Define metadata, parameters, and a Jinja2 template
4. Validate using `bash scripts/validate.sh examples/your_category/`

See existing tools for examples of the YAML format and template patterns.

## Using Tools

Execute tools via CLI:
```bash
cogito execute think_aloud depth=detailed
```

Or via MCP server integration with Claude Code or other MCP clients.
"""

        try:
            dest_examples_dir.mkdir(parents=True, exist_ok=True)
            readme_path.write_text(readme_content, encoding="utf-8")
            result["success"] = True
        except Exception as e:
            result["error"] = f"Failed to create README: {e}"

        return result
