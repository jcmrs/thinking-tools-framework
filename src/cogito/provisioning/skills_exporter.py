"""Skills export functionality for thinking tools."""

import os
from pathlib import Path
from typing import Any

from cogito.orchestration.registry import ToolRegistry
from cogito.provisioning.skill_generator import SkillGenerator


class SkillsExporter:
    """Export thinking tools as Claude Code Skills."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        skill_generator: SkillGenerator | None = None,
    ) -> None:
        """Initialize skills exporter.

        Args:
            tool_registry: ToolRegistry instance for tool discovery
            skill_generator: Optional SkillGenerator instance
        """
        self.registry = tool_registry
        self.generator = skill_generator or SkillGenerator()

    def export_tool(
        self, tool_name: str, output_dir: Path, create_symlink: bool = True
    ) -> dict[str, Any]:
        """Export single tool as Claude Skill.

        Args:
            tool_name: Tool name to export
            output_dir: Output directory for skill files
            create_symlink: Whether to create symlink to source YAML

        Returns:
            Dictionary with export results

        Raises:
            FileNotFoundError: If tool not found
            IOError: If export fails
        """
        # Load tool spec
        tool_spec = self.registry.get_tool(tool_name)
        if tool_spec is None:
            raise FileNotFoundError(f"Tool '{tool_name}' not found")

        # Get source file path
        source_path = self._get_tool_source_path(tool_name)

        # Generate skill name
        metadata = tool_spec.get("metadata", {})
        display_name = metadata.get("display_name", metadata.get("name", tool_name))
        skill_name = self.generator.generate_skill_name(display_name)

        # Create skill directory
        skill_dir = output_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Generate SKILL.md
        skill_md_content = self.generator.generate_skill_md(tool_spec, source_path)
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(skill_md_content, encoding="utf-8")

        # Generate bash wrapper
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        wrapper_content = self.generator.generate_bash_wrapper(tool_name)
        wrapper_path = scripts_dir / "execute.sh"
        wrapper_path.write_text(wrapper_content, encoding="utf-8")

        # Make wrapper executable (Unix)
        if os.name != "nt":  # Not Windows
            wrapper_path.chmod(0o755)

        # Create symlink to source YAML
        symlink_path = skill_dir / "tool.yml"
        if create_symlink and source_path.exists():
            # Remove existing symlink if present
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()

            # Create new symlink
            try:
                symlink_path.symlink_to(source_path.resolve())
            except OSError:
                # Symlink failed (e.g., Windows without permissions)
                # Copy file instead
                symlink_path.write_text(
                    source_path.read_text(encoding="utf-8"), encoding="utf-8"
                )

        return {
            "skill_name": skill_name,
            "tool_name": tool_name,
            "skill_dir": str(skill_dir),
            "files": {
                "skill_md": str(skill_md_path),
                "wrapper": str(wrapper_path),
                "symlink": str(symlink_path) if create_symlink else None,
            },
        }

    def export_category(
        self, category: str, output_dir: Path, create_symlinks: bool = True
    ) -> dict[str, Any]:
        """Export all tools in category as Claude Skills.

        Args:
            category: Category name
            output_dir: Output directory for skill files
            create_symlinks: Whether to create symlinks to source YAMLs

        Returns:
            Dictionary with export results
        """
        # Get tools in category
        all_tool_names = self.registry.list_tools()
        category_tools: list[str] = []

        # Filter by category
        for tool_name in all_tool_names:
            tool_spec = self.registry.get_tool(tool_name)
            if tool_spec:
                metadata = tool_spec.get("metadata", {})
                if metadata.get("category") == category:
                    category_tools.append(tool_name)

        results: dict[str, Any] = {
            "category": category,
            "total": len(category_tools),
            "exported": [],
            "failed": [],
        }

        for tool_name in category_tools:
            try:
                result = self.export_tool(tool_name, output_dir, create_symlinks)
                results["exported"].append(result)
            except Exception as e:
                results["failed"].append({"tool_name": tool_name, "error": str(e)})

        return results

    def export_all(
        self, output_dir: Path, create_symlinks: bool = True
    ) -> dict[str, Any]:
        """Export all tools as Claude Skills.

        Args:
            output_dir: Output directory for skill files
            create_symlinks: Whether to create symlinks to source YAMLs

        Returns:
            Dictionary with export results
        """
        all_tool_names = self.registry.list_tools()

        results: dict[str, Any] = {
            "total": len(all_tool_names),
            "exported": [],
            "failed": [],
        }

        for tool_name in all_tool_names:
            try:
                result = self.export_tool(tool_name, output_dir, create_symlinks)
                results["exported"].append(result)
            except Exception as e:
                results["failed"].append({"tool_name": tool_name, "error": str(e)})

        return results

    def _get_tool_source_path(self, tool_name: str) -> Path:
        """Get source YAML path for tool.

        Args:
            tool_name: Tool name

        Returns:
            Path to source YAML file
        """
        # Get tool metadata
        tool_spec = self.registry.get_tool(tool_name)
        if tool_spec is None:
            raise FileNotFoundError(f"Tool '{tool_name}' not found")

        metadata = tool_spec.get("metadata", {})
        category: str = str(metadata.get("category", "unknown"))

        # Construct path to examples directory
        # Assumes registry discovers from examples/
        examples_dir = Path("examples")
        source_path = examples_dir / category / f"{tool_name}.yml"

        # Try absolute path if relative doesn't exist
        if not source_path.exists():
            # Get absolute path from current working directory
            cwd = Path.cwd()
            source_path = cwd / "examples" / category / f"{tool_name}.yml"

        return source_path
