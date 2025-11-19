"""Unit tests for TemplateRenderer.

Tests the core template rendering functionality with sandboxed Jinja2 environment.
Covers basic rendering, parameter substitution, conditionals, loops, error handling,
and security constraints.
"""

import pytest
from jinja2.exceptions import TemplateSyntaxError

from cogito.processing import TemplateRenderer, TemplateRenderError


class TestTemplateRendererBasics:
    """Test basic template rendering functionality."""

    def test_simple_text_rendering(self) -> None:
        """Test rendering template with no variables."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "simple"},
            "template": {"source": "Hello World!"},
        }

        result = renderer.render(tool_spec)

        assert result == "Hello World!"

    def test_single_variable_substitution(self) -> None:
        """Test rendering template with single variable substitution."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "greeting"},
            "template": {"source": "Hello {{ name }}!"},
        }
        params = {"name": "Alice"}

        result = renderer.render(tool_spec, params)

        assert result == "Hello Alice!"

    def test_multiple_variable_substitution(self) -> None:
        """Test rendering template with multiple variables."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "multi_var"},
            "template": {
                "source": "Name: {{ name }}\nAge: {{ age }}\nCity: {{ city }}"
            },
        }
        params = {"name": "Bob", "age": "30", "city": "NYC"}

        result = renderer.render(tool_spec, params)

        assert "Name: Bob" in result
        assert "Age: 30" in result
        assert "City: NYC" in result

    def test_empty_parameters_dict(self) -> None:
        """Test rendering with explicitly empty parameters dict."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "no_params"},
            "template": {"source": "Static content"},
        }

        result = renderer.render(tool_spec, {})

        assert result == "Static content"

    def test_none_parameters_treated_as_empty(self) -> None:
        """Test that None parameters is treated as empty dict."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "none_params"},
            "template": {"source": "Static content"},
        }

        result = renderer.render(tool_spec, None)

        assert result == "Static content"


class TestTemplateRendererConditionals:
    """Test conditional logic ({% if %}) in templates."""

    def test_if_condition_true(self) -> None:
        """Test rendering when if condition evaluates to true."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "conditional"},
            "template": {
                "source": "{% if show_message %}Hello!{% endif %}"
            },
        }
        params = {"show_message": True}

        result = renderer.render(tool_spec, params)

        assert "Hello!" in result

    def test_if_condition_false(self) -> None:
        """Test rendering when if condition evaluates to false."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "conditional"},
            "template": {
                "source": "{% if show_message %}Hello!{% endif %}"
            },
        }
        params = {"show_message": False}

        result = renderer.render(tool_spec, params)

        assert "Hello!" not in result

    def test_if_else_branches(self) -> None:
        """Test rendering with if-else branches."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "if_else"},
            "template": {
                "source": "{% if premium %}Premium{% else %}Free{% endif %}"
            },
        }

        result_premium = renderer.render(tool_spec, {"premium": True})
        result_free = renderer.render(tool_spec, {"premium": False})

        assert result_premium == "Premium"
        assert result_free == "Free"

    def test_if_elif_else_branches(self) -> None:
        """Test rendering with if-elif-else branches."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "multi_branch"},
            "template": {
                "source": (
                    "{% if level == 'high' %}High"
                    "{% elif level == 'medium' %}Medium"
                    "{% else %}Low{% endif %}"
                )
            },
        }

        assert renderer.render(tool_spec, {"level": "high"}) == "High"
        assert renderer.render(tool_spec, {"level": "medium"}) == "Medium"
        assert renderer.render(tool_spec, {"level": "low"}) == "Low"


class TestTemplateRendererLoops:
    """Test loop logic ({% for %}) in templates."""

    def test_for_loop_over_list(self) -> None:
        """Test rendering with for loop over list."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "loop"},
            "template": {
                "source": "{% for item in items %}- {{ item }}\n{% endfor %}"
            },
        }
        params = {"items": ["apple", "banana", "cherry"]}

        result = renderer.render(tool_spec, params)

        assert "- apple" in result
        assert "- banana" in result
        assert "- cherry" in result

    def test_for_loop_empty_list(self) -> None:
        """Test rendering for loop with empty list."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "empty_loop"},
            "template": {
                "source": "{% for item in items %}- {{ item }}\n{% endfor %}"
            },
        }
        params = {"items": []}

        result = renderer.render(tool_spec, params)

        # Should produce empty output (no iterations)
        assert result.strip() == ""

    def test_for_loop_with_index(self) -> None:
        """Test for loop with loop.index variable."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "indexed_loop"},
            "template": {
                "source": (
                    "{% for item in items %}"
                    "{{ loop.index }}. {{ item }}\n"
                    "{% endfor %}"
                )
            },
        }
        params = {"items": ["first", "second", "third"]}

        result = renderer.render(tool_spec, params)

        assert "1. first" in result
        assert "2. second" in result
        assert "3. third" in result


class TestTemplateRendererFilters:
    """Test Jinja2 built-in filters."""

    def test_upper_filter(self) -> None:
        """Test upper case filter."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "upper"},
            "template": {"source": "{{ text|upper }}"},
        }
        params = {"text": "hello"}

        result = renderer.render(tool_spec, params)

        assert result == "HELLO"

    def test_lower_filter(self) -> None:
        """Test lower case filter."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "lower"},
            "template": {"source": "{{ text|lower }}"},
        }
        params = {"text": "WORLD"}

        result = renderer.render(tool_spec, params)

        assert result == "world"

    def test_default_filter_with_value(self) -> None:
        """Test default filter when value is provided."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "default"},
            "template": {"source": "{{ name|default('Guest') }}"},
        }
        params = {"name": "Alice"}

        result = renderer.render(tool_spec, params)

        assert result == "Alice"

    def test_default_filter_without_value(self) -> None:
        """Test default filter when value is not provided."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "default"},
            "template": {"source": "{{ name|default('Guest') }}"},
        }
        params = {}

        # The default filter works even with StrictUndefined
        result = renderer.render(tool_spec, params)

        assert result == "Guest"


class TestTemplateRendererErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_template_key_raises_value_error(self) -> None:
        """Test that missing 'template' key raises ValueError."""
        renderer = TemplateRenderer()
        tool_spec = {"metadata": {"name": "broken"}}

        with pytest.raises(ValueError, match="tool_spec missing 'template' key"):
            renderer.render(tool_spec)

    def test_missing_source_key_raises_value_error(self) -> None:
        """Test that missing 'source' key raises ValueError."""
        renderer = TemplateRenderer()
        tool_spec = {"metadata": {"name": "broken"}, "template": {}}

        with pytest.raises(ValueError, match="missing 'source' key"):
            renderer.render(tool_spec)

    def test_undefined_variable_raises_render_error(self) -> None:
        """Test that undefined variable raises TemplateRenderError."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "undefined_test"},
            "template": {"source": "Hello {{ missing_var }}!"},
        }

        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render(tool_spec, {})

        assert "Undefined variable" in str(exc_info.value)
        assert exc_info.value.template_name == "undefined_test"

    def test_template_syntax_error_raises_render_error(self) -> None:
        """Test that template syntax error raises TemplateRenderError."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "syntax_error"},
            "template": {"source": "{% if broken %}"},  # Missing endif
        }

        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render(tool_spec)

        assert "syntax error" in str(exc_info.value).lower()

    def test_error_includes_template_name(self) -> None:
        """Test that error messages include template name for debugging."""
        renderer = TemplateRenderer()
        tool_spec = {
            "metadata": {"name": "my_tool"},
            "template": {"source": "{{ undefined }}"},
        }

        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render(tool_spec)

        assert exc_info.value.template_name == "my_tool"

    def test_missing_metadata_uses_unknown_name(self) -> None:
        """Test that missing metadata defaults to 'unknown' template name."""
        renderer = TemplateRenderer()
        tool_spec = {"template": {"source": "{{ undefined }}"}}

        with pytest.raises(TemplateRenderError) as exc_info:
            renderer.render(tool_spec)

        assert exc_info.value.template_name == "unknown"


class TestTemplateRendererSyntaxValidation:
    """Test template syntax validation without rendering."""

    def test_validate_valid_template(self) -> None:
        """Test validating a syntactically correct template."""
        renderer = TemplateRenderer()
        template_source = "Hello {{ name }}!"

        result = renderer.validate_template_syntax(template_source)

        assert result is True

    def test_validate_template_with_conditionals(self) -> None:
        """Test validating template with conditional logic."""
        renderer = TemplateRenderer()
        template_source = "{% if show %}Message{% endif %}"

        result = renderer.validate_template_syntax(template_source)

        assert result is True

    def test_validate_invalid_template_raises_syntax_error(self) -> None:
        """Test that invalid template raises TemplateSyntaxError."""
        renderer = TemplateRenderer()
        template_source = "{% if broken %}"  # Missing endif

        with pytest.raises(TemplateSyntaxError):
            renderer.validate_template_syntax(template_source)

    def test_validate_template_with_loops(self) -> None:
        """Test validating template with for loops."""
        renderer = TemplateRenderer()
        template_source = "{% for item in items %}{{ item }}{% endfor %}"

        result = renderer.validate_template_syntax(template_source)

        assert result is True
