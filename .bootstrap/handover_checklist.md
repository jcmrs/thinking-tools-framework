# AI Session Startup Checklist

**Purpose:** Enable new Claude Code instance to establish full project context in <20 minutes.

---

## Phase 1: Initial Orientation (5 minutes)

- [ ] Read `IMPLEMENTATION-ROADMAP.md` (current status, what's done, what's next)
- [ ] Read `06-TECHNICAL-SPECIFICATIONS-INDEX.md` (navigation map)
- [ ] Read `.cogito/bootstrap/session_context.md` (this provides condensed context)
- [ ] Scan process memory count: `wc -l .cogito/bootstrap/process_memory.jsonl`

**Checkpoint:** Can you summarize project phase and current priorities?

---

## Phase 2: Understand Architecture (5 minutes)

- [ ] Read `02-ARCHITECTURE.md` (five-layer architecture overview)
- [ ] Read `specs/00-IMPERATIVES-INTEGRATION.md` (Five Cornerstones + AI-First)
- [ ] Review knowledge graph: `cat .cogito/bootstrap/knowledge_graph.json`
- [ ] Identify architecture hotspots (most-connected decisions)

**Checkpoint:** Can you explain the five layers and Five Cornerstones?

---

## Phase 3: Understand Key Decisions (5 minutes)

- [ ] Read `04-ARCHITECTURE-DECISION-RECORDS.md` (all 10 ADRs)
- [ ] Focus on high-confidence decisions (pm-001 through pm-010)
- [ ] Note alternatives that were considered and why rejected
- [ ] Understand trade-offs accepted

**Checkpoint:** Can you explain why YAML + Jinja2 + JSONL were chosen?

---

## Phase 4: Understand Current Work (5 minutes)

- [ ] Read most recent checkpoint document (e.g., `PHASE1-EXAMPLES-COMPLETE.md`)
- [ ] Review recent git commits: `git log --oneline -10`
- [ ] Check current branch: `git branch --show-current`
- [ ] Review in-progress work from checkpoint

**Checkpoint:** What was just completed? What's next?

---

## Phase 5: Establish Mental Models (Optional, 5 minutes)

- [ ] Review mental model entries (pm-027, pm-028, pm-029)
- [ ] Understand five-layer architecture model
- [ ] Understand protocol-based dependency injection model
- [ ] Understand thinking tool lifecycle

**Checkpoint:** Can you trace a thinking tool through its lifecycle?

---

## Verification

Before proceeding with work, verify understanding:

1. **Summarize project:** What is this framework? What's its purpose?
2. **Summarize current phase:** Where are we in development?
3. **Summarize next steps:** What should be worked on next?
4. **Identify key constraints:** What architectural principles must be preserved?

If you can answer these four questions, you're ready to contribute effectively.

---

## Quick Reference

**Essential Commands:**
```bash
# Project status
cat IMPLEMENTATION-ROADMAP.md

# Session context
cat .cogito/bootstrap/session_context.md

# Process memory
cat .cogito/bootstrap/process_memory.jsonl | wc -l

# Recent work
git log --oneline -10
```

**Essential Concepts:**
- Five Cornerstones: Configurability, Modularity, Extensibility, Integration, Automation
- AI-First: Machine-readable, Self-documenting, Context preservation, No hidden state
- Five Layers: UI, Orchestration, Processing, Storage, Integration

**Decision Confidence Levels:**
- 0.95+: Very high confidence, core decisions
- 0.85-0.94: High confidence, solid decisions
- 0.75-0.84: Medium confidence, may revisit
- <0.75: Lower confidence, validate assumptions

---

## Total Time Investment

- **Minimum viable context:** 10 minutes (Phases 1-2)
- **Good working context:** 15 minutes (Phases 1-3)
- **Full context:** 20-25 minutes (All phases)

Choose depth based on task complexity and available time.
