# Contributing to Thinking Tools Framework

Thank you for your interest in contributing! This document provides guidelines for contributing thinking tools, code improvements, and documentation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Creating Thinking Tools](#creating-thinking-tools)
- [Code Contributions](#code-contributions)
- [Documentation](#documentation)
- [Testing](#testing)
- [Style Guidelines](#style-guidelines)

---

## Code of Conduct

### Our Principles

- **AI-First:** Humans as strategic partners, AI as implementation collaborators
- **Five Cornerstones:** All contributions embody Configurability, Modularity, Extensibility, Integration, Automation
- **Context Preservation:** Document decisions, rationale, and lessons learned
- **Quality Over Quantity:** Better to have 9 excellent tools than 90 mediocre ones

### Expected Behavior

- Be respectful and constructive
- Focus on what's best for the framework
- Document your reasoning (capture process memory)
- Test thoroughly before submitting
- Follow existing patterns and conventions

---

## How to Contribute

### Small Contributions

- **Bug fixes:** Submit a PR with test demonstrating the fix
- **Documentation improvements:** Typos, clarifications, examples
- **Validation improvements:** Better error messages, additional checks

### Medium Contributions

- **New thinking tools:** Follow the creation guide below
- **Framework enhancements:** Improve existing layers
- **Integration improvements:** Better MCP integration, new protocols

### Large Contributions

- **New framework features:** Discuss in issue first
- **Architecture changes:** Requires design discussion
- **New layers or subsystems:** ADR required

**General Process:**
1. Open an issue to discuss (for medium/large contributions)
2. Fork the repository
3. Create a feature branch
4. Make changes following guidelines
5. Add tests
6. Update documentation
7. Submit pull request

---

## Creating Thinking Tools

### Quick Checklist

- [ ] Follows YAML specification (v1.0)
- [ ] Includes complete metadata
- [ ] Parameters use JSON Schema
- [ ] Template uses Jinja2 (safe subset)
- [ ] Validates against schema
- [ ] Includes usage examples in comments
- [ ] Embodies Five Cornerstones
- [ ] Passes validation: `bash scripts/validate.sh`

### Step-by-Step Guide

**1. Choose a Category**

- `metacognition/` - Thinking about thinking
- `review/` - Quality assessment
- `handoff/` - Context preservation
- `debugging/` - Problem diagnosis
- `planning/` - Design and architecture
- `learning/` - Knowledge extraction

**2. Copy a Template**

Start with a similar existing tool:
```bash
cp examples/metacognition/think_aloud.yml examples/metacognition/my_tool.yml
```

**3. Define Metadata**

```yaml
version: "1.0"

metadata:
  name: "my_tool"                    # Snake_case, unique
  display_name: "My Thinking Tool"   # Human-readable
  description: "Brief description"   # What problem it solves
  category: "metacognition"          # One of the categories
  author: "Your Name"
  tags: ["tag1", "tag2", "tag3"]     # Searchable keywords
```

**4. Design Parameters**

Use JSON Schema for type safety:
```yaml
parameters:
  type: "object"
  properties:
    depth:
      type: "string"
      description: "Analysis depth"
      enum: ["quick", "standard", "detailed"]
      default: "standard"
    focus:
      type: "string"
      description: "Aspect to focus on"
  required: ["focus"]  # Optional: required parameters
```

**5. Write Template**

Use Jinja2 + Markdown:
```yaml
template:
  source: |
    # {{ display_name }} - {{ depth|upper }}

    **Focus:** {{ focus }}

    {% if depth == 'quick' %}
    ## Quick Analysis
    - Core question: ...
    - Key insight: ...
    {% else %}
    ## Detailed Analysis
    ### Context
    ...

    ### Analysis
    ...
    {% endif %}
```

**6. Add Usage Examples (Comments)**

```yaml
# Usage Examples:
# - Quick security review: depth=quick, focus=security
# - Detailed architecture: depth=detailed, focus=scalability
```

**7. Validate**

```bash
bash scripts/validate.sh examples/metacognition/my_tool.yml
```

**8. Test with Real Use Case**

Use your tool on an actual problem to ensure it's practical.

### Design Principles for Tools

**Progressive Depth**
- Support quick/standard/detailed variants via parameter
- Don't create separate tools for each depth level

**Domain-Specific Branching**
- Use conditional sections for different contexts
- Example: `{% if language == 'python' %}...{% endif %}`

**Explicit Structure**
- Tables, checklists, numbered steps
- Makes output scannable and actionable

**Reflection Questions**
- Prompt deeper thinking
- "What assumptions am I making?"
- "What would I do differently next time?"

**Meta-Analysis**
- Evaluate the analysis itself
- "Was this thorough enough?"
- "Did I miss anything?"

---

## Code Contributions

### Architecture Layers

When modifying code, respect the five-layer architecture:

**Layer 1: UI**
- CLI interfaces
- User interaction
- Input/output formatting

**Layer 2: Orchestration**
- Tool discovery and loading
- Execution coordination
- Workflow management

**Layer 3: Processing**
- Template rendering
- Validation (schema, semantic, security)
- Parameter handling

**Layer 4: Storage**
- Process memory management
- Caching
- Persistence

**Layer 5: Integration**
- MCP server implementation
- External tool integration
- Protocol adapters

**Rules:**
- Dependencies flow downward only
- Each layer has single responsibility
- No direct Layer 1 → Layer 4 communication

### Adding Features

**Before coding:**
1. Check if it fits Five Cornerstones
2. Consider where in architecture it belongs
3. Think about testing and validation
4. Document your design decisions

**During development:**
1. Write tests first (TDD encouraged)
2. Keep functions focused (single responsibility)
3. Use type hints (Python 3.11+ style)
4. Document with docstrings

**Before submitting:**
1. All tests pass: `pytest`
2. Type checking clean: `mypy src/`
3. Linting clean: `ruff check src/`
4. Format with: `black src/`

---

## Documentation

### What to Document

**Code:**
- Docstrings for all public functions/classes
- Type hints for all parameters and returns
- Inline comments for complex logic only

**Thinking Tools:**
- Usage examples in YAML comments
- Parameter descriptions
- When to use this tool

**Architecture:**
- ADRs for significant decisions
- Update specs when behavior changes
- Capture lessons learned in process memory

### Documentation Style

- **Be concise** - Prefer clarity over verbosity
- **Show examples** - One example worth 1000 words
- **Explain why** - Rationale more important than what
- **Update inline** - Documentation next to code

---

## Testing

### Test Requirements

**All code changes must include tests:**
- Unit tests for new functions/classes
- Integration tests for layer interactions
- Validation tests for thinking tools

**Test Organization:**
```
tests/
├── unit/           # Isolated component tests
├── integration/    # Multi-component tests
└── fixtures/       # Test data and helpers
```

### Writing Tests

```python
import pytest
from cogito.processing import TemplateRenderer

def test_render_simple_template():
    """Test basic template rendering"""
    renderer = TemplateRenderer()
    template = "Hello {{ name }}"
    result = renderer.render_string(template, {"name": "World"})
    assert result == "Hello World"

def test_render_with_invalid_syntax():
    """Test error handling for invalid Jinja2"""
    renderer = TemplateRenderer()
    template = "{{ unclosed"
    with pytest.raises(TemplateSyntaxError):
        renderer.render_string(template, {})
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_renderer.py

# With coverage
pytest --cov=cogito --cov-report=html

# Specific test
pytest tests/unit/test_renderer.py::test_render_simple_template
```

---

## Style Guidelines

### Python Code

**Follow PEP 8 + Black formatting:**
- Line length: 100 characters
- Imports: standard → third-party → local
- Type hints: Required for all public functions
- Docstrings: Required for all public functions/classes

**Example:**
```python
from typing import Dict, Any
from pathlib import Path

def load_tool(tool_path: Path) -> Dict[str, Any]:
    """Load thinking tool from YAML file.

    Args:
        tool_path: Path to the YAML tool specification

    Returns:
        Parsed tool data as dictionary

    Raises:
        FileNotFoundError: If tool file doesn't exist
        ValidationError: If tool doesn't match schema
    """
    # Implementation...
```

### YAML Thinking Tools

**Consistent formatting:**
- 2-space indentation
- Double quotes for strings (when needed)
- Comments use `#` with space after
- Blank line between major sections

**Example:**
```yaml
version: "1.0"

metadata:
  name: "tool_name"
  display_name: "Tool Display Name"
  description: "What this tool does"
  category: "category"
  author: "Author Name"
  tags: ["tag1", "tag2"]

parameters:
  type: "object"
  properties:
    param1:
      type: "string"
      description: "What this parameter controls"
      default: "value"

template:
  source: |
    # Template content here
```

### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change, no feature/fix
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```
feat(tools): Add decision matrix thinking tool

Created new metacognition tool for systematic decision-making.
Uses weighted criteria and scoring matrix.

Closes #42
```

---

## Pull Request Process

### Before Submitting

1. **Fork and branch**
   ```bash
   git checkout -b feat/my-feature
   ```

2. **Make changes**
   - Follow guidelines above
   - Write tests
   - Update documentation

3. **Test locally**
   ```bash
   pytest
   mypy src/
   ruff check src/
   bash scripts/validate.sh
   ```

4. **Commit with good messages**
   ```bash
   git commit -m "feat(scope): Description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feat/my-feature
   ```

### Submitting PR

**PR Description Template:**
```markdown
## Summary
Brief description of what this PR does

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes
- Bullet list of specific changes
- Be thorough but concise

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Follows style guidelines
- [ ] All tests passing
- [ ] Commits are clean
```

### Review Process

1. **Automated checks** must pass
2. **Maintainer review** for code quality
3. **Discussion** if needed
4. **Approval** when ready
5. **Merge** by maintainer

---

## Questions?

- **General questions:** Open a discussion
- **Bug reports:** Open an issue
- **Feature requests:** Open an issue with proposal
- **Quick help:** Check docs/ and examples/

Thank you for contributing to Thinking Tools Framework!
