"""Configuration file generator for bootstrap package.

This module generates configuration files (pyproject.toml, cogito.yml, logging.yml)
for new thinking-tools-framework projects using Jinja2 templates.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class ConfigGenerator:
    """Generates configuration files from templates for new projects."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize the config generator.

        Args:
            template_dir: Directory containing Jinja2 templates.
                         Defaults to templates/bootstrap/ relative to package root.
        """
        if template_dir is None:
            # Default to templates/bootstrap directory
            package_root = Path(__file__).parent.parent.parent.parent
            template_dir = package_root / "templates" / "bootstrap"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,  # Config files are not HTML
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_pyproject_toml(self, context: dict[str, Any]) -> str:
        """Generate pyproject.toml content from template.

        Args:
            context: Template context with project metadata
                Required keys: project_name, description, author_name, author_email

        Returns:
            Rendered pyproject.toml content

        Raises:
            ValueError: If required context keys are missing
        """
        required_keys = ["project_name", "description"]
        missing_keys = [k for k in required_keys if k not in context]
        if missing_keys:
            raise ValueError(f"Missing required context keys: {missing_keys}")

        template = self.env.get_template("pyproject.toml.j2")
        return template.render(**context)

    def generate_cogito_yml(self, context: dict[str, Any]) -> str:
        """Generate cogito.yml content from template.

        Args:
            context: Template context with framework configuration
                Optional keys: tool_directories, cache_settings, security_settings

        Returns:
            Rendered cogito.yml content
        """
        # Provide sensible defaults
        defaults: dict[str, Any] = {
            "tool_directories": ["examples/"],
            "cache_enabled": True,
            "cache_ttl_seconds": 3600,
            "template_sandboxing": True,
        }
        # Merge provided context with defaults
        merged_context = {**defaults, **context}

        template = self.env.get_template("cogito.yml.j2")
        return template.render(**merged_context)

    def generate_logging_yml(self, context: dict[str, Any]) -> str:
        """Generate logging.yml content from template.

        Args:
            context: Template context with logging configuration
                Optional keys: log_level, log_file, console_logging

        Returns:
            Rendered logging.yml content
        """
        # Provide sensible defaults for development
        defaults: dict[str, Any] = {
            "log_level": "INFO",
            "log_file": "logs/cogito.log",
            "console_logging": True,
        }
        merged_context = {**defaults, **context}

        template = self.env.get_template("logging.yml.j2")
        return template.render(**merged_context)

    def generate_all_configs(
        self, project_name: str, description: str, **kwargs: Any
    ) -> dict[str, str]:
        """Generate all configuration files at once.

        Args:
            project_name: Name of the project (used for pyproject.toml)
            description: Project description (used for pyproject.toml)
            **kwargs: Additional context for templates

        Returns:
            Dictionary mapping config filenames to rendered content:
                - pyproject.toml: Project metadata and dependencies
                - cogito.yml: Framework configuration
                - logging.yml: Logging configuration
        """
        # Build context for pyproject.toml
        pyproject_context = {
            "project_name": project_name,
            "description": description,
            **{k: v for k, v in kwargs.items() if k in ["author_name", "author_email"]},
        }

        # Build context for other configs
        config_context = {k: v for k, v in kwargs.items() if k not in pyproject_context}

        return {
            "pyproject.toml": self.generate_pyproject_toml(pyproject_context),
            "cogito.yml": self.generate_cogito_yml(config_context),
            "logging.yml": self.generate_logging_yml(config_context),
        }
