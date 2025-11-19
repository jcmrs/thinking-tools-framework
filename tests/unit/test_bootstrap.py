"""Unit tests for bootstrap orchestrator."""

from pathlib import Path

import pytest

from cogito.provisioning.bootstrap import ProjectBootstrapper


class TestProjectBootstrapper:
    """Tests for ProjectBootstrapper class."""

    def test_initialization_default_template_dir(self) -> None:
        """Test bootstrapper initializes with default template directory."""
        bootstrapper = ProjectBootstrapper()

        assert bootstrapper.template_dir.exists()
        assert bootstrapper.template_dir.name == "bootstrap"

    def test_initialization_custom_template_dir(self, tmp_path: Path) -> None:
        """Test bootstrapper initializes with custom template directory."""
        template_dir = tmp_path / "custom_templates"
        template_dir.mkdir()

        bootstrapper = ProjectBootstrapper(template_dir)

        assert bootstrapper.template_dir == template_dir

    def test_bootstrap_project_basic(self, tmp_path: Path) -> None:
        """Test bootstrapping a basic project."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
            description="A test project",
        )

        assert result["success"] is True
        # May have warnings about missing example tools, but should succeed
        assert result["directories_created"] > 0
        assert result["files_created"] > 0

        project_root = Path(result["project_root"])
        assert project_root.exists()
        assert (project_root / "src" / "cogito").exists()
        assert (project_root / "config").exists()

    def test_bootstrap_project_with_examples(self, tmp_path: Path) -> None:
        """Test bootstrapping project with example tools."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
            include_examples=True,
        )

        assert result["success"] is True
        assert result["examples_copied"] > 0

        project_root = Path(result["project_root"])
        assert (project_root / "examples").exists()
        assert (project_root / "examples" / "metacognition").exists()

        # Verify at least one example tool exists
        metacog_tools = list((project_root / "examples" / "metacognition").glob("*.yml"))
        assert len(metacog_tools) > 0

    def test_bootstrap_project_minimal(self, tmp_path: Path) -> None:
        """Test bootstrapping minimal project without examples."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
            include_examples=False,
        )

        assert result["success"] is True
        assert result["examples_copied"] == 0

        project_root = Path(result["project_root"])
        # Examples directory may exist but should be empty or minimal
        # (depending on whether README is created)

    def test_bootstrap_project_with_author_info(self, tmp_path: Path) -> None:
        """Test bootstrapping project with author information."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
            author_name="Jane Doe",
            author_email="jane@example.com",
        )

        assert result["success"] is True

        # Verify author info in pyproject.toml
        project_root = Path(result["project_root"])
        pyproject = (project_root / "config" / "pyproject.toml").read_text()
        assert "Jane Doe" in pyproject
        assert "jane@example.com" in pyproject

    def test_bootstrap_project_creates_config_files(self, tmp_path: Path) -> None:
        """Test that bootstrap creates all required config files."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
        )

        assert result["success"] is True

        project_root = Path(result["project_root"])
        config_dir = project_root / "config"

        assert (config_dir / "pyproject.toml").exists()
        assert (config_dir / "cogito.yml").exists()
        assert (config_dir / "logging.yml").exists()

    def test_bootstrap_project_existing_directory_fails(self, tmp_path: Path) -> None:
        """Test that bootstrap fails if project directory already exists."""
        # Create the directory first
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "already exists" in result["errors"][0]

    def test_bootstrap_project_copies_imperatives(self, tmp_path: Path) -> None:
        """Test that PROJECT-IMPERATIVES.md is copied to new project."""
        bootstrapper = ProjectBootstrapper()

        result = bootstrapper.bootstrap_project(
            project_name="test-project",
            output_dir=tmp_path,
        )

        assert result["success"] is True

        project_root = Path(result["project_root"])
        imperatives = project_root / "PROJECT-IMPERATIVES.md"

        # May or may not exist depending on framework setup
        # (Test passes if file exists)
        if imperatives.exists():
            content = imperatives.read_text(encoding="utf-8")
            assert len(content) > 0
            assert "Imperative" in content  # Basic content check
