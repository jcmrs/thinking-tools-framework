# Project Overview

## Purpose
The Thinking Tools Framework (cogito package) provides AI-augmented metacognition tools for software development. It uses **parameterized YAML prompt templates** with Jinja2 rendering to guide systematic analysis, planning, and reflection.

## Package Name
`cogito`

## Tech Stack
- **Language:** Python 3.11+ (strict typing required)
- **Dependencies:**
  - jinja2>=3.1.0 (template rendering)
  - pyyaml>=6.0.0 (YAML parsing)
  - jsonschema>=4.20.0 (validation)
  - watchdog>=3.0.0 (hot-reload)
  - pydantic>=2.5.0 (data validation)
- **Dev Dependencies:**
  - pytest>=7.4.0 (testing)
  - pytest-cov>=4.1.0 (coverage)
  - mypy>=1.7.0 (type checking)
  - ruff>=0.1.0 (linting)
  - black>=23.0.0 (formatting)
- **Optional:** mcp>=0.1.0 (MCP server integration)

## Five-Layer Clean Architecture
**Critical:** Dependencies flow downward only - no upward dependencies allowed.

1. **Layer 1: UI** - CLI interfaces, user I/O formatting
2. **Layer 2: Orchestration** - Tool discovery (auto-discovery from examples/), execution coordination
3. **Layer 3: Processing** - Jinja2 rendering, JSON Schema validation, security checks
4. **Layer 4: Storage** - Process memory JSONL format, caching strategies
5. **Layer 5: Integration** - MCP protocol implementation, external tool adapters

## Core Directories
- `src/cogito/` - Framework source (five-layer architecture)
- `examples/` - Production-ready thinking tools (metacognition, review, handoff, debugging)
- `schemas/` - JSON schemas for validation
- `tests/` - Unit and integration tests
- `.bootstrap/` - Process memory system (52 documented decisions)
- `scripts/` - Validation and utility scripts

## Five Cornerstones Principle
All code must embody:
1. **Configurability** - Parameterized behavior, no hardcoded assumptions
2. **Modularity** - Clear separation of concerns, composable components
3. **Extensibility** - Plugin architecture, open for enhancement
4. **Integration** - Standard protocols (MCP), works with existing tools
5. **Automation** - Auto-discovery, validation, hot-reload support

## AI-First Design
- Machine-readable YAML specs and JSON schemas
- Self-documenting with inline rationale
- Context preservation via process memory system
- Explicit parameters, deterministic execution
- Zero-information-loss session handover tools
