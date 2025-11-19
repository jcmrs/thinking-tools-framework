# Thinking Tools Framework - Session Context

**Generated:** 2025-11-15 23:45:08

## Project Status

- **Phase:** Bootstrap Package Creation
- **Completed:** All 27 technical specifications, 9 example thinking tools, process memory system
- **In Progress:** Bootstrap scripts, templates, project structure
- **Next Priority:** Complete Phase 3 (scripts/templates), then execute bootstrap

## Strategic Decisions (11)

Top 10 architectural decisions driving the framework:

### 1. YAML Specification Format
**Source:** ADR-001
**Summary:** Selected YAML over JSON, TOML, and Python DSL for thinking tool specifications
**Rationale:** Human readability and accessibility for non-programmers. YAML provides comments, multi-line strings, and familiar infrastructure pattern. Balances expressiveness with simplicity.
**Confidence:** 90%

### 2. Sandboxed Jinja2 Template Engine
**Source:** ADR-002
**Summary:** Use Jinja2 with custom sandboxed environment for template rendering
**Rationale:** Balance between power and security. Jinja2 is battle-tested, familiar, and provides rich features. Sandboxing prevents arbitrary code execution while preserving needed functionality (conditionals, loops, filters).
**Confidence:** 95%

### 3. Append-Only Process Memory Log
**Source:** ADR-003
**Summary:** Use JSONL append-only log with deprecation instead of deletion
**Rationale:** Never lose information - critical for AI-First principle. Deprecate entries instead of deleting to preserve context and decision history. JSONL format enables efficient append and streaming read.
**Confidence:** 95%

### 4. Hot-Reload Capability
**Source:** ADR-004
**Summary:** Support spec changes without restart via file watching and atomic swap
**Rationale:** Developer experience and iteration speed. Sub-second feedback loops enable rapid experimentation. File watcher detects changes, validates, and atomically swaps in new specs without disrupting running system.
**Confidence:** 85%

### 5. Multi-Layer Validation Pipeline
**Source:** ADR-005
**Summary:** Implement three sequential validation layers: schema, semantic, security
**Rationale:** Defense-in-depth for specification quality. Schema catches structure errors, semantic catches logic errors, security catches dangerous patterns. Each layer adds context to errors for developer guidance.
**Confidence:** 90%

### 6. Protocol-Based Plugin Architecture
**Source:** ADR-006
**Summary:** Use Python Protocols (PEP 544) for structural subtyping with entry point discovery
**Rationale:** Extensibility without coupling. Plugins discovered via entry points, validated via protocol conformance. No core changes needed for new plugins. Modularity and extensibility cornerstones embodied.
**Confidence:** 90%

### 7. Semantic Versioning for Specifications
**Source:** ADR-007
**Summary:** Use SemVer (MAJOR.MINOR.PATCH) for spec versions with clear breaking change policy
**Rationale:** Predictable evolution and backward compatibility. MAJOR for breaking changes, MINOR for features, PATCH for fixes. Enables gradual migration and clear expectations for spec consumers.
**Confidence:** 95%

### 8. Five-Layer Architecture
**Source:** ADR-008
**Summary:** Organize system into UI, Orchestration, Processing, Storage, Integration layers
**Rationale:** Clear separation of concerns enables independent evolution. Each layer has single responsibility. Dependency direction enforced (higher layers depend on lower). Modularity cornerstone embodied in architecture.
**Confidence:** 90%

### 9. Zero Serena Core Modifications
**Source:** ADR-009
**Summary:** Integrate with Serena exclusively through MCP tool interface, no core changes
**Rationale:** Stability and decoupling. Thinking tools remain independent. Serena updates don't break thinking tools. Integration cornerstone demonstrated through MCP protocol.
**Confidence:** 95%

### 10. Declarative-First Design
**Source:** ADR-010
**Summary:** Favor declarative specifications over imperative code
**Rationale:** Accessibility and automation. Non-programmers can create tools through YAML. Declarative specs enable code generation, validation, and analysis. Aligns with configurability and automation cornerstones.
**Confidence:** 90%

## Recent Lessons Learned (11)

Key insights from development:

### Modularity Enables JIT Learning
Breaking system into independent modules enables just-in-time learning for AI agents

**Learning:** Discovered that Claude Code instances can load module-specific context on demand rather than reading entire system. Memory summaries (150-200 words) plus full specs on demand achieves 70% token savings. Modularity cornerstone directly enables AI-First principle.

### AI-First Requires Explicit Imperative Integration
AI-First principles must be explicitly integrated into all specifications, not assumed

**Learning:** Initially assumed AI-First would emerge naturally. Learned it requires deliberate design: machine-readable contracts (JSON schemas), self-documenting code (inline metadata), context preservation (process memory), no hidden state (everything queryable). Created ADR-000 to codify this learning.

### Template Injection is Primary Security Risk
In declarative systems with templates, template injection becomes the main attack surface

**Learning:** Learned that moving logic from code to templates shifts security focus. Template injection (inserting malicious template code) becomes primary risk. Requires sandboxing, input validation, and careful filter/tag whitelisting. Security must be designed into template engine, not added later.

### Process Memory is Critical for Handovers
Without process memory, AI session transitions lose critical context and rationale

**Learning:** Observed that new Claude instances struggled to understand 'why' decisions were made when only given 'what' was decided. Process memory capturing rationale, alternatives, and confidence enables effective handovers. Created session_handover.yml thinking tool to operationalize this.

### Five Cornerstones Must Be Measurable
Abstract principles need concrete manifestations to be useful in code review

**Learning:** Realized Five Cornerstones (Configurability, Modularity, Extensibility, Integration, Automation) were too abstract for practical assessment. Created code_review_checklist.yml with specific, checkable criteria for each cornerstone. Principles become actionable through checklists.

## Key Assumptions (6)

Critical assumptions to validate:

### Spec Format Won't Need Frequent Major Changes
- **Assumption:** Assumed specification schema will be stable after v1.0
- **Rationale:** Betting that initial design captures core needs and future changes will be additive (MINOR/PATCH) rather than breaking (MAJOR). Semantic versioning provides migration path if assumption proves wrong. Confidence based on thorough upfront design.
- **Confidence:** 75%
- **Risk if wrong:** High

### Most Users Can Write YAML but Not Python
- **Assumption:** Assumed target users comfortable with YAML but not programming
- **Rationale:** Betting on infrastructure-as-code familiarity (Kubernetes, Docker Compose, CI/CD configs) being more widespread than Python programming. If wrong, Python DSL alternative remains viable future option. YAML accessibility enables broader adoption.
- **Confidence:** 80%
- **Risk if wrong:** Medium

### Jinja2 Sandbox is Sufficient Security
- **Assumption:** Assumed sandboxed Jinja2 provides adequate protection against template injection
- **Rationale:** Betting on battle-tested sandboxing approach (used in Ansible, etc.) combined with strict whitelisting. Aware of historical sandbox escapes but mitigated through: restricted feature set, input validation, resource limits, and regular security updates. Multi-layer validation provides defense-in-depth.
- **Confidence:** 85%
- **Risk if wrong:** Medium

### Append-Only Log Won't Grow Too Large
- **Assumption:** Assumed process memory log size manageable with periodic archival
- **Rationale:** Betting that process memory entries (hundreds to low thousands) won't create performance issues. JSONL streaming read enables efficient processing. Log rotation and archival strategies available if growth becomes problem. Monitoring log size validates assumption over time.
- **Confidence:** 80%
- **Risk if wrong:** Medium

### File Watching is Reliable Across Platforms
- **Assumption:** Assumed file system watchers work reliably on Linux, macOS, Windows
- **Rationale:** Betting on mature file watching libraries (watchdog, inotify, etc.) being reliable across platforms. Aware of edge cases (network drives, Docker volumes) but acceptable for local development use case. Polling fallback available if watching fails.
- **Confidence:** 85%
- **Risk if wrong:** Medium

### Code Review Should Explicitly Check Five Cornerstones
- **Assumption:** Assumed code_review_checklist.yml should have explicit Five Cornerstones section
- **Rationale:** Decided to make principles actionable by providing checkable criteria for each cornerstone. Teaches users our values, ensures alignment, demonstrates principles in practice. Risk: might be too prescriptive for some users. Mitigation: tools are customizable.
- **Confidence:** 85%
- **Risk if wrong:** Medium

## Knowledge Graph Hotspots

Most-linked concepts (hub nodes in decision graph):

- Five Cornerstones (pm-004, pm-006, pm-021)
- AI-First Principles (pm-003, pm-017, pm-018, pm-020)
- Security (pm-002, pm-019, pm-024)
- Architecture (pm-008, pm-027)
- Templates (pm-002, pm-014, pm-015, pm-016)

## Recommended Reading Order

1. **Start Here:** IMPLEMENTATION-ROADMAP.md (current status)
2. **Architecture:** 02-ARCHITECTURE.md (system overview)
3. **Decisions:** 04-ARCHITECTURE-DECISION-RECORDS.md (why choices made)
4. **Imperatives:** specs/00-IMPERATIVES-INTEGRATION.md (Five Cornerstones + AI-First)
5. **Process Memory:** This file + process_memory.jsonl (full decision history)

## Quick Context Establishment

For new AI session:

```bash
# Read project status
cat IMPLEMENTATION-ROADMAP.md

# Read this session context
cat .cogito/bootstrap/session_context.md

# Query process memory
# (Use process memory tools when available)

# Review recent work
cat PHASE1-EXAMPLES-COMPLETE.md
```

**Time to establish full context:** 15-20 minutes
