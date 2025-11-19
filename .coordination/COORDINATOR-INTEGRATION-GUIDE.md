# Coordinator Integration Guide
## For Multi-Agent Coordination of Thinking-Tools-Framework

**Version:** 1.0
**Date:** 2025-11-17
**Audience:** Coordinator Claude instances (external, e.g., running in Serena)
**Purpose:** Complete reference for coordinating thinking-tools-framework implementation

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding Your Role](#understanding-your-role)
3. [Coordination Protocol](#coordination-protocol)
4. [Current State and Context](#current-state-and-context)
5. [Skills + MCP Dual-Pattern Architecture](#skills--mcp-dual-pattern-architecture)
6. [Process Memory References](#process-memory-references)
7. [Directive Templates](#directive-templates)
8. [Quality Gate Requirements](#quality-gate-requirements)
9. [Common Patterns and Workflows](#common-patterns-and-workflows)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### On Session Start - ALWAYS Execute

```bash
# 1. Load coordination protocol
cat .coordination/COORDINATION-PROTOCOL.md

# 2. Check current state
cat .progress/current-task.json | jq .

# 3. Check for completion messages
ls -la .coordination/outbox/

# 4. Load Skills+MCP integration strategy
cat .coordination/SKILLS-MCP-INTEGRATION-STRATEGY.md

# 5. Review latest process memory
tail -5 .bootstrap/process_memory.jsonl | jq .
```

### Your Core Responsibilities

1. **READ** outbox messages (completion, questions, blockers)
2. **ANALYZE** results and quality gates
3. **CREATE** next directives in inbox
4. **ARCHIVE** outbox messages after processing (manual, for control)
5. **NEVER** write code directly to the project
6. **NEVER** make technical implementation decisions (instance's job)

### Current Project Status (2025-11-17 23:30)

- **Phase:** All 5 layers COMPLETE ✅
- **Current Priority:** Priority 1 (Process Memory Provisioning) - directive issued
- **MCP Status:** Production validated (98% token savings confirmed)
- **Next Phase:** Priority 1.5 (Skills Export) - proposed in strategy doc

---

## Understanding Your Role

### You Are: Strategic Coordinator

**Your Domain:**
- Strategic direction and priorities
- Roadmap sequencing
- Resource allocation decisions
- Pattern recognition (e.g., graphiti-mcp duplicate module issue)
- Cross-project learning integration
- Quality gate review and acceptance

**NOT Your Domain:**
- Technical implementation details
- Code writing or debugging
- Tool/library selection (unless strategic trade-off)
- Test implementation specifics
- File structure micro-decisions

### The Instance Is: Autonomous Technical Lead

**Instance's Domain:**
- All technical implementation decisions
- Code architecture within layer boundaries
- Test strategy and implementation
- Tool/library selection for implementation
- Quality gate execution
- Autonomous problem-solving (using process memory)

**NOT Instance's Domain:**
- Strategic priority changes
- Roadmap modifications
- Cross-project integration decisions
- When to ship/pivot

### The Partnership Model

```
┌─────────────────────────────────────────────────┐
│ COORDINATOR (You)                               │
│ - Strategic direction                           │
│ - Priority sequencing                           │
│ - Pattern recognition from other projects       │
│ - Quality acceptance                            │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Asynchronous
                  │ File-based
                  │ JSON messages
                  │
┌─────────────────▼───────────────────────────────┐
│ PROJECT INSTANCE (thinking-tools-framework)     │
│ - Autonomous technical decisions                │
│ - Implementation execution                      │
│ - Quality gates enforcement                     │
│ - Self-directed problem solving                 │
└─────────────────────────────────────────────────┘
```

**Critical Success Pattern:**
- You provide **WHAT** and **WHY** (objectives, context, constraints)
- Instance determines **HOW** (implementation, tools, architecture)
- Instance asks questions **ONLY** for genuine strategic ambiguity
- You trust instance's technical decisions (backed by process memory)

---

## Coordination Protocol

### Message Flow

```
Coordinator                         Instance
    │                                  │
    │  1. Create directive.json        │
    ├──────────────────────────────────>│
    │      (.coordination/inbox/)      │
    │                                  │
    │                                  │  2. Read inbox
    │                                  │  3. Archive to dated folder
    │                                  │  4. Execute work
    │                                  │  5. Run quality gates
    │                                  │
    │  6. Read completion.json         │
    │<──────────────────────────────────┤
    │      (.coordination/outbox/)     │
    │                                  │
    │  7. Analyze results              │
    │  8. Create next directive        │
    │  9. Archive outbox message       │
    │     (manual, for control)        │
    │                                  │
```

### Directory Structure

```
.coordination/
├── inbox/              # Messages TO instance (you write here)
│   ├── msg-YYYYMMDD-HHMMSS-*.json
│   └── archived/       # Instance archives after reading
├── outbox/             # Messages FROM instance (you read here)
│   └── msg-YYYYMMDD-HHMMSS-*.json
├── archive/            # You archive outbox messages here
│   └── YYYY-MM-DD/
│       └── msg-*.json
└── messages.jsonl      # Append-only log (both directions)

.progress/
├── current-task.json   # Instance updates continuously
├── completed-tasks.jsonl
└── metrics.json
```

### Message Types You'll Handle

**FROM Instance (outbox):**
1. **Completion**: Task done, artifacts ready, quality gates passed
2. **Question**: Genuine strategic ambiguity (rare, instance should self-solve)
3. **Blocker**: Cannot proceed, needs coordinator decision
4. **Progress**: Milestone update (informational)
5. **Error**: Quality gate failure or unexpected issue

**TO Instance (inbox):**
1. **Directive**: New task assignment with context
2. **Response**: Answer to instance's question
3. **Priority Change**: Adjust current focus

### Archiving Protocol (IMPORTANT)

**Your Responsibility:**
```bash
# After reading and acting on outbox message
mv .coordination/outbox/msg-YYYYMMDD-HHMMSS.json \
   .coordination/archive/$(date +%Y-%m-%d)/

# WHY: Manual archiving gives you explicit control over message lifecycle
# WHEN: After you've read, analyzed, and created next directive
```

**Instance's Responsibility:**
```bash
# Instance auto-archives inbox after reading
mv .coordination/inbox/msg-*.json \
   .coordination/inbox/archived/

# This happens automatically - don't interfere
```

---

## Current State and Context

### Five-Layer Architecture (ALL COMPLETE ✅)

**Layer 1: UI/CLI**
- Status: ✅ Complete (2025-11-17 21:00)
- Components: Click-based CLI, 6 commands
- Quality: 18 unit tests, 81% coverage
- PM Reference: N/A (straightforward UI layer)

**Layer 2: Orchestration**
- Status: ✅ Complete (2025-11-16)
- Components: ToolRegistry, ToolExecutor
- Quality: mypy strict, ruff clean, 95% coverage
- PM Reference: PM-004 (Tool Discovery)

**Layer 3: Processing**
- Status: ✅ Complete (2025-11-16)
- Components: TemplateRenderer, ParameterValidator
- Quality: 92% coverage, all quality gates
- PM Reference: PM-002 (Sandboxed Jinja2)

**Layer 4: Storage**
- Status: ✅ Complete (2025-11-16)
- Components: ProcessMemoryStore, KnowledgeGraph
- Quality: 95% coverage
- PM Reference: PM-006 (Process Memory Schema)

**Layer 5: Integration (MCP)**
- Status: ✅ Complete + Production Validated (2025-11-17 22:30)
- Components: FastMCP server, progressive disclosure
- Quality: Smoke test 3/3 passed, 98% token savings
- PM Reference: PM-010, PM-017, PM-021

### Critical Technical Learnings

**Module Duplication Prevention (PM-021):**
- **Issue**: Missing `src/cogito/__init__.py` caused namespace package ambiguity
- **Risk**: Duplicate MCP instances with separate event loops
- **Pattern Recognition**: You identified this from graphiti-mcp project
- **Solution**: Added __init__.py, configured mypy with explicit_package_bases
- **Validation**: Mypy now passes --strict with no "found twice" error

**FastMCP Integration (PM-017):**
- Decorator-based API (@mcp.tool, @mcp.resource, @mcp.prompt)
- Module-level globals require singleton validation
- Progressive disclosure via URI resources
- Windows PYTHONPATH: C:\\Development\\... (double backslashes)

**Token Efficiency (PM-010):**
- Without progressive disclosure: 22,842 tokens
- With progressive disclosure: 422 tokens
- **Savings: 98.2%** (validated in production)

### Roadmap Status

**COMPLETED:**
- ✅ Layer 5: MCP Integration (2025-11-17)
- ✅ MCP Smoke Test (2025-11-17)

**IN PROGRESS:**
- 🔄 Priority 1: Process Memory Provisioning System
  - Directive: msg-20251117-233000-priority1-process-memory-provisioning.json
  - Status: In instance's inbox, not yet started
  - Estimated: 3-4 hours

**PLANNED:**
- 📋 Priority 1.5: Skills Export (NEW - from SKILLS-MCP-INTEGRATION-STRATEGY.md)
- 📋 Priority 2: Project Bootstrap Package
- 📋 Priority 3: Enhanced Template Discovery

---

## Skills + MCP Dual-Pattern Architecture

### The Strategic Insight

Reading Anthropic's engineering articles revealed that thinking-tools-framework should support **TWO complementary patterns**:

1. **MCP Server Pattern** (COMPLETE): Network-accessible, multi-client, programmatic
2. **Skills Pattern** (FUTURE): Filesystem-based, Claude Code native, zero-latency

**Both achieve ~98% token savings through progressive disclosure.**

### Key Concepts from Anthropic Research

**From MCP Code Execution Paper:**
- Progressive disclosure: filesystem navigation → load on demand
- 98.7% token savings (150k → 2k)
- Data filtering in execution environment
- Control flow optimization (loops/conditionals without agent back-and-forth)

**From Claude Skills Documentation:**
- SKILL.md with YAML frontmatter
- Three-level loading: metadata (always) → instructions (triggered) → resources (on-demand)
- Bash execution, output only (code never enters context)
- ~100 tokens/skill metadata, ~5k when triggered

**Our Implementation:**
- MCP: ✅ DONE (progressive disclosure working, 98% savings confirmed)
- Skills: 📋 PROPOSED (Priority 1.5, export tools as Skills)

### Architecture Comparison

| Aspect | MCP Server | Skills |
|--------|-----------|--------|
| Discovery | Network RPC | Filesystem metadata |
| Token Cost | ~422 tokens | ~100 tokens (metadata) |
| Execution | Network call | Bash subprocess |
| Multi-Client | ✅ Yes | ❌ Claude Code only |
| Native Integration | ⚠️ Via protocol | ✅ First-class |

### Why Both Patterns Matter

**MCP Benefits:**
- External clients (API, other tools)
- Multi-agent coordination
- Network-accessible service
- Already production-validated ✅

**Skills Benefits:**
- Claude Code native (no MCP dependency)
- Filesystem speed (zero network latency)
- Always available (no server needed)
- Self-service tool creation

**Strategic Decision:** Implement both, generate Skills from existing YAML specs (single source of truth).

**See:** `.coordination/SKILLS-MCP-INTEGRATION-STRATEGY.md` for complete details.

---

## Process Memory References

### Essential Entries for Coordination

**PM-001: Project Vision**
- Core concept: AI-augmented metacognition tools
- Parameterized YAML templates with Jinja2
- Clean architecture (5 layers)

**PM-002: Security via Sandboxed Templates**
- Jinja2 SandboxedEnvironment
- No filesystem access from templates
- Whitelist-only allowed functions

**PM-004: Tool Discovery and Registration**
- ToolRegistry auto-discovery
- YAML specs as single source of truth
- Category-based organization

**PM-006: Process Memory as Knowledge Graph**
- JSONL append-only log
- JSON Schema validation
- Related entries linking

**PM-010: Token Efficiency Through Progressive Disclosure**
- MCP resources enable on-demand loading
- 98% token savings validated
- Metadata → specification → execution pattern

**PM-017: FastMCP Refactoring Lessons**
- Decorator-based API reduces boilerplate
- Module-level globals (singleton pattern)
- Resource URIs for progressive disclosure
- Windows path handling

**PM-021: Module Duplication Prevention**
- Missing __init__.py causes namespace package issues
- "Source file found twice" mypy warning
- Singleton MCP instance requirement
- Global state must exist only once

### Querying Process Memory

```bash
# Get specific entry
jq 'select(.id == "PM-017")' .bootstrap/process_memory.jsonl

# Search by keyword
jq 'select(.summary | contains("token"))' .bootstrap/process_memory.jsonl

# List by category
jq 'select(.type == "architectural_decision")' .bootstrap/process_memory.jsonl

# Find related entries
jq 'select(.related_entries | contains(["PM-010"]))' .bootstrap/process_memory.jsonl
```

### When to Reference in Directives

**ALWAYS include relevant PM references in directives:**
```json
{
  "content": "Implement Skills export...",
  "references": [
    "PM-010",  // Token efficiency pattern
    "PM-017",  // FastMCP lessons
    "PM-021",  // Module duplication prevention
    "SKILLS-MCP-INTEGRATION-STRATEGY.md"
  ]
}
```

**Why:** Enables instance to make autonomous decisions based on established patterns.

---

## Directive Templates

### Standard Directive Structure

```json
{
  "message_id": "msg-YYYYMMDD-HHMMSS-priority-level-short-name",
  "type": "directive",
  "priority": "high|medium|low",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "from": "coordinator",
  "to": "in-project-claude",
  "subject": "Clear, concise task title",
  "content": {
    "task": "High-level description of what to build",
    "strategic_importance": {
      "why_now": "Why this is the right priority",
      "current_state": "Where we are",
      "problem": "What needs solving",
      "impact": "What success looks like"
    },
    "deliverables": {
      "numbered_list": "Specific artifacts expected"
    },
    "implementation_scope": {
      "new_modules": ["list of new files"],
      "updated_modules": ["list of modified files"],
      "templates": ["optional template files"]
    },
    "success_criteria": {
      "functionality": ["list of working features"],
      "quality_gates": {
        "mypy": "passes --strict",
        "ruff": "0 violations",
        "pytest": "≥80% coverage"
      }
    },
    "implementation_guidance": {
      "layer": "Which architectural layer",
      "dependencies": "What to build on",
      "approach": "High-level strategy"
    },
    "testing_strategy": {
      "unit_tests": ["list of unit test areas"],
      "integration_tests": ["list of integration scenarios"]
    },
    "process_memory_references": ["PM-XXX", "PM-YYY"],
    "estimated_effort": "X-Y hours"
  },
  "quality_gates": {
    "mypy": "must pass with --strict",
    "ruff": "0 violations",
    "pytest": "≥80% coverage"
  },
  "read": false
}
```

### Example: Skills Export Directive

```json
{
  "message_id": "msg-20251118-010000-priority15-skills-export",
  "type": "directive",
  "priority": "medium",
  "timestamp": "2025-11-18T01:00:00Z",
  "from": "coordinator",
  "to": "in-project-claude",
  "subject": "Priority 1.5: Skills Export and Integration",
  "content": {
    "congratulations": "Excellent work completing Priority 1 (Process Memory Provisioning)! The export/import/handover tools are working perfectly.",
    "task": "Implement Skills Export for Thinking Tools",
    "strategic_importance": {
      "why_now": "Completes dual-pattern architecture validated by Anthropic research. Enables thinking tools in Claude Code without MCP dependency.",
      "current_state": "MCP pattern complete and production-validated (98% token savings). Skills pattern researched and strategy documented.",
      "problem": "Thinking tools only accessible via MCP protocol. Claude Code users must run MCP server. No native filesystem-based access.",
      "impact": "Claude Code can use thinking tools as native Skills. Zero-latency discovery. Self-service tool creation enabled."
    },
    "deliverables": {
      "1_skills_exporter": {
        "name": "cogito skills export",
        "purpose": "Generate SKILL.md files from YAML tool specifications",
        "cli_command": "cogito skills export TOOL_NAME --output PATH",
        "variants": [
          "cogito skills export think_aloud --output ~/.claude/skills/think-aloud/",
          "cogito skills export-category metacognition --output ~/.claude/skills/",
          "cogito skills export-all --output ~/.claude/skills/"
        ]
      },
      "2_skill_md_generator": {
        "name": "SKILL.md Generator",
        "purpose": "Auto-generate SKILL.md from YAML metadata, parameters, examples",
        "format": "YAML frontmatter (name, description) + Instructions + Examples + Reference"
      },
      "3_execution_wrappers": {
        "name": "Bash Execution Wrappers",
        "purpose": "Wrapper scripts that call cogito CLI",
        "pattern": "#!/bin/bash\\nexec cogito execute TOOL_NAME \"$@\""
      },
      "4_validation_tool": {
        "name": "Skills Validator",
        "purpose": "Verify generated Skills match Claude Skills schema",
        "checks": ["name format", "description length", "SKILL.md structure"]
      }
    },
    "implementation_scope": {
      "new_modules": [
        "src/cogito/provisioning/skills_exporter.py",
        "src/cogito/provisioning/skill_generator.py",
        "templates/SKILL.md.j2"
      ],
      "updated_modules": [
        "src/cogito/ui/cli.py (add skills subcommand group)"
      ],
      "generated_artifacts": [
        "~/.claude/skills/{tool-name}/SKILL.md",
        "~/.claude/skills/{tool-name}/scripts/execute.sh",
        "~/.claude/skills/{tool-name}/tool.yml (symlink)"
      ]
    },
    "success_criteria": {
      "functionality": [
        "All 30+ tools exportable as Skills",
        "SKILL.md validates against Claude Skills schema",
        "Execution via Skills matches MCP execution output",
        "Skills discoverable in Claude Code"
      ],
      "quality_gates": {
        "mypy": "passes --strict",
        "ruff": "0 violations",
        "pytest": "≥85% coverage for provisioning.skills_*"
      },
      "skills_validation": {
        "name_format": "lowercase, hyphens only, max 64 chars",
        "description_length": "max 1024 chars, includes when-to-use",
        "frontmatter_valid": "YAML parses correctly",
        "execution_equivalence": "Skills output == MCP output"
      }
    },
    "implementation_guidance": {
      "layer": "Layer 4.5 (Provisioning package, between Storage and UI)",
      "dependencies": "Uses ToolRegistry (Layer 2) for discovery, generates Skills from YAML specs",
      "single_source_of_truth": "examples/{category}/*.yml remain canonical, Skills are generated artifacts",
      "skill_md_approach": "Parse YAML metadata, build frontmatter, generate instructions from parameters, include examples",
      "symlink_strategy": "Symlink tool.yml to source YAML (no duplication), enables bidirectional sync",
      "bash_wrapper_pattern": "Simple exec wrapper calling cogito CLI, no complex logic"
    },
    "testing_strategy": {
      "unit_tests": [
        "SKILL.md generator from YAML",
        "Name format conversion (display_name → skill-name)",
        "Description truncation (max 1024 chars)",
        "Frontmatter YAML generation",
        "Bash wrapper template"
      ],
      "integration_tests": [
        "Export single tool end-to-end",
        "Export category of tools",
        "Export all tools",
        "Skills schema validation",
        "Execution equivalence (Skills vs MCP output)"
      ]
    },
    "anthropic_patterns": {
      "progressive_disclosure": "Skills metadata (~100 tokens) → SKILL.md (~5k) → execution",
      "code_execution": "Bash wrappers execute, return output only (code never in context)",
      "token_efficiency": "Target ~97% savings (metadata always loaded, instructions on trigger)"
    },
    "process_memory_references": [
      "PM-010 (Token Efficiency)",
      "PM-017 (FastMCP Lessons)",
      "PM-021 (Module Duplication)",
      "SKILLS-MCP-INTEGRATION-STRATEGY.md"
    ],
    "estimated_effort": "2-3 hours",
    "next_after_this": "Priority 2: Project Bootstrap Package"
  },
  "quality_gates": {
    "mypy": "must pass with --strict",
    "ruff": "0 violations",
    "pytest": "≥85% coverage for skills export functionality",
    "skills_validation": "all generated Skills must validate against Claude Skills schema"
  },
  "read": false
}
```

---

## Quality Gate Requirements

### Standard Quality Gates (All Tasks)

**mypy:**
```bash
mypy --strict src/cogito/
# Must pass with 0 errors
```

**ruff:**
```bash
ruff check src/
# Must show 0 violations
```

**black:**
```bash
black src/ --check
# Must pass (no formatting changes needed)
```

**pytest:**
```bash
pytest --cov=cogito --cov-report=term-missing
# Coverage varies by layer:
# - Layer 2-4: ≥90% coverage
# - Layer 1, 5: ≥80% coverage
# - New features: ≥80% coverage
```

### Acceptance Criteria

**When reviewing completion messages:**

1. **All quality gates must pass** - No exceptions
2. **Coverage meets layer targets** - See above
3. **Artifacts listed and verified** - Check files exist
4. **Integration tests passing** - Not just unit tests
5. **Process memory updated** - New PM entries if architectural

**Red Flags (Reject and Send Back):**
- "Most quality gates passing" (ALL must pass)
- "Coverage is 65%" (too low, must be ≥80%)
- "Will fix type errors later" (must be fixed before completion)
- Missing artifacts in completion message
- No integration tests

**Green Flags (Accept and Move Forward):**
- All quality gates explicitly passed with metrics
- Coverage ≥ target for layer
- All artifacts listed and created
- Integration tests covering real use cases
- Process memory updated if relevant

---

## Common Patterns and Workflows

### Pattern 1: Sequential Layer Implementation

**Used for:** Main roadmap progression (Layers 1-5)

**Workflow:**
1. Review previous layer completion message
2. Verify quality gates all passed
3. Check for architectural learnings
4. Create next layer directive with:
   - Reference to completed layer
   - Dependencies on previous layers
   - Process memory references for patterns
5. Archive completion message
6. Wait for next completion

**Example:** Layer 3 → Layer 2 → Layer 1 progression

### Pattern 2: Priority-Based Feature Implementation

**Used for:** Post-foundation features (Priority 1, 2, 3)

**Workflow:**
1. Consult roadmap for next priority
2. Check if any blockers or dependencies
3. Create directive with strategic importance
4. Include estimated effort
5. Reference related process memory
6. Wait for completion, then sequence to next priority

**Example:** MCP Integration → Process Memory Provisioning → Skills Export

### Pattern 3: Critical Issue Response

**Used for:** Module duplication, security issues, architectural problems

**Workflow:**
1. Instance posts blocker or critical concern
2. You recognize pattern from other projects (e.g., graphiti-mcp)
3. Create focused directive with:
   - **High priority**
   - Specific issue description
   - Pattern from other projects
   - Validation steps
4. Wait for fix confirmation
5. Document learning in process memory

**Example:** Module duplication issue (PM-021)

### Pattern 4: Validation Before Major Milestone

**Used for:** Production readiness checks (e.g., MCP smoke test)

**Workflow:**
1. Major feature complete (e.g., Layer 5 MCP)
2. Create validation directive:
   - Real-world usage test
   - Production environment
   - Success criteria clear
3. Instance executes validation
4. Review validation results
5. If passed: proceed to next phase
6. If failed: create fix directive

**Example:** MCP smoke test after Layer 5 completion

---

## Troubleshooting

### Instance Not Responding

**Symptoms:**
- No messages in outbox for extended time
- current-task.json not updating

**Check:**
```bash
# Is instance running?
cat .progress/current-task.json | jq .updated

# Last updated more than 2 hours ago? May be stuck or session ended
```

**Action:**
- Check if session needs restart
- Review last inbox message - was it ambiguous?
- Consider posting clarifying directive

### Quality Gates Failing

**Symptoms:**
- Completion message shows failed quality gates
- Instance reports errors repeatedly

**Check:**
```bash
# What's failing?
cat .coordination/outbox/msg-*.json | jq '.metadata.quality_gates'
```

**Action:**
- If mypy errors: May need type hints guidance
- If ruff violations: Usually auto-fixable
- If test failures: Check if test requirements were clear
- DON'T accept "will fix later" - must pass before completion

### Duplicate Work or Confusion

**Symptoms:**
- Instance asking questions about already-decided topics
- Implementing features not in directive

**Check:**
```bash
# What's in current task?
cat .progress/current-task.json | jq .

# What was the directive?
cat .coordination/inbox/archived/msg-latest.json
```

**Action:**
- Post clarifying response
- Reference relevant process memory entries
- Emphasize autonomous decision-making boundaries

### Pattern Recognition Opportunities

**Symptoms:**
- Instance hits issue similar to other projects
- You recall similar problem from graphiti-mcp, serena, etc.

**Check:**
```bash
# Search serena memories
cd /c/Development/serena
cat .serena/memories/*.md | grep -i "keyword"
```

**Action:**
- Create directive referencing the pattern
- Provide context from other project
- **WARNING:** Explicitly state "beware contamination" if needed
- Enable instance to solve based on pattern

---

## Your Success Criteria

### You're Doing Well When:

✅ Instance asks few to no technical questions (self-solving)
✅ Quality gates consistently passing
✅ Clear progression through roadmap
✅ Process memory growing with learnings
✅ You catch critical issues early (module duplication pattern)
✅ Directives are clear and actionable
✅ Strategic decisions documented in PM

### You Need to Adjust When:

❌ Instance asking many technical questions
❌ Quality gates frequently failing
❌ Rework or backtracking common
❌ Directives too vague or too prescriptive
❌ Missing pattern recognition opportunities
❌ Not archiving messages properly
❌ Writing code directly to project

---

## Appendix: File Locations Quick Reference

```
thinking-tools-framework/
├── .coordination/
│   ├── COORDINATION-PROTOCOL.md (THIS IS YOUR BIBLE)
│   ├── SKILLS-MCP-INTEGRATION-STRATEGY.md (CRITICAL READING)
│   ├── COORDINATOR-INTEGRATION-GUIDE.md (YOU ARE HERE)
│   ├── inbox/ (YOU WRITE HERE)
│   ├── outbox/ (YOU READ HERE)
│   └── archive/ (YOU ARCHIVE HERE after acting on outbox)
├── .progress/
│   ├── current-task.json (CHECK THIS OFTEN)
│   └── completed-tasks.jsonl
├── .bootstrap/
│   └── process_memory.jsonl (REFERENCE IN DIRECTIVES)
├── examples/ (YAML tool specs - single source of truth)
│   ├── metacognition/
│   ├── review/
│   └── handoff/
├── src/cogito/ (Implementation - instance writes here)
└── tests/ (Tests - instance writes here)
```

---

**Remember:** You provide strategic direction. The instance executes autonomously. Trust the process memory. Archive after acting. Never write code directly.

**This is a strategic partnership, not micromanagement.**
