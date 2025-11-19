"""Unit tests for ProcessMemoryImporter."""

import json
from pathlib import Path

import pytest
import yaml

from cogito.provisioning.importer import ProcessMemoryImporter
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def temp_memory_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create temporary process memory store."""
    memory_file = tmp_path / "test_memory.jsonl"
    return ProcessMemoryStore(memory_file)


@pytest.fixture
def valid_entry() -> dict:
    """Sample valid process memory entry."""
    return {
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Test Decision",
        "summary": "A test decision summary",
        "rationale": "Test rationale",
        "related_concepts": ["testing"],
        "tags": ["test"],
        "confidence_level": 0.9,
    }


def test_import_from_json_single_entry(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test importing single entry from JSON."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(valid_entry), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 1
    assert len(errors) == 0

    # Verify entry was added
    entry = temp_memory_store.get_entry("test-001")
    assert entry is not None
    assert entry["title"] == "Test Decision"


def test_import_from_json_multiple_entries(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test importing multiple entries from JSON."""
    importer = ProcessMemoryImporter(temp_memory_store)

    entries = [
        valid_entry,
        {
            "id": "test-002",
            "type": "LessonLearned",
            "title": "Test Lesson",
            "summary": "A test lesson",
        },
    ]

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(entries), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 2
    assert len(errors) == 0

    # Verify entries were added
    assert temp_memory_store.get_entry("test-001") is not None
    assert temp_memory_store.get_entry("test-002") is not None


def test_import_from_yaml(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test importing from YAML."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create YAML file
    yaml_file = tmp_path / "import.yaml"
    yaml_file.write_text(yaml.dump([valid_entry]), encoding="utf-8")

    # Import
    count, errors = importer.import_from_yaml(yaml_file, merge=True)

    assert count == 1
    assert len(errors) == 0

    # Verify entry was added
    entry = temp_memory_store.get_entry("test-001")
    assert entry is not None


def test_import_from_jsonl(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test importing from JSONL."""
    importer = ProcessMemoryImporter(temp_memory_store)

    entry2 = {
        "id": "test-002",
        "type": "LessonLearned",
        "title": "Test Lesson",
        "summary": "A test lesson",
    }

    # Create JSONL file
    jsonl_file = tmp_path / "import.jsonl"
    with jsonl_file.open("w", encoding="utf-8") as f:
        f.write(json.dumps(valid_entry) + "\n")
        f.write(json.dumps(entry2) + "\n")

    # Import
    count, errors = importer.import_from_jsonl(jsonl_file, merge=True)

    assert count == 2
    assert len(errors) == 0

    # Verify entries were added
    assert temp_memory_store.get_entry("test-001") is not None
    assert temp_memory_store.get_entry("test-002") is not None


def test_import_validation_only(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test validation-only mode doesn't add entries."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(valid_entry), encoding="utf-8")

    # Import with merge=False
    count, errors = importer.import_from_json(json_file, merge=False)

    assert count == 1
    assert len(errors) == 0

    # Verify entry was NOT added
    entry = temp_memory_store.get_entry("test-001")
    assert entry is None


def test_import_missing_required_field(
    temp_memory_store: ProcessMemoryStore, tmp_path: Path
) -> None:
    """Test validation catches missing required fields."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Entry missing 'summary'
    invalid_entry = {
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Test Decision",
    }

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(invalid_entry), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 0
    assert len(errors) == 1
    assert "Missing required fields" in errors[0]
    assert "summary" in errors[0]


def test_import_invalid_field_type(
    temp_memory_store: ProcessMemoryStore, tmp_path: Path
) -> None:
    """Test validation catches invalid field types."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Entry with tags as string instead of list
    invalid_entry = {
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Test Decision",
        "summary": "A test decision",
        "tags": "invalid-not-a-list",
    }

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(invalid_entry), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 0
    assert len(errors) == 1
    assert "'tags' must be a list" in errors[0]


def test_import_partial_success(
    temp_memory_store: ProcessMemoryStore, valid_entry: dict, tmp_path: Path
) -> None:
    """Test importing with some valid and some invalid entries."""
    importer = ProcessMemoryImporter(temp_memory_store)

    invalid_entry = {
        "id": "test-002",
        "type": "LessonLearned",
        # Missing title and summary
    }

    entries = [valid_entry, invalid_entry]

    # Create JSON file
    json_file = tmp_path / "import.json"
    json_file.write_text(json.dumps(entries), encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 1  # Only valid entry imported
    assert len(errors) == 1  # One error for invalid entry

    # Verify only valid entry was added
    assert temp_memory_store.get_entry("test-001") is not None
    assert temp_memory_store.get_entry("test-002") is None


def test_import_invalid_json(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test importing invalid JSON raises error."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create invalid JSON file
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{ invalid json }", encoding="utf-8")

    # Import should raise JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        importer.import_from_json(json_file, merge=True)


def test_import_invalid_jsonl(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test importing invalid JSONL raises error."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create JSONL file with invalid line
    jsonl_file = tmp_path / "invalid.jsonl"
    with jsonl_file.open("w", encoding="utf-8") as f:
        f.write('{"id": "test-001", "type": "Test", "title": "Valid", "summary": "Valid"}\n')
        f.write("{ invalid json }\n")

    # Import should raise JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        importer.import_from_jsonl(jsonl_file, merge=True)


def test_import_not_dict_or_list(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test importing non-dict/non-list data."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create JSON file with string
    json_file = tmp_path / "import.json"
    json_file.write_text('"not a dict or list"', encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 0
    assert len(errors) == 1
    assert "Invalid data type" in errors[0]


def test_import_empty_list(temp_memory_store: ProcessMemoryStore, tmp_path: Path) -> None:
    """Test importing empty list."""
    importer = ProcessMemoryImporter(temp_memory_store)

    # Create JSON file with empty list
    json_file = tmp_path / "import.json"
    json_file.write_text("[]", encoding="utf-8")

    # Import
    count, errors = importer.import_from_json(json_file, merge=True)

    assert count == 0
    assert len(errors) == 0
