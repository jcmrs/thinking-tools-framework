# Thinking Tools Framework

**AI-Augmented Metacognition for Software Development**

The Thinking Tools Framework provides structured thinking prompts, checklists, and frameworks that help AI coding assistants (and humans) work more effectively by making reasoning processes explicit.

## What Are Thinking Tools?

Thinking tools are **parameterized prompt templates** that guide systematic analysis, planning, and reflection during software development. They transform implicit cognitive processes into explicit, repeatable frameworks.

### Example Use Cases

- **Code Review:** Systematic quality assessment with explicit Five Cornerstones checks
- **Debugging:** Root cause analysis using Five Whys technique
- **Architecture Design:** Multi-aspect system evaluation and trade-off analysis
- **Session Handoff:** Zero-information-loss context preservation for AI continuity
- **Metacognition:** Think aloud, assumption checking, fresh eyes exercises

## Quick Start

```bash
# 1. Install dependencies
python3 -m pip install -e ".[dev]"

# 2. Explore example thinking tools
ls examples/

# 3. Read 5-minute onboarding guide
cat docs/QUICK_START.md

# 4. Validate all tools
bash scripts/validate.sh
```

## Project Structure

```
thinking-tools-framework/
├── src/cogito/              # Framework source (five-layer architecture)
│   ├── ui/                  # CLI and interfaces
│   ├── orchestration/       # Tool discovery and execution
│   ├── processing/          # Template rendering and validation
│   ├── storage/             # Process memory and caching
│   └── integration/         # MCP server and external integrations
├── examples/                # 9 production-ready thinking tools
│   ├── metacognition/       # think_aloud, assumption_check, fresh_eyes
│   ├── review/              # code_review_checklist, architecture_review
│   ├── handoff/             # session_handover, context_preservation
│   └── debugging/           # five_whys, error_analysis
├── schemas/                 # JSON schemas for validation
├── docs/                    # Complete technical specifications
└── .bootstrap/              # Process memory and knowledge graph
```

## The Five Cornerstones

Every thinking tool and framework component embodies these principles:

1. **Configurability** - Parameterized behavior, no hardcoded assumptions
2. **Modularity** - Clear separation of concerns, composable components
3. **Extensibility** - Plugin architecture, open for enhancement
4. **Integration** - MCP protocol, works with existing tools
5. **Automation** - Auto-discovery, validation, hot-reload

## AI-First Design

Built from the ground up for AI coding assistants:

- **Machine-Readable:** YAML specifications, JSON schemas, structured metadata
- **Self-Documenting:** Inline documentation, examples, and rationale
- **Context Preservation:** Process memory system captures decisions and learnings
- **No Hidden State:** Explicit parameters, deterministic execution
- **Zero-Information-Loss:** Session handover tools for AI continuity

## Architecture Overview

**Five-Layer Architecture:**

```
┌─────────────────────────────────────┐
│  Layer 1: UI (CLI, Interfaces)      │  ← User interaction
├─────────────────────────────────────┤
│  Layer 2: Orchestration             │  ← Tool discovery, execution
├─────────────────────────────────────┤
│  Layer 3: Processing                │  ← Template rendering, validation
├─────────────────────────────────────┤
│  Layer 4: Storage                   │  ← Process memory, caching
├─────────────────────────────────────┤
│  Layer 5: Integration               │  ← MCP server, external tools
└─────────────────────────────────────┘
```

## Creating a Thinking Tool

Thinking tools are YAML files with this structure:

```yaml
version: "1.0"

metadata:
  name: "my_tool"
  display_name: "My Thinking Tool"
  description: "What this tool helps you do"
  category: "metacognition"
  author: "Your Name"
  tags: ["tag1", "tag2"]

parameters:
  type: "object"
  properties:
    depth:
      type: "string"
      enum: ["quick", "detailed"]
      default: "quick"
  required: []

template:
  source: |
    # Analysis - {{ depth|upper }}

    {% if depth == 'quick' %}
    ## Quick Analysis
    - What's the core question?
    - What's the simplest approach?
    {% else %}
    ## Detailed Analysis
    - Context and background
    - Multiple approaches considered
    - Trade-offs and decisions
    {% endif %}
```

## Example Tools Included

**Metacognition (3 tools)**
- `think_aloud.yml` - Verbalize reasoning process
- `assumption_check.yml` - Surface implicit assumptions
- `fresh_eyes_exercise.yml` - Step back and re-evaluate

**Review (2 tools)**
- `code_review_checklist.yml` - Comprehensive code quality assessment
- `architecture_review.yml` - System design evaluation

**Handoff (2 tools)**
- `session_handover.yml` - AI session context preservation
- `context_preservation.yml` - Quick interruption handling

**Debugging (2 tools)**
- `five_whys.yml` - Root cause analysis
- `error_analysis.yml` - Structured error investigation

## Process Memory System

The framework includes a **process memory system** that captures:

- Strategic decisions and rationale
- Alternatives considered and why rejected
- Lessons learned during design and development
- Assumptions made and confidence levels
- Mental models for understanding the system

**52 Process Memory Entries** document the complete design journey.

Access via:
- `.bootstrap/process_memory.jsonl` - Machine-readable log
- `.bootstrap/knowledge_graph.json` - Relationship graph
- `.bootstrap/session_context.md` - Human-readable summary

## Integration with Serena MCP

This framework integrates with Serena (Claude Code's MCP server) via the Model Context Protocol:

- **Zero Serena modifications required**
- **Independent installation and updates**
- **Standard MCP tool interface**
- **Hot-reload support for development**

## Development

```bash
# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
black src/

# Full validation
bash scripts/validate.sh
```

## Documentation

- **[QUICK_START.md](docs/QUICK_START.md)** - 5-minute onboarding
- **[Architecture Decision Records](docs/specs/)** - Design rationale
- **[Technical Specifications](docs/specs/)** - Complete spec suite
- **[Session Context](.bootstrap/session_context.md)** - Framework context

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Creating new thinking tools
- Extending the framework
- Submitting improvements
- Code style and standards

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with the Five Cornerstones principles and AI-First design philosophy.

Designed for AI coding assistants like Claude Code, with humans as strategic partners.

---

**Ready to think more systematically? Explore the examples and create your own thinking tools!**
