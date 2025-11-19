"""Process memory import functionality with validation."""

import json
from pathlib import Path
from typing import Any

import yaml

from cogito.storage.process_memory import ProcessMemoryStore


class ProcessMemoryImporter:
    """Import process memory entries from external files with validation."""

    # Required fields for process memory entries
    REQUIRED_FIELDS = {"id", "type", "title", "summary"}

    def __init__(self, memory_store: ProcessMemoryStore) -> None:
        """Initialize importer with memory store.

        Args:
            memory_store: ProcessMemoryStore instance to import into
        """
        self.memory_store = memory_store

    def import_from_json(
        self, file_path: Path, merge: bool = True
    ) -> tuple[int, list[str]]:
        """Import process memory entries from JSON file.

        Args:
            file_path: Path to JSON file
            merge: If True, merge with existing entries. If False, validation only.

        Returns:
            Tuple of (number_of_entries_imported, list_of_validation_errors)

        Raises:
            FileNotFoundError: If file_path doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        # Load JSON
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)

        # Validate and import
        return self._validate_and_import(data, merge)

    def import_from_yaml(
        self, file_path: Path, merge: bool = True
    ) -> tuple[int, list[str]]:
        """Import process memory entries from YAML file.

        Args:
            file_path: Path to YAML file
            merge: If True, merge with existing entries. If False, validation only.

        Returns:
            Tuple of (number_of_entries_imported, list_of_validation_errors)

        Raises:
            FileNotFoundError: If file_path doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        # Load YAML
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        # Validate and import
        return self._validate_and_import(data, merge)

    def import_from_jsonl(
        self, file_path: Path, merge: bool = True
    ) -> tuple[int, list[str]]:
        """Import process memory entries from JSONL file.

        Args:
            file_path: Path to JSONL file
            merge: If True, merge with existing entries. If False, validation only.

        Returns:
            Tuple of (number_of_entries_imported, list_of_validation_errors)

        Raises:
            FileNotFoundError: If file_path doesn't exist
            json.JSONDecodeError: If any line is not valid JSON
        """
        # Load JSONL
        entries = []
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON on line {line_num}: {e.msg}",
                        e.doc,
                        e.pos,
                    ) from e

        # Validate and import
        return self._validate_and_import(entries, merge)

    def _validate_and_import(
        self, data: Any, merge: bool
    ) -> tuple[int, list[str]]:
        """Validate entries and optionally import them.

        Args:
            data: List of entry dictionaries or single entry dictionary
            merge: If True, add entries to store. If False, validation only.

        Returns:
            Tuple of (number_of_valid_entries, list_of_validation_errors)
        """
        # Ensure data is a list
        if isinstance(data, dict):
            entries = [data]
        elif isinstance(data, list):
            entries = data
        else:
            return (0, [f"Invalid data type: expected list or dict, got {type(data).__name__}"])

        validation_errors = []
        valid_entries = []

        # Validate each entry
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                validation_errors.append(
                    f"Entry {i}: Not a dictionary (got {type(entry).__name__})"
                )
                continue

            # Check required fields
            missing_fields = self.REQUIRED_FIELDS - set(entry.keys())
            if missing_fields:
                validation_errors.append(
                    f"Entry {i} ({entry.get('id', 'unknown')}): "
                    f"Missing required fields: {missing_fields}"
                )
                continue

            # Validate field types
            if not isinstance(entry.get("id"), str):
                validation_errors.append(
                    f"Entry {i}: 'id' must be a string"
                )
                continue

            if not isinstance(entry.get("type"), str):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'type' must be a string"
                )
                continue

            if not isinstance(entry.get("title"), str):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'title' must be a string"
                )
                continue

            if not isinstance(entry.get("summary"), str):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'summary' must be a string"
                )
                continue

            # Validate optional fields if present
            if "tags" in entry and not isinstance(entry["tags"], list):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'tags' must be a list"
                )
                continue

            if "links" in entry and not isinstance(entry["links"], list):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'links' must be a list"
                )
                continue

            if "related_concepts" in entry and not isinstance(entry["related_concepts"], list):
                validation_errors.append(
                    f"Entry {i} ({entry['id']}): 'related_concepts' must be a list"
                )
                continue

            # Entry is valid
            valid_entries.append(entry)

        # Import if merge=True and there are valid entries
        if merge and valid_entries:
            for entry in valid_entries:
                self.memory_store.append_entry(entry)

        return (len(valid_entries), validation_errors)
