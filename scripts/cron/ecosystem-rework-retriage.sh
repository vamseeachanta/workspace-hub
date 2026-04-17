#!/usr/bin/env bash
# ecosystem-rework-retriage.sh — Quarterly re-triage of ecosystem rework candidates.
# Issue: #2319 (https://github.com/vamseeachanta/workspace-hub/issues/2319)
# Companion: docs/reports/2026-04-16-ecosystem-rework-candidates.md (2026-Q1 baseline)
#
# Re-runs the Q1 ecosystem-rework triage and emits a delta report:
#   - Which Tier-1 candidates shipped (closed with commits)
#   - Which are in progress (open with recent activity)
#   - Which stalled (open, no activity in 90 days)
#   - New Tier-1 candidates surfaced since last quarter
#
# V1: rules-based deterministic scoring. Sub-agent deep-triage mode as
# a --deep flag is a follow-up (plan §Risks).
#
# Env overrides (testing):
#   ECOSYSTEM_OUT_DIR        — override docs/reports output dir
#   ECOSYSTEM_QUARTER        — override quarter (e.g. 2026-Q2)
#   ECOSYSTEM_ISSUE_STATES   — JSON file mapping issue ref -> state snapshot
#                              (bypasses `gh` calls; used by tests)
#   ECOSYSTEM_WARN_COUNT     — stalled threshold for YELLOW (default 2)
#   ECOSYSTEM_BLOCK_COUNT    — stalled threshold for RED    (default 6)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/cadence-common.sh"
cadence_init_repo_root

QUARTER="${ECOSYSTEM_QUARTER:-$(cadence_period quarterly)}"
OUT_DIR="${ECOSYSTEM_OUT_DIR:-${REPO_ROOT}/docs/reports}"
OUT="${OUT_DIR}/ecosystem-rework-${QUARTER}.md"
WARN_COUNT="${ECOSYSTEM_WARN_COUNT:-2}"
BLOCK_COUNT="${ECOSYSTEM_BLOCK_COUNT:-6}"
STATES_FILE="${ECOSYSTEM_ISSUE_STATES:-}"

mkdir -p "$OUT_DIR"

# ── Find most recent prior ecosystem-rework report (baseline) ───────────
BASELINE=""
BASELINE_NAME=""
if compgen -G "${OUT_DIR}/*ecosystem-rework*.md" > /dev/null; then
    # Most recent by filename (ISO-date prefix sorts naturally)
    BASELINE="$(ls -1 "${OUT_DIR}"/*ecosystem-rework*.md | grep -v "${QUARTER}" | sort | tail -1)"
    BASELINE_NAME="$(basename "$BASELINE")"
fi

# ── Extract Tier-1 and Tier-2 issue refs from baseline ──────────────────
TMP_REFS="$(mktemp)"
trap 'rm -f "$TMP_REFS"' EXIT

if [[ -n "$BASELINE" && -f "$BASELINE" ]]; then
    # Match rows in tier tables. Issue refs look like wh#1839, dm#503, etc.
    grep -oE '\| *([a-z]+#[0-9]+) *\|' "$BASELINE" | \
        sed -E 's/^\| *//; s/ *\|$//' | sort -u > "$TMP_REFS"
fi

# ── Query issue state (from fixture or stub-out if no gh) ───────────────
get_state() {
    local ref="$1"
    if [[ -n "$STATES_FILE" && -f "$STATES_FILE" ]]; then
        python3 -c "
import json, sys
try:
    with open('$STATES_FILE') as f: d = json.load(f)
    v = d.get('$ref', {})
    print(v.get('state', 'unknown'))
    print(v.get('days_since_activity', -1))
    print(v.get('commits', 0))
    print(v.get('title', ''))
except Exception:
    print('unknown'); print(-1); print(0); print('')
"
    elif command -v gh >/dev/null 2>&1; then
        # Live mode — query gh for real state. Map short prefix to owner/repo.
        local prefix="${ref%%#*}"
        local num="${ref##*#}"
        local repo=""
        case "$prefix" in
            wh)   repo="vamseeachanta/workspace-hub" ;;
            dm)   repo="vamseeachanta/digitalmodel" ;;
            wed)  repo="vamseeachanta/worldenergydata" ;;
            au)   repo="vamseeachanta/assetutilities" ;;
            ah)   repo="vamseeachanta/assethold" ;;
            og)   repo="vamseeachanta/OGManufacturing" ;;
            *)    printf "unknown\n-1\n0\n\n"; return ;;
        esac
        local json
        json=$(timeout 15 gh issue view "$num" --repo "$repo" \
            --json state,updatedAt,title 2>/dev/null || echo "{}")
        python3 -c "
import json, sys, datetime
try:
    d = json.loads('''$json''')
    state = d.get('state', 'unknown').lower()
    title = d.get('title', '')
    updated = d.get('updatedAt', '')
    if updated:
        dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
        days = (datetime.datetime.now(datetime.timezone.utc) - dt).days
    else:
        days = -1
    print(state)
    print(days)
    print(0)  # commit count deferred — separate gh API
    print(title)
except Exception:
    print('unknown'); print(-1); print(0); print('')
"
    else
        # No states file and no gh → stub mode
        printf "unknown\n-1\n0\n\n"
    fi
}

classify() {
    local state="$1" days="$2" commits="$3"
    if [[ "$state" == "closed" ]]; then
        echo "shipped"
    elif [[ "$state" == "open" && "$days" != "-1" && "$days" -le 30 && "$commits" -gt 0 ]]; then
        echo "in progress"
    elif [[ "$state" == "open" && "$days" != "-1" && "$days" -gt 90 ]]; then
        echo "stalled"
    elif [[ "$state" == "open" ]]; then
        echo "pending"
    else
        echo "unknown"
    fi
}

# ── Build delta rows ────────────────────────────────────────────────────
TMP_DELTA="$(mktemp)"
TMP_NEW="$(mktemp)"
trap 'rm -f "$TMP_REFS" "$TMP_DELTA" "$TMP_NEW"' EXIT

stalled_count=0
shipped_count=0
inprogress_count=0

idx=0
if [[ -s "$TMP_REFS" ]]; then
    while IFS= read -r ref; do
        idx=$((idx + 1))
        state_info=$(get_state "$ref")
        state=$(echo "$state_info" | sed -n 1p)
        days=$(echo "$state_info" | sed -n 2p)
        commits=$(echo "$state_info" | sed -n 3p)
        verdict=$(classify "$state" "$days" "$commits")
        case "$verdict" in
            shipped)      shipped_count=$((shipped_count + 1)) ;;
            "in progress") inprogress_count=$((inprogress_count + 1)) ;;
            stalled)      stalled_count=$((stalled_count + 1)) ;;
        esac
        printf "| %d | %s | %s | %s | %s |\n" \
            "$idx" "$ref" "$verdict" "$commits" "${days}d" >> "$TMP_DELTA"
    done < "$TMP_REFS"
fi

# ── Scan states file for NEW candidates not present in baseline ─────────
if [[ -n "$STATES_FILE" && -f "$STATES_FILE" ]]; then
    python3 -c "
import json, sys
with open('$STATES_FILE') as f: d = json.load(f)
with open('$TMP_REFS') as f: existing = {ln.strip() for ln in f if ln.strip()}
for ref, v in d.items():
    if ref in existing: continue
    if not v.get('new'): continue
    title = v.get('title', '')
    print(f'| {ref} | {title} | opened recently |')
" >> "$TMP_NEW"
fi

status="$(compute_status_band "$stalled_count" "$WARN_COUNT" "$BLOCK_COUNT")"
total=$idx
summary="${shipped_count} shipped, ${inprogress_count} in progress, ${stalled_count} stalled (of ${total} from ${BASELINE_NAME:-baseline})"

# ── Write report ────────────────────────────────────────────────────────
{
    emit_report_header "ecosystem-rework" "$QUARTER" "$status" "$summary"
    if [[ -z "$BASELINE" ]]; then
        echo "> First run — no prior ecosystem-rework report found."
        echo "> Subsequent quarters will diff against this baseline."
    else
        echo "Baseline: \`${BASELINE_NAME}\`"
    fi
    echo
    echo "## Delta vs last quarter"
    echo
    echo "| # | Issue | Status | Commits (ref) | Days since activity |"
    echo "|---|-------|--------|---------------|---------------------|"
    if [[ -s "$TMP_DELTA" ]]; then
        cat "$TMP_DELTA"
    else
        echo "| — | _(no baseline to diff against)_ | — | — | — |"
    fi
    echo
    echo "## New Tier-1 candidates"
    echo
    if [[ -s "$TMP_NEW" ]]; then
        echo "| Issue | Title | Why now |"
        echo "|-------|-------|---------|"
        cat "$TMP_NEW"
    else
        echo "_No newly-opened Tier-1 candidates surfaced this quarter._"
    fi
    echo
    echo "## Dropped from Tier-1 (obviated / deprioritized)"
    echo
    echo "_Manual review — auto-detection of obviation requires sub-agent deep-triage (--deep flag, follow-up)._"
    echo
    echo "## Source"
    echo
    echo "Generated by \`scripts/cron/ecosystem-rework-retriage.sh\` (#2319)."
    echo "V1 = rules-based scoring (deterministic). \`--deep\` sub-agent mode deferred."
} > "$OUT"

echo "[ecosystem-rework-retriage] wrote $OUT (status: $status, ${shipped_count}S/${inprogress_count}IP/${stalled_count}ST of ${total})"
