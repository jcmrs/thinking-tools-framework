"""Integration tests for Process Memory + Knowledge Graph workflow.

Tests the complete workflow: append entry → query → build graph → traverse relationships.
"""
from pathlib import Path

import pytest

from cogito.storage.knowledge_graph import KnowledgeGraph
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def temp_memory_store(tmp_path: Path) -> ProcessMemoryStore:
    """Create temporary process memory store."""
    memory_file = tmp_path / "test_memory.jsonl"
    return ProcessMemoryStore(memory_file)


class TestProcessMemoryWorkflow:
    """Test complete PM + graph workflow."""

    def test_append_entry_and_query(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test appending entry and querying by ID."""
        entry: dict = {
            "id": "test-entry-1",
            "timestamp": "2025-11-20T00:00:00Z",
            "type": "test",
            "category": "integration-test",
            "title": "Test Entry 1",
            "summary": "Test summary",
            "links": [],
            "tags": ["test"],
        }

        temp_memory_store.append_entry(entry)
        retrieved = temp_memory_store.get_entry("test-entry-1")

        assert retrieved is not None
        assert retrieved["id"] == "test-entry-1"
        assert retrieved["title"] == "Test Entry 1"

    def test_search_by_category(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test searching entries by type."""
        entries = [
            {
                "id": "entry-1",
                "timestamp": "2025-11-20T00:00:00Z",
                "type": "completion",
                "category": "milestone",
                "title": "Entry 1",
                "summary": "Summary 1",
                "links": [],
                "tags": ["test"],
            },
            {
                "id": "entry-2",
                "timestamp": "2025-11-20T00:01:00Z",
                "type": "completion",
                "category": "milestone",
                "title": "Entry 2",
                "summary": "Summary 2",
                "links": [],
                "tags": ["test"],
            },
            {
                "id": "entry-3",
                "timestamp": "2025-11-20T00:02:00Z",
                "type": "research",
                "category": "analysis",
                "title": "Entry 3",
                "summary": "Summary 3",
                "links": [],
                "tags": ["test"],
            },
        ]

        for entry in entries:
            temp_memory_store.append_entry(entry)

        completions = temp_memory_store.list_entries(category="completion")
        assert len(completions) == 2
        assert all(e["type"] == "completion" for e in completions)

    def test_search_by_tags(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test searching entries by tags."""
        entries = [
            {
                "id": "entry-1",
                "timestamp": "2025-11-20T00:00:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry 1",
                "summary": "Summary 1",
                "links": [],
                "tags": ["foundation", "priority1"],
            },
            {
                "id": "entry-2",
                "timestamp": "2025-11-20T00:01:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry 2",
                "summary": "Summary 2",
                "links": [],
                "tags": ["foundation", "priority2"],
            },
            {
                "id": "entry-3",
                "timestamp": "2025-11-20T00:02:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry 3",
                "summary": "Summary 3",
                "links": [],
                "tags": ["core", "priority3"],
            },
        ]

        for entry in entries:
            temp_memory_store.append_entry(entry)

        foundation_entries = temp_memory_store.list_entries(tags=["foundation"])
        assert len(foundation_entries) == 2
        assert all("foundation" in e["tags"] for e in foundation_entries)

    def test_graph_traversal(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test building graph and traversing relationships."""
        entries = [
            {
                "id": "entry-a",
                "timestamp": "2025-11-20T00:00:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry A",
                "summary": "First entry",
                "links": [],
                "tags": ["test"],
            },
            {
                "id": "entry-b",
                "timestamp": "2025-11-20T00:01:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry B",
                "summary": "Second entry",
                "links": ["entry-a"],
                "tags": ["test"],
            },
            {
                "id": "entry-c",
                "timestamp": "2025-11-20T00:02:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry C",
                "summary": "Third entry",
                "links": ["entry-b"],
                "tags": ["test"],
            },
        ]

        for entry in entries:
            temp_memory_store.append_entry(entry)

        graph = KnowledgeGraph(temp_memory_store)
        graph.build_graph()

        # Query forward links from entry-b
        related = graph.get_related("entry-b")
        assert len(related) == 1
        assert related[0]["id"] == "entry-a"

    def test_reverse_links(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test bidirectional graph traversal with reverse links."""
        entries = [
            {
                "id": "entry-a",
                "timestamp": "2025-11-20T00:00:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry A",
                "summary": "First entry",
                "links": [],
                "tags": ["test"],
            },
            {
                "id": "entry-b",
                "timestamp": "2025-11-20T00:01:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry B",
                "summary": "Second entry links to A",
                "links": ["entry-a"],
                "tags": ["test"],
            },
            {
                "id": "entry-c",
                "timestamp": "2025-11-20T00:02:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry C",
                "summary": "Third entry links to A",
                "links": ["entry-a"],
                "tags": ["test"],
            },
        ]

        for entry in entries:
            temp_memory_store.append_entry(entry)

        graph = KnowledgeGraph(temp_memory_store)
        graph.build_graph()

        # Query reverse links from entry-a (who links to me?)
        reverse_related = graph.get_related("entry-a", include_reverse=True)
        assert len(reverse_related) == 2
        reverse_ids = {e["id"] for e in reverse_related}
        assert reverse_ids == {"entry-b", "entry-c"}

    def test_depth_traversal(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test deep graph traversal with depth parameter."""
        entries = [
            {
                "id": "entry-a",
                "timestamp": "2025-11-20T00:00:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry A",
                "summary": "Root entry",
                "links": [],
                "tags": ["test"],
            },
            {
                "id": "entry-b",
                "timestamp": "2025-11-20T00:01:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry B",
                "summary": "Depth 1 from C",
                "links": ["entry-a"],
                "tags": ["test"],
            },
            {
                "id": "entry-c",
                "timestamp": "2025-11-20T00:02:00Z",
                "type": "test",
                "category": "test",
                "title": "Entry C",
                "summary": "Starting point",
                "links": ["entry-b"],
                "tags": ["test"],
            },
        ]

        for entry in entries:
            temp_memory_store.append_entry(entry)

        graph = KnowledgeGraph(temp_memory_store)
        graph.build_graph()

        # Depth 1: Should find entry-b only
        depth1 = graph.get_related("entry-c", depth=1)
        assert len(depth1) == 1
        assert depth1[0]["id"] == "entry-b"

        # Depth 2: Should find both entry-b and entry-a
        depth2 = graph.get_related("entry-c", depth=2)
        assert len(depth2) == 2
        depth2_ids = {e["id"] for e in depth2}
        assert depth2_ids == {"entry-b", "entry-a"}

    def test_end_to_end_workflow(self, temp_memory_store: ProcessMemoryStore) -> None:
        """Test complete PM + graph workflow end-to-end."""
        # Step 1: Append entries with relationships
        priority1 = {
            "id": "priority1-test",
            "timestamp": "2025-11-20T00:00:00Z",
            "type": "completion",
            "category": "milestone",
            "title": "Priority 1 Complete",
            "summary": "Foundation work",
            "links": [],
            "tags": ["priority1", "foundation"],
        }

        priority2 = {
            "id": "priority2-test",
            "timestamp": "2025-11-20T00:01:00Z",
            "type": "completion",
            "category": "milestone",
            "title": "Priority 2 Complete",
            "summary": "Builds on priority 1",
            "links": ["priority1-test"],
            "tags": ["priority2", "foundation"],
        }

        temp_memory_store.append_entry(priority1)
        temp_memory_store.append_entry(priority2)

        # Step 2: Search by tags
        foundation = temp_memory_store.list_entries(tags=["foundation"])
        assert len(foundation) == 2

        # Step 3: Build graph
        graph = KnowledgeGraph(temp_memory_store)
        graph.build_graph()

        # Step 4: Traverse relationships
        related = graph.get_related("priority2-test")
        assert len(related) == 1
        assert related[0]["id"] == "priority1-test"

        # Step 5: Reverse traversal
        reverse = graph.get_related("priority1-test", include_reverse=True)
        assert len(reverse) == 1
        assert reverse[0]["id"] == "priority2-test"
