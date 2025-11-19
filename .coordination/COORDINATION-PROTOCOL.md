# Coordination Protocol for Asynchronous Project Management

**Version:** 1.0
**Purpose:** Enable asynchronous coordination between project coordinators (external Claude instances) and project instances (in-project Claude instances) without requiring synchronous interaction.

---

## Overview

The Coordination Protocol provides structured communication between:
- **Coordinator:** External Claude instance (e.g., running in Serena) providing strategic direction
- **Project Instance:** Claude instance running within the project, executing implementation work
- **System:** Automated processes, quality gates, CI/CD pipelines

This enables the **strategic partnership model** where:
- Coordinator provides direction, priorities, strategic decisions
- Project instance makes autonomous technical decisions and executes implementation
- Communication is asynchronous via JSON files with schema validation

---

## Directory Structure

```
project-root/
├── .coordination/
│   ├── messages.jsonl          # Append-only message log
│   ├── inbox/                   # Unread messages for project instance
│   │   └── msg-*.json
│   ├── outbox/                  # Messages from project instance
│   │   └── msg-*.json
│   └── archive/                 # Processed messages
│       └── YYYY-MM-DD/
│           └── msg-*.json
├── .progress/
│   ├── current-task.json        # Current task status
│   ├── completed-tasks.jsonl    # History of completed tasks
│   └── metrics.json             # Cumulative metrics
└── schemas/
    ├── coordination-message-v1.0.schema.json
    └── task-progress-v1.0.schema.json
```

---

## Message Types

### 1. Directive (Coordinator → Project Instance)
**Purpose:** Provide task assignment, priority change, or strategic direction

**Example:**
```json
{
  "id": "msg-20251116-153045",
  "from": "coordinator",
  "to": "project-instance",
  "timestamp": "2025-11-16T15:30:45Z",
  "type": "directive",
  "priority": "high",
  "content": "Implement Layer 3 (Processing) - TemplateRenderer class. Focus on security (sandboxed Jinja2 per PM-002). Target: Week 1 completion.",
  "references": ["layer3-renderer-implementation"],
  "metadata": {
    "task_id": "layer3-renderer-implementation"
  },
  "read": false
}
```

### 2. Question (Project Instance → Coordinator)
**Purpose:** Request clarification on ambiguous requirements or strategic decisions

**When to use:**
- Genuine ambiguity not covered by process memory or CLAUDE.md
- Need for priority/scope decision
- Strategic direction choice (not technical implementation)

**Example:**
```json
{
  "id": "msg-20251116-160000",
  "from": "project-instance",
  "to": "coordinator",
  "timestamp": "2025-11-16T16:00:00Z",
  "type": "question",
  "priority": "normal",
  "content": "Should we prioritize Layer 3 test coverage (>90%) or move to Layer 2 integration after basic renderer works (>70% coverage)?",
  "references": ["layer3-renderer-implementation"],
  "metadata": {
    "task_id": "layer3-renderer-implementation",
    "context": "Week 1 timeline may be tight for >90% coverage"
  },
  "read": false
}
```

### 3. Response (Coordinator → Project Instance)
**Purpose:** Answer questions from project instance

**Example:**
```json
{
  "id": "msg-20251116-163000",
  "from": "coordinator",
  "to": "project-instance",
  "timestamp": "2025-11-16T16:30:00Z",
  "type": "response",
  "priority": "normal",
  "content": "Prioritize test coverage >90% for Layer 3. Solid foundation more important than speed. Adjust timeline if needed.",
  "references": ["msg-20251116-160000", "layer3-renderer-implementation"],
  "read": false
}
```

### 4. Progress (Project Instance → Coordinator)
**Purpose:** Report progress on current task

**Example:**
```json
{
  "id": "msg-20251116-170000",
  "from": "project-instance",
  "to": "coordinator",
  "timestamp": "2025-11-16T17:00:00Z",
  "type": "progress",
  "content": "TemplateRenderer implemented with 15 unit tests. Quality gates: mypy ✓, ruff ✓, black ✓, pytest 87% coverage. Targeting 90% by EOD.",
  "references": ["layer3-renderer-implementation"],
  "metadata": {
    "task_id": "layer3-renderer-implementation",
    "artifacts": [
      "src/cogito/processing/renderer.py",
      "tests/unit/test_renderer.py"
    ],
    "quality_gates": {
      "mypy": {"status": "passed", "errors": 0},
      "ruff": {"status": "passed", "violations": 0},
      "black": {"status": "passed"},
      "pytest": {"status": "passed", "coverage_percent": 87}
    }
  },
  "read": false
}
```

### 5. Blocker (Project Instance → Coordinator)
**Purpose:** Report blocking issue requiring coordinator intervention

**Example:**
```json
{
  "id": "msg-20251116-180000",
  "from": "project-instance",
  "to": "coordinator",
  "timestamp": "2025-11-16T18:00:00Z",
  "type": "blocker",
  "priority": "urgent",
  "content": "Cannot proceed with Layer 2 integration tests - missing specification for tool discovery protocol. Need clarification on auto-discovery vs. registry pattern.",
  "references": ["layer2-orchestration"],
  "metadata": {
    "task_id": "layer2-orchestration",
    "blocker_type": "missing_information"
  },
  "read": false
}
```

### 6. Completion (Project Instance → Coordinator)
**Purpose:** Report task completion with artifacts and quality gate results

**Example:**
```json
{
  "id": "msg-20251118-120000",
  "from": "project-instance",
  "to": "coordinator",
  "timestamp": "2025-11-18T12:00:00Z",
  "type": "completion",
  "content": "Layer 3 (Processing) complete. TemplateRenderer + ParameterValidator implemented with 92% test coverage. All quality gates passed. Ready for Layer 2.",
  "references": ["layer3-renderer-implementation"],
  "metadata": {
    "task_id": "layer3-renderer-implementation",
    "artifacts": [
      "src/cogito/processing/renderer.py",
      "src/cogito/processing/validator.py",
      "src/cogito/processing/__init__.py",
      "tests/unit/test_renderer.py",
      "tests/unit/test_validator.py"
    ],
    "quality_gates": {
      "mypy": {"status": "passed", "errors": 0},
      "ruff": {"status": "passed", "violations": 0},
      "black": {"status": "passed"},
      "pytest": {"status": "passed", "passed": 28, "failed": 0, "coverage_percent": 92},
      "validation": {"status": "passed", "tools_validated": 9}
    },
    "metrics": {
      "lines_of_code": 450,
      "test_count": 28,
      "time_spent_minutes": 180
    }
  },
  "read": false
}
```

### 7. Error (Project Instance → Coordinator)
**Purpose:** Report unexpected errors or failures

**Example:**
```json
{
  "id": "msg-20251116-190000",
  "from": "project-instance",
  "to": "coordinator",
  "timestamp": "2025-11-16T19:00:00Z",
  "type": "error",
  "priority": "high",
  "content": "Quality gate failure: 3 type errors in renderer.py after refactoring. Rolling back changes. Will fix and retry.",
  "references": ["layer3-renderer-implementation"],
  "metadata": {
    "task_id": "layer3-renderer-implementation",
    "error_type": "quality_gate_failure",
    "quality_gates": {
      "mypy": {"status": "failed", "errors": 3}
    }
  },
  "read": false
}
```

---

## Workflows

### Project Instance Workflow

**On session start:**
1. Check `.coordination/inbox/` for new messages
2. Process messages in timestamp order
3. Move processed messages to `.coordination/archive/YYYY-MM-DD/`
4. Load current task from `.progress/current-task.json`

**During work:**
1. Update `.progress/current-task.json` after each significant step
2. Append progress update to `.coordination/messages.jsonl` after significant milestones
3. Create message files in `.coordination/outbox/` only when blocked or have questions

**When blocked:**
1. Update `.progress/current-task.json` with blocker details
2. Post blocker message to coordinator
3. Continue with other work if possible

**On task completion:**
1. Run all quality gates
2. Update `.progress/current-task.json` to "completed"
3. Append to `.progress/completed-tasks.jsonl`
4. Post completion message with artifacts and metrics
5. Archive task to `.progress/archive/`

### Coordinator Workflow

**Checking progress:**
```bash
# Read current status
cat .progress/current-task.json | jq .

# Check for new messages
ls .coordination/outbox/

# Read recent progress
tail -10 .coordination/messages.jsonl | jq .

# Check for blockers
jq 'select(.blocked_on != null)' .progress/current-task.json
```

**Sending directives:**
```bash
# Create message file
cat > .coordination/inbox/msg-$(date +%Y%m%d-%H%M%S).json << 'EOF'
{
  "id": "msg-20251116-153045",
  "from": "coordinator",
  "to": "project-instance",
  "timestamp": "2025-11-16T15:30:45Z",
  "type": "directive",
  "content": "Implement Layer 3 Processing",
  "priority": "high",
  "read": false
}
EOF

# Append to message log
cat .coordination/inbox/msg-*.json >> .coordination/messages.jsonl
```

**Responding to questions:**
```bash
# Read question
cat .coordination/outbox/msg-20251116-160000.json

# Create response
cat > .coordination/inbox/msg-$(date +%Y%m%d-%H%M%S).json << 'EOF'
{
  "id": "msg-20251116-163000",
  "from": "coordinator",
  "to": "project-instance",
  "timestamp": "2025-11-16T16:30:00Z",
  "type": "response",
  "content": "Prioritize test coverage >90%",
  "references": ["msg-20251116-160000"],
  "read": false
}
EOF
```

---

## Task Progress Tracking

### Current Task (`current-task.json`)

**Example:**
```json
{
  "task_id": "layer3-renderer-implementation",
  "task_name": "Layer 3 Processing - Template Renderer",
  "phase": "implementation",
  "started": "2025-11-16T15:00:00Z",
  "updated": "2025-11-16T17:30:00Z",
  "estimated_completion": "2025-11-18T18:00:00Z",
  "status": "in_progress",
  "current_step": "implementing_parameter_validation",
  "completed_steps": [
    "design_approved",
    "created_renderer_class",
    "implemented_sandboxed_environment",
    "created_unit_tests",
    "renderer_tests_passing"
  ],
  "remaining_steps": [
    "implement_parameter_validator",
    "create_validator_tests",
    "integration_test_with_real_tools",
    "documentation",
    "final_quality_gates"
  ],
  "blocked_on": null,
  "questions_for_coordinator": [],
  "artifacts": [
    {
      "path": "src/cogito/processing/renderer.py",
      "type": "source_code",
      "status": "complete",
      "created_at": "2025-11-16T15:30:00Z"
    },
    {
      "path": "tests/unit/test_renderer.py",
      "type": "test",
      "status": "complete",
      "created_at": "2025-11-16T16:00:00Z"
    },
    {
      "path": "src/cogito/processing/validator.py",
      "type": "source_code",
      "status": "draft",
      "created_at": "2025-11-16T17:00:00Z"
    }
  ],
  "quality_gates": {
    "mypy": {
      "status": "passed",
      "last_run": "2025-11-16T17:15:00Z",
      "errors": 0
    },
    "ruff": {
      "status": "passed",
      "last_run": "2025-11-16T17:15:00Z",
      "violations": 0
    },
    "black": {
      "status": "passed",
      "last_run": "2025-11-16T17:15:00Z"
    },
    "pytest": {
      "status": "passed",
      "last_run": "2025-11-16T17:20:00Z",
      "passed": 15,
      "failed": 0,
      "coverage_percent": 87
    },
    "validation": {
      "status": "not_run"
    }
  },
  "metrics": {
    "lines_of_code": 320,
    "test_count": 15,
    "time_spent_minutes": 150
  }
}
```

---

## Best Practices

### For Project Instances

**DO:**
- Update `.progress/current-task.json` after every significant step
- Append to `.coordination/messages.jsonl` after significant milestones
- Ask questions only for genuine ambiguity (not technical decisions)
- Post to `.coordination/outbox/` when blocked or needing strategic direction
- Include quality gate results in completion messages
- List all artifacts created/modified

**DON'T:**
- Ask coordinator for technical implementation decisions
- Post messages for trivial updates
- Leave blockers unreported
- Forget to run quality gates before completion
- Ignore messages in inbox

### For Coordinators

**DO:**
- Check progress regularly but asynchronously
- Provide clear directives with context and priorities
- Respond to blockers promptly
- Acknowledge completion messages
- Review quality gate results

**DON'T:**
- Micromanage technical decisions
- Interrupt mid-task without good reason
- Leave questions unanswered
- Override autonomous technical decisions without strong rationale

---

## Integration with CLAUDE.md

Add to project's CLAUDE.md:

```markdown
## Coordination Protocol

This project uses asynchronous coordination for strategic oversight.

**Your Responsibilities:**

1. **Check inbox on session start:**
   ```bash
   ls .coordination/inbox/
   cat .coordination/inbox/msg-*.json
   ```

2. **Update progress after significant steps:**
   - After each significant step: Update `.progress/current-task.json`
   - After major milestones: Append progress to `.coordination/messages.jsonl`
   - On completion: Post completion message with artifacts and quality gates

3. **Post questions for strategic decisions only:**
   - Genuine ambiguity not covered in docs
   - Priority/scope trade-offs
   - Strategic direction choices
   - NOT for technical implementation details

4. **Report blockers immediately:**
   - Update current-task.json with blocker
   - Post blocker message with details
   - Continue other work if possible

See `.coordination/COORDINATION-PROTOCOL.md` for complete protocol.
```

---

## Schema Validation

**Validate messages:**
```bash
# Validate coordination message
python3 -c "
import json
import jsonschema
import sys

with open('schemas/coordination-message-v1.0.schema.json') as f:
    schema = json.load(f)

with open(sys.argv[1]) as f:
    message = json.load(f)

jsonschema.validate(instance=message, schema=schema)
print('✓ Valid')
" .coordination/inbox/msg-*.json
```

**Validate task progress:**
```bash
# Validate task progress
python3 -c "
import json
import jsonschema

with open('schemas/task-progress-v1.0.schema.json') as f:
    schema = json.load(f)

with open('.progress/current-task.json') as f:
    task = json.load(f)

jsonschema.validate(instance=task, schema=schema)
print('✓ Valid')
"
```

---

## Future Enhancements

- **Web dashboard** for visual progress monitoring
- **GitHub Actions integration** for automated quality gate reporting
- **Slack/Discord webhooks** for real-time notifications
- **AI-powered blocker resolution suggestions**
- **Automated task breakdown** from high-level directives

---

**This protocol enables true strategic partnership: coordinator provides direction, project instance executes autonomously, communication is asynchronous and structured.**
