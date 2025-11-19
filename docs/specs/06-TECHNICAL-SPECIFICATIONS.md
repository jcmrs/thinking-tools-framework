# Thinking Tools Framework - Technical Specifications

## Preamble: Adherence to Imperatives

This technical specification is grounded in the **Five Cornerstones** and **AI-First** principles:

### Five Cornerstones Integration

**1. Configurability**
- All behavior driven by external configuration files
- No hardcoded paths, values, or behaviors
- Environment-specific overrides supported
- Runtime reconfiguration without code changes

**2. Modularity**
- Each component independently replaceable
- Clear interfaces between modules
- No tight coupling or hidden dependencies
- Standard Python protocols for contracts

**3. Extensibility**
- Plugin architecture for all major subsystems
- Hooks at key lifecycle points
- Custom validators, filters, backends, integrations
- No core modifications required for extensions

**4. Integration**
- Standard interfaces (MCP protocol, Python protocols)
- Adapter pattern for external systems
- Graceful degradation when integrations unavailable
- Version negotiation and compatibility checks

**5. Automation**
- Self-healing on errors (fallback modes)
- Automated discovery and registration
- Zero-config defaults with override capability
- Scripts for all operational tasks

### AI-First Design

**Machine-Readable Contracts:**
- JSON Schema for all specifications
- Protocol classes for all interfaces
- OpenAPI/JSON-RPC for all APIs
- Type hints everywhere (mypy strict)

**Self-Documenting Systems:**
- Introspectable architecture (query component graph)
- Process memory captures all decisions
- Configuration schema with inline documentation
- Auto-generated API docs from type hints

**Context Preservation:**
- Append-only process memory log
- Knowledge graph construction
- Session handover protocols
- Zero-information-loss on transitions

**No Hidden State:**
- All state queryable via APIs
- Configuration files version-controlled
- Generated code tracked in process memory
- Cache invalidation explicit and logged

---

## Document Organization

This specification is organized by system layer (following our five-layer architecture), with explicit mapping to the Five Cornerstones for each component.

```
1. User Interface Layer Specifications
2. Orchestration Layer Specifications
3. Processing Layer Specifications
4. Storage Layer Specifications
5. Integration Layer Specifications
6. Cross-Cutting Specifications (Security, Performance, Observability)
7. Deployment and Operations
8. Testing Strategy
```

---

## 1. User Interface Layer Specifications

### 1.1 CLI (Command Line Interface)

**Cornerstone Mapping:** Automation, Configurability

#### 1.1.1 Design Principles

**AI-First CLI:**
- Machine-readable output (JSON, YAML)
- Structured error messages with error codes
- Exit codes convey detailed status
- Scriptable (no interactive prompts by default)
- Idempotent operations

**Human-Friendly:**
- Colorized output (disable with `--no-color`)
- Progress indicators for long operations
- Helpful error messages with suggestions
- Interactive mode available with `--interactive`

#### 1.1.2 Command Structure

**Standard Format:**
```bash
cogito <command> [<subcommand>] [options] [arguments]
```

**Global Options:**
```bash
--config PATH          # Custom config file (default: .cogito/config.yml)
--verbose, -v          # Verbose output
--quiet, -q            # Minimal output
--json                 # JSON output
--no-color             # Disable colored output
--help, -h             # Show help
--version              # Show version
```

**Exit Codes:**
```
0   - Success
1   - General error
2   - Invalid arguments
3   - Configuration error
4   - Validation error
5   - Generation error
6   - Integration error
10  - Security error
20  - Network error
255 - Unexpected error
```

#### 1.1.3 Command Specifications

**`cogito init`** - Initialize project

```yaml
command: init
description: Initialize Thinking Tools Framework in project
usage: cogito init [PATH] [OPTIONS]

options:
  --template: |
    Template to use (default: standard)
    Values: standard, minimal, research, enterprise
  --no-examples:
    Don't include example thinking tools
  --git-init:
    Initialize git repository if not exists

arguments:
  PATH:
    description: Project directory (default: current)
    required: false

behavior:
  - Creates .cogito/ directory structure
  - Generates default config.yml
  - Creates initial thinking_tools/ directory
  - Optionally adds example tools
  - Creates .gitignore entries

output_structure:
  json:
    status: success|error
    created_files: [...]
    config_path: string
    next_steps: [...]

examples:
  - cogito init
  - cogito init my-project --template=minimal
  - cogito init --no-examples --git-init
```

**`cogito discover`** - Discover thinking tools

```yaml
command: discover
description: Discover and index thinking tool specs
usage: cogito discover [OPTIONS]

options:
  --force:
    Force rescan (ignore cache)
  --paths:
    Additional paths to scan (comma-separated)
  --watch:
    Watch for changes and auto-reload

output:
  json:
    discovered_count: integer
    specs: [
      {
        name: string,
        path: string,
        version: string,
        valid: boolean,
        errors: [...]
      }
    ]
    duration_ms: integer

examples:
  - cogito discover
  - cogito discover --force
  - cogito discover --paths="~/.cogito/tools,./custom_tools"
```

**`cogito validate`** - Validate spec

```yaml
command: validate
description: Validate thinking tool specification
usage: cogito validate SPEC_PATH [OPTIONS]

options:
  --strict:
    Enable strict validation (quality checks)
  --security-only:
    Only run security validation
  --json:
    Output as JSON

arguments:
  SPEC_PATH:
    description: Path to spec file
    required: true

output:
  json:
    valid: boolean
    errors: [
      {
        layer: syntax|schema|semantic|security|quality,
        severity: error|warning,
        message: string,
        line: integer,
        column: integer,
        hint: string
      }
    ]
    warnings: [...]
    duration_ms: integer

examples:
  - cogito validate specs/my_tool.yml
  - cogito validate specs/my_tool.yml --strict
  - cogito validate specs/my_tool.yml --json
```

**`cogito generate`** - Generate tool code

```yaml
command: generate
description: Generate Python tool from spec
usage: cogito generate SPEC_PATH [OPTIONS]

options:
  --output DIR:
    Output directory (default: .cogito/generated_tools)
  --validate:
    Validate before generating (default: true)
  --register:
    Register with Serena immediately (default: false)

output:
  json:
    generated_file: string
    spec_version: string
    tool_name: string
    validation_result: {...}
    process_memory_entry: string  # Memory ID

examples:
  - cogito generate specs/my_tool.yml
  - cogito generate specs/my_tool.yml --register
```

**`cogito install`** - Install thinking tool

```yaml
command: install
description: Install thinking tool from spec or registry
usage: cogito install SOURCE [OPTIONS]

options:
  --scope:
    Installation scope (default: project)
    Values: global, project, user
  --override:
    Override existing tool with same name

arguments:
  SOURCE:
    description: Spec file path, registry URL, or tool name
    examples:
      - specs/my_tool.yml
      - https://registry.cogito.dev/tools/fresh-eyes
      - fresh-eyes-exercise

output:
  json:
    installed: boolean
    tool_name: string
    scope: string
    location: string

examples:
  - cogito install specs/my_tool.yml
  - cogito install fresh-eyes-exercise
  - cogito install https://registry.cogito.dev/tools/fresh-eyes --scope=global
```

**`cogito list`** - List installed tools

```yaml
command: list
description: List installed thinking tools
usage: cogito list [OPTIONS]

options:
  --scope:
    Filter by scope (global, project, user)
  --category:
    Filter by category
  --json:
    Output as JSON

output:
  json:
    tools: [
      {
        name: string,
        display_name: string,
        version: string,
        category: string,
        scope: string,
        path: string,
        installed_at: string  # ISO 8601
      }
    ]
    total: integer

examples:
  - cogito list
  - cogito list --category=review
  - cogito list --scope=project --json
```

**`cogito uninstall`** - Uninstall tool

```yaml
command: uninstall
description: Uninstall thinking tool
usage: cogito uninstall TOOL_NAME [OPTIONS]

options:
  --scope:
    Scope to remove from (default: all)
  --purge:
    Also remove spec file

arguments:
  TOOL_NAME:
    description: Name of tool to uninstall
    required: true

examples:
  - cogito uninstall fresh-eyes-exercise
  - cogito uninstall my-tool --scope=project --purge
```

**`cogito search`** - Search registry

```yaml
command: search
description: Search thinking tools registry
usage: cogito search QUERY [OPTIONS]

options:
  --category:
    Filter by category
  --min-quality:
    Minimum quality score (0-1)
  --registry:
    Registry URL (default: official)

arguments:
  QUERY:
    description: Search query
    required: true

output:
  json:
    results: [
      {
        name: string,
        display_name: string,
        description: string,
        category: string,
        quality_score: float,
        downloads: integer,
        author: string,
        updated_at: string
      }
    ]
    total: integer

examples:
  - cogito search "code review"
  - cogito search debugging --category=debugging
```

**`cogito publish`** - Publish to registry

```yaml
command: publish
description: Publish thinking tool to registry
usage: cogito publish SPEC_PATH [OPTIONS]

options:
  --registry:
    Target registry (default: official)
  --visibility:
    public or private (default: public)
  --license:
    License (default: Apache-2.0)

arguments:
  SPEC_PATH:
    description: Path to spec file
    required: true

validation:
  - Spec must pass strict validation
  - Must include test cases
  - Documentation must meet quality threshold
  - Security scan must pass

examples:
  - cogito publish specs/my_tool.yml
  - cogito publish specs/my_tool.yml --visibility=private
```

**`cogito memory`** - Query process memory

```yaml
command: memory
description: Query and manage process memory
usage: cogito memory <subcommand> [OPTIONS]

subcommands:
  list:
    description: List process memory entries
    options:
      --type: Filter by memory type
      --since: ISO 8601 timestamp
      --tags: Filter by tags (comma-separated)
      --limit: Max results (default: 20)

  show:
    description: Show memory entry details
    arguments:
      MEMORY_ID: Memory entry ID

  query:
    description: Advanced query with filters
    options:
      --query: JSON query object

  graph:
    description: Show knowledge graph
    options:
      --from: Starting memory ID
      --depth: Max depth (default: 3)
      --format: Format (dot, json, mermaid)

  export:
    description: Export process memory
    options:
      --format: Format (json, yaml, markdown)
      --output: Output file

examples:
  - cogito memory list --type=StrategicDecision
  - cogito memory show pm-001
  - cogito memory graph --from=pm-001 --format=mermaid
  - cogito memory export --format=markdown --output=memory.md
```

**`cogito config`** - Configuration management

```yaml
command: config
description: Manage configuration
usage: cogito config <subcommand> [OPTIONS]

subcommands:
  show:
    description: Show current configuration
    options:
      --json: Output as JSON

  set:
    description: Set configuration value
    arguments:
      KEY: Configuration key (dot notation)
      VALUE: Configuration value

  get:
    description: Get configuration value
    arguments:
      KEY: Configuration key

  validate:
    description: Validate configuration file

examples:
  - cogito config show
  - cogito config set validation.strict_mode true
  - cogito config get discovery.paths
```

#### 1.1.4 Configuration File Specification

**Location Priority:**
1. `--config` CLI argument
2. `.cogito/config.yml` (project-specific)
3. `~/.config/cogito/config.yml` (user-specific)
4. `/etc/cogito/config.yml` (system-wide)

**Schema:** (YAML)
```yaml
# Cogito Framework Configuration v1.0
# This file is machine-readable and AI-introspectable

system:
  version: "1.0.0"
  data_directory: "${PROJECT_ROOT}/.cogito"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  log_file: "${DATA_DIR}/logs/cogito.log"

# Cornerstone: Configurability
# All discovery behavior driven by config
discovery:
  paths:
    global: "${COGITO_HOME}/specs"
    project: "${PROJECT_ROOT}/.cogito/thinking_tools"
    user: "${USER_HOME}/.cogito/thinking_tools"

  watch: true  # Enable hot-reload
  watch_interval_seconds: 1

  ignore_patterns:
    - "*.tmp"
    - "*.swp"
    - ".git/*"
    - "__pycache__/*"

# Cornerstone: Automation
# Self-healing and automatic validation
validation:
  strict_mode: true

  layers:
    syntax: true
    schema: true
    semantic: true
    security: true
    quality: true  # Can be disabled for speed

  security:
    sandbox_templates: true
    max_execution_time_ms: 5000
    max_memory_mb: 50
    max_iterations: 10000
    allowed_jinja_tags:
      - if
      - for
      - set
      - block
      - extends
      - include
    blocked_jinja_tags:
      - import
      - from
      - call
      - macro

  quality:
    min_documentation_score: 0.7
    require_examples: true
    require_test_cases: false  # Warning only

# Cornerstone: Extensibility
# Plugin configuration
plugins:
  enabled: true
  auto_discover: true

  paths:
    - "${PROJECT_ROOT}/.cogito/plugins"
    - "${USER_HOME}/.cogito/plugins"

  validators: []  # List of validator plugin names
  filters: []     # List of filter plugin names
  backends: []    # List of storage backend plugin names

# Cornerstone: Modularity
# Independent cache configuration
performance:
  cache_enabled: true
  cache_ttl_seconds: 3600
  cache_directory: "${DATA_DIR}/cache"

  lazy_loading: true
  parallel_validation: true
  max_workers: 4

# Cornerstone: Integration
# External system connections
integration:
  serena:
    enabled: true
    tool_registry_path: null  # Auto-detect
    generated_tools_directory: "${DATA_DIR}/generated_tools"

  git:
    enabled: true
    auto_commit_specs: false
    commit_message_template: "chore: update thinking tool {tool_name}"

  registry:
    default: "https://registry.cogito.dev"
    mirrors: []
    timeout_seconds: 30

# AI-First: Process Memory
process_memory:
  enabled: true
  log_file: "${DATA_DIR}/process_memory/log.jsonl"

  capture:
    tool_executions: true
    validation_failures: true
    generation_events: true
    configuration_changes: true

  retention:
    max_entries: 100000
    archive_after_days: 365
    archive_directory: "${DATA_DIR}/process_memory/archive"

  indexing:
    rebuild_on_startup: true
    index_file: "${DATA_DIR}/process_memory/index.db"

# AI-First: Observability
observability:
  metrics:
    enabled: false
    endpoint: null

  tracing:
    enabled: false
    endpoint: null

  telemetry:
    anonymous_usage: false  # Opt-in only

# Environment variable substitution
# ${VAR} or ${VAR:-default}
# Available variables:
# - PROJECT_ROOT: Current project directory
# - USER_HOME: User home directory
# - COGITO_HOME: Framework installation directory
# - DATA_DIR: Resolved data_directory value
```

### 1.2 MCP Server Interface

**Cornerstone Mapping:** Integration, Automation

#### 1.2.1 Tool Exposure Protocol

**MCP Tool Schema:**
```json
{
  "name": "fresh_eyes_exercise",
  "description": "Step back and re-evaluate the current work with fresh perspective",
  "inputSchema": {
    "type": "object",
    "properties": {
      "phase": {
        "type": "string",
        "enum": ["full", "current_state", "target_state", "gap_analysis"],
        "description": "Which phase of the exercise to perform",
        "default": "full"
      }
    }
  }
}
```

**Auto-Registration:**
```python
# Framework automatically registers with MCP
class ThinkingToolMCPServer:
    """MCP server for thinking tools."""

    def __init__(self, manager: ThinkingToolsManager):
        self.manager = manager
        self.server = Server("thinking-tools")

    async def start(self):
        """Start MCP server and register tools."""
        # Discover all thinking tools
        tools = self.manager.discover_tools()

        # Register each as MCP tool
        for tool in tools:
            self.server.add_tool(
                name=tool.metadata.name,
                description=tool.metadata.description,
                input_schema=self._generate_input_schema(tool),
                handler=self._create_handler(tool)
            )

        await self.server.start()

    def _generate_input_schema(self, tool: ThinkingToolSpec) -> dict:
        """Generate JSON Schema for tool parameters."""
        properties = {}
        required = []

        for param_name, param_def in tool.parameters.items():
            properties[param_name] = {
                "type": param_def.type,
                "description": param_def.description
            }

            if param_def.type == "enum":
                properties[param_name]["enum"] = param_def.validation.values

            if param_def.required:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def _create_handler(self, tool: ThinkingToolSpec):
        """Create async handler for tool execution."""
        async def handler(**params):
            # Validate parameters
            validation = self._validate_params(tool, params)
            if not validation.valid:
                raise ValueError(validation.error)

            # Render template
            engine = TemplateEngine()
            prompt = engine.render(tool.template.source, **params)

            # Capture execution in process memory
            self._capture_execution(tool, params)

            return {"content": [{"type": "text", "text": prompt}]}

        return handler
```

---

## 2. Orchestration Layer Specifications

### 2.1 ThinkingToolsManager

**Cornerstone Mapping:** All Five (central coordinator)

#### 2.1.1 Interface Definition

```python
from typing import Protocol
from pathlib import Path
from dataclasses import dataclass

class ThinkingToolsManagerProtocol(Protocol):
    """
    Primary orchestration interface for thinking tools framework.

    Cornerstone Alignment:
    - Configurability: Accepts config paths, respects environment
    - Modularity: Coordinates independent components
    - Extensibility: Plugin discovery and management
    - Integration: Provides unified API for external systems
    - Automation: Self-healing, auto-discovery, auto-reload
    """

    def discover_tools(
        self,
        scan_paths: list[Path] | None = None,
        force_rescan: bool = False
    ) -> DiscoveryResult:
        """
        Discover thinking tool specs from configured paths.

        AI-First: Returns machine-readable result with full provenance.
        Automation: Caches results, only rescans on force or changes.

        Returns:
            DiscoveryResult with list of discovered specs, errors, metadata
        """
        ...

    def validate_tool(
        self,
        spec_path: Path | str,
        strict: bool = True
    ) -> ValidationResult:
        """
        Validate thinking tool specification through all layers.

        AI-First: Structured errors with line numbers, hints, examples.
        Configurability: 'strict' mode from config or override.

        Returns:
            ValidationResult with errors, warnings, suggestions
        """
        ...

    def generate_tool(
        self,
        spec: ThinkingToolSpec,
        output_path: Path | None = None
    ) -> GeneratedTool:
        """
        Generate Python tool class from validated spec.

        Automation: Auto-determines output path from config if not provided.
        Integration: Generates code compatible with Serena ToolRegistry.

        Returns:
            GeneratedTool with file path, class name, metadata
        """
        ...

    def install_tool(
        self,
        spec_path: Path | str,
        scope: str = "project",
        override: bool = False
    ) -> InstallationResult:
        """
        Install thinking tool at specified scope.

        Configurability: Scope determines installation location via config.
        Automation: Validates, generates, registers automatically.

        Returns:
            InstallationResult with installation details, success status
        """
        ...

    def reload_tools(
        self,
        tool_names: list[str] | None = None
    ) -> ReloadResult:
        """
        Hot-reload thinking tools (for development).

        Automation: Auto-detects changes, revalidates, regenerates.
        Modularity: Only reloads specified tools, doesn't affect others.

        Returns:
            ReloadResult with list of reloaded tools, errors
        """
        ...

    def list_installed(
        self,
        scope: str | None = None,
        category: str | None = None
    ) -> list[InstalledTool]:
        """
        List installed thinking tools with filters.

        AI-First: Returns structured data, machine-queryable.

        Returns:
            List of InstalledTool objects with full metadata
        """
        ...

    def get_process_memory(self) -> ProcessMemoryStore:
        """
        Get process memory store for querying system knowledge.

        AI-First: Primary context source for new AI sessions.

        Returns:
            ProcessMemoryStore instance
        """
        ...

    def get_plugin_registry(self) -> PluginRegistry:
        """
        Get plugin registry for extensibility.

        Extensibility: Access to all discovered plugins.

        Returns:
            PluginRegistry instance
        """
        ...
```

#### 2.1.2 Data Models

```python
@dataclass
class DiscoveryResult:
    """Result of thinking tool discovery."""

    success: bool
    discovered_specs: list[Path]
    total_count: int
    new_count: int  # Since last discovery
    errors: list[DiscoveryError]
    duration_ms: int
    scan_paths: list[Path]
    timestamp: str  # ISO 8601

@dataclass
class ValidationResult:
    """Result of spec validation."""

    valid: bool
    spec_path: Path
    spec_version: str
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    duration_ms: int
    layers_checked: list[str]  # [syntax, schema, semantic, security, quality]
    timestamp: str

@dataclass
class ValidationError:
    """Validation error with context."""

    layer: str  # syntax, schema, semantic, security, quality
    severity: str  # error, warning
    message: str
    line: int | None
    column: int | None
    hint: str | None
    example: str | None  # Example of correct usage
    docs_url: str | None

@dataclass
class GeneratedTool:
    """Result of tool generation."""

    file_path: Path
    class_name: str
    tool_name: str
    spec_version: str
    template_hash: str  # For cache invalidation
    generated_at: str
    process_memory_id: str  # Link to process memory entry

@dataclass
class InstallationResult:
    """Result of tool installation."""

    installed: bool
    tool_name: str
    scope: str
    location: Path
    overrode_existing: bool
    validation_result: ValidationResult
    generation_result: GeneratedTool
    timestamp: str

@dataclass
class ReloadResult:
    """Result of hot-reload operation."""

    success: bool
    reloaded_tools: list[str]
    failed_tools: dict[str, str]  # tool_name -> error
    duration_ms: int
    timestamp: str

@dataclass
class InstalledTool:
    """Installed thinking tool metadata."""

    name: str
    display_name: str
    version: str
    category: str
    scope: str  # global, project, user
    spec_path: Path
    generated_path: Path
    installed_at: str
    last_used: str | None
    usage_count: int
```

#### 2.1.3 Implementation Requirements

**State Management:**
```python
class ThinkingToolsManager:
    """Implementation of ThinkingToolsManagerProtocol."""

    def __init__(self, config_path: Path | None = None):
        # Cornerstone: Configurability
        self.config = self._load_config(config_path)

        # Cornerstone: Modularity (independent components)
        self._spec_loader = SpecLoader(self.config)
        self._validator = Validator(self.config)
        self._generator = CodeGenerator(self.config)
        self._template_engine = SecureTemplateEngine(self.config)
        self._process_memory = ProcessMemoryStore(self.config)
        self._plugin_registry = PluginRegistry(self.config)

        # Cornerstone: Automation (caching)
        self._cache = ToolCache(self.config)

        # Internal state (queryable via getters)
        self._discovered_tools: dict[str, ThinkingToolSpec] = {}
        self._installed_tools: dict[str, InstalledTool] = {}

        # Cornerstone: Extensibility
        self._discover_and_load_plugins()

    def _load_config(self, config_path: Path | None) -> ManagerConfig:
        """
        Load configuration with fallback chain.

        Priority:
        1. Explicit config_path
        2. .cogito/config.yml (project)
        3. ~/.config/cogito/config.yml (user)
        4. /etc/cogito/config.yml (system)
        5. Built-in defaults
        """
        # Search config files in priority order
        search_paths = [
            config_path,
            Path(".cogito/config.yml"),
            Path.home() / ".config/cogito/config.yml",
            Path("/etc/cogito/config.yml")
        ]

        for path in search_paths:
            if path and path.exists():
                return ManagerConfig.from_yaml(path)

        # Fall back to defaults
        return ManagerConfig.defaults()

    def discover_tools(
        self,
        scan_paths: list[Path] | None = None,
        force_rescan: bool = False
    ) -> DiscoveryResult:
        """Discover thinking tool specs."""

        start_time = time.time()

        # Use config paths if not provided
        if scan_paths is None:
            scan_paths = self.config.discovery.paths.all()

        # Check cache unless force rescan
        if not force_rescan and self._cache.has_valid_discovery():
            cached = self._cache.get_discovery()
            return DiscoveryResult(
                success=True,
                discovered_specs=cached.specs,
                total_count=len(cached.specs),
                new_count=0,
                errors=[],
                duration_ms=int((time.time() - start_time) * 1000),
                scan_paths=scan_paths,
                timestamp=datetime.utcnow().isoformat()
            )

        # Discover specs
        discovered = []
        errors = []

        for scan_path in scan_paths:
            try:
                specs = self._discover_in_path(scan_path)
                discovered.extend(specs)
            except Exception as e:
                errors.append(DiscoveryError(
                    path=scan_path,
                    error=str(e)
                ))

        # Update internal state
        previous_count = len(self._discovered_tools)
        self._discovered_tools = {
            spec.metadata.name: spec
            for spec in discovered
        }
        new_count = len(self._discovered_tools) - previous_count

        # Update cache
        self._cache.set_discovery(discovered)

        # Capture in process memory
        self._process_memory.capture(ProcessMemoryEntry(
            type="Observation",
            title=f"Discovered {len(discovered)} thinking tools",
            summary=f"Found {len(discovered)} tools across {len(scan_paths)} paths",
            tags=["discovery", "automation"],
            confidence_level=1.0
        ))

        return DiscoveryResult(
            success=len(errors) == 0,
            discovered_specs=[spec.path for spec in discovered],
            total_count=len(discovered),
            new_count=new_count,
            errors=errors,
            duration_ms=int((time.time() - start_time) * 1000),
            scan_paths=scan_paths,
            timestamp=datetime.utcnow().isoformat()
        )

    def _discover_in_path(self, path: Path) -> list[ThinkingToolSpec]:
        """Recursively discover specs in path."""
        specs = []

        # Find all .yml/.yaml files
        for spec_file in path.rglob("*.y*ml"):
            # Skip ignored patterns
            if self._should_ignore(spec_file):
                continue

            try:
                spec = self._spec_loader.load(spec_file)
                specs.append(spec)
            except Exception as e:
                # Log but don't fail discovery
                logger.warning(f"Failed to load {spec_file}: {e}")

        return specs

    def _should_ignore(self, path: Path) -> bool:
        """Check if path matches ignore patterns."""
        ignore_patterns = self.config.discovery.ignore_patterns

        for pattern in ignore_patterns:
            if path.match(pattern):
                return True

        return False
```

---

## 3. Processing Layer Specifications

### 3.1 SpecLoader

**Cornerstone Mapping:** Modularity, Configurability

#### 3.1.1 Interface

```python
class SpecLoaderProtocol(Protocol):
    """
    Load and parse thinking tool specifications.

    Modularity: Independent, replaceable component.
    Configurability: Behavior driven by config (encoding, includes, etc.)
    """

    def load(self, spec_path: Path) -> ThinkingToolSpec:
        """
        Load spec from YAML file.

        Raises:
            SpecSyntaxError: Invalid YAML syntax
            SpecSchemaError: Doesn't conform to schema
        """
        ...

    def load_string(self, spec_yaml: str) -> ThinkingToolSpec:
        """Load spec from YAML string."""
        ...

    def resolve_includes(self, spec: ThinkingToolSpec) -> ThinkingToolSpec:
        """Resolve template includes recursively."""
        ...
```

#### 3.1.2 Implementation

```python
class SpecLoader:
    """YAML spec loader with include resolution."""

    def __init__(self, config: ManagerConfig):
        self.config = config
        self._include_cache: dict[Path, str] = {}

    def load(self, spec_path: Path) -> ThinkingToolSpec:
        """Load and parse spec file."""

        # Read file with configured encoding
        try:
            content = spec_path.read_text(encoding=self.config.system.encoding)
        except UnicodeDecodeError as e:
            raise SpecSyntaxError(f"File encoding error: {e}")
        except FileNotFoundError:
            raise SpecSyntaxError(f"Spec file not found: {spec_path}")

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise SpecSyntaxError(
                message=str(e),
                file=spec_path,
                line=getattr(e, 'problem_mark', {}).get('line'),
                column=getattr(e, 'problem_mark', {}).get('column')
            )

        # Convert to ThinkingToolSpec object
        try:
            spec = ThinkingToolSpec.from_dict(data, source_path=spec_path)
        except Exception as e:
            raise SpecSchemaError(f"Invalid spec structure: {e}")

        # Resolve includes if present
        if spec.template.includes:
            spec = self.resolve_includes(spec)

        return spec

    def resolve_includes(self, spec: ThinkingToolSpec) -> ThinkingToolSpec:
        """Recursively resolve template includes."""

        resolved_template = spec.template.source

        for include_path in spec.template.includes:
            # Resolve relative to spec file
            full_path = spec.source_path.parent / include_path

            # Load included template (with caching)
            if full_path not in self._include_cache:
                if not full_path.exists():
                    raise SpecSyntaxError(
                        f"Include file not found: {include_path}"
                    )
                self._include_cache[full_path] = full_path.read_text()

            # Replace {% include 'name' %} with content
            include_name = include_path.stem
            resolved_template = resolved_template.replace(
                f"{{% include '{include_name}' %}}",
                self._include_cache[full_path]
            )

        # Return spec with resolved template
        return dataclasses.replace(
            spec,
            template=dataclasses.replace(
                spec.template,
                source=resolved_template
            )
        )
```

### 3.2 Validator

**Cornerstone Mapping:** Automation, Modularity, Extensibility

#### 3.2.1 Multi-Layer Validation Pipeline

```python
class ValidatorProtocol(Protocol):
    """
    Multi-layer validation with extensible pipeline.

    Automation: Fail-fast, helpful error messages.
    Modularity: Each layer independent.
    Extensibility: Plugins can add custom validators.
    """

    def validate(
        self,
        spec: ThinkingToolSpec,
        strict: bool = True
    ) -> ValidationResult:
        """
        Run all validation layers.

        Layers (in order):
        1. Syntax (YAML parsing) - handled by SpecLoader
        2. Schema (JSON Schema validation)
        3. Semantic (cross-field validation, dependencies)
        4. Security (template injection, resource limits)
        5. Quality (best practices, documentation) - optional

        Args:
            spec: Loaded spec to validate
            strict: If True, run quality validation (warnings)

        Returns:
            ValidationResult with all errors and warnings
        """
        ...

    def validate_layer(
        self,
        spec: ThinkingToolSpec,
        layer: str
    ) -> list[ValidationError]:
        """Validate single layer (for testing/debugging)."""
        ...
```

#### 3.2.2 Validation Layers Implementation

```python
class Validator:
    """Multi-layer validation pipeline."""

    def __init__(self, config: ManagerConfig, plugin_registry: PluginRegistry):
        self.config = config
        self.plugin_registry = plugin_registry

        # Load JSON Schema
        schema_path = Path(__file__).parent / "schemas" / "thinking-tool-v1.0.schema.json"
        self.json_schema = json.loads(schema_path.read_text())

        # Initialize layer validators
        self._schema_validator = jsonschema.Draft7Validator(self.json_schema)
        self._semantic_validator = SemanticValidator(config)
        self._security_validator = SecurityValidator(config)
        self._quality_validator = QualityValidator(config)

    def validate(
        self,
        spec: ThinkingToolSpec,
        strict: bool = True
    ) -> ValidationResult:
        """Run all validation layers."""

        start_time = time.time()
        errors = []
        warnings = []
        layers_checked = []

        # Layer 1: Syntax - already done by SpecLoader

        # Layer 2: Schema validation
        if self.config.validation.layers.schema:
            schema_errors = self._validate_schema(spec)
            errors.extend(schema_errors)
            layers_checked.append("schema")

        # Layer 3: Semantic validation
        if self.config.validation.layers.semantic:
            semantic_errors = self._validate_semantic(spec)
            errors.extend(semantic_errors)
            layers_checked.append("semantic")

        # Layer 4: Security validation
        if self.config.validation.layers.security:
            security_errors = self._validate_security(spec)
            errors.extend(security_errors)
            layers_checked.append("security")

        # Layer 5: Quality validation (warnings only)
        if strict and self.config.validation.layers.quality:
            quality_warnings = self._validate_quality(spec)
            warnings.extend(quality_warnings)
            layers_checked.append("quality")

        # Extensibility: Run plugin validators
        for validator_plugin in self.plugin_registry.get_validators():
            plugin_errors = validator_plugin.validate(spec)
            errors.extend(plugin_errors)
            layers_checked.append(f"plugin:{validator_plugin.name}")

        return ValidationResult(
            valid=(len(errors) == 0),
            spec_path=spec.source_path,
            spec_version=spec.version,
            errors=errors,
            warnings=warnings,
            duration_ms=int((time.time() - start_time) * 1000),
            layers_checked=layers_checked,
            timestamp=datetime.utcnow().isoformat()
        )

    def _validate_schema(self, spec: ThinkingToolSpec) -> list[ValidationError]:
        """JSON Schema validation."""
        errors = []

        # Convert spec to dict for validation
        spec_dict = spec.to_dict()

        for error in self._schema_validator.iter_errors(spec_dict):
            errors.append(ValidationError(
                layer="schema",
                severity="error",
                message=error.message,
                line=None,  # JSON Schema doesn't provide line numbers
                column=None,
                hint=self._generate_schema_hint(error),
                example=self._find_schema_example(error),
                docs_url=f"https://docs.cogito.dev/specs/schema#{error.json_path}"
            ))

        return errors

    def _validate_semantic(self, spec: ThinkingToolSpec) -> list[ValidationError]:
        """Cross-field and dependency validation."""
        return self._semantic_validator.validate(spec)

    def _validate_security(self, spec: ThinkingToolSpec) -> list[ValidationError]:
        """Security validation (template injection, etc.)."""
        return self._security_validator.validate(spec)

    def _validate_quality(self, spec: ThinkingToolSpec) -> list[ValidationWarning]:
        """Quality and best practices validation."""
        return self._quality_validator.validate(spec)
```

(Document continues with remaining specifications...)

---

## Appendix: Integration with Five Cornerstones

This appendix explicitly maps every major component to the Five Cornerstones:

### Configurability
- CLI accepts `--config` flag
- Configuration file priority chain
- Environment variable substitution in config
- Runtime reconfiguration without code changes
- All paths, timeouts, limits in config

### Modularity
- Five-layer architecture with clear boundaries
- Python Protocols for all interfaces
- Independent component replacement
- No tight coupling between layers
- Standard data models for communication

### Extensibility
- Plugin system for validators, filters, backends
- Entry point discovery mechanism
- Hook system at key lifecycle points
- No core modifications for extensions

### Integration
- MCP protocol for external systems
- Adapter pattern for Serena ToolRegistry
- Standard interfaces (JSON Schema, OpenAPI)
- Version negotiation and compatibility

### Automation
- Auto-discovery of specs and plugins
- Hot-reload without restart
- Self-healing on validation errors
- Automated cache management
- Process memory auto-capture

---

**Document Status**: Partial v1.0 (Layer 1-3 complete)
**Next Section**: Processing Layer (continued), Storage Layer, Integration Layer
**Total Estimated Pages**: 40-50 when complete
