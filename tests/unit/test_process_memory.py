"""Unit tests for ProcessMemoryStore class."""

import json
from pathlib import Path
from typing import Any

import pytest

from cogito.storage.process_memory import ProcessMemoryError, ProcessMemoryStore


@pytest.fixture
def temp_memory_file(tmp_path: Path) -> Path:
    """Create temporary process memory file."""
    return tmp_path / "process_memory.jsonl"


@pytest.fixture
def sample_entry() -> dict[str, Any]:
    """Sample process memory entry."""
    return {
        "id": "pm-test-001",
        "type": "TestEntry",
        "title": "Test Entry",
        "summary": "A test entry for unit tests",
        "tags": ["test", "unit"],
        "links": ["pm-test-002"],
        "deprecated": False,
    }


class TestProcessMemoryStoreInit:
    """Test ProcessMemoryStore initialization."""

    def test_init_with_path(self, temp_memory_file: Path) -> None:
        """Test initialization with path."""
        store = ProcessMemoryStore(temp_memory_file)
        assert store._memory_path == temp_memory_file
        assert not store._cache_loaded

    def test_init_with_nonexistent_file(self, tmp_path: Path) -> None:
        """Test initialization with nonexistent file."""
        path = tmp_path / "nonexistent" / "memory.jsonl"
        store = ProcessMemoryStore(path)
        assert store._memory_path == path


class TestProcessMemoryStoreAppend:
    """Test append operations."""

    def test_append_entry(
        self, temp_memory_file: Path, sample_entry: dict[str, Any]
    ) -> None:
        """Test appending entry to file."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry(sample_entry)

        # Verify entry was written
        assert temp_memory_file.exists()
        with open(temp_memory_file) as f:
            line = f.readline()
            loaded = json.loads(line)
            assert loaded["id"] == sample_entry["id"]
            assert loaded["title"] == sample_entry["title"]

    def test_append_entry_adds_timestamp(self, temp_memory_file: Path) -> None:
        """Test that append adds timestamp_created."""
        store = ProcessMemoryStore(temp_memory_file)
        entry = {"id": "test-001"}
        store.append_entry(entry)

        loaded = store.get_entry("test-001")
        assert loaded is not None
        assert "timestamp_created" in loaded

    def test_append_entry_adds_deprecated_field(self, temp_memory_file: Path) -> None:
        """Test that append adds deprecated field."""
        store = ProcessMemoryStore(temp_memory_file)
        entry = {"id": "test-001"}
        store.append_entry(entry)

        loaded = store.get_entry("test-001")
        assert loaded is not None
        assert "deprecated" in loaded
        assert loaded["deprecated"] is False

    def test_append_entry_without_id_raises_error(self, temp_memory_file: Path) -> None:
        """Test that append without ID raises error."""
        store = ProcessMemoryStore(temp_memory_file)
        with pytest.raises(ProcessMemoryError) as exc_info:
            store.append_entry({"title": "No ID"})
        assert "must have 'id' field" in str(exc_info.value).lower()

    def test_append_multiple_entries(self, temp_memory_file: Path) -> None:
        """Test appending multiple entries."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "value": 1})
        store.append_entry({"id": "test-002", "value": 2})
        store.append_entry({"id": "test-003", "value": 3})

        assert store.get_entry_count() == 3


class TestProcessMemoryStoreDeprecation:
    """Test entry deprecation."""

    def test_deprecate_entry(self, temp_memory_file: Path) -> None:
        """Test deprecating an entry."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "title": "Test"})
        store.deprecate_entry("test-001", "No longer needed")

        # Should have appended deprecation entry
        entry = store.get_entry("test-001")
        assert entry is not None
        assert entry["deprecated"] is True
        assert "timestamp_deprecated" in entry
        assert entry["deprecation_reason"] == "No longer needed"

    def test_deprecate_nonexistent_entry_raises_error(
        self, temp_memory_file: Path
    ) -> None:
        """Test deprecating nonexistent entry raises error."""
        store = ProcessMemoryStore(temp_memory_file)
        with pytest.raises(ProcessMemoryError) as exc_info:
            store.deprecate_entry("nonexistent")
        assert "not found" in str(exc_info.value).lower()


class TestProcessMemoryStoreQuery:
    """Test entry querying."""

    def test_get_entry(
        self, temp_memory_file: Path, sample_entry: dict[str, Any]
    ) -> None:
        """Test getting entry by ID."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry(sample_entry)

        entry = store.get_entry("pm-test-001")
        assert entry is not None
        assert entry["id"] == "pm-test-001"
        assert entry["title"] == "Test Entry"

    def test_get_nonexistent_entry(self, temp_memory_file: Path) -> None:
        """Test getting nonexistent entry returns None."""
        store = ProcessMemoryStore(temp_memory_file)
        assert store.get_entry("nonexistent") is None

    def test_list_entries(self, temp_memory_file: Path) -> None:
        """Test listing all entries."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "type": "TypeA"})
        store.append_entry({"id": "test-002", "type": "TypeB"})
        store.append_entry({"id": "test-003", "type": "TypeA"})

        entries = store.list_entries()
        assert len(entries) == 3

    def test_list_entries_excludes_deprecated(self, temp_memory_file: Path) -> None:
        """Test that list_entries excludes deprecated by default."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})
        store.append_entry({"id": "test-002", "deprecated": True})

        entries = store.list_entries(include_deprecated=False)
        assert len(entries) == 1
        assert entries[0]["id"] == "test-001"

    def test_list_entries_filter_by_category(self, temp_memory_file: Path) -> None:
        """Test filtering entries by category."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "type": "TypeA"})
        store.append_entry({"id": "test-002", "type": "TypeB"})
        store.append_entry({"id": "test-003", "type": "TypeA"})

        entries = store.list_entries(category="TypeA")
        assert len(entries) == 2
        assert all(e["type"] == "TypeA" for e in entries)

    def test_list_entries_filter_by_tags(self, temp_memory_file: Path) -> None:
        """Test filtering entries by tags."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "tags": ["python", "test"]})
        store.append_entry({"id": "test-002", "tags": ["javascript", "test"]})
        store.append_entry({"id": "test-003", "tags": ["python", "production"]})

        entries = store.list_entries(tags=["python", "test"])
        assert len(entries) == 1
        assert entries[0]["id"] == "test-001"


class TestProcessMemoryStoreStreaming:
    """Test streaming operations."""

    def test_stream_entries(self, temp_memory_file: Path) -> None:
        """Test streaming entries from file."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})
        store.append_entry({"id": "test-002"})
        store.append_entry({"id": "test-003"})

        entries = list(store.stream_entries())
        assert len(entries) == 3

    def test_stream_entries_with_filter(self, temp_memory_file: Path) -> None:
        """Test streaming with category filter."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "type": "TypeA"})
        store.append_entry({"id": "test-002", "type": "TypeB"})

        entries = list(store.stream_entries(category="TypeA"))
        assert len(entries) == 1
        assert entries[0]["type"] == "TypeA"

    def test_stream_entries_nonexistent_file(self, tmp_path: Path) -> None:
        """Test streaming from nonexistent file returns empty."""
        store = ProcessMemoryStore(tmp_path / "nonexistent.jsonl")
        entries = list(store.stream_entries())
        assert len(entries) == 0


class TestProcessMemoryStoreJIT:
    """Test JIT (Just-In-Time) reading."""

    def test_get_summary(
        self, temp_memory_file: Path, sample_entry: dict[str, Any]
    ) -> None:
        """Test getting entry summary for JIT learning."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry(sample_entry)

        summary = store.get_summary("pm-test-001")
        assert summary is not None
        assert "id" in summary
        assert "type" in summary
        assert "title" in summary
        assert "summary" in summary
        assert "tags" in summary
        # Should not include full rationale, links, etc.
        assert "links" not in summary or summary.get("links") is None

    def test_get_summary_nonexistent(self, temp_memory_file: Path) -> None:
        """Test getting summary for nonexistent entry."""
        store = ProcessMemoryStore(temp_memory_file)
        assert store.get_summary("nonexistent") is None

    def test_get_related_entries(self, temp_memory_file: Path) -> None:
        """Test getting related entries via links."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "links": ["test-002", "test-003"]})
        store.append_entry({"id": "test-002", "title": "Related 1"})
        store.append_entry({"id": "test-003", "title": "Related 2"})

        related = store.get_related_entries("test-001")
        assert len(related) == 2
        assert any(e["id"] == "test-002" for e in related)
        assert any(e["id"] == "test-003" for e in related)

    def test_get_related_entries_no_links(self, temp_memory_file: Path) -> None:
        """Test getting related entries for entry with no links."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})

        related = store.get_related_entries("test-001")
        assert len(related) == 0


class TestProcessMemoryStoreSearch:
    """Test search functionality."""

    def test_search_by_title(self, temp_memory_file: Path) -> None:
        """Test searching entries by title."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "title": "Python Testing"})
        store.append_entry({"id": "test-002", "title": "JavaScript Linting"})

        results = store.search_entries("python")
        assert len(results) == 1
        assert results[0]["id"] == "test-001"

    def test_search_by_summary(self, temp_memory_file: Path) -> None:
        """Test searching entries by summary."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "summary": "Uses pytest framework"})
        store.append_entry({"id": "test-002", "summary": "Uses jest framework"})

        results = store.search_entries("pytest")
        assert len(results) == 1
        assert results[0]["id"] == "test-001"

    def test_search_by_tags(self, temp_memory_file: Path) -> None:
        """Test searching entries by tags."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "tags": ["validation", "security"]})
        store.append_entry({"id": "test-002", "tags": ["rendering", "templates"]})

        results = store.search_entries("security")
        assert len(results) == 1
        assert results[0]["id"] == "test-001"

    def test_search_case_insensitive(self, temp_memory_file: Path) -> None:
        """Test that search is case-insensitive."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001", "title": "Python Testing"})

        results = store.search_entries("PYTHON")
        assert len(results) == 1


class TestProcessMemoryStoreStats:
    """Test statistics and cache management."""

    def test_get_entry_count(self, temp_memory_file: Path) -> None:
        """Test getting entry count."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})
        store.append_entry({"id": "test-002"})

        assert store.get_entry_count() == 2

    def test_get_entry_count_excludes_deprecated(self, temp_memory_file: Path) -> None:
        """Test that count excludes deprecated by default."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})
        store.append_entry({"id": "test-002", "deprecated": True})

        assert store.get_entry_count(include_deprecated=False) == 1
        assert store.get_entry_count(include_deprecated=True) == 2

    def test_clear_cache(self, temp_memory_file: Path) -> None:
        """Test clearing cache."""
        store = ProcessMemoryStore(temp_memory_file)
        store.append_entry({"id": "test-001"})

        # Load cache
        _ = store.get_entry("test-001")
        assert store._cache_loaded

        # Clear cache
        store.clear_cache()
        assert not store._cache_loaded
        assert len(store._cache) == 0
