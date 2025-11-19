# Thinking Tools Framework - Framework & API Specification

**Document Type**: Technical Specification (Machine-Readable)
**AI-First**: Designed for autonomous AI implementation
**Status**: Specification Complete
**Version**: 1.0.0
**Last Updated**: 2025-01-14

---

## Specification Overview

This document provides the complete technical specification for implementing the Thinking Tools Framework (Cogito). It includes:
- Formal API definitions
- Data schemas (JSON Schema)
- Protocol specifications
- Interface contracts
- Type systems
- Error handling specifications

**Target Audience**: AI agents implementing the framework

---

## 1. Spec Format Specification

### 1.1 JSON Schema for Thinking Tool Specs

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://cogito.dev/schemas/thinking-tool-spec-v1.0.json",
  "title": "Thinking Tool Specification",
  "description": "Schema for defining thinking tool specifications",
  "type": "object",
  "required": ["version", "metadata", "template"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Spec format version (e.g., '1.0')"
    },
    "metadata": {
      "type": "object",
      "required": ["name", "description"],
      "properties": {
        "id": {
          "type": "string",
          "format": "uuid",
          "description": "Unique identifier (auto-generated if not provided)"
        },
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$",
          "description": "Tool identifier in snake_case"
        },
        "display_name": {
          "type": "string",
          "description": "Human-readable name"
        },
        "description": {
          "type": "string",
          "minLength": 10,
          "maxLength": 500,
          "description": "Brief description of tool purpose"
        },
        "author": {
          "type": "string",
          "description": "Creator name or organization"
        },
        "version": {
          "type": "string",
          "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
          "description": "Tool version (semver)"
        },
        "created": {
          "type": "string",
          "format": "date-time",
          "description": "Creation timestamp (ISO 8601)"
        },
        "updated": {
          "type": "string",
          "format": "date-time",
          "description": "Last update timestamp (ISO 8601)"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Categorization tags"
        },
        "category": {
          "type": "string",
          "enum": ["metacognition", "review", "analysis", "planning", "debugging", "handoff"],
          "description": "Primary category"
        }
      }
    },
    "parameters": {
      "type": "object",
      "additionalProperties": {
        "$ref": "#/definitions/parameter"
      },
      "description": "Named parameters for the tool"
    },
    "template": {
      "oneOf": [
        {
          "type": "object",
          "required": ["source"],
          "properties": {
            "source": {
              "type": "string",
              "description": "Inline Jinja2 template"
            },
            "variables": {
              "type": "object",
              "description": "Expected variables with descriptions"
            }
          }
        },
        {
          "type": "object",
          "required": ["file"],
          "properties": {
            "file": {
              "type": "string",
              "description": "Path to template file"
            },
            "variables": {
              "type": "object",
              "description": "Expected variables with descriptions"
            }
          }
        }
      ],
      "description": "Template definition (inline or file reference)"
    },
    "execution": {
      "type": "object",
      "properties": {
        "timeout_ms": {
          "type": "integer",
          "minimum": 100,
          "maximum": 30000,
          "default": 5000,
          "description": "Execution timeout in milliseconds"
        },
        "retry_on_failure": {
          "type": "boolean",
          "default": false,
          "description": "Whether to retry on failure"
        },
        "max_retries": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5,
          "default": 1,
          "description": "Maximum retry attempts"
        }
      }
    },
    "integration": {
      "type": "object",
      "properties": {
        "optional": {
          "type": "boolean",
          "default": false,
          "description": "Whether tool is optional (disabled by default)"
        },
        "requires_project": {
          "type": "boolean",
          "default": false,
          "description": "Whether tool requires active project"
        },
        "requires_language_server": {
          "type": "boolean",
          "default": false,
          "description": "Whether tool requires language server"
        },
        "conflicts_with": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Tools that conflict with this one"
        }
      }
    },
    "quality": {
      "type": "object",
      "properties": {
        "test_cases": {
          "type": "array",
          "items": {"$ref": "#/definitions/testCase"},
          "description": "Validation test cases"
        },
        "examples": {
          "type": "array",
          "items": {"$ref": "#/definitions/example"},
          "description": "Usage examples"
        }
      }
    },
    "process_memory": {
      "type": "object",
      "properties": {
        "capture_execution": {
          "type": "boolean",
          "default": true,
          "description": "Capture tool executions"
        },
        "log_parameters": {
          "type": "boolean",
          "default": false,
          "description": "Log parameter values"
        },
        "track_effectiveness": {
          "type": "boolean",
          "default": true,
          "description": "Track tool effectiveness metrics"
        }
      }
    }
  },
  "definitions": {
    "parameter": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["string", "int", "float", "bool", "enum", "list", "dict"],
          "description": "Parameter data type"
        },
        "required": {
          "type": "boolean",
          "default": true,
          "description": "Whether parameter is required"
        },
        "default": {
          "description": "Default value if not required"
        },
        "description": {
          "type": "string",
          "description": "Parameter description"
        },
        "validation": {
          "type": "object",
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "pattern": {"type": "string"},
            "values": {"type": "array"}
          }
        }
      }
    },
    "testCase": {
      "type": "object",
      "required": ["description", "parameters", "expected"],
      "properties": {
        "description": {"type": "string"},
        "parameters": {"type": "object"},
        "expected": {
          "type": "object",
          "properties": {
            "success": {"type": "boolean"},
            "contains": {"type": "array", "items": {"type": "string"}},
            "not_contains": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    },
    "example": {
      "type": "object",
      "required": ["description", "usage"],
      "properties": {
        "description": {"type": "string"},
        "usage": {"type": "string"},
        "output_sample": {"type": "string"}
      }
    }
  }
}
```

### 1.2 YAML Example (Canonical)

```yaml
version: "1.0"

metadata:
  id: "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  name: "fresh_eyes_exercise"
  display_name: "Fresh Eyes Exercise"
  description: "Systematic perspective switching for assumption discovery"
  author: "Cogito Framework Team"
  version: "1.0.0"
  created: "2025-01-14T10:00:00Z"
  updated: "2025-01-14T10:00:00Z"
  tags: ["metacognition", "perspective-switching", "assumptions"]
  category: "metacognition"

parameters:
  phase:
    type: "enum"
    required: true
    default: "full"
    description: "Which phase of the analysis to perform"
    validation:
      values: ["full", "current_state", "target_state", "gap_analysis", "validation", "quick"]

  domain:
    type: "string"
    required: false
    description: "Specific domain context for the analysis"

template:
  source: |
    # Fresh Eyes Exercise - {{ phase|upper }} Phase

    {% if phase == 'full' or phase == 'current_state' %}
    ## Phase 1: Current State Analysis
    ### Step 1: Context Inventory
    **Question**: What do I know that influences my approach?
    **Method**: List technical knowledge, setup procedures, architecture understanding.
    {% if domain %}
    **Domain Context**: {{ domain }}
    {% endif %}
    {% endif %}

    {% if phase == 'quick' %}
    ## Quick Perspective Check
    1. What assumptions am I making?
    2. What would a novice not understand?
    3. What's the simplest alternative approach?
    {% endif %}

  variables:
    phase: "Analysis phase selector"
    domain: "Optional domain context"

execution:
  timeout_ms: 5000
  retry_on_failure: false
  max_retries: 1

integration:
  optional: false
  requires_project: false
  requires_language_server: false
  conflicts_with: []

quality:
  test_cases:
    - description: "Full phase execution"
      parameters:
        phase: "full"
      expected:
        success: true
        contains: ["Phase 1", "Context Inventory"]

    - description: "Quick phase execution"
      parameters:
        phase: "quick"
      expected:
        success: true
        contains: ["Quick Perspective Check"]

  examples:
    - description: "Basic usage for architecture review"
      usage: "mcp__serena__fresh_eyes_exercise(phase='full')"
      output_sample: "# Fresh Eyes Exercise - FULL Phase\n\n## Phase 1: Current State Analysis..."

process_memory:
  capture_execution: true
  log_parameters: false
  track_effectiveness: true
```

---

## 2. Core API Specifications

### 2.1 ThinkingToolsManager API

```python
from typing import Protocol, Optional
from pathlib import Path
from dataclasses import dataclass

class ThinkingToolsManagerProtocol(Protocol):
    """
    Protocol defining the public API for ThinkingToolsManager.

    This is the primary interface for all thinking tool operations.
    """

    def discover_tools(
        self,
        scan_paths: list[Path] | None = None,
        force_rescan: bool = False
    ) -> DiscoveryResult:
        """
        Discover all thinking tool specs from configured locations.

        Args:
            scan_paths: Override default scan paths (None = use config)
            force_rescan: Bypass cache and force fresh scan

        Returns:
            DiscoveryResult with discovered tools and errors

        Raises:
            DiscoveryError: If critical error prevents discovery
        """
        ...

    def validate_tool(
        self,
        spec_path: Path | str,
        strict: bool = True
    ) -> ValidationResult:
        """
        Validate a thinking tool specification.

        Args:
            spec_path: Path to spec file or spec content as string
            strict: Enable strict validation mode

        Returns:
            ValidationResult with errors, warnings, and scores

        Raises:
            ValidationError: If spec is malformed
        """
        ...

    def generate_tool(
        self,
        spec: ThinkingToolSpec,
        output_path: Path | None = None
    ) -> GeneratedTool:
        """
        Generate Python tool class from validated spec.

        Args:
            spec: Validated thinking tool specification
            output_path: Override default output location

        Returns:
            GeneratedTool with code and metadata

        Raises:
            GenerationError: If code generation fails
        """
        ...

    def install_tool(
        self,
        spec_path: Path,
        scope: Literal["global", "project", "user"],
        override: bool = False
    ) -> InstallationResult:
        """
        Install thinking tool to specified scope.

        Args:
            spec_path: Path to spec file
            scope: Installation scope (global/project/user)
            override: Allow overriding existing tool

        Returns:
            InstallationResult with status

        Raises:
            InstallationError: If installation fails
        """
        ...

    def uninstall_tool(
        self,
        tool_name: str,
        scope: Literal["global", "project", "user"]
    ) -> UninstallationResult:
        """
        Uninstall thinking tool from specified scope.

        Args:
            tool_name: Name of tool to remove
            scope: Scope to remove from

        Returns:
            UninstallationResult with cleanup report

        Raises:
            UninstallationError: If uninstallation fails
        """
        ...

    def reload_tools(
        self,
        tool_names: list[str] | None = None
    ) -> ReloadResult:
        """
        Hot-reload changed tools without restart.

        Args:
            tool_names: Specific tools to reload (None = all changed)

        Returns:
            ReloadResult with status per tool

        Raises:
            ReloadError: If reload fails critically
        """
        ...

    def get_tool_info(
        self,
        tool_name: str
    ) -> ToolInfo:
        """
        Get detailed information about a tool.

        Args:
            tool_name: Name of tool

        Returns:
            ToolInfo with metadata, status, and usage

        Raises:
            ToolNotFoundError: If tool doesn't exist
        """
        ...

    def list_tools(
        self,
        category: str | None = None,
        scope: Literal["global", "project", "user", "all"] = "all"
    ) -> list[ToolSummary]:
        """
        List available thinking tools.

        Args:
            category: Filter by category (None = all)
            scope: Filter by installation scope

        Returns:
            List of ToolSummary objects
        """
        ...

    def get_process_memory_context(
        self,
        session_id: str
    ) -> str:
        """
        Generate process memory context for AI session.

        Args:
            session_id: Unique session identifier

        Returns:
            Markdown-formatted context summary
        """
        ...


@dataclass
class DiscoveryResult:
    """Result of tool discovery operation."""
    discovered: list[ThinkingToolSpec]
    errors: list[DiscoveryError]
    duration_ms: int
    scan_paths: list[Path]


@dataclass
class ValidationResult:
    """Result of spec validation."""
    valid: bool
    spec_id: str
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    security_score: float  # 0-1
    quality_score: float   # 0-1
    recommendations: list[str]


@dataclass
class GeneratedTool:
    """Generated tool class information."""
    class_name: str
    code: str
    spec_id: str
    output_path: Path
    hash: str
    generated_at: str


@dataclass
class InstallationResult:
    """Result of tool installation."""
    success: bool
    tool_name: str
    scope: str
    installed_path: Path
    message: str


@dataclass
class ToolInfo:
    """Detailed tool information."""
    spec: ThinkingToolSpec
    status: Literal["active", "disabled", "error"]
    installation_scope: str
    usage_count: int
    last_used: str | None
    effectiveness_score: float | None
```

### 2.2 CLI API Specification

```yaml
# CLI command specification
cli:
  name: "cogito"
  version: "1.0.0"
  description: "Thinking Tools Framework CLI"

  global_options:
    - name: "--config"
      type: "path"
      description: "Path to config file"

    - name: "--project"
      type: "path"
      description: "Project directory"

    - name: "--verbose"
      short: "-v"
      type: "flag"
      description: "Verbose output"

  commands:
    - name: "init"
      description: "Initialize new Cogito project"
      usage: "cogito init [PATH]"
      arguments:
        - name: "path"
          type: "path"
          required: false
          default: "."
          description: "Project directory"
      options:
        - name: "--template"
          type: "string"
          description: "Project template"
      example: "cogito init my-project --template=standard"

    - name: "discover"
      description: "Discover thinking tool specs"
      usage: "cogito discover [OPTIONS]"
      options:
        - name: "--path"
          type: "path"
          description: "Additional scan path"
        - name: "--force"
          type: "flag"
          description: "Force rescan"
      example: "cogito discover --force"

    - name: "validate"
      description: "Validate thinking tool spec"
      usage: "cogito validate SPEC_PATH"
      arguments:
        - name: "spec_path"
          type: "path"
          required: true
          description: "Path to spec file"
      options:
        - name: "--strict"
          type: "flag"
          description: "Strict validation mode"
      example: "cogito validate specs/my_tool.yml --strict"

    - name: "generate"
      description: "Generate tool class from spec"
      usage: "cogito generate SPEC_PATH"
      arguments:
        - name: "spec_path"
          type: "path"
          required: true
      options:
        - name: "--output"
          type: "path"
          description: "Output directory"
      example: "cogito generate specs/my_tool.yml --output=src/tools"

    - name: "install"
      description: "Install thinking tool"
      usage: "cogito install SPEC_PATH [OPTIONS]"
      arguments:
        - name: "spec_path"
          type: "path"
          required: true
      options:
        - name: "--scope"
          type: "choice"
          choices: ["global", "project", "user"]
          default: "project"
        - name: "--override"
          type: "flag"
      example: "cogito install my_tool.yml --scope=global"

    - name: "uninstall"
      description: "Uninstall thinking tool"
      usage: "cogito uninstall TOOL_NAME [OPTIONS]"
      arguments:
        - name: "tool_name"
          type: "string"
          required: true
      options:
        - name: "--scope"
          type: "choice"
          choices: ["global", "project", "user"]
          default: "project"
      example: "cogito uninstall my_tool --scope=global"

    - name: "list"
      description: "List thinking tools"
      usage: "cogito list [OPTIONS]"
      options:
        - name: "--category"
          type: "string"
        - name: "--scope"
          type: "choice"
          choices: ["global", "project", "user", "all"]
          default: "all"
        - name: "--format"
          type: "choice"
          choices: ["table", "json", "yaml"]
          default: "table"
      example: "cogito list --category=metacognition --format=json"

    - name: "info"
      description: "Show tool information"
      usage: "cogito info TOOL_NAME"
      arguments:
        - name: "tool_name"
          type: "string"
          required: true
      example: "cogito info fresh_eyes_exercise"

    - name: "reload"
      description: "Hot-reload changed tools"
      usage: "cogito reload [TOOL_NAMES...]"
      arguments:
        - name: "tool_names"
          type: "list"
          required: false
      example: "cogito reload fresh_eyes my_custom_tool"

    - name: "create"
      description: "Create new thinking tool spec"
      usage: "cogito create [OPTIONS]"
      options:
        - name: "--name"
          type: "string"
          required: true
        - name: "--category"
          type: "choice"
          choices: ["metacognition", "review", "analysis", "planning", "debugging"]
        - name: "--template"
          type: "path"
        - name: "--interactive"
          short: "-i"
          type: "flag"
      example: "cogito create --name=my_tool --category=review --interactive"

    - name: "process-memory"
      description: "Process memory operations"
      usage: "cogito process-memory SUBCOMMAND"
      subcommands:
        - name: "query"
          description: "Query process memory"
          options:
            - name: "--type"
              type: "string"
            - name: "--tags"
              type: "list"
            - name: "--since"
              type: "date"
        - name: "export"
          description: "Export process memory"
          options:
            - name: "--output"
              type: "path"
              required: true
            - name: "--format"
              type: "choice"
              choices: ["json", "markdown"]
      example: "cogito process-memory query --type=StrategicDecision --since=2025-01-01"

    - name: "health"
      description: "Check system health"
      usage: "cogito health"
      options:
        - name: "--fix"
          type: "flag"
          description: "Auto-fix issues"
      example: "cogito health --fix"
```

---

## 3. Process Memory Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://cogito.dev/schemas/process-memory-v1.0.json",
  "title": "Process Memory Entry",
  "description": "Unified schema for process memory entries",
  "type": "object",
  "required": ["id", "type", "title", "summary", "rationale", "timestamp_created"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier"
    },
    "type": {
      "type": "string",
      "enum": [
        "StrategicDecision",
        "AlternativeConsidered",
        "FailureAnalysis",
        "LessonLearned",
        "AssumptionMade",
        "ContextualMemory",
        "MentalModels",
        "FeedbackLoops",
        "HypothesesTested",
        "ImplicitBiases",
        "Observations",
        "CollaborationMemory",
        "SystemArchetypes"
      ],
      "description": "Memory entry type"
    },
    "title": {
      "type": "string",
      "minLength": 5,
      "maxLength": 200,
      "description": "Succinct title"
    },
    "summary": {
      "type": "string",
      "minLength": 10,
      "description": "Brief description"
    },
    "rationale": {
      "type": "string",
      "minLength": 10,
      "description": "Why this memory exists"
    },
    "source_adr": {
      "type": "string",
      "format": "uri",
      "description": "Link to ADR or documentation"
    },
    "related_concepts": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Related keywords/concepts"
    },
    "timestamp_created": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp (ISO 8601)"
    },
    "timestamp_updated": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp"
    },
    "confidence_level": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "default": 1.0,
      "description": "Confidence score 0-1"
    },
    "phase": {
      "type": "string",
      "description": "Project phase"
    },
    "deprecated": {
      "type": "boolean",
      "default": false,
      "description": "Whether memory is superseded"
    },
    "provenance": {
      "type": "object",
      "properties": {
        "author": {"type": "string"},
        "system_version": {"type": "string"},
        "created_by_module": {"type": "string"}
      },
      "description": "Authorship metadata"
    },
    "links": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uuid"
      },
      "description": "Links to other memory IDs"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Categorization tags"
    }
  }
}
```

---

## 4. Error Handling Specification

### 4.1 Error Hierarchy

```python
class CogitoError(Exception):
    """Base exception for all Cogito errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_process_memory(self) -> ProcessMemoryEntry:
        """Convert error to process memory entry."""
        return ProcessMemoryEntry(
            type="FailureAnalysis",
            title=f"Error: {self.__class__.__name__}",
            summary=self.message,
            rationale="System error encountered during operation",
            provenance={"error_class": self.__class__.__name__},
            tags=["error", "system_failure"]
        )


class DiscoveryError(CogitoError):
    """Error during spec discovery."""
    pass


class ValidationError(CogitoError):
    """Error during spec validation."""

    def __init__(
        self,
        message: str,
        spec_id: str,
        validation_type: str,
        details: dict | None = None
    ):
        super().__init__(message, details)
        self.spec_id = spec_id
        self.validation_type = validation_type


class GenerationError(CogitoError):
    """Error during code generation."""
    pass


class TemplateError(CogitoError):
    """Error during template rendering."""

    def __init__(
        self,
        message: str,
        template_name: str,
        line_number: int | None = None,
        details: dict | None = None
    ):
        super().__init__(message, details)
        self.template_name = template_name
        self.line_number = line_number


class SecurityError(CogitoError):
    """Security violation detected."""

    def __init__(
        self,
        message: str,
        violation_type: str,
        severity: Literal["low", "medium", "high", "critical"],
        details: dict | None = None
    ):
        super().__init__(message, details)
        self.violation_type = violation_type
        self.severity = severity
```

### 4.2 Error Response Format

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Spec validation failed: missing required field 'description'",
    "code": "E1001",
    "severity": "high",
    "spec_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "details": {
      "field": "metadata.description",
      "validation_rule": "required_field",
      "line": 5
    },
    "suggestions": [
      "Add 'description' field to metadata section",
      "Refer to schema: https://cogito.dev/schemas/thinking-tool-spec-v1.0.json"
    ],
    "timestamp": "2025-01-14T12:34:56Z"
  }
}
```

---

## 5. Configuration Schema

```yaml
# config/cogito.yml - Complete configuration schema

# System configuration
system:
  version: "1.0.0"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  data_directory: "${PROJECT_ROOT}/.cogito"
  temp_directory: "${SYSTEM_TEMP}/cogito"

# Discovery settings
discovery:
  paths:
    global: "${COGITO_HOME}/specs"
    project: "${PROJECT_ROOT}/.cogito/thinking_tools"
    user: "${USER_HOME}/.cogito/thinking_tools"

  watch: true
  interval_seconds: 30
  ignore_patterns:
    - "*.bak"
    - "*.tmp"
    - "__pycache__"

  parallel: true
  max_workers: 4

# Validation settings
validation:
  strict_mode: true
  fail_fast: false  # Continue validating after first error

  schema_validation:
    enabled: true
    cache_schemas: true

  security_validation:
    enabled: true
    sandbox_templates: true
    max_execution_time_ms: 5000
    max_memory_mb: 50
    scan_for_injection: true

  quality_validation:
    enabled: true
    require_documentation: true
    require_examples: false
    min_description_length: 10
    max_template_size_kb: 100

# Generation settings
generation:
  output_directory: "src/cogito/tools/generated"
  template_path: "${COGITO_HOME}/templates/tool_class.py.j2"

  auto_import: true
  auto_format: true
  auto_typecheck: false  # Requires mypy

  naming_convention: "PascalCase"
  file_naming: "generated_{tool_name}.py"

  include_spec_metadata: true
  include_docstrings: true
  include_type_hints: true

# Process memory settings
process_memory:
  enabled: true
  storage_path: "${PROJECT_ROOT}/.cogito/process_memory"

  capture_execution: true
  capture_failures: true
  capture_validations: false

  retention_days: 365
  auto_cleanup: true

  indexing:
    enabled: true
    rebuild_on_startup: false

  export:
    auto_export: false
    export_path: "${PROJECT_ROOT}/.cogito/exports"
    format: "jsonl"  # jsonl, json, markdown

# Performance settings
performance:
  cache_enabled: true
  cache_ttl_seconds: 3600
  max_cache_size_mb: 100

  lazy_loading: true
  precompile_templates: true

  parallel_processing:
    enabled: true
    max_workers: 4

# Integration settings
integration:
  serena:
    enabled: true
    auto_register: true
    namespace: "cogito"

  mcp:
    enabled: true
    expose_all_tools: true

# CLI settings
cli:
  color_output: true
  progress_bars: true
  interactive_prompts: true

  defaults:
    validation_strict: true
    installation_scope: "project"

# Telemetry settings (opt-in)
telemetry:
  enabled: false  # Must be explicitly enabled
  anonymous: true
  endpoint: "https://telemetry.cogito.dev/v1/events"

  collect:
    - usage_statistics
    - error_reports
    - performance_metrics

  exclude:
    - tool_contents
    - parameter_values
    - user_data
```

---

## 6. Extension Points

### 6.1 Plugin System Specification

```python
class ThinkingToolPlugin(Protocol):
    """
    Protocol for Cogito plugins.

    Plugins can extend Cogito with:
    - Custom validators
    - Custom generators
    - Custom template filters
    - Custom CLI commands
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        ...

    @property
    def version(self) -> str:
        """Plugin version (semver)."""
        ...

    def initialize(self, manager: ThinkingToolsManager) -> None:
        """
        Initialize plugin with access to manager.

        Args:
            manager: ThinkingToolsManager instance
        """
        ...

    def register_validators(self) -> list[Validator]:
        """
        Register custom validators.

        Returns:
            List of validator instances
        """
        ...

    def register_generators(self) -> list[Generator]:
        """
        Register custom code generators.

        Returns:
            List of generator instances
        """
        ...

    def register_template_filters(self) -> dict[str, Callable]:
        """
        Register custom Jinja2 filters.

        Returns:
            Mapping of filter name to filter function
        """
        ...

    def register_cli_commands(self) -> list[CLICommand]:
        """
        Register custom CLI commands.

        Returns:
            List of CLI command definitions
        """
        ...


# Example plugin registration
def register_plugin(plugin: ThinkingToolPlugin) -> None:
    """
    Register a plugin with Cogito.

    Plugins must be registered before calling ThinkingToolsManager.__init__()
    """
    PLUGIN_REGISTRY[plugin.name] = plugin
```

### 6.2 Hook System Specification

```python
class HookRegistry:
    """
    Registry for lifecycle hooks.

    Hooks allow plugins and extensions to inject behavior
    at specific points in the Cogito lifecycle.
    """

    # Discovery hooks
    @hook("before_discovery")
    def before_discovery(self, scan_paths: list[Path]) -> None:
        """Called before spec discovery starts."""
        ...

    @hook("after_discovery")
    def after_discovery(self, result: DiscoveryResult) -> None:
        """Called after spec discovery completes."""
        ...

    # Validation hooks
    @hook("before_validation")
    def before_validation(self, spec: ThinkingToolSpec) -> None:
        """Called before validating a spec."""
        ...

    @hook("after_validation")
    def after_validation(
        self,
        spec: ThinkingToolSpec,
        result: ValidationResult
    ) -> None:
        """Called after validation completes."""
        ...

    # Generation hooks
    @hook("before_generation")
    def before_generation(self, spec: ThinkingToolSpec) -> None:
        """Called before code generation."""
        ...

    @hook("after_generation")
    def after_generation(
        self,
        spec: ThinkingToolSpec,
        code: GeneratedTool
    ) -> None:
        """Called after code generation."""
        ...

    # Template rendering hooks
    @hook("before_template_render")
    def before_template_render(
        self,
        template: str,
        context: dict
    ) -> tuple[str, dict]:
        """
        Called before rendering template.
        Can modify template or context.
        """
        ...

    @hook("after_template_render")
    def after_template_render(
        self,
        template: str,
        context: dict,
        result: str
    ) -> str:
        """
        Called after rendering template.
        Can modify result.
        """
        ...

    # Process memory hooks
    @hook("before_memory_store")
    def before_memory_store(
        self,
        memory: ProcessMemoryEntry
    ) -> ProcessMemoryEntry:
        """
        Called before storing memory.
        Can modify memory entry.
        """
        ...
```

---

## 7. Testing Specification

### 7.1 Test Coverage Requirements

```yaml
test_coverage:
  overall: 0.90  # 90% minimum
  critical_paths: 1.00  # 100% for security, validation

  per_component:
    spec_loader: 0.95
    validator: 1.00  # Critical path
    generator: 0.95
    template_engine: 1.00  # Security critical
    process_memory: 0.90
    cli: 0.85
```

### 7.2 Test Categories

```python
# Unit tests
class TestSpecLoader(unittest.TestCase):
    """Unit tests for SpecLoader component."""

    def test_load_valid_spec(self):
        """Should load and parse valid YAML spec."""
        ...

    def test_load_invalid_yaml(self):
        """Should raise error for malformed YAML."""
        ...

    def test_normalize_spec(self):
        """Should convert to canonical form."""
        ...


# Integration tests
class TestEndToEndFlow(unittest.TestCase):
    """Integration tests for complete workflows."""

    def test_discover_validate_generate(self):
        """Should discover, validate, and generate tools."""
        ...

    def test_hot_reload(self):
        """Should detect changes and reload tools."""
        ...


# Security tests
class TestTemplateSecurity(unittest.TestCase):
    """Security tests for template rendering."""

    def test_prevent_code_injection(self):
        """Should prevent template code injection."""
        ...

    def test_resource_limits(self):
        """Should enforce execution time and memory limits."""
        ...


# Performance tests
class TestPerformance(unittest.TestCase):
    """Performance benchmark tests."""

    def test_discovery_performance(self):
        """Discovery should complete in <100ms for 1000 specs."""
        ...

    def test_validation_performance(self):
        """Validation should complete in <50ms per spec."""
        ...
```

---

## Summary

This Framework Specification provides:

✅ **Complete JSON Schemas** for specs and process memory
✅ **Formal API Protocols** with type signatures
✅ **CLI Specification** with all commands
✅ **Configuration Schema** with all settings
✅ **Error Handling** hierarchy and formats
✅ **Extension Points** via plugins and hooks
✅ **Testing Requirements** with coverage targets

All specifications are **machine-readable** and designed for **autonomous AI implementation**.

---

**Next**: Architecture Decision Records (ADRs) documenting key design choices

**Document Status**: Framework Specification v1.0.0 Complete
**Owner**: AI System Architect
**Last Updated**: 2025-01-14
