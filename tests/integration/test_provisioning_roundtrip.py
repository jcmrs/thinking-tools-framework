"""Integration tests for provisioning system roundtrip scenarios."""

from pathlib import Path
import json

import pytest

from cogito.provisioning.exporter import ProcessMemoryExporter
from cogito.provisioning.importer import ProcessMemoryImporter
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def source_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create source process memory store with comprehensive test data."""
    memory_file = tmp_path / "source_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    # Add diverse entries
    store.append_entry({
        "id": "pm-001",
        "type": "StrategicDecision",
        "title": "YAML Specification Format",
        "summary": "Selected YAML over JSON and TOML",
        "rationale": "Human readability and accessibility",
        "related_concepts": ["accessibility", "declarative-design"],
        "tags": ["format", "yaml"],
        "links": ["pm-002"],
        "confidence_level": 0.9,
    })

    store.append_entry({
        "id": "pm-002",
        "type": "LessonLearned",
        "title": "JSON Schema Validation",
        "summary": "Use JSON Schema for parameter validation",
        "tags": ["validation", "schema"],
        "confidence_level": 0.85,
    })

    store.append_entry({
        "id": "pm-003",
        "type": "Observation",
        "title": "Template Rendering Performance",
        "summary": "Jinja2 rendering is fast enough for our use case",
        "related_concepts": ["performance", "rendering"],
        "tags": ["performance"],
        "confidence_level": 0.7,
    })

    return store


@pytest.fixture
def destination_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create empty destination process memory store."""
    memory_file = tmp_path / "destination_memory.jsonl"
    return ProcessMemoryStore(memory_file)


def test_json_export_import_roundtrip(
    source_store: ProcessMemoryStore,
    destination_store: ProcessMemoryStore,
    tmp_path: Path,
) -> None:
    """Test exporting to JSON and importing back preserves all data."""
    exporter = ProcessMemoryExporter(source_store)
    importer = ProcessMemoryImporter(destination_store)

    # Export to JSON
    export_file = tmp_path / "export.json"
    exporter.export_to_json(output_path=export_file)

    # Import back
    count, errors = importer.import_from_json(export_file, merge=True)

    # Verify
    assert count == 3
    assert len(errors) == 0

    # Check all entries preserved
    for entry_id in ["pm-001", "pm-002", "pm-003"]:
        original = source_store.get_entry(entry_id)
        imported = destination_store.get_entry(entry_id)

        assert imported is not None
        assert imported["id"] == original["id"]
        assert imported["type"] == original["type"]
        assert imported["title"] == original["title"]
        assert imported["summary"] == original["summary"]

        # Check optional fields preserved
        if "rationale" in original:
            assert imported["rationale"] == original["rationale"]
        if "related_concepts" in original:
            assert imported["related_concepts"] == original["related_concepts"]
        if "tags" in original:
            assert imported["tags"] == original["tags"]
        if "links" in original:
            assert imported["links"] == original["links"]


def test_yaml_export_import_roundtrip(
    source_store: ProcessMemoryStore,
    destination_store: ProcessMemoryStore,
    tmp_path: Path,
) -> None:
    """Test exporting to YAML and importing back preserves all data."""
    exporter = ProcessMemoryExporter(source_store)
    importer = ProcessMemoryImporter(destination_store)

    # Export to YAML
    export_file = tmp_path / "export.yaml"
    exporter.export_to_yaml(output_path=export_file)

    # Import back
    count, errors = importer.import_from_yaml(export_file, merge=True)

    # Verify
    assert count == 3
    assert len(errors) == 0

    # Check entries preserved
    assert destination_store.get_entry("pm-001") is not None
    assert destination_store.get_entry("pm-002") is not None
    assert destination_store.get_entry("pm-003") is not None


def test_filtered_export_import(
    source_store: ProcessMemoryStore,
    destination_store: ProcessMemoryStore,
    tmp_path: Path,
) -> None:
    """Test exporting filtered subset and importing."""
    exporter = ProcessMemoryExporter(source_store)
    importer = ProcessMemoryImporter(destination_store)

    # Export only StrategicDecision entries
    export_file = tmp_path / "filtered_export.json"
    exporter.export_to_json(output_path=export_file, category="StrategicDecision")

    # Import
    count, errors = importer.import_from_json(export_file, merge=True)

    # Verify only StrategicDecision imported
    assert count == 1
    assert destination_store.get_entry("pm-001") is not None
    assert destination_store.get_entry("pm-002") is None
    assert destination_store.get_entry("pm-003") is None


def test_multiple_format_consistency(
    source_store: ProcessMemoryStore, tmp_path: Path
) -> None:
    """Test exporting to different formats produces consistent data."""
    exporter = ProcessMemoryExporter(source_store)

    # Export to all formats
    json_file = tmp_path / "export.json"
    yaml_file = tmp_path / "export.yaml"

    exporter.export_to_json(output_path=json_file)
    exporter.export_to_yaml(output_path=yaml_file)

    # Import both
    json_store = ProcessMemoryStore(tmp_path / "json_store.jsonl")
    yaml_store = ProcessMemoryStore(tmp_path / "yaml_store.jsonl")

    json_importer = ProcessMemoryImporter(json_store)
    yaml_importer = ProcessMemoryImporter(yaml_store)

    json_count, _ = json_importer.import_from_json(json_file, merge=True)
    yaml_count, _ = yaml_importer.import_from_yaml(yaml_file, merge=True)

    # Both should have same count
    assert json_count == yaml_count == 3

    # Verify same entries in both
    for entry_id in ["pm-001", "pm-002", "pm-003"]:
        json_entry = json_store.get_entry(entry_id)
        yaml_entry = yaml_store.get_entry(entry_id)

        assert json_entry is not None
        assert yaml_entry is not None
        assert json_entry["title"] == yaml_entry["title"]
        assert json_entry["summary"] == yaml_entry["summary"]


def test_incremental_import(
    source_store: ProcessMemoryStore,
    destination_store: ProcessMemoryStore,
    tmp_path: Path,
) -> None:
    """Test importing additional entries doesn't duplicate existing ones."""
    exporter = ProcessMemoryExporter(source_store)
    importer = ProcessMemoryImporter(destination_store)

    # First import
    export_file = tmp_path / "export.json"
    exporter.export_to_json(output_path=export_file)
    count1, _ = importer.import_from_json(export_file, merge=True)

    assert count1 == 3

    # Add new entry to source
    source_store.append_entry({
        "id": "pm-004",
        "type": "StrategicDecision",
        "title": "New Decision",
        "summary": "A new decision",
    })

    # Export again
    exporter.export_to_json(output_path=export_file)

    # Import again
    count2, _ = importer.import_from_json(export_file, merge=True)

    # Should import 4 entries (ProcessMemoryStore handles duplicates)
    assert count2 == 4

    # All entries should be present
    assert destination_store.get_entry("pm-001") is not None
    assert destination_store.get_entry("pm-004") is not None


def test_validation_before_import(
    source_store: ProcessMemoryStore,
    destination_store: ProcessMemoryStore,
    tmp_path: Path,
) -> None:
    """Test validation-only mode before actual import."""
    exporter = ProcessMemoryExporter(source_store)
    importer = ProcessMemoryImporter(destination_store)

    # Export
    export_file = tmp_path / "export.json"
    exporter.export_to_json(output_path=export_file)

    # Validate first
    count, errors = importer.import_from_json(export_file, merge=False)

    assert count == 3
    assert len(errors) == 0

    # Destination should still be empty
    assert destination_store.get_entry("pm-001") is None

    # Now actually import
    count, errors = importer.import_from_json(export_file, merge=True)

    assert count == 3
    assert destination_store.get_entry("pm-001") is not None


def test_import_with_validation_errors_rollback(
    destination_store: ProcessMemoryStore, tmp_path: Path
) -> None:
    """Test that partial failures don't corrupt the store."""
    importer = ProcessMemoryImporter(destination_store)

    # Create file with mix of valid and invalid entries
    mixed_data = [
        {
            "id": "valid-001",
            "type": "StrategicDecision",
            "title": "Valid Entry",
            "summary": "Valid summary",
        },
        {
            "id": "invalid-001",
            "type": "Invalid",
            # Missing title and summary
        },
        {
            "id": "valid-002",
            "type": "LessonLearned",
            "title": "Another Valid",
            "summary": "Another valid summary",
        },
    ]

    import_file = tmp_path / "mixed.json"
    import_file.write_text(json.dumps(mixed_data), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(import_file, merge=True)

    # Should import valid entries only
    assert count == 2
    assert len(errors) == 1

    # Verify valid entries imported
    assert destination_store.get_entry("valid-001") is not None
    assert destination_store.get_entry("valid-002") is not None
    assert destination_store.get_entry("invalid-001") is None
