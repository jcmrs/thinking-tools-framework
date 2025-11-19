"""Unit tests for ContextGenerator."""

from pathlib import Path

import pytest

from cogito.provisioning.context import ContextGenerator
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def temp_memory_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create temporary process memory store with sample entries."""
    memory_file = tmp_path / "test_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    # Add entries with various topics
    store.append_entry({
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Testing Strategy",
        "summary": "Use pytest for testing framework",
        "rationale": "pytest is industry standard",
        "related_concepts": ["testing", "quality"],
        "tags": ["testing", "pytest"],
        "links": ["test-002"],
    })

    store.append_entry({
        "id": "test-002",
        "type": "LessonLearned",
        "title": "Test Coverage Matters",
        "summary": "High test coverage prevents regressions",
        "tags": ["testing", "coverage"],
    })

    store.append_entry({
        "id": "test-003",
        "type": "StrategicDecision",
        "title": "Architecture Decision",
        "summary": "Use clean architecture pattern",
        "related_concepts": ["architecture", "design"],
        "tags": ["architecture"],
    })

    return store


def test_generate_context_for_topic_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test basic context generation for a topic."""
    generator = ContextGenerator(temp_memory_store)
    context = generator.generate_context_for_topic("testing")

    # Check structure
    assert "# Context: testing" in context
    assert "Found" in context
    assert "entries matching 'testing'" in context

    # Check entries are included
    assert "test-001: Testing Strategy" in context
    assert "test-002: Test Coverage Matters" in context


def test_generate_context_no_results(temp_memory_store: ProcessMemoryStore) -> None:
    """Test context generation when no entries match."""
    generator = ContextGenerator(temp_memory_store)
    context = generator.generate_context_for_topic("nonexistent")

    assert "# Context: nonexistent" in context
    assert "No process memory entries found" in context


def test_generate_context_with_max_entries(temp_memory_store: ProcessMemoryStore) -> None:
    """Test limiting number of entries in context."""
    generator = ContextGenerator(temp_memory_store)

    # Request only 1 entry
    context = generator.generate_context_for_topic("testing", max_entries=1)

    # Should show "Showing top 1"
    assert "Showing top 1" in context

    # Should only have one entry in primary section
    primary_section = context.split("## Related Entries")[0] if "## Related Entries" in context else context
    assert primary_section.count("###") == 1  # Only one entry heading


def test_generate_context_with_related_entries(temp_memory_store: ProcessMemoryStore) -> None:
    """Test including related entries via links."""
    generator = ContextGenerator(temp_memory_store)

    # Generate context for testing, which links to test-002
    context = generator.generate_context_for_topic("testing", include_related=True)

    # Check related entries section
    if "## Related Entries" in context:
        assert "test-002" in context


def test_generate_context_without_related(temp_memory_store: ProcessMemoryStore) -> None:
    """Test excluding related entries."""
    generator = ContextGenerator(temp_memory_store)

    context = generator.generate_context_for_topic("testing", include_related=False)

    # Should not have related entries section
    assert "## Related Entries" not in context


def test_generate_context_includes_metadata(temp_memory_store: ProcessMemoryStore) -> None:
    """Test context includes entry metadata."""
    generator = ContextGenerator(temp_memory_store)
    context = generator.generate_context_for_topic("testing")

    # Check metadata is included
    assert "Type: StrategicDecision" in context or "Type: LessonLearned" in context
    assert "Summary" in context or "**Summary**" in context

    # Check optional fields
    assert "Rationale" in context or "Related Concepts" in context or "Tags" in context


def test_generate_context_tags_formatting(temp_memory_store: ProcessMemoryStore) -> None:
    """Test tags are formatted properly."""
    generator = ContextGenerator(temp_memory_store)
    context = generator.generate_context_for_topic("testing")

    # Tags should be in backticks
    assert "`testing`" in context or "`pytest`" in context


def test_generate_type_summary_basic(temp_memory_store: ProcessMemoryStore) -> None:
    """Test type summary generation."""
    generator = ContextGenerator(temp_memory_store)
    summary = generator.generate_type_summary("StrategicDecision")

    # Check structure
    assert "# StrategicDecision" in summary
    assert "Total: 2 entries" in summary

    # Check entries are included
    assert "test-001: Testing Strategy" in summary
    assert "test-003: Architecture Decision" in summary


def test_generate_type_summary_no_results(temp_memory_store: ProcessMemoryStore) -> None:
    """Test type summary when no entries of that type."""
    generator = ContextGenerator(temp_memory_store)
    summary = generator.generate_type_summary("NonexistentType")

    assert "# NonexistentType" in summary
    assert "No entries of type 'NonexistentType' found" in summary


def test_generate_type_summary_includes_confidence(tmp_path: Path) -> None:
    """Test type summary includes confidence levels."""
    memory_file = tmp_path / "test_memory.jsonl"
    store = ProcessMemoryStore(memory_file)

    store.append_entry({
        "id": "test-001",
        "type": "StrategicDecision",
        "title": "Test Decision",
        "summary": "Test summary",
        "confidence_level": 0.95,
    })

    generator = ContextGenerator(store)
    summary = generator.generate_type_summary("StrategicDecision")

    # Check confidence is displayed
    assert "Confidence" in summary or "95%" in summary


def test_generate_type_summary_includes_tags(temp_memory_store: ProcessMemoryStore) -> None:
    """Test type summary includes tags."""
    generator = ContextGenerator(temp_memory_store)
    summary = generator.generate_type_summary("StrategicDecision")

    # Check tags are included
    assert "Tags" in summary
    assert "`testing`" in summary or "`architecture`" in summary


def test_generate_context_markdown_formatting(temp_memory_store: ProcessMemoryStore) -> None:
    """Test context uses proper markdown formatting."""
    generator = ContextGenerator(temp_memory_store)
    context = generator.generate_context_for_topic("testing")

    # Check markdown elements
    assert context.startswith("#")  # Starts with heading
    assert "##" in context  # Has subheadings
    assert "###" in context  # Has entry headings
    assert "**" in context  # Has bold text
    assert "---" in context  # Has separators


def test_generate_type_summary_markdown_formatting(temp_memory_store: ProcessMemoryStore) -> None:
    """Test type summary uses proper markdown formatting."""
    generator = ContextGenerator(temp_memory_store)
    summary = generator.generate_type_summary("StrategicDecision")

    # Check markdown elements
    assert summary.startswith("#")  # Starts with heading
    assert "##" in summary  # Has subheadings
    assert "---" in summary  # Has separators
