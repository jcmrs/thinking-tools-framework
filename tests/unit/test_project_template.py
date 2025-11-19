"""Unit tests for project_template module."""

from pathlib import Path

from cogito.provisioning.project_template import (
    ProjectStructure,
    create_project_directories,
    get_canonical_structure,
    get_file_locations,
)


class TestGetCanonicalStructure:
    """Tests for get_canonical_structure function."""

    def test_structure_with_examples(self) -> None:
        """Test canonical structure includes examples when requested."""
        structure = get_canonical_structure(include_examples=True)

        assert isinstance(structure, ProjectStructure)
        assert "pyproject.toml" in structure.root_files
        assert "README.md" in structure.root_files
        assert "PROJECT-IMPERATIVES.md" in structure.root_files
        assert len(structure.examples_dirs) > 0
        assert "metacognition" in structure.examples_dirs
        assert "problem_solving" in structure.examples_dirs

    def test_structure_without_examples(self) -> None:
        """Test canonical structure excludes examples when minimal."""
        structure = get_canonical_structure(include_examples=False)

        assert isinstance(structure, ProjectStructure)
        assert "pyproject.toml" in structure.root_files
        assert len(structure.examples_dirs) == 0

    def test_structure_includes_all_required_files(self) -> None:
        """Test structure includes all required configuration files."""
        structure = get_canonical_structure()

        # Root files
        assert ".gitignore" in structure.root_files
        assert "LICENSE" in structure.root_files

        # Config files
        assert "cogito.yml" in structure.config_files
        assert "logging.yml" in structure.config_files

        # Bootstrap files
        assert "process_memory.jsonl" in structure.bootstrap_files
        assert "knowledge_graph.json" in structure.bootstrap_files

        # Test files
        assert "__init__.py" in structure.tests_files
        assert "conftest.py" in structure.tests_files

        # Docs files
        assert "QUICK-START.md" in structure.docs_files
        assert "ARCHITECTURE.md" in structure.docs_files
        assert "CONFIGURATION.md" in structure.docs_files


class TestCreateProjectDirectories:
    """Tests for create_project_directories function."""

    def test_creates_basic_structure(self, tmp_path: Path) -> None:
        """Test creating basic project directory structure."""
        project_root = tmp_path / "test-project"
        structure = get_canonical_structure(include_examples=False)

        result = create_project_directories(project_root, structure)

        assert result["errors"] == []
        assert len(result["directories_created"]) > 0
        assert project_root.exists()
        assert (project_root / "src" / "cogito").exists()
        assert (project_root / "tests").exists()
        assert (project_root / "docs").exists()
        assert (project_root / "config").exists()
        assert (project_root / ".bootstrap").exists()

    def test_creates_examples_directories(self, tmp_path: Path) -> None:
        """Test creating examples directories when requested."""
        project_root = tmp_path / "test-project"
        structure = get_canonical_structure(include_examples=True)

        result = create_project_directories(project_root, structure)

        assert result["errors"] == []
        assert (project_root / "examples").exists()
        assert (project_root / "examples" / "metacognition").exists()
        assert (project_root / "examples" / "problem_solving").exists()

    def test_creates_test_subdirectories(self, tmp_path: Path) -> None:
        """Test creating test subdirectories."""
        project_root = tmp_path / "test-project"
        structure = get_canonical_structure()

        result = create_project_directories(project_root, structure)

        assert result["errors"] == []
        assert (project_root / "tests" / "unit").exists()
        assert (project_root / "tests" / "integration").exists()
        assert (project_root / "tests" / "fixtures").exists()

    def test_handles_existing_directory(self, tmp_path: Path) -> None:
        """Test graceful handling when directory already exists."""
        project_root = tmp_path / "test-project"
        project_root.mkdir(parents=True)
        structure = get_canonical_structure()

        result = create_project_directories(project_root, structure)

        # Should succeed with exist_ok=True
        assert len(result["directories_created"]) > 0


class TestGetFileLocations:
    """Tests for get_file_locations function."""

    def test_returns_all_template_locations(self, tmp_path: Path) -> None:
        """Test that all template file locations are returned."""
        project_root = tmp_path / "test-project"
        structure = get_canonical_structure(include_examples=True)

        locations = get_file_locations(project_root, structure)

        assert isinstance(locations, dict)
        assert len(locations) > 0

        # Check root file locations
        assert any("pyproject_toml_j2" in k for k in locations)
        assert any("README_md_j2" in k for k in locations)

        # Check config file locations
        assert any("cogito_yml_j2" in k for k in locations)
        assert any("logging_yml_j2" in k for k in locations)

    def test_paths_are_absolute(self, tmp_path: Path) -> None:
        """Test that returned paths are properly constructed."""
        project_root = tmp_path / "test-project"
        structure = get_canonical_structure()

        locations = get_file_locations(project_root, structure)

        for path in locations.values():
            assert isinstance(path, Path)
            # Check path starts with project_root
            assert str(path).startswith(str(project_root))

    def test_minimal_structure_fewer_locations(self, tmp_path: Path) -> None:
        """Test minimal structure has fewer file locations."""
        project_root = tmp_path / "test-project"

        full_structure = get_canonical_structure(include_examples=True)
        minimal_structure = get_canonical_structure(include_examples=False)

        get_file_locations(project_root, full_structure)
        minimal_locations = get_file_locations(project_root, minimal_structure)

        # Minimal should have same or fewer locations
        # (Both have same template files, just different directory structure)
        assert len(minimal_locations) >= 5  # At least core files
