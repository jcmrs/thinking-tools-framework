"""Process memory store for append-only JSONL operations.

Implements PM-003 (Append-Only Process Memory Log) and PM-017 (JIT Learning).
Provides JSONL append operations, entry querying/filtering, and JIT reading.
"""

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any


class ProcessMemoryError(Exception):
    """Raised when process memory operations fail."""

    pass


class ProcessMemoryStore:
    """Append-only process memory store with JSONL format.

    Implements PM-003 (Append-Only Process Memory Log):
    - Append-only operations (no deletion, only deprecation)
    - JSONL format for efficient streaming read
    - Immutability preserves full decision history

    Implements PM-017 (JIT Learning) with 70% token savings:
    - Lazy loading of entries
    - Filtered reading by category/tags
    - Summary-first approach for memory provisioning
    """

    def __init__(self, memory_path: Path) -> None:
        """Initialize process memory store.

        Args:
            memory_path: Path to JSONL process memory file
        """
        self._memory_path = memory_path
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_loaded = False

    def append_entry(self, entry: dict[str, Any]) -> None:
        """Append new entry to process memory.

        Implements PM-003 append-only pattern.

        Args:
            entry: Process memory entry (must have 'id' field)

        Raises:
            ProcessMemoryError: If entry is invalid or append fails
        """
        # Validate entry has required fields
        if "id" not in entry:
            raise ProcessMemoryError("Entry must have 'id' field")

        # Add timestamp if not present
        if "timestamp_created" not in entry:
            entry["timestamp_created"] = datetime.utcnow().isoformat()

        # Ensure deprecated field exists
        if "deprecated" not in entry:
            entry["deprecated"] = False

        try:
            # Append to file (create if doesn't exist)
            self._memory_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self._memory_path, "a", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

            # Update cache if loaded
            if self._cache_loaded:
                self._cache[entry["id"]] = entry

        except Exception as e:
            raise ProcessMemoryError(f"Failed to append entry: {e}") from e

    def deprecate_entry(self, entry_id: str, reason: str | None = None) -> None:
        """Deprecate an entry instead of deleting (PM-003).

        Args:
            entry_id: ID of entry to deprecate
            reason: Optional deprecation reason

        Raises:
            ProcessMemoryError: If entry not found or deprecation fails
        """
        # Load entry to verify it exists
        entry = self.get_entry(entry_id)
        if entry is None:
            raise ProcessMemoryError(f"Entry '{entry_id}' not found")

        # Create deprecation entry
        deprecation_entry = entry.copy()
        deprecation_entry["deprecated"] = True
        deprecation_entry["timestamp_deprecated"] = datetime.utcnow().isoformat()

        if reason:
            deprecation_entry["deprecation_reason"] = reason

        # Append deprecation as new entry
        self.append_entry(deprecation_entry)

    def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Get a specific entry by ID.

        Uses lazy loading - only loads cache if needed.

        Args:
            entry_id: ID of entry to retrieve

        Returns:
            Entry dict or None if not found
        """
        self._ensure_cache_loaded()
        return self._cache.get(entry_id)

    def list_entries(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        include_deprecated: bool = False,
    ) -> list[dict[str, Any]]:
        """List entries with optional filtering.

        Implements JIT reading with filtering for token efficiency.

        Args:
            category: Filter by category (exact match)
            tags: Filter by tags (entry must have all specified tags)
            include_deprecated: Include deprecated entries

        Returns:
            List of matching entries
        """
        self._ensure_cache_loaded()

        results = []
        for entry in self._cache.values():
            # Skip deprecated unless explicitly included
            if not include_deprecated and entry.get("deprecated", False):
                continue

            # Filter by category
            if category and entry.get("type") != category:
                continue

            # Filter by tags
            if tags:
                entry_tags = entry.get("tags", [])
                if not all(tag in entry_tags for tag in tags):
                    continue

            results.append(entry)

        return results

    def stream_entries(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        include_deprecated: bool = False,
    ) -> Iterator[dict[str, Any]]:
        """Stream entries from file without loading all into memory.

        Implements JIT reading for large process memory files.

        Args:
            category: Filter by category (exact match)
            tags: Filter by tags (entry must have all specified tags)
            include_deprecated: Include deprecated entries

        Yields:
            Process memory entries matching criteria
        """
        if not self._memory_path.exists():
            return

        try:
            with open(self._memory_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        # Skip invalid lines
                        continue

                    # Apply filters
                    if not include_deprecated and entry.get("deprecated", False):
                        continue

                    if category and entry.get("type") != category:
                        continue

                    if tags:
                        entry_tags = entry.get("tags", [])
                        if not all(tag in entry_tags for tag in tags):
                            continue

                    yield entry

        except Exception as e:
            raise ProcessMemoryError(f"Failed to stream entries: {e}") from e

    def get_summary(self, entry_id: str, max_words: int = 150) -> dict[str, Any] | None:
        """Get summary of entry for JIT learning (PM-017).

        Returns lightweight summary with 70% token savings:
        - id, type, title, summary
        - No full rationale, links, or detailed provenance

        Args:
            entry_id: ID of entry
            max_words: Maximum words in summary field (for truncation)

        Returns:
            Summary dict or None if entry not found
        """
        entry = self.get_entry(entry_id)
        if entry is None:
            return None

        # Extract summary fields only
        summary = {
            "id": entry.get("id"),
            "type": entry.get("type"),
            "title": entry.get("title"),
            "summary": entry.get("summary", "")[: max_words * 6],  # Rough word limit
        }

        # Add tags for context
        if "tags" in entry:
            summary["tags"] = entry["tags"]

        return summary

    def get_related_entries(self, entry_id: str) -> list[dict[str, Any]]:
        """Get entries related to given entry via links field.

        Args:
            entry_id: ID of entry to find relations for

        Returns:
            List of related entries
        """
        entry = self.get_entry(entry_id)
        if entry is None or "links" not in entry:
            return []

        related = []
        for linked_id in entry["links"]:
            linked_entry = self.get_entry(linked_id)
            if linked_entry and not linked_entry.get("deprecated", False):
                related.append(linked_entry)

        return related

    def search_entries(
        self,
        keyword: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search entries by keyword in title, summary, or tags.

        Args:
            keyword: Search keyword (case-insensitive)
            category: Filter by category (exact match)
            tags: Filter by tags (entry must have all specified tags)

        Returns:
            List of matching entries
        """
        self._ensure_cache_loaded()

        results = []

        for entry in self._cache.values():
            # Skip deprecated
            if entry.get("deprecated", False):
                continue

            # Filter by category
            if category and entry.get("type") != category:
                continue

            # Filter by tags
            if tags:
                entry_tags = entry.get("tags", [])
                if not all(tag in entry_tags for tag in tags):
                    continue

            # Search by keyword if provided
            if keyword:
                keyword_lower = keyword.lower()

                # Search in title
                if keyword_lower in entry.get("title", "").lower():
                    results.append(entry)
                    continue

                # Search in summary
                if keyword_lower in entry.get("summary", "").lower():
                    results.append(entry)
                    continue

                # Search in tags
                entry_tags_list = entry.get("tags", [])
                if any(keyword_lower in tag.lower() for tag in entry_tags_list):
                    results.append(entry)
                    continue
            else:
                # If no keyword, include entry (already filtered by category/tags)
                results.append(entry)

        return results

    def get_entry_count(self, include_deprecated: bool = False) -> int:
        """Get total number of entries.

        Args:
            include_deprecated: Include deprecated entries in count

        Returns:
            Number of entries
        """
        self._ensure_cache_loaded()

        if include_deprecated:
            return len(self._cache)

        return sum(1 for entry in self._cache.values() if not entry.get("deprecated", False))

    def clear_cache(self) -> None:
        """Clear in-memory cache."""
        self._cache.clear()
        self._cache_loaded = False

    def _ensure_cache_loaded(self) -> None:
        """Load all entries into cache if not already loaded."""
        if self._cache_loaded:
            return

        if not self._memory_path.exists():
            self._cache_loaded = True
            return

        try:
            with open(self._memory_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        entry_id = entry.get("id")
                        if entry_id:
                            # Later entries override earlier ones (append-only update)
                            self._cache[entry_id] = entry
                    except json.JSONDecodeError:
                        continue

            self._cache_loaded = True

        except Exception as e:
            raise ProcessMemoryError(f"Failed to load cache: {e}") from e
