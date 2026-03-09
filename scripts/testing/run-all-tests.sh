#!/usr/bin/env bash
# run-all-tests.sh — Unified test runner for tier-1 Python repos
#
# Iterates tier-1 repos, runs the canonical uv-run pytest command per
# .claude/rules/python-runtime.md, and produces a structured JSONL + markdown summary.
#
# Usage:
#   run-all-tests.sh [--repo <name>] [--json-out <file>]
#
# Exit code:
#   0 = no unexpected failures across all repos
#   1 = one or more unexpected failures (or infrastructure error)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
PARSER="${SCRIPT_DIR}/parse_pytest_output.py"
EF_FILE="${SCRIPT_DIR}/expected-failures.txt"

# ── Repo config table ─────────────────────────────────────────────────────────
# Format: "name:rel_dir:PYTHONPATH:pytest_args"
# rel_dir is relative to REPO_ROOT; PYTHONPATH is relative to repo root (or empty)
REPO_CONFIGS=(
    "assetutilities:assetutilities::tests/ --noconftest"
    "digitalmodel:digitalmodel:src:"
    "worldenergydata:worldenergydata:src:--noconftest"
    "assethold:assethold::tests/ --noconftest --tb=short -q"
)

# ── Argument parsing ──────────────────────────────────────────────────────────
FILTER_REPO=""
JSON_OUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)     FILTER_REPO="$2"; shift 2 ;;
        --json-out) JSON_OUT="$2";    shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ── Run one repo ──────────────────────────────────────────────────────────────

run_repo() {
    local name="$1" rel_dir="$2" pythonpath="$3" pytest_args="$4"
    local repo_dir="${REPO_ROOT}/${rel_dir}"

    if [[ ! -d "$repo_dir" ]]; then
        printf '{"repo":"%s","exit_code":-1,"status":"skipped","passed":0,"failed":0,"error":0,"skipped_count":0,"unexpected":0,"expected_fail":0,"unexpected_ids":[]}\n' "$name"
        return 0
    fi

    local tmpout exit_code=0
    tmpout="$(mktemp)"

    local cmd="uv run python -m pytest -v $pytest_args"

    if [[ -n "$pythonpath" ]]; then
        (cd "$repo_dir" && PYTHONPATH="$pythonpath" eval "$cmd" >"$tmpout" 2>&1) || exit_code=$?
    else
        (cd "$repo_dir" && eval "$cmd" >"$tmpout" 2>&1) || exit_code=$?
    fi

    uv run --no-project python "$PARSER" "$name" "$exit_code" "$EF_FILE" < "$tmpout"

    rm -f "$tmpout"
}

# ── Collect records ───────────────────────────────────────────────────────────

JSONL_RECORDS=""

for config in "${REPO_CONFIGS[@]}"; do
    IFS=':' read -r name rel_dir pythonpath pytest_args <<< "$config"
    [[ -n "$FILTER_REPO" && "$name" != "$FILTER_REPO" ]] && continue

    record="$(run_repo "$name" "$rel_dir" "$pythonpath" "$pytest_args")"
    JSONL_RECORDS="${JSONL_RECORDS}${record}"$'\n'

    if [[ -n "$JSON_OUT" ]]; then
        echo "$record" >> "$JSON_OUT"
    fi
done

# ── Render summary table and exit code ────────────────────────────────────────

uv run --no-project python - <<PYEOF
import json, sys

records = []
for line in """${JSONL_RECORDS}""".strip().splitlines():
    line = line.strip()
    if line:
        records.append(json.loads(line))

if not records:
    print("No repos matched.")
    sys.exit(0)

print()
header = f"{'repo':<20} {'pass':>6} {'fail':>6} {'exp-fail':>10} {'skip':>6} {'error':>6}  status"
print(header)
print("\u2500" * 70)

total_pass = total_fail = total_expfail = total_skip = total_err = 0
overall_ok = True

for r in records:
    # Field name for skipped may be 'skipped' or 'skipped_count' depending on version
    skipped = r.get("skipped", r.get("skipped_count", 0))
    print(
        f"{r['repo']:<20} {r['passed']:>6} {r['failed']:>6} "
        f"{r['expected_fail']:>10} {skipped:>6} {r['error']:>6}  {r['status']}"
    )
    total_pass   += r["passed"]
    total_fail   += r["failed"]
    total_expfail += r["expected_fail"]
    total_skip   += skipped
    total_err    += r["error"]
    if r["status"] in ("unexpected_failures", "error"):
        overall_ok = False

print("\u2500" * 70)
status_str = "ok" if overall_ok else "FAILED"
print(
    f"{'TOTAL':<20} {total_pass:>6} {total_fail:>6} "
    f"{total_expfail:>10} {total_skip:>6} {total_err:>6}  {status_str}"
)
print()

if not overall_ok:
    # Print unexpected failure IDs
    for r in records:
        if r.get("unexpected_ids"):
            print(f"Unexpected failures in {r['repo']}:")
            for nid in r["unexpected_ids"]:
                print(f"  FAILED {nid}")
    sys.exit(1)

sys.exit(0)
PYEOF
