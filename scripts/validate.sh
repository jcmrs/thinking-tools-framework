#!/usr/bin/env bash
#
# Thinking Tools Framework - Validation Script
#
# Purpose: Validate thinking tool YAML files against JSON schema
# Usage: ./validate.sh [path/to/tools/directory]
#
# This script:
# - Finds all *.yml files in specified directory (or examples/ by default)
# - Validates each against thinking-tool-v1.0.schema.json
# - Reports errors with context and line numbers
# - Exits with non-zero status if any validation fails
#
# Requirements:
# - Python 3.11+ with jsonschema, pyyaml

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="${1:-$PROJECT_ROOT/examples}"
SCHEMA_PATH="$PROJECT_ROOT/schemas/thinking-tool-v1.0.schema.json"

# Colors
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# ============================================================================
# Utility Functions
# ============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ============================================================================
# Validation
# ============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi

    # Check if required Python packages are available
    if ! python3 -c "import jsonschema, yaml" 2>/dev/null; then
        log_error "Required Python packages not found"
        log_info "Please install: pip install jsonschema pyyaml"
        exit 1
    fi

    if [[ ! -f "$SCHEMA_PATH" ]]; then
        log_error "Schema file not found: $SCHEMA_PATH"
        exit 1
    fi

    if [[ ! -d "$TOOLS_DIR" ]]; then
        log_error "Tools directory not found: $TOOLS_DIR"
        exit 1
    fi

    log_success "Prerequisites OK"
}

validate_tools() {
    log_info "Validating thinking tools in: $TOOLS_DIR"
    echo ""

    local total=0
    local passed=0
    local failed=0

    # Find all .yml files
    while IFS= read -r -d '' tool_file; do
        ((total++))

        local tool_name
        tool_name=$(basename "$tool_file")

        # Validate using Python
        if python3 - "$tool_file" "$SCHEMA_PATH" << 'PYTHON_VALIDATOR'
import sys
import json
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError

def main():
    tool_file = Path(sys.argv[1])
    schema_file = Path(sys.argv[2])

    # Load tool YAML
    try:
        with open(tool_file, 'r', encoding='utf-8') as f:
            tool_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"YAML Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading tool: {e}", file=sys.stderr)
        sys.exit(1)

    # Load schema
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    try:
        validate(instance=tool_data, schema=schema)
        print("VALID")
        sys.exit(0)
    except ValidationError as e:
        print(f"Validation Error: {e.message}", file=sys.stderr)
        if e.path:
            path_str = '.'.join(str(p) for p in e.path)
            print(f"  At path: {path_str}", file=sys.stderr)
        if e.schema_path:
            schema_path_str = '.'.join(str(p) for p in e.schema_path)
            print(f"  Schema path: {schema_path_str}", file=sys.stderr)
        sys.exit(1)
    except SchemaError as e:
        print(f"Schema Error: {e.message}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
PYTHON_VALIDATOR
        then
            log_success "$tool_name"
            ((passed++))
        else
            log_error "$tool_name - FAILED"
            ((failed++))
        fi
    done < <(find "$TOOLS_DIR" -name "*.yml" -type f -print0)

    echo ""
    echo "=========================================="
    echo "Validation Summary"
    echo "=========================================="
    echo "Total tools: $total"
    echo -e "${GREEN}Passed: $passed${NC}"
    if [[ $failed -gt 0 ]]; then
        echo -e "${RED}Failed: $failed${NC}"
    else
        echo "Failed: 0"
    fi
    echo "=========================================="

    if [[ $failed -gt 0 ]]; then
        exit 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "Thinking Tools Validator"
    echo "=========================================="
    echo ""

    check_prerequisites
    validate_tools

    log_success "All validations passed!"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
