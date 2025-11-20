"""Process memory export functionality for various formats."""

import json
from pathlib import Path
from typing import Any

import yaml

from cogito.contracts.layer_protocols import StorageProtocol


class ProcessMemoryExporter:
    """Export process memory entries in various formats."""

    def __init__(self, memory_store: StorageProtocol) -> None:
        """Initialize exporter with memory store.

        Args:
            memory_store: Storage layer instance implementing StorageProtocol
        """
        self.memory_store = memory_store

    def export_to_markdown(
        self,
        output_path: Path | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Export process memory entries as markdown document.

        Args:
            output_path: Optional path to write markdown file
            category: Optional filter by entry type/category
            tags: Optional filter by tags (must have all)

        Returns:
            Markdown-formatted string

        Raises:
            IOError: If output_path specified but write fails
        """
        # Get entries (filtered if specified)
        entries = self.memory_store.list_entries()

        # Apply filters manually
        if category:
            entries = [e for e in entries if e.get("type") == category]
        if tags:
            entries = [e for e in entries if all(tag in e.get("tags", []) for tag in tags)]

        # Build markdown
        lines = [
            "# Process Memory",
            "",
            "Accumulated design decisions, lessons learned, and observations.",
            "",
        ]

        # Group by type
        by_type: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            entry_type = entry.get("type", "Unknown")
            if entry_type not in by_type:
                by_type[entry_type] = []
            by_type[entry_type].append(entry)

        # Output each type
        for entry_type, type_entries in sorted(by_type.items()):
            lines.append(f"## {entry_type}")
            lines.append("")

            for entry in type_entries:
                lines.append(f"### {entry['id']}: {entry['title']}")
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

                if "links" in entry and entry["links"]:
                    links_str = ", ".join(entry["links"])
                    lines.append(f"**Links**: {links_str}")
                    lines.append("")

                if "confidence_level" in entry:
                    confidence = entry["confidence_level"]
                    lines.append(f"**Confidence**: {confidence:.0%}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        markdown = "\n".join(lines)

        # Write to file if specified
        if output_path:
            output_path.write_text(markdown, encoding="utf-8")

        return markdown

    def export_to_json(
        self,
        output_path: Path | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        pretty: bool = True,
    ) -> str:
        """Export process memory entries as JSON.

        Args:
            output_path: Optional path to write JSON file
            category: Optional filter by entry type/category
            tags: Optional filter by tags (must have all)
            pretty: Whether to pretty-print JSON (default: True)

        Returns:
            JSON-formatted string

        Raises:
            IOError: If output_path specified but write fails
        """
        # Get entries (filtered if specified)
        entries = self.memory_store.list_entries()

        # Apply filters manually
        if category:
            entries = [e for e in entries if e.get("type") == category]
        if tags:
            entries = [e for e in entries if all(tag in e.get("tags", []) for tag in tags)]

        # Convert to JSON
        if pretty:
            json_str = json.dumps(entries, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(entries, ensure_ascii=False)

        # Write to file if specified
        if output_path:
            output_path.write_text(json_str, encoding="utf-8")

        return json_str

    def export_to_yaml(
        self,
        output_path: Path | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Export process memory entries as YAML.

        Args:
            output_path: Optional path to write YAML file
            category: Optional filter by entry type/category
            tags: Optional filter by tags (must have all)

        Returns:
            YAML-formatted string

        Raises:
            IOError: If output_path specified but write fails
        """
        # Get entries (filtered if specified)
        entries = self.memory_store.list_entries()

        # Apply filters manually
        if category:
            entries = [e for e in entries if e.get("type") == category]
        if tags:
            entries = [e for e in entries if all(tag in e.get("tags", []) for tag in tags)]

        # Convert to YAML
        yaml_str = yaml.dump(
            entries,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

        # Write to file if specified
        if output_path:
            output_path.write_text(yaml_str, encoding="utf-8")

        return yaml_str
