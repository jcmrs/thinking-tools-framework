"""Bootstrap orchestrator for creating new thinking-tools-framework projects.

This module coordinates project structure creation, configuration generation,
example tool copying, and template rendering for new project instances.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from cogito.provisioning.config_generator import ConfigGenerator
from cogito.provisioning.example_tools import ExampleToolsSelector
from cogito.provisioning.project_template import (
    create_project_directories,
    get_canonical_structure,
    get_file_locations,
)


class ProjectBootstrapper:
    """Orchestrates creation of new thinking-tools-framework project instances."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize the project bootstrapper.

        Args:
            template_dir: Directory containing bootstrap templates.
                         Defaults to templates/bootstrap/ relative to package root.
        """
        if template_dir is None:
            package_root = Path(__file__).parent.parent.parent.parent
            template_dir = package_root / "templates" / "bootstrap"

        self.template_dir = template_dir
        self.config_generator = ConfigGenerator(template_dir)
        self.example_tools_selector = ExampleToolsSelector()

        # Initialize Jinja2 environment for general templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def bootstrap_project(
        self,
        project_name: str,
        output_dir: Path,
        description: str | None = None,
        include_examples: bool = True,
        **context: Any,
    ) -> dict[str, Any]:
        """Bootstrap a complete new project instance.

        Args:
            project_name: Name of the new project (used for directory and package name)
            output_dir: Parent directory where project will be created
            description: Project description for README and pyproject.toml
            include_examples: If True, include example thinking tools
            **context: Additional context for template rendering

        Returns:
            Dictionary with bootstrap results:
                - success: True if bootstrap succeeded
                - project_root: Path to created project
                - directories_created: Number of directories created
                - files_created: Number of files created
                - examples_copied: Number of example tools copied (if include_examples)
                - errors: List of any errors encountered
        """
        result: dict[str, Any] = {
            "success": False,
            "project_root": None,
            "directories_created": 0,
            "files_created": 0,
            "examples_copied": 0,
            "errors": [],
        }

        # Determine project root
        project_root = output_dir / project_name
        result["project_root"] = str(project_root)

        # Check if project directory already exists
        if project_root.exists():
            result["errors"].append(f"Project directory already exists: {project_root}")
            return result

        try:
            # Step 1: Create directory structure
            structure = get_canonical_structure(include_examples=include_examples)
            dir_result = create_project_directories(project_root, structure)
            result["directories_created"] = len(dir_result["directories_created"])
            if dir_result["errors"]:
                result["errors"].extend(dir_result["errors"])
                return result

            # Step 2: Generate configuration files
            desc = description or f"A thinking-tools-framework instance: {project_name}"
            configs = self.config_generator.generate_all_configs(
                project_name=project_name, description=desc, **context
            )

            # Write config files
            for config_name, content in configs.items():
                config_path = project_root / "config" / config_name
                config_path.write_text(content, encoding="utf-8")
                result["files_created"] += 1

            # Step 3: Render and write template files
            template_context = {
                "project_name": project_name,
                "description": desc,
                "include_examples": include_examples,
                "now": datetime.now().isoformat(),
                **context,
            }

            file_locations = get_file_locations(project_root, structure)
            rendered_files = self._render_all_templates(file_locations, template_context)

            for file_path, content in rendered_files.items():
                file_path.write_text(content, encoding="utf-8")
                result["files_created"] += 1

            # Step 4: Copy PROJECT-IMPERATIVES.md from framework root
            self._copy_project_imperatives(project_root)
            result["files_created"] += 1

            # Step 5: Copy example tools (if requested)
            if include_examples:
                examples_result = self.example_tools_selector.copy_starter_tools(
                    project_root / "examples"
                )
                result["examples_copied"] = examples_result["copied"]
                if examples_result["failed"] > 0:
                    result["errors"].extend(
                        [r["error"] for r in examples_result["results"] if not r["success"]]
                    )

                # Create examples README
                readme_result = self.example_tools_selector.create_examples_readme(
                    project_root / "examples"
                )
                if readme_result["success"]:
                    result["files_created"] += 1
                else:
                    result["errors"].append(readme_result.get("error", "Unknown error"))

            # Success!
            result["success"] = True

        except Exception as e:
            result["errors"].append(f"Bootstrap failed: {e}")

        return result

    def _render_all_templates(
        self, file_locations: dict[str, Path], context: dict[str, Any]
    ) -> dict[Path, str]:
        """Render all template files.

        Args:
            file_locations: Mapping of template names to output paths
            context: Template rendering context

        Returns:
            Dictionary mapping output paths to rendered content
        """
        rendered: dict[Path, str] = {}

        for template_name, output_path in file_locations.items():
            # Template names have path prefixes that need to be stripped
            # Example: "docs_QUICK_START_md_j2" -> "QUICK-START.md.j2"
            # Example: "README_md_j2" -> "README.md.j2"

            # Strip path prefixes (docs_, src_cogito_, tests_, config_, bootstrap_)
            prefixes = ["docs_", "src_cogito_", "tests_", "config_", "bootstrap_"]
            base_name = template_name
            for prefix in prefixes:
                if base_name.startswith(prefix):
                    base_name = base_name[len(prefix):]
                    break

            # Convert back to actual filename
            # "QUICK_START_md_j2" -> "QUICK-START.md.j2"
            # "__init___py_j2" -> "__init__.py.j2"
            # "_gitignore_j2" -> ".gitignore.j2"
            if base_name.endswith("_j2"):
                # Remove _j2 suffix
                base_name = base_name[:-3]

                # Handle dotfiles (like .gitignore)
                # "_gitignore" -> ".gitignore"
                if base_name.startswith("_") and not base_name.startswith("__"):
                    template_filename = f".{base_name[1:]}.j2"
                else:
                    # Replace underscore before extension with dot
                    # Extensions: md, yml, toml, json, jsonl, py
                    parts = base_name.rsplit("_", 1)
                    if len(parts) == 2 and parts[1] in ["md", "yml", "toml", "json", "jsonl", "py"]:
                        # Convert template name back to actual filename
                        # Examples:
                        #   QUICK_START -> QUICK-START (for docs)
                        #   knowledge_graph -> knowledge_graph (for other files)
                        #   __init__ -> __init__ (preserve double underscores)
                        filename_part = parts[0]

                        # Only convert underscores to hyphens for ALL-CAPS names (doc files)
                        # Leave other files with underscores (knowledge_graph, process_memory)
                        if filename_part.isupper() and not filename_part.startswith("__"):
                            filename_part = filename_part.replace("_", "-")

                        template_filename = f"{filename_part}.{parts[1]}.j2"
                    else:
                        template_filename = f"{base_name}.j2"
            else:
                template_filename = base_name

            try:
                template = self.jinja_env.get_template(template_filename)
                content = template.render(**context)
                rendered[output_path] = content
            except Exception:
                # Skip templates that don't exist (not all files use templates)
                # Debug: Uncomment to see what templates are failing
                # print(f"Skipping {template_filename}: {e}")
                continue

        return rendered

    def _copy_project_imperatives(self, project_root: Path) -> None:
        """Copy PROJECT-IMPERATIVES.md from framework root to new project.

        Args:
            project_root: Root directory of new project
        """
        # Find framework root (4 levels up from this file)
        framework_root = Path(__file__).parent.parent.parent.parent
        source = framework_root / "PROJECT-IMPERATIVES.md"
        dest = project_root / "PROJECT-IMPERATIVES.md"

        if source.exists():
            # Read with utf-8 encoding and write to destination
            content = source.read_text(encoding="utf-8")
            dest.write_text(content, encoding="utf-8")
