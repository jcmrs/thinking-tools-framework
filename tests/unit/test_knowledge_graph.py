"""Unit tests for KnowledgeGraph class."""

from pathlib import Path
from typing import Any

import pytest

from cogito.storage.knowledge_graph import KnowledgeGraph
from cogito.storage.process_memory import ProcessMemoryStore


@pytest.fixture
def temp_memory_file(tmp_path: Path) -> Path:
    """Create temporary process memory file."""
    return tmp_path / "process_memory.jsonl"


@pytest.fixture
def populated_store(temp_memory_file: Path) -> ProcessMemoryStore:
    """Create populated process memory store."""
    store = ProcessMemoryStore(temp_memory_file)

    # Create entries with link relationships
    store.append_entry({
        "id": "pm-001",
        "title": "Entry 1",
        "type": "Decision",
        "links": ["pm-002", "pm-003"],
        "tags": ["test", "architecture"],
        "related_concepts": ["modularity", "testing"],
    })
    store.append_entry({
        "id": "pm-002",
        "title": "Entry 2",
        "type": "Decision",
        "links": ["pm-004"],
        "tags": ["test"],
        "related_concepts": ["validation"],
    })
    store.append_entry({
        "id": "pm-003",
        "title": "Entry 3",
        "type": "Lesson",
        "links": [],
        "tags": ["lesson"],
        "related_concepts": ["modularity"],
    })
    store.append_entry({
        "id": "pm-004",
        "title": "Entry 4",
        "type": "Decision",
        "links": [],
        "tags": ["security"],
        "related_concepts": ["security", "validation"],
    })

    return store


class TestKnowledgeGraphInit:
    """Test KnowledgeGraph initialization."""

    def test_init_with_store(self, temp_memory_file: Path) -> None:
        """Test initialization with process memory store."""
        store = ProcessMemoryStore(temp_memory_file)
        graph = KnowledgeGraph(store)
        assert graph._store is store
        assert not graph._built


class TestKnowledgeGraphBuild:
    """Test graph construction."""

    def test_build_graph(self, populated_store: ProcessMemoryStore) -> None:
        """Test building graph from entries."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        assert graph._built
        assert "pm-001" in graph._graph
        assert "pm-002" in graph._graph

    def test_build_graph_creates_forward_links(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test that graph builds forward links."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        # pm-001 links to pm-002 and pm-003
        assert "pm-002" in graph._graph["pm-001"]
        assert "pm-003" in graph._graph["pm-001"]

    def test_build_graph_creates_reverse_links(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test that graph builds reverse index."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        # pm-002 is linked TO by pm-001
        assert "pm-001" in graph._reverse_graph["pm-002"]


class TestKnowledgeGraphRelated:
    """Test finding related entries."""

    def test_get_related_depth_1(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting directly related entries."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        related = graph.get_related("pm-001", depth=1)
        assert len(related) == 2
        ids = {e["id"] for e in related}
        assert "pm-002" in ids
        assert "pm-003" in ids

    def test_get_related_depth_2(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting entries 2 levels deep."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        related = graph.get_related("pm-001", depth=2)
        assert len(related) == 3
        ids = {e["id"] for e in related}
        assert "pm-002" in ids
        assert "pm-003" in ids
        assert "pm-004" in ids  # Linked from pm-002

    def test_get_related_with_reverse(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test getting related entries including reverse links."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        # pm-002 is linked FROM pm-001
        related = graph.get_related("pm-002", depth=1, include_reverse=True)
        ids = {e["id"] for e in related}
        assert "pm-001" in ids  # Reverse link
        assert "pm-004" in ids  # Forward link

    def test_get_related_nonexistent_entry(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test getting related for nonexistent entry returns empty."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        related = graph.get_related("nonexistent")
        assert len(related) == 0


class TestKnowledgeGraphDependencies:
    """Test dependency analysis."""

    def test_get_dependencies(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting all dependencies."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        deps = graph.get_dependencies("pm-001")
        ids = {e["id"] for e in deps}
        # Should include all transitive dependencies
        assert "pm-002" in ids
        assert "pm-003" in ids
        assert "pm-004" in ids  # Transitive via pm-002

    def test_get_dependents(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting entries that depend on given entry."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        # pm-002 is depended on by pm-001
        dependents = graph.get_dependents("pm-002")
        assert len(dependents) >= 1
        assert any(e["id"] == "pm-001" for e in dependents)


class TestKnowledgeGraphSearch:
    """Test semantic search functionality."""

    def test_find_by_concept(self, populated_store: ProcessMemoryStore) -> None:
        """Test finding entries by concept."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        results = graph.find_by_concept("modularity")
        assert len(results) == 2
        ids = {e["id"] for e in results}
        assert "pm-001" in ids
        assert "pm-003" in ids

    def test_find_by_concept_case_insensitive(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test that concept search is case-insensitive."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        results = graph.find_by_concept("VALIDATION")
        assert len(results) >= 1

    def test_find_by_tag(self, populated_store: ProcessMemoryStore) -> None:
        """Test finding entries by tag."""
        graph = KnowledgeGraph(populated_store)

        results = graph.find_by_tag("test")
        assert len(results) == 2
        ids = {e["id"] for e in results}
        assert "pm-001" in ids
        assert "pm-002" in ids


class TestKnowledgeGraphNetwork:
    """Test network extraction."""

    def test_get_entry_network(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting network around entry."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        network = graph.get_entry_network("pm-001", max_depth=2)
        assert "nodes" in network
        assert "edges" in network
        assert len(network["nodes"]) >= 3
        assert len(network["edges"]) >= 2

    def test_get_entry_network_edges_format(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test that network edges have correct format."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        network = graph.get_entry_network("pm-001", max_depth=1)
        for edge in network["edges"]:
            assert "from" in edge
            assert "to" in edge


class TestKnowledgeGraphStats:
    """Test graph statistics."""

    def test_get_graph_stats(self, populated_store: ProcessMemoryStore) -> None:
        """Test getting graph statistics."""
        graph = KnowledgeGraph(populated_store)
        graph.build_graph()

        stats = graph.get_graph_stats()
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "max_outgoing_links" in stats
        assert "max_incoming_links" in stats
        assert stats["total_nodes"] == 4
        assert stats["total_edges"] >= 3

    def test_get_graph_stats_before_build(
        self, populated_store: ProcessMemoryStore
    ) -> None:
        """Test that stats builds graph if not already built."""
        graph = KnowledgeGraph(populated_store)
        assert not graph._built

        stats = graph.get_graph_stats()
        assert graph._built
        assert stats["total_nodes"] > 0
