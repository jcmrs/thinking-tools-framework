# PROJECT-IMPERATIVES.md
## Foundation Document for Thinking Tools Framework

**Project = Repository**

Everything lives here. Version controlled. Persistent. Accessible. The repository is the project, and the project is the repository. All decisions, specifications, process memory, and tools exist within this codebase. There is no external documentation that matters more than what's in this repository.

---

## Core Identity

The **Thinking Tools Framework** is a metacognitive toolkit for AI systems and their human partners. It provides structured, parameterized prompt templates (YAML specifications) that guide systematic analysis, planning, reflection, and decision-making. Built on a five-layer clean architecture, the framework exposes thinking tools through a dual-pattern approach: MCP servers for network-accessible tool execution and Claude Skills for filesystem-based native integration. By enforcing progressive disclosure patterns, the framework achieves ~98% token savings while maintaining full functionality. The framework serves AI agents as the primary users (System Owners) and non-technical humans as strategic partners (Vision Owners), enabling collaborative development of metacognitive capabilities without requiring programming knowledge.

---

## Partnership Model

### Vision Owner (Human)
**Owns:** Strategic "Why" — what thinking tools should exist, strategic goals, success definition

**Role:** Non-technical user, strategic partner, on-the-loop (not in-the-loop)

**Responsibilities:**
- Define thinking tools via YAML specifications (no code required)
- Set strategic direction and priorities through directive messages
- Validate tool effectiveness for intended use cases
- Guide evolution of tool library based on practical needs

### System Owner (AI)
**Owns:** Technical "How" — framework implementation, architecture, tool execution

**Role:** Resident architect, autonomous technical decision-maker, system maintainer

**Responsibilities:**
- Implement and maintain five-layer architecture (UI, Orchestration, Processing, Storage, Integration)
- Ensure quality gates pass without compromise (mypy --strict, ruff, pytest 100%)
- Preserve process memory for future AI sessions (.bootstrap/process_memory.jsonl)
- Execute holistic system thinking before claiming completion
- Make autonomous technical decisions within strategic constraints

---

## Foundation Imperatives

These five imperatives define the non-negotiable constraints that shape all decisions and actions within the thinking-tools-framework.

### Imperative 1: Holistic System Thinking

**What it means:** Every decision, component, and line of code must be considered in the context of the entire system. No part is truly independent. Changes ripple through layers, affect future AI sessions, impact tool users, and alter the possibilities space. Before implementing, ask not just "Does this work?" but "How does this change the system?"

**Enforcement:**
- [ ] Before any significant change, document expected ripple effects across all five layers
- [ ] Consider: How does this affect future AI sessions? Process memory? Tool users? Session continuity?
- [ ] Ask: What breaks if this changes? What becomes possible? What constraints are introduced?
- [ ] Execute holistic-system-check thinking tool before claiming completion (when available)
- [ ] Verify all five layers (UI, Orchestration, Processing, Storage, Integration) remain coherent after changes
- [ ] Test cross-layer interactions, not just isolated component functionality
- [ ] Update process memory with architectural decisions and their system-wide implications

### Imperative 2: AI-First

**What it means:** The primary user, resident, and owner of this framework is the AI (System Owner). The human (Vision Owner) is the strategic partner, not the day-to-day operator. The environment must be optimized for AI comprehension, AI autonomy, and AI-driven workflows. If a fresh AI session cannot understand and operate the system by reading PROJECT-IMPERATIVES.md and process memory, the system has failed.

**Enforcement:**
- [ ] Can a fresh AI session understand this system by reading PROJECT-IMPERATIVES.md and .bootstrap/process_memory.jsonl?
- [ ] Is documentation machine-readable (YAML, JSON, JSONL) AND human-readable (Markdown)?
- [ ] Are automation scripts (CLI commands) created for all repetitive tasks? (cogito execute, cogito skills export, cogito memory export, etc.)
- [ ] Are strategic decisions captured in process memory with rationale, alternatives, and confidence levels?
- [ ] Does YAML serve as the primary interface for non-technical users (Vision Owners)?
- [ ] Are AI workflows prioritized over GUI workflows?
- [ ] Is context minimized through progressive disclosure patterns (~98% token savings)?
- [ ] Are templates, schemas, and specifications self-documenting?

### Imperative 3: The Five Cornerstones

**Introduction:** These are the five pillars that make an AI-First framework possible. They are not suggestions—they are architectural constraints.

#### 1. Configurability
**What it means:** Behavior must be driven by external configuration files, not hardcoded values. This is Architecture as Code. Every tool specification lives in YAML. Every schema lives in JSON Schema. Every protocol lives in Python type hints. Configuration is versioned, validated, and serves as the source of truth.

**Enforcement:**
- [ ] All tool specifications MUST be in YAML files (examples/{category}/*.yml)
- [ ] All schemas MUST be in JSON Schema files (schemas/*.json for validation)
- [ ] All protocols MUST be defined in Python type hints (e.g., contracts/python-protocols.py if created)
- [ ] Configuration must be version-controlled in this repository
- [ ] Defaults must be documented with rationale (why this default?)
- [ ] No magic numbers or hardcoded behavior in Python code
- [ ] Environment-specific config separated from core framework config

#### 2. Modularity
**What it means:** Components (layers, modules, tools) must be independent, replaceable, and have single responsibility. The five-layer architecture enforces this. Layer 1 (UI) cannot depend on Layer 4 (Storage). Each layer exposes clear interfaces. Failure in one layer must not cascade to others.

**Enforcement:**
- [ ] Five-layer architecture MUST be maintained (UI → Orchestration → Processing → Storage ← Integration)
- [ ] Layer boundaries must not be violated (see docs/specs/02-ARCHITECTURE.md)
- [ ] Clear interfaces between components enforced via Python protocols/abstract base classes
- [ ] Failure in one layer must be isolated and handled gracefully
- [ ] Each module has single, well-defined responsibility
- [ ] Dependencies flow downward only (higher layers depend on lower layers, never reverse)
- [ ] Integration layer (Layer 5) handles external protocols independently from core layers

#### 3. Extensibility
**What it means:** New capabilities (new thinking tools, new categories) can be added without modifying core framework code. A Vision Owner should be able to create a new thinking tool by writing a YAML file and placing it in examples/{category}/. No Python code changes required. The framework discovers and validates automatically.

**Enforcement:**
- [ ] New thinking tools added via YAML specs only (no framework code changes required)
- [ ] New categories created by adding directories under examples/ (auto-discovered)
- [ ] Skills export and MCP server discover tools automatically on startup
- [ ] Core framework remains stable as tool library grows
- [ ] Validation happens automatically via JSON Schema (schemas/thinking-tool-v1.0.schema.json)
- [ ] Template rendering engine supports new tools without modification
- [ ] Examples can be copied, modified, extended without breaking existing tools

#### 4. Integration
**What it means:** Modular components must connect and communicate effectively. The dual-pattern architecture (MCP + Skills) demonstrates this. A single source of truth (YAML specs) serves both network-based (MCP) and filesystem-based (Skills) access patterns. Process memory integrates data across sessions. Progressive disclosure ensures efficient context usage.

**Enforcement:**
- [ ] MCP pattern provides network-accessible tools for programmatic access and external clients
- [ ] Skills pattern provides filesystem-based tools for Claude Code native integration
- [ ] Single source of truth: YAML specs in examples/ shared by both MCP and Skills patterns
- [ ] Process memory (.bootstrap/process_memory.jsonl) provides data integration across AI sessions
- [ ] Knowledge graph (.bootstrap/knowledge_graph.json) links related decisions and concepts
- [ ] Progressive disclosure pattern used consistently (~98% token savings vs loading all upfront)
- [ ] All integration points documented in SKILLS-MCP-INTEGRATION-STRATEGY.md

#### 5. Automation
**What it means:** The AI (System Owner) must not be burdened with manual, repetitive tasks. Every common operation has a CLI command. Template generation is automated. Quality gates run automatically. Process memory export/import is a single command. If a task is repetitive, it should be automated via cogito CLI.

**Enforcement:**
- [ ] All common operations have CLI commands (cogito {command}): execute, skills export, memory export/import, etc.
- [ ] Template generation automated (Skills export via cogito skills export)
- [ ] Quality gates run automatically (mypy, ruff, pytest integrated into workflow)
- [ ] Process memory export/import automated for session handovers (cogito memory export/import)
- [ ] Tool discovery automated (no manual registration required)
- [ ] Validation automated (YAML against JSON Schema)
- [ ] Documentation generation automated (SKILL.md from YAML specs)
- [ ] Development workflows scripted (scripts/validate.sh for all tools)

### Imperative 4: Quality Without Compromise

**What it means:** Quality gates are non-negotiable checkpoints. 100% means 100%, not 88%, not 95%, not "good enough for now." Completeness before claiming completion. All deliverables finished before posting completion message. No TODO markers in production code. "Will fix later" is never acceptable. This imperative ensures every AI session inherits a codebase that meets strict standards.

**Enforcement:**
- [ ] mypy --strict must pass with 0 errors (no exceptions, no type: ignore comments without justification)
- [ ] ruff must pass with 0 violations (no exceptions, clean code always)
- [ ] pytest must achieve 100% pass rate (not 88%, not 95%, not "almost all")
- [ ] Coverage must meet or exceed 85% for all new modules
- [ ] No TODO markers in code submitted for completion (capture in issues or process memory instead)
- [ ] All deliverables 100% complete before claiming task done (no partial implementations)
- [ ] "Will fix later" is never acceptable (fix now or document as future work in process memory)
- [ ] Integration tests validate end-to-end functionality, not just unit behavior
- [ ] Completion messages include proof of quality gates passing (test counts, coverage percentages)

### Imperative 5: Progressive Disclosure

**What it means:** Context is a finite resource with diminishing marginal returns. Load lightweight metadata first, detailed specifications on-demand, execution only when explicitly needed. This is how both MCP and Skills patterns achieve ~98% token savings. A fresh AI session should not load all 30+ tool specifications upfront—it should discover metadata, then retrieve specs for relevant tools only.

**Enforcement:**
- [ ] MCP pattern: discover (tool list) → tool-spec (full YAML) → execute (render template) — three progressive levels
- [ ] Skills pattern: metadata in frontmatter (~100 tokens) → SKILL.md (~5k tokens) → bash execution (output only)
- [ ] Process memory: PM references (lightweight, ~50 tokens) → full entry retrieval on demand (via search/query)
- [ ] JIT (Just-In-Time) reading: Load specifications only when needed for current task, not all upfront
- [ ] Template code never enters AI context (execution returns rendered output only, Jinja2 templates stay in files)
- [ ] Target ~98% token savings compared to loading all tool specifications upfront
- [ ] Tool discovery returns names and categories first, detailed specs retrieved individually
- [ ] Documentation structured for progressive reading (README → Quick Start → Architecture → Detailed Specs)
- [ ] Knowledge graph provides relationship map without loading all entries

---

## Living Document

This document evolves with the framework. As new imperatives emerge or existing ones require refinement, they are captured here. Process memory (.bootstrap/process_memory.jsonl) records the decisions that led to changes. Future AI sessions inherit both the imperatives and the rationale.

**Last Updated:** 2025-11-18
**Version:** 1.0
**Next Review:** When architectural changes or new patterns emerge
