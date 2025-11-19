"""Unit tests for parameter and tool spec validation."""

from typing import Any

import pytest

from cogito.processing.validator import (
    ParameterValidationError,
    ParameterValidator,
    SchemaValidator,
    ToolSpecValidationError,
)


class TestParameterValidatorBasics:
    """Test basic parameter validation functionality."""

    def test_validate_empty_parameters(self) -> None:
        """Test validation with no parameters defined."""
        validator = ParameterValidator()
        tool_spec: dict[str, Any] = {"metadata": {"name": "test"}}

        result = validator.validate_parameters(tool_spec, {})

        assert result == {}

    def test_validate_with_no_user_params(self) -> None:
        """Test validation when user provides None."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "default": "guest"}},
            }
        }

        result = validator.validate_parameters(tool_spec, None)

        assert result == {"name": "guest"}

    def test_validate_simple_valid_parameters(self) -> None:
        """Test validation with simple valid parameters."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        }
        params = {"name": "Alice"}

        result = validator.validate_parameters(tool_spec, params)

        assert result == {"name": "Alice"}

    def test_validate_missing_required_parameter(self) -> None:
        """Test validation fails on missing required parameter."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }
        }
        params = {}

        with pytest.raises(ParameterValidationError) as exc_info:
            validator.validate_parameters(tool_spec, params)

        assert "'name' is a required property" in str(exc_info.value)
        # parameter_name may be None for required property errors
        assert len(exc_info.value.schema_errors) > 0

    def test_validate_wrong_type(self) -> None:
        """Test validation fails on wrong parameter type."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {"age": {"type": "integer"}},
            }
        }
        params = {"age": "twenty"}

        with pytest.raises(ParameterValidationError) as exc_info:
            validator.validate_parameters(tool_spec, params)

        assert "is not of type" in str(exc_info.value)


class TestParameterValidatorDefaults:
    """Test default value application."""

    def test_apply_default_string(self) -> None:
        """Test applying default string value."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string", "default": "guest"}},
        }
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {"name": "guest"}

    def test_apply_default_integer(self) -> None:
        """Test applying default integer value."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {"count": {"type": "integer", "default": 5}},
        }
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {"count": 5}

    def test_apply_default_boolean(self) -> None:
        """Test applying default boolean value."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {"enabled": {"type": "boolean", "default": True}},
        }
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {"enabled": True}

    def test_apply_multiple_defaults(self) -> None:
        """Test applying multiple default values."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "guest"},
                "age": {"type": "integer", "default": 0},
                "active": {"type": "boolean", "default": False},
            },
        }
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {"name": "guest", "age": 0, "active": False}

    def test_user_value_overrides_default(self) -> None:
        """Test that user-provided value overrides default."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string", "default": "guest"}},
        }
        params = {"name": "Alice"}

        result = validator.apply_defaults(schema, params)

        assert result == {"name": "Alice"}

    def test_partial_defaults_application(self) -> None:
        """Test applying defaults for missing keys only."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "guest"},
                "age": {"type": "integer", "default": 0},
            },
        }
        params = {"name": "Alice"}

        result = validator.apply_defaults(schema, params)

        assert result == {"name": "Alice", "age": 0}

    def test_no_defaults_defined(self) -> None:
        """Test schema with no default values."""
        validator = ParameterValidator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {}

    def test_non_object_schema(self) -> None:
        """Test that non-object schemas return unchanged parameters."""
        validator = ParameterValidator()
        schema = {"type": "string"}
        params = {}

        result = validator.apply_defaults(schema, params)

        assert result == {}


class TestParameterValidatorEnums:
    """Test enum validation."""

    def test_validate_enum_value(self) -> None:
        """Test validation with enum constraint."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["low", "medium", "high"]}
                },
            }
        }
        params = {"level": "medium"}

        result = validator.validate_parameters(tool_spec, params)

        assert result == {"level": "medium"}

    def test_validate_invalid_enum_value(self) -> None:
        """Test validation fails on invalid enum value."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["low", "medium", "high"]}
                },
            }
        }
        params = {"level": "extreme"}

        with pytest.raises(ParameterValidationError) as exc_info:
            validator.validate_parameters(tool_spec, params)

        assert "is not one of" in str(exc_info.value)

    def test_enum_with_default(self) -> None:
        """Test enum parameter with default value."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "detailed"],
                        "default": "standard",
                    }
                },
            }
        }
        params = {}

        result = validator.validate_parameters(tool_spec, params)

        assert result == {"depth": "standard"}


class TestSchemaValidatorBasics:
    """Test basic schema validator functionality."""

    def test_validate_minimal_tool_spec(self) -> None:
        """Test validation of minimal tool spec."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test", "description": "Test tool"},
            "template": {"source": "Hello {{ name }}!"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "semantic" in result["layers_passed"]

    def test_validate_tool_with_parameters(self) -> None:
        """Test validation of tool with parameters."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
            "template": {"source": "Hello {{ name }}!"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"] is True


class TestSchemaValidatorSemantics:
    """Test semantic validation layer."""

    def test_invalid_template_syntax(self) -> None:
        """Test detection of invalid Jinja2 syntax."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{% if x %} broken"},  # Missing endif
        }

        with pytest.raises(ToolSpecValidationError) as exc_info:
            validator.validate_tool_spec(tool_spec)

        assert exc_info.value.validation_layer == "semantic"
        # Check errors list for syntax error details
        assert len(exc_info.value.errors) > 0
        assert "syntax error" in exc_info.value.errors[0].lower()

    def test_valid_template_conditionals(self) -> None:
        """Test valid template with conditionals."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {
                "source": "{% if x %}Hello{% else %}Goodbye{% endif %}"
            },
        }

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"] is True

    def test_valid_template_loops(self) -> None:
        """Test valid template with loops."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {
                "source": "{% for item in items %}{{ item }}{% endfor %}"
            },
        }

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"] is True

    def test_invalid_parameter_schema(self) -> None:
        """Test detection of invalid JSON Schema in parameters."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "parameters": {
                "type": "invalid_type",  # Invalid JSON Schema type
            },
            "template": {"source": "Test"},
        }

        # This should fail semantic validation
        with pytest.raises(ToolSpecValidationError) as exc_info:
            validator.validate_tool_spec(tool_spec)

        assert exc_info.value.validation_layer == "semantic"


class TestSchemaValidatorSecurity:
    """Test security validation layer."""

    def test_detect_import_statement(self) -> None:
        """Test detection of import statements."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "import os\n{{ name }}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        # Security warnings don't fail validation, but are reported
        assert "Import statements detected" in str(result["warnings"])

    def test_detect_subprocess(self) -> None:
        """Test detection of subprocess usage."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{{ subprocess.call('ls') }}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "Subprocess execution detected" in str(result["warnings"])

    def test_detect_exec(self) -> None:
        """Test detection of exec() usage."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{% set x = exec('print(1)') %}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "exec() usage detected" in str(result["warnings"])

    def test_detect_eval(self) -> None:
        """Test detection of eval() usage."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{{ eval('1+1') }}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "eval() usage detected" in str(result["warnings"])

    def test_detect_file_operations(self) -> None:
        """Test detection of file operations."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{% set f = open('/etc/passwd') %}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "File operations detected" in str(result["warnings"])

    def test_detect_dynamic_import(self) -> None:
        """Test detection of dynamic imports."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{{ __import__('os').system('ls') }}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "Dynamic import detected" in str(result["warnings"])

    def test_detect_compile(self) -> None:
        """Test detection of code compilation."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{% set code = compile('x=1', '<string>', 'exec') %}"},
        }

        result = validator.validate_tool_spec(tool_spec)

        assert "Code compilation detected" in str(result["warnings"])

    def test_safe_template_no_warnings(self) -> None:
        """Test that safe templates generate no security warnings."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {
                "source": "Hello {{ name }}!\n{% if x %}Conditional{% endif %}"
            },
        }

        result = validator.validate_tool_spec(tool_spec)

        assert len(result["warnings"]) == 0
        assert "security" in result["layers_passed"]


class TestSchemaValidatorMultiLayer:
    """Test multi-layer validation integration."""

    def test_all_layers_pass(self) -> None:
        """Test tool that passes all validation layers."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test", "description": "Test"},
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "default": "user"}},
            },
            "template": {
                "source": "Hello {{ name }}!\n{% if name %}Welcome{% endif %}"
            },
        }

        result = validator.validate_tool_spec(tool_spec)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert set(result["layers_passed"]) == {"schema", "semantic", "security"}

    def test_fails_at_semantic_layer(self) -> None:
        """Test validation stops at semantic layer failure."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "{% if x %} broken"},  # Invalid syntax
        }

        with pytest.raises(ToolSpecValidationError) as exc_info:
            validator.validate_tool_spec(tool_spec)

        assert exc_info.value.validation_layer == "semantic"
        # Should not reach security layer
        assert "security" not in str(exc_info.value)

    def test_security_warnings_dont_fail_validation(self) -> None:
        """Test that security warnings don't cause validation failure."""
        validator = SchemaValidator()
        tool_spec = {
            "metadata": {"name": "test"},
            "template": {"source": "import os\n{{ name }}"},  # Security warning
        }

        result = validator.validate_tool_spec(tool_spec)

        # Valid despite security warnings
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert "security" in result["layers_passed"]


class TestParameterValidatorIntegration:
    """Test integration between parameter validator and real tool specs."""

    def test_validate_think_aloud_parameters(self) -> None:
        """Test validation with think_aloud tool parameters."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "detailed"],
                        "default": "standard",
                    },
                    "focus": {"type": "string", "default": ""},
                },
                "required": [],
            }
        }

        # Test with no parameters - should apply defaults
        result = validator.validate_parameters(tool_spec, {})
        assert result == {"depth": "standard", "focus": ""}

        # Test with explicit depth
        result = validator.validate_parameters(tool_spec, {"depth": "detailed"})
        assert result == {"depth": "detailed", "focus": ""}

        # Test with both parameters
        result = validator.validate_parameters(
            tool_spec, {"depth": "quick", "focus": "algorithm choice"}
        )
        assert result == {"depth": "quick", "focus": "algorithm choice"}

    def test_validate_invalid_enum_value_for_depth(self) -> None:
        """Test validation fails on invalid depth value."""
        validator = ParameterValidator()
        tool_spec = {
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "detailed"],
                    }
                },
            }
        }
        params = {"depth": "extreme"}

        with pytest.raises(ParameterValidationError):
            validator.validate_parameters(tool_spec, params)
