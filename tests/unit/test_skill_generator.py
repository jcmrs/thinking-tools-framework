"""Unit tests for SkillGenerator."""

from pathlib import Path

import pytest

from cogito.provisioning.skill_generator import SkillGenerator


class TestSkillGenerator:
    """Test SkillGenerator class."""

    def test_generate_skill_name_basic(self) -> None:
        """Test basic skill name generation."""
        generator = SkillGenerator()

        # Basic conversion
        assert generator.generate_skill_name("Think Aloud") == "think-aloud"
        assert generator.generate_skill_name("Code Review") == "code-review"
        assert generator.generate_skill_name("Session Handover") == "session-handover"

    def test_generate_skill_name_special_chars(self) -> None:
        """Test skill name generation with special characters."""
        generator = SkillGenerator()

        # Special characters replaced with hyphens
        assert generator.generate_skill_name("Think! Aloud?") == "think-aloud"
        assert generator.generate_skill_name("Code_Review@2024") == "code-review-2024"

        # Multiple consecutive hyphens collapsed
        assert generator.generate_skill_name("Think   Aloud") == "think-aloud"
        assert generator.generate_skill_name("Code---Review") == "code-review"

    def test_generate_skill_name_edge_cases(self) -> None:
        """Test skill name generation edge cases."""
        generator = SkillGenerator()

        # Leading/trailing hyphens stripped
        assert generator.generate_skill_name("-Think Aloud-") == "think-aloud"
        assert generator.generate_skill_name("  Code Review  ") == "code-review"

        # Numbers preserved
        assert generator.generate_skill_name("Version 2 Review") == "version-2-review"

    def test_generate_skill_name_too_long(self) -> None:
        """Test skill name generation with name too long."""
        generator = SkillGenerator()

        long_name = "a" * 70  # Exceeds 64 char limit
        with pytest.raises(ValueError, match="exceeds maximum length"):
            generator.generate_skill_name(long_name)

    def test_generate_skill_name_forbidden_patterns(self) -> None:
        """Test skill name generation with forbidden patterns."""
        generator = SkillGenerator()

        with pytest.raises(ValueError, match="contains forbidden pattern"):
            generator.generate_skill_name("Anthropic Tool")

        with pytest.raises(ValueError, match="contains forbidden pattern"):
            generator.generate_skill_name("Claude Helper")

    def test_generate_description_basic(self) -> None:
        """Test basic description generation."""
        generator = SkillGenerator()

        metadata = {
            "description": "Help with code review tasks.",
            "category": "review",
        }
        parameters = {}

        desc = generator.generate_description(metadata, parameters)
        assert "Help with code review tasks" in desc
        assert "Use when" in desc
        assert "conducting code or system reviews" in desc

    def test_generate_description_truncation(self) -> None:
        """Test description truncation at 1024 chars."""
        generator = SkillGenerator()

        long_desc = "a" * 1500
        metadata = {"description": long_desc}
        parameters = {}

        desc = generator.generate_description(metadata, parameters)
        assert len(desc) <= 1024
        assert desc.endswith("...")

    def test_infer_use_cases_by_category(self) -> None:
        """Test use case inference from category."""
        generator = SkillGenerator()

        test_cases = [
            ("metacognition", "working through complex problems step-by-step"),
            ("review", "conducting code or system reviews"),
            ("handoff", "documenting decisions or transferring knowledge"),
            ("debugging", "investigating errors or unexpected behavior"),
            ("planning", "designing architecture or breaking down tasks"),
        ]

        for category, expected in test_cases:
            metadata = {"category": category}
            result = generator._infer_use_cases(metadata, {})
            assert result == expected

    def test_infer_use_cases_by_tags(self) -> None:
        """Test use case inference from tags."""
        generator = SkillGenerator()

        # Planning tag
        metadata = {"tags": ["planning", "organization"]}
        assert "planning or organizing" in generator._infer_use_cases(metadata, {})

        # Analysis tag
        metadata = {"tags": ["analysis"]}
        assert "analyzing systems" in generator._infer_use_cases(metadata, {})

        # Documentation tag
        metadata = {"tags": ["documentation"]}
        assert "creating or reviewing documentation" in generator._infer_use_cases(
            metadata, {}
        )

    def test_infer_use_cases_default(self) -> None:
        """Test default use case inference."""
        generator = SkillGenerator()

        metadata = {"category": "unknown", "tags": []}
        result = generator._infer_use_cases(metadata, {})
        assert "structured guidance" in result

    def test_generate_skill_md_basic(self) -> None:
        """Test basic SKILL.md generation."""
        generator = SkillGenerator()

        tool_spec = {
            "metadata": {
                "name": "test_tool",
                "display_name": "Test Tool",
                "description": "A test thinking tool",
                "category": "metacognition",
                "tags": ["testing"],
                "author": "Test Author",
                "version": "1.0",
            },
            "parameters": {
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to analyze",
                    }
                },
                "required": ["topic"],
            },
        }

        source_path = Path("examples/metacognition/test_tool.yml")
        skill_md = generator.generate_skill_md(tool_spec, source_path)

        # Check frontmatter
        assert "---" in skill_md
        assert "name: test-tool" in skill_md
        assert "description:" in skill_md

        # Check sections
        assert "# Test Tool" in skill_md
        assert "## Instructions" in skill_md
        assert "**When to use:**" in skill_md
        assert "**Parameters:**" in skill_md
        assert "**Execution:**" in skill_md

        # Check parameter docs
        assert "topic" in skill_md
        assert "required" in skill_md
        assert "Topic to analyze" in skill_md

    def test_generate_skill_md_with_examples(self) -> None:
        """Test SKILL.md generation with examples."""
        generator = SkillGenerator()

        tool_spec = {
            "metadata": {
                "name": "test_tool",
                "display_name": "Test Tool",
                "description": "A test tool",
                "category": "metacognition",
                "examples": [
                    {
                        "title": "Basic Usage",
                        "description": "Simple example",
                        "parameters": {"topic": "testing"},
                        "output": "Test output",
                    }
                ],
            },
            "parameters": {},
        }

        source_path = Path("examples/test_tool.yml")
        skill_md = generator.generate_skill_md(tool_spec, source_path)

        # Check examples section
        assert "## Examples" in skill_md
        assert "Example 1: Basic Usage" in skill_md
        assert "Simple example" in skill_md
        assert "--topic" in skill_md
        assert "Expected Output:" in skill_md

    def test_generate_bash_wrapper(self) -> None:
        """Test bash wrapper generation."""
        generator = SkillGenerator()

        wrapper = generator.generate_bash_wrapper("think_aloud")

        # Check shebang
        assert wrapper.startswith("#!/usr/bin/env bash")

        # Check set flags
        assert "set -euo pipefail" in wrapper

        # Check tool name
        assert 'TOOL_NAME="think_aloud"' in wrapper

        # Check cogito bin
        assert 'COGITO_BIN="${COGITO_BIN:-cogito}"' in wrapper

        # Check exec
        assert 'exec "$COGITO_BIN" execute "$TOOL_NAME" "$@"' in wrapper
