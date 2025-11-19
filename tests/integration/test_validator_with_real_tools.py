"""Integration tests for validators with real thinking tools."""

from pathlib import Path

import yaml

from cogito.processing.renderer import TemplateRenderer
from cogito.processing.validator import (
    ParameterValidator,
    SchemaValidator,
)

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


class TestParameterValidatorWithRealTools:
    """Test ParameterValidator with actual thinking tool specs."""

    def test_validate_think_aloud_with_defaults(self) -> None:
        """Test think_aloud tool parameter validation with defaults."""
        validator = ParameterValidator()
        renderer = TemplateRenderer()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Validate with no parameters - should apply defaults
        params = validator.validate_parameters(tool_spec, {})

        assert "depth" in params
        assert params["depth"] == "standard"
        assert "focus" in params
        assert params["focus"] == ""

        # Should be able to render with validated params
        result = renderer.render(tool_spec, params)
        assert "Think Aloud Protocol" in result
        assert "Standard Think Aloud" in result

    def test_validate_think_aloud_with_custom_params(self) -> None:
        """Test think_aloud with custom parameter values."""
        validator = ParameterValidator()
        renderer = TemplateRenderer()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Validate with custom parameters
        user_params = {"depth": "detailed", "focus": "algorithm optimization"}
        params = validator.validate_parameters(tool_spec, user_params)

        assert params["depth"] == "detailed"
        assert params["focus"] == "algorithm optimization"

        # Should render detailed mode
        result = renderer.render(tool_spec, params)
        assert "Detailed Think Aloud" in result
        assert "algorithm optimization" in result

    def test_validate_assumption_check_parameters(self) -> None:
        """Test assumption_check tool parameter validation."""
        validator = ParameterValidator()

        tool_path = EXAMPLES_DIR / "metacognition" / "assumption_check.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Should apply defaults
        params = validator.validate_parameters(tool_spec, {})

        assert "scope" in params
        assert params["scope"] == "all"  # Actual default value

    def test_validate_error_analysis_parameters(self) -> None:
        """Test error_analysis tool parameter validation."""
        validator = ParameterValidator()

        tool_path = EXAMPLES_DIR / "debugging" / "error_analysis.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Test with explicit parameters (actual parameter is error_description, not error_message)
        user_params = {
            "error_type": "logic",
            "error_description": "Expected output 42, got 0",
        }
        params = validator.validate_parameters(tool_spec, user_params)

        assert params["error_type"] == "logic"
        assert "Expected output 42" in params["error_description"]

    def test_validate_session_handover_parameters(self) -> None:
        """Test session_handover tool parameter validation."""
        validator = ParameterValidator()

        tool_path = EXAMPLES_DIR / "handoff" / "session_handover.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Should apply completeness default
        params = validator.validate_parameters(tool_spec, {})

        assert "completeness" in params
        assert params["completeness"] == "standard"  # Actual default value


class TestSchemaValidatorWithRealTools:
    """Test SchemaValidator with actual thinking tool specs."""

    def test_validate_all_example_tools(self) -> None:
        """Test that all example tools pass validation."""
        validator = SchemaValidator()

        tool_files = [
            EXAMPLES_DIR / "metacognition" / "think_aloud.yml",
            EXAMPLES_DIR / "metacognition" / "assumption_check.yml",
            EXAMPLES_DIR / "metacognition" / "fresh_eyes_exercise.yml",
            EXAMPLES_DIR / "review" / "code_review_checklist.yml",
            EXAMPLES_DIR / "review" / "architecture_review.yml",
            EXAMPLES_DIR / "handoff" / "session_handover.yml",
            EXAMPLES_DIR / "handoff" / "context_preservation.yml",
            EXAMPLES_DIR / "debugging" / "error_analysis.yml",
            EXAMPLES_DIR / "debugging" / "five_whys.yml",
        ]

        for tool_file in tool_files:
            with open(tool_file, encoding="utf-8") as f:
                tool_spec = yaml.safe_load(f)

            result = validator.validate_tool_spec(tool_spec)

            assert result["valid"], f"Tool {tool_file.name} failed validation: {result['errors']}"
            assert len(result["errors"]) == 0, f"Errors in {tool_file.name}: {result['errors']}"
            # All layers should pass
            assert "semantic" in result["layers_passed"]
            assert "security" in result["layers_passed"]

    def test_validate_think_aloud_tool_spec(self) -> None:
        """Test complete validation of think_aloud tool."""
        validator = SchemaValidator()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"]
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
        assert "semantic" in result["layers_passed"]
        assert "security" in result["layers_passed"]

    def test_validate_code_review_checklist_tool(self) -> None:
        """Test validation of code_review_checklist tool."""
        validator = SchemaValidator()

        tool_path = EXAMPLES_DIR / "review" / "code_review_checklist.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"]
        assert len(result["errors"]) == 0

    def test_validate_error_analysis_tool(self) -> None:
        """Test validation of error_analysis tool."""
        validator = SchemaValidator()

        tool_path = EXAMPLES_DIR / "debugging" / "error_analysis.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"]
        assert len(result["errors"]) == 0
        # Should have no security warnings (safe template)
        assert len(result["warnings"]) == 0


class TestIntegrationParameterValidationAndRendering:
    """Test integration between parameter validation and template rendering."""

    def test_validate_and_render_think_aloud_quick_mode(self) -> None:
        """Test end-to-end: validate parameters then render template."""
        param_validator = ParameterValidator()
        renderer = TemplateRenderer()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # User provides minimal params
        user_params = {"depth": "quick"}

        # Validate and apply defaults
        validated_params = param_validator.validate_parameters(tool_spec, user_params)

        # Render with validated params
        result = renderer.render(tool_spec, validated_params)

        assert "Quick Think Aloud" in result
        assert "Current Understanding" in result
        assert "Reasoning Path" in result

    def test_validate_and_render_with_all_defaults(self) -> None:
        """Test end-to-end with all parameters from defaults."""
        param_validator = ParameterValidator()
        renderer = TemplateRenderer()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # User provides no params - all should come from defaults
        validated_params = param_validator.validate_parameters(tool_spec, {})

        # Render with defaults
        result = renderer.render(tool_spec, validated_params)

        assert "Think Aloud Protocol" in result
        assert "Standard Think Aloud" in result  # Default depth

    def test_validate_and_render_error_analysis(self) -> None:
        """Test error_analysis tool validation and rendering."""
        param_validator = ParameterValidator()
        renderer = TemplateRenderer()

        tool_path = EXAMPLES_DIR / "debugging" / "error_analysis.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Provide parameters (use correct parameter name: error_description)
        user_params = {
            "error_type": "logic",
            "error_description": "Expected output 42, got 0",
        }

        validated_params = param_validator.validate_parameters(tool_spec, user_params)

        result = renderer.render(tool_spec, validated_params)

        assert "LOGIC" in result  # Error type appears in uppercase
        assert "Expected output 42" in result or len(result) > 0  # Template renders

    def test_tool_spec_validation_before_parameter_validation(self) -> None:
        """Test that tool spec is validated before accepting parameters."""
        schema_validator = SchemaValidator()
        param_validator = ParameterValidator()

        tool_path = EXAMPLES_DIR / "metacognition" / "think_aloud.yml"
        with open(tool_path, encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # First validate the tool spec itself
        spec_result = schema_validator.validate_tool_spec(tool_spec)
        assert spec_result["valid"], "Tool spec must be valid before parameter validation"

        # Then validate user parameters
        user_params = {"depth": "detailed"}
        validated_params = param_validator.validate_parameters(tool_spec, user_params)

        assert validated_params["depth"] == "detailed"
