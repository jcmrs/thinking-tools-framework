"""Integration tests for provisioning CLI commands."""

from pathlib import Path
import json

import pytest
from click.testing import CliRunner

from cogito.ui.cli import cli
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def sample_memory_file(tmp_path: Path) -> Path:
    """Create sample process memory file."""
    memory_file = tmp_path / "test_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    store.append_entry({
        "id": "cli-test-001",
        "type": "StrategicDecision",
        "title": "CLI Testing Strategy",
        "summary": "Use Click testing utilities",
        "tags": ["cli", "testing"],
    })

    store.append_entry({
        "id": "cli-test-002",
        "type": "LessonLearned",
        "title": "CLI UX Matters",
        "summary": "Good CLI UX improves developer experience",
        "tags": ["cli", "ux"],
    })

    return memory_file


def test_memory_export_markdown_command(sample_memory_file: Path, tmp_path: Path) -> None:
    """Test cogito memory export markdown command."""
    runner = CliRunner()
    output_file = tmp_path / "export.md"

    result = runner.invoke(
        cli,
        [
            "memory",
            "export",
            "markdown",
            "--memory-file",
            str(sample_memory_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check content
    content = output_file.read_text(encoding="utf-8")
    assert "# Process Memory" in content
    assert "CLI Testing Strategy" in content


def test_memory_export_json_command(sample_memory_file: Path, tmp_path: Path) -> None:
    """Test cogito memory export json command."""
    runner = CliRunner()
    output_file = tmp_path / "export.json"

    result = runner.invoke(
        cli,
        [
            "memory",
            "export",
            "json",
            "--memory-file",
            str(sample_memory_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check valid JSON
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2


def test_memory_export_yaml_command(sample_memory_file: Path, tmp_path: Path) -> None:
    """Test cogito memory export yaml command."""
    runner = CliRunner()
    output_file = tmp_path / "export.yaml"

    result = runner.invoke(
        cli,
        [
            "memory",
            "export",
            "yaml",
            "--memory-file",
            str(sample_memory_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check content
    content = output_file.read_text(encoding="utf-8")
    assert "id: cli-test-001" in content


def test_memory_export_to_stdout(sample_memory_file: Path) -> None:
    """Test exporting to stdout when no output file specified."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["memory", "export", "markdown", "--memory-file", str(sample_memory_file)],
    )

    assert result.exit_code == 0
    assert "# Process Memory" in result.output
    assert "CLI Testing Strategy" in result.output


def test_memory_export_with_category_filter(sample_memory_file: Path) -> None:
    """Test export with category filter."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "memory",
            "export",
            "markdown",
            "--memory-file",
            str(sample_memory_file),
            "--category",
            "StrategicDecision",
        ],
    )

    assert result.exit_code == 0
    assert "CLI Testing Strategy" in result.output
    assert "CLI UX Matters" not in result.output


def test_memory_import_json_command(tmp_path: Path) -> None:
    """Test cogito memory import command with JSON."""
    # Create import file
    import_data = [
        {
            "id": "import-001",
            "type": "StrategicDecision",
            "title": "Import Test",
            "summary": "Testing import functionality",
        }
    ]
    import_file = tmp_path / "import.json"
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    # Create destination memory file
    memory_file = tmp_path / "imported_memory.jsonl"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["memory", "import", str(import_file), "--memory-file", str(memory_file)],
    )

    assert result.exit_code == 0
    assert "Imported 1 entries" in result.output

    # Verify import
    store = ProcessMemoryStore(memory_file)
    entry = store.get_entry("import-001")
    assert entry is not None
    assert entry["title"] == "Import Test"


def test_memory_import_with_format_specification(tmp_path: Path) -> None:
    """Test import with explicit format specification."""
    # Create YAML import file with .txt extension
    import_data = [
        {
            "id": "import-002",
            "type": "LessonLearned",
            "title": "Format Test",
            "summary": "Testing format specification",
        }
    ]
    import yaml
    import_file = tmp_path / "import.txt"
    import_file.write_text(yaml.dump(import_data), encoding="utf-8")

    memory_file = tmp_path / "imported_memory.jsonl"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "memory",
            "import",
            str(import_file),
            "--format",
            "yaml",
            "--memory-file",
            str(memory_file),
        ],
    )

    assert result.exit_code == 0
    assert "Imported 1 entries" in result.output


def test_memory_import_validate_only(tmp_path: Path) -> None:
    """Test import with validation-only mode."""
    import_data = [
        {
            "id": "validate-001",
            "type": "StrategicDecision",
            "title": "Validation Test",
            "summary": "Testing validation",
        }
    ]
    import_file = tmp_path / "import.json"
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    memory_file = tmp_path / "not_imported_memory.jsonl"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "memory",
            "import",
            str(import_file),
            "--validate-only",
            "--memory-file",
            str(memory_file),
        ],
    )

    assert result.exit_code == 0
    assert "Validation: 1 entries valid" in result.output

    # Memory file should not exist (validation only)
    assert not memory_file.exists()


def test_memory_import_with_errors(tmp_path: Path) -> None:
    """Test import with validation errors."""
    # Invalid entry missing required fields
    import_data = [
        {
            "id": "invalid-001",
            # Missing type, title, summary
        }
    ]
    import_file = tmp_path / "invalid.json"
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    memory_file = tmp_path / "imported_memory.jsonl"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["memory", "import", str(import_file), "--memory-file", str(memory_file)],
    )

    # Should fail with validation errors
    assert result.exit_code == 1
    assert "Validation errors" in result.output


def test_memory_handover_command(sample_memory_file: Path, tmp_path: Path) -> None:
    """Test cogito memory handover command."""
    runner = CliRunner()
    output_file = tmp_path / "handover.md"

    result = runner.invoke(
        cli,
        [
            "memory",
            "handover",
            "--memory-file",
            str(sample_memory_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check content
    content = output_file.read_text(encoding="utf-8")
    assert "# Session Handover Document" in content
    assert "2 process memory entries" in content


def test_memory_handover_to_stdout(sample_memory_file: Path) -> None:
    """Test handover to stdout."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["memory", "handover", "--memory-file", str(sample_memory_file)],
    )

    assert result.exit_code == 0
    assert "# Session Handover Document" in result.output


def test_memory_context_command(sample_memory_file: Path) -> None:
    """Test cogito memory context command."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["memory", "context", "cli", "--memory-file", str(sample_memory_file)],
    )

    assert result.exit_code == 0
    assert "# Context: cli" in result.output
    assert "CLI Testing Strategy" in result.output


def test_memory_context_with_max_entries(sample_memory_file: Path) -> None:
    """Test context with max entries limit."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "memory",
            "context",
            "cli",
            "--max-entries",
            "1",
            "--memory-file",
            str(sample_memory_file),
        ],
    )

    assert result.exit_code == 0
    assert "Showing top 1" in result.output


def test_memory_context_no_related(sample_memory_file: Path) -> None:
    """Test context without related entries."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "memory",
            "context",
            "cli",
            "--no-related",
            "--memory-file",
            str(sample_memory_file),
        ],
    )

    assert result.exit_code == 0
    # Should not have related entries section
    assert "## Related Entries" not in result.output


def test_cli_end_to_end_workflow(tmp_path: Path) -> None:
    """Test complete workflow: create, export, import to new store."""
    runner = CliRunner()

    # Create source memory
    source_memory = tmp_path / "source.jsonl"
    store = ProcessMemoryStore(source_memory)
    store.append_entry({
        "id": "workflow-001",
        "type": "StrategicDecision",
        "title": "Workflow Test",
        "summary": "End-to-end workflow testing",
    })

    # Export
    export_file = tmp_path / "export.json"
    result = runner.invoke(
        cli,
        ["memory", "export", "json", "--memory-file", str(source_memory), "--output", str(export_file)],
    )
    assert result.exit_code == 0

    # Import to new store
    dest_memory = tmp_path / "destination.jsonl"
    result = runner.invoke(
        cli,
        ["memory", "import", str(export_file), "--memory-file", str(dest_memory)],
    )
    assert result.exit_code == 0

    # Verify
    dest_store = ProcessMemoryStore(dest_memory)
    entry = dest_store.get_entry("workflow-001")
    assert entry is not None
    assert entry["title"] == "Workflow Test"
