# Thinking Tools Framework - Project Backlog

**Last Updated**: 2025-11-19
**Maintained By**: Coordinator

---

## Active Priorities (In Progress)

### Priority 7: CLI Layer Boundary Refactoring 📋
**Status**: Ready to start (Priority 6 complete)
**Estimated Effort**: 2-3 hours
**Context**: Gap 3 from holistic analysis - CLI directly imports from all layers

**Deliverables**:
1. Refactor cli.py to use OrchestrationProtocol only
2. Remove direct imports from processing/storage layers
3. Fix layer boundary violations
4. All tests still pass (486+)

**Dependencies**: Priority 5 (Contracts - completed), Priority 6 (Process Memory)

**Why Critical**: Enforces five-layer architecture boundaries, prevents architectural drift

---

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
**Severity**: Medium
**Impact**: Future development and onboarding

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
- ❌ 27 detailed modular spec files
- ❌ JSON schemas (thinking-tool, config, process-memory, plugin-manifest)
- ❌ Plan files for spec generation
- ❌ Cross-reference validation
- ❌ Detailed component specifications

**Recommendation**:
Add as **Priority 9** or later, after core functionality is complete and stable.

**Proposed Deliverables**:
1. Generate all 27 modular specs from existing code and architecture
2. Create JSON schemas in `schemas/` directory
3. Validate cross-references between specs
4. Update index to reflect actual status
5. Create plan files for future spec updates

**Estimated Effort**: 8-12 hours (comprehensive documentation generation)

**Process Memory Reference**: `technical-documentation-gap-2025-11-19`

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

