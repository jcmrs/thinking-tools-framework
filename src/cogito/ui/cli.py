"""Command-line interface for Cogito thinking tools framework."""

import json
import sys
from pathlib import Path
from typing import Any

import click

from cogito import __version__
from cogito.orchestration.executor import ToolExecutor
from cogito.orchestration.registry import ToolRegistry
from cogito.processing.validator import SchemaValidator
from cogito.storage.process_memory import ProcessMemoryStore


@click.group()
@click.version_option(version=__version__)
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """Cogito: Thinking Tools Framework.

    AI-augmented metacognition tools using parameterized YAML templates.
    """
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
@click.option("--category", help="Filter tools by category")
@click.option(
    "--output-format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def list(category: str | None, output_format: str, tools_dir: Path | None) -> None:
    """List available thinking tools."""
    try:
        # Default to examples directory
        if tools_dir is None:
            tools_dir = Path("examples")

        # Initialize registry and discover tools
        registry = ToolRegistry([tools_dir])
        count = registry.discover_tools()

        if count == 0:
            click.echo(f"No tools found in {tools_dir}", err=True)
            sys.exit(1)

        # Get tools, optionally filtered by category
        tool_names = registry.list_tools()
        tools = []

        for tool_name in tool_names:
            tool_spec = registry.get_tool(tool_name)
            if tool_spec:
                metadata = tool_spec.get("metadata", {})

                # Filter by category if specified
                if category and metadata.get("category") != category:
                    continue

                tools.append(
                    {
                        "name": metadata.get("name", "unknown"),
                        "display_name": metadata.get("display_name", ""),
                        "description": metadata.get("description", ""),
                        "category": metadata.get("category", ""),
                        "tags": metadata.get("tags", []),
                    }
                )

        # Output results
        if output_format == "json":
            click.echo(json.dumps(tools, indent=2))
        else:
            if not tools:
                click.echo(f"No tools found in category '{category}'")
            else:
                click.echo(f"\nFound {len(tools)} thinking tools:\n")
                for tool in tools:
                    click.echo(f"  • {tool['display_name']}")
                    click.echo(f"    {tool['description']}")
                    click.echo(f"    Category: {tool['category']}")
                    click.echo(f"    Tags: {', '.join(tool['tags']) if tool['tags'] else 'none'}")
                    click.echo()

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument("tool_name")
@click.option(
    "--param",
    "-p",
    multiple=True,
    help="Tool parameters as KEY=VALUE pairs (can be used multiple times)",
)
@click.option(
    "--output-format",
    type=click.Choice(["text", "markdown"]),
    default="text",
    help="Output format",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def execute(
    tool_name: str,
    param: tuple[str, ...],
    output_format: str,
    tools_dir: Path | None,
) -> None:
    """Execute a thinking tool with parameters.

    \b
    Examples:
      cogito execute think_aloud -p context="Debugging API" -p depth=standard
      cogito execute code_review_checklist -p file_path=src/main.py
    """
    try:
        # Default to examples directory
        if tools_dir is None:
            tools_dir = Path("examples")

        # Parse parameters from KEY=VALUE format
        parameters: dict[str, Any] = {}
        for p in param:
            if "=" not in p:
                raise click.UsageError(f"Invalid parameter format: '{p}'. Use KEY=VALUE format.")
            key, value = p.split("=", 1)
            parameters[key.strip()] = value.strip()

        # Initialize registry and executor
        registry = ToolRegistry([tools_dir])
        registry.discover_tools()
        executor = ToolExecutor()

        # Execute tool
        result = executor.execute_by_name(tool_name, registry, parameters)

        # Output result
        if output_format == "markdown":
            click.echo(result)
        else:
            # Strip markdown formatting for text output
            click.echo(result)

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument("tool_name")
@click.option(
    "--output-format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def info(tool_name: str, output_format: str, tools_dir: Path | None) -> None:
    """Show detailed information about a thinking tool."""
    try:
        # Default to examples directory
        if tools_dir is None:
            tools_dir = Path("examples")

        # Initialize registry
        registry = ToolRegistry([tools_dir])
        registry.discover_tools()

        # Get tool spec
        tool_spec = registry.get_tool(tool_name)
        if tool_spec is None:
            raise click.ClickException(f"Tool '{tool_name}' not found")

        # Output results
        if output_format == "json":
            click.echo(json.dumps(tool_spec, indent=2))
        else:
            metadata = tool_spec.get("metadata", {})
            parameters = tool_spec.get("parameters", {})

            click.echo(f"\n{metadata.get('display_name', tool_name)}\n")
            click.echo(f"Description: {metadata.get('description', 'N/A')}")
            click.echo(f"Category: {metadata.get('category', 'N/A')}")
            click.echo(f"Author: {metadata.get('author', 'N/A')}")
            click.echo(f"Version: {metadata.get('version', 'N/A')}")
            click.echo(f"Tags: {', '.join(metadata.get('tags', []))}")

            click.echo("\nParameters:")
            for param_name, param_schema in parameters.get("properties", {}).items():
                required = param_name in parameters.get("required", [])
                req_str = " (required)" if required else ""
                click.echo(f"  • {param_name}{req_str}")
                click.echo(f"    {param_schema.get('description', 'No description')}")
                click.echo(f"    Type: {param_schema.get('type', 'string')}")
            click.echo()

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument("tool_file", type=click.Path(exists=True, path_type=Path))
def validate(tool_file: Path) -> None:
    """Validate a thinking tool YAML specification."""
    try:
        # Load YAML file
        import yaml

        with tool_file.open(encoding="utf-8") as f:
            tool_spec = yaml.safe_load(f)

        # Validate against schema
        validator = SchemaValidator()
        validator.validate_tool_spec(tool_spec)

        click.echo(f"✓ {tool_file.name} is valid")

    except Exception as e:
        raise click.ClickException(f"Validation failed: {e}") from e


@cli.command()
@click.option("--search", help="Search keyword in title, summary, or tags")
@click.option("--category", help="Filter by entry type/category")
@click.option("--entry-id", help="Get specific entry by ID")
@click.option(
    "--output-format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--memory-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def memory(
    search: str | None,
    category: str | None,
    entry_id: str | None,
    output_format: str,
    memory_file: Path | None,
) -> None:
    """Query process memory entries.

    \b
    Examples:
      cogito memory --search validation
      cogito memory --category lessons_learned
      cogito memory --entry-id PM-021
    """
    try:
        # Default to .bootstrap/process_memory.jsonl
        if memory_file is None:
            memory_file = Path(".bootstrap/process_memory.jsonl")

        if not memory_file.exists():
            raise click.ClickException(f"Process memory file not found: {memory_file}")

        # Initialize memory store
        memory_store = ProcessMemoryStore(memory_file)

        # Query based on parameters
        if entry_id:
            entry = memory_store.get_entry(entry_id)
            if not entry:
                raise click.ClickException(f"Entry '{entry_id}' not found")
            entries = [entry]
        elif search:
            entries = memory_store.search_entries(search)
        else:
            entries = memory_store.list_entries(category=category, tags=[])

        # Output results
        if output_format == "json":
            click.echo(json.dumps(entries, indent=2))
        else:
            if not entries:
                click.echo("No entries found")
            else:
                click.echo(f"\nFound {len(entries)} entries:\n")
                for entry in entries:
                    click.echo(f"  {entry['id']}: {entry['title']}")
                    click.echo(f"  Type: {entry['type']}")
                    click.echo(f"  {entry['summary']}")
                    if entry.get("tags"):
                        click.echo(f"  Tags: {', '.join(entry['tags'])}")
                    click.echo()

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.group(name="provisioning")
def memory_group() -> None:
    """Process memory provisioning commands."""
    pass


@memory_group.command(name="export")
@click.argument("format", type=click.Choice(["markdown", "json", "yaml"]))
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option("--category", help="Filter by entry type/category")
@click.option(
    "--memory-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def memory_export(
    format: str, output: Path | None, category: str | None, memory_file: Path | None
) -> None:
    """Export process memory entries.

    \b
    Examples:
      cogito memory export markdown --output handover.md
      cogito memory export json --category StrategicDecision
      cogito memory export yaml --output decisions.yml
    """
    try:
        from cogito.provisioning.exporter import ProcessMemoryExporter

        # Default to .bootstrap/process_memory.jsonl
        if memory_file is None:
            memory_file = Path(".bootstrap/process_memory.jsonl")

        if not memory_file.exists():
            raise click.ClickException(f"Process memory file not found: {memory_file}")

        # Initialize exporter
        memory_store = ProcessMemoryStore(memory_file)
        exporter = ProcessMemoryExporter(memory_store)

        # Export in requested format
        if format == "markdown":
            result = exporter.export_to_markdown(output, category)
        elif format == "json":
            result = exporter.export_to_json(output, category)
        else:  # yaml
            result = exporter.export_to_yaml(output, category)

        # Output to stdout if no file specified
        if not output:
            click.echo(result)
        else:
            click.echo(f"Exported to {output}")

    except Exception as e:
        raise click.ClickException(str(e)) from e


@memory_group.command(name="import")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "jsonl"]),
    help="Input format (auto-detected if not specified)",
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Validate without importing",
)
@click.option(
    "--memory-file",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def memory_import(
    file: Path,
    format: str | None,
    validate_only: bool,
    memory_file: Path | None,
) -> None:
    """Import process memory entries.

    \b
    Examples:
      cogito memory import entries.json
      cogito memory import --format yaml decisions.yml
      cogito memory import --validate-only test.jsonl
    """
    try:
        from cogito.provisioning.importer import ProcessMemoryImporter

        # Default to .bootstrap/process_memory.jsonl
        if memory_file is None:
            memory_file = Path(".bootstrap/process_memory.jsonl")

        # Initialize importer
        memory_store = ProcessMemoryStore(memory_file)
        importer = ProcessMemoryImporter(memory_store)

        # Auto-detect format if not specified
        if format is None:
            if file.suffix == ".json":
                format = "json"
            elif file.suffix in (".yml", ".yaml"):
                format = "yaml"
            elif file.suffix == ".jsonl":
                format = "jsonl"
            else:
                raise click.ClickException(
                    f"Cannot auto-detect format for {file}. Use --format to specify."
                )

        # Import based on format
        merge = not validate_only
        if format == "json":
            count, errors = importer.import_from_json(file, merge)
        elif format == "yaml":
            count, errors = importer.import_from_yaml(file, merge)
        else:  # jsonl
            count, errors = importer.import_from_jsonl(file, merge)

        # Report results
        if errors:
            click.echo(f"Validation errors ({len(errors)}):")
            for error in errors:
                click.echo(f"  - {error}")

        if validate_only:
            click.echo(f"\nValidation: {count} entries valid")
        else:
            click.echo(f"\nImported {count} entries")

        if errors:
            raise click.ClickException(f"{len(errors)} validation errors found")

    except Exception as e:
        raise click.ClickException(str(e)) from e


@memory_group.command(name="handover")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--include-deprecated",
    is_flag=True,
    help="Include deprecated entries",
)
@click.option(
    "--memory-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def memory_handover(
    output: Path | None, include_deprecated: bool, memory_file: Path | None
) -> None:
    """Generate session handover document.

    \b
    Examples:
      cogito memory handover --output HANDOVER.md
      cogito memory handover --include-deprecated
    """
    try:
        from cogito.provisioning.handover import HandoverGenerator

        # Default to .bootstrap/process_memory.jsonl
        if memory_file is None:
            memory_file = Path(".bootstrap/process_memory.jsonl")

        if not memory_file.exists():
            raise click.ClickException(f"Process memory file not found: {memory_file}")

        # Initialize handover generator
        memory_store = ProcessMemoryStore(memory_file)
        generator = HandoverGenerator(memory_store)

        # Generate handover document
        result = generator.generate_handover_document(output, include_deprecated)

        # Output to stdout if no file specified
        if not output:
            click.echo(result)
        else:
            click.echo(f"Generated handover document: {output}")

    except Exception as e:
        raise click.ClickException(str(e)) from e


@memory_group.command(name="context")
@click.argument("topic")
@click.option(
    "--max-entries",
    type=int,
    default=10,
    help="Maximum number of entries to include",
)
@click.option(
    "--no-related",
    is_flag=True,
    help="Don't include related entries",
)
@click.option(
    "--memory-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def memory_context(
    topic: str, max_entries: int, no_related: bool, memory_file: Path | None
) -> None:
    """Generate context snippet for a topic.

    \b
    Examples:
      cogito memory context validation
      cogito memory context MCP --max-entries 5
      cogito memory context architecture --no-related
    """
    try:
        from cogito.provisioning.context import ContextGenerator

        # Default to .bootstrap/process_memory.jsonl
        if memory_file is None:
            memory_file = Path(".bootstrap/process_memory.jsonl")

        if not memory_file.exists():
            raise click.ClickException(f"Process memory file not found: {memory_file}")

        # Initialize context generator
        memory_store = ProcessMemoryStore(memory_file)
        generator = ContextGenerator(memory_store)

        # Generate context
        result = generator.generate_context_for_topic(
            topic, max_entries, include_related=not no_related
        )

        click.echo(result)

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.group()
def skills() -> None:
    """Export thinking tools as Claude Code Skills."""
    pass


@skills.command("export")
@click.argument("tool_name")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for skill files",
)
@click.option(
    "--no-symlink",
    is_flag=True,
    default=False,
    help="Don't create symlink to source YAML (copy instead)",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def export_skill(
    tool_name: str,
    output: Path,
    no_symlink: bool,
    tools_dir: Path | None,
) -> None:
    """Export single thinking tool as Claude Code Skill.

    TOOL_NAME: Name of the thinking tool to export

    Examples:
        cogito skills export think_aloud --output ~/.claude/skills/
        cogito skills export code_review_checklist --output ./skills/
    """
    try:
        from cogito.orchestration.registry import ToolRegistry
        from cogito.provisioning.skills_exporter import SkillsExporter

        # Initialize registry
        tool_dirs = [tools_dir] if tools_dir else [Path("examples")]
        registry = ToolRegistry(tool_dirs)
        registry.discover_tools()

        # Initialize exporter
        exporter = SkillsExporter(tool_registry=registry)

        # Export tool
        click.echo(f"Exporting tool '{tool_name}'...")
        result = exporter.export_tool(
            tool_name=tool_name,
            output_dir=output,
            create_symlink=not no_symlink,
        )

        # Report results
        click.echo(f"✓ Exported to: {result['skill_dir']}")
        click.echo(f"  - SKILL.md: {result['files']['skill_md']}")
        click.echo(f"  - Wrapper: {result['files']['wrapper']}")
        if result["files"].get("symlink"):
            click.echo(f"  - Source: {result['files']['symlink']}")

    except FileNotFoundError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(f"Export failed: {e}") from e


@skills.command("export-category")
@click.argument("category")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for skill files",
)
@click.option(
    "--no-symlinks",
    is_flag=True,
    default=False,
    help="Don't create symlinks to source YAMLs (copy instead)",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def export_category(
    category: str,
    output: Path,
    no_symlinks: bool,
    tools_dir: Path | None,
) -> None:
    """Export all tools in a category as Claude Code Skills.

    CATEGORY: Category name (e.g., metacognition, review, handoff)

    Examples:
        cogito skills export-category metacognition --output ~/.claude/skills/
        cogito skills export-category review --output ./skills/
    """
    try:
        from cogito.orchestration.registry import ToolRegistry
        from cogito.provisioning.skills_exporter import SkillsExporter

        # Initialize registry
        tool_dirs = [tools_dir] if tools_dir else [Path("examples")]
        registry = ToolRegistry(tool_dirs)
        registry.discover_tools()

        # Initialize exporter
        exporter = SkillsExporter(tool_registry=registry)

        # Export category
        click.echo(f"Exporting category '{category}'...")
        result = exporter.export_category(
            category=category,
            output_dir=output,
            create_symlinks=not no_symlinks,
        )

        # Report results
        click.echo(f"\n✓ Exported {len(result['exported'])} / {result['total']} tools")

        if result["exported"]:
            click.echo("\nExported tools:")
            for tool in result["exported"]:
                click.echo(f"  - {tool['tool_name']} → {tool['skill_name']}")

        if result["failed"]:
            click.echo("\n✗ Failed exports:", err=True)
            for failure in result["failed"]:
                click.echo(f"  - {failure['tool_name']}: {failure['error']}", err=True)

    except Exception as e:
        raise click.ClickException(f"Export failed: {e}") from e


@skills.command("export-all")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for skill files",
)
@click.option(
    "--no-symlinks",
    is_flag=True,
    default=False,
    help="Don't create symlinks to source YAMLs (copy instead)",
)
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
def export_all(
    output: Path,
    no_symlinks: bool,
    tools_dir: Path | None,
) -> None:
    """Export all thinking tools as Claude Code Skills.

    Examples:
        cogito skills export-all --output ~/.claude/skills/
        cogito skills export-all --output ./skills/ --no-symlinks
    """
    try:
        from cogito.orchestration.registry import ToolRegistry
        from cogito.provisioning.skills_exporter import SkillsExporter

        # Initialize registry
        tool_dirs = [tools_dir] if tools_dir else [Path("examples")]
        registry = ToolRegistry(tool_dirs)
        registry.discover_tools()

        # Initialize exporter
        exporter = SkillsExporter(tool_registry=registry)

        # Export all
        click.echo("Exporting all thinking tools...")
        result = exporter.export_all(
            output_dir=output,
            create_symlinks=not no_symlinks,
        )

        # Report results
        click.echo(f"\n✓ Exported {len(result['exported'])} / {result['total']} tools")

        if result["exported"]:
            click.echo("\nExported tools:")
            for tool in result["exported"]:
                click.echo(f"  - {tool['tool_name']} → {tool['skill_name']}")

        if result["failed"]:
            click.echo("\n✗ Failed exports:", err=True)
            for failure in result["failed"]:
                click.echo(f"  - {failure['tool_name']}: {failure['error']}", err=True)

    except Exception as e:
        raise click.ClickException(f"Export failed: {e}") from e


@cli.command()
@click.argument("project_name")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Parent directory for new project (default: current directory)",
)
@click.option(
    "--description",
    default=None,
    help="Project description for README and pyproject.toml",
)
@click.option(
    "--minimal",
    is_flag=True,
    default=False,
    help="Create minimal project structure without examples",
)
@click.option(
    "--author-name",
    default=None,
    help="Author name for pyproject.toml",
)
@click.option(
    "--author-email",
    default=None,
    help="Author email for pyproject.toml",
)
def bootstrap(
    project_name: str,
    output_dir: Path | None,
    description: str | None,
    minimal: bool,
    author_name: str | None,
    author_email: str | None,
) -> None:
    """Bootstrap a new thinking-tools-framework project.

    PROJECT_NAME: Name of the new project (used for directory and package name)

    \b
    Examples:
        cogito bootstrap my-thinking-tools
        cogito bootstrap my-project --output-dir ~/projects
        cogito bootstrap minimal-project --minimal --description "A minimal setup"
        cogito bootstrap my-project --author-name "Jane Doe" --author-email "jane@example.com"
    """
    try:
        from cogito.provisioning.bootstrap import ProjectBootstrapper

        # Use current directory if not specified
        if output_dir is None:
            output_dir = Path.cwd()

        # Build context for templates
        context: dict[str, Any] = {}
        if author_name:
            context["author_name"] = author_name
        if author_email:
            context["author_email"] = author_email

        # Initialize bootstrapper
        bootstrapper = ProjectBootstrapper()

        # Bootstrap project
        click.echo(f"Bootstrapping project '{project_name}' in {output_dir}...")
        result = bootstrapper.bootstrap_project(
            project_name=project_name,
            output_dir=output_dir,
            description=description,
            include_examples=not minimal,
            **context,
        )

        # Check results
        if not result["success"]:
            if result["errors"]:
                click.echo("Bootstrap failed with errors:", err=True)
                for error in result["errors"]:
                    click.echo(f"  - {error}", err=True)
            raise click.ClickException("Project bootstrap failed")

        # Report success
        click.echo(f"\nSuccessfully bootstrapped '{project_name}'")
        click.echo(f"  Project root: {result['project_root']}")
        click.echo(f"  Directories created: {result['directories_created']}")
        click.echo(f"  Files created: {result['files_created']}")
        if not minimal:
            click.echo(f"  Example tools copied: {result['examples_copied']}")

        # Next steps
        click.echo("\nNext steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  python -m pip install -e '.[dev]'")
        click.echo("  cogito list")
        if not minimal:
            click.echo("  cogito execute think_aloud topic='your topic'")

        # Warn about errors if any (but project still created)
        if result["errors"]:
            click.echo("\nWarnings:", err=True)
            for error in result["errors"]:
                click.echo(f"  - {error}", err=True)

    except Exception as e:
        raise click.ClickException(f"Bootstrap failed: {e}") from e


@cli.command()
@click.option(
    "--tools-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing tool YAML files",
)
@click.option(
    "--memory-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to process_memory.jsonl file",
)
def serve(tools_dir: Path | None, memory_file: Path | None) -> None:
    """Start MCP server for thinking tools.

    This command starts the FastMCP server, making thinking tools
    available to MCP clients like Claude Code and Serena.
    """
    try:
        # Import here to avoid circular dependency
        from cogito.integration.mcp_server import create_server, mcp

        # Default to examples directory
        if tools_dir is None:
            tools_dir = Path("examples")

        # Initialize server
        create_server(
            tools_directory=tools_dir,
            memory_path=memory_file,
        )

        click.echo(f"Starting MCP server with tools from {tools_dir}")
        if memory_file:
            click.echo(f"Process memory: {memory_file}")

        # Run server
        mcp.run()

    except Exception as e:
        raise click.ClickException(str(e)) from e


def main() -> None:
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
