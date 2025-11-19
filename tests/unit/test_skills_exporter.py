"""Unit tests for SkillsExporter."""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from cogito.orchestration.registry import ToolRegistry
from cogito.provisioning.skill_generator import SkillGenerator
from cogito.provisioning.skills_exporter import SkillsExporter


@pytest.fixture
def mock_registry() -> ToolRegistry:
    """Create mock ToolRegistry."""
    registry = Mock(spec=ToolRegistry)

    # Mock tool specs
    tool_specs = {
        "think_aloud": {
            "metadata": {
                "name": "think_aloud",
                "display_name": "Think Aloud",
                "description": "Work through problems step-by-step",
                "category": "metacognition",
                "tags": ["reasoning"],
                "author": "Test",
                "version": "1.0",
            },
            "parameters": {
                "properties": {
                    "problem": {"type": "string", "description": "Problem to solve"}
                },
                "required": ["problem"],
            },
        },
        "code_review": {
            "metadata": {
                "name": "code_review",
                "display_name": "Code Review",
                "description": "Review code changes",
                "category": "review",
                "tags": ["quality"],
                "author": "Test",
                "version": "1.0",
            },
            "parameters": {},
        },
        "session_handover": {
            "metadata": {
                "name": "session_handover",
                "display_name": "Session Handover",
                "description": "Create handover document",
                "category": "handoff",
                "tags": ["documentation"],
                "author": "Test",
                "version": "1.0",
            },
            "parameters": {},
        },
    }

    registry.get_tool = MagicMock(side_effect=lambda name: tool_specs.get(name))
    registry.list_tools = MagicMock(return_value=list(tool_specs.keys()))

    return registry


@pytest.fixture
def mock_generator() -> SkillGenerator:
    """Create mock SkillGenerator."""
    generator = Mock(spec=SkillGenerator)

    generator.generate_skill_name = MagicMock(
        side_effect=lambda name: name.lower().replace(" ", "-")
    )
    generator.generate_skill_md = MagicMock(
        return_value="---\nname: test\n---\n# Test\n"
    )
    generator.generate_bash_wrapper = MagicMock(
        return_value="#!/usr/bin/env bash\nset -euo pipefail\n"
    )

    return generator


class TestSkillsExporter:
    """Test SkillsExporter class."""

    def test_init(self, mock_registry: ToolRegistry) -> None:
        """Test SkillsExporter initialization."""
        exporter = SkillsExporter(tool_registry=mock_registry)

        assert exporter.registry == mock_registry
        assert exporter.generator is not None
        assert isinstance(exporter.generator, SkillGenerator)

    def test_init_with_generator(
        self, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test SkillsExporter initialization with custom generator."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        assert exporter.registry == mock_registry
        assert exporter.generator == mock_generator

    def test_export_tool_basic(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test basic tool export."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        # Export tool
        result = exporter.export_tool(
            tool_name="think_aloud",
            output_dir=tmp_path,
            create_symlink=False,  # Don't create symlink for test
        )

        # Verify result structure
        assert result["skill_name"] == "think-aloud"
        assert result["tool_name"] == "think_aloud"
        assert "skill_dir" in result
        assert "files" in result

        # Verify files created
        skill_dir = Path(result["skill_dir"])
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "scripts" / "execute.sh").exists()

        # Verify SKILL.md content
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert "name: test" in skill_md

        # Verify wrapper content
        wrapper = (skill_dir / "scripts" / "execute.sh").read_text(encoding="utf-8")
        assert "#!/usr/bin/env bash" in wrapper

    def test_export_tool_with_symlink(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test tool export with symlink creation."""
        # Create fake source file
        examples_dir = tmp_path / "examples" / "metacognition"
        examples_dir.mkdir(parents=True)
        source_file = examples_dir / "think_aloud.yml"
        source_file.write_text("# Test YAML", encoding="utf-8")

        # Change to tmp directory
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            exporter = SkillsExporter(
                tool_registry=mock_registry, skill_generator=mock_generator
            )

            result = exporter.export_tool(
                tool_name="think_aloud",
                output_dir=tmp_path / "skills",
                create_symlink=True,
            )

            # Verify symlink created (or file copied on Windows)
            skill_dir = Path(result["skill_dir"])
            tool_yml = skill_dir / "tool.yml"
            assert tool_yml.exists()

        finally:
            os.chdir(original_cwd)

    def test_export_tool_not_found(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test export of non-existent tool."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        with pytest.raises(FileNotFoundError, match="not found"):
            exporter.export_tool(
                tool_name="nonexistent",
                output_dir=tmp_path,
                create_symlink=False,
            )

    def test_export_category(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test category export."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        result = exporter.export_category(
            category="metacognition",
            output_dir=tmp_path,
            create_symlinks=False,
        )

        # Verify result structure
        assert result["category"] == "metacognition"
        assert result["total"] == 1  # Only think_aloud
        assert len(result["exported"]) == 1
        assert len(result["failed"]) == 0

        # Verify exported tool
        assert result["exported"][0]["tool_name"] == "think_aloud"
        assert result["exported"][0]["skill_name"] == "think-aloud"

    def test_export_category_empty(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test export of empty category."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        result = exporter.export_category(
            category="nonexistent",
            output_dir=tmp_path,
            create_symlinks=False,
        )

        assert result["category"] == "nonexistent"
        assert result["total"] == 0
        assert len(result["exported"]) == 0
        assert len(result["failed"]) == 0

    def test_export_category_with_failures(
        self, tmp_path: Path, mock_registry: ToolRegistry
    ) -> None:
        """Test category export with some failures."""
        # Mock generator that fails for specific tool
        generator = Mock(spec=SkillGenerator)
        generator.generate_skill_name = MagicMock(
            side_effect=lambda name: name.lower().replace(" ", "-")
        )
        generator.generate_skill_md = MagicMock(
            side_effect=lambda spec, path: (
                ValueError("Invalid spec")
                if spec["metadata"]["name"] == "code_review"
                else "# Test\n"
            )
        )
        generator.generate_bash_wrapper = MagicMock(
            return_value="#!/usr/bin/env bash\n"
        )

        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=generator
        )

        result = exporter.export_category(
            category="review",
            output_dir=tmp_path,
            create_symlinks=False,
        )

        # Verify failures tracked
        assert result["total"] == 1
        assert len(result["failed"]) == 1
        assert result["failed"][0]["tool_name"] == "code_review"
        assert "error" in result["failed"][0]

    def test_export_all(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test export all tools."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        result = exporter.export_all(
            output_dir=tmp_path,
            create_symlinks=False,
        )

        # Verify result
        assert result["total"] == 3  # think_aloud, code_review, session_handover
        assert len(result["exported"]) == 3
        assert len(result["failed"]) == 0

        # Verify all tools exported
        exported_names = {tool["tool_name"] for tool in result["exported"]}
        assert exported_names == {"think_aloud", "code_review", "session_handover"}

    def test_get_tool_source_path(
        self, tmp_path: Path, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test source path resolution."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        # Test path construction
        source_path = exporter._get_tool_source_path("think_aloud")

        # Should be examples/metacognition/think_aloud.yml
        assert "examples" in str(source_path)
        assert "metacognition" in str(source_path)
        assert "think_aloud.yml" in str(source_path)

    def test_get_tool_source_path_not_found(
        self, mock_registry: ToolRegistry, mock_generator: SkillGenerator
    ) -> None:
        """Test source path for non-existent tool."""
        exporter = SkillsExporter(
            tool_registry=mock_registry, skill_generator=mock_generator
        )

        with pytest.raises(FileNotFoundError, match="not found"):
            exporter._get_tool_source_path("nonexistent")
