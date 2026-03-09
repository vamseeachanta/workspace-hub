#!/usr/bin/env bash
# ABOUTME: WRK-1085 — Fast symbol lookup from pre-built symbol-index.jsonl.
# ABOUTME: Usage: find-symbol.sh <name> [--kind class|function|method|constant] [--repo <repo>]
# ABOUTME: Exits 1 if symbol not found; 0 on match.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SYMBOL_INDEX="$REPO_ROOT/config/search/symbol-index.jsonl"

usage() {
    echo "Usage: $0 <symbol_name> [--kind <kind>] [--repo <repo>]" >&2
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

SYMBOL_NAME="$1"
shift

KIND_FILTER=""
REPO_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --kind)  KIND_FILTER="$2"; shift 2 ;;
        --repo)  REPO_FILTER="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; usage ;;
    esac
done

if [[ ! -f "$SYMBOL_INDEX" ]]; then
    echo "Error: symbol index not found at $SYMBOL_INDEX" >&2
    echo "Run: uv run --no-project python scripts/search/build-symbol-index.py" >&2
    exit 1
fi

# --- jq path (fast) ---
if command -v jq &>/dev/null; then
    jq_filter='. | select(.symbol == $name)'
    jq_args=(--arg name "$SYMBOL_NAME")

    if [[ -n "$KIND_FILTER" ]]; then
        jq_filter+=' | select(.kind == $kind)'
        jq_args+=(--arg kind "$KIND_FILTER")
    fi
    if [[ -n "$REPO_FILTER" ]]; then
        jq_filter+=' | select(.repo == $repo)'
        jq_args+=(--arg repo "$REPO_FILTER")
    fi

    jq_filter+=' | "\(.repo):\(.file):\(.line) (\(.kind))"'

    results=$(jq -r "${jq_args[@]}" "$jq_filter" "$SYMBOL_INDEX" 2>/dev/null)

# --- fallback: grep + python ---
else
    raw=$(grep -F "\"$SYMBOL_NAME\"" "$SYMBOL_INDEX" || true)
    if [[ -z "$raw" ]]; then
        echo "Symbol not found: $SYMBOL_NAME" >&2
        exit 1
    fi
    results=$(echo "$raw" | uv run --no-project python - <<'PYEOF'
import sys, json
lines = sys.stdin.read().splitlines()
for line in lines:
    try:
        r = json.loads(line)
    except Exception:
        continue
    import os
    name_filter = os.environ.get("SYMBOL_NAME", "")
    kind_filter = os.environ.get("KIND_FILTER", "")
    repo_filter = os.environ.get("REPO_FILTER", "")
    if r.get("symbol") != name_filter:
        continue
    if kind_filter and r.get("kind") != kind_filter:
        continue
    if repo_filter and r.get("repo") != repo_filter:
        continue
    print(f"{r['repo']}:{r['file']}:{r['line']} ({r['kind']})")
PYEOF
    )
fi

if [[ -z "$results" ]]; then
    echo "Symbol not found: $SYMBOL_NAME" >&2
    exit 1
fi

echo "$results"
