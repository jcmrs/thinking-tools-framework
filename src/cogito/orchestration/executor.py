"""Tool executor coordinating validation and rendering.

Orchestrates the execution pipeline: parameter validation → template rendering.
"""

from typing import Any

from cogito.processing.renderer import TemplateRenderer, TemplateRenderError
from cogito.processing.validator import ParameterValidationError, ParameterValidator


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""

    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        phase: str | None = None,
    ) -> None:
        """Initialize tool execution error with context.

        Args:
            message: Human-readable error message
            tool_name: Name of the tool that failed
            phase: Execution phase where error occurred (validation/rendering)
        """
        self.tool_name = tool_name
        self.phase = phase
        super().__init__(message)


class ToolExecutor:
    """Executes thinking tools by coordinating validation and rendering.

    Orchestrates the execution pipeline:
    1. Parameter validation with defaults (ParameterValidator)
    2. Template rendering (TemplateRenderer)

    Provides comprehensive error handling and reporting for each phase.
    """

    def __init__(
        self,
        parameter_validator: ParameterValidator | None = None,
        template_renderer: TemplateRenderer | None = None,
    ) -> None:
        """Initialize tool executor with validators and renderers.

        Args:
            parameter_validator: Parameter validator instance. If None, creates new.
            template_renderer: Template renderer instance. If None, creates new.
        """
        self._param_validator = parameter_validator or ParameterValidator()
        self._renderer = template_renderer or TemplateRenderer()

    def execute(
        self,
        tool_spec: dict[str, Any],
        parameters: dict[str, Any] | None = None,
    ) -> str:
        """Execute a thinking tool with given parameters.

        Orchestrates the full execution pipeline:
        1. Validates and applies defaults to parameters
        2. Renders template with validated parameters
        3. Returns rendered output

        Args:
            tool_spec: Tool specification dictionary
            parameters: User-provided parameters (may be incomplete)

        Returns:
            Rendered tool output as string

        Raises:
            ToolExecutionError: If execution fails in any phase
        """
        tool_name = tool_spec.get("metadata", {}).get("name", "unknown")

        # Phase 1: Parameter validation and defaults
        try:
            validated_params = self._param_validator.validate_parameters(tool_spec, parameters)
        except ParameterValidationError as e:
            raise ToolExecutionError(
                f"Parameter validation failed: {e}",
                tool_name=tool_name,
                phase="validation",
            ) from e
        except Exception as e:
            raise ToolExecutionError(
                f"Unexpected error during parameter validation: {e}",
                tool_name=tool_name,
                phase="validation",
            ) from e

        # Phase 2: Template rendering
        try:
            rendered = self._renderer.render(tool_spec, validated_params)
            return rendered
        except TemplateRenderError as e:
            raise ToolExecutionError(
                f"Template rendering failed: {e}",
                tool_name=tool_name,
                phase="rendering",
            ) from e
        except Exception as e:
            raise ToolExecutionError(
                f"Unexpected error during template rendering: {e}",
                tool_name=tool_name,
                phase="rendering",
            ) from e

    def execute_by_name(
        self,
        tool_name: str,
        tool_registry: Any,  # ToolRegistry type, avoiding circular import
        parameters: dict[str, Any] | None = None,
    ) -> str:
        """Execute a tool by name from a registry.

        Convenience method that looks up tool from registry and executes it.

        Args:
            tool_name: Name of the tool to execute
            tool_registry: ToolRegistry instance to look up tool
            parameters: User-provided parameters

        Returns:
            Rendered tool output

        Raises:
            ToolExecutionError: If tool not found or execution fails
        """
        tool_spec = tool_registry.get_tool(tool_name)
        if tool_spec is None:
            raise ToolExecutionError(
                f"Tool '{tool_name}' not found in registry",
                tool_name=tool_name,
                phase="lookup",
            )

        return self.execute(tool_spec, parameters)
