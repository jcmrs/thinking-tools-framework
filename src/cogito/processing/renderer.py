"""Template rendering engine for thinking tools with sandboxed Jinja2 execution.

This module implements Layer 3 (Processing) functionality for secure template
rendering. Uses Jinja2's SandboxedEnvironment to prevent arbitrary code execution
while preserving needed functionality (conditionals, loops, filters).

Architecture: Layer 3 - Processing
Dependencies: None (lowest layer in processing stack)
Security: Defense-in-depth with sandboxing and input validation
"""

from typing import Any

from jinja2 import StrictUndefined
from jinja2.exceptions import TemplateError, TemplateSyntaxError, UndefinedError
from jinja2.sandbox import SandboxedEnvironment


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    def __init__(self, message: str, template_name: str | None = None) -> None:
        """Initialize render error with context.

        Args:
            message: Error description
            template_name: Optional name of template that failed
        """
        self.template_name = template_name
        super().__init__(message)


class TemplateRenderer:
    """Secure template renderer using sandboxed Jinja2 environment.

    Implements PM-002 (Sandboxed Jinja2 Template Engine) design decision:
    - Uses SandboxedEnvironment to prevent arbitrary code execution
    - Strict undefined variable handling (fail fast on missing data)
    - Whitelisted filters only (no dangerous operations)
    - No filesystem access, no imports, no subprocess execution

    Example:
        >>> renderer = TemplateRenderer()
        >>> tool_spec = {
        ...     'metadata': {'name': 'think_aloud'},
        ...     'template': {'source': 'Hello {{ name }}!'}
        ... }
        >>> params = {'name': 'World'}
        >>> result = renderer.render(tool_spec, params)
        >>> print(result)
        Hello World!
    """

    def __init__(self) -> None:
        """Initialize sandboxed Jinja2 environment with security constraints."""
        self._env = SandboxedEnvironment(
            # Fail on undefined variables (strict mode)
            undefined=StrictUndefined,
            # Disable autoescaping (we're generating prompts, not HTML)
            autoescape=False,
            # Keep Python whitespace behavior
            keep_trailing_newline=True,
            trim_blocks=False,
            lstrip_blocks=False,
        )

        # Register safe custom filters (if needed)
        self._register_safe_filters()

    def _register_safe_filters(self) -> None:
        """Register whitelisted Jinja2 filters that are safe to expose.

        Only includes filters that cannot:
        - Access filesystem
        - Execute code
        - Import modules
        - Perform network operations
        """
        # Built-in Jinja2 filters are already available in SandboxedEnvironment
        # Custom filters can be added here if needed
        # Example: self._env.filters['custom_filter'] = safe_custom_filter
        pass

    def render(self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None) -> str:
        """Render thinking tool template with provided parameters.

        Args:
            tool_spec: Complete tool specification from YAML
                      Must contain 'template' key with 'source' subkey
            parameters: Parameter values to substitute in template
                       If None, uses empty dict

        Returns:
            Rendered template as string

        Raises:
            TemplateRenderError: If rendering fails
            ValueError: If tool_spec is missing required keys

        Example:
            >>> tool_spec = {
            ...     'metadata': {'name': 'example'},
            ...     'template': {
            ...         'source': '# {{ title }}\\n\\nDepth: {{ depth }}'
            ...     }
            ... }
            >>> params = {'title': 'Think Aloud', 'depth': 'standard'}
            >>> result = renderer.render(tool_spec, params)
        """
        # Validate tool spec structure
        if "template" not in tool_spec:
            raise ValueError("tool_spec missing 'template' key")

        if "source" not in tool_spec["template"]:
            raise ValueError("tool_spec['template'] missing 'source' key")

        # Extract template source and metadata
        template_source = tool_spec["template"]["source"]
        tool_name = tool_spec.get("metadata", {}).get("name", "unknown")

        # Use empty dict if no parameters provided
        params = parameters or {}

        try:
            # Compile template in sandboxed environment
            template = self._env.from_string(template_source)

            # Render with parameters
            rendered = template.render(**params)

            return rendered

        except UndefinedError as e:
            raise TemplateRenderError(
                f"Undefined variable in template: {e}", template_name=tool_name
            ) from e

        except TemplateSyntaxError as e:
            raise TemplateRenderError(
                f"Template syntax error at line {e.lineno}: {e.message}",
                template_name=tool_name,
            ) from e

        except TemplateError as e:
            raise TemplateRenderError(
                f"Template rendering failed: {e}", template_name=tool_name
            ) from e

    def validate_template_syntax(self, template_source: str) -> bool:
        """Validate template syntax without rendering.

        Useful for schema validation layer (PM-005 Multi-Layer Validation).

        Args:
            template_source: Jinja2 template string to validate

        Returns:
            True if syntax is valid

        Raises:
            TemplateSyntaxError: If template has syntax errors
        """
        try:
            self._env.from_string(template_source)
            return True
        except TemplateSyntaxError:
            raise
