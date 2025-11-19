# Project Bootstrap Package

## Purpose

The **Project Bootstrap Package** provides everything needed to create a new Thinking Tools Framework (Cogito) project instance with:

1. Complete product context via process memory
2. Functional configuration and directory structure
3. Example thinking tools demonstrating capabilities
4. Development tools and documentation
5. AI-readable contracts and schemas

**Goal:** New Claude Code instance can be productive in <5 minutes.

---

## Package Structure

```
thinking-tools-framework/
│
├── .cogito/                          # Framework data directory
│   ├── config.yml                    # Main configuration
│   ├── bootstrap/                    # Bootstrap data
│   │   ├── process_memory.jsonl      # All design decisions
│   │   ├── knowledge_graph.json      # Decision relationships
│   │   ├── session_context.md        # Human-readable summary
│   │   └── handover_checklist.md     # AI session startup guide
│   ├── thinking_tools/               # Thinking tool specs
│   │   ├── metacognition/
│   │   │   ├── fresh_eyes_exercise.yml
│   │   │   ├── think_aloud.yml
│   │   │   └── assumption_check.yml
│   │   ├── review/
│   │   │   ├── code_review_checklist.yml
│   │   │   └── architecture_review.yml
│   │   ├── handoff/
│   │   │   ├── session_handover.yml
│   │   │   └── context_preservation.yml
│   │   └── debugging/
│   │       ├── five_whys.yml
│   │       └── error_analysis.yml
│   └── generated_tools/              # Auto-generated (gitignored)
│
├── docs/                             # Complete documentation
│   ├── plans/
│   │   └── thinking-tools/
│   │       ├── 00-PRODUCT-VISION.md
│   │       ├── 01-CONSTITUTION.md
│   │       ├── 02-ARCHITECTURE.md
│   │       ├── 03-FRAMEWORK-SPECIFICATION.md
│   │       ├── 04-ARCHITECTURE-DECISION-RECORDS.md
│   │       ├── 05-PRODUCT-DESCRIPTION.md
│   │       ├── 06-TECHNICAL-SPECIFICATIONS-INDEX.md
│   │       ├── 07-PROCESS-MEMORY-PROVISIONING.md
│   │       ├── 08-PROJECT-BOOTSTRAP-PACKAGE.md (this file)
│   │       ├── IMPLEMENTATION-ROADMAP.md
│   │       ├── specs/
│   │       │   ├── 00-IMPERATIVES-INTEGRATION.md
│   │       │   ├── 07-SPEC-LOADER.md
│   │       │   ├── 08-VALIDATOR.md
│   │       │   └── ... (remaining specs)
│   │       └── schemas/
│   │           ├── thinking-tool-v1.0.schema.json
│   │           ├── config-v1.0.schema.json
│   │           ├── process-memory-v1.0.schema.json
│   │           └── plugin-manifest-v1.0.schema.json
│   ├── README.md                     # Project overview
│   └── QUICK_START.md                # Getting started guide
│
├── src/                              # Implementation (to be created)
│   └── cogito/
│       ├── __init__.py
│       ├── contracts/
│       │   └── python-protocols.py   # All Protocol interfaces
│       ├── core/                     # Core components
│       ├── cli/                      # CLI implementation
│       ├── storage/                  # Storage backends
│       └── plugins/                  # Plugin system
│
├── tests/                            # Test suite (to be created)
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                          # Automation scripts
│   ├── bootstrap.sh                  # Initial setup
│   ├── validate.sh                   # Validate all specs
│   └── generate_contracts.py        # Generate Python protocols
│
├── .gitignore                        # Git ignore rules
├── pyproject.toml                    # Python project config
├── README.md                         # Main README
└── LICENSE                           # Apache 2.0
```

---

## Bootstrap Process

### Automated Bootstrap Script

```bash
#!/usr/bin/env bash
# scripts/bootstrap.sh - Bootstrap new Thinking Tools Framework project

set -euo pipefail

echo "🚀 Bootstrapping Thinking Tools Framework..."

# Step 1: Create directory structure
echo "📁 Creating directory structure..."
mkdir -p .cogito/{bootstrap,thinking_tools/{metacognition,review,handoff,debugging},generated_tools}
mkdir -p docs/plans/thinking-tools/{specs,schemas}
mkdir -p src/cogito/{contracts,core,cli,storage,plugins}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p scripts

# Step 2: Copy/generate configuration
echo "⚙️  Generating configuration..."
cat > .cogito/config.yml <<'EOF'
# Cogito Framework Configuration v1.0
# Auto-generated by bootstrap process

system:
  version: "1.0.0"
  data_directory: "${PROJECT_ROOT}/.cogito"
  log_level: "INFO"

discovery:
  paths:
    project: "${PROJECT_ROOT}/.cogito/thinking_tools"
    user: "${USER_HOME}/.cogito/thinking_tools"
  watch: true

validation:
  strict_mode: true
  layers:
    syntax: true
    schema: true
    semantic: true
    security: true
    quality: true

performance:
  cache_enabled: true
  cache_ttl_seconds: 3600

process_memory:
  enabled: true
  log_file: "${DATA_DIR}/process_memory/log.jsonl"
EOF

# Step 3: Generate process memory with design decisions
echo "🧠 Generating process memory..."
python3 scripts/generate_process_memory.py

# Step 4: Create example thinking tools
echo "🛠️  Creating example thinking tools..."
cat > .cogito/thinking_tools/metacognition/fresh_eyes_exercise.yml <<'EOF'
version: "1.0"

metadata:
  name: "fresh_eyes_exercise"
  display_name: "Fresh Eyes Exercise"
  description: "Step back and re-evaluate with fresh perspective"
  category: "metacognition"
  author: "Cogito Framework"
  tags: ["metacognition", "perspective", "reflection"]

parameters:
  phase:
    type: "enum"
    description: "Which phase of the exercise to perform"
    required: true
    default: "full"
    validation:
      values: ["full", "current_state", "target_state", "gap_analysis", "validation", "quick"]

template:
  source: |
    # Fresh Eyes Exercise - {{ phase|upper }} Phase

    {% if phase == 'full' or phase == 'current_state' %}
    ## Current State Analysis
    Step back from the immediate work. What is the current state?
    - What patterns do you observe in the code/design/approach?
    - What assumptions have been made (explicit or implicit)?
    - What constraints are you operating under?
    - What's working well? What's not?
    {% endif %}

    {% if phase == 'full' or phase == 'target_state' %}
    ## Target State Vision
    What does the ideal solution look like?
    - What are the core requirements (not implementation details)?
    - What constraints must be respected vs. what's negotiable?
    - What would "done and excellent" look like?
    - What patterns or approaches align with project principles?
    {% endif %}

    {% if phase == 'full' or phase == 'gap_analysis' %}
    ## Gap Analysis
    What's the delta between current and target state?
    - What needs to change?
    - What's the simplest path forward?
    - What risks or blockers exist?
    - What can be deferred vs. must be now?
    {% endif %}

    {% if phase == 'full' or phase == 'validation' %}
    ## Validation
    Reality check the plan:
    - Does this align with Five Cornerstones?
    - Does this support AI-First principles?
    - Are there simpler approaches being overlooked?
    - What would future-you wish current-you had considered?
    {% endif %}

    {% if phase == 'quick' %}
    ## Quick Fresh Eyes
    Take 60 seconds to:
    1. State the problem in one sentence
    2. List 3 assumptions you're making
    3. Consider: "Is there a simpler way?"
    {% endif %}

execution:
  timeout_ms: 5000
  optional: true
  requires_project: false

process_memory:
  capture_execution: true
  memory_type: "Observation"

testing:
  test_cases:
    - name: "Full exercise"
      parameters: {phase: "full"}
      expected_contains: ["Current State", "Target State", "Gap Analysis", "Validation"]

    - name: "Current state only"
      parameters: {phase: "current_state"}
      expected_contains: ["Current State"]
      expected_not_contains: ["Target State"]

quality:
  examples:
    - description: "Use when starting a new feature"
      usage: "Let's do a fresh eyes exercise before implementing feature X"

    - description: "Use when debugging seems stuck"
      usage: "I'm stuck on this bug, let's do a quick fresh eyes check"

  complexity_score: 0.3  # Low complexity
  estimated_duration_seconds: 120  # 2 minutes
EOF

# Step 5: Generate README
echo "📝 Generating README..."
cat > README.md <<'EOF'
# Thinking Tools Framework (Cogito)

**Declarative metacognition for AI agents**

## What Is This?

The Thinking Tools Framework enables you to create structured reflection exercises ("thinking tools") for AI coding agents using simple YAML files—no programming required.

## Quick Start

```bash
# 1. Activate this project in Claude Code
cd thinking-tools-framework

# 2. Explore example tools
ls .cogito/thinking_tools/metacognition/

# 3. Try a thinking tool
"Let's do a fresh eyes exercise"

# 4. Create your own tool
# Edit: .cogito/thinking_tools/my_tool.yml
# (See examples for template)

# 5. Tools are auto-discovered and available immediately
```

## Documentation

- **Product Vision**: `docs/plans/thinking-tools/00-PRODUCT-VISION.md`
- **Architecture**: `docs/plans/thinking-tools/02-ARCHITECTURE.md`
- **Quick Start**: `docs/QUICK_START.md`
- **Specifications Index**: `docs/plans/thinking-tools/06-TECHNICAL-SPECIFICATIONS-INDEX.md`

## For AI Agents

If you're an AI agent starting fresh:

1. Read: `.cogito/bootstrap/handover_checklist.md`
2. Load: `.cogito/bootstrap/process_memory.jsonl` (context)
3. Query: Process memory for decisions and rationale
4. Proceed: Following roadmap in `docs/plans/thinking-tools/IMPLEMENTATION-ROADMAP.md`

## License

Apache 2.0 - See LICENSE file
EOF

echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Review: README.md"
echo "  2. Read: docs/QUICK_START.md"
echo "  3. Explore: .cogito/thinking_tools/"
echo "  4. Start: Create your first thinking tool!"
```

### Process Memory Generator Script

```python
#!/usr/bin/env python3
# scripts/generate_process_memory.py

"""
Generate process memory entries from product design phase.
"""

import json
from datetime import datetime
from pathlib import Path

# Memory entries from design phase (captured in 07-PROCESS-MEMORY-PROVISIONING.md)
MEMORIES = [
    {
        "id": "pm-001",
        "type": "StrategicDecision",
        "title": "YAML Specification Format",
        "summary": "Selected YAML over JSON, TOML, Python DSL for thinking tool specs",
        "rationale": "Human readability and accessibility for non-programmers. YAML provides comments, multi-line strings, familiar pattern.",
        "source_adr": "ADR-001",
        "related_concepts": ["accessibility", "declarative-design", "spec-format"],
        "timestamp_created": "2025-01-15T10:00:00Z",
        "confidence_level": 0.9,
        "phase": "product",
        "deprecated": False,
        "provenance": {
            "author": "AI Product Owner",
            "document": "04-ARCHITECTURE-DECISION-RECORDS.md"
        },
        "links": ["pm-002", "pm-003", "pm-004"],
        "tags": ["spec-format", "yaml", "design-decision"]
    },
    # ... (all 40+ entries from 07-PROCESS-MEMORY-PROVISIONING.md)
]

def generate_process_memory():
    """Generate process memory log file."""

    output_dir = Path(".cogito/bootstrap")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "process_memory.jsonl"

    with output_file.open("w") as f:
        for memory in MEMORIES:
            f.write(json.dumps(memory) + "\n")

    print(f"✅ Generated {len(MEMORIES)} process memory entries")
    print(f"   Location: {output_file}")

def generate_knowledge_graph():
    """Generate knowledge graph from memory links."""

    nodes = [{"id": m["id"], "title": m["title"], "type": m["type"]} for m in MEMORIES]
    edges = []

    for memory in MEMORIES:
        source = memory["id"]
        for target in memory.get("links", []):
            edges.append({"source": source, "target": target})

    graph = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    }

    output_file = Path(".cogito/bootstrap/knowledge_graph.json")
    output_file.write_text(json.dumps(graph, indent=2))

    print(f"✅ Generated knowledge graph")
    print(f"   Nodes: {len(nodes)}, Edges: {len(edges)}")

def generate_session_context():
    """Generate human-readable session context."""

    decisions = [m for m in MEMORIES if m["type"] == "StrategicDecision"]
    lessons = [m for m in MEMORIES if m["type"] == "LessonLearned"]
    assumptions = [m for m in MEMORIES if m["type"] == "AssumptionMade"]

    context = f"""# Thinking Tools Framework - Session Context

**Generated**: {datetime.utcnow().isoformat()}

## Project Overview

The Thinking Tools Framework (Cogito) enables creation of structured reflection exercises for AI agents via declarative YAML specifications.

**Status**: Product design complete, entering implementation phase
**Phase**: Development
**Next Priority**: Complete remaining technical specifications

## Strategic Decisions ({len(decisions)})

"""

    for decision in decisions[:10]:  # Top 10
        context += f"""
### {decision['title']}
- **Summary**: {decision['summary']}
- **Rationale**: {decision['rationale']}
- **Confidence**: {decision['confidence_level']:.0%}
- **Source**: {decision.get('source_adr', 'N/A')}
"""

    context += f"""

## Lessons Learned ({len(lessons)})

"""

    for lesson in lessons:
        context += f"""
### {lesson['title']}
{lesson['summary']}
"""

    context += f"""

## Key Assumptions ({len(assumptions)})

"""

    for assumption in assumptions:
        context += f"""
### {assumption['title']}
- **Summary**: {assumption['summary']}
- **Confidence**: {assumption['confidence_level']:.0%}
"""

    context += """

## Recommended Reading Order

1. `IMPLEMENTATION-ROADMAP.md` - Current status and priorities
2. `specs/00-IMPERATIVES-INTEGRATION.md` - Five Cornerstones + AI-First
3. `02-ARCHITECTURE.md` - System architecture overview
4. Specific specs based on work area (see Technical Specifications Index)

## Process Memory Query Examples

```bash
# Get all strategic decisions
cogito memory query --type=StrategicDecision

# Get security-related decisions
cogito memory query --tags=security

# Get recent lessons
cogito memory list --type=LessonLearned --limit=5
```
"""

    output_file = Path(".cogito/bootstrap/session_context.md")
    output_file.write_text(context)

    print(f"✅ Generated session context summary")

if __name__ == "__main__":
    generate_process_memory()
    generate_knowledge_graph()
    generate_session_context()
    print("\n🎉 Process memory provisioning complete!")
```

---

## AI Session Handover Checklist

```markdown
# AI Session Handover Checklist

**Purpose**: Ensure new AI sessions can reconstruct full project context

## Prerequisites

- [ ] Claude Code instance active in project directory
- [ ] Git repository initialized
- [ ] Bootstrap process completed

## Phase 1: Foundation Loading (5 minutes)

### Step 1.1: Read Core Documents
- [ ] `README.md` - Project overview
- [ ] `IMPLEMENTATION-ROADMAP.md` - Current status, priorities
- [ ] `docs/plans/thinking-tools/00-PRODUCT-VISION.md` - Product context

### Step 1.2: Load Process Memory
```bash
# Read session context summary
cat .cogito/bootstrap/session_context.md

# Load strategic decisions
# (Process memory query commands here once system implemented)
```

### Step 1.3: Understand Imperatives
- [ ] `specs/00-IMPERATIVES-INTEGRATION.md` - Five Cornerstones + AI-First
- Validate understanding of:
  - Configurability (all behavior driven by config)
  - Modularity (Protocol interfaces, dependency injection)
  - Extensibility (plugin architecture)
  - Integration (standard protocols, graceful degradation)
  - Automation (auto-discovery, self-healing)

## Phase 2: Architecture Understanding (10 minutes)

### Step 2.1: System Architecture
- [ ] `02-ARCHITECTURE.md` - Five-layer architecture
- [ ] `06-TECHNICAL-SPECIFICATIONS-INDEX.md` - Spec navigation

### Step 2.2: Key Decisions
- [ ] `04-ARCHITECTURE-DECISION-RECORDS.md` - All 10 ADRs
- Focus on:
  - ADR-001: YAML format (accessibility)
  - ADR-002: Sandboxed Jinja2 (security)
  - ADR-009: Zero Serena mods (integration)
  - ADR-010: Declarative-first (design philosophy)

## Phase 3: Work Area Preparation (5-10 minutes)

### Step 3.1: Determine Current Work
```bash
# Check implementation roadmap
grep "⏳" IMPLEMENTATION-ROADMAP.md  # In progress items
grep "Priority" IMPLEMENTATION-ROADMAP.md  # Next priorities
```

### Step 3.2: Load Relevant Specs
Based on work area, read:
- Component spec (e.g., `specs/04-THINKING-TOOLS-MANAGER.md`)
- Dependencies (listed in spec)
- Related ADRs (cross-referenced)

### Step 3.3: Query Related Memories
```bash
# Query process memory for work area
# (Commands here once system implemented)
# Example: cogito memory query --tags=validation
```

## Phase 4: Environment Setup (5 minutes)

### Step 4.1: Verify Configuration
```bash
# Check config file
cat .cogito/config.yml

# Verify paths exist
ls -la .cogito/thinking_tools/
```

### Step 4.2: Test Examples
```bash
# List example tools
ls .cogito/thinking_tools/metacognition/

# Validate an example
# (Once implemented: cogito validate .cogito/thinking_tools/metacognition/fresh_eyes_exercise.yml)
```

## Phase 5: Ready to Work

### Validation Checklist
- [ ] Understand Five Cornerstones and how they apply
- [ ] Know current phase and priorities
- [ ] Loaded relevant component specs
- [ ] Queried process memory for context
- [ ] Environment validated

### Next Actions
- [ ] Identify specific task from roadmap
- [ ] Create todo list for task
- [ ] Begin implementation following specs
- [ ] Capture new decisions in process memory

## Continuous Integration

### During Work
- Document all decisions immediately
- Update roadmap as tasks complete
- Capture lessons learned
- Link new memories to existing graph

### Before Session End
- Update IMPLEMENTATION-ROADMAP.md
- Capture session summary in process memory
- Note any blockers or open questions
- Prepare handover for next session

---

**Session handover target**: <20 minutes from fresh start to productive work
```

---

## Example Thinking Tools

### Included Examples (8 tools)

**Metacognition (3):**
1. `fresh_eyes_exercise.yml` - Perspective shift and re-evaluation
2. `think_aloud.yml` - Explicit reasoning verbalization
3. `assumption_check.yml` - Surface implicit assumptions

**Review (2):**
1. `code_review_checklist.yml` - Structured code review
2. `architecture_review.yml` - System design evaluation

**Handoff (2):**
1. `session_handover.yml` - AI session transition
2. `context_preservation.yml` - Capture work context

**Debugging (1):**
1. `five_whys.yml` - Root cause analysis

---

## Quick Start Guide

```markdown
# Quick Start Guide

## 5-Minute Setup

### 1. Bootstrap Project
```bash
cd thinking-tools-framework
./scripts/bootstrap.sh
```

### 2. Verify Setup
```bash
# Check config
cat .cogito/config.yml

# List example tools
ls .cogito/thinking_tools/metacognition/
```

### 3. Try Example Tool

In Claude Code:
```
"Let's do a fresh eyes exercise on this architecture"
```

### 4. Create Your Own Tool

```bash
# Copy template
cp .cogito/thinking_tools/metacognition/fresh_eyes_exercise.yml \
   .cogito/thinking_tools/my_tool.yml

# Edit with your content
vim .cogito/thinking_tools/my_tool.yml
```

### 5. Tool Available Immediately

- No restart needed (hot-reload enabled)
- Automatically validated
- Instantly available in Claude Code

## Next Steps

1. **Read Product Vision**: Understand what we're building
2. **Review Architecture**: Understand how it works
3. **Explore Specs**: Deep-dive into components
4. **Implement**: Start building!

## For AI Agents

See: `.cogito/bootstrap/handover_checklist.md`
```

---

## Document Status

**Version:** 1.0.0
**Status:** Complete - Ready for Project Creation
**Dependencies:** Process Memory Provisioning (07)
**Next Step:** Create actual bootstrap package in separate directory

---

**"The bootstrap package ensures every new instance starts with full context."**
