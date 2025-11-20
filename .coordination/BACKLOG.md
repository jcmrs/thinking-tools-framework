# Thinking Tools Framework - Project Backlog

**Last Updated**: 2025-11-20
**Maintained By**: Coordinator

---

## Active Priorities (In Progress)

### Priority 8: User Documentation 📝
**Status**: Deferred (Low priority)
**Estimated Effort**: 3-4 hours
**Context**: User-facing documentation for framework usage

**Deliverables**:
1. USER-GUIDE.md - End-user guide for thinking tools
2. TOOL-CREATION-GUIDE.md - How to create custom tools
3. INTEGRATION-GUIDE.md - How to integrate with projects

**Dependencies**: Core functionality complete (Priority 7)

**Why Deferred**: Framework itself must be stable first

---

## Technical Debt & Gaps

### CRITICAL GAP: Technical Specifications Not Generated 🚨
**Identified**: 2025-11-19 (User observation)
**Updated**: 2025-11-20 (Severity escalated)
**Severity**: HIGH - Violates Imperatives 1 (Holistic Thinking) & 4 (Quality Without Compromise)
**Impact**: CRITICAL - Blocks decision tracing, architecture validation, and holistic system understanding

**Problem**:
- `docs/specs/06-TECHNICAL-SPECIFICATIONS-INDEX.md` claims "27 of 27 specs complete (100%)"
- Individual spec files **DO NOT EXIST**:
  - `specs/01-CLI-SPECIFICATION.md` through `specs/26-BACKUP-RECOVERY.md`
  - `schemas/` subdirectory (JSON schemas)
  - No plan files for spec generation found
- Only foundation docs exist (00-PRODUCT-VISION.md through 08-PROJECT-BOOTSTRAP-PACKAGE.md)

**What Exists**:
- ✅ Core architecture documented: `docs/specs/02-ARCHITECTURE.md`
- ✅ Contracts implemented: `src/cogito/contracts/layer_protocols.py` (Priority 5)
- ✅ Code tested: 486+ passing tests
- ✅ Foundation documents complete

**What's Missing**:
- ❌ 27 detailed modular spec files (0/27 exist, despite INDEX claiming 100%)
- ❌ `docs/specs/specs/` directory does not exist
- ❌ 1 JSON schema (plugin-manifest-v1.0.schema.json)
- ❌ Granular ADRs for component-level decisions
- ❌ Plan files documenting priority execution strategies
- ❌ Cross-reference validation between specs and implementation

**Why This Is Critical** (User insight, 2025-11-20):
> "Completeness as a requirement dictates that we need the adr/plan/spec files, and we need them in such a way that we can work with them. Holistic system thinking dictates the same, missing a decision point can easily introduce uncertainties, influence decisions, cause assumptions."

**Imperative Violations**:
- **Imperative 1 (Holistic Thinking)**: Cannot trace decision rationale → introduces uncertainties and assumptions
- **Imperative 4 (Quality Without Compromise)**: INDEX claims "27 of 27 ✅ (100%)" but reality is 0/27 (0%) for modular specs

**Practical Consequences**:
- Cannot trace why specific implementation choices were made
- Cannot validate if current code matches intended design
- Cannot reference component specs for new development
- Cannot onboard fresh AI sessions with component-level context
- Cannot understand dependencies between components precisely

**Recommendation**:
Add as **Priority 9** IMMEDIATELY after Priority 7. Core functionality is complete and stable, making this the RIGHT TIME to document the working system.

**Proposed Deliverables**:
1. **Reverse-engineer 27 modular specs** from implementation (one per claimed spec)
2. **Create `docs/specs/specs/` directory** with proper structure
3. **Generate plugin-manifest-v1.0.schema.json**
4. **Extract granular ADRs** from process memory and git history
5. **Document priority planning** (plan files for Priorities 1-7)
6. **Validate cross-references** between specs, implementation, and tests
7. **Update INDEX** to reflect actual reality (not aspirational)

**Estimated Effort**: 8-12 hours (comprehensive reverse-engineering from working code)

**Process Memory References**:
- `technical-documentation-gap-2025-11-19` (original identification)
- `critical-gap-documentation-system-incomplete` (detailed analysis, imperative violations)

---

## Completed Priorities ✅

### Priority 1: Foundation (Skills + Bootstrap + MCP Server) ✅
**Completed**: 2025-11-17
**Deliverables**: Skills export, Bootstrap package, MCP server baseline

### Priority 1.5: Skills Export to SKILL.md Format ✅
**Completed**: 2025-11-18
**Deliverables**: SKILL.md format specification and examples

### Priority 1.9: Bootstrap Package with Examples ✅
**Completed**: 2025-11-18
**Deliverables**: Project generation system with working examples

### Priority 2: Process Memory System Implementation ✅
**Completed**: 2025-11-18
**Deliverables**: ProcessMemoryStore, KnowledgeGraph, JSONL storage

### Priority 3: Thinking Tools (14 Tools Created) ✅
**Completed**: 2025-11-19
**Deliverables**: 14 thinking tools in YAML format, validated and tested

### Priority 4: Core Components (Custom Jinja2 Filters) ✅
**Completed**: 2025-11-19
**Deliverables**: Template engine with custom filters, 90% already existed

### Priority 5: Python Contracts/Protocols ✅
**Completed**: 2025-11-19
**Deliverables**: 8 Protocol definitions enforcing five-layer architecture
**Quality**: ACCEPTED with EXCELLENCE (8 protocols vs 5 requested)

### Priority 6: Process Memory Activation ✅
**Completed**: 2025-11-20
**Duration**: 90 minutes
**Deliverables**:
- 4 PM entries created (Priorities 2-5), total 6 entries in file
- Knowledge graph built and validated with real queries
- Information-Memory-Graph paradigm validated
- 7 integration tests (100% passing)
- PROCESS-MEMORY-USAGE.md documentation (~4000 words)
**Quality**: All gates passed (pytest 493/494, mypy 0 errors, ruff 0 violations, 83% coverage)
**Key Achievement**: PM system transitioned from "built but unused" to "actively used with real data"

### Priority 7: CLI Layer Boundary Refactoring ✅
**Completed**: 2025-11-20
**Duration**: ~45 minutes (exceptionally fast execution)
**Deliverables**:
- Removed SchemaValidator import from cli.py (Processing layer violation)
- Added StorageProtocol type hints for 5 ProcessMemoryStore instances
- Extended StorageProtocol with list_entries() method
- Updated 4 provisioning classes to use StorageProtocol
- Refactored validation to delegate to ToolRegistry.load_tool()
- Updated CLI tests to reflect new architecture
**Quality**: All gates passed (pytest 493/493, mypy 0 errors, ruff 0 violations, 82% coverage)
**Key Achievement**: CLI now follows five-layer boundaries, no upward dependencies
**Architectural Impact**: Gap 3 resolved - proper layer isolation enforced through protocol contracts
**Commit**: 26a12f8

---

## Future Considerations (Not Yet Prioritized)

### Plugin System Implementation
**Context**: Spec exists (specs/05-PLUGIN-SYSTEM.md claimed), needs implementation
**Estimate**: TBD
**Dependencies**: Core framework stable

### Web Dashboard (Optional)
**Context**: React-based UI for thinking tools
**Estimate**: TBD
**Priority**: Low (CLI and MCP server sufficient for now)

### Registry Integration
**Context**: Publishing/sync with tool registries
**Estimate**: TBD
**Dependencies**: Core tools stable and validated

---

## Notes

**Prioritization Criteria**:
1. Architectural foundation (contracts, boundaries)
2. AI-First validation (process memory, paradigm)
3. Core functionality (CLI, tools)
4. Documentation (specs, guides)
5. Advanced features (plugins, registry)

**Quality Standard**: 100% means 100%
- pytest: All tests pass
- mypy: 0 errors with --strict
- ruff: 0 violations
- No regressions tolerated

**Paradigm**: "Everything is information → memory → graph"
- All work documented in process memory
- Knowledge graph tracks relationships
- Future AI sessions have complete context

---

## Backlog Maintenance

**Review Cadence**: After each priority completion
**Owner**: Coordinator
**Updates**: Add new items, reprioritize based on learnings
**Process Memory Integration**: All backlog items linked to PM entries

---

## Ideas Tracker (Concepts for Future Exploration)

### Idea: Perplexity Conversation Processor 📊
**Status**: Immature concept (needs refinement)
**Estimated Effort**: 4-6 hours
**Context**: Tool to process Perplexity AI conversation exports for knowledge extraction

**Deliverables**:
1. **Direct-to-Memory Mode**:
   - Parse Perplexity conversation structure (/// delimiters, # markers)
   - Extract hypotheses, validations, code examples
   - Generate process memory entries automatically
   - Link related concepts in knowledge graph
   
2. **Analysis Modes**:
   - Paradigm extraction (identify foundational principles)
   - High-level concept mapping (distill key ideas)
   - Evolution tracing (map how ideas changed through conversation)
   - Code example progression (extract phase-by-phase learning)
   - Correction detection (find "however", "but", "actually" markers)
   
3. **Integration**:
   - Serena MCP tool for structure-first analysis
   - Adaptive reading strategy (calculate optimal chunk sizes)
   - Multi-context analysis (structure, content, evolution, meta)
   - Output to process memory JSONL with proper linking

**Why Interesting**: Perplexity conversations are knowledge goldmines, but 100k+ char files exceed context limits. Need intelligent extraction.

**Needs Exploration**:
- Define clear scope (what modes are actually needed?)
- Determine if this should be Serena tool, thinking tool, or separate utility
- Validate use case frequency (how often will this be needed?)
- Consider if manual analysis with adaptive strategy is sufficient

**Related Patterns**:
- Structure-Before-Content (Pattern 1)
- Evolution-First Reading (Pattern 4)
- Adaptive Reading Strategy (Serena memory)

**Potential Dependencies**: Serena MCP server, Process Memory system

---

## Future Priorities (Research & Analysis Tools)

### Priority: Six Thinking Tool Patterns Implementation 🧠
**Status**: Proposed (Ready for prioritization)
**Estimated Effort**: 6-8 hours
**Context**: Implement the six patterns distilled from Perplexity analysis session

**Deliverables**:
1. **Pattern 1: Structure-Before-Content Analyzer**
   - Tool to map document structure before reading
   - Calculate optimal reading strategies
   - Generate sectioned analysis plans
   
2. **Pattern 2: Context-Cycling Enforcer**
   - Timer-based context switching
   - Prevent single-context fixation
   - Track context coverage
   
3. **Pattern 3: Rhythmic Processing Guide**
   - Probe → Measure → Adapt → Execute → Reflect workflow
   - Pause enforcement between phases
   - Reflection prompts
   
4. **Pattern 4: Evolution Tracer**
   - Find initial hypothesis
   - Map doubt/correction markers
   - Trace synthesis progression
   - Generate evolution narratives
   
5. **Pattern 5: Correction-First Analyzer**
   - Search corrections before validations
   - Anti-confirmation-bias checks
   - Map where ideas changed and why
   
6. **Pattern 6: Phase-Progressive Learner**
   - Extract learning from example progression
   - Identify phase transitions
   - Discover underlying principles

**Why Critical**: These patterns prevent cognitive fixation and improve analytical quality. Emerged from real analysis failures.

**Quality Gates**:
- Each pattern has YAML tool definition
- Integration tests with sample documents
- Process memory integration
- Documentation with examples

**Dependencies**: Core thinking tools framework (Priority 3 - complete)

---

### Ideas Tracker Entry: Perplexity Conversation Analysis Toolkit

**Concept**: Specialized toolkit for processing Perplexity AI conversations

**Components**:
- **Structure Discovery**: Automatic delimiter detection, section mapping
- **Content Extraction**: Hypothesis evolution, code examples, paradigms
- **Memory Generation**: Auto-create process memory entries with links
- **Analysis Modes**: 
  - Paradigm extraction
  - High-level concept distillation
  - Evolution tracing
  - Correction detection
  - Progressive learning from examples

**Use Cases**:
- Research validation documentation
- Knowledge extraction from expert consultations
- Hypothesis evolution tracking
- Pattern library building from conversations

**Technical Approach**:
- Serena MCP for structure analysis
- Adaptive chunk reading (based on measured sizes)
- Pattern-based extraction (regex + context awareness)
- Knowledge graph linking (automatic relationship detection)

**Value Proposition**: Turn 100k+ char Perplexity conversations into structured, queryable knowledge without context overload.

---

