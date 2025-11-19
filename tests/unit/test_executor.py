"""Unit tests for ToolExecutor class.

Tests execution pipeline coordinating ParameterValidator and TemplateRenderer.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from cogito.orchestration.executor import ToolExecutionError, ToolExecutor
from cogito.processing.renderer import TemplateRenderError
from cogito.processing.validator import ParameterValidationError


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
        "template": {"source": "Test template: {{ param1 }}"},
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "default": "default_value"}
            },
        },
    }


@pytest.fixture
def tool_with_required_params() -> dict[str, Any]:
    """Tool spec with required parameters."""
    return {
        "metadata": {
            "name": "required_tool",
            "display_name": "Required Tool",
            "description": "Tool with required params",
            "category": "test",
            "version": "1.0.0",
        },
        "template": {"source": "Value: {{ value }}"},
        "parameters": {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    }


class TestToolExecutorInit:
    """Test ToolExecutor initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default validators/renderers."""
        executor = ToolExecutor()
        assert executor._param_validator is not None
        assert executor._renderer is not None

    def test_init_with_custom_validator(self) -> None:
        """Test initialization with custom parameter validator."""
        mock_validator = MagicMock()
        executor = ToolExecutor(parameter_validator=mock_validator)
        assert executor._param_validator is mock_validator

    def test_init_with_custom_renderer(self) -> None:
        """Test initialization with custom template renderer."""
        mock_renderer = MagicMock()
        executor = ToolExecutor(template_renderer=mock_renderer)
        assert executor._renderer is mock_renderer

    def test_init_with_both_custom(self) -> None:
        """Test initialization with both custom components."""
        mock_validator = MagicMock()
        mock_renderer = MagicMock()
        executor = ToolExecutor(
            parameter_validator=mock_validator, template_renderer=mock_renderer
        )
        assert executor._param_validator is mock_validator
        assert executor._renderer is mock_renderer


class TestToolExecutorExecute:
    """Test execute() method."""

    def test_execute_with_valid_parameters(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test successful execution with valid parameters."""
        executor = ToolExecutor()
        result = executor.execute(minimal_tool_spec, {"param1": "custom_value"})

        assert "custom_value" in result
        assert isinstance(result, str)

    def test_execute_with_no_parameters(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test execution with no parameters applies defaults."""
        executor = ToolExecutor()
        result = executor.execute(minimal_tool_spec, None)

        assert "default_value" in result

    def test_execute_with_empty_parameters(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test execution with empty dict applies defaults."""
        executor = ToolExecutor()
        result = executor.execute(minimal_tool_spec, {})

        assert "default_value" in result

    def test_execute_validation_phase_error(
        self, tool_with_required_params: dict[str, Any]
    ) -> None:
        """Test that validation errors are wrapped in ToolExecutionError."""
        executor = ToolExecutor()

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(tool_with_required_params, {})

        assert exc_info.value.tool_name == "required_tool"
        assert exc_info.value.phase == "validation"
        assert "parameter validation failed" in str(exc_info.value).lower()

    def test_execute_validation_unexpected_error(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that unexpected validation errors are wrapped."""
        executor = ToolExecutor()

        # Mock validator to raise unexpected error
        executor._param_validator = MagicMock()
        executor._param_validator.validate_parameters.side_effect = RuntimeError(
            "Unexpected error"
        )

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(minimal_tool_spec, {})

        assert exc_info.value.tool_name == "test_tool"
        assert exc_info.value.phase == "validation"
        assert "unexpected error during parameter validation" in str(
            exc_info.value
        ).lower()

    def test_execute_rendering_phase_error(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that rendering errors are wrapped in ToolExecutionError."""
        executor = ToolExecutor()

        # Mock renderer to raise TemplateRenderError
        executor._renderer = MagicMock()
        executor._renderer.render.side_effect = TemplateRenderError("Render failed")

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(minimal_tool_spec, {})

        assert exc_info.value.tool_name == "test_tool"
        assert exc_info.value.phase == "rendering"
        assert "template rendering failed" in str(exc_info.value).lower()

    def test_execute_rendering_unexpected_error(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that unexpected rendering errors are wrapped."""
        executor = ToolExecutor()

        # Mock renderer to raise unexpected error
        executor._renderer = MagicMock()
        executor._renderer.render.side_effect = RuntimeError("Unexpected render error")

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(minimal_tool_spec, {})

        assert exc_info.value.tool_name == "test_tool"
        assert exc_info.value.phase == "rendering"
        assert "unexpected error during template rendering" in str(
            exc_info.value
        ).lower()

    def test_execute_tool_without_name(self) -> None:
        """Test execution with tool missing metadata.name uses 'unknown'."""
        tool_spec = {
            "metadata": {},
            "template": {"source": "Test output"},
        }
        executor = ToolExecutor()

        # Should successfully execute and use "unknown" as tool name if error occurs
        result = executor.execute(tool_spec, {})
        assert "Test output" in result

        # Verify error uses "unknown" when tool name is missing
        executor._renderer = MagicMock()
        executor._renderer.render.side_effect = TemplateRenderError("Render failed")

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(tool_spec, {})

        assert exc_info.value.tool_name == "unknown"

    def test_execute_preserves_exception_chain(
        self, tool_with_required_params: dict[str, Any]
    ) -> None:
        """Test that original exceptions are preserved in chain."""
        executor = ToolExecutor()

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute(tool_with_required_params, {})

        # Check exception chain
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ParameterValidationError)

    def test_execute_calls_validator_before_renderer(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that validator is called before renderer."""
        call_order = []

        mock_validator = MagicMock()
        mock_validator.validate_parameters.side_effect = (
            lambda spec, params: call_order.append("validator") or {"param1": "value"}
        )

        mock_renderer = MagicMock()
        mock_renderer.render.side_effect = (
            lambda spec, params: call_order.append("renderer") or "result"
        )

        executor = ToolExecutor(
            parameter_validator=mock_validator, template_renderer=mock_renderer
        )
        executor.execute(minimal_tool_spec, {})

        assert call_order == ["validator", "renderer"]


class TestToolExecutorExecuteByName:
    """Test execute_by_name() method."""

    def test_execute_by_name_success(self, minimal_tool_spec: dict[str, Any]) -> None:
        """Test successful execution by tool name."""
        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = minimal_tool_spec

        executor = ToolExecutor()
        result = executor.execute_by_name("test_tool", mock_registry, {})

        assert "default_value" in result
        mock_registry.get_tool.assert_called_once_with("test_tool")

    def test_execute_by_name_tool_not_found(self) -> None:
        """Test execution by name when tool not in registry."""
        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = None

        executor = ToolExecutor()

        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute_by_name("nonexistent_tool", mock_registry, {})

        assert exc_info.value.tool_name == "nonexistent_tool"
        assert exc_info.value.phase == "lookup"
        assert "not found in registry" in str(exc_info.value).lower()

    def test_execute_by_name_with_parameters(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test execution by name with custom parameters."""
        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = minimal_tool_spec

        executor = ToolExecutor()
        result = executor.execute_by_name(
            "test_tool", mock_registry, {"param1": "custom"}
        )

        assert "custom" in result

    def test_execute_by_name_delegates_to_execute(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test that execute_by_name delegates to execute()."""
        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = minimal_tool_spec

        executor = ToolExecutor()

        # Mock the execute method to verify it's called
        original_execute = executor.execute
        executor.execute = MagicMock(return_value="mocked_result")

        result = executor.execute_by_name("test_tool", mock_registry, {"key": "value"})

        executor.execute.assert_called_once_with(minimal_tool_spec, {"key": "value"})
        assert result == "mocked_result"


class TestToolExecutionError:
    """Test ToolExecutionError exception class."""

    def test_error_with_all_fields(self) -> None:
        """Test error with all optional fields."""
        error = ToolExecutionError(
            "Test error", tool_name="my_tool", phase="validation"
        )

        assert str(error) == "Test error"
        assert error.tool_name == "my_tool"
        assert error.phase == "validation"

    def test_error_with_minimal_fields(self) -> None:
        """Test error with only required message."""
        error = ToolExecutionError("Test error")

        assert str(error) == "Test error"
        assert error.tool_name is None
        assert error.phase is None

    def test_error_is_exception_subclass(self) -> None:
        """Test that ToolExecutionError is an Exception."""
        error = ToolExecutionError("Test")
        assert isinstance(error, Exception)


class TestToolExecutorIntegration:
    """Integration tests with real ParameterValidator and TemplateRenderer."""

    def test_full_pipeline_with_defaults(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test full execution pipeline with default values."""
        executor = ToolExecutor()
        result = executor.execute(minimal_tool_spec, {})

        assert "Test template:" in result
        assert "default_value" in result

    def test_full_pipeline_with_custom_params(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test full execution pipeline with custom parameters."""
        executor = ToolExecutor()
        result = executor.execute(minimal_tool_spec, {"param1": "my_custom_value"})

        assert "Test template:" in result
        assert "my_custom_value" in result

    def test_full_pipeline_parameter_validation_failure(
        self, tool_with_required_params: dict[str, Any]
    ) -> None:
        """Test that parameter validation failures prevent rendering."""
        executor = ToolExecutor()

        # Mock renderer to track if it was called
        executor._renderer = MagicMock()

        with pytest.raises(ToolExecutionError):
            executor.execute(tool_with_required_params, {})

        # Renderer should not be called if validation fails
        executor._renderer.render.assert_not_called()

    def test_full_pipeline_with_complex_template(self) -> None:
        """Test execution with more complex Jinja2 template."""
        tool_spec = {
            "metadata": {
                "name": "complex_tool",
                "display_name": "Complex Tool",
                "description": "Complex template",
                "category": "test",
                "version": "1.0.0",
            },
            "template": {
                "source": """
# {{ title }}

{% if show_details %}
Details: {{ details }}
{% else %}
No details provided
{% endif %}

Count: {{ count }}
"""
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Default Title"},
                    "show_details": {"type": "boolean", "default": False},
                    "details": {"type": "string", "default": ""},
                    "count": {"type": "integer", "default": 0},
                },
            },
        }

        executor = ToolExecutor()
        result = executor.execute(
            tool_spec, {"title": "My Title", "show_details": True, "details": "Info"}
        )

        assert "My Title" in result
        assert "Details: Info" in result
        assert "Count: 0" in result

    def test_full_pipeline_with_registry_lookup(
        self, minimal_tool_spec: dict[str, Any]
    ) -> None:
        """Test full pipeline using registry lookup."""
        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = minimal_tool_spec

        executor = ToolExecutor()
        result = executor.execute_by_name(
            "test_tool", mock_registry, {"param1": "registry_test"}
        )

        assert "registry_test" in result
