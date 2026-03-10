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
    "OGManufacturing:OGManufacturing::tests/"
)

# ── Argument parsing ──────────────────────────────────────────────────────────
FILTER_REPO=""
JSON_OUT=""
INCLUDE_LIVE=false
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)         FILTER_REPO="$2"; shift 2 ;;
        --json-out)     JSON_OUT="$2";    shift 2 ;;
        --include-live) INCLUDE_LIVE=true; shift ;;
        --coverage)     COVERAGE=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# live_data exclusion flag — applied to repos that carry live_data markers
if [[ "$INCLUDE_LIVE" == "false" ]]; then
    LIVE_FLAG='-m "not live_data"'
else
    LIVE_FLAG=""
fi

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

    # Coverage: add --cov-report=json (structured); do NOT add --cov=src (repos own source config)
    local cov_args=""
    if [[ "$COVERAGE" == "true" ]]; then
        cov_args="--cov-report=json --cov-report=term-missing"
    fi

    local cmd="uv run python -m pytest -v $pytest_args $cov_args"

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

    # Append live_data exclusion for repos that use live_data markers
    if [[ "$name" == "assethold" || "$name" == "assetutilities" ]]; then
        pytest_args="${pytest_args} ${LIVE_FLAG}"
    fi

    record="$(run_repo "$name" "$rel_dir" "$pythonpath" "$pytest_args")"
    JSONL_RECORDS="${JSONL_RECORDS}${record}"$'\n'

    if [[ -n "$JSON_OUT" ]]; then
        echo "$record" >> "$JSON_OUT"
    fi
done

# ── Coverage: extract results and run ratchet gate ───────────────────────────

if [[ "$COVERAGE" == "true" ]]; then
    COVERAGE_RESULTS="${SCRIPT_DIR}/coverage-results.json"
    COVERAGE_BASELINE="${REPO_ROOT}/config/testing/coverage-baseline.yaml"
    COVERAGE_REPORTS_DIR="${SCRIPT_DIR}/coverage-reports"
    RATCHET="${SCRIPT_DIR}/check_coverage_ratchet.py"
    DATESTAMP="$(date +%Y%m%d)"
    REPORT_OUT="${COVERAGE_REPORTS_DIR}/WRK-1067-coverage-${DATESTAMP}.txt"

    mkdir -p "$COVERAGE_REPORTS_DIR"

    # Extract coverage % from each repo's coverage.json and build results mapping
    uv run --no-project python - <<PYEOF2
import json, sys
from pathlib import Path

repo_root = Path("${REPO_ROOT}")
repos = {
    "assetutilities": repo_root / "assetutilities",
    "digitalmodel":   repo_root / "digitalmodel",
    "worldenergydata": repo_root / "worldenergydata",
    "assethold":      repo_root / "assethold",
}
filter_repo = "${FILTER_REPO}"
results = {}
for name, repo_dir in repos.items():
    if filter_repo and name != filter_repo:
        continue
    cov_json = repo_dir / "coverage.json"
    if cov_json.exists():
        data = json.loads(cov_json.read_text())
        pct = data.get("totals", {}).get("percent_covered", 0.0)
        results[name] = round(float(pct), 2)
    else:
        print(f"  [coverage] no coverage.json found for {name}", file=sys.stderr)

Path("${COVERAGE_RESULTS}").write_text(json.dumps(results, indent=2))
print(f"  [coverage] results written to ${COVERAGE_RESULTS}")
PYEOF2

    # Run ratchet check if baseline exists
    if [[ -f "$COVERAGE_BASELINE" ]]; then
        echo ""
        echo "── Coverage ratchet gate ──────────────────────────────────────"
        uv run --no-project python "$RATCHET" \
            --baseline "$COVERAGE_BASELINE" \
            --results  "$COVERAGE_RESULTS" \
            --report-out "$REPORT_OUT"
        echo "  Report: $REPORT_OUT"
    else
        echo "  [coverage] No baseline found at $COVERAGE_BASELINE — skipping ratchet gate."
        echo "  Run once to create baseline, then commit config/testing/coverage-baseline.yaml"
    fi
fi

# ── Contract tests (digitalmodel + worldenergydata) ──────────────────────────

for repo in digitalmodel worldenergydata; do
    if [[ -d "${REPO_ROOT}/${repo}/tests/contracts" ]]; then
        PYTHONPATH="${REPO_ROOT}/${repo}/src:${REPO_ROOT}/assetutilities/src" \
            uv run --project "${REPO_ROOT}/${repo}" python -m pytest \
            "${REPO_ROOT}/${repo}/tests/contracts/" -v --tb=short -m contracts
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
