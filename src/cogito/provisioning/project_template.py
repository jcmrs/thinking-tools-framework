"""Project structure template generator for bootstrap package.

This module defines the canonical project structure for new thinking-tools-framework
instances and provides functions to generate the directory tree.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProjectStructure:
    """Defines the canonical directory structure for a new project."""

    root_files: list[str]
    src_cogito_files: list[str]
    src_cogito_dirs: list[str]
    examples_dirs: list[str]
    tests_files: list[str]
    tests_dirs: list[str]
    docs_files: list[str]
    config_files: list[str]
    bootstrap_files: list[str]


def get_canonical_structure(include_examples: bool = True) -> ProjectStructure:
    """Get the canonical project structure definition.

    Args:
        include_examples: If True, include examples directories and files

    Returns:
        ProjectStructure defining all directories and files to create
    """
    root_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "LICENSE",
        "PROJECT-IMPERATIVES.md",
    ]

    src_cogito_files = ["__init__.py"]
    src_cogito_dirs = ["core", "ui"]

    examples_dirs = (
        ["metacognition", "problem_solving", "review", "handoff", "debugging"]
        if include_examples
        else []
    )

    tests_files = ["__init__.py", "conftest.py"]
    tests_dirs = ["unit", "integration", "fixtures"]

    docs_files = ["QUICK-START.md", "ARCHITECTURE.md", "CONFIGURATION.md"]

    config_files = ["cogito.yml", "logging.yml"]

    bootstrap_files = ["process_memory.jsonl", "knowledge_graph.json"]

    return ProjectStructure(
        root_files=root_files,
        src_cogito_files=src_cogito_files,
        src_cogito_dirs=src_cogito_dirs,
        examples_dirs=examples_dirs,
        tests_files=tests_files,
        tests_dirs=tests_dirs,
        docs_files=docs_files,
        config_files=config_files,
        bootstrap_files=bootstrap_files,
    )


def create_project_directories(
    project_root: Path, structure: ProjectStructure
) -> dict[str, Any]:
    """Create all directories for the project structure.

    Args:
        project_root: Root directory for the new project
        structure: Project structure definition

    Returns:
        Dictionary with creation results:
            - directories_created: List of created directory paths
            - errors: List of any errors encountered
    """
    directories_created: list[str] = []
    errors: list[str] = []

    # Create root directory
    try:
        project_root.mkdir(parents=True, exist_ok=True)
        directories_created.append(str(project_root))
    except Exception as e:
        errors.append(f"Failed to create root directory {project_root}: {e}")
        return {"directories_created": directories_created, "errors": errors}

    # Define all directories to create
    directories = [
        project_root / "src" / "cogito",
        project_root / "tests",
        project_root / "docs",
        project_root / "config",
        project_root / ".bootstrap",
    ]

    # Add src/cogito subdirectories
    for subdir in structure.src_cogito_dirs:
        directories.append(project_root / "src" / "cogito" / subdir)

    # Add examples directories
    if structure.examples_dirs:
        directories.append(project_root / "examples")
        for example_dir in structure.examples_dirs:
            directories.append(project_root / "examples" / example_dir)

    # Add test subdirectories
    for test_dir in structure.tests_dirs:
        directories.append(project_root / "tests" / test_dir)

    # Create all directories
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            directories_created.append(str(directory))
        except Exception as e:
            errors.append(f"Failed to create directory {directory}: {e}")

    return {"directories_created": directories_created, "errors": errors}


def get_file_locations(project_root: Path, structure: ProjectStructure) -> dict[str, Path]:
    """Get full paths for all template files to be generated.

    Args:
        project_root: Root directory for the new project
        structure: Project structure definition

    Returns:
        Dictionary mapping template names to output file paths
    """
    locations: dict[str, Path] = {}

    # Root files
    for filename in structure.root_files:
        template_name = filename.replace(".", "_") + "_j2"
        locations[template_name] = project_root / filename

    # src/cogito files
    for filename in structure.src_cogito_files:
        template_name = f"src_cogito_{filename.replace('.', '_')}_j2"
        locations[template_name] = project_root / "src" / "cogito" / filename

    # tests files
    for filename in structure.tests_files:
        template_name = f"tests_{filename.replace('.', '_')}_j2"
        locations[template_name] = project_root / "tests" / filename

    # docs files
    for filename in structure.docs_files:
        template_name = f"docs_{filename.replace('.', '_').replace('-', '_')}_j2"
        locations[template_name] = project_root / "docs" / filename

    # config files
    for filename in structure.config_files:
        template_name = f"config_{filename.replace('.', '_')}_j2"
        locations[template_name] = project_root / "config" / filename

    # bootstrap files
    for filename in structure.bootstrap_files:
        template_name = f"bootstrap_{filename.replace('.', '_')}_j2"
        locations[template_name] = project_root / ".bootstrap" / filename

    return locations
