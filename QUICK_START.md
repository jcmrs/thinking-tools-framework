# Thinking Tools Framework - Quick Start Guide

**Goal:** Understand and use the framework in under 5 minutes.

---

## What You'll Learn

1. What thinking tools are and why they matter
2. How to use existing thinking tools
3. How to create your own thinking tool
4. How the framework integrates with AI assistants

---

## 1. Understanding Thinking Tools (60 seconds)

**Thinking tools = Structured prompts that make reasoning explicit**

Instead of asking: "Review this code"
Use a thinking tool: `code_review_checklist` with explicit criteria for:
- Code quality
- Security
- Performance
- Five Cornerstones compliance

**Key Insight:** Explicit structure → Better consistency + Higher quality

---

## 2. Using an Existing Tool (90 seconds)

### Example: Code Review Checklist

**File:** `examples/review/code_review_checklist.yml`

**Parameters:**
- `review_type`: self | peer | pre_commit | architecture
- `language`: python | javascript | go | rust | etc.
- `change_description`: What changed

**Output:** Comprehensive checklist covering:
- Correctness, readability, maintainability
- Security vulnerabilities
- Performance considerations
- Five Cornerstones compliance
- Language-specific concerns

**When to use:** Before committing code, during PR reviews, architecture changes

---

### Example: Session Handover

**File:** `examples/handoff/session_handover.yml`

**Purpose:** Preserve complete context for next AI session (zero information loss)

**Parameters:**
- `completeness`: minimal | standard | comprehensive
- `reason`: session_end | context_limit | checkpoint | blocked

**Output:** Structured handover document with:
- What was accomplished
- What's in progress
- Blockers and decisions
- Context and priorities
- Resume strategies

**When to use:** End of work session, before context window limit, when switching tasks

---

## 3. Exploring Categories (30 seconds)

**Metacognition** (`examples/metacognition/`)
- Thinking about thinking
- Surface assumptions, verbalize reasoning
- Tools: think_aloud, assumption_check, fresh_eyes_exercise

**Review** (`examples/review/`)
- Systematic quality assessment
- Code and architecture evaluation
- Tools: code_review_checklist, architecture_review

**Handoff** (`examples/handoff/`)
- Context preservation
- AI session continuity
- Tools: session_handover, context_preservation

**Debugging** (`examples/debugging/`)
- Root cause analysis
- Error investigation
- Tools: five_whys, error_analysis

---

## 4. Creating Your First Tool (90 seconds)

**Step 1:** Copy a template (use `think_aloud.yml` as base)

**Step 2:** Modify metadata
```yaml
metadata:
  name: "my_analysis"
  display_name: "My Analysis Tool"
  description: "Helps me analyze X"
  category: "metacognition"
```

**Step 3:** Define parameters
```yaml
parameters:
  type: "object"
  properties:
    depth:
      type: "string"
      enum: ["quick", "detailed"]
      default: "quick"
```

**Step 4:** Write template (Jinja2 + Markdown)
```yaml
template:
  source: |
    # My Analysis - {{ depth|upper }}

    {% if depth == 'quick' %}
    ## Quick Check
    - Key question: [What to analyze]
    - Answer: [Analysis result]
    {% else %}
    ## Detailed Analysis
    [More comprehensive structure]
    {% endif %}
```

**Step 5:** Validate
```bash
bash scripts/validate.sh examples/metacognition/
```

---

## 5. Framework Integration (30 seconds)

### With Serena MCP (Claude Code)

The framework integrates as an MCP server:

1. **Zero Serena modifications** - Install independently
2. **Auto-discovery** - Tools found automatically in `examples/`
3. **Hot-reload** - Edit tools, changes apply immediately
4. **Standard interface** - Same MCP protocol as other tools

### Standalone Usage

```python
from cogito.orchestration import ToolRegistry
from cogito.processing import TemplateRenderer

# Load tool
registry = ToolRegistry()
tool = registry.get_tool("code_review_checklist")

# Render with parameters
renderer = TemplateRenderer()
result = renderer.render(tool, {
    "review_type": "self",
    "language": "python",
    "change_description": "Added input validation"
})

print(result)
```

---

## 6. Key Concepts (60 seconds)

### Five Cornerstones

Every tool embodies these principles:

1. **Configurability** - Parameters, not hardcoded values
2. **Modularity** - Single responsibility, composable
3. **Extensibility** - Plugin architecture
4. **Integration** - Standard protocols (MCP)
5. **Automation** - Auto-discovery, validation

### AI-First Design

**Machine-readable formats** (YAML, JSON)
+ **Self-documenting** (metadata, examples)
+ **Context preservation** (process memory)
+ **No hidden state** (explicit parameters)
= **Effective AI-human collaboration**

### Process Memory

**52 entries** documenting design decisions, lessons learned, assumptions.

- **Why this matters:** New AI instances can establish context in <5 minutes
- **Where to find:** `.bootstrap/session_context.md`
- **How to use:** Read at session start for framework understanding

---

## Next Steps

### Learn More
1. **Read examples** - Best way to learn patterns
2. **Check specs** - `docs/specs/` for complete technical detail
3. **Explore process memory** - `.bootstrap/session_context.md`

### Create Tools
1. **Copy example** - Start with similar existing tool
2. **Modify gradually** - Change one thing at a time
3. **Validate often** - `bash scripts/validate.sh`

### Integrate
1. **With Serena** - Follow MCP integration guide
2. **Standalone** - Import cogito package
3. **Custom workflows** - Combine multiple tools

---

## Common Patterns

### Progressive Depth
Single tool, multiple depth levels (quick/standard/detailed)
- **Example:** think_aloud, session_handover
- **Benefit:** Less tool proliferation

### Domain-Specific Branching
Conditional sections based on parameters
- **Example:** error_analysis (runtime/logic/performance)
- **Benefit:** Unified structure, specialized content

### Checklists
Explicit, checkable criteria for thoroughness
- **Example:** code_review_checklist, architecture_review
- **Benefit:** Nothing missed, consistent quality

---

## Troubleshooting

**Tool not loading?**
→ Check YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('tool.yml'))"`

**Validation failing?**
→ Run: `bash scripts/validate.sh path/to/tool.yml`

**Template not rendering?**
→ Check Jinja2 syntax, ensure parameters exist in YAML

**Need help?**
→ Check docs/, examine similar example, read process memory

---

## Summary

**5 Minutes:**
1. ✅ Understand what thinking tools are
2. ✅ Know when to use which tool
3. ✅ Can create a basic tool
4. ✅ Understand framework integration
5. ✅ Know where to find more info

**You're ready to use thinking tools!**

Explore `examples/`, create your own, and make your development process more systematic.
