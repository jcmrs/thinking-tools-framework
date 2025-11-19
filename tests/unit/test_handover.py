"""Unit tests for HandoverGenerator."""

from pathlib import Path

import pytest

from cogito.provisioning.handover import HandoverGenerator
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
        "confidence_level": 0.95,
    })

    store.append_entry({
        "id": "test-002",
        "type": "LessonLearned",
        "title": "Test Lesson",
        "summary": "A test lesson summary",
        "tags": ["test", "learning"],
        "confidence_level": 0.75,
    })

    store.append_entry({
        "id": "test-003",
        "type": "Observation",
        "title": "Test Observation",
        "summary": "A test observation",
        "related_concepts": ["testing"],
        "confidence_level": 0.5,
    })

    return store


def test_generate_handover_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test basic handover document generation."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check structure
    assert "# Session Handover Document" in handover
    assert "## Executive Summary" in handover
    assert "3 process memory entries" in handover

    # Check statistics
    assert "StrategicDecision" in handover
    assert "LessonLearned" in handover
    assert "Observation" in handover


def test_generate_handover_statistics(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover includes correct statistics."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check confidence distribution
    assert "High confidence" in handover
    assert "Medium confidence" in handover
    assert "Low confidence" in handover

    # Verify counts (1 high ≥0.9, 1 medium 0.7-0.9, 1 low <0.7)
    assert "1 entries" in handover or "1 entry" in handover


def test_generate_handover_recent_entries(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover includes recent entries."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check recent entries section exists
    assert "## Recent" in handover

    # Check entries are present
    assert "test-001: Test Decision" in handover
    assert "test-002: Test Lesson" in handover
    assert "A test decision summary" in handover


def test_generate_handover_key_concepts(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover includes key concepts."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check key concepts section
    assert "## Key Concepts" in handover
    assert "testing" in handover
    assert "automation" in handover


def test_generate_handover_with_file(
    temp_memory_store: ProcessMemoryStore, tmp_path: Path
) -> None:
    """Test handover generation to file."""
    generator = HandoverGenerator(temp_memory_store)
    output_file = tmp_path / "handover.md"

    handover = generator.generate_handover_document(output_path=output_file)

    # Check file was created
    assert output_file.exists()

    # Check content matches
    file_content = output_file.read_text(encoding="utf-8")
    assert file_content == handover


def test_generate_handover_exclude_deprecated(tmp_path: Path) -> None:
    """Test excluding deprecated entries."""
    memory_file = tmp_path / "test_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    # Add active and deprecated entries
    store.append_entry({
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Active Entry",
        "summary": "Active summary",
        "deprecated": False,
    })

    store.append_entry({
        "id": "test-002",
        "type": "StrategicDecision",
        "title": "Deprecated Entry",
        "summary": "Deprecated summary",
        "deprecated": True,
    })

    generator = HandoverGenerator(store)

    # Generate without deprecated
    handover = generator.generate_handover_document(include_deprecated=False)
    assert "Active Entry" in handover
    assert "Deprecated Entry" not in handover

    # Generate with deprecated
    handover_with_deprecated = generator.generate_handover_document(include_deprecated=True)
    assert "Active Entry" in handover_with_deprecated
    assert "Deprecated Entry" in handover_with_deprecated


def test_generate_handover_empty_store(tmp_path: Path) -> None:
    """Test handover generation with empty store."""
    memory_file = tmp_path / "empty_memory.jsonl"
    store = ProcessMemoryStore(memory_file)
    generator = HandoverGenerator(store)

    handover = generator.generate_handover_document()

    # Should still generate valid handover
    assert "# Session Handover Document" in handover
    assert "0 process memory entries" in handover


def test_generate_handover_simple_fallback(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover generation works with template."""
    # The generator finds the actual template, so this tests template rendering
    generator = HandoverGenerator(temp_memory_store)

    handover = generator.generate_handover_document()

    # Check structure (from template)
    assert "# Session Handover Document" in handover
    assert "## Executive Summary" in handover
    assert "## Recent Activity" in handover or "## Recent Decisions" in handover
    assert "## Key Concepts" in handover


def test_handover_organizes_by_type(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover organizes entries by type."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check type sections
    assert "StrategicDecision" in handover
    assert "LessonLearned" in handover
    assert "Observation" in handover

    # Each type should show its count
    assert "1 entries" in handover or "entries in this category" in handover


def test_handover_includes_next_steps(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover includes actionable next steps."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check next steps section
    assert "## Next Steps" in handover
    assert "Review" in handover or "review" in handover


def test_handover_markdown_formatting(temp_memory_store: ProcessMemoryStore) -> None:
    """Test handover uses proper markdown formatting."""
    generator = HandoverGenerator(temp_memory_store)
    handover = generator.generate_handover_document()

    # Check markdown elements
    assert handover.startswith("#")  # Starts with heading
    assert "##" in handover  # Has subheadings
    assert "**" in handover  # Has bold text
    assert "---" in handover  # Has separators
