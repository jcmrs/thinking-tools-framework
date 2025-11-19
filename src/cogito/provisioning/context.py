"""Context snippet generation for focused topic exploration."""

from typing import Any

from cogito.storage.process_memory import ProcessMemoryStore


class ContextGenerator:
    """Generate focused context snippets from process memory."""

    def __init__(self, memory_store: ProcessMemoryStore) -> None:
        """Initialize context generator.

        Args:
            memory_store: ProcessMemoryStore instance
        """
        self.memory_store = memory_store

    def generate_context_for_topic(
        self,
        topic: str,
        max_entries: int = 10,
        include_related: bool = True,
    ) -> str:
        """Generate context snippet for a specific topic.

        Args:
            topic: Topic keyword to search for
            max_entries: Maximum number of entries to include
            include_related: Whether to include related entries via links

        Returns:
            Markdown-formatted context snippet
        """
        # Search for entries matching topic
        entries = self.memory_store.search_entries(keyword=topic)

        if not entries:
            return f"# Context: {topic}\n\nNo process memory entries found for '{topic}'.\n"

        # Limit entries
        primary_entries = entries[:max_entries]

        # Collect related entries if requested
        related_entries: list[dict[str, Any]] = []
        if include_related:
            related_ids = set()
            for entry in primary_entries:
                links = entry.get("links", [])
                if links:
                    related_ids.update(links)

            # Fetch related entries
            for entry_id in related_ids:
                related = self.memory_store.get_entry(entry_id)
                if related and related not in primary_entries:
                    related_entries.append(related)

        # Build context document
        lines = [
            f"# Context: {topic}",
            "",
            f"Found {len(entries)} entries matching '{topic}'. Showing top {len(primary_entries)}.",
            "",
        ]

        # Add primary entries
        lines.append("## Primary Entries")
        lines.append("")

        for entry in primary_entries:
            lines.append(f"### {entry['id']}: {entry['title']}")
            lines.append(f"*Type: {entry['type']}*")
            lines.append("")
            lines.append(f"**Summary**: {entry['summary']}")
            lines.append("")

            if "rationale" in entry:
                lines.append(f"**Rationale**: {entry['rationale']}")
                lines.append("")

            if "related_concepts" in entry and entry["related_concepts"]:
                concepts = ", ".join(entry["related_concepts"])
                lines.append(f"**Related Concepts**: {concepts}")
                lines.append("")

            if "tags" in entry and entry["tags"]:
                tags_str = ", ".join(f"`{tag}`" for tag in entry["tags"])
                lines.append(f"**Tags**: {tags_str}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Add related entries
        if related_entries:
            lines.append("## Related Entries")
            lines.append("")
            lines.append(
                f"{len(related_entries)} additional entries linked from the primary entries:"
            )
            lines.append("")

            for entry in related_entries[:5]:  # Limit related entries
                lines.append(f"- **{entry['id']}**: {entry['title']} ({entry['type']})")

            if len(related_entries) > 5:
                lines.append(f"- ... and {len(related_entries) - 5} more")

            lines.append("")

        return "\n".join(lines)

    def generate_type_summary(self, entry_type: str) -> str:
        """Generate summary of all entries of a specific type.

        Args:
            entry_type: Type to summarize (e.g., 'StrategicDecision', 'LessonLearned')

        Returns:
            Markdown-formatted summary
        """
        # Get all entries
        all_entries = self.memory_store.list_entries()

        # Filter by type
        type_entries = [e for e in all_entries if e.get("type") == entry_type]

        if not type_entries:
            return f"# {entry_type}\n\nNo entries of type '{entry_type}' found.\n"

        # Build summary
        lines = [
            f"# {entry_type}",
            "",
            f"Total: {len(type_entries)} entries",
            "",
        ]

        # Add each entry
        for entry in type_entries:
            lines.append(f"## {entry['id']}: {entry['title']}")
            lines.append("")
            lines.append(entry["summary"])
            lines.append("")

            if "confidence_level" in entry:
                confidence = entry["confidence_level"]
                lines.append(f"**Confidence**: {confidence:.0%}")
                lines.append("")

            if "tags" in entry and entry["tags"]:
                tags_str = ", ".join(f"`{tag}`" for tag in entry["tags"])
                lines.append(f"**Tags**: {tags_str}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
