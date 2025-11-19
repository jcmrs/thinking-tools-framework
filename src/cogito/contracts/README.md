# Contracts Layer: Python Protocols for Architectural Boundaries

This directory contains Protocol definitions that enforce the five-layer architecture through Python's type system.

## What are Python Protocols?

Python Protocols (PEP 544) provide **structural typing** (duck typing with types). Unlike Abstract Base Classes (ABCs), Protocols don't require explicit inheritance. A class conforms to a Protocol if it implements the required methods with matching signatures.

### Why Protocols, not ABCs?

**Protocols** = Structural typing (duck typing with types)
**ABCs** = Nominal typing (requires explicit inheritance)

We use Protocols because:
1. **Non-breaking**: Retrofitting existing code doesn't require changing class hierarchies
2. **Loose coupling**: Depend on interfaces, not implementations
3. **Type safety**: mypy validates Protocol conformance at compile-time
4. **Runtime checks**: `@runtime_checkable` enables `isinstance()` checks
5. **Documentation**: Protocols serve as formal interface contracts

## Five-Layer Architecture Contracts

The thinking-tools framework follows a strict five-layer architecture:

```
Layer 1: UI (Command-Line Interfaces)
   ↓
Layer 2: Orchestration (Tool Discovery & Execution)
   ↓
Layer 3: Processing (Template Rendering & Validation)
   ↓
Layer 4: Storage (Process Memory & Knowledge Graph)
   ↑
Layer 5: Integration (MCP Server & External Integrations)
```

**Dependency Rule**: Dependencies flow downward only (except Layer 5, which can access Storage).

### Layer 1: UIProtocol

**Purpose**: Command-line interface contract
**Implementations**: CLI commands in `src/cogito/ui/cli.py`
**Used by**: External invocation (command line)

**Key Methods**:
- `execute_command(args: list[str]) -> int`: Execute CLI command
- `list_available_tools(orchestrator, category)`: List tools via orchestration layer
- `execute_tool_by_name(orchestrator, tool_name, parameters)`: Execute tool

**Architectural Constraint**: UI layer depends on `OrchestrationProtocol`, not concrete orchestration classes.

### Layer 2: OrchestrationProtocol

**Purpose**: Tool execution and registry contract
**Implementations**: `ToolExecutor`, `ToolRegistry` in `src/cogito/orchestration/`
**Used by**: UI layer (`cli.py`)

**Key Methods**:
- `execute(tool_spec, parameters) -> str`: Execute tool with spec
- `execute_by_name(tool_name, registry, parameters) -> str`: Execute tool by name
- `discover_tools(scan_dirs) -> int`: Auto-discover tools from directories
- `load_tool(tool_path) -> dict`: Load single tool from YAML
- `get_tool(tool_name) -> dict | None`: Retrieve tool from registry
- `list_tools() -> list[str]`: List all tool names

**Architectural Constraint**: Orchestration layer depends on `ProcessingProtocol`, not concrete processing classes.

### Layer 3: ProcessingProtocol

**Purpose**: Rendering and validation contract
**Implementations**: `TemplateRenderer`, `ParameterValidator`, `SchemaValidator` in `src/cogito/processing/`
**Used by**: Orchestration layer (`executor.py`)

**Key Methods**:
- `render(tool_spec, parameters) -> str`: Render Jinja2 template
- `validate_template_syntax(template_source) -> bool`: Validate template syntax
- `validate_parameters(tool_spec, parameters) -> dict`: Validate & apply defaults
- `validate_tool_spec(tool_spec) -> dict`: Multi-layer spec validation

**Architectural Constraint**: Processing layer has no upward dependencies (pure logic layer).

### Layer 4: StorageProtocol

**Purpose**: Process memory and knowledge graph contract
**Implementations**: `ProcessMemoryStore`, `KnowledgeGraph` in `src/cogito/storage/`
**Used by**: All layers for persistent storage

**Key Methods**:
- `append_entry(entry)`: Append process memory entry
- `get_entry(entry_id) -> dict | None`: Retrieve entry by ID
- `search_entries(keyword, category, tags) -> list`: Search entries
- `build_graph()`: Build knowledge graph from memory
- `get_related(entry_id, depth, include_reverse) -> list`: Graph traversal

**Architectural Constraint**: Storage layer has no dependencies on other cogito layers.

### Layer 5: IntegrationProtocol

**Purpose**: MCP server contract
**Implementations**: `MCPServer` in `src/cogito/integration/mcp_server.py`
**Used by**: External clients via MCP protocol

**Key Methods**:
- `execute_thinking_tool(tool_name, parameters) -> str`: Execute tool via MCP
- `list_thinking_tools(category) -> list`: List tools via MCP
- `query_process_memory(entry_id, keyword, category, tags) -> str`: Query memory via MCP

**Architectural Constraint**: Integration layer can access Storage layer but not UI/Orchestration/Processing.

## How to Use Protocols

### Type Hints (Compile-Time Type Safety)

Use Protocols in type hints to depend on interfaces, not implementations:

```python
from cogito.contracts.layer_protocols import OrchestrationProtocol

def run_analysis(orchestrator: OrchestrationProtocol, tool_name: str) -> str:
    """Run analysis with any orchestrator conforming to protocol."""
    return orchestrator.execute_by_name(tool_name, orchestrator, {})
```

**mypy** validates that:
1. The passed object has all required methods
2. Method signatures match the protocol
3. Return types are compatible

### Runtime Checks (isinstance)

All protocols use `@runtime_checkable`, enabling runtime validation:

```python
from cogito.contracts.layer_protocols import OrchestrationProtocol
from cogito.orchestration.executor import ToolExecutor

executor = ToolExecutor()

if isinstance(executor, OrchestrationProtocol):
    result = executor.execute(tool_spec, params)
```

### Dependency Injection

Protocols enable dependency injection with loose coupling:

```python
class CLI:
    def __init__(self, orchestrator: OrchestrationProtocol):
        self.orchestrator = orchestrator  # Depends on interface, not implementation

    def list_tools(self) -> None:
        tools = self.orchestrator.list_tools()
        for tool in tools:
            print(tool)
```

## Architectural Boundaries Enforced

Protocols prevent common architectural violations:

### ❌ Before Protocols (Tight Coupling)

```python
# cli.py - Direct import violates layer boundaries
from cogito.orchestration.executor import ToolExecutor

def run_tool(tool_name: str):
    executor = ToolExecutor()  # Tight coupling to concrete class
    executor.execute_by_name(tool_name, ...)
```

**Problems**:
- Tight coupling to implementation
- Layer violation not caught by type checker
- Harder to test (can't mock easily)

### ✅ After Protocols (Loose Coupling)

```python
# cli.py - Protocol import enables loose coupling
from cogito.contracts.layer_protocols import OrchestrationProtocol

def run_tool(orchestrator: OrchestrationProtocol, tool_name: str):
    orchestrator.execute_by_name(tool_name, ...)  # Works with any implementation
```

**Benefits**:
- Loose coupling to interface
- Type safety via mypy
- Easy to test (mock Protocol implementations)
- Layer boundaries visible and enforceable

## Examples from Existing Code

### Example 1: ToolExecutor conforms to OrchestrationProtocol

`ToolExecutor` in `src/cogito/orchestration/executor.py` implements all methods required by `OrchestrationProtocol`:

```python
class ToolExecutor:
    def execute(
        self,
        tool_spec: dict[str, Any],
        parameters: dict[str, Any] | None = None,
    ) -> str:
        # Implementation...
        pass

    def execute_by_name(
        self,
        tool_name: str,
        tool_registry: Any,
        parameters: dict[str, Any] | None = None,
    ) -> str:
        # Implementation...
        pass
```

Verification:
```python
from cogito.orchestration.executor import ToolExecutor
from cogito.contracts.layer_protocols import OrchestrationProtocol

assert isinstance(ToolExecutor(), OrchestrationProtocol)  # ✅ True
```

### Example 2: TemplateRenderer conforms to ProcessingProtocol

`TemplateRenderer` in `src/cogito/processing/renderer.py` implements rendering methods:

```python
class TemplateRenderer:
    def render(
        self, tool_spec: dict[str, Any], parameters: dict[str, Any] | None = None
    ) -> str:
        # Implementation...
        pass

    def validate_template_syntax(self, template_source: str) -> bool:
        # Implementation...
        pass
```

### Example 3: CLI uses OrchestrationProtocol type hints

`cli.py` should use Protocol type hints for dependency injection:

```python
# Instead of:
from cogito.orchestration import ToolExecutor

# Use:
from cogito.contracts.layer_protocols import OrchestrationProtocol

def list_tools(orchestrator: OrchestrationProtocol) -> None:
    for tool in orchestrator.list_tools():
        print(tool)
```

## Validation with mypy --strict

All Protocol definitions and usages must pass `mypy --strict`:

```bash
mypy --strict src/cogito/contracts/
mypy --strict src/cogito/ui/cli.py
```

Expected output:
```
Success: no issues found in X source files
```

## Testing Protocol Conformance

See `tests/unit/test_contracts.py` for protocol conformance tests:

```python
def test_executor_conforms_to_orchestration_protocol():
    from cogito.orchestration.executor import ToolExecutor
    from cogito.contracts.layer_protocols import OrchestrationProtocol

    executor = ToolExecutor()
    assert isinstance(executor, OrchestrationProtocol)
```

## References

- **PEP 544**: Protocols: Structural subtyping (static duck typing)
- **Python typing module**: https://docs.python.org/3/library/typing.html#typing.Protocol
- **mypy documentation**: https://mypy.readthedocs.io/en/stable/protocols.html
- **PROJECT-IMPERATIVES.md**: Imperative 3.2 (Modularity)

## Summary

Protocols enforce the five-layer architecture through the type system:

1. **Type safety**: mypy validates Protocol conformance
2. **Loose coupling**: Depend on interfaces, not implementations
3. **Runtime checks**: `isinstance()` works with `@runtime_checkable`
4. **Non-breaking**: Retrofit existing code without inheritance changes
5. **Documentation**: Protocols serve as formal contracts

This enables the type system to catch architectural violations before runtime, preventing architectural drift.
