#!/usr/bin/env bash
# coverage-drift-report.sh — Monthly report of line-coverage drift per tier-1 repo.
# Issue: #2315 (https://github.com/vamseeachanta/workspace-hub/issues/2315)
# Companion: vamseeachanta/assethold#31 (enforce coverage gates)
#
# Computes each repo's current line-coverage (from coverage.xml) minus the
# previous month's figure (parsed from the prior report). PR-level gates only
# catch drops per PR; slow erosion across many small PRs is invisible without
# a trend report.
#
# Env overrides (testing):
#   COVERAGE_DRIFT_OUT_DIR       — override docs/reports output dir
#   COVERAGE_DRIFT_MONTH         — override month (e.g. 2026-04)
#   COVERAGE_DRIFT_PREV_MONTH    — override previous month (e.g. 2026-03)
#   COVERAGE_DRIFT_REPOS         — comma-separated "name:path" pairs
#   COVERAGE_DRIFT_WARN_PP       — warn threshold, percentage points (default 1)
#   COVERAGE_DRIFT_BLOCK_PP      — block threshold, percentage points (default 5)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/cadence-common.sh"
cadence_init_repo_root

MONTH="${COVERAGE_DRIFT_MONTH:-$(cadence_period monthly)}"
PREV_MONTH="${COVERAGE_DRIFT_PREV_MONTH:-$(date -d "${MONTH}-01 -1 month" +%Y-%m 2>/dev/null || date +%Y-%m)}"
OUT_DIR="${COVERAGE_DRIFT_OUT_DIR:-${REPO_ROOT}/docs/reports}"
OUT="${OUT_DIR}/coverage-drift-${MONTH}.md"
PREV="${OUT_DIR}/coverage-drift-${PREV_MONTH}.md"
WARN_PP="${COVERAGE_DRIFT_WARN_PP:-1}"
BLOCK_PP="${COVERAGE_DRIFT_BLOCK_PP:-5}"

# ── Repo list ────────────────────────────────────────────────────────────
# Default: tier-1 repos relative to REPO_ROOT. Overridable via env as
# "name1:/abs/path1,name2:/abs/path2".
declare -a REPO_NAMES=()
declare -a REPO_PATHS=()
if [[ -n "${COVERAGE_DRIFT_REPOS:-}" ]]; then
    IFS=',' read -ra pairs <<< "$COVERAGE_DRIFT_REPOS"
    for p in "${pairs[@]}"; do
        REPO_NAMES+=("${p%%:*}")
        REPO_PATHS+=("${p#*:}")
    done
else
    for name in assetutilities digitalmodel worldenergydata assethold OGManufacturing; do
        REPO_NAMES+=("$name")
        REPO_PATHS+=("${REPO_ROOT}/${name}")
    done
fi

mkdir -p "$OUT_DIR"

# ── Parse coverage.xml line-rate → percentage ────────────────────────────
parse_line_rate() {
    local xml="$1"
    [[ -f "$xml" ]] || { echo ""; return; }
    # Extract first line-rate="N.NN" on the root <coverage> element.
    local rate
    rate="$(grep -m1 -oE 'line-rate="[0-9]+\.?[0-9]*"' "$xml" 2>/dev/null | head -1 | sed -E 's/.*"([^"]+)".*/\1/')"
    [[ -n "$rate" ]] || { echo ""; return; }
    awk -v r="$rate" 'BEGIN{printf "%.1f", r*100}'
}

# ── Parse previous report for last-month's per-repo coverage ─────────────
prev_coverage() {
    local name="$1"
    [[ -f "$PREV" ]] || { echo ""; return; }
    # Row format: "| repo_a | 80.0% | ... |"
    awk -v n="$name" -F'|' '
        $2 ~ ("^ *" n " *$") {
            gsub(/[[:space:]%]/, "", $3)
            if ($3 ~ /^[0-9]+(\.[0-9]+)?$/) { print $3; exit }
        }
    ' "$PREV"
}

# ── Collect rows ─────────────────────────────────────────────────────────
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

max_drop=0
for i in "${!REPO_NAMES[@]}"; do
    name="${REPO_NAMES[$i]}"
    path="${REPO_PATHS[$i]}"
    current_pct="$(parse_line_rate "${path}/coverage.xml")"
    prev_pct="$(prev_coverage "$name")"

    if [[ -z "$current_pct" ]]; then
        flag="no data"
        delta_cell="—"
        current_cell="—"
    else
        current_cell="${current_pct}%"
        if [[ -n "$prev_pct" ]]; then
            delta="$(awk -v a="$current_pct" -v b="$prev_pct" 'BEGIN{printf "%.1f", a-b}')"
            delta_cell="${delta}pp"
            drop="$(awk -v d="$delta" 'BEGIN{printf "%.2f", (d<0)?-d:0}')"
            # Track max drop for status band
            if awk -v d="$drop" -v m="$max_drop" 'BEGIN{exit !(d>m)}'; then
                max_drop="$drop"
            fi
            if awk -v d="$drop" -v b="$BLOCK_PP" 'BEGIN{exit !(d>b)}'; then
                flag="🔴 over block"
            elif awk -v d="$drop" -v w="$WARN_PP" 'BEGIN{exit !(d>w)}'; then
                flag="🟡 over warn"
            else
                flag=""
            fi
        else
            delta_cell="—"
            flag=""
        fi
    fi
    prev_cell="${prev_pct:+${prev_pct}%}"
    prev_cell="${prev_cell:-—}"
    printf "| %s | %s | %s | %s | %s |\n" "$name" "$current_cell" "$prev_cell" "$delta_cell" "$flag" >> "$TMP"
done

status="$(compute_status_band "$max_drop" "$WARN_PP" "$BLOCK_PP")"
summary="max per-repo drop is ${max_drop}pp (warn ${WARN_PP}pp, block ${BLOCK_PP}pp)"

# ── Write report ─────────────────────────────────────────────────────────
{
    emit_report_header "coverage-drift" "$MONTH" "$status" "$summary"
    echo "Baseline: \`$(basename "$PREV")\`$([[ -f "$PREV" ]] || echo ' (not found — first run)')"
    echo

    echo "## Per-repo coverage"
    echo
    echo "| Repo | This month | Last month | Δ (pp) | Flag |"
    echo "|------|-----------|-----------|--------|------|"
    cat "$TMP"
    echo

    echo "## Files with largest drops"
    echo
    echo "_Per-file drops require diffing coverage.xml per class. Deferred to follow-up; v1 reports repo-level Δ only._"
    echo

    echo "## Source"
    echo
    echo "Generated by \`scripts/cron/coverage-drift-report.sh\` (#2315, companion assethold#31)."
} > "$OUT"

echo "[coverage-drift] wrote $OUT (status: $status, max drop ${max_drop}pp)"
