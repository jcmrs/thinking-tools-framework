# Prompt Engineering Issue: Instance Stalling on Priority 5

## Incident Report

**Date**: 2025-11-19
**Priority**: 5 (Python Contracts/Protocols)
**Issue**: Instance created todos, acknowledged start, but did not execute first step

## User Observation

> "Observation: the instance processed the message, created the todo list, then said it would start, but did not continue. Something with the prompt/instruction? I have told it manually to proceed."

## Root Cause Analysis

### Suspected Issue: Validation Questions Creating Decision Paralysis

**Problematic Pattern in Directive**:
```json
{
  "step_1_understand_layer_interfaces": {
    "action": "Read existing layer implementations to understand their public APIs",
    "tools": [
      "get_symbols_overview file_path='src/cogito/orchestration/executor.py'",
      ...
    ],
    "validation": "Can you list the public methods each layer exposes?",
    "next": "Proceed to step 2 once you understand existing interfaces"
  }
}
```

**Why This Causes Stalling**:
1. **Validation as Question**: "Can you list the public methods..." sounds like asking user for confirmation
2. **"Once you understand" condition**: Creates ambiguity about when to proceed
3. **Instance interprets as checkpoint**: Waits for user signal instead of autonomous execution

### Contrast with Working Prompts (Priority 3, 4)

**Priority 3 Enhanced (WORKED - 14 min session)**:
```json
{
  "step_1": {
    "action": "Read schema file",
    "tool": "Read file_path='schemas/thinking-tool-v1.0.schema.json'",
    "validation": "Schema loaded successfully",
    "expected": "JSON schema with required fields",
    "next": "Proceed to step 2"
  }
}
```

**Key Difference**: 
- ✓ "Schema loaded successfully" = STATEMENT (autonomous validation)
- ✗ "Can you list the public methods..." = QUESTION (waits for user)

## The Pattern That Works vs Doesn't Work

### ✓ WORKS: Declarative Validation (Autonomous)
```json
{
  "validation": "All tests pass",
  "expected": "pytest shows 451 passed, 0 failed"
}
```
**Instance behavior**: Runs pytest, checks output, proceeds

### ✗ DOESN'T WORK: Interrogative Validation (User-Directed)
```json
{
  "validation": "Can you list the public methods each layer exposes?",
  "next": "Proceed to step 2 once you understand existing interfaces"
}
```
**Instance behavior**: Creates todos, reports understanding, **WAITS FOR USER**

## Why This Matters for Execution-Heavy Prompts

**Execution Mode Definition** (from directive):
> "Execution agent: Design → Implement → Validate → Report. Minimal reasoning commentary."

**Contradiction**:
- Role says: "Execution agent" (autonomous)
- Validation says: "Can you list..." (interactive checkpoint)
- Instance prioritizes: Interactive interpretation (safer)

**Result**: Instance stalls, waiting for user confirmation

## The Fix: Remove All Interrogative Language

### Before (Causes Stalling)
```json
{
  "validation": "Can you list the public methods each layer exposes?",
  "next": "Proceed to step 2 once you understand existing interfaces"
}
```

### After (Enables Autonomous Execution)
```json
{
  "validation": "Layer interfaces discovered via get_symbols_overview",
  "expected": "Public methods identified for executor, registry, renderer, validator",
  "next": "Proceed to step 2"
}
```

**Changes**:
1. "Can you list..." → "Layer interfaces discovered"
2. "once you understand" → Removed (unconditional next step)
3. Question format → Statement format

## Broader Implications

### For Hypothesis 1 (Reasoning Cost)

**Still Valid**: Execution is cheaper than reasoning

**New Finding**: **Interrogative language triggers reasoning mode**
- Question format → Instance enters "answer question" mode
- Requires reasoning about "do I have enough understanding?"
- Burns tokens generating explanation
- **Then waits for user validation of explanation**

### For Hypothesis 2 (Request Frequency)

**Compounding Effect**: Stalling + interrogative language = DOUBLE TOKEN BURN
1. Instance reasons about question
2. Generates explanation (high tokens)
3. Waits for user (no tool execution gaps)
4. No natural pacing (reasoning-heavy pattern resumes after user signal)

**Result**: Defeats purpose of execution-heavy prompt

## Directive Template Anti-Patterns Identified

### ❌ Anti-Pattern 1: Interrogative Validation
```json
"validation": "Can you...?", "Do you...?", "Are you able to...?"
```

### ❌ Anti-Pattern 2: Conditional Next Steps
```json
"next": "Proceed to step X once you understand/confirm/verify..."
```

### ❌ Anti-Pattern 3: Ambiguous Completion Criteria
```json
"validation": "Ensure code quality is good"
```

### ✓ Pattern: Declarative, Binary, Unconditional

```json
{
  "action": "Run pytest to validate all tests",
  "tool": "Bash command='pytest tests/ -v'",
  "validation": "All tests pass",
  "expected": "pytest output shows '451 passed, 0 failed'",
  "next": "Proceed to step 2"
}
```

## Updated Directive Template Guidelines

### Role Definition
```json
{
  "execution_mode": "Autonomous execution agent: Execute → Validate → Proceed. No user checkpoints.",
  "autonomy": "Full autonomy. Do not wait for user confirmation between steps."
}
```

### Step Structure (CORRECTED)
```json
{
  "step_N": {
    "action": "IMPERATIVE VERB + specific action",
    "tool": "Exact tool call with parameters",
    "validation": "DECLARATIVE statement of success condition",
    "expected": "Binary verification criteria",
    "next": "Proceed to step N+1"  // NO CONDITIONS
  }
}
```

### Forbidden Language
- ❌ "Can you...?"
- ❌ "Do you...?"
- ❌ "Once you understand..."
- ❌ "When you're ready..."
- ❌ "If successful..."
- ❌ "Ensure that..."
- ❌ "Make sure..."

### Required Language
- ✓ "Run [tool]"
- ✓ "Execute [command]"
- ✓ "Create [file]"
- ✓ "Validation: [declarative statement]"
- ✓ "Expected: [binary criteria]"
- ✓ "Proceed to step N" (unconditional)

## Immediate Fix for Priority 5

**Option 1: Let it run** (user manually told it to proceed)
- Monitor completion
- Note any other stalling points
- Measure actual vs expected session duration

**Option 2: Issue corrected directive** (restart with fixed prompt)
- Remove all interrogative validation
- Make all next steps unconditional
- Risk: Loses any progress made

**Recommendation**: Option 1 (user already intervened, let it complete)

## Process Improvement

### For Future Directives (Priority 6+)

**Pre-Flight Checklist** (before creating directive):
1. ✓ All validations are declarative statements (not questions)
2. ✓ All "next" steps are unconditional (no "once you...")
3. ✓ All expectations are binary (pass/fail, yes/no)
4. ✓ No ambiguous quality statements ("ensure good code")
5. ✓ Role definition explicitly states "autonomous, no checkpoints"

**Automated Check** (future):
```bash
# Scan directive for anti-patterns
grep -E "(Can you|Do you|Are you|once you|when you|if you)" directive.json
# Should return 0 matches
```

## Updated Token Economics Model

**Previous Model**:
```
Token cost = Reasoning_tokens + Tool_result_tokens
```

**Updated Model**:
```
Token cost = Reasoning_tokens + Tool_result_tokens + Stalling_penalty

Where:
  Stalling_penalty = f(interrogative_language, conditional_steps, ambiguous_validation)
  
  Interrogative language → "Answer question" mode → High reasoning tokens + User wait
  Conditional steps → Decision paralysis → Unclear when to proceed
  Ambiguous validation → Can't verify completion → Waits for user signal
```

## Cross-References

**Related Memories**:
- `reasoning-cost-hypothesis-token-economics.md`: Reasoning vs execution cost
- `request-pattern-hypothesis-rate-limits.md`: Request frequency and pacing
- `priority3-prompt-engineering-application.md`: First enhanced directive attempt

**Lessons Learned**:
- Priority 3 worked (14 min) because validations were declarative
- Priority 5 stalled because validations were interrogative
- **Execution-heavy ≠ just tool calls, also requires autonomous language**

## Conclusion

**Root Cause**: Interrogative validation language creates decision paralysis

**Mechanism**: "Can you...?" triggers interactive checkpoint mode, not execution mode

**Fix**: Use only declarative, binary, unconditional step structures

**Impact**: Critical for achieving 95% execution, 5% reasoning target

**Status**: Priority 5 allowed to continue (user intervened), future directives will use corrected template
