# Code Style and Conventions

## Python Code Style (PEP 8 + Black + strict mypy)

### General Rules
- **Line length:** 100 characters
- **Python version:** 3.11+ (use modern type hints)
- **Type hints:** REQUIRED for all public functions and classes
- **Docstrings:** REQUIRED for all public functions and classes
- **Import order:** standard library → third-party → local
- **Strict typing:** mypy strict mode enabled (`disallow_untyped_defs = true`)

### Function Signature Example
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
```

### Naming Conventions
- **Functions/variables:** snake_case
- **Classes:** PascalCase
- **Constants:** UPPER_SNAKE_CASE
- **Private members:** _leading_underscore
- **Thinking tool files:** snake_case.yml

## YAML Thinking Tools Style

### YAML Formatting
- **Indentation:** 2 spaces (strict)
- **Quotes:** Double quotes for strings (when needed)
- **Format:** Must follow `thinking-tool-v1.0.schema.json` schema
- **Validation:** ALWAYS run `bash scripts/validate.sh` after creating/editing tools

### Thinking Tool Structure
```yaml
version: "1.0"

metadata:
  name: "tool_name"              # snake_case
  display_name: "Tool Name"      # Human readable
  description: "..."
  category: "metacognition"      # From schema enum
  author: "Your Name"
  version: "1.0.0"               # SemVer
  tags: ["tag1", "tag2"]

parameters:
  # Use JSON Schema for type safety
  type: object
  properties:
    param_name:
      type: string
      description: "..."

template: |
  # Jinja2 template with Markdown
  {% if param_name %}
  ...
  {% endif %}
```

## Tool Configuration Files

### pyproject.toml
Contains all project configuration:
- Build system (hatchling)
- Dependencies (main and optional)
- pytest configuration
- mypy strict configuration
- ruff linting rules
- black formatting rules

### Line Length: 100
Enforced across:
- Python code (black)
- Docstrings
- Comments

## Linting Rules (Ruff)
Enabled checks:
- E: pycodestyle errors
- W: pycodestyle warnings
- F: pyflakes
- I: isort (import ordering)
- N: pep8-naming
- UP: pyupgrade (modern Python syntax)
- B: flake8-bugbear (common bugs)
- C4: flake8-comprehensions
- SIM: flake8-simplify

## Type Checking (mypy)
Configuration in pyproject.toml:
- `strict = true`
- `warn_return_any = true`
- `warn_unused_configs = true`
- `disallow_untyped_defs = true`

All public functions MUST have type annotations.

## Testing Conventions

### Test File Structure
```
tests/
├── unit/           # Isolated component tests
├── integration/    # Multi-component/layer interaction tests
└── fixtures/       # Test data and helpers
```

### Test Naming
- Files: `test_*.py`
- Functions: `test_*`
- Coverage target: >80%

### Required Tests
- All new code must include unit tests
- Layer interactions require integration tests
- Thinking tools require schema validation tests
