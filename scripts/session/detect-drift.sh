#!/usr/bin/env bash
# detect-drift.sh — Scan session logs for rule violation patterns
# Outputs per-session counts to stdout; appends to .claude/state/drift-summary.yaml
#
# Usage:
#   detect-drift.sh --log <jsonl-path> [--since <YYYYMMDD>] [--no-git]
#   --no-git  skip real git log; scan cmd fields only (for testing)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")"
STATE_DIR="${REPO_ROOT}/.claude/state"
SUMMARY_FILE="${STATE_DIR}/drift-summary.yaml"

LOG_FILE=""
SINCE_DATE="$(date +%Y%m%d)"
NO_GIT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --log)    LOG_FILE="$2";   shift 2 ;;
    --since)  SINCE_DATE="$2"; shift 2 ;;
    --no-git) NO_GIT=true;     shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$LOG_FILE" ]] && { echo "Error: --log required" >&2; exit 1; }
[[ -f "$LOG_FILE" ]] || { echo "Error: log file not found: $LOG_FILE" >&2; exit 1; }

# Use Python for reliable JSON field extraction from JSONL
read -r -d '' PY_EXTRACT << 'PYEOF' || true
import sys, json, re

log_file = sys.argv[1]
python_runtime = 0
file_placement = 0
git_workflow_cmds = []

def is_python3_violation(cmd):
    """Flag bare python3 unless it is the direct interpreter in a uv run call.

    Split on shell operators so compound commands like:
      uv run something && python3 foo.py
    are correctly identified as violations.
    """
    sub_cmds = re.split(r'\s*(?:&&|\|\||;|\|)\s*', cmd)
    for sub in sub_cmds:
        sub = sub.strip()
        if re.search(r'\bpython3\b', sub) and not re.search(r'\buv\s+run\b.*\bpython3\b', sub):
            return True
    return False

with open(log_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        cmd = rec.get("cmd", "")
        path = rec.get("path", "")
        # python_runtime: bare python3 not invoked via uv run
        if cmd and is_python3_violation(cmd):
            python_runtime += 1
        # file_placement: test files written inside src/
        if path and "src/" in path and "/tests/" in path:
            file_placement += 1
        # git_workflow: collect commit messages from cmd fields
        if cmd and "git commit" in cmd:
            m = re.search(r"-m\s+['\"]([^'\"]+)['\"]", cmd)
            if m:
                git_workflow_cmds.append(m.group(1))
            else:
                m2 = re.search(r"-m\s+(\S+)", cmd)
                if m2:
                    git_workflow_cmds.append(m2.group(1))

print(f"python_runtime={python_runtime}")
print(f"file_placement={file_placement}")
print(f"git_cmds={'|||'.join(git_workflow_cmds)}")
PYEOF

result=$(uv run --no-project python -c "$PY_EXTRACT" "$LOG_FILE" 2>/dev/null)
python_runtime=$(echo "$result" | grep "^python_runtime=" | cut -d= -f2)
file_placement=$(echo "$result" | grep "^file_placement=" | cut -d= -f2)
git_cmds=$(echo "$result" | grep "^git_cmds=" | cut -d= -f2-)

# ── Pattern 3: git_workflow ──────────────────────────────────────────────────
# CONVENTIONAL_RE: all standard conventional commit type prefixes
CONVENTIONAL_RE='^(feat|fix|chore|docs|refactor|test|style|perf|build|ci|merge|revert|wip)(\(|!|:|$| )'
# EXEMPT_RE: types that do NOT require a WRK-NNN reference
EXEMPT_RE='^(build|ci|merge|revert|wip|chore|style)(\(|!|:|$| )'
git_workflow=0; non_conventional=0; missing_wrk_ref=0; exempt_type=0

check_msg() {
    local msg="$1"
    if ! echo "$msg" | grep -qE "$CONVENTIONAL_RE"; then
        # Not a conventional commit at all — violation
        non_conventional=$((non_conventional + 1))
        git_workflow=$((git_workflow + 1))
    elif echo "$msg" | grep -qE "$EXEMPT_RE"; then
        # Exempt type (chore/merge/revert/wip/build/ci/style) — no WRK ref required
        exempt_type=$((exempt_type + 1))
    elif ! echo "$msg" | grep -qE 'WRK-[0-9]+'; then
        # Conventional non-exempt (feat/fix/docs/refactor/test/perf) without WRK ref — violation
        missing_wrk_ref=$((missing_wrk_ref + 1))
        git_workflow=$((git_workflow + 1))
    fi
}

if [[ "$NO_GIT" == "true" ]]; then
    # Use commit messages extracted from session log cmd fields
    IFS='|||' read -ra msgs <<< "$git_cmds"
    for msg in "${msgs[@]}"; do
        [[ -z "$msg" ]] && continue
        check_msg "$msg"
    done
else
    since_fmt="${SINCE_DATE:0:4}-${SINCE_DATE:4:2}-${SINCE_DATE:6:2}"
    while IFS= read -r msg; do
        [[ -z "$msg" ]] && continue
        check_msg "$msg"
    done < <(git -C "$REPO_ROOT" log --since="${since_fmt}T00:00:00" --format="%s" 2>/dev/null || true)
fi

# ── Output ───────────────────────────────────────────────────────────────────
scanned_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "python_runtime: ${python_runtime}"
echo "file_placement: ${file_placement}"
echo "git_workflow: ${git_workflow}"
echo "git_non_conventional: ${non_conventional}"
echo "git_missing_wrk_ref: ${missing_wrk_ref}"
echo "git_exempt_type: ${exempt_type}"

# Append to drift-summary.yaml with file lock for concurrent-write safety
mkdir -p "$STATE_DIR"
LOCK_FILE="${SUMMARY_FILE}.lock"
(
  flock -x 9
  printf -- '- scanned_at: "%s"\n  log: "%s"\n  violations:\n    python_runtime: %s\n    file_placement: %s\n    git_workflow: %s\n    git_non_conventional: %s\n    git_missing_wrk_ref: %s\n    git_exempt_type: %s\n' \
    "$scanned_at" "$LOG_FILE" "$python_runtime" "$file_placement" \
    "$git_workflow" "$non_conventional" "$missing_wrk_ref" "$exempt_type" \
    >> "$SUMMARY_FILE"
) 9>"$LOCK_FILE"
