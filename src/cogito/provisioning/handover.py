"""Session handover document generation from process memory."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from cogito.contracts.layer_protocols import StorageProtocol


class HandoverGenerator:
    """Generate comprehensive session handover documents from process memory."""

    def __init__(
        self,
        memory_store: StorageProtocol,
        templates_dir: Path | None = None,
    ) -> None:
        """Initialize handover generator.

        Args:
            memory_store: Storage layer instance implementing StorageProtocol
            templates_dir: Optional path to templates directory.
                          If None, uses built-in templates.
        """
        self.memory_store = memory_store

        # Set up Jinja2 environment
        if templates_dir and templates_dir.exists():
            loader = FileSystemLoader(str(templates_dir))
        else:
            # Use package templates
            loader = FileSystemLoader(
                str(Path(__file__).parent.parent.parent.parent / "templates")
            )

        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generate_handover_document(
        self,
        output_path: Path | None = None,
        include_deprecated: bool = False,
    ) -> str:
        """Generate comprehensive handover document.

        Args:
            output_path: Optional path to write document
            include_deprecated: Whether to include deprecated entries

        Returns:
            Markdown-formatted handover document

        Raises:
            IOError: If output_path specified but write fails
        """
        # Get all entries (with or without deprecated based on flag)
        all_entries = self.memory_store.list_entries(include_deprecated=include_deprecated)

        # Organize entries by type
        by_type: dict[str, list[dict[str, Any]]] = {}
        for entry in all_entries:
            entry_type = entry.get("type", "Unknown")
            if entry_type not in by_type:
                by_type[entry_type] = []
            by_type[entry_type].append(entry)

        # Calculate statistics
        stats = {
            "total_entries": len(all_entries),
            "by_type": {t: len(entries) for t, entries in by_type.items()},
            "high_confidence": len([e for e in all_entries if e.get("confidence_level", 0) >= 0.9]),
            "medium_confidence": len(
                [e for e in all_entries if 0.7 <= e.get("confidence_level", 0) < 0.9]
            ),
            "low_confidence": len([e for e in all_entries if e.get("confidence_level", 0) < 0.7]),
        }

        # Extract key concepts
        all_concepts: set[str] = set()
        for entry in all_entries:
            concepts = entry.get("related_concepts", [])
            if concepts:
                all_concepts.update(concepts)

        # Get recent entries (last 10)
        recent_entries = sorted(
            all_entries,
            key=lambda e: e.get("timestamp_created", ""),
            reverse=True,
        )[:10]

        # Prepare template context
        context = {
            "stats": stats,
            "by_type": by_type,
            "recent_entries": recent_entries,
            "key_concepts": sorted(all_concepts),
            "all_entries": all_entries,
        }

        # Render template
        try:
            template = self.env.get_template("handover_document.md.j2")
            handover_doc = template.render(**context)
        except Exception:
            # Fallback to simple handover if template missing
            handover_doc = self._generate_simple_handover(context)

        # Write to file if specified
        if output_path:
            output_path.write_text(handover_doc, encoding="utf-8")

        return handover_doc

    def _generate_simple_handover(self, context: dict[str, Any]) -> str:
        """Generate simple handover document without template.

        Args:
            context: Template context dictionary

        Returns:
            Markdown-formatted handover document
        """
        lines = [
            "# Session Handover Document",
            "",
            "## Executive Summary",
            "",
            f"This project has accumulated **{context['stats']['total_entries']} "
            "process memory entries** capturing design decisions, lessons learned, "
            "and observations.",
            "",
            "### Statistics",
            "",
        ]

        # Add type breakdown
        for entry_type, count in sorted(context["stats"]["by_type"].items()):
            lines.append(f"- **{entry_type}**: {count} entries")

        lines.extend([
            "",
            "### Confidence Levels",
            "",
            f"- High confidence (≥90%): {context['stats']['high_confidence']} entries",
            f"- Medium confidence (70-89%): {context['stats']['medium_confidence']} entries",
            f"- Low confidence (<70%): {context['stats']['low_confidence']} entries",
            "",
            "## Recent Decisions",
            "",
        ])

        # Add recent entries
        for entry in context["recent_entries"][:5]:
            lines.append(f"### {entry['id']}: {entry['title']}")
            lines.append(f"*{entry['type']}*")
            lines.append("")
            lines.append(entry["summary"])
            lines.append("")

        lines.extend([
            "## Key Concepts",
            "",
            "The following concepts are referenced throughout the process memory:",
            "",
        ])

        # Add key concepts
        for concept in context["key_concepts"][:20]:
            lines.append(f"- {concept}")

        lines.extend([
            "",
            "## Next Steps",
            "",
            "1. Review the process memory entries for architectural context",
            "2. Understand the Five Cornerstones and AI-First principles",
            "3. Examine recent decisions and lessons learned",
            "4. Continue development aligned with established patterns",
            "",
        ])

        return "\n".join(lines)
