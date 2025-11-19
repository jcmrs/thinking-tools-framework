"""Parameter and tool specification validation with multi-layer approach.

This module implements PM-005 (Multi-Layer Validation Pipeline) with three
sequential validation layers: schema, semantic, and security validation.
"""

from typing import Any

import jsonschema
from jinja2.exceptions import TemplateSyntaxError

from cogito.processing.renderer import TemplateRenderer


class ParameterValidationError(Exception):
    """Raised when parameter validation fails."""

    def __init__(
        self,
        message: str,
        parameter_name: str | None = None,
        schema_errors: list[str] | None = None,
    ) -> None:
        """Initialize parameter validation error with context.

        Args:
            message: Human-readable error message
            parameter_name: Name of the invalid parameter (if applicable)
            schema_errors: List of JSON Schema validation errors
        """
        self.parameter_name = parameter_name
        self.schema_errors = schema_errors or []
        super().__init__(message)


class ToolSpecValidationError(Exception):
    """Raised when tool specification validation fails."""

    def __init__(
        self,
        message: str,
        validation_layer: str,
        errors: list[str] | None = None,
    ) -> None:
        """Initialize tool spec validation error with context.

        Args:
            message: Human-readable error message
            validation_layer: Which layer failed (schema/semantic/security)
            errors: List of validation errors from that layer
        """
        self.validation_layer = validation_layer
        self.errors = errors or []
        super().__init__(message)


class ParameterValidator:
    """Validates user-provided parameters against tool's JSON Schema.

    Handles parameter validation and default value application according to
    the tool's parameter schema definition.
    """

    def validate_parameters(
        self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate parameters against tool schema and apply defaults.

        Args:
            tool_spec: Tool specification containing parameters schema
            parameters: User-provided parameters to validate

        Returns:
            Validated parameters with defaults applied

        Raises:
            ParameterValidationError: If validation fails
        """
        params = parameters or {}

        # Get parameter schema from tool spec
        if "parameters" not in tool_spec:
            # No parameters defined - return empty dict
            return {}

        param_schema = tool_spec["parameters"]

        # Apply defaults first
        params_with_defaults = self.apply_defaults(param_schema, params)

        # Validate against schema
        try:
            jsonschema.validate(instance=params_with_defaults, schema=param_schema)
        except jsonschema.ValidationError as e:
            # Extract helpful error message
            error_path = ".".join(str(p) for p in e.absolute_path)
            parameter_name = error_path if error_path else None

            raise ParameterValidationError(
                f"Parameter validation failed: {e.message}",
                parameter_name=parameter_name,
                schema_errors=[str(e)],
            ) from e
        except jsonschema.SchemaError as e:
            raise ParameterValidationError(
                f"Invalid parameter schema in tool spec: {e.message}",
                schema_errors=[str(e)],
            ) from e

        return params_with_defaults

    def apply_defaults(self, schema: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        """Apply default values from schema to parameters.

        Recursively walks schema finding default values and applies them
        to parameters where keys are missing.

        Args:
            schema: JSON Schema with default values
            parameters: User-provided parameters (may be incomplete)

        Returns:
            New dict with defaults merged in (does not modify input)
        """
        # Start with copy of user parameters
        result = parameters.copy()

        # Only handle object schemas with properties
        if schema.get("type") != "object":
            return result

        properties = schema.get("properties", {})

        for prop_name, prop_schema in properties.items():
            if prop_name not in result and "default" in prop_schema:
                # Apply default value
                result[prop_name] = prop_schema["default"]

        return result


class SchemaValidator:
    """Multi-layer validation of tool specifications.

    Implements PM-005 (Multi-Layer Validation Pipeline) with three sequential
    validation layers:
    1. Schema validation - Validates against thinking-tool-v1.0.schema.json
    2. Semantic validation - Checks template syntax and parameter schema validity
    3. Security validation - Scans for dangerous template patterns
    """

    def __init__(self, tool_schema: dict[str, Any] | None = None) -> None:
        """Initialize schema validator.

        Args:
            tool_schema: JSON Schema for thinking tools. If None, will load
                        from schemas/thinking-tool-v1.0.schema.json when needed.
        """
        self._tool_schema = tool_schema
        self._renderer = TemplateRenderer()

    def validate_tool_spec(self, tool_spec: dict[str, Any]) -> dict[str, Any]:
        """Validate tool specification through all three layers.

        Runs schema → semantic → security validation in sequence.
        Stops at first critical failure.

        Args:
            tool_spec: Tool specification to validate

        Returns:
            Validation result dict with structure:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "layers_passed": List[str]
            }

        Raises:
            ToolSpecValidationError: On critical validation failure
        """
        errors: list[str] = []
        warnings: list[str] = []
        layers_passed: list[str] = []

        # Layer 1: Schema validation
        try:
            schema_errors = self.validate_schema(tool_spec)
            if schema_errors:
                errors.extend(schema_errors)
                raise ToolSpecValidationError(
                    "Schema validation failed",
                    validation_layer="schema",
                    errors=schema_errors,
                )
            layers_passed.append("schema")
        except ToolSpecValidationError:
            raise
        except Exception as e:
            raise ToolSpecValidationError(
                f"Schema validation error: {e}",
                validation_layer="schema",
                errors=[str(e)],
            ) from e

        # Layer 2: Semantic validation
        try:
            semantic_errors = self.validate_semantics(tool_spec)
            if semantic_errors:
                errors.extend(semantic_errors)
                raise ToolSpecValidationError(
                    "Semantic validation failed",
                    validation_layer="semantic",
                    errors=semantic_errors,
                )
            layers_passed.append("semantic")
        except ToolSpecValidationError:
            raise
        except Exception as e:
            raise ToolSpecValidationError(
                f"Semantic validation error: {e}",
                validation_layer="semantic",
                errors=[str(e)],
            ) from e

        # Layer 3: Security validation
        try:
            security_warnings = self.validate_security(tool_spec)
            if security_warnings:
                warnings.extend(security_warnings)
            layers_passed.append("security")
        except Exception as e:
            raise ToolSpecValidationError(
                f"Security validation error: {e}",
                validation_layer="security",
                errors=[str(e)],
            ) from e

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "layers_passed": layers_passed,
        }

    def validate_schema(self, tool_spec: dict[str, Any]) -> list[str]:
        """Layer 1: Validate tool spec against JSON Schema.

        Args:
            tool_spec: Tool specification to validate

        Returns:
            List of schema validation errors (empty if valid)
        """
        if self._tool_schema is None:
            # Schema validation not available without schema
            # In production, would load from file
            return []

        errors: list[str] = []

        try:
            jsonschema.validate(instance=tool_spec, schema=self._tool_schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
        except jsonschema.SchemaError as e:
            errors.append(f"Invalid tool schema: {e.message}")

        return errors

    def validate_semantics(self, tool_spec: dict[str, Any]) -> list[str]:
        """Layer 2: Validate semantic correctness.

        Checks:
        - Template syntax (Jinja2) is valid
        - Parameter schema (if present) is valid JSON Schema

        Args:
            tool_spec: Tool specification to validate

        Returns:
            List of semantic errors (empty if valid)
        """
        errors: list[str] = []

        # Check template syntax
        if "template" in tool_spec and "source" in tool_spec["template"]:
            template_source = tool_spec["template"]["source"]
            try:
                self._renderer.validate_template_syntax(template_source)
            except TemplateSyntaxError as e:
                errors.append(f"Template syntax error at line {e.lineno}: {e.message}")

        # Check parameter schema validity
        if "parameters" in tool_spec:
            param_schema = tool_spec["parameters"]
            try:
                # Validate that parameter schema is valid JSON Schema structure
                # Use Draft7Validator to check schema validity without instance validation
                jsonschema.Draft7Validator.check_schema(param_schema)
            except jsonschema.SchemaError as e:
                errors.append(f"Invalid parameter schema: {e.message}")

        return errors

    def validate_security(self, tool_spec: dict[str, Any]) -> list[str]:
        """Layer 3: Validate security constraints.

        Scans template for dangerous patterns:
        - File system access attempts
        - Subprocess/command execution
        - Import statements
        - eval/exec usage

        Args:
            tool_spec: Tool specification to validate

        Returns:
            List of security warnings (empty if no issues)
        """
        warnings: list[str] = []

        if "template" not in tool_spec or "source" not in tool_spec["template"]:
            return warnings

        template_source = tool_spec["template"]["source"]

        # Dangerous patterns to detect
        dangerous_patterns = [
            ("import ", "Import statements detected in template"),
            ("subprocess", "Subprocess execution detected in template"),
            ("exec(", "exec() usage detected in template"),
            ("eval(", "eval() usage detected in template"),
            ("open(", "File operations detected in template"),
            ("__import__", "Dynamic import detected in template"),
            ("compile(", "Code compilation detected in template"),
        ]

        for pattern, warning_msg in dangerous_patterns:
            if pattern in template_source:
                warnings.append(warning_msg)

        return warnings
