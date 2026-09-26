#!/bin/bash
# ABOUTME: Test runner stage supporting unit, integration, and E2E tests
# ABOUTME: Uses Factory.ai droids or native test frameworks with coverage reporting

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/multi-ai-workflow.yaml"
REPORT_DIR="${REPO_ROOT}/reports/ai-workflow"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

# Usage
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Test runner stage for comprehensive testing.

OPTIONS:
    -l, --levels LEVELS     Comma-separated test levels: unit,integration,e2e (default: all)
    -c, --coverage          Enable coverage reporting
    -t, --threshold PCT     Coverage threshold percentage (default: 80)
    -f, --framework FW      Force test framework: pytest,jest,mocha,native
    -r, --report FILE       Output report file path
    --use-factory           Use Factory.ai droids for testing
    --use-gemini            Use Gemini for test generation
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0") --levels unit,integration --coverage
    $(basename "$0") --use-factory --levels e2e
    $(basename "$0") --coverage --threshold 90
EOF
}

# Parse arguments
LEVELS="unit,integration,e2e"
COVERAGE=false
THRESHOLD=80
FRAMEWORK=""
REPORT_FILE=""
USE_FACTORY=false
USE_GEMINI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--levels) LEVELS="$2"; shift 2 ;;
        -c|--coverage) COVERAGE=true; shift ;;
        -t|--threshold) THRESHOLD="$2"; shift 2 ;;
        -f|--framework) FRAMEWORK="$2"; shift 2 ;;
        -r|--report) REPORT_FILE="$2"; shift 2 ;;
        --use-factory) USE_FACTORY=true; shift ;;
        --use-gemini) USE_GEMINI=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Create report directory
mkdir -p "$REPORT_DIR"

# Set default report file
if [[ -z "$REPORT_FILE" ]]; then
    REPORT_FILE="${REPORT_DIR}/test-runner-$(date +%Y%m%d-%H%M%S).json"
fi

# Detect test framework
detect_framework() {
    if [[ -n "$FRAMEWORK" ]]; then
        echo "$FRAMEWORK"
        return
    fi

    # Check for Python
    if [[ -f "pytest.ini" ]] || [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]]; then
        if command -v pytest &>/dev/null; then
            echo "pytest"
            return
        fi
    fi

    # Check for Node.js
    if [[ -f "package.json" ]]; then
        if grep -q '"jest"' package.json 2>/dev/null; then
            echo "jest"
            return
        fi
        if grep -q '"mocha"' package.json 2>/dev/null; then
            echo "mocha"
            return
        fi
    fi

    # Check for bash tests
    if [[ -d "tests" ]] && ls tests/*.sh &>/dev/null; then
        echo "native"
        return
    fi

    echo "none"
}

# Run pytest tests
run_pytest() {
    local level="$1"
    local test_dir=""
    local pytest_args="-v"

    case "$level" in
        unit) test_dir="tests/unit" ;;
        integration) test_dir="tests/integration" ;;
        e2e) test_dir="tests/e2e" ;;
    esac

    # Check if directory exists
    if [[ ! -d "$test_dir" ]]; then
        log_warn "Test directory not found: $test_dir"
        echo '{"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "status": "skipped"}'
        return 0
    fi

    # Add coverage if enabled
    if [[ "$COVERAGE" == "true" ]]; then
        pytest_args+=" --cov=src --cov-report=json:coverage-${level}.json"
    fi

    log_test "Running pytest $level tests..."

    local output
    local exit_code=0
    output=$(pytest "$test_dir" $pytest_args --json-report --json-report-file="pytest-${level}.json" 2>&1) || exit_code=$?

    # Parse results
    if [[ -f "pytest-${level}.json" ]]; then
        local passed failed skipped errors
        passed=$(jq '.summary.passed // 0' "pytest-${level}.json")
        failed=$(jq '.summary.failed // 0' "pytest-${level}.json")
        skipped=$(jq '.summary.skipped // 0' "pytest-${level}.json")
        errors=$(jq '.summary.error // 0' "pytest-${level}.json")

        local status="passed"
        if [[ $exit_code -ne 0 ]] || [[ $failed -gt 0 ]] || [[ $errors -gt 0 ]]; then
            status="failed"
        fi

        echo "{\"passed\": $passed, \"failed\": $failed, \"skipped\": $skipped, \"errors\": $errors, \"status\": \"$status\"}"
    else
        if [[ $exit_code -eq 0 ]]; then
            echo '{"passed": 1, "failed": 0, "skipped": 0, "errors": 0, "status": "passed"}'
        else
            echo '{"passed": 0, "failed": 1, "skipped": 0, "errors": 0, "status": "failed"}'
        fi
    fi

    return $exit_code
}

# Run jest tests
run_jest() {
    local level="$1"
    local test_pattern=""

    case "$level" in
        unit) test_pattern="**/*.test.{js,ts}" ;;
        integration) test_pattern="**/*.integration.{js,ts}" ;;
        e2e) test_pattern="**/*.e2e.{js,ts}" ;;
    esac

    log_test "Running jest $level tests..."

    local jest_args="--testPathPattern=\"$test_pattern\" --json --outputFile=jest-${level}.json"

    if [[ "$COVERAGE" == "true" ]]; then
        jest_args+=" --coverage --coverageReporters=json"
    fi

    local exit_code=0
    npx jest $jest_args 2>&1 || exit_code=$?

    # Parse results
    if [[ -f "jest-${level}.json" ]]; then
        local passed failed
        passed=$(jq '.numPassedTests // 0' "jest-${level}.json")
        failed=$(jq '.numFailedTests // 0' "jest-${level}.json")

        local status="passed"
        if [[ $exit_code -ne 0 ]] || [[ $failed -gt 0 ]]; then
            status="failed"
        fi

        echo "{\"passed\": $passed, \"failed\": $failed, \"skipped\": 0, \"errors\": 0, \"status\": \"$status\"}"
    else
        echo '{"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "status": "error"}'
    fi

    return $exit_code
}

# Run native bash tests
run_native() {
    local level="$1"
    local test_dir="tests/${level}"

    if [[ ! -d "$test_dir" ]]; then
        log_warn "Test directory not found: $test_dir"
        echo '{"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "status": "skipped"}'
        return 0
    fi

    log_test "Running native $level tests..."

    local passed=0
    local failed=0
    local errors=0

    for test_file in "$test_dir"/*.sh; do
        [[ ! -f "$test_file" ]] && continue

        log_test "Running: $(basename "$test_file")"

        if bash "$test_file" 2>&1; then
            ((passed++))
        else
            ((failed++))
        fi
    done

    local status="passed"
    if [[ $failed -gt 0 ]] || [[ $errors -gt 0 ]]; then
        status="failed"
    fi

    echo "{\"passed\": $passed, \"failed\": $failed, \"skipped\": 0, \"errors\": $errors, \"status\": \"$status\"}"

    [[ $failed -gt 0 ]] && return 1
    return 0
}

# Run tests using Factory.ai
run_factory_tests() {
    local level="$1"

    if ! command -v droid &>/dev/null; then
        log_error "Factory.ai (droid) not installed"
        return 1
    fi

    log_test "Running Factory.ai $level tests..."

    local prompt="Run $level tests for this repository. Execute all test files and report results in JSON format with passed, failed, skipped counts."

    local result
    result=$(droid exec "$prompt" 2>&1 || echo "")

    # Parse result (Factory.ai returns structured output)
    if echo "$result" | jq . &>/dev/null; then
        echo "$result"
    else
        # Try to extract test counts from output
        local passed=0 failed=0
        passed=$(echo "$result" | grep -oP '\d+(?= passed)' | head -1 || echo 0)
        failed=$(echo "$result" | grep -oP '\d+(?= failed)' | head -1 || echo 0)

        local status="passed"
        [[ $failed -gt 0 ]] && status="failed"

        echo "{\"passed\": ${passed:-0}, \"failed\": ${failed:-0}, \"skipped\": 0, \"errors\": 0, \"status\": \"$status\"}"
    fi
}

# Generate tests using Gemini (if needed)
generate_tests_gemini() {
    local file="$1"

    if [[ -z "${GOOGLE_API_KEY:-}" ]]; then
        log_warn "GOOGLE_API_KEY not set, skipping Gemini test generation"
        return 1
    fi

    log_test "Generating tests with Gemini for: $file"

    local content
    content=$(cat "$file")

    local prompt="Generate comprehensive unit tests for this code. Return only the test code, no explanations.

File: $file

\`\`\`
$content
\`\`\`"

    local response
    response=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GOOGLE_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg prompt "$prompt" '{
            contents: [{
                parts: [{
                    text: $prompt
                }]
            }]
        }')")

    echo "$response" | jq -r '.candidates[0].content.parts[0].text // empty'
}

# Get coverage data
get_coverage() {
    local framework="$1"

    case "$framework" in
        pytest)
            if [[ -f "coverage.json" ]]; then
                jq '.totals.percent_covered // 0' coverage.json
            else
                echo "0"
            fi
            ;;
        jest)
            if [[ -f "coverage/coverage-summary.json" ]]; then
                jq '.total.lines.pct // 0' coverage/coverage-summary.json
            else
                echo "0"
            fi
            ;;
        *)
            echo "0"
            ;;
    esac
}

# Main execution
main() {
    log_info "Starting Test Runner Stage"
    log_info "Repository: $REPO_ROOT"
    log_info "Test levels: $LEVELS"
    log_info "Coverage: $COVERAGE"

    cd "$REPO_ROOT"

    # Detect framework
    local framework
    framework=$(detect_framework)
    log_info "Detected framework: $framework"

    if [[ "$framework" == "none" ]]; then
        log_warn "No test framework detected"
        echo '{"status": "skipped", "reason": "No test framework", "results": {}}' > "$REPORT_FILE"
        exit 0
    fi

    # Run tests for each level
    local all_results="{}"
    local total_passed=0
    local total_failed=0
    local overall_status="passed"

    IFS=',' read -ra LEVEL_ARRAY <<< "$LEVELS"
    for level in "${LEVEL_ARRAY[@]}"; do
        log_test "=== Running $level tests ==="

        local result

        if [[ "$USE_FACTORY" == "true" ]]; then
            result=$(run_factory_tests "$level")
        else
            case "$framework" in
                pytest) result=$(run_pytest "$level") || true ;;
                jest) result=$(run_jest "$level") || true ;;
                native) result=$(run_native "$level") || true ;;
                *) result='{"passed": 0, "failed": 0, "status": "skipped"}' ;;
            esac
        fi

        all_results=$(echo "$all_results" | jq --arg level "$level" --argjson result "$result" '. + {($level): $result}')

        # Update totals
        local level_passed level_failed level_status
        level_passed=$(echo "$result" | jq '.passed // 0')
        level_failed=$(echo "$result" | jq '.failed // 0')
        level_status=$(echo "$result" | jq -r '.status // "unknown"')

        total_passed=$((total_passed + level_passed))
        total_failed=$((total_failed + level_failed))

        if [[ "$level_status" == "failed" ]]; then
            overall_status="failed"
        fi

        log_test "$level: $level_passed passed, $level_failed failed"
    done

    # Get coverage if enabled
    local coverage_pct=0
    if [[ "$COVERAGE" == "true" ]]; then
        coverage_pct=$(get_coverage "$framework")
        log_info "Coverage: ${coverage_pct}%"

        if (( $(echo "$coverage_pct < $THRESHOLD" | bc -l) )); then
            log_warn "Coverage ${coverage_pct}% below threshold ${THRESHOLD}%"
            overall_status="failed"
        fi
    fi

    # Generate report
    local report
    report=$(jq -n \
        --arg status "$overall_status" \
        --arg timestamp "$(date -Iseconds)" \
        --arg framework "$framework" \
        --arg levels "$LEVELS" \
        --argjson results "$all_results" \
        --argjson total_passed "$total_passed" \
        --argjson total_failed "$total_failed" \
        --argjson coverage "$coverage_pct" \
        --argjson threshold "$THRESHOLD" \
        --argjson coverage_enabled "$COVERAGE" \
        '{
            status: $status,
            timestamp: $timestamp,
            stage: "test-runner",
            config: {
                framework: $framework,
                levels: ($levels | split(",")),
                coverage_enabled: $coverage_enabled,
                coverage_threshold: $threshold
            },
            summary: {
                total_passed: $total_passed,
                total_failed: $total_failed,
                coverage_percent: $coverage
            },
            results: $results
        }')

    echo "$report" > "$REPORT_FILE"

    log_success "Test run complete"
    log_info "Total passed: $total_passed"
    log_info "Total failed: $total_failed"
    log_info "Report saved to: $REPORT_FILE"

    # Exit with appropriate code
    [[ "$overall_status" == "failed" ]] && exit 1
    exit 0
}

main "$@"
