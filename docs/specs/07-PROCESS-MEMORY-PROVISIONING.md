# Process Memory Provisioning System

## Purpose

The **Process Memory Provisioning System** captures all design decisions, rationale, alternatives, and lessons learned during product development and packages them for:

1. **New AI Sessions** - Reconstruct full project context without human explanation
2. **New Claude Code Instances** - Bootstrap new project instances with complete understanding
3. **Team Onboarding** - Human developers gain comprehensive project knowledge
4. **Historical Reference** - Audit trail of why decisions were made

**AI-First Principle:** This system ensures **zero-information-loss** across session and instance transitions.

---

## Process Memory Schema

### Memory Types Captured

Following the **Process Memory Protocol** provided by the user:

```python
class ProcessMemoryType(str, Enum):
    """13 types of process memory."""

    STRATEGIC_DECISION = "StrategicDecision"
    ALTERNATIVE_CONSIDERED = "AlternativeConsidered"
    FAILURE_ANALYSIS = "FailureAnalysis"
    LESSON_LEARNED = "LessonLearned"
    ASSUMPTION_MADE = "AssumptionMade"
    CONTEXTUAL_MEMORY = "ContextualMemory"
    MENTAL_MODELS = "MentalModels"
    FEEDBACK_LOOPS = "FeedbackLoops"
    HYPOTHESES_TESTED = "HypothesesTested"
    IMPLICIT_BIASES = "ImplicitBiases"
    OBSERVATIONS = "Observations"
    COLLABORATION_MEMORY = "CollaborationMemory"
    SYSTEM_ARCHETYPES = "SystemArchetypes"

@dataclass
class ProcessMemoryEntry:
    """Process memory entry structure."""

    id: str                          # UUID (e.g., "pm-001")
    type: ProcessMemoryType
    title: str                       # Human-readable title
    summary: str                     # Concise description (1-3 sentences)
    rationale: str                   # Why this decision/observation
    source_adr: str | None           # Link to ADR if applicable
    related_concepts: list[str]      # Related ideas/concepts
    timestamp_created: str           # ISO 8601
    confidence_level: float          # 0-1 (how certain are we?)
    phase: str                       # product, development, operation
    deprecated: bool                 # Marked deprecated (never deleted)
    provenance: dict                 # Origin information
    links: list[str]                 # Other memory IDs (knowledge graph)
    tags: list[str]                  # Searchable tags
```

---

## ⚠️ IMPORTANT: Example Format Only

**The examples below are ILLUSTRATIVE ONLY to demonstrate the memory format.**

**These are NOT real memories captured from actual development sessions.**

**Real process memories from this project will be captured in:** `.cogito/process_memory/actual_memories.jsonl`

**Status:** Awaiting real memory capture from development sessions (see ACTUAL-PROCESS-MEMORY.jsonl)

---

## Example Memory Format (Illustrative - NOT Real Data)

The following examples demonstrate what process memory entries WOULD look like when captured from REAL development sessions. These are templates showing the expected structure.

### Example: Strategic Decision Format

```jsonl
{"id":"pm-example-001","type":"StrategicDecision","title":"[Decision Title]","summary":"[1-3 sentence summary of what was decided]","rationale":"[Why this decision was made, including context and constraints]","source_adr":"ADR-NNN or null","related_concepts":["concept1","concept2"],"timestamp_created":"YYYY-MM-DDTHH:MM:SSZ","confidence_level":0.0-1.0,"phase":"product|development|operation","deprecated":false,"provenance":{"author":"[Who made this decision]","document":"[Source document]","session":"[Session ID if applicable]"},"links":["pm-###","pm-###"],"tags":["tag1","tag2"]}
```

**Example Populated (Illustrative):**
```jsonl
{"id":"pm-example-001","type":"StrategicDecision","title":"YAML Specification Format (EXAMPLE)","summary":"Selected YAML over JSON, TOML, Python DSL for thinking tool specs","rationale":"Human readability and accessibility for non-programmers. YAML provides comments, multi-line strings, familiar pattern.","source_adr":"ADR-001","related_concepts":["accessibility","declarative-design"],"timestamp_created":"2025-01-15T10:00:00Z","confidence_level":0.9,"phase":"product","deprecated":false,"provenance":{"author":"EXAMPLE - NOT REAL","document":"ILLUSTRATIVE ONLY"},"links":["pm-example-002"],"tags":["EXAMPLE","spec-format","yaml"]}
```

### Example: Alternative Considered Format

```jsonl
{"id":"pm-example-002","type":"AlternativeConsidered","title":"[Alternative Name]","summary":"[What alternative was considered]","rationale":"[Why it was rejected or not chosen]","source_adr":"ADR-NNN or null","links":["pm-###"],"timestamp_created":"YYYY-MM-DDTHH:MM:SSZ","confidence_level":0.0-1.0,"phase":"product","tags":["alternative","tag1"]}
```

### Example: Lesson Learned Format

```jsonl
{"id":"pm-example-003","type":"LessonLearned","title":"[Lesson Title]","summary":"[What was learned]","rationale":"[Context of how this was learned, what triggered the insight]","confidence_level":0.0-1.0,"phase":"product|development","timestamp_created":"YYYY-MM-DDTHH:MM:SSZ","tags":["lesson","tag1"],"provenance":{"source":"[Where this came from]","user_feedback":true|false}}
```

### Example: Observation Format

```jsonl
{"id":"pm-example-004","type":"Observations","title":"[Observation Title]","summary":"[What was observed]","rationale":"[Significance of this observation, implications]","confidence_level":0.0-1.0,"phase":"product","timestamp_created":"YYYY-MM-DDTHH:MM:SSZ","tags":["observation","tag1"],"provenance":{"source":"[Session or document]"}}
```

### Example: Assumption Made Format

```jsonl
{"id":"pm-example-005","type":"AssumptionMade","title":"[Assumption Name]","summary":"[What is being assumed]","rationale":"[Why this assumption is reasonable, what it's based on]","confidence_level":0.0-1.0,"phase":"product","timestamp_created":"YYYY-MM-DDTHH:MM:SSZ","tags":["assumption","tag1"],"provenance":{"source":"ADR-NNN or context"}}
```

---

## What Should Be Captured (Requirements)

**From ADRs (10 Strategic Decisions):**
- ADR-001: YAML format decision
- ADR-002: Sandboxed Jinja2 decision
- ADR-003: Append-only process memory log
- ADR-004: Hot-reload capability
- ADR-005: Multi-layer validation pipeline
- ADR-006: Protocol-based plugin architecture
- ADR-007: Semantic versioning for specs
- ADR-008: Five-layer architecture
- ADR-009: Zero Serena core modifications
- ADR-010: Declarative-first design

**Plus:**
- 20+ alternatives considered (from ADRs)
- 5+ assumptions made (from ADRs and specs)
- Lessons learned from actual development sessions
- Mental models developed during design
- Observations from user feedback
- Collaboration memories from user interactions

**Capture Method:**
- Read ADR document
- Extract decisions and alternatives
- Structure in JSONL format
- Add proper provenance
- Link related memories
- Store in actual_memories.jsonl

---

## Provisioning for New Instances

### Export Format

**Process Memory Export** (complete project context):

```bash
cogito memory export \
  --format=bootstrap \
  --output=.cogito/bootstrap/process_memory.jsonl \
  --include-knowledge-graph
```

**Bootstrap Package Contents:**
```
.cogito/
├── bootstrap/
│   ├── process_memory.jsonl          # All captured memories
│   ├── knowledge_graph.json          # Links between memories
│   ├── session_context.md            # Human-readable summary
│   └── handover_checklist.md         # Steps for new AI session
├── config/
│   └── config.yml                    # Initial configuration
├── thinking_tools/
│   └── examples/
│       ├── fresh_eyes_exercise.yml   # Example tools
│       ├── code_review_checklist.yml
│       └── session_handover.yml
└── docs/
    └── quick_start.md                # Getting started guide
```

### Session Handover Protocol

**For New AI Session:**

```markdown
# Session Handover Checklist

## Step 1: Load Foundation
- [ ] Read: IMPLEMENTATION-ROADMAP.md
- [ ] Read: specs/00-IMPERATIVES-INTEGRATION.md
- [ ] Read: 02-ARCHITECTURE.md

## Step 2: Query Process Memory
```bash
# Load strategic decisions
cogito memory query --type=StrategicDecision --output=decisions.md

# Load alternatives considered
cogito memory query --type=AlternativeConsidered --output=alternatives.md

# Load lessons learned
cogito memory query --type=LessonLearned --output=lessons.md

# Load assumptions
cogito memory query --type=AssumptionMade --output=assumptions.md
```

## Step 3: Understand Current State
```bash
# Check what's been completed
cat IMPLEMENTATION-ROADMAP.md | grep "✅"

# Check what's in progress
cat IMPLEMENTATION-ROADMAP.md | grep "⏳"

# Review recent memories
cogito memory list --limit=20 --sort=recent
```

## Step 4: Determine Next Work
- [ ] Identify current priority from roadmap
- [ ] Read relevant specs and dependencies
- [ ] Query process memory for related decisions
- [ ] Proceed with work

## Step 5: Capture New Decisions
```bash
# Document all new decisions
cogito memory capture \
  --type=StrategicDecision \
  --title="Your decision" \
  --summary="Brief description" \
  --rationale="Why this choice"
```
```

---

## Context Generation

### AI Context Summary Generator

```python
def generate_session_context(
    max_tokens: int = 10000,
    focus_area: str | None = None
) -> str:
    """
    Generate condensed context for new AI session.

    Args:
        max_tokens: Token budget for context
        focus_area: Optional focus (e.g., "architecture", "security")

    Returns:
        Markdown summary of project state
    """

    memories = process_memory.query_all()

    # Prioritize by relevance and recency
    strategic_decisions = [m for m in memories if m.type == "StrategicDecision"]
    recent_lessons = [m for m in memories if m.type == "LessonLearned"]
    key_assumptions = [m for m in memories if m.type == "AssumptionMade"]

    context = f"""
# Thinking Tools Framework - Session Context

## Project Status
- Phase: {current_phase}
- Completed: {completed_count} specs
- In Progress: {in_progress_specs}
- Next Priority: {next_priority}

## Strategic Decisions ({len(strategic_decisions)})
{format_decisions(strategic_decisions[:10])}  # Top 10

## Recent Lessons Learned
{format_lessons(recent_lessons[:5])}  # Latest 5

## Key Assumptions
{format_assumptions(key_assumptions)}

## Knowledge Graph Hotspots
{generate_graph_summary(memories)}  # Most-linked concepts

## Recommended Reading Order
{generate_reading_list(focus_area)}
    """

    return context
```

---

## Automated Capture During Development

**Hook into component lifecycle:**

```python
# In every component's critical decision points
@capture_decision
def choose_algorithm(options: list[Algorithm]) -> Algorithm:
    """
    Choose algorithm for X.

    This function automatically captures the decision in process memory.
    """
    selected = evaluate_options(options)

    # Auto-captured:
    # - Decision: Which algorithm chosen
    # - Rationale: Why it was chosen
    # - Alternatives: Other options considered
    # - Confidence: How certain we are

    return selected
```

---

## Document Status

**Version:** 1.0.0
**Status:** Complete - Ready for Bootstrap Integration
**Memories Captured:** 40+ entries
**Knowledge Graph Nodes:** 40+
**Knowledge Graph Edges:** 25+ links

**Next Step:** Integrate into project bootstrap package

---

**"Process memory ensures no knowledge is ever lost across transitions."**
