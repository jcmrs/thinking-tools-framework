"""Integration tests for storage layer with real process_memory.jsonl."""

from pathlib import Path

import pytest

from cogito.storage.knowledge_graph import KnowledgeGraph
from cogito.storage.process_memory import ProcessMemoryStore

# Path to real process memory file
PROCESS_MEMORY_PATH = Path(__file__).parent.parent.parent / ".bootstrap" / "process_memory.jsonl"


@pytest.fixture
def real_memory_store() -> ProcessMemoryStore:
    """Create store with real process memory file."""
    if not PROCESS_MEMORY_PATH.exists():
        pytest.skip("Real process memory file not found")
    return ProcessMemoryStore(PROCESS_MEMORY_PATH)


class TestRealProcessMemory:
    """Test with real process_memory.jsonl file."""

    def test_load_real_process_memory(self, real_memory_store: ProcessMemoryStore) -> None:
        """Test loading real process memory file."""
        count = real_memory_store.get_entry_count()
        assert count > 0
        assert count == 52  # Known count from BOOTSTRAP-COMPLETE.md

    def test_get_pm003_append_only_decision(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting PM-003 (Append-Only Process Memory Log)."""
        entry = real_memory_store.get_entry("pm-003")
        assert entry is not None
        assert entry["title"] == "Append-Only Process Memory Log"
        assert "JSONL" in entry["summary"]
        assert "append-only" in entry["summary"].lower()

    def test_get_pm008_five_layer_architecture(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting PM-008 (Five-Layer Architecture)."""
        entry = real_memory_store.get_entry("pm-008")
        assert entry is not None
        assert entry["title"] == "Five-Layer Architecture"
        assert "Storage" in entry["summary"]

    def test_get_pm017_jit_learning(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting PM-017 (JIT Learning)."""
        entry = real_memory_store.get_entry("pm-017")
        assert entry is not None
        assert "JIT" in entry["title"] or "just-in-time" in entry["summary"].lower()
        # 70% token savings mentioned in rationale
        assert "70%" in entry.get("rationale", "") or "token" in entry["summary"].lower()

    def test_list_strategic_decisions(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test filtering by StrategicDecision category."""
        decisions = real_memory_store.list_entries(category="StrategicDecision")
        assert len(decisions) >= 10  # Should have many strategic decisions

    def test_list_lessons_learned(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test filtering by LessonLearned category."""
        lessons = real_memory_store.list_entries(category="LessonLearned")
        assert len(lessons) >= 5

    def test_search_for_validation(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test searching for validation-related entries."""
        results = real_memory_store.search_entries("validation")
        assert len(results) > 0
        # Should find PM-005 (Multi-Layer Validation)
        assert any(e["id"] == "pm-005" for e in results)

    def test_get_summary_token_efficient(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test that summaries are token-efficient."""
        entry = real_memory_store.get_entry("pm-001")
        summary = real_memory_store.get_summary("pm-001")

        assert summary is not None
        assert len(str(summary)) < len(str(entry))  # Summary should be smaller
        assert "id" in summary
        assert "title" in summary

    def test_stream_all_entries(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test streaming all entries from real file."""
        count = sum(1 for _ in real_memory_store.stream_entries())
        assert count == 52

    def test_filter_by_tags(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test filtering entries by tags."""
        # Find entries tagged with 'modularity'
        entries = real_memory_store.list_entries(tags=["modularity"])
        assert len(entries) > 0


class TestRealKnowledgeGraph:
    """Test KnowledgeGraph with real process memory."""

    def test_build_graph_from_real_memory(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test building knowledge graph from real memory."""
        graph = KnowledgeGraph(real_memory_store)
        graph.build_graph()

        assert graph._built
        assert len(graph._graph) > 0

    def test_get_graph_stats(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting stats from real graph."""
        graph = KnowledgeGraph(real_memory_store)
        stats = graph.get_graph_stats()

        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0

    def test_get_related_to_pm003(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting entries related to PM-003."""
        graph = KnowledgeGraph(real_memory_store)
        graph.build_graph()

        related = graph.get_related("pm-003", depth=1)
        # PM-003 links to pm-025
        assert len(related) > 0

    def test_find_by_modularity_concept(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test finding entries by modularity concept."""
        graph = KnowledgeGraph(real_memory_store)
        graph.build_graph()

        results = graph.find_by_concept("modularity")
        assert len(results) > 0
        # Should find entries discussing modularity

    def test_get_entry_network(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting network visualization data."""
        graph = KnowledgeGraph(real_memory_store)
        graph.build_graph()

        network = graph.get_entry_network("pm-003", max_depth=2)
        assert "nodes" in network
        assert "edges" in network
        assert len(network["nodes"]) > 0

    def test_get_dependencies_of_pm005(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test getting dependencies of PM-005 (Multi-Layer Validation)."""
        graph = KnowledgeGraph(real_memory_store)
        graph.build_graph()

        deps = graph.get_dependencies("pm-005")
        # PM-005 links to pm-001 and pm-002
        assert len(deps) >= 2
        ids = {e["id"] for e in deps}
        assert "pm-001" in ids or "pm-002" in ids


class TestJITReadingPerformance:
    """Test JIT reading performance characteristics."""

    def test_streaming_vs_full_load(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test that streaming doesn't load full file into memory."""
        # Stream with filter should be efficient
        count = 0
        for entry in real_memory_store.stream_entries(category="StrategicDecision"):
            count += 1
            if count >= 5:
                break  # Early exit without reading full file

        assert count == 5

    def test_summary_reduces_tokens(
        self, real_memory_store: ProcessMemoryStore
    ) -> None:
        """Test that summaries achieve token savings."""
        full_entry = real_memory_store.get_entry("pm-001")
        summary = real_memory_store.get_summary("pm-001")

        assert full_entry is not None
        assert summary is not None

        # Summary should not have full rationale or provenance
        assert "rationale" not in summary
        assert "provenance" not in summary

        # But should have key identifying info
        assert summary["id"] == full_entry["id"]
        assert summary["title"] == full_entry["title"]
