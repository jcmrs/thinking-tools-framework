"""SKILL.md generation from YAML tool specifications."""

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class SkillGenerator:
    """Generate Claude Code SKILL.md files from YAML tool specifications."""

    # Claude Skills constraints
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 1024
    FORBIDDEN_NAME_PATTERNS = ["anthropic", "claude"]

    def __init__(self, templates_dir: Path | None = None) -> None:
        """Initialize skill generator.

        Args:
            templates_dir: Optional path to templates directory.
                          If None, uses built-in templates.
        """
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
            autoescape=select_autoescape([]),
        )

    def generate_skill_name(self, display_name: str) -> str:
        """Convert display name to skill name format.

        Args:
            display_name: Human-readable name (e.g., "Think Aloud")

        Returns:
            Skill name (e.g., "think-aloud")

        Raises:
            ValueError: If name doesn't meet Claude Skills constraints
        """
        # Convert to lowercase
        name = display_name.lower()

        # Replace spaces and special chars with hyphens
        name = re.sub(r"[^a-z0-9-]", "-", name)

        # Remove consecutive hyphens
        name = re.sub(r"-+", "-", name)

        # Strip leading/trailing hyphens
        name = name.strip("-")

        # Validate length
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Skill name '{name}' exceeds maximum length "
                f"{self.MAX_NAME_LENGTH} chars"
            )

        # Check forbidden patterns
        for pattern in self.FORBIDDEN_NAME_PATTERNS:
            if pattern in name:
                raise ValueError(
                    f"Skill name '{name}' contains forbidden pattern '{pattern}'"
                )

        return name

    def generate_description(
        self, metadata: dict[str, Any], parameters: dict[str, Any]
    ) -> str:
        """Build skill description with when-to-use guidance.

        Args:
            metadata: Tool metadata from YAML
            parameters: Tool parameters schema

        Returns:
            Description string (max 1024 chars)
        """
        # Start with base description
        desc: str = str(metadata.get("description", ""))

        # Infer when-to-use from metadata
        use_cases = self._infer_use_cases(metadata, parameters)

        if use_cases:
            desc = f"{desc} Use when {use_cases}"

        # Truncate if needed
        if len(desc) > self.MAX_DESCRIPTION_LENGTH:
            desc = desc[: self.MAX_DESCRIPTION_LENGTH - 3] + "..."

        return desc

    def _infer_use_cases(
        self, metadata: dict[str, Any], parameters: dict[str, Any]
    ) -> str:
        """Infer when-to-use guidance from metadata and parameters.

        Args:
            metadata: Tool metadata
            parameters: Tool parameters

        Returns:
            When-to-use clause
        """
        # Extract category-based guidance
        category = metadata.get("category", "")
        category_hints = {
            "metacognition": "working through complex problems step-by-step",
            "review": "conducting code or system reviews",
            "handoff": "documenting decisions or transferring knowledge",
            "debugging": "investigating errors or unexpected behavior",
            "planning": "designing architecture or breaking down tasks",
        }

        if category in category_hints:
            return category_hints[category]

        # Extract from tags
        tags = metadata.get("tags", [])
        if "planning" in tags:
            return "planning or organizing complex work"
        if "analysis" in tags:
            return "analyzing systems or making decisions"
        if "documentation" in tags:
            return "creating or reviewing documentation"

        # Default
        return "you need structured guidance for this type of task"

    def generate_skill_md(
        self, tool_spec: dict[str, Any], source_path: Path
    ) -> str:
        """Generate SKILL.md content from tool specification.

        Args:
            tool_spec: Complete tool specification from YAML
            source_path: Path to source YAML file

        Returns:
            SKILL.md content as markdown string

        Raises:
            ValueError: If skill name or description invalid
        """
        metadata = tool_spec.get("metadata", {})
        parameters = tool_spec.get("parameters", {})

        # Generate skill name
        display_name = metadata.get("display_name", metadata.get("name", ""))
        skill_name = self.generate_skill_name(display_name)

        # Generate description
        description = self.generate_description(metadata, parameters)

        # Prepare template context
        context = {
            "skill_name": skill_name,
            "display_name": display_name,
            "description": description,
            "metadata": metadata,
            "parameters": parameters,
            "template": tool_spec.get("template", ""),
            "source_path": source_path,
        }

        # Render template
        try:
            template = self.env.get_template("SKILL.md.j2")
            return template.render(**context)
        except Exception:
            # Fallback to simple generation if template missing
            return self._generate_simple_skill_md(context)

    def _generate_simple_skill_md(self, context: dict[str, Any]) -> str:
        """Generate simple SKILL.md without template.

        Args:
            context: Template context dictionary

        Returns:
            Markdown-formatted SKILL.md content
        """
        metadata = context["metadata"]
        parameters = context["parameters"]

        # Build frontmatter
        frontmatter = f"""---
name: {context['skill_name']}
description: {context['description']}
---
"""

        # Build instructions
        instructions = f"""# {context['display_name']}

## Instructions

{metadata.get('description', 'No description available.')}

**When to use:**
- {self._infer_use_cases(metadata, parameters)}

**Parameters:**
"""

        # Add parameter docs
        if parameters and "properties" in parameters:
            for param_name, param_spec in parameters["properties"].items():
                required = param_name in parameters.get("required", [])
                req_str = "required" if required else "optional"
                param_desc = param_spec.get("description", "No description")
                instructions += f"- `{param_name}` ({req_str}): {param_desc}\n"

        instructions += f"""
**Execution:**
```bash
cogito execute {metadata.get('name', 'tool')} \\
  --parameter "value"
```

**Output:** Structured prompts or guidance based on parameters.
"""

        # Build examples section
        examples = "\n## Examples\n\n"
        tool_examples = metadata.get("examples", [])
        if tool_examples:
            for i, example in enumerate(tool_examples, 1):
                examples += f"### Example {i}\n```bash\n"
                examples += f"cogito execute {metadata.get('name', 'tool')}"
                if isinstance(example, dict) and "parameters" in example:
                    for k, v in example["parameters"].items():
                        examples += f' \\\n  --{k} "{v}"'
                examples += "\n```\n\n"

        # Build reference section
        reference = f"""
## Reference

**Category:** {metadata.get('category', 'unknown')}
**Tags:** {', '.join(metadata.get('tags', []))}
**Source:** {context['source_path']}
"""

        return frontmatter + instructions + examples + reference

    def generate_bash_wrapper(self, tool_name: str) -> str:
        """Generate bash execution wrapper script.

        Args:
            tool_name: Tool name (from YAML metadata.name)

        Returns:
            Bash script content
        """
        try:
            template = self.env.get_template("execute.sh.j2")
            return template.render(tool_name=tool_name)
        except Exception:
            # Fallback to simple wrapper
            return f"""#!/usr/bin/env bash
# Auto-generated execution wrapper for {tool_name}
set -euo pipefail

TOOL_NAME="{tool_name}"
COGITO_BIN="${{COGITO_BIN:-cogito}}"

# Execute thinking tool via CLI
exec "$COGITO_BIN" execute "$TOOL_NAME" "$@"
"""
