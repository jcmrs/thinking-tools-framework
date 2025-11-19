"""Integration tests for rendering real example thinking tools.

Tests that all 9 example tools can be successfully rendered with sample parameters.
Validates that the TemplateRenderer works correctly with production tool specifications.
"""

from pathlib import Path

import pytest
import yaml

from cogito.processing import TemplateRenderer

# Path to example tools
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


class TestRealToolRendering:
    """Test rendering of actual example thinking tools."""

    def test_think_aloud_quick_mode(self) -> None:
        """Test rendering think_aloud tool in quick mode."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"depth": "quick", "focus": "algorithm choice"}
        result = renderer.render(tool_spec, params)

        # Verify key sections appear in quick mode
        assert "Quick Think Aloud" in result
        assert "algorithm choice" in result
        assert "Current Understanding" in result
        assert "Reasoning Path" in result
        assert "Conclusion" in result

    def test_think_aloud_standard_mode(self) -> None:
        """Test rendering think_aloud tool in standard mode."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"depth": "standard", "focus": ""}
        result = renderer.render(tool_spec, params)

        # Verify standard mode sections
        assert "Standard Think Aloud" in result
        assert "State Current Understanding" in result
        assert "Articulate Assumptions" in result
        assert "Walk Through Reasoning" in result

    def test_think_aloud_detailed_mode(self) -> None:
        """Test rendering think_aloud tool in detailed mode."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"depth": "detailed", "focus": "architecture decision"}
        result = renderer.render(tool_spec, params)

        # Verify detailed mode has all sections
        assert "Detailed Think Aloud" in result
        assert "architecture decision" in result
        assert "Articulate Mental Model" in result
        assert "Identify Decision Points" in result
        assert "Question Assumptions" in result
        assert "Examine Biases" in result

    def test_assumption_check(self) -> None:
        """Test rendering assumption_check tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "metacognition" / "assumption_check.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"scope": "current_task", "task_context": ""}
        result = renderer.render(tool_spec, params)

        assert "Assumption Check" in result
        assert "CURRENT_TASK" in result

    def test_fresh_eyes_exercise(self) -> None:
        """Test rendering fresh_eyes_exercise tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "metacognition" / "fresh_eyes_exercise.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"phase": "full"}
        result = renderer.render(tool_spec, params)

        assert "Fresh Eyes Exercise" in result
        assert ("Step Back" in result or "Step back" in result)

    def test_code_review_checklist(self) -> None:
        """Test rendering code_review_checklist tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "review" / "code_review_checklist.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {
            "review_type": "self",
            "language": "python",
            "change_description": "add user authentication",
        }
        result = renderer.render(tool_spec, params)

        assert "Code Review Checklist" in result
        assert "SELF" in result
        assert "PYTHON" in result
        assert "add user authentication" in result
        assert "Five Cornerstones Compliance" in result
        assert "Configurability" in result

    def test_architecture_review(self) -> None:
        """Test rendering architecture_review tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "review" / "architecture_review.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"aspect": "full", "system_description": "payment-service"}
        result = renderer.render(tool_spec, params)

        assert "Architecture Review" in result
        assert "payment-service" in result

    def test_session_handover(self) -> None:
        """Test rendering session_handover tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "handoff" / "session_handover.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"completeness": "essential", "reason": "session_end"}
        result = renderer.render(tool_spec, params)

        assert "Session Handover" in result
        assert "ESSENTIAL" in result

    def test_context_preservation(self) -> None:
        """Test rendering context_preservation tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "handoff" / "context_preservation.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"trigger": "checkpoint", "expected_duration": "unknown"}
        result = renderer.render(tool_spec, params)

        assert "Context Preservation" in result

    def test_five_whys(self) -> None:
        """Test rendering five_whys tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "debugging" / "five_whys.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {"problem": "database connection timeout", "depth": 5}
        result = renderer.render(tool_spec, params)

        assert "Five Whys Analysis" in result
        assert "database connection timeout" in result

    def test_error_analysis(self) -> None:
        """Test rendering error_analysis tool."""
        renderer = TemplateRenderer()
        tool_path = EXAMPLES_DIR / "debugging" / "error_analysis.yml"

        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        params = {
            "error_type": "runtime",
            "error_description": "NullPointerException at line 42",
        }
        result = renderer.render(tool_spec, params)

        assert "Error Analysis" in result
        assert "RUNTIME" in result
        assert "NullPointerException at line 42" in result


class TestToolsWithCompleteParameters:
    """Test tools that we've provided complete parameters for.

    Note: Full parameter defaulting will be handled by ParameterValidator
    (to be implemented in next phase). For now, we test with explicitly
    provided parameters to verify the renderer works correctly.
    """

    def test_all_tools_can_load_yaml(self) -> None:
        """Verify all 9 example tools have valid YAML structure."""
        tool_paths = [
            "metacognition/think_aloud.yml",
            "metacognition/assumption_check.yml",
            "metacognition/fresh_eyes_exercise.yml",
            "review/code_review_checklist.yml",
            "review/architecture_review.yml",
            "handoff/session_handover.yml",
            "handoff/context_preservation.yml",
            "debugging/five_whys.yml",
            "debugging/error_analysis.yml",
        ]

        for tool_path in tool_paths:
            full_path = EXAMPLES_DIR / tool_path
            try:
                with open(full_path, encoding="utf-8") as f:
                    tool_spec = yaml.safe_load(f)
                # Verify basic structure
                assert "metadata" in tool_spec
                assert "template" in tool_spec
                assert "source" in tool_spec["template"]
            except Exception as e:
                pytest.fail(f"Tool {tool_path} failed to load as valid YAML: {e}")
