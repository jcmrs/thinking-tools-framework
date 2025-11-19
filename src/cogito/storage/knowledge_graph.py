"""Knowledge graph for process memory relationship traversal.

Builds graph structure from JSONL process memory for efficient traversal
and semantic search across related entries.
"""

from typing import Any

from cogito.storage.process_memory import ProcessMemoryStore


class KnowledgeGraphError(Exception):
    """Raised when knowledge graph operations fail."""

    pass


class KnowledgeGraph:
    """Knowledge graph for process memory entries.

    Builds directed graph from process memory JSONL:
    - Nodes: Process memory entries
    - Edges: Links between entries (from 'links' field)

    Enables:
    - Relationship traversal (find related entries)
    - Dependency chains (find all dependencies)
    - Semantic search (find entries by concept)
    """

    def __init__(self, memory_store: ProcessMemoryStore) -> None:
        """Initialize knowledge graph from process memory store.

        Args:
            memory_store: ProcessMemoryStore instance
        """
        self._store = memory_store
        self._graph: dict[str, set[str]] = {}  # entry_id -> set of linked entry IDs
        self._reverse_graph: dict[str, set[str]] = {}  # entry_id -> entries linking TO it
        self._built = False

    def build_graph(self) -> None:
        """Build graph structure from process memory.

        Loads all entries and constructs forward and reverse link indices.
        """
        self._graph.clear()
        self._reverse_graph.clear()

        # Get all non-deprecated entries
        entries = self._store.list_entries(include_deprecated=False)

        for entry in entries:
            entry_id = entry.get("id")
            if not entry_id:
                continue

            # Initialize entry in graph
            if entry_id not in self._graph:
                self._graph[entry_id] = set()

            # Add forward links
            links = entry.get("links", [])
            for linked_id in links:
                self._graph[entry_id].add(linked_id)

                # Build reverse index
                if linked_id not in self._reverse_graph:
                    self._reverse_graph[linked_id] = set()
                self._reverse_graph[linked_id].add(entry_id)

        self._built = True

    def get_related(
        self, entry_id: str, depth: int = 1, include_reverse: bool = False
    ) -> list[dict[str, Any]]:
        """Get entries related to given entry.

        Args:
            entry_id: ID of entry to find relations for
            depth: How many levels deep to traverse (1 = direct links only)
            include_reverse: Include entries that link TO this entry

        Returns:
            List of related entries
        """
        if not self._built:
            self.build_graph()

        if entry_id not in self._graph:
            return []

        # BFS to find all related entries within depth
        visited = {entry_id}
        current_level = {entry_id}
        all_related_ids = set()

        for _ in range(depth):
            next_level = set()

            for current_id in current_level:
                # Forward links
                if current_id in self._graph:
                    for linked_id in self._graph[current_id]:
                        if linked_id not in visited:
                            next_level.add(linked_id)
                            all_related_ids.add(linked_id)
                            visited.add(linked_id)

                # Reverse links
                if include_reverse and current_id in self._reverse_graph:
                    for linking_id in self._reverse_graph[current_id]:
                        if linking_id not in visited:
                            next_level.add(linking_id)
                            all_related_ids.add(linking_id)
                            visited.add(linking_id)

            current_level = next_level

            if not current_level:
                break

        # Fetch actual entries
        related_entries = []
        for related_id in all_related_ids:
            entry = self._store.get_entry(related_id)
            if entry and not entry.get("deprecated", False):
                related_entries.append(entry)

        return related_entries

    def get_dependencies(self, entry_id: str) -> list[dict[str, Any]]:
        """Get all dependencies of an entry (transitive closure of links).

        Args:
            entry_id: ID of entry to find dependencies for

        Returns:
            List of all entries this entry depends on (directly or indirectly)
        """
        # Use unbounded depth to get all dependencies
        return self.get_related(entry_id, depth=100, include_reverse=False)

    def get_dependents(self, entry_id: str) -> list[dict[str, Any]]:
        """Get all entries that depend on this entry.

        Args:
            entry_id: ID of entry to find dependents for

        Returns:
            List of entries that link to this entry
        """
        if not self._built:
            self.build_graph()

        if entry_id not in self._reverse_graph:
            return []

        dependent_entries = []
        for dependent_id in self._reverse_graph[entry_id]:
            entry = self._store.get_entry(dependent_id)
            if entry and not entry.get("deprecated", False):
                dependent_entries.append(entry)

        return dependent_entries

    def find_by_concept(self, concept: str) -> list[dict[str, Any]]:
        """Find entries related to a concept via related_concepts field.

        Args:
            concept: Concept keyword (case-insensitive)

        Returns:
            List of entries with matching concept
        """
        if not self._built:
            self.build_graph()

        concept_lower = concept.lower()
        matching_entries = []

        entries = self._store.list_entries(include_deprecated=False)
        for entry in entries:
            concepts = entry.get("related_concepts", [])
            if any(concept_lower in c.lower() for c in concepts):
                matching_entries.append(entry)

        return matching_entries

    def find_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """Find entries with specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of entries with matching tag
        """
        return self._store.list_entries(tags=[tag])

    def get_entry_network(self, entry_id: str, max_depth: int = 2) -> dict[str, Any]:
        """Get network of entries around given entry.

        Returns graph structure for visualization.

        Args:
            entry_id: Center entry ID
            max_depth: Maximum depth to traverse

        Returns:
            Dict with 'nodes' and 'edges' lists
        """
        if not self._built:
            self.build_graph()

        # Get related entries
        related = self.get_related(entry_id, depth=max_depth, include_reverse=True)

        # Add center entry
        center_entry = self._store.get_entry(entry_id)
        if center_entry and not center_entry.get("deprecated", False):
            nodes = [center_entry] + related
        else:
            nodes = related

        # Build edges list
        edges = []
        for node in nodes:
            node_id = node.get("id")
            if node_id in self._graph:
                for linked_id in self._graph[node_id]:
                    # Only include edge if target is in nodes
                    if any(n.get("id") == linked_id for n in nodes):
                        edges.append({"from": node_id, "to": linked_id})

        return {"nodes": nodes, "edges": edges}

    def get_graph_stats(self) -> dict[str, Any]:
        """Get statistics about the knowledge graph.

        Returns:
            Dict with node count, edge count, and other metrics
        """
        if not self._built:
            self.build_graph()

        total_nodes = len(self._graph)
        total_edges = sum(len(links) for links in self._graph.values())

        # Find nodes with most connections
        max_outgoing = max(len(links) for links in self._graph.values()) if self._graph else 0
        max_incoming = (
            max(len(links) for links in self._reverse_graph.values()) if self._reverse_graph else 0
        )

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "max_outgoing_links": max_outgoing,
            "max_incoming_links": max_incoming,
        }
