# Suggested Commands

## Installation Commands

### Install with dev dependencies
```bash
python3 -m pip install -e ".[dev]"
```

### Install with MCP support
```bash
python3 -m pip install -e ".[mcp]"
```

## Testing Commands

### Run all tests
```bash
pytest
```

### Run tests with coverage report (HTML)
```bash
pytest --cov=cogito --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_renderer.py
```

### Run specific test function
```bash
pytest tests/unit/test_renderer.py::test_render_simple_template
```

## Code Quality Commands

### Type checking (strict mode enabled)
```bash
mypy src/
```

### Linting with ruff
```bash
ruff check src/
```

### Code formatting with black (line length: 100)
```bash
black src/
```

### Validate all thinking tools against schema
```bash
bash scripts/validate.sh
```

### Validate specific directory
```bash
bash scripts/validate.sh examples/metacognition/
```

## Full Validation Suite
Run complete validation (recommended before commits):
```bash
bash scripts/validate.sh && pytest && mypy src/ && ruff check src/
```

## Windows-Specific Utility Commands

Since the system is Windows, use these commands:

### Directory operations
```bash
dir                    # List directory contents
cd <path>              # Change directory
mkdir <name>           # Create directory
```

### File operations
```bash
type <file>            # Display file contents
copy <src> <dest>      # Copy files
del <file>             # Delete file
```

### Search operations
```bash
findstr /s /i "pattern" *.py    # Search for pattern in Python files
dir /s /b *.yml                  # Find all YAML files recursively
```

### Git operations (standard cross-platform)
```bash
git status
git add .
git commit -m "message"
git push
```

## Project-Specific Entry Points

Currently, the project is in bootstrap phase. Once complete, entry points will be:
- CLI tool execution (to be implemented)
- MCP server mode (Layer 5 integration)
