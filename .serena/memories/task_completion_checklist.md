# Task Completion Checklist

## What to Do When a Task is Completed

Before marking any coding task as complete, ensure all of the following are done:

### 1. Code Quality Checks

#### Type Checking (REQUIRED)
```bash
mypy src/
```
**Must pass:** No type errors allowed. Strict mode is enabled.

#### Linting (REQUIRED)
```bash
ruff check src/
```
**Must pass:** All linting rules must be satisfied.

#### Code Formatting (REQUIRED)
```bash
black src/
```
**Must pass:** Code must be formatted with black (line length: 100).

### 2. Testing (REQUIRED for new code)

#### Run all tests
```bash
pytest
```

#### Run tests with coverage
```bash
pytest --cov=cogito --cov-report=html
```
**Target:** Aim for >80% coverage on new code.

### 3. Thinking Tools Validation (if applicable)

If you created or modified any YAML thinking tools:
```bash
bash scripts/validate.sh
```
**Must pass:** All tools must validate against the JSON schema.

### 4. Full Validation Suite (RECOMMENDED)

Run the complete validation before committing:
```bash
bash scripts/validate.sh && pytest && mypy src/ && ruff check src/
```

### 5. Documentation Updates (if applicable)

- Update docstrings for new/modified public functions
- Update README.md if adding new features or categories
- Update CLAUDE.md if changing development workflows
- Consider adding process memory entries for significant decisions

### 6. Architecture Compliance

Verify that changes:
- Respect layer dependencies (no upward dependencies)
- Embody the Five Cornerstones (Configurability, Modularity, Extensibility, Integration, Automation)
- Use parameters instead of hardcoded values
- Include proper type hints and docstrings
- Follow existing patterns and conventions

### 7. Testing Completeness

For new features, ensure:
- Unit tests cover the new code
- Integration tests cover layer interactions (if applicable)
- Edge cases are tested
- Error conditions are tested

### 8. Clean Git State (if committing)

Before committing:
```bash
git status                           # Check what's changed
git add <files>                      # Stage changes
git commit -m "descriptive message"  # Commit with clear message
```

## Summary Command

Use this one-liner for complete validation:
```bash
bash scripts/validate.sh && pytest --cov=cogito && mypy src/ && ruff check src/ && black --check src/
```

If all pass, the task is ready for completion!
