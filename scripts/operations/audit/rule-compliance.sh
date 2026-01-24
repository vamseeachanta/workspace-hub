#!/usr/bin/env bash
# rule-compliance.sh - Automated compliance checking against workspace rules
set -euo pipefail

# Colors and counters
RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[0;33m' BLUE='\033[0;34m' NC='\033[0m'
PASS=0 FAIL=0 WARN=0

# Configuration
COVERAGE_MIN=80
MAX_LINES=400
BRANCH_RE="^(feature|bugfix|hotfix|chore|docs|refactor)/"

usage() { cat << 'EOF'
Usage: rule-compliance.sh [OPTIONS]

Checks: coverage >= 80%, no hardcoded secrets, files <= 400 lines, branch naming

OPTIONS:
    -h, --help          Show help
    -d, --dir DIR       Target directory (default: current)
    --skip-coverage     Skip coverage check
    --skip-secrets      Skip secrets check
    --skip-size         Skip file size check
    --skip-branch       Skip branch naming check

EXIT: 0 = pass, 1 = failures found
EOF
}

pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASS++)) || true; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; ((FAIL++)) || true; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARN++)) || true; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Parse args
TARGET_DIR="." SKIP_COV=false SKIP_SEC=false SKIP_SIZE=false SKIP_BR=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) usage; exit 0 ;;
        -d|--dir) TARGET_DIR="$2"; shift 2 ;;
        --skip-coverage) SKIP_COV=true; shift ;;
        --skip-secrets) SKIP_SEC=true; shift ;;
        --skip-size) SKIP_SIZE=true; shift ;;
        --skip-branch) SKIP_BR=true; shift ;;
        *) echo "Unknown: $1"; usage; exit 1 ;;
    esac
done

cd "$TARGET_DIR"
info "Checking: $(pwd)"
echo ""

# Check 1: Test Coverage (80% threshold per testing.md)
check_coverage() {
    info "Coverage check (>= ${COVERAGE_MIN}%)..."
    local pct=0 found=false

    if [[ -f ".coverage" ]] && command -v coverage &>/dev/null; then
        pct=$(coverage report 2>/dev/null | grep -oP 'TOTAL.*\s+\K\d+(?=%)' || echo "0")
        found=true
    elif [[ -f "coverage/coverage-summary.json" ]]; then
        pct=$(jq -r '.total.lines.pct // 0' coverage/coverage-summary.json 2>/dev/null | cut -d. -f1)
        found=true
    elif [[ -f "coverage.out" ]]; then
        pct=$(go tool cover -func=coverage.out 2>/dev/null | grep total | awk '{print $3}' | tr -d '%' | cut -d. -f1 || echo "0")
        found=true
    fi

    if [[ "$found" == "false" ]]; then warn "No coverage reports found"; return; fi
    [[ "$pct" -ge "$COVERAGE_MIN" ]] && pass "Coverage: ${pct}%" || fail "Coverage: ${pct}% < ${COVERAGE_MIN}%"
}

# Check 2: No hardcoded secrets (per security.md)
check_secrets() {
    info "Secrets check..."
    local pattern='(API_KEY|PASSWORD|SECRET|TOKEN|PRIVATE_KEY|AWS_SECRET)\s*=\s*["\x27][^"\x27]+'
    local files matches

    files=$(git ls-files --cached 2>/dev/null | grep -E '\.(py|js|ts|go|sh|yaml|yml)$' || true)
    [[ -z "$files" ]] && { warn "No source files found"; return; }

    matches=$(echo "$files" | xargs grep -lE "$pattern" 2>/dev/null | head -10 || true)
    if [[ -z "$matches" ]]; then
        pass "No hardcoded secrets"
    else
        fail "Potential secrets in: $(echo "$matches" | wc -l) files"
        echo "$matches" | head -3 | sed 's/^/       /'
    fi
}

# Check 3: File size (400 lines max per coding-style.md)
check_sizes() {
    info "File size check (<= ${MAX_LINES} lines)..."
    local count=0 samples=""

    while IFS= read -r file; do
        [[ -z "$file" || ! -f "$file" ]] && continue
        local lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        if [[ "$lines" -gt "$MAX_LINES" ]]; then
            ((count++)) || true
            [[ -z "$samples" ]] && samples="$file ($lines)"
        fi
    done < <(git ls-files --cached 2>/dev/null | grep -E '\.(py|js|ts|go|sh)$' || true)

    [[ "$count" -eq 0 ]] && pass "All files <= ${MAX_LINES} lines" || fail "$count files exceed ${MAX_LINES} lines (e.g., $samples)"
}

# Check 4: Branch naming (per git-workflow.md)
check_branch() {
    info "Branch naming check..."
    local branch=$(git branch --show-current 2>/dev/null || echo "")

    [[ -z "$branch" ]] && { warn "Detached HEAD"; return; }
    [[ "$branch" =~ ^(main|master|develop)$ ]] && { pass "Protected branch: $branch"; return; }
    [[ "$branch" =~ $BRANCH_RE ]] && pass "Valid: $branch" || fail "Invalid branch: $branch"
}

# Run checks
[[ "$SKIP_COV" == "false" ]] && check_coverage
[[ "$SKIP_SEC" == "false" ]] && check_secrets
[[ "$SKIP_SIZE" == "false" ]] && check_sizes
[[ "$SKIP_BR" == "false" ]] && check_branch

# Summary
echo ""
echo "============================================"
printf "  ${GREEN}PASS${NC}: %d  ${RED}FAIL${NC}: %d  ${YELLOW}WARN${NC}: %d\n" "$PASS" "$FAIL" "$WARN"
echo "============================================"
[[ "$FAIL" -gt 0 ]] && { echo -e "${RED}Compliance failed${NC}"; exit 1; }
echo -e "${GREEN}Compliance passed${NC}"
