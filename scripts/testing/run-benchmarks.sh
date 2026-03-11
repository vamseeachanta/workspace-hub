#!/usr/bin/env bash
# run-benchmarks.sh — Performance benchmark runner for tier-1 engineering calc repos.
#
# Runs pytest-benchmark suites per repo, compares against a committed baseline,
# and exits nonzero when any benchmark regresses >20% in mean execution time.
#
# Usage:
#   run-benchmarks.sh [--repo <name>] [--save-baseline] [--no-compare]
#
# Exit codes:
#   0 = clean (all benchmarks within threshold or --no-compare)
#   1 = regression detected (at least one benchmark >20% slower)
#   2 = setup/bootstrap error (missing baseline, unknown repo, etc.)
#
# Environment:
#   BENCHMARK_BASELINE_PATH — override default baseline JSON path (for testing)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
PARSER="${SCRIPT_DIR}/parse_benchmark_output.py"
RESULTS_DIR="${SCRIPT_DIR}/benchmark-results"
DEFAULT_BASELINE="${REPO_ROOT}/config/testing/benchmark-baseline.json"
BASELINE="${BENCHMARK_BASELINE_PATH:-$DEFAULT_BASELINE}"
TODAY="$(date -u +%Y-%m-%d)"
AGGREGATE_OUT="${RESULTS_DIR}/benchmark-${TODAY}.json"

# ── Repo config table ─────────────────────────────────────────────────────────
# Format: "name|rel_dir|PYTHONPATH|uv_group|benchmark_targets"
# - PYTHONPATH may contain colons (e.g. src:../assetutilities/src)
# - uv_group: dependency group to activate (empty = default dev group)
# - benchmark_targets: space-separated pytest file/dir paths
REPO_CONFIGS=(
    "assetutilities|assetutilities|src|test|tests/benchmarks"
    "digitalmodel|digitalmodel|src||tests/benchmarks/test_cp_benchmarks.py tests/benchmarks/test_wall_thickness_benchmarks.py"
    "worldenergydata|worldenergydata|src:../assetutilities/src|benchmark|tests/benchmarks/test_eia_benchmarks.py"
)

# ── Argument parsing ──────────────────────────────────────────────────────────
FILTER_REPO=""
SAVE_BASELINE=false
NO_COMPARE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            [[ $# -ge 2 ]] || { echo "ERROR: --repo requires a value" >&2; exit 2; }
            FILTER_REPO="$2"; shift 2 ;;
        --save-baseline) SAVE_BASELINE=true; shift ;;
        --no-compare)    NO_COMPARE=true;    shift ;;
        *) echo "ERROR: Unknown option: $1" >&2; exit 2 ;;
    esac
done

# Validate --repo if supplied
if [[ -n "$FILTER_REPO" ]]; then
    found=false
    for entry in "${REPO_CONFIGS[@]}"; do
        name="${entry%%|*}"
        if [[ "$name" == "$FILTER_REPO" ]]; then found=true; break; fi
    done
    if [[ "$found" == "false" ]]; then
        echo "ERROR: Unknown repo '$FILTER_REPO'. Valid: assetutilities digitalmodel worldenergydata" >&2
        exit 1
    fi
fi

# Baseline check (before running, unless --no-compare or --save-baseline)
if [[ "$NO_COMPARE" == "false" && "$SAVE_BASELINE" == "false" ]]; then
    if [[ ! -f "$BASELINE" ]]; then
        echo "ERROR: No baseline found at $BASELINE" >&2
        echo "Run with --save-baseline --no-compare to bootstrap the baseline first." >&2
        exit 2
    fi
fi

mkdir -p "$RESULTS_DIR"

# ── Run benchmarks per repo ───────────────────────────────────────────────────
declare -a all_json_files=()
overall_exit=0

run_repo_benchmarks() {
    local name="$1" rel_dir="$2" pythonpath="$3" uv_group="$4" targets="$5"
    local repo_dir="${REPO_ROOT}/${rel_dir}"
    local tmp_json="${RESULTS_DIR}/${name}-${TODAY}-raw.json"

    if [[ ! -d "$repo_dir" ]]; then
        echo "  SKIP $name — directory not found: $repo_dir" >&2
        return 0
    fi

    # Build optional --group flag
    local group_args=()
    if [[ -n "$uv_group" ]]; then
        group_args=(--group "$uv_group")
    fi

    echo "  Running $name benchmarks..."
    local exit_code=0
    (
        cd "$repo_dir"
        # shellcheck disable=SC2086
        PYTHONPATH="$pythonpath" uv run "${group_args[@]}" python -m pytest $targets \
            --benchmark-only \
            --benchmark-json="$tmp_json" \
            --benchmark-min-rounds=5 \
            -q --tb=short
    ) || exit_code=$?

    if [[ "$exit_code" -ne 0 ]]; then
        echo "  FAIL $name — pytest exited $exit_code" >&2
        overall_exit=1
        return 0
    fi

    if [[ -f "$tmp_json" ]]; then
        all_json_files+=("$name:$tmp_json")
        echo "  OK   $name — results: $tmp_json"
    fi
}

for entry in "${REPO_CONFIGS[@]}"; do
    IFS='|' read -r name rel_dir pythonpath uv_group targets <<< "$entry"
    [[ -n "$FILTER_REPO" && "$name" != "$FILTER_REPO" ]] && continue
    run_repo_benchmarks "$name" "$rel_dir" "$pythonpath" "$uv_group" "$targets"
done

if [[ ${#all_json_files[@]} -eq 0 ]]; then
    echo "WARNING: No benchmark results collected." >&2
    exit "$overall_exit"
fi

# ── Save baseline ─────────────────────────────────────────────────────────────
if [[ "$SAVE_BASELINE" == "true" ]]; then
    mkdir -p "$(dirname "$BASELINE")"
    uv run --no-project python "$PARSER" \
        --mode save-baseline \
        --output "$BASELINE" \
        "${all_json_files[@]}"
    echo "Baseline saved: $BASELINE"
fi

# ── Compare against baseline ──────────────────────────────────────────────────
if [[ "$NO_COMPARE" == "false" && -f "$BASELINE" ]]; then
    compare_exit=0
    uv run --no-project python "$PARSER" \
        --mode compare \
        --baseline "$BASELINE" \
        --output "$AGGREGATE_OUT" \
        "${all_json_files[@]}" || compare_exit=$?

    if [[ "$compare_exit" -eq 1 ]]; then
        echo "REGRESSION detected — see results above." >&2
        overall_exit=1
    fi
fi

exit "$overall_exit"
