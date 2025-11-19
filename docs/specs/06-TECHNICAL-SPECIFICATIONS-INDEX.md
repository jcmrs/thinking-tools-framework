# Thinking Tools Framework - Technical Specifications Index

## Document Purpose

This index provides a modular, just-in-time navigation system for the technical specifications. Following the **AI-First** and **Modularity** principles, specifications are split into focused documents that can be:

- Loaded on-demand (no massive token consumption)
- Updated independently (single responsibility)
- Referenced precisely (clear dependencies)
- Queried efficiently (specific topics)

---

## Specification Map

### Layer-Based Organization

The technical specifications follow our five-layer architecture. Load only the layers relevant to your current work:

```
Technical Specifications
│
├── 00-IMPERATIVES-INTEGRATION.md          [START HERE]
│   └── How Five Cornerstones + AI-First permeate all specs
│
├── Layer 1: User Interface
│   ├── specs/01-CLI-SPECIFICATION.md
│   ├── specs/02-MCP-SERVER-INTERFACE.md
│   └── specs/03-WEB-DASHBOARD.md (future)
│
├── Layer 2: Orchestration
│   ├── specs/04-THINKING-TOOLS-MANAGER.md
│   ├── specs/05-PLUGIN-SYSTEM.md
│   └── specs/06-CACHE-MANAGEMENT.md
│
├── Layer 3: Processing
│   ├── specs/07-SPEC-LOADER.md
│   ├── specs/08-VALIDATOR.md
│   ├── specs/09-CODE-GENERATOR.md
│   ├── specs/10-TEMPLATE-ENGINE.md
│   └── specs/11-PROCESS-MEMORY.md
│
├── Layer 4: Storage
│   ├── specs/12-SPEC-STORAGE.md
│   ├── specs/13-GENERATED-CODE-CACHE.md
│   ├── specs/14-PROCESS-MEMORY-LOG.md
│   └── specs/15-CACHE-BACKEND.md
│
├── Layer 5: Integration
│   ├── specs/16-SERENA-INTEGRATION.md
│   ├── specs/17-GIT-VCS-INTEGRATION.md
│   └── specs/18-REGISTRY-INTEGRATION.md
│
├── Cross-Cutting Concerns
│   ├── specs/19-SECURITY-SPECIFICATION.md
│   ├── specs/20-PERFORMANCE-SPECIFICATION.md
│   ├── specs/21-OBSERVABILITY-SPECIFICATION.md
│   └── specs/22-ERROR-HANDLING.md
│
├── Operations
│   ├── specs/23-DEPLOYMENT-SPECIFICATION.md
│   ├── specs/24-TESTING-STRATEGY.md
│   ├── specs/25-MONITORING-ALERTING.md
│   └── specs/26-BACKUP-RECOVERY.md
│
└── Schemas & Contracts
    ├── schemas/thinking-tool-v1.0.schema.json
    ├── schemas/config-v1.0.schema.json
    ├── schemas/process-memory-v1.0.schema.json
    └── contracts/python-protocols.py
```

---

## Quick Navigation

### By Role

**Product Owner / Strategist:**
- Start: `00-IMPERATIVES-INTEGRATION.md`
- Review: Product alignment with cornerstones
- Context: How architecture embodies values

**Backend Developer (Python):**
- Start: `specs/04-THINKING-TOOLS-MANAGER.md`
- Core: Processing Layer specs (07-11)
- Contracts: `contracts/python-protocols.py`

**CLI Developer:**
- Start: `specs/01-CLI-SPECIFICATION.md`
- Related: `04-THINKING-TOOLS-MANAGER.md` (API consumer)

**Integration Engineer:**
- Start: `specs/16-SERENA-INTEGRATION.md`
- Related: Integration Layer specs (16-18)

**Security Engineer:**
- Start: `specs/19-SECURITY-SPECIFICATION.md`
- Critical: `specs/10-TEMPLATE-ENGINE.md` (sandboxing)

**QA / Test Engineer:**
- Start: `specs/24-TESTING-STRATEGY.md`
- Related: All specs (testing requirements per component)

**DevOps / SRE:**
- Start: `specs/23-DEPLOYMENT-SPECIFICATION.md`
- Related: `specs/25-MONITORING-ALERTING.md`, `specs/26-BACKUP-RECOVERY.md`

**AI Agent (New Session):**
- Start: `00-IMPERATIVES-INTEGRATION.md`
- Context: `specs/11-PROCESS-MEMORY.md`
- Architecture: `../02-ARCHITECTURE.md`

---

## Reading Order Recommendations

### First-Time Orientation
1. `00-IMPERATIVES-INTEGRATION.md` - Understand foundational constraints
2. `../02-ARCHITECTURE.md` - System overview (already read)
3. `specs/04-THINKING-TOOLS-MANAGER.md` - Central coordinator
4. Choose layer based on work area

### Implementation Phase
1. Choose component to implement
2. Read component spec + dependencies
3. Review cross-cutting concerns (security, performance)
4. Check contracts in `contracts/`

### Integration Phase
1. `specs/16-SERENA-INTEGRATION.md`
2. `specs/02-MCP-SERVER-INTERFACE.md`
3. `specs/24-TESTING-STRATEGY.md` (integration tests)

### Operations Phase
1. `specs/23-DEPLOYMENT-SPECIFICATION.md`
2. `specs/25-MONITORING-ALERTING.md`
3. `specs/26-BACKUP-RECOVERY.md`

---

## Document Relationships

### Dependencies (Read Prerequisites)

```
01-CLI-SPECIFICATION.md
  requires: 04-THINKING-TOOLS-MANAGER.md

02-MCP-SERVER-INTERFACE.md
  requires: 04-THINKING-TOOLS-MANAGER.md
  requires: 16-SERENA-INTEGRATION.md

04-THINKING-TOOLS-MANAGER.md
  requires: 07-SPEC-LOADER.md
  requires: 08-VALIDATOR.md
  requires: 09-CODE-GENERATOR.md
  requires: 11-PROCESS-MEMORY.md

08-VALIDATOR.md
  requires: 10-TEMPLATE-ENGINE.md (security validation)
  requires: schemas/thinking-tool-v1.0.schema.json

10-TEMPLATE-ENGINE.md
  requires: 19-SECURITY-SPECIFICATION.md

11-PROCESS-MEMORY.md
  requires: 14-PROCESS-MEMORY-LOG.md
  requires: schemas/process-memory-v1.0.schema.json

16-SERENA-INTEGRATION.md
  requires: 09-CODE-GENERATOR.md
```

### Cornerstone References

Each spec explicitly maps to cornerstones. Quick reference:

**Configurability:**
- CLI: `01-CLI-SPECIFICATION.md`
- Config: `schemas/config-v1.0.schema.json`
- All components: Config-driven behavior

**Modularity:**
- Architecture: `../02-ARCHITECTURE.md`
- Protocols: `contracts/python-protocols.py`
- All component specs: Interface definitions

**Extensibility:**
- Plugins: `specs/05-PLUGIN-SYSTEM.md`
- Hooks: Referenced in component specs

**Integration:**
- Layer 5 specs: `specs/16-18`
- MCP: `specs/02-MCP-SERVER-INTERFACE.md`

**Automation:**
- Manager: `specs/04-THINKING-TOOLS-MANAGER.md`
- Discovery: `specs/07-SPEC-LOADER.md`
- Reload: `specs/06-CACHE-MANAGEMENT.md`

---

## Schema & Contract Files

### JSON Schemas (Machine-Readable)

**Location:** `schemas/`

- `thinking-tool-v1.0.schema.json` - Spec format validation
- `config-v1.0.schema.json` - Configuration validation
- `process-memory-v1.0.schema.json` - Memory entry validation
- `plugin-manifest-v1.0.schema.json` - Plugin metadata

**Usage:**
```python
import jsonschema

schema = json.load(open("schemas/thinking-tool-v1.0.schema.json"))
jsonschema.validate(instance=spec_data, schema=schema)
```

### Python Protocols (Type Contracts)

**Location:** `contracts/python-protocols.py`

All interface definitions in one place:
- `ThinkingToolsManagerProtocol`
- `SpecLoaderProtocol`
- `ValidatorProtocol`
- `CodeGeneratorProtocol`
- `TemplateEngineProtocol`
- `ProcessMemoryStoreProtocol`
- `PluginProtocol`
- And all data models

**Usage:**
```python
from cogito.contracts import ThinkingToolsManagerProtocol

# Type checker validates conformance
class MyManager(ThinkingToolsManagerProtocol):
    ...
```

---

## Specification Format

Each modular spec follows this structure:

```markdown
# Component Name

## Cornerstone Alignment
[Explicit mapping to Five Cornerstones]

## AI-First Considerations
[Machine-readability, introspection, context preservation]

## Overview
[What this component does]

## Interface Definition
[Protocol/API with type hints]

## Data Models
[Structured data formats]

## Implementation Requirements
[Behavioral contracts]

## Configuration
[Config schema for this component]

## Testing Requirements
[How to test this component]

## Process Memory Integration
[What this component captures]

## Dependencies
[What other components it requires]

## Example Usage
[Code examples]
```

---

## Version Control Strategy

**Specifications are code.** They follow semantic versioning:

- **MAJOR**: Breaking changes to interfaces
- **MINOR**: Backward-compatible additions
- **PATCH**: Clarifications, typos, examples

**Current Version:** All specs at v1.0.0 (initial)

**Change Process:**
1. Propose change via RFC
2. Update spec file
3. Bump version
4. Update index dependencies
5. Regenerate contracts if needed

---

## AI Session Instructions

### For New AI Sessions

**Step 1: Understand Context**
```
Read in order:
1. This index (06-TECHNICAL-SPECIFICATIONS-INDEX.md)
2. 00-IMPERATIVES-INTEGRATION.md
3. ../02-ARCHITECTURE.md (overview)
```

**Step 2: Query Process Memory**
```
# Use process memory to understand decisions
cogito memory query --type=StrategicDecision --tags=architecture
```

**Step 3: Load Relevant Specs**
```
# Only load specs for your work area
# Example: Working on validator
Read: specs/08-VALIDATOR.md
Read: specs/10-TEMPLATE-ENGINE.md (dependency)
Read: specs/19-SECURITY-SPECIFICATION.md (cross-cutting)
```

**Step 4: Reference Contracts**
```
# Check type contracts before implementing
Read: contracts/python-protocols.py
```

### For Continuing AI Sessions

**Update Context:**
```
# Check for spec updates since last session
git log --since="last session date" -- docs/plans/thinking-tools/specs/

# Read updated specs
# Update process memory with new understanding
```

---

## Maintenance

**Spec Ownership:**
- Each spec has designated owner (see file header)
- Owners responsible for keeping spec current
- Cross-reference updates when dependencies change

**Review Cadence:**
- Quarterly review of all specs
- Update version numbers as needed
- Sync with implementation reality

**Integration with ADRs:**
- Specs implement decisions from ADRs
- ADR changes → spec updates
- Bidirectional traceability

---

## Tools

**Validation:**
```bash
# Validate all JSON schemas
make validate-schemas

# Check spec format consistency
make lint-specs

# Verify cross-references
make check-spec-links
```

**Generation:**
```bash
# Generate Python protocols from specs
make generate-contracts

# Generate OpenAPI docs from MCP spec
make generate-api-docs
```

**Querying:**
```bash
# Find specs mentioning a topic
grep -r "Jinja2" specs/

# List specs by cornerstone
grep -l "Cornerstone.*Modularity" specs/*
```

---

## Document Status

**Index Version:** 2.0.0
**Last Updated:** 2025-01-15
**Specs Completed:** 27 of 27 ✅ (100%)
**Schemas Completed:** 3 of 4 (75%)
**Contracts Completed:** 1 of 1 ✅ (100%)
**Review Exercises:** 4 of 4 ✅ (100%)
**Operational Guides:** 2 of 2 ✅ (100%)

**Next Steps:**
1. ✅ All specifications complete
2. Memory provisioning (57 files - in progress)
3. Example thinking tools (5-10 YAML specs)
4. Implementation phase
3. Generate Python contracts file
4. Validate all cross-references

---

## Questions & Support

**For Spec Clarifications:**
- Check ADRs: `../04-ARCHITECTURE-DECISION-RECORDS.md`
- Query process memory: `cogito memory query`
- Review architecture: `../02-ARCHITECTURE.md`

**For Implementation Questions:**
- Refer to contracts: `contracts/python-protocols.py`
- Check test specs: `specs/24-TESTING-STRATEGY.md`
- Review examples in spec files

---

**"Modular specifications enable just-in-time learning and precise understanding."**
