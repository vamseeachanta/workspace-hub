#!/usr/bin/env bash
# run-cross-repo-integration.sh — Run downstream contract tests per cross-repo-graph.yaml
# WRK-1091: cross-repo integration test gate for workspace-hub
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
GRAPH_FILE="${REPO_ROOT}/config/deps/cross-repo-graph.yaml"
BYPASS_LOG="${REPO_ROOT}/logs/hooks/pre-push-bypass.jsonl"

# ── Bypass support ────────────────────────────────────────────────────────────
if [[ "${SKIP_CROSS_REPO_CHECK:-0}" == "1" ]]; then
    echo "SKIP_CROSS_REPO_CHECK=1: bypassing cross-repo integration check" >&2
    mkdir -p "$(dirname "$BYPASS_LOG")"
    printf '{"timestamp":"%s","wrk":"WRK-1091","reason":"SKIP_CROSS_REPO_CHECK","script":"run-cross-repo-integration.sh"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BYPASS_LOG" || true
    exit 0
fi

# ── Argument parsing ──────────────────────────────────────────────────────────
TARGET_REPO=""
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            TARGET_REPO="$2"
            shift 2
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --help)
            echo "Usage: run-cross-repo-integration.sh [--repo <name>] [--fail-fast]"
            echo ""
            echo "Options:"
            echo "  --repo <name>   Run contracts for a single downstream repo only"
            echo "  --fail-fast     Exit immediately on first repo failure"
            echo ""
            echo "Environment:"
            echo "  SKIP_CROSS_REPO_CHECK=1   Bypass all checks (logged)"
            exit 0
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

# ── Validate graph file ───────────────────────────────────────────────────────
if [[ ! -f "$GRAPH_FILE" ]]; then
    echo "ERROR: Graph file not found: $GRAPH_FILE" >&2
    exit 2
fi

# ── Parse graph YAML — emit JSON array of layer-1 repos ──────────────────────
export GRAPH_FILE
REPOS_JSON="$(uv run --no-project python -c "
import sys, json, yaml, os
graph_file = os.environ['GRAPH_FILE']
with open(graph_file) as f:
    data = yaml.safe_load(f)
repos = [
    {'id': e['id'], 'pythonpath': e.get('pythonpath', []), 'contract_tests': e.get('contract_tests', [])}
    for e in data.get('graph', [])
    if e.get('layer', 0) == 1
]
print(json.dumps(repos))
")"

if [[ -z "$REPOS_JSON" || "$REPOS_JSON" == "[]" ]]; then
    echo "ERROR: No layer-1 repos found in graph YAML" >&2
    exit 2
fi

# ── Validate --repo if given ──────────────────────────────────────────────────
if [[ -n "$TARGET_REPO" ]]; then
    export REPOS_JSON TARGET_REPO
    FOUND="$(uv run --no-project python -c "
import json, os
repos = json.loads(os.environ['REPOS_JSON'])
ids = [r['id'] for r in repos]
print('yes' if os.environ['TARGET_REPO'] in ids else 'no')
")"
    if [[ "$FOUND" != "yes" ]]; then
        ALL_IDS="$(uv run --no-project python -c "
import json, os
repos = json.loads(os.environ['REPOS_JSON'])
print(', '.join(r['id'] for r in repos))
")"
        echo "ERROR: Unknown repo '${TARGET_REPO}'. Layer-1 repos in graph: ${ALL_IDS}" >&2
        exit 1
    fi
fi

# ── Run contract tests for a single repo ─────────────────────────────────────
PASS_COUNT=0
FAIL_COUNT=0
declare -a RESULTS=()

run_repo_contracts() {
    local repo_id="$1"
    local pythonpath_json="$2"
    local repo_dir="${REPO_ROOT}/${repo_id}"
    local tests_dir="${repo_dir}/tests/contracts"

    # Build PYTHONPATH from graph entries (absolute paths)
    export PYTHONPATH_ENTRIES="$pythonpath_json" REPO_ROOT
    local pypath
    pypath="$(uv run --no-project python -c "
import json, os
entries = json.loads(os.environ['PYTHONPATH_ENTRIES'])
repo_root = os.environ['REPO_ROOT']
print(':'.join(os.path.join(repo_root, e) for e in entries))
")"

    if [[ ! -d "$tests_dir" ]]; then
        RESULTS+=("  [SKIP] ${repo_id}: contracts dir not found (${tests_dir})")
        return 0
    fi

    if [[ ! -f "${repo_dir}/pyproject.toml" ]]; then
        RESULTS+=("  [SKIP] ${repo_id}: no pyproject.toml — cannot run uv run")
        return 0
    fi

    local exit_code=0
    # Run pytest using the repo's own uv venv (cd into repo dir)
    if (cd "$repo_dir" && PYTHONPATH="$pypath" uv run python -m pytest \
            -m contracts \
            --tb=short -q \
            "tests/contracts/" \
            2>&1); then
        exit_code=0
    else
        exit_code=$?
    fi

    if [[ "$exit_code" -eq 0 ]]; then
        RESULTS+=("  [PASS] ${repo_id}: contract tests passed")
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        RESULTS+=("  [FAIL] ${repo_id}: pytest exit code ${exit_code}")
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [[ "$FAIL_FAST" == "true" ]]; then
            return 1
        fi
    fi
}

# Iterate repos parsed from JSON
export REPOS_JSON
readarray -t REPO_LINES < <(uv run --no-project python -c "
import json, os
repos = json.loads(os.environ['REPOS_JSON'])
for r in repos:
    print(json.dumps(r))
")

for repo_line in "${REPO_LINES[@]}"; do
    export REPO_LINE="$repo_line"
    repo_id="$(uv run --no-project python -c "import json,os; print(json.loads(os.environ['REPO_LINE'])['id'])")"
    pythonpath_json="$(uv run --no-project python -c "import json,os; print(json.dumps(json.loads(os.environ['REPO_LINE'])['pythonpath']))")"

    if [[ -n "$TARGET_REPO" && "$repo_id" != "$TARGET_REPO" ]]; then
        continue
    fi

    run_repo_contracts "$repo_id" "$pythonpath_json" || {
        if [[ "$FAIL_FAST" == "true" ]]; then
            break
        fi
    }
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Cross-Repo Integration Results ==="
for line in "${RESULTS[@]}"; do
    echo "$line"
done
echo "==="
TOTAL=$((PASS_COUNT + FAIL_COUNT))
if [[ "$FAIL_COUNT" -eq 0 ]]; then
    echo "RESULT: All ${TOTAL} downstream repo(s) PASSED"
    exit 0
else
    echo "RESULT: ${FAIL_COUNT} downstream repo(s) FAILED"
    exit 1
fi
