# Claude Code Quick Start Guide - Cogito Framework

## 🏠 Welcome to the House

You're working in the **Cogito Framework** - a thinking tools system for AI-augmented development. This guide teaches you how to "live in the house, work in the house, and work with the house."

---

## 🔍 Environment Detection

**How do I know I'm in a Cogito project?**

Look for these markers:

```bash
# Primary indicators
.cogito/                    # Configuration directory
cogito.yml                  # Main configuration file
specs/thinking-tools/       # Thinking tool specifications

# Documentation indicators
docs/plans/thinking-tools/  # Planning and specification docs
IMPLEMENTATION-ROADMAP.md   # Project status tracker
06-TECHNICAL-SPECIFICATIONS-INDEX.md  # Spec navigation

# Memory indicators (Serena integration)
.serena/memories/cogito-*   # Pre-provisioned design memories
```

**Environment Variables to Check:**

```bash
# Check if Cogito CLI is available
which cogito || echo "Cogito not installed yet"

# Check configuration
cat cogito.yml 2>/dev/null || cat .cogito/config.yml 2>/dev/null
```

---

## 🚀 Initial Orientation Sequence

**IMPORTANT:** Do NOT read all 27 specifications at once! You'll consume 40% of your context window (81k tokens). Use this sequence instead.

### Phase 1: Bootstrap Understanding (5-10 minutes)

**Read these files in order:**

1. **This file** - CLAUDE-CODE-QUICK-START.md (you are here)
2. **Project Status** - `IMPLEMENTATION-ROADMAP.md` (current phase, completion status)
3. **Navigation Index** - `06-TECHNICAL-SPECIFICATIONS-INDEX.md` (what exists, where to find it)

**Run these memory queries:**

```bash
# Get architecture overview
mcp__serena__read_memory --memory_file_name="cogito-architecture-overview.md"

# Get quick FAQ
mcp__serena__read_memory --memory_file_name="cogito-faq-getting-started.md"

# List all available Cogito memories
mcp__serena__list_memories | grep "cogito-"
```

**Total token cost:** ~3,000 tokens (1.5% of context window)

### Phase 2: Understand Your Task Context (2-5 minutes)

**Ask yourself:**

1. **What am I being asked to do?**
   - Implement a component? → Query `cogito-spec-summary-{component}.md`
   - Fix a bug? → Query `cogito-pattern-debugging.md`
   - Add a feature? → Query `cogito-architecture-overview.md` first
   - Review design? → Query `cogito-decision-*.md` memories

2. **Which layer does this involve?**
   - Layer 1 (UI): CLI, MCP Server, Web Dashboard
   - Layer 2 (Orchestration): Manager, Plugins, Cache
   - Layer 3 (Processing): Loader, Validator, Generator, Template, Memory
   - Layer 4 (Storage): Spec Storage, Code Cache, Memory Log, Cache Backend
   - Layer 5 (Integration): Serena, Git, Registry

3. **What components are involved?**
   - Use index to find spec numbers
   - Query only those spec summaries
   - Read full specs only if implementing

**Memory Query Pattern:**

```bash
# Example: Implementing Template Engine
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-template-engine.md"
mcp__serena__read_memory --memory_file_name="cogito-decision-sandboxed-jinja2.md"
mcp__serena__read_memory --memory_file_name="cogito-protocols-quick-ref.md"

# Now you have context without reading full spec (saves ~3,500 tokens)
```

### Phase 3: Load Detailed Information (Just-In-Time)

**Only read full specifications when:**
- You need to implement the component
- You're reviewing implementation details
- You're writing tests for the component
- The summary doesn't answer your specific question

**Reading Strategy:**

```bash
# Option 1: Read single spec (average 3,000 tokens each)
Read --file_path="docs/plans/thinking-tools/specs/10-TEMPLATE-ENGINE.md"

# Option 2: Read specific sections using grep
Bash --command="grep -A 50 '## Interface Definition' docs/plans/thinking-tools/specs/10-TEMPLATE-ENGINE.md"

# Option 3: Query memory for cross-references
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-template-engine.md"
# This memory will tell you dependencies: "Depends on: Validator (08)"
```

---

## 🧭 JIT Reading Decision Tree

**Use this decision tree for every task:**

```
START: New task received
│
├─→ Is this my first time in this project?
│   YES → Run Phase 1 Bootstrap (read Quick Start + Roadmap + Index)
│   NO  → Continue
│
├─→ Do I understand which components are involved?
│   NO  → Query cogito-architecture-overview.md + cogito-faq-components.md
│   YES → Continue
│
├─→ Do I need to know WHY decisions were made?
│   YES → Query cogito-decision-*.md memories (10 available)
│   NO  → Continue
│
├─→ Do I need high-level understanding of component?
│   YES → Query cogito-spec-summary-{component}.md (27 available)
│   NO  → Continue
│
├─→ Do I need to see code interfaces/protocols?
│   YES → Query cogito-protocols-quick-ref.md
│   NO  → Continue
│
├─→ Do I need implementation details?
│   YES → Read full spec for component (specs/{NN}-{NAME}.md)
│   NO  → Continue
│
├─→ Do I need to understand patterns/best practices?
│   YES → Query cogito-pattern-*.md memories
│   NO  → Continue
│
└─→ READY TO WORK
```

**Token Budget Management:**

| Action | Tokens | Cumulative | Context % |
|--------|--------|------------|-----------|
| Bootstrap (Phase 1) | 3,000 | 3,000 | 1.5% |
| Architecture memory | 800 | 3,800 | 1.9% |
| 3 spec summaries | 600 | 4,400 | 2.2% |
| Protocols reference | 1,200 | 5,600 | 2.8% |
| 1 full spec (if needed) | 3,000 | 8,600 | 4.3% |
| Working space remaining | - | 191,400 | 95.7% |

---

## 🛠️ Common Workflows

### Workflow 1: Implementing a New Component

**Scenario:** Implement the Template Engine component

```bash
# Step 1: Understand architecture context
mcp__serena__read_memory --memory_file_name="cogito-architecture-overview.md"

# Step 2: Read component summary
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-template-engine.md"
# Output shows: "Depends on: None | Used by: Code Generator (09), Thinking Tools Manager (04)"

# Step 3: Read design decision
mcp__serena__read_memory --memory_file_name="cogito-decision-sandboxed-jinja2.md"
# Output shows: Why Jinja2, why sandboxed, security requirements

# Step 4: Get protocol interface
mcp__serena__read_memory --memory_file_name="cogito-protocols-quick-ref.md"
# Scan for: "class TemplateEngineProtocol(Protocol):"

# Step 5: NOW read full spec (only if implementing)
Read --file_path="docs/plans/thinking-tools/specs/10-TEMPLATE-ENGINE.md"

# Step 6: Check dependencies (Validator summary said it's needed)
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-validator.md"

# Ready to implement!
```

**Token Cost:** ~8,000 tokens (4% of context window) vs. 81,000 tokens if you read everything

### Workflow 2: Debugging an Issue

**Scenario:** Template rendering is failing with security error

```bash
# Step 1: Query debugging pattern
mcp__serena__read_memory --memory_file_name="cogito-pattern-debugging.md"

# Step 2: Query relevant decision
mcp__serena__read_memory --memory_file_name="cogito-decision-sandboxed-jinja2.md"
# Learn: ImmutableSandboxedEnvironment is used, what's allowed/blocked

# Step 3: Query security spec summary
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-security.md"

# Step 4: Only if needed, read full security spec
Read --file_path="docs/plans/thinking-tools/specs/19-SECURITY-SPECIFICATION.md"

# Step 5: Check error handling patterns
mcp__serena__read_memory --memory_file_name="cogito-pattern-error-handling.md"
```

### Workflow 3: Reviewing Design Decisions

**Scenario:** User asks "Why YAML instead of JSON?"

```bash
# Step 1: Query specific decision
mcp__serena__read_memory --memory_file_name="cogito-decision-yaml-format.md"
# Output shows: Decision, rationale, alternatives considered, trade-offs

# Step 2: If more context needed, query ADR
Read --file_path="docs/plans/thinking-tools/04-ARCHITECTURE-DECISION-RECORDS.md"
Bash --command="grep -A 30 'ADR-001: YAML Specification Format' docs/plans/thinking-tools/04-ARCHITECTURE-DECISION-RECORDS.md"

# Ready to answer!
```

### Workflow 4: Adding a New Feature

**Scenario:** Add process memory export feature

```bash
# Step 1: Understand process memory component
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-process-memory.md"

# Step 2: Read design decision
mcp__serena__read_memory --memory_file_name="cogito-decision-process-memory-log.md"

# Step 3: Check related components
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-process-memory-log.md"

# Step 4: Get protocols
mcp__serena__read_memory --memory_file_name="cogito-protocols-quick-ref.md"

# Step 5: Read full spec for implementation details
Read --file_path="docs/plans/thinking-tools/specs/11-PROCESS-MEMORY.md"
Read --file_path="docs/plans/thinking-tools/specs/14-PROCESS-MEMORY-LOG.md"

# Step 6: Check testing requirements
Bash --command="grep -A 20 'Testing Requirements' docs/plans/thinking-tools/specs/11-PROCESS-MEMORY.md"
```

---

## 🧠 Working with Serena Memory System

### Memory Organization

**All Cogito memories follow this naming convention:**

```
cogito-{category}-{topic}.md

Categories:
- architecture    (system structure, layers, components)
- decision       (ADR summaries, rationale, alternatives)
- spec-summary   (condensed spec overviews)
- protocols      (interface definitions)
- pattern        (implementation patterns, best practices)
- faq            (common questions and answers)
```

### Memory Discovery

**List all available memories:**

```bash
# All Cogito memories
mcp__serena__list_memories | grep "cogito-"

# By category
mcp__serena__list_memories | grep "cogito-decision-"
mcp__serena__list_memories | grep "cogito-spec-summary-"
```

**Expected memories (to be provisioned):**

```yaml
Architecture Memories (5):
- cogito-architecture-overview.md
- cogito-architecture-five-layers.md
- cogito-architecture-cornerstones.md
- cogito-architecture-ai-first.md
- cogito-architecture-integration.md

Decision Memories (10):
- cogito-decision-yaml-format.md
- cogito-decision-sandboxed-jinja2.md
- cogito-decision-process-memory-log.md
- cogito-decision-hot-reload.md
- cogito-decision-validation-pipeline.md
- cogito-decision-plugin-architecture.md
- cogito-decision-semantic-versioning.md
- cogito-decision-five-layer-arch.md
- cogito-decision-zero-serena-mods.md
- cogito-decision-declarative-first.md

Spec Summary Memories (27):
- cogito-spec-summary-cli.md
- cogito-spec-summary-mcp-server.md
- cogito-spec-summary-web-dashboard.md
- ... (one for each of 27 specs)

Protocol Reference (1):
- cogito-protocols-quick-ref.md

Pattern Memories (8):
- cogito-pattern-validation.md
- cogito-pattern-error-handling.md
- cogito-pattern-caching.md
- cogito-pattern-security.md
- cogito-pattern-testing.md
- cogito-pattern-debugging.md
- cogito-pattern-configuration.md
- cogito-pattern-integration.md

FAQ Memories (6):
- cogito-faq-getting-started.md
- cogito-faq-components.md
- cogito-faq-security.md
- cogito-faq-performance.md
- cogito-faq-deployment.md
- cogito-faq-troubleshooting.md
```

### Memory Query Patterns

**Pattern 1: Quick Start (First Session)**

```bash
mcp__serena__read_memory --memory_file_name="cogito-faq-getting-started.md"
mcp__serena__read_memory --memory_file_name="cogito-architecture-overview.md"
mcp__serena__list_memories | grep "cogito-"
```

**Pattern 2: Component Understanding**

```bash
# Summary first
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-{component}.md"

# Then decision if needed
mcp__serena__read_memory --memory_file_name="cogito-decision-{related}.md"

# Finally full spec if implementing
Read --file_path="docs/plans/thinking-tools/specs/{NN}-{COMPONENT}.md"
```

**Pattern 3: Implementation Readiness**

```bash
# Get interfaces
mcp__serena__read_memory --memory_file_name="cogito-protocols-quick-ref.md"

# Get patterns
mcp__serena__read_memory --memory_file_name="cogito-pattern-{relevant}.md"

# Get testing guidance
mcp__serena__read_memory --memory_file_name="cogito-spec-summary-testing-strategy.md"
```

**Pattern 4: Design Rationale**

```bash
# Read decision
mcp__serena__read_memory --memory_file_name="cogito-decision-{topic}.md"

# Get architecture context
mcp__serena__read_memory --memory_file_name="cogito-architecture-cornerstones.md"

# Check related ADR if needed
Bash --command="grep -A 50 'ADR-00{N}' docs/plans/thinking-tools/04-ARCHITECTURE-DECISION-RECORDS.md"
```

### Creating New Memories

**When to create a new memory:**

- You discover a pattern not documented
- You learn something that would help future sessions
- You solve a problem that might recur
- You make an implementation decision

**Memory creation template:**

```bash
mcp__serena__write_memory \
  --memory_file_name="cogito-{category}-{topic}.md" \
  --content="# {Title}

## Context
[Why this memory exists]

## Key Information
[The actual knowledge]

## Usage
[When/how to apply this]

## Related
- Memory: cogito-{related}-{topic}.md
- Spec: specs/{NN}-{NAME}.md
- Decision: cogito-decision-{related}.md
"
```

---

## 📋 Daily Operations Checklist

### Starting a New Task

- [ ] Understand the task scope and objectives
- [ ] Identify which components are involved (use index)
- [ ] Query relevant spec summaries (not full specs!)
- [ ] Query relevant decision memories if design context needed
- [ ] Query protocols reference if implementing
- [ ] Read full specs only for components you're implementing
- [ ] Check pattern memories for implementation guidance

### During Implementation

- [ ] Follow protocol interfaces from memory/specs
- [ ] Check security considerations (query cogito-pattern-security.md)
- [ ] Check error handling patterns (query cogito-pattern-error-handling.md)
- [ ] Verify test requirements from spec
- [ ] Document any new patterns learned

### Before Completing Task

- [ ] Run tests (if implementation)
- [ ] Verify cornerstone alignment (Configurability, Modularity, Extensibility, Integration, Automation)
- [ ] Verify AI-First principles (Machine-readable, Self-documenting, Context preservation, No hidden state)
- [ ] Update relevant memories if new knowledge gained
- [ ] Check if process memory should be updated

---

## 🎯 Success Metrics

**You're working efficiently if:**

- ✅ Bootstrap phase uses <5% of context window (~10k tokens)
- ✅ You query memories before reading full specs
- ✅ You only read full specs when implementing
- ✅ You maintain >90% context window for actual work
- ✅ You can answer "why" questions from decision memories
- ✅ You discover and use patterns from pattern memories

**You're using too much context if:**

- ❌ You read all 27 specs upfront
- ❌ You read full specs for components you're not implementing
- ❌ You don't check memories before reading docs
- ❌ You re-read the same content multiple times
- ❌ You have <80% context window remaining for work

---

## 🏗️ Project Structure Reference

```
docs/plans/thinking-tools/
├── IMPLEMENTATION-ROADMAP.md              # Current status, next steps
├── 06-TECHNICAL-SPECIFICATIONS-INDEX.md   # Navigation, dependencies
├── CLAUDE-CODE-QUICK-START.md             # This file
│
├── Foundation Documents/
│   ├── 00-PRODUCT-VISION.md
│   ├── 01-CONSTITUTION.md
│   ├── 02-ARCHITECTURE.md                  # Five-layer architecture
│   ├── 03-FRAMEWORK-SPECIFICATION.md
│   ├── 04-ARCHITECTURE-DECISION-RECORDS.md # 10 ADRs
│   └── 05-PRODUCT-DESCRIPTION.md
│
├── specs/                                  # 27 technical specifications
│   ├── 00-IMPERATIVES-INTEGRATION.md
│   ├── 01-CLI-SPECIFICATION.md
│   ├── 02-MCP-SERVER-INTERFACE.md
│   ├── ... (27 total)
│   └── 26-BACKUP-RECOVERY.md
│
├── schemas/                                # Machine-readable contracts
│   ├── thinking-tool-v1.0.schema.json
│   ├── config-v1.0.schema.json
│   └── process-memory-v1.0.schema.json
│
└── contracts/
    └── python-protocols.py                 # All protocol interfaces

.serena/memories/                           # Serena memory integration
├── cogito-architecture-*.md                # Architecture memories (5)
├── cogito-decision-*.md                    # Decision memories (10)
├── cogito-spec-summary-*.md                # Spec summaries (27)
├── cogito-protocols-quick-ref.md           # Protocol reference (1)
├── cogito-pattern-*.md                     # Pattern memories (8)
└── cogito-faq-*.md                         # FAQ memories (6)
                                            # Total: 57 memory files
```

---

## 🔧 Troubleshooting

### "I don't know where to start"

→ Run Phase 1 Bootstrap sequence (this file + roadmap + index)
→ Query `cogito-faq-getting-started.md`
→ Use JIT reading decision tree above

### "I'm running out of context"

→ You probably read too many full specs
→ Use memory queries instead: `mcp__serena__read_memory --memory_file_name="cogito-spec-summary-*.md"`
→ Read full specs only when implementing

### "I don't understand why a decision was made"

→ Query `cogito-decision-{topic}.md` memory
→ If not sufficient, read relevant ADR section
→ Don't read entire ADR document (use grep)

### "I need to know interfaces/protocols"

→ Query `cogito-protocols-quick-ref.md` first
→ If implementing, read full spec for detailed type hints
→ Reference `contracts/python-protocols.py` for complete definitions

### "I don't know what patterns to follow"

→ Query `cogito-pattern-{relevant}.md` memories
→ Check spec's "Example Usage" section
→ Look at "Implementation Requirements" in spec

### "Memory not found"

→ Memory provisioning may not be complete yet
→ Check available memories: `mcp__serena__list_memories | grep "cogito-"`
→ Fall back to spec summaries in index
→ Create the memory if you develop the knowledge

---

## 📚 Further Reading

**After bootstrap, consult these as needed:**

- **Architecture deep-dive:** `02-ARCHITECTURE.md` (five layers, components, data flow)
- **Design decisions:** `04-ARCHITECTURE-DECISION-RECORDS.md` (10 ADRs with rationale)
- **All specs navigation:** `06-TECHNICAL-SPECIFICATIONS-INDEX.md`
- **Cornerstone principles:** `01-CONSTITUTION.md`
- **Product vision:** `00-PRODUCT-VISION.md`

**Remember:** Query memories first, read full documents only when necessary!

---

## 🎓 Key Principles

1. **JIT Reading:** Load information just-in-time, not just-in-case
2. **Memory First:** Query Serena memories before reading full specs
3. **Summaries Save Context:** 200-word summaries vs. 3,000-word specs
4. **Progressive Detail:** Start broad (architecture) → narrow (component) → deep (implementation)
5. **Decision Context:** Understand WHY through decision memories
6. **Pattern Reuse:** Don't reinvent, query pattern memories
7. **Context Budget:** Bootstrap = 5%, Working = 90%, References = 5%

---

## ✅ Quick Start Checklist

**First 5 minutes in the project:**

- [ ] Run environment detection (check for `.cogito/`, `cogito.yml`)
- [ ] Read this quick start guide (you are here!)
- [ ] Read `IMPLEMENTATION-ROADMAP.md` (current status)
- [ ] Read `06-TECHNICAL-SPECIFICATIONS-INDEX.md` (navigation)
- [ ] List available memories: `mcp__serena__list_memories | grep "cogito-"`
- [ ] Query: `cogito-faq-getting-started.md`
- [ ] Query: `cogito-architecture-overview.md`

**Total: ~3,000 tokens, ~1.5% of context window**

You're now ready to work efficiently in the Cogito framework! 🚀

---

**Document Status:**
- **Version:** 1.0.0
- **Status:** Complete
- **Dependencies:** IMPLEMENTATION-ROADMAP.md, 06-TECHNICAL-SPECIFICATIONS-INDEX.md, Serena memory system
- **Integration:** Part of Review Exercise 4 deliverables
