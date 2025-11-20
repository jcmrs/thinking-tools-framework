# Process Memory Usage Guide

## What is Process Memory?

Process Memory is an append-only, machine-readable decision log that captures key moments, decisions, learnings, and architectural changes during software development. It implements the **Information-Memory-Graph paradigm**: "Everything is information → memory → graph."

**Key Characteristics:**
- **Append-only JSONL format**: Each line is a self-contained JSON entry
- **Machine-readable**: Structured data for AI comprehension and querying
- **Graph-enabled**: Entries link to each other, creating a knowledge graph of relationships
- **Temporal**: Timestamped entries preserve development history

**Reference**: See [docs/PARADIGM-INFORMATION-MEMORY-GRAPH.md](PARADIGM-INFORMATION-MEMORY-GRAPH.md) for the underlying philosophy.

## When to Create Entries

Create Process Memory entries at these key moments:

### 1. **Completion of Major Milestones**
- Priority or phase completions
- Feature implementation complete
- Architectural layer implementations

**Example**: Priority 5 completion (Python Contracts/Protocols defined)

### 2. **Architectural Decisions**
- Technology choices (e.g., "Why Protocol over ABC?")
- Design pattern selections
- Layer boundary definitions

**Example**: Paradigm discovery (Information-Memory-Graph)

### 3. **Lessons Learned**
- Problem-solving insights
- Performance optimizations
- Testing strategies that worked/failed

**Example**: Jinja2 whitespace issues in YAML templates

### 4. **Research Findings**
- Technical investigations
- Validation of hypotheses
- External research synthesis

**Example**: Perplexity AI research on token economics

### 5. **Gap Identifications**
- Missing functionality discovered
- Technical debt identified
- Architectural gaps

**Example**: Technical specifications not generated (backlog item)

## Entry Schema

### Required Fields

```json
{
  "id": "unique-identifier-2025-11-20",
  "timestamp": "2025-11-20T12:00:00Z",
  "type": "completion | decision | learning | research | gap",
  "category": "milestone | architecture | optimization | analysis",
  "title": "Concise entry title",
  "summary": "1-2 sentence summary of the entry",
  "links": ["related-entry-1", "related-entry-2"],
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Optional Fields

```json
{
  "details": {
    "deliverables": ["Item 1", "Item 2"],
    "quality_gates": "100%",
    "custom_field": "Any additional structured data"
  },
  "metadata": {
    "commit_sha": "abc123",
    "impact": "Description of impact",
    "session_duration": "2 hours"
  }
}
```

## Entry Schema Explained

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier (use kebab-case with date) | `priority5-contracts-protocols-completion` |
| `timestamp` | string | ISO 8601 timestamp (UTC) | `2025-11-20T12:00:00Z` |
| `type` | string | Entry category | `completion`, `decision`, `learning`, `research`, `gap` |
| `category` | string | Subcategory for organization | `milestone`, `architecture`, `optimization` |
| `title` | string | Concise, descriptive title | `Priority 5: Python Contracts/Protocols - COMPLETE` |
| `summary` | string | 1-2 sentence overview | Brief description of what happened |
| `links` | array | IDs of related entries (creates graph) | `["priority4-completion", "paradigm-entry"]` |
| `tags` | array | Keywords for search | `["priority5", "protocols", "architecture"]` |
| `details` | object | Optional structured details | Deliverables, metrics, custom data |
| `metadata` | object | Optional metadata | Git commit, duration, impact assessment |

## Practical Examples from Actual Entries

### Example 1: Priority Completion

```json
{
  "id": "priority5-contracts-protocols-completion",
  "timestamp": "2025-11-19T22:30:00Z",
  "type": "completion",
  "category": "priority-milestone",
  "title": "Priority 5: Python Contracts/Protocols - COMPLETE",
  "summary": "Defined 8 Protocol definitions for five-layer architecture. Enforces layer boundaries via type system. All quality gates passed (486 tests, mypy 0 errors, ruff 0 violations).",
  "details": {
    "deliverables": [
      "layer_protocols.py (8 protocols, 357 lines)",
      "README.md (~1500 words)",
      "test_contracts.py (35 tests)",
      "__init__.py (exports all protocols)"
    ],
    "quality_gates": "100%",
    "protocols_defined": [
      "OrchestrationProtocol (ToolExecutor)",
      "ToolRegistryProtocol (ToolRegistry)",
      "ProcessingProtocol (TemplateRenderer)",
      "ValidationProtocol (ParameterValidator)",
      "SchemaValidationProtocol (SchemaValidator)",
      "StorageProtocol (ProcessMemoryStore)",
      "KnowledgeGraphProtocol (KnowledgeGraph)",
      "IntegrationProtocol (MCPServer)",
      "UIProtocol (CLI)"
    ]
  },
  "links": [
    "priority4-core-components-completion",
    "paradigm-information-memory-graph-2025-11-19",
    "knowledge-graph-protocol",
    "imperative-3-modularity"
  ],
  "tags": ["priority5", "completion", "contracts", "protocols", "architecture", "type-safety"],
  "metadata": {
    "quality_gates": "100%",
    "session_duration": "210 minutes",
    "commit_sha": "db78a1b",
    "impact": "Layer boundaries now enforceable by type system"
  }
}
```

### Example 2: Paradigm Discovery

```json
{
  "id": "paradigm-information-memory-graph-2025-11-19",
  "timestamp": "2025-11-19T20:51:10.569721Z",
  "type": "foundational-paradigm",
  "category": "architecture-philosophy",
  "title": "The Information-Memory-Graph Paradigm (User-Coined)",
  "summary": "User coined paradigm: Everything is information → memory → graph. AI instance independently discovered implementation (KnowledgeGraphProtocol). Rare convergence of human philosophical insight and AI architectural reasoning.",
  "details": {
    "paradigm_statement": "Everything is information, so everything is memory, and as everything is memory, everything is a graph",
    "coined_by": "User",
    "discovered_by": "thinking-tools-framework AI instance (Priority 5)",
    "convergence_date": "2025-11-19",
    "significance": "AI identified both Idea (relationships matter) AND Concept (graph structure optimal) autonomously"
  },
  "links": [
    "priority5-completion",
    "knowledge-graph-protocol",
    "storage-protocol",
    "imperative-1-holistic-thinking",
    "imperative-2-ai-first"
  ],
  "tags": ["paradigm", "architecture", "philosophy", "knowledge-graph", "ai-discovery", "foundational"],
  "metadata": {
    "priority": "foundational",
    "impact": "project-defining",
    "validation": "implementation-exists"
  }
}
```

## Knowledge Graph Traversal

Process Memory entries create a **knowledge graph** through their `links` field. This enables:
- **Forward traversal**: Find entries this entry depends on
- **Reverse traversal**: Find entries that depend on this entry
- **Deep traversal**: Multi-hop relationship discovery

### Building the Graph

```python
from pathlib import Path
from cogito.storage.knowledge_graph import KnowledgeGraph
from cogito.storage.process_memory import ProcessMemoryStore

# Load process memory and build graph
store = ProcessMemoryStore(Path("data/process_memory.jsonl"))
graph = KnowledgeGraph(store)
graph.build_graph()
```

### Query Examples

**Forward traversal (what does this entry link to?)**:
```python
related = graph.get_related("priority5-contracts-protocols-completion")
# Returns: [paradigm-entry, priority4-completion, ...]
```

**Reverse traversal (what links to this entry?)**:
```python
references = graph.get_related(
    "paradigm-information-memory-graph-2025-11-19",
    include_reverse=True
)
# Returns: [priority5-completion, priority4-completion, ...]
```

**Deep traversal (multi-hop relationships)**:
```python
deep = graph.get_related("priority3-thinking-tools-completion", depth=2)
# Returns all entries within 2 hops
```

### Paradigm Validation Example

The graph queries demonstrate the Information-Memory-Graph paradigm:

```python
# What led to Priority 5?
related = graph.get_related("priority5-contracts-protocols-completion")
# Found 2 related entries:
#   - paradigm-information-memory-graph-2025-11-19
#   - priority4-core-components-completion

# What references the paradigm?
references = graph.get_related(
    "paradigm-information-memory-graph-2025-11-19",
    include_reverse=True
)
# Found 4 entries (forward + reverse links):
#   - priority2-process-memory-completion
#   - priority5-contracts-protocols-completion
#   - priority4-core-components-completion
```

## Integration with MCP Server

The MCP server exposes Process Memory through tools for AI agents:

### Available MCP Tools

- **`query_process_memory`**: Search entries by ID, keyword, category, or tags
- **`query_knowledge_graph`**: Find related entries, dependencies, concepts

### Usage from Claude Code

```
User: "What architectural decisions led to the current storage layer?"

Claude uses: query_knowledge_graph(entry_id="storage-protocol")
Returns: Graph of related entries showing design evolution
```

## Best Practices

### 1. **Write Entries Immediately**
Don't wait - capture decisions and learnings as they happen. Context fades quickly.

### 2. **Be Specific in Summaries**
Good: "Defined 8 Protocol definitions for five-layer architecture. Enforces layer boundaries via type system."

Bad: "Implemented protocols."

### 3. **Create Meaningful Links**
Links should represent real relationships:
- **Depends on**: Priority 5 links to Priority 4 (built on its foundation)
- **References**: Paradigm entry linked from implementations
- **Related to**: Imperative compliance links to relevant entries

### 4. **Use Consistent ID Patterns**
- Completions: `priority{N}-{name}-completion`
- Decisions: `decision-{topic}-{date}`
- Learnings: `learning-{topic}-{date}`
- Research: `research-{topic}-{date}`

### 5. **Tag Strategically**
Tags enable search - use them well:
- **Priority/phase**: `priority1`, `priority2`, ...
- **Component**: `contracts`, `storage`, `mcp`, ...
- **Type**: `completion`, `architecture`, `optimization`, ...
- **Impact**: `foundational`, `breaking-change`, `bugfix`, ...

### 6. **Include Quality Metrics**
For completions, always document:
- Test pass rates
- Coverage percentages
- Lint/type-check results
- Git commit SHA

### 7. **Reference External Sources**
For research entries, cite sources:
```json
"metadata": {
  "sources": [
    "https://docs.claude.com/en/api/rate-limits",
    "Academic paper: arxiv.org/2401.00588"
  ]
}
```

## Appending Entries

### Manual Append (Python)

```python
import json
from datetime import datetime, timezone

entry = {
    "id": "my-decision-2025-11-20",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "type": "decision",
    "category": "architecture",
    "title": "Chose Protocol over ABC for Contracts",
    "summary": "Structural typing allows non-breaking retrofitting to existing classes.",
    "links": ["priority5-contracts-protocols-completion"],
    "tags": ["decision", "architecture", "protocols"]
}

with open("data/process_memory.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
```

### Via ProcessMemoryStore

```python
from pathlib import Path
from cogito.storage.process_memory import ProcessMemoryStore

store = ProcessMemoryStore(Path("data/process_memory.jsonl"))
store.append_entry(entry)  # Same entry dict as above
```

## Querying Entries

### Search by Type/Category

```python
completions = store.search_entries(type="completion")
architectural_decisions = store.search_entries(category="architecture")
```

### Search by Tags

```python
foundation_work = store.search_entries(tags=["foundation"])
priority5_items = store.search_entries(tags=["priority5"])
```

### Get Specific Entry

```python
entry = store.get_entry("priority5-contracts-protocols-completion")
print(entry["summary"])
```

## Maintenance

### Deprecating Entries

If an entry becomes obsolete, mark it as deprecated (don't delete):
```json
{
  "id": "old-approach-2025-11-15",
  "deprecated": true,
  "deprecated_reason": "Replaced by new-approach-2025-11-20",
  ...
}
```

### Rebuilding the Graph

After significant PM updates:
```python
graph = KnowledgeGraph(store)
graph.build_graph()  # Rebuilds from all current entries
```

## Integration Examples

### During Development

**Scenario**: Just completed a major refactoring.

```python
entry = {
    "id": "refactor-cli-layer-2025-11-20",
    "timestamp": "2025-11-20T15:30:00Z",
    "type": "completion",
    "category": "refactoring",
    "title": "CLI Layer Refactored to Use Protocols",
    "summary": "Refactored CLI to depend on OrchestrationProtocol instead of concrete ToolExecutor class. Improves testability and maintains SRP.",
    "details": {
        "files_modified": ["src/cogito/ui/cli.py"],
        "test_impact": "15 tests updated",
        "quality_gates": "100%"
    },
    "links": ["priority5-contracts-protocols-completion", "priority7-cli-refactoring"],
    "tags": ["refactoring", "cli", "protocols", "priority7"],
    "metadata": {
        "commit_sha": "xyz789",
        "impact": "Reduced coupling, improved testability"
    }
}

store.append_entry(entry)
```

### For Fresh AI Sessions

New AI instance queries PM for context:
```python
# Get all priority completions
priorities = store.search_entries(category="priority-milestone")

# Understand foundation work
foundation = store.search_entries(tags=["foundation"])

# See what depends on paradigm
graph = KnowledgeGraph(store)
graph.build_graph()
paradigm_refs = graph.get_related(
    "paradigm-information-memory-graph-2025-11-19",
    include_reverse=True
)
```

## Summary

Process Memory is your project's **living knowledge base**:
- **Captures** decisions, learnings, and milestones
- **Connects** entries through a knowledge graph
- **Enables** AI comprehension and context preservation
- **Validates** the Information-Memory-Graph paradigm

By consistently documenting in Process Memory, you create a rich, queryable history that helps both human developers and AI agents understand the evolution and rationale of your codebase.

**Start using Process Memory today** - your future self (and AI collaborators) will thank you.
