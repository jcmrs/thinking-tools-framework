# Process Memory System

## Overview

The framework includes **52 process memory entries** documenting design decisions and lessons learned throughout development.

## File Locations

### `.bootstrap/process_memory.jsonl`
Machine-readable decision log in JSONL (JSON Lines) format.
- Append-only structure (never delete, only deprecate)
- Each entry is a complete JSON object on one line
- Enables efficient streaming reads

### `.bootstrap/knowledge_graph.json`
Relationship graph between decisions showing:
- Dependencies between decisions
- Related architectural choices
- Evolution of design thinking

### `.bootstrap/session_context.md`
Human-readable summary for AI onboarding containing:
- Project status and current phase
- Top strategic decisions (11 architectural choices)
- Recent lessons learned
- Next priorities

## When to Update Process Memory

Add new process memory entries after:
- Significant architectural decisions
- Design pattern choices
- Framework structure changes
- Major refactoring decisions
- Performance optimization choices
- Security-related decisions

## What to Capture

For each decision, document:
1. **Rationale:** Why this approach was chosen
2. **Alternatives considered:** What other options were evaluated
3. **Trade-offs:** What was gained and what was sacrificed
4. **Confidence level:** How certain are we this is the right choice (%)
5. **Related decisions:** What other choices depend on or influence this

## Key Documented Decisions (Top 11)

1. **YAML Specification Format** - Human readability for non-programmers
2. **Sandboxed Jinja2 Template Engine** - Balance power and security
3. **Append-Only Process Memory Log** - Never lose information
4. **Hot-Reload Capability** - Sub-second feedback loops
5. **Multi-Layer Validation Pipeline** - Defense-in-depth for quality
6. **Protocol-Based Plugin Architecture** - Extensibility without coupling
7. **Semantic Versioning for Specs** - Predictable evolution
8. **Five-Layer Architecture** - Clear separation of concerns
9. **Zero Serena Core Modifications** - Stability and decoupling
10. **Declarative-First Design** - Accessibility and automation
11. **MCP Protocol Integration** - Standard tool interface

## Process Memory Format

Each entry should capture:
```json
{
  "id": "ADR-XXX",
  "timestamp": "2025-11-15T23:45:08",
  "type": "architectural_decision",
  "title": "Decision Title",
  "summary": "Brief one-line summary",
  "rationale": "Detailed reasoning",
  "alternatives": ["Alternative 1", "Alternative 2"],
  "confidence": 90,
  "tags": ["architecture", "design"]
}
```

## Using Process Memory

### For AI Agents
- Read `.bootstrap/session_context.md` for quick onboarding
- Consult process memory before making similar decisions
- Add new entries when making architectural choices
- Reference existing decisions to maintain consistency

### For Human Developers
- Review process memory to understand "why" not just "what"
- Use it to avoid repeating past mistakes
- Add entries to capture tribal knowledge
- Keep context alive across team changes
