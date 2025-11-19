"""Unit tests for ProcessMemoryExporter."""

from pathlib import Path
from tempfile import TemporaryDirectory

import json
import yaml
import pytest

from cogito.provisioning.exporter import ProcessMemoryExporter
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def temp_memory_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create temporary process memory store with sample entries."""
    memory_file = tmp_path / "test_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    # Add sample entries
    store.append_entry({
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Test Decision",
        "summary": "A test decision summary",
        "rationale": "Test rationale",
        "related_concepts": ["testing", "automation"],
        "tags": ["test", "decision"],
        "links": ["test-002"],
        "confidence_level": 0.9,
    })

    store.append_entry({
        "id": "test-002",
        "type": "LessonLearned",
        "title": "Test Lesson",
        "summary": "A test lesson summary",
        "tags": ["test", "learning"],
    })

    return store


def test_export_to_markdown_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test basic markdown export."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    markdown = exporter.export_to_markdown()

    assert "# Process Memory" in markdown
    assert "## StrategicDecision" in markdown
    assert "## LessonLearned" in markdown
    assert "test-001: Test Decision" in markdown
    assert "test-002: Test Lesson" in markdown
    assert "A test decision summary" in markdown


def test_export_to_markdown_with_file(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test markdown export to file."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    output_file = tmp_path / "export.md"

    markdown = exporter.export_to_markdown(output_path=output_file)

    # Check file was created
    assert output_file.exists()

    # Check content matches
    file_content = output_file.read_text(encoding="utf-8")
    assert file_content == markdown


def test_export_to_markdown_with_category_filter(temp_memory_store: ProcessMemoryStore) -> None:
    """Test markdown export with category filter."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    markdown = exporter.export_to_markdown(category="StrategicDecision")

    assert "test-001: Test Decision" in markdown
    assert "test-002: Test Lesson" not in markdown


def test_export_to_markdown_with_tags_filter(temp_memory_store: ProcessMemoryStore) -> None:
    """Test markdown export with tags filter."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    markdown = exporter.export_to_markdown(tags=["learning"])

    assert "test-002: Test Lesson" in markdown
    assert "test-001: Test Decision" not in markdown


def test_export_to_json_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test basic JSON export."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    json_str = exporter.export_to_json()

    # Parse JSON
    data = json.loads(json_str)

    assert isinstance(data, list)
    assert len(data) == 2

    # Check entry structure
    ids = {entry["id"] for entry in data}
    assert "test-001" in ids
    assert "test-002" in ids


def test_export_to_json_pretty(temp_memory_store: ProcessMemoryStore) -> None:
    """Test pretty-printed JSON export."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    json_str = exporter.export_to_json(pretty=True)

    # Pretty-printed JSON should have newlines and indentation
    assert "\n" in json_str
    assert "  " in json_str


def test_export_to_json_compact(temp_memory_store: ProcessMemoryStore) -> None:
    """Test compact JSON export."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    json_str = exporter.export_to_json(pretty=False)

    # Compact JSON should be single line
    assert json_str.count("\n") == 0


def test_export_to_json_with_file(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test JSON export to file."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    output_file = tmp_path / "export.json"

    json_str = exporter.export_to_json(output_path=output_file)

    # Check file was created
    assert output_file.exists()

    # Check content matches
    file_content = output_file.read_text(encoding="utf-8")
    assert file_content == json_str


def test_export_to_yaml_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test basic YAML export."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    yaml_str = exporter.export_to_yaml()

    # Parse YAML
    data = yaml.safe_load(yaml_str)

    assert isinstance(data, list)
    assert len(data) == 2

    # Check entry structure
    ids = {entry["id"] for entry in data}
    assert "test-001" in ids
    assert "test-002" in ids


def test_export_to_yaml_with_file(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test YAML export to file."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    output_file = tmp_path / "export.yaml"

    yaml_str = exporter.export_to_yaml(output_path=output_file)

    # Check file was created
    assert output_file.exists()

    # Check content matches
    file_content = output_file.read_text(encoding="utf-8")
    assert file_content == yaml_str


def test_export_roundtrip_json(temp_memory_store: ProcessMemoryStore) -> None:
    """Test JSON export can be parsed back."""
    exporter = ProcessMemoryExporter(temp_memory_store)
    json_str = exporter.export_to_json()

    # Parse back
    data = json.loads(json_str)

    # Verify all entries preserved
    assert len(data) == 2

    # Check first entry has all fields
    entry = next(e for e in data if e["id"] == "test-001")
    assert entry["type"] == "StrategicDecision"
    assert entry["title"] == "Test Decision"
    assert entry["summary"] == "A test decision summary"
    assert entry["rationale"] == "Test rationale"
    assert entry["related_concepts"] == ["testing", "automation"]
    assert entry["tags"] == ["test", "decision"]


def test_export_empty_store(tmp_path: Path) -> None:
    """Test exporting from empty store."""
    memory_file = tmp_path / "empty_memory.jsonl"
    store = ProcessMemoryStore(memory_file)
    exporter = ProcessMemoryExporter(store)

    markdown = exporter.export_to_markdown()
    assert "# Process Memory" in markdown

    json_str = exporter.export_to_json()
    assert json.loads(json_str) == []

    yaml_str = exporter.export_to_yaml()
    assert yaml.safe_load(yaml_str) == []
