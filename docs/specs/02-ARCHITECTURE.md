# Thinking Tools Framework - System Architecture

**Document Type**: Living Architecture Specification
**AI-First**: Primary consumer is AI agents; humans are strategic partners
**Status**: Active Development
**Version**: 1.0
**Last Updated**: 2025-01-14

---

## Architectural Vision

This architecture embodies **AI-First Holistic System Design** where:
- Every component can be understood and operated by AI agents autonomously
- The system thinks and evolves as a coherent organism
- Configuration drives behavior; code implements capability
- Fresh Claude sessions can resume work with full context
- Process memory captures the living knowledge of the system

---

## Core Architectural Principles

### 1. AI-First Architecture
**Implication**: Every design decision optimizes for AI comprehension and autonomous operation.

**Manifestations**:
- **Machine-Readable Contracts**: All interfaces, configs, and schemas are parseable
- **Self-Documenting Systems**: Components expose their own metadata and capabilities
- **Context Preservation**: Process memory protocol embeds understanding
- **Autonomous Recovery**: Systems can self-diagnose and repair with AI guidance
- **No Hidden State**: All system state is queryable and introspectable

### 2. Holistic System Thinking
**Implication**: Components are interdependent parts of a living system, not isolated modules.

**Manifestations**:
- **Ripple Effect Analysis**: Every change documented with system-wide impacts
- **Emergent Behavior Monitoring**: System observes its own patterns
- **Feedback Loop Integration**: Continuous learning from execution
- **Cross-Cutting Concerns**: Logging, security, validation as system properties
- **Organic Evolution**: Architecture adapts based on usage patterns

### 3. Five Cornerstones as Architectural Constraints

#### Configurability
- **All behavior** defined in `/config` directory
- **Configuration schema** validated and versioned
- **Runtime reconfiguration** supported where safe
- **Defaults documented** with strategic rationale

#### Modularity
- **Bounded contexts** with explicit contracts
- **Single responsibility** per component
- **Dependency injection** for all cross-component needs
- **Independent evolution** of modules

#### Extensibility
- **Plugin architecture** for thinking tools
- **Hook system** for lifecycle events
- **Protocol-based design** allowing alternative implementations
- **Open/Closed Principle**: Open for extension, closed for modification

#### Integration
- **Standard interfaces** (JSON, YAML, Python protocols)
- **Adapter pattern** for external systems
- **Event-driven communication** where appropriate
- **API versioning** for backward compatibility

#### Automation
- **Scripts in `/tools`** for all common operations
- **CI/CD pipelines** for validation and deployment
- **Self-testing systems** that verify their own correctness
- **Automated provisioning** of new instances

---

## System Architecture Overview

### Conceptual Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI Commands │  │  MCP Server  │  │  Web Dashboard│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Thinking Tools Manager (Coordinator)         │   │
│  │  - Discovery  - Validation  - Lifecycle  - Registry │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                          │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Spec Loader   │  │  Validator   │  │  Generator   │    │
│  └───────────────┘  └──────────────┘  └──────────────┘    │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Template Engine│  │ Tool Registry│  │Process Memory│    │
│  └───────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Specs   │  │Generated │  │ Process  │  │  Cache   │   │
│  │  (YAML)  │  │  Tools   │  │ Memory   │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Serena     │  │   Git/VCS    │  │  File System │     │
│  │ Tool Registry│  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Boundaries

Each layer has **explicit contracts** and **clear responsibilities**:

**User Interface Layer**:
- **Responsibility**: Human and AI interaction points
- **Contract**: Command → Response, all operations idempotent
- **State**: Stateless, delegates to Orchestration Layer

**Orchestration Layer**:
- **Responsibility**: Coordinate workflows, manage lifecycle
- **Contract**: High-level operations (discover, install, validate)
- **State**: Maintains registry, cache, and active tool set

**Processing Layer**:
- **Responsibility**: Transform specs → tools, render templates
- **Contract**: Input validation, deterministic outputs
- **State**: Stateless transformations, cached results

**Storage Layer**:
- **Responsibility**: Persist data, version control integration
- **Contract**: CRUD operations, transactional where needed
- **State**: Durable storage with backup/recovery

**Integration Layer**:
- **Responsibility**: Interface with external systems
- **Contract**: Adapters for each system, isolated changes
- **State**: Connection management, retry logic

---

## Component Specifications

### 1. Thinking Tools Manager (Orchestrator)

**Purpose**: Central coordinator for all thinking tool operations.

**Capabilities**:
```yaml
capabilities:
  - discover_tools:
      description: "Scan all spec locations and build registry"
      inputs: [scan_paths, filter_criteria]
      outputs: [tool_registry, errors]

  - validate_tool:
      description: "Ensure spec correctness and security"
      inputs: [spec_path_or_content]
      outputs: [validation_result, issues]

  - generate_tool:
      description: "Create Python tool class from spec"
      inputs: [validated_spec]
      outputs: [python_code, metadata]

  - install_tool:
      description: "Add tool to system (global or project)"
      inputs: [spec, scope, override_policy]
      outputs: [installation_status]

  - uninstall_tool:
      description: "Remove tool from system"
      inputs: [tool_name, scope]
      outputs: [removal_status, cleanup_report]

  - reload_tools:
      description: "Hot-reload changed specs without restart"
      inputs: [changed_specs]
      outputs: [reload_status]
```

**State Management**:
```python
class ThinkingToolsManager:
    _registry: ToolRegistry  # Discovered tools
    _cache: ToolCache       # Compiled templates
    _process_memory: ProcessMemoryStore  # Execution history
    _config: ManagerConfig  # Runtime configuration

    def __init__(self, config_path: Path):
        # Load configuration from YAML
        # Initialize storage backends
        # Trigger initial discovery
```

**Configuration**:
```yaml
# config/thinking_tools_manager.yml
discovery:
  scan_paths:
    - "${SERENA_HOME}/resources/thinking_tools"
    - "${PROJECT_ROOT}/.serena/thinking_tools"
    - "${USER_HOME}/.serena/thinking_tools"

  watch_for_changes: true
  hot_reload_enabled: true
  scan_interval_seconds: 30

validation:
  strict_mode: true
  max_template_size_kb: 100
  allowed_jinja_features:
    - variables
    - conditionals
    - loops
    - filters

  security:
    sandbox_enabled: true
    max_execution_time_ms: 5000

generation:
  output_directory: "${PROJECT_ROOT}/src/cogito/tools/generated"
  template_path: "${SERENA_HOME}/templates/tool_class.py.j2"
  auto_import: true

caching:
  enabled: true
  ttl_seconds: 3600
  max_entries: 1000
```

---

### 2. Spec Loader

**Purpose**: Load, parse, and normalize thinking tool specifications.

**Capabilities**:
```yaml
capabilities:
  - load_spec:
      description: "Read spec from file or string"
      inputs: [source]
      outputs: [parsed_spec, schema_version]

  - normalize_spec:
      description: "Convert to canonical form"
      inputs: [raw_spec]
      outputs: [normalized_spec]

  - merge_specs:
      description: "Combine project and global specs"
      inputs: [specs_list]
      outputs: [merged_spec, override_report]

  - migrate_spec:
      description: "Upgrade old spec versions"
      inputs: [old_spec, target_version]
      outputs: [migrated_spec, migration_log]
```

**Spec Schema (Canonical Form)**:
```yaml
# Canonical thinking tool specification schema
version: "1.0"  # Spec format version

metadata:
  id: UUID  # Auto-generated if not provided
  name: string  # Tool identifier (snake_case)
  display_name: string
  description: string
  author: string
  version: semver  # Tool version
  created: ISO8601
  updated: ISO8601
  tags: list[string]
  category: enum[metacognition, review, analysis, planning, debugging]

parameters:
  param_name:
    type: enum[string, int, float, bool, enum, list, dict]
    required: boolean
    default: any
    description: string
    validation:
      min: number  # For numeric types
      max: number
      pattern: regex  # For strings
      values: list  # For enums

template:
  source: string  # Inline template
  file: path  # Or reference to template file
  variables: dict  # Expected variables with descriptions

execution:
  timeout_ms: int
  retry_on_failure: boolean
  max_retries: int

integration:
  optional: boolean  # Default enabled or not
  requires_project: boolean
  requires_language_server: boolean
  conflicts_with: list[string]  # Tool names

quality:
  test_cases: list[TestCase]  # Validation test cases
  examples: list[Example]  # Usage examples

process_memory:
  capture_execution: boolean
  log_parameters: boolean
  track_effectiveness: boolean
```

**Process Memory Integration**:
Every spec load/update creates a memory entry:
```json
{
  "id": "...",
  "type": "Observation",
  "title": "Loaded thinking tool spec: fresh_eyes_exercise",
  "summary": "Successfully loaded and validated spec from project repository",
  "rationale": "Spec discovered during routine scan, validation passed",
  "source_adr": "file://.serena/thinking_tools/fresh_eyes.yml",
  "related_concepts": ["thinking_tools", "metacognition", "spec_loading"],
  "timestamp_created": "2025-01-14T...",
  "confidence_level": 1.0,
  "phase": "runtime",
  "deprecated": false,
  "provenance": {
    "author": "SpecLoader_v1.0",
    "system_version": "cogito-v1.0.0"
  },
  "tags": ["spec_loading", "tool_discovery"]
}
```

---

### 3. Validator

**Purpose**: Ensure spec correctness, security, and quality.

**Validation Layers**:

```yaml
validation_pipeline:
  - schema_validation:
      description: "Check YAML structure against schema"
      checks:
        - valid_yaml_syntax
        - required_fields_present
        - type_correctness
        - version_compatibility

  - semantic_validation:
      description: "Validate logical consistency"
      checks:
        - parameter_references_exist
        - template_variables_match_parameters
        - no_circular_dependencies
        - conflict_resolution_valid

  - security_validation:
      description: "Prevent malicious specs"
      checks:
        - template_injection_scan
        - file_path_traversal_check
        - code_execution_prevention
        - resource_limit_enforcement

  - quality_validation:
      description: "Ensure maintainability"
      checks:
        - documentation_completeness
        - test_coverage_minimum
        - example_validity
        - naming_conventions
```

**Validation Result Schema**:
```python
@dataclass
class ValidationResult:
    valid: bool
    spec_id: str
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    info: list[ValidationInfo]

    security_score: float  # 0-1
    quality_score: float   # 0-1

    recommendations: list[str]

    def to_process_memory(self) -> ProcessMemoryEntry:
        """Convert validation to process memory entry."""
        return ProcessMemoryEntry(
            type="HypothesisTested" if self.valid else "FailureAnalysis",
            title=f"Validated spec: {self.spec_id}",
            summary=f"Validation {'passed' if self.valid else 'failed'} with {len(self.errors)} errors",
            # ... rest of memory entry
        )
```

---

### 4. Generator

**Purpose**: Transform validated specs into executable Python tool classes.

**Generation Pipeline**:
```
Validated Spec → Template Context → Jinja2 Rendering → Python AST Validation → File Write
```

**Template Context Structure**:
```python
@dataclass
class GenerationContext:
    spec: ThinkingToolSpec
    class_name: str  # PascalCase from spec.metadata.name
    imports: list[str]  # Required imports
    base_classes: list[str]  # Tool, ToolMarkerOptional, etc.

    parameters: list[Parameter]  # Typed parameters for apply()
    docstring: str  # Generated from spec metadata

    template_render_call: str  # Code to render template
    validation_checks: list[str]  # Parameter validation code

    process_memory_hooks: ProcessMemoryHooks  # Memory capture points
```

**Generated Tool Class Template**:
```python
# This is the Jinja2 template for generating tool classes
# Located at: templates/tool_class.py.j2

"""
{{ spec.metadata.description }}

Auto-generated from spec: {{ spec.metadata.name }}
Version: {{ spec.metadata.version }}
Generated: {{ generation_timestamp }}

DO NOT EDIT THIS FILE DIRECTLY - Edit the spec instead.
"""

from typing import {{ type_imports }}
from cogito.core import Tool{{ ', ' + ', '.join(base_classes) if base_classes }}
from cogito.process_memory import capture_execution

{% if spec.integration.optional %}
from serena.tools.tools_base import ToolMarkerOptional
{% endif %}


class {{ class_name }}Tool(Tool{% if spec.integration.optional %}, ToolMarkerOptional{% endif %}):
    """
    {{ spec.metadata.description }}

    Category: {{ spec.metadata.category }}
    Version: {{ spec.metadata.version }}
    Author: {{ spec.metadata.author }}

    Parameters:
    {% for param_name, param_spec in spec.parameters.items() %}
    - {{ param_name }} ({{ param_spec.type }}): {{ param_spec.description }}
      {% if param_spec.required %}Required{% else %}Optional{% if param_spec.default %}, default: {{ param_spec.default }}{% endif %}{% endif %}
    {% endfor %}
    """

    # Spec metadata for introspection
    SPEC_ID = "{{ spec.metadata.id }}"
    SPEC_VERSION = "{{ spec.metadata.version }}"
    TOOL_NAME = "{{ spec.metadata.name }}"

    @capture_execution  # Process memory decorator
    def apply(self{% for param_name, param_spec in spec.parameters.items() %}, {{ param_name }}: {{ param_spec.python_type }}{% if not param_spec.required %} = {{ param_spec.default|repr }}{% endif %}{% endfor %}) -> str:
        """
        {{ spec.metadata.description }}

        {% for param_name, param_spec in spec.parameters.items() %}
        :param {{ param_name }}: {{ param_spec.description }}
        {% endfor %}
        :return: Rendered thinking tool prompt
        """

        # Parameter validation
        {% for param_name, param_spec in spec.parameters.items() %}
        {% if param_spec.validation %}
        {{ generate_validation_code(param_name, param_spec.validation) }}
        {% endif %}
        {% endfor %}

        # Prepare template context
        context = {
            {% for param_name in spec.parameters.keys() %}
            "{{ param_name }}": {{ param_name }},
            {% endfor %}
            # System-provided variables
            "tool_name": self.TOOL_NAME,
            "timestamp": datetime.now().isoformat(),
        }

        # Render template
        try:
            result = self.prompt_factory.render_thinking_tool(
                tool_name=self.TOOL_NAME,
                **context
            )

            # Process memory: Successful execution
            self._record_success(context, result)

            return result

        except Exception as e:
            # Process memory: Failure analysis
            self._record_failure(context, e)
            raise

    def _record_success(self, context: dict, result: str) -> None:
        """Record successful execution to process memory."""
        if not self.agent.config.thinking_tools.capture_execution:
            return

        memory = ProcessMemoryEntry(
            type="Observation",
            title=f"Executed {self.TOOL_NAME}",
            summary=f"Successfully generated thinking tool prompt",
            rationale="Tool executed without errors",
            # ... rest of entry
        )
        self.agent.process_memory.store(memory)

    def _record_failure(self, context: dict, error: Exception) -> None:
        """Record execution failure to process memory."""
        memory = ProcessMemoryEntry(
            type="FailureAnalysis",
            title=f"Failed to execute {self.TOOL_NAME}",
            summary=f"Error: {str(error)}",
            # ... rest of entry
        )
        self.agent.process_memory.store(memory)
```

**Code Quality Assurance**:
```python
class CodeGenerator:
    def generate(self, spec: ThinkingToolSpec) -> GeneratedCode:
        # 1. Render template
        code = self.render_template(spec)

        # 2. Parse as Python AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise GenerationError(f"Generated invalid Python: {e}")

        # 3. Validate AST structure
        self.validate_ast(tree, spec)

        # 4. Format with Black
        formatted = black.format_str(code, mode=black.Mode())

        # 5. Type check with mypy
        self.typecheck(formatted)

        # 6. Security scan
        self.security_scan(formatted)

        return GeneratedCode(
            code=formatted,
            spec_id=spec.metadata.id,
            hash=self.compute_hash(formatted)
        )
```

---

### 5. Template Engine

**Purpose**: Render thinking tool templates with security and performance.

**Design**:
```python
class SecureTemplateEngine:
    """
    Sandboxed Jinja2 environment for rendering thinking tool templates.

    Security Features:
    - Restricted function/filter whitelist
    - No filesystem access
    - No code execution
    - Resource limits (time, memory)
    """

    def __init__(self):
        self.env = SandboxedEnvironment(
            autoescape=False,  # We're generating prompts, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,  # Fail on missing variables
        )

        # Whitelist safe filters
        self.env.filters = {
            'upper': str.upper,
            'lower': str.lower,
            'title': str.title,
            'capitalize': str.capitalize,
            'trim': str.strip,
            'length': len,
            'default': lambda v, d: v if v is not None else d,
            # ... other safe filters
        }

        # No custom functions allowed
        self.env.globals = {}

    @timeout(seconds=5)  # Prevent infinite loops
    @memory_limit(mb=50)  # Prevent memory exhaustion
    def render(self, template_str: str, context: dict) -> str:
        """
        Render template with security constraints.

        Raises:
            TemplateSecurityError: If template violates security policy
            TemplateRenderError: If rendering fails
        """
        # Pre-scan for obvious injection attempts
        if self._contains_injection(template_str):
            raise TemplateSecurityError("Potential template injection detected")

        try:
            template = self.env.from_string(template_str)
            result = template.render(**context)

            # Post-render validation
            if len(result) > MAX_RENDERED_SIZE:
                raise TemplateRenderError("Rendered output exceeds size limit")

            return result

        except TemplateSyntaxError as e:
            raise TemplateRenderError(f"Template syntax error: {e}")
        except UndefinedError as e:
            raise TemplateRenderError(f"Undefined variable: {e}")
```

**Caching Strategy**:
```python
class TemplateCache:
    """
    LRU cache for compiled templates and rendered results.
    """

    def __init__(self, max_size: int = 1000):
        self._template_cache: LRUCache[str, Template] = LRUCache(max_size)
        self._render_cache: LRUCache[tuple, str] = LRUCache(max_size * 10)

    def get_template(self, template_str: str) -> Template:
        """Get compiled template from cache or compile."""
        cache_key = hash(template_str)

        if cache_key not in self._template_cache:
            template = self.engine.env.from_string(template_str)
            self._template_cache[cache_key] = template

        return self._template_cache[cache_key]

    def get_rendered(self, template_str: str, context: dict) -> str | None:
        """Get cached render result if available."""
        cache_key = (hash(template_str), frozenset(context.items()))
        return self._render_cache.get(cache_key)

    def cache_rendered(self, template_str: str, context: dict, result: str):
        """Store render result in cache."""
        cache_key = (hash(template_str), frozenset(context.items()))
        self._render_cache[cache_key] = result
```

---

### 6. Process Memory Store

**Purpose**: Capture system knowledge as structured, queryable memories.

**Schema Implementation**:
```python
@dataclass
class ProcessMemoryEntry:
    """
    Structured process memory following the unified schema.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ProcessMemoryType
    title: str
    summary: str
    rationale: str

    source_adr: str | None = None
    related_concepts: list[str] = field(default_factory=list)

    timestamp_created: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    timestamp_updated: str | None = None

    confidence_level: float = 1.0  # 0-1
    phase: str = "runtime"
    deprecated: bool = False

    provenance: dict = field(default_factory=dict)
    links: list[str] = field(default_factory=list)  # Links to other memory IDs
    tags: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Serialize to JSON for storage."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'ProcessMemoryEntry':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(**data)


class ProcessMemoryStore:
    """
    Storage and retrieval system for process memories.

    Implements:
    - Append-only log (immutability)
    - Index for fast querying
    - Knowledge graph construction
    - Memory hygiene enforcement
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Memory log (append-only)
        self.log_file = storage_path / "memory_log.jsonl"

        # Indexes
        self.by_type: dict[str, list[str]] = defaultdict(list)
        self.by_tag: dict[str, list[str]] = defaultdict(list)
        self.by_phase: dict[str, list[str]] = defaultdict(list)

        # Knowledge graph (memory_id -> linked_memory_ids)
        self.knowledge_graph: dict[str, set[str]] = defaultdict(set)

        # Load existing memories
        self._load_index()

    def store(self, memory: ProcessMemoryEntry) -> None:
        """
        Store a new memory entry.

        Enforces:
        - Immutability (append-only)
        - Schema validation
        - Index updating
        """
        # Validate
        if not self._validate_memory(memory):
            raise ValueError("Invalid memory entry")

        # Append to log
        with open(self.log_file, 'a') as f:
            f.write(memory.to_json() + '\n')

        # Update indexes
        self._update_indexes(memory)

        # Update knowledge graph
        for linked_id in memory.links:
            self.knowledge_graph[memory.id].add(linked_id)
            self.knowledge_graph[linked_id].add(memory.id)  # Bidirectional

    def query(
        self,
        type: ProcessMemoryType | None = None,
        tags: list[str] | None = None,
        phase: str | None = None,
        since: datetime | None = None,
        deprecated: bool = False,
    ) -> list[ProcessMemoryEntry]:
        """
        Query memories with filters.
        """
        # Implementation using indexes for efficiency
        ...

    def get_context_for_session(self, session_id: str) -> str:
        """
        Generate context summary for new AI session.

        Returns:
            Markdown-formatted context with:
            - Recent strategic decisions
            - Active assumptions
            - Known failures and lessons
            - Current system state
        """
        # Query relevant memories
        decisions = self.query(type="StrategicDecision", deprecated=False)
        assumptions = self.query(type="AssumptionMade", deprecated=False)
        lessons = self.query(type="LessonLearned", deprecated=False)

        # Format as structured markdown
        context = f"""
# Process Memory Context - Session {session_id}

## Strategic Decisions (Active)
{self._format_memories(decisions)}

## Current Assumptions
{self._format_memories(assumptions)}

## Lessons Learned
{self._format_memories(lessons)}

## Knowledge Graph
{self._visualize_graph()}
"""
        return context

    def deprecate(self, memory_id: str, reason: str) -> None:
        """
        Mark a memory as deprecated.

        Creates new memory entry documenting deprecation.
        """
        # Load original memory
        memory = self.get(memory_id)

        # Create deprecation record
        deprecation_memory = ProcessMemoryEntry(
            type="Observation",
            title=f"Deprecated memory: {memory.title}",
            summary=f"Memory {memory_id} deprecated: {reason}",
            rationale=reason,
            links=[memory_id],
            tags=["deprecation"]
        )

        # Store deprecation
        self.store(deprecation_memory)

        # Update index to mark as deprecated
        # (Actual memory log entry remains immutable)
        self._mark_deprecated(memory_id)
```

**Memory Provisioning for New Projects**:
```python
class ProjectProvisioner:
    """
    Provisions new Thinking Tools projects with essential process memory.
    """

    def provision(self, project_path: Path) -> ProvisioningReport:
        """
        Create new project with:
        - Directory structure
        - Configuration files
        - Initial process memories
        - Documentation templates
        """

        # 1. Create structure
        self._create_directories(project_path)

        # 2. Copy configuration templates
        self._install_configs(project_path)

        # 3. Create foundational process memories
        initial_memories = [
            ProcessMemoryEntry(
                type="StrategicDecision",
                title="Project initialized with Thinking Tools Framework",
                summary="New project created using Cogito framework",
                rationale="Leveraging declarative thinking tools for AI-first development",
                source_adr=str(project_path / "docs/adr/001-adopt-thinking-tools.md"),
                related_concepts=["initialization", "framework", "thinking_tools"],
                phase="initialization",
                tags=["bootstrap", "foundation"]
            ),

            ProcessMemoryEntry(
                type="AssumptionMade",
                title="AI-First development model assumed",
                summary="Project assumes AI agents as primary developers",
                rationale="Human as strategic partner, AI owns implementation",
                related_concepts=["ai_first", "development_model"],
                phase="initialization",
                tags=["assumption", "development_philosophy"]
            ),

            ProcessMemoryEntry(
                type="MentalModel",
                title="Five Cornerstones architectural model",
                summary="System designed around Configurability, Modularity, Extensibility, Integration, Automation",
                rationale="Proven pattern for sustainable AI-driven systems",
                related_concepts=["architecture", "principles", "cornerstones"],
                phase="initialization",
                tags=["architecture", "principles"]
            ),
        ]

        # 4. Store memories
        memory_store = ProcessMemoryStore(project_path / ".cogito/process_memory")
        for memory in initial_memories:
            memory_store.store(memory)

        # 5. Generate bootstrap documentation
        self._generate_docs(project_path, memory_store)

        return ProvisioningReport(
            project_path=project_path,
            memories_created=len(initial_memories),
            structure_created=True,
            documentation_generated=True
        )
```

---

## Data Flow Architecture

### Discovery → Execution Flow

```
1. DISCOVERY
   ┌──────────────────────┐
   │  Scan Directories    │
   │  - Global specs      │
   │  - Project specs     │
   │  - User specs        │
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐
   │  Load & Parse Specs  │
   │  - YAML parsing      │
   │  - Schema validation │
   │  - Normalization     │
   └──────┬───────────────┘
          ▼
2. VALIDATION
   ┌──────────────────────┐
   │  Multi-Layer Check   │
   │  - Schema            │
   │  - Semantics         │
   │  - Security          │
   │  - Quality           │
   └──────┬───────────────┘
          ▼
3. GENERATION
   ┌──────────────────────┐
   │  Generate Tool Class │
   │  - Template render   │
   │  - AST validation    │
   │  - Code formatting   │
   │  - Write to disk     │
   └──────┬───────────────┘
          ▼
4. REGISTRATION
   ┌──────────────────────┐
   │  Tool Registry       │
   │  - Import generated  │
   │  - Register with MCP │
   │  - Cache metadata    │
   └──────┬───────────────┘
          ▼
5. EXECUTION (Runtime)
   ┌──────────────────────┐
   │  AI Calls Tool       │
   │  (via MCP)           │
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐
   │  Parameter Validation│
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐
   │  Template Rendering  │
   │  (Sandboxed)         │
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐
   │  Process Memory      │
   │  Capture             │
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐
   │  Return Prompt       │
   │  to AI Agent         │
   └──────────────────────┘
```

### Hot-Reload Flow

```
File System Change Detected
          ▼
┌──────────────────────┐
│  Which spec changed? │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  Reload & Validate   │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  Regenerate Tool     │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  Update Registry     │
│  (No restart needed) │
└──────────────────────┘
```

---

## Integration Architecture

### Serena Integration

```python
# Integration point in Serena's ToolRegistry

class SerenaToolRegistry:
    """Extended to discover Cogito-generated tools."""

    def __init__(self):
        # ... existing Serena tool discovery ...

        # Discover Cogito tools
        self._discover_cogito_tools()

    def _discover_cogito_tools(self):
        """
        Find and register all Cogito-generated thinking tools.
        """
        cogito_tools_path = Path(__file__).parent / "thinking_tools" / "generated"

        if not cogito_tools_path.exists():
            return

        # Import all generated tool modules
        for tool_file in cogito_tools_path.glob("generated_*.py"):
            module_name = tool_file.stem
            module = importlib.import_module(f"serena.tools.thinking_tools.generated.{module_name}")

            # Tools auto-register via inheritance from Tool base class
            # Serena's existing discovery mechanism picks them up
```

**Integration Contract**:
```yaml
# Integration guarantees between Cogito and Serena

guarantees:
  backwards_compatibility:
    - Cogito tools are standard Serena tools
    - No Serena core changes required
    - Existing tool infrastructure works unchanged

  namespacing:
    - All Cogito tools in dedicated namespace
    - No name collisions with core Serena tools
    - Clear provenance (Cogito-generated)

  lifecycle:
    - Cogito manages own tool lifecycle
    - Serena discovers and registers automatically
    - Hot-reload doesn't affect Serena stability

  security:
    - Cogito tools pass same security standards
    - Sandboxing enforced
    - Serena security model respected
```

---

## Configuration Architecture

### Configuration Hierarchy

```
System Config (Highest Priority)
    ↓
Project Config (Overrides system)
    ↓
User Config (Overrides project)
    ↓
Spec Config (Tool-specific)
    ↓
Defaults (Lowest priority)
```

### Configuration Schema

```yaml
# config/cogito.yml (Master configuration)

system:
  version: "1.0.0"
  log_level: INFO
  data_directory: "${PROJECT_ROOT}/.cogito"

discovery:
  paths:
    global: "${COGITO_HOME}/specs"
    project: "${PROJECT_ROOT}/.cogito/thinking_tools"
    user: "${USER_HOME}/.cogito/thinking_tools"

  watch: true
  interval_seconds: 30

validation:
  strict_mode: true

  security:
    sandbox_templates: true
    max_execution_time_ms: 5000
    max_memory_mb: 50

  quality:
    require_documentation: true
    require_examples: true
    min_test_coverage: 0.8

generation:
  output_directory: "src/cogito/tools/generated"
  auto_import: true
  format_code: true
  type_check: true

process_memory:
  enabled: true
  storage_path: "${PROJECT_ROOT}/.cogito/process_memory"
  capture_execution: true
  capture_failures: true
  retention_days: 365

performance:
  cache_enabled: true
  cache_ttl_seconds: 3600
  max_cache_size_mb: 100

integration:
  serena:
    auto_register: true
    namespace: "cogito"
```

**Configuration as Code**:
All configuration files are:
- Version controlled
- Schema validated
- Documented with inline comments
- Migrate-able between versions

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────┐
│         User Input Validation           │  ← First line of defense
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│       Spec Schema Validation            │  ← Structure enforcement
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│      Template Injection Scanning        │  ← Attack pattern detection
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│     Sandboxed Template Execution        │  ← Runtime isolation
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│      Resource Limit Enforcement         │  ← DoS prevention
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         Audit Logging                   │  ← Forensics
└─────────────────────────────────────────┘
```

### Security Policies

```python
class SecurityPolicy:
    """
    Configurable security policies for Cogito.
    """

    # Template security
    ALLOWED_JINJA_TAGS = {'if', 'for', 'set', 'block', 'extends', 'include'}
    BLOCKED_JINJA_TAGS = {'import', 'from', 'exec', 'eval'}

    # Filesystem security
    ALLOWED_TEMPLATE_PATHS = [
        Path.cwd() / ".cogito/templates",
        COGITO_HOME / "templates",
    ]

    # Execution security
    MAX_TEMPLATE_EXECUTION_TIME_MS = 5000
    MAX_TEMPLATE_MEMORY_MB = 50
    MAX_RENDERED_OUTPUT_KB = 500

    # Network security (templates cannot access network)
    NETWORK_ACCESS_ALLOWED = False

    # Code generation security
    ALLOWED_PYTHON_AST_NODES = {
        ast.Module, ast.ClassDef, ast.FunctionDef,
        ast.Assign, ast.Return, ast.If, ast.For,
        # ... safe nodes only
    }
```

---

## Deployment Architecture

### Packaging Structure

```
cogito/
├── pyproject.toml           # Package metadata
├── README.md
├── LICENSE
├── SECURITY.md              # Security policy
├── src/
│   └── cogito/
│       ├── __init__.py
│       ├── core/            # Core framework
│       │   ├── manager.py
│       │   ├── spec_loader.py
│       │   ├── validator.py
│       │   ├── generator.py
│       │   └── template_engine.py
│       ├── tools/           # Tool implementations
│       │   └── generated/   # Auto-generated tools
│       ├── process_memory/  # Memory system
│       │   ├── store.py
│       │   └── schema.py
│       ├── cli/             # CLI commands
│       │   └── main.py
│       └── integrations/    # Framework integrations
│           └── serena.py
├── config/                  # Default configurations
│   └── cogito.yml
├── specs/                   # Bundled thinking tool specs
│   ├── fresh_eyes.yml
│   ├── domain_expert.yml
│   └── ...
├── templates/               # Code generation templates
│   └── tool_class.py.j2
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
└── docs/
    ├── architecture/
    ├── adr/
    └── user_guide/
```

### Deployment Models

**1. Standalone Installation**
```bash
pip install cogito
cogito init my-project
cd my-project
cogito discover
```

**2. Serena Integration**
```bash
pip install cogito[serena]
# Auto-discovered by Serena
serena start-mcp-server
```

**3. Development Mode**
```bash
git clone https://github.com/cogito/cogito
cd cogito
pip install -e ".[dev]"
```

---

## Performance Architecture

### Performance Targets

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| Spec discovery | <100ms | For 1000 specs |
| Spec validation | <50ms per spec | Parallel processing |
| Tool generation | <200ms per tool | Including formatting |
| Template rendering | <20ms | Cached templates |
| Hot-reload | <500ms | For single spec |
| Process memory query | <10ms | Indexed queries |

### Optimization Strategies

**1. Caching**
- Compiled templates cached in memory
- Rendered results cached by parameters
- Validation results cached by spec hash
- LRU eviction policy

**2. Lazy Loading**
- Tools generated on-demand initially
- Background generation after initial load
- Incremental compilation

**3. Parallel Processing**
- Spec validation parallelized
- Tool generation parallelized
- Independent operations concurrent

**4. Index-Based Queries**
- Process memory indexed by type, tag, phase
- B-tree indexes for timestamp queries
- Full-text search for content queries

---

## Monitoring & Observability

### Telemetry Points

```python
class TelemetryCollector:
    """
    Collect system metrics and events.
    """

    def record_event(
        self,
        event_type: str,
        metadata: dict,
        process_memory: bool = True
    ):
        """
        Record system event.

        Events automatically create process memory entries
        for critical operations.
        """

        event = Event(
            type=event_type,
            timestamp=datetime.now(UTC),
            metadata=metadata
        )

        # Emit to monitoring system
        self._emit_metric(event)

        # Store in process memory if significant
        if process_memory and self._is_significant(event):
            memory = event.to_process_memory()
            self.process_memory_store.store(memory)
```

### Metrics Tracked

```yaml
metrics:
  counters:
    - tools_discovered
    - tools_generated
    - tools_executed
    - validation_failures
    - generation_failures
    - template_render_errors

  histograms:
    - spec_validation_duration_ms
    - tool_generation_duration_ms
    - template_render_duration_ms
    - hot_reload_duration_ms

  gauges:
    - active_tools_count
    - cached_templates_count
    - process_memory_entries_count
    - total_specs_size_kb
```

---

## Failure Modes & Recovery

### Fault Tolerance

**Graceful Degradation**:
```yaml
failure_scenarios:
  spec_validation_failure:
    behavior: Skip invalid spec, log error, continue
    recovery: User fixes spec, hot-reload detects

  tool_generation_failure:
    behavior: Use last known good version, alert
    recovery: Fix spec or template, regenerate

  template_render_failure:
    behavior: Return error to AI with context
    recovery: AI adjusts parameters or retries

  process_memory_corruption:
    behavior: Rebuild index from log, verify
    recovery: Log is append-only, always valid

  hot_reload_failure:
    behavior: Keep existing tools, log error
    recovery: Manual reload or restart
```

**Self-Healing**:
```python
class SelfHealingManager:
    """
    Detect and automatically fix common issues.
    """

    def health_check(self) -> HealthReport:
        """
        Periodic health check of system.
        """
        issues = []

        # Check 1: Verify all generated tools valid
        for tool in self.registry.get_all():
            if not self._verify_tool(tool):
                issues.append(f"Invalid tool: {tool.name}")
                self._regenerate_tool(tool)  # Auto-fix

        # Check 2: Verify process memory index
        if not self.process_memory.verify_index():
            issues.append("Process memory index corrupted")
            self.process_memory.rebuild_index()  # Auto-fix

        # Check 3: Verify cache consistency
        if not self.cache.verify():
            issues.append("Cache inconsistency detected")
            self.cache.clear()  # Safe fallback

        return HealthReport(issues=issues, auto_fixed=len(issues))
```

---

## Evolution & Versioning

### Spec Format Versioning

```yaml
# Version migration path
versions:
  "1.0":
    description: "Initial release"
    breaking_changes: []

  "1.1":
    description: "Add quality metrics"
    breaking_changes: []
    migration:
      - Add default quality section if missing

  "2.0":
    description: "Restructure parameters"
    breaking_changes:
      - "parameters schema changed"
    migration:
      - Convert old parameter format to new
      - Validate all specs
```

**Migration Strategy**:
```python
class SpecMigrator:
    """
    Migrate specs between format versions.
    """

    def migrate(self, spec: dict, from_version: str, to_version: str) -> dict:
        """
        Migrate spec from one version to another.

        Returns migrated spec with metadata documenting migration.
        """

        migrated = spec.copy()
        migrated['_migration_history'] = migrated.get('_migration_history', [])

        # Apply migration steps
        for step in self._get_migration_path(from_version, to_version):
            migrated = step.apply(migrated)

            migrated['_migration_history'].append({
                'from_version': step.from_version,
                'to_version': step.to_version,
                'timestamp': datetime.now(UTC).isoformat(),
                'automated': True
            })

        # Update version
        migrated['version'] = to_version

        return migrated
```

---

## Summary: Architectural Qualities

This architecture achieves:

✅ **AI-First**: Every component designed for AI comprehension and autonomous operation
✅ **Holistic Thinking**: System aware of its own state and patterns
✅ **Configurability**: Behavior driven by external configuration
✅ **Modularity**: Independent, replaceable components
✅ **Extensibility**: Plugin architecture for unlimited growth
✅ **Integration**: Standard interfaces, seamless connections
✅ **Automation**: Scripts for all operations, self-healing systems
✅ **Process Memory**: Living knowledge graph of system evolution
✅ **Security**: Defense in depth, sandboxing, auditing
✅ **Performance**: Sub-second operations, efficient caching
✅ **Resilience**: Graceful degradation, self-healing, fault tolerance

---

**Next Steps**: Proceed to Framework Specification and ADR documentation.

**Document Status**: Architecture Specification v1.0
**Owner**: AI Product Owner & System Architect
**Last Updated**: 2025-01-14
**Living Document**: Yes - evolves with system
