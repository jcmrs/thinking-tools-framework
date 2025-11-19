# Architecture Patterns and Design Guidelines

## Five-Layer Architecture

**CRITICAL RULE:** Dependencies flow downward only. Higher layers can depend on lower layers, but NEVER the reverse.

### Layer Responsibilities

#### Layer 1: UI (src/cogito/ui/)
- CLI interfaces
- User I/O formatting
- Command-line argument parsing
- Interactive prompts

#### Layer 2: Orchestration (src/cogito/orchestration/)
- Tool discovery (auto-discovery from examples/)
- Execution coordination
- Workflow management
- Plugin system

#### Layer 3: Processing (src/cogito/processing/)
- Jinja2 template rendering
- JSON Schema validation
- Security checks (sandboxed execution)
- Template compilation

#### Layer 4: Storage (src/cogito/storage/)
- Process memory JSONL format
- Caching strategies
- Data persistence
- Configuration storage

#### Layer 5: Integration (src/cogito/integration/)
- MCP protocol implementation
- External tool adapters
- API integrations
- Hot-reload support

## Creating New Thinking Tools

### Step-by-Step Process

1. **Choose category:** metacognition, review, handoff, debugging, planning, learning
2. **Copy template:** Start from similar existing tool in `examples/`
3. **Define metadata:** 
   - name (snake_case)
   - display_name (human readable)
   - description (clear purpose)
   - category (from schema enum)
   - author, version (SemVer), tags
4. **Design parameters:** Use JSON Schema for type safety
5. **Write Jinja2 template:** Combine with Markdown for structured output
6. **Validate:** `bash scripts/validate.sh examples/category/tool.yml`

### Key Patterns

#### Progressive Depth
Single tool with configurable detail level:
```yaml
parameters:
  properties:
    depth:
      type: string
      enum: ["quick", "standard", "detailed"]
```

#### Domain Branching
Conditional sections based on context:
```jinja2
{% if language == 'python' %}
- Check for type hints
- Verify docstrings
{% elif language == 'typescript' %}
- Check for interface definitions
- Verify JSDoc comments
{% endif %}
```

#### Checklists
Explicit, checkable criteria:
```markdown
## Code Quality Checklist
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Tests achieve >80% coverage
```

## Common Workflows

### Adding a New Thinking Tool Category

1. Create directory: `examples/new_category/`
2. Create first tool following YAML schema
3. Validate: `bash scripts/validate.sh examples/new_category/`
4. Update README.md category list
5. Consider adding category to schema enum

### Extending Template Rendering

1. Modify `src/cogito/processing/` (Layer 3)
2. Add unit tests in `tests/unit/`
3. Verify existing tools still validate
4. Update documentation if new Jinja2 features added

### Adding MCP Integration Feature

1. Work in `src/cogito/integration/` (Layer 5)
2. Follow MCP protocol specifications
3. Ensure hot-reload compatibility
4. Test with actual MCP client (e.g., Claude Code)

## Design Principles

### Zero Serena Core Modifications
- Integrate with Serena exclusively through MCP tool interface
- No core changes to Serena required
- Independent installation and updates
- Standard MCP tool interface
- Hot-reload support during development

### Declarative-First Design
- Favor declarative YAML specifications over imperative code
- Enable non-programmers to create tools
- Allow code generation, validation, and analysis
- Align with configurability and automation cornerstones

### Defense-in-Depth Validation
Three sequential layers:
1. **Schema validation:** Structure and types
2. **Semantic validation:** Logic and consistency
3. **Security validation:** Dangerous patterns and injection risks

## What NOT to Do

❌ **Don't violate layer dependencies** - No upward dependencies allowed
❌ **Don't add hardcoded values** - Use parameters instead
❌ **Don't skip validation** - Always run `bash scripts/validate.sh`
❌ **Don't create tools without testing** - Test on real use cases
❌ **Don't modify thinking tools without validating** - Against schema
❌ **Don't bypass type checking** - All public functions need type hints
❌ **Don't skip docstrings** - All public functions need documentation
