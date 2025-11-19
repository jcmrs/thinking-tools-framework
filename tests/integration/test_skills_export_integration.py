"""Integration tests for Skills export end-to-end functionality."""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from cogito.orchestration.registry import ToolRegistry
from cogito.provisioning.skill_generator import SkillGenerator
from cogito.provisioning.skills_exporter import SkillsExporter
from cogito.ui.cli import cli


class TestSkillsExportIntegration:
    """Integration tests for Skills export."""

    def test_export_real_tool_end_to_end(self, tmp_path: Path) -> None:
        """Test exporting a real tool from examples directory."""
        # Initialize real components
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()

        generator = SkillGenerator()
        exporter = SkillsExporter(tool_registry=registry, skill_generator=generator)

        # Get first available tool
        tool_names = registry.list_tools()
        assert len(tool_names) > 0, "No tools found in examples/"

        tool_name = tool_names[0]
        tool_spec = registry.get_tool(tool_name)
        assert tool_spec is not None

        # Export tool
        result = exporter.export_tool(
            tool_name=tool_name,
            output_dir=tmp_path,
            create_symlink=False,
        )

        # Verify result structure
        assert result["skill_name"]
        assert result["tool_name"] == tool_name
        assert result["skill_dir"]
        assert result["files"]["skill_md"]
        assert result["files"]["wrapper"]

        # Verify files exist
        skill_dir = Path(result["skill_dir"])
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "scripts" / "execute.sh").exists()

        # Verify SKILL.md content
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert "---" in skill_md  # Frontmatter
        assert "name:" in skill_md
        assert "description:" in skill_md
        assert "# " in skill_md  # Heading
        assert "## Instructions" in skill_md
        assert "## Examples" in skill_md or "## Reference" in skill_md

        # Verify bash wrapper
        wrapper = (skill_dir / "scripts" / "execute.sh").read_text(encoding="utf-8")
        assert wrapper.startswith("#!/usr/bin/env bash")
        assert "set -euo pipefail" in wrapper
        assert tool_name in wrapper

    def test_skill_md_validates_schema(self, tmp_path: Path) -> None:
        """Test that generated SKILL.md validates against Claude Skills schema."""
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()

        generator = SkillGenerator()
        exporter = SkillsExporter(tool_registry=registry, skill_generator=generator)

        # Export first tool
        tool_name = registry.list_tools()[0]
        result = exporter.export_tool(
            tool_name=tool_name,
            output_dir=tmp_path,
            create_symlink=False,
        )

        # Read SKILL.md
        skill_md_path = Path(result["files"]["skill_md"])
        skill_md = skill_md_path.read_text(encoding="utf-8")

        # Validate frontmatter structure
        assert skill_md.startswith("---\n")
        frontmatter_end = skill_md.find("\n---\n", 4)
        assert frontmatter_end > 0

        frontmatter = skill_md[4:frontmatter_end]

        # Validate required frontmatter fields
        assert "name:" in frontmatter
        assert "description:" in frontmatter

        # Extract and validate name
        name_line = [line for line in frontmatter.split("\n") if line.startswith("name:")]
        assert len(name_line) == 1
        name = name_line[0].split(":", 1)[1].strip()

        # Validate name format (lowercase, hyphens, max 64 chars)
        assert name.islower() or "-" in name  # lowercase or contains hyphens
        assert len(name) <= 64
        assert "anthropic" not in name
        assert "claude" not in name

        # Extract and validate description
        desc_line = [
            line for line in frontmatter.split("\n") if line.startswith("description:")
        ]
        assert len(desc_line) == 1
        desc = desc_line[0].split(":", 1)[1].strip()

        # Validate description length
        assert len(desc) <= 1024

    def test_export_category_integration(self, tmp_path: Path) -> None:
        """Test exporting all tools in a category."""
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()

        generator = SkillGenerator()
        exporter = SkillsExporter(tool_registry=registry, skill_generator=generator)

        # Find category with tools
        all_tools = registry.list_tools()
        categories = set()
        for tool_name in all_tools:
            tool_spec = registry.get_tool(tool_name)
            if tool_spec:
                metadata = tool_spec.get("metadata", {})
                category = metadata.get("category")
                if category:
                    categories.add(category)

        assert len(categories) > 0, "No categories found"

        # Export first category
        category = list(categories)[0]
        result = exporter.export_category(
            category=category,
            output_dir=tmp_path,
            create_symlinks=False,
        )

        # Verify results
        assert result["category"] == category
        assert result["total"] > 0
        assert len(result["exported"]) > 0
        assert len(result["failed"]) == 0

        # Verify all exported tools
        for export in result["exported"]:
            skill_dir = Path(export["skill_dir"])
            assert skill_dir.exists()
            assert (skill_dir / "SKILL.md").exists()
            assert (skill_dir / "scripts" / "execute.sh").exists()

    def test_export_all_integration(self, tmp_path: Path) -> None:
        """Test exporting all tools."""
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()

        generator = SkillGenerator()
        exporter = SkillsExporter(tool_registry=registry, skill_generator=generator)

        # Export all
        result = exporter.export_all(
            output_dir=tmp_path,
            create_symlinks=False,
        )

        # Verify results
        assert result["total"] > 0
        assert len(result["exported"]) > 0

        # Should export most/all tools successfully
        success_rate = len(result["exported"]) / result["total"]
        assert success_rate >= 0.9, f"Low success rate: {success_rate:.0%}"

    def test_cli_export_command(self, tmp_path: Path) -> None:
        """Test CLI export command."""
        runner = CliRunner()

        # Get first available tool
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()
        tool_names = registry.list_tools()
        assert len(tool_names) > 0

        tool_name = tool_names[0]

        # Run export command
        result = runner.invoke(
            cli,
            ["skills", "export", tool_name, "--output", str(tmp_path), "--no-symlink"],
        )

        # Verify command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Exporting tool" in result.output
        assert "Exported to:" in result.output

        # Verify files created
        # Find skill directory (name is derived from tool)
        skill_dirs = list(tmp_path.iterdir())
        assert len(skill_dirs) >= 1

    def test_cli_export_category_command(self, tmp_path: Path) -> None:
        """Test CLI export-category command."""
        runner = CliRunner()

        # Find a category
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()
        all_tools = registry.list_tools()
        category = None
        for tool_name in all_tools:
            tool_spec = registry.get_tool(tool_name)
            if tool_spec:
                metadata = tool_spec.get("metadata", {})
                category = metadata.get("category")
                if category:
                    break

        assert category is not None

        # Run export-category command
        result = runner.invoke(
            cli,
            [
                "skills",
                "export-category",
                category,
                "--output",
                str(tmp_path),
                "--no-symlinks",
            ],
        )

        # Verify command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert f"Exporting category '{category}'" in result.output
        assert "Exported" in result.output

    def test_cli_export_all_command(self, tmp_path: Path) -> None:
        """Test CLI export-all command."""
        runner = CliRunner()

        # Run export-all command
        result = runner.invoke(
            cli,
            ["skills", "export-all", "--output", str(tmp_path), "--no-symlinks"],
        )

        # Verify command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Exporting all thinking tools" in result.output
        assert "Exported" in result.output

        # Verify multiple tools exported
        skill_dirs = list(tmp_path.iterdir())
        assert len(skill_dirs) > 1

    def test_symlink_creation(self, tmp_path: Path) -> None:
        """Test symlink creation to source YAML."""
        # Change to project root
        original_cwd = Path.cwd()

        try:
            examples_dir = Path("examples")
            registry = ToolRegistry(tool_dirs=[examples_dir])
            registry.discover_tools()

            generator = SkillGenerator()
            exporter = SkillsExporter(
                tool_registry=registry, skill_generator=generator
            )

            # Export first tool with symlink
            tool_name = registry.list_tools()[0]
            result = exporter.export_tool(
                tool_name=tool_name,
                output_dir=tmp_path,
                create_symlink=True,
            )

            # Verify symlink exists (or file copied on Windows)
            skill_dir = Path(result["skill_dir"])
            tool_yml = skill_dir / "tool.yml"
            assert tool_yml.exists()

            # Verify it points to or contains YAML content
            content = tool_yml.read_text(encoding="utf-8")
            assert "metadata:" in content or "parameters:" in content

        finally:
            os.chdir(original_cwd)

    def test_bash_wrapper_executable(self, tmp_path: Path) -> None:
        """Test bash wrapper is executable on Unix."""
        examples_dir = Path("examples")
        registry = ToolRegistry(tool_dirs=[examples_dir])
        registry.discover_tools()

        generator = SkillGenerator()
        exporter = SkillsExporter(tool_registry=registry, skill_generator=generator)

        # Export first tool
        tool_name = registry.list_tools()[0]
        result = exporter.export_tool(
            tool_name=tool_name,
            output_dir=tmp_path,
            create_symlink=False,
        )

        # Check wrapper permissions (Unix only)
        wrapper_path = Path(result["files"]["wrapper"])
        assert wrapper_path.exists()

        if os.name != "nt":  # Not Windows
            # Verify executable bit set
            assert os.access(wrapper_path, os.X_OK)
