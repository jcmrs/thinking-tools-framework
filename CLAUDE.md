# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Thinking Tools Framework is a Python project (cogito package) that provides AI-augmented metacognition tools for software development. It uses **parameterized YAML prompt templates** with Jinja2 rendering to guide systematic analysis, planning, and reflection.

Key architecture: **Five-layer clean architecture**
- Layer 1: UI (CLI, interfaces)
- Layer 2: Orchestration (tool discovery, execution)
- Layer 3: Processing (template rendering, validation)
- Layer 4: Storage (process memory, caching)
- Layer 5: Integration (MCP server, external integrations)

**Dependencies flow downward only** - no Layer 1 → Layer 4 communication.

## Development Commands

### Installation
```bash
# Install with dev dependencies
python3 -m pip install -e ".[dev]"

# Install with MCP support
python3 -m pip install -e ".[mcp]"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cogito --cov-report=html

# Run specific test file
pytest tests/unit/test_renderer.py

# Run specific test
pytest tests/unit/test_renderer.py::test_render_simple_template
```

### Code Quality
```bash
# Type checking (strict mode enabled)
mypy src/

# Linting (ruff configuration in pyproject.toml)
ruff check src/

# Code formatting (line length: 100)
black src/

# Validate all thinking tools against schema
bash scripts/validate.sh

# Validate specific directory
bash scripts/validate.sh examples/metacognition/
```

### Full Validation Suite
```bash
# Run complete validation (tests, typing, linting, tool validation)
bash scripts/validate.sh && pytest && mypy src/ && ruff check src/
```

## Code Style Requirements

### Python (PEP 8 + Black + strict mypy)
- **Line length:** 100 characters
- **Python version:** 3.11+ (use modern type hints)
- **Type hints:** Required for all public functions/classes
- **Docstrings:** Required for all public functions/classes
- **Import order:** standard library → third-party → local
- **Strict typing:** mypy strict mode enabled (`disallow_untyped_defs = true`)

Example function signature:
```python
from typing import Dict, Any
from pathlib import Path

def load_tool(tool_path: Path) -> Dict[str, Any]:
    """Load thinking tool from YAML file.

    Args:
        tool_path: Path to the YAML tool specification

    Returns:
        Parsed tool data as dictionary

    Raises:
        FileNotFoundError: If tool file doesn't exist
        ValidationError: If tool doesn't match schema
    """
```

### YAML Thinking Tools
- **Indentation:** 2 spaces
- **Quotes:** Double quotes for strings (when needed)
- **Format:** Follow `thinking-tool-v1.0.schema.json` schema
- **Validation:** Always run `bash scripts/validate.sh` after creating/editing tools

## Architecture Patterns

### Creating New Thinking Tools

1. **Choose category:** metacognition, review, handoff, debugging, planning, learning
2. **Copy template:** Start from similar existing tool in `examples/`
3. **Define metadata:** name (snake_case), display_name, description, category, author, tags
4. **Design parameters:** Use JSON Schema for type safety
5. **Write Jinja2 template:** Combine with Markdown for structured output
6. **Validate:** `bash scripts/validate.sh examples/category/tool.yml`

Key patterns:
- **Progressive depth:** Single tool with quick/standard/detailed parameter
- **Domain branching:** Conditional sections (`{% if language == 'python' %}`)
- **Checklists:** Explicit, checkable criteria for thoroughness

### Layer-Specific Development

**Layer 1 (UI):** CLI interfaces, user I/O formatting
**Layer 2 (Orchestration):** Tool discovery (auto-discovery from `examples/`), execution coordination
**Layer 3 (Processing):** Jinja2 rendering, JSON Schema validation, security checks
**Layer 4 (Storage):** Process memory JSONL format, caching strategies
**Layer 5 (Integration):** MCP protocol implementation, external tool adapters

**Critical:** Respect dependency flow - higher layers can depend on lower layers, never reverse.

## Five Cornerstones Principle

All code and thinking tools must embody these principles:

1. **Configurability** - Parameterized behavior, no hardcoded assumptions
2. **Modularity** - Clear separation of concerns, composable components
3. **Extensibility** - Plugin architecture, open for enhancement
4. **Integration** - Standard protocols (MCP), works with existing tools
5. **Automation** - Auto-discovery, validation, hot-reload support

Use `code_review_checklist.yml` to verify Five Cornerstones compliance.

## Process Memory System

The framework includes **52 process memory entries** documenting design decisions and lessons learned:

- `.bootstrap/process_memory.jsonl` - Machine-readable decision log
- `.bootstrap/knowledge_graph.json` - Relationship graph between decisions
- `.bootstrap/session_context.md` - Human-readable summary for AI onboarding

**When to update:** After significant architectural decisions, capture rationale, alternatives considered, and confidence levels.

## Coordination Protocol

This project uses **asynchronous coordination** for strategic oversight between external coordinators and the in-project Claude instance.

### Your Responsibilities

**1. Check inbox on session start:**
```bash
ls .coordination/inbox/
cat .coordination/inbox/msg-*.json
```

Process any directive, response, or strategic messages from the coordinator.

**2. Update progress after significant steps:**
- After each significant step: Update `.progress/current-task.json`
- After major milestones: Append progress to `.coordination/messages.jsonl`
- On completion: Post completion message with artifacts and quality gates

**3. Post questions for strategic decisions only:**
- Genuine ambiguity not covered in process memory or CLAUDE.md
- Priority/scope trade-offs requiring strategic direction
- **NOT for technical implementation details** - make autonomous decisions using process memory (PM-002, PM-005, etc.)

**4. Report blockers immediately:**
- Update `.progress/current-task.json` with blocker details
- Post blocker message to `.coordination/outbox/`
- Continue other work if possible

### Message Types
- **directive** - Task assignment from coordinator
- **question** - Ask coordinator for strategic direction
- **response** - Answer from coordinator
- **progress** - Update on current work
- **blocker** - Report blocking issue
- **completion** - Task complete with artifacts

See `.coordination/COORDINATION-PROTOCOL.md` for complete protocol specification.

## Testing Requirements

### Test Structure
```
tests/
├── unit/           # Isolated component tests
├── integration/    # Multi-component/layer interaction tests
└── fixtures/       # Test data and helpers
```

### Required Coverage
- **All new code:** Must include unit tests
- **Layer interactions:** Integration tests required
- **Thinking tools:** Schema validation tests required
- **Coverage target:** Aim for >80% coverage (`--cov=cogito`)

### TDD Encouraged
Write tests first for new features, especially for:
- Template rendering edge cases
- Validation logic
- Tool discovery mechanisms

## Common Workflows

### Adding a New Thinking Tool Category
1. Create directory: `examples/new_category/`
2. Create first tool following YAML schema
3. Validate: `bash scripts/validate.sh examples/new_category/`
4. Update README.md category list
5. Consider adding category to schema enum

### Extending Template Rendering
1. Modify `src/cogito/processing/` (Layer 3)
2. Add unit tests in `tests/unit/`
3. Verify existing tools still validate
4. Update documentation if new Jinja2 features added

### Adding MCP Integration Feature
1. Work in `src/cogito/integration/` (Layer 5)
2. Follow MCP protocol specifications
3. Ensure hot-reload compatibility
4. Test with actual MCP client (e.g., Claude Code)

## Special Notes

### AI-First Design Philosophy
- **Machine-readable:** YAML specs, JSON schemas, structured metadata
- **Self-documenting:** Inline docs, examples, rationale in YAML comments
- **Context preservation:** Use session handover tools before context limits
- **No hidden state:** All parameters explicit, deterministic execution

### Integration with Serena MCP
- Zero Serena modifications required
- Independent installation and updates
- Standard MCP tool interface
- Hot-reload support during development

### What NOT to Do
- Don't violate layer dependencies (no upward dependencies)
- Don't add hardcoded values - use parameters instead
- Don't skip validation - always run `bash scripts/validate.sh`
- Don't create tools without testing them on real use cases
- Don't modify thinking tools without validating against schema
