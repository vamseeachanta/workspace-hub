#!/usr/bin/env bash
# broken-windows-sweep.sh — Monthly cross-repo pytest delta report.
# Issue: #2314 (https://github.com/vamseeachanta/workspace-hub/issues/2314)
# Companion: vamseeachanta/digitalmodel#510 (20 pre-existing OrcaFlex failures)
#
# Instead of re-executing the full suite, reads each tier-1 repo's cached
# `.claude/state/test-health.jsonl` and diffs the failing set against the
# previous month's report. Emits three sections:
#   - New failures (failing this month, not last)
#   - Resolved (passing this month, were failing last)
#   - Persistent (failing both months)
#
# Env overrides (testing):
#   BROKEN_WINDOWS_OUT_DIR       — override docs/reports output dir
#   BROKEN_WINDOWS_MONTH         — override month (e.g. 2026-04)
#   BROKEN_WINDOWS_PREV_MONTH    — override previous month
#   BROKEN_WINDOWS_REPOS         — comma-separated "name:path" pairs
#   BROKEN_WINDOWS_WARN_COUNT    — warn threshold on NEW failures (default 0)
#   BROKEN_WINDOWS_BLOCK_COUNT   — block threshold on NEW failures (default 5)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/cadence-common.sh"
cadence_init_repo_root

MONTH="${BROKEN_WINDOWS_MONTH:-$(cadence_period monthly)}"
PREV_MONTH="${BROKEN_WINDOWS_PREV_MONTH:-$(date -d "${MONTH}-01 -1 month" +%Y-%m 2>/dev/null || date +%Y-%m)}"
OUT_DIR="${BROKEN_WINDOWS_OUT_DIR:-${REPO_ROOT}/docs/reports}"
OUT="${OUT_DIR}/broken-windows-${MONTH}.md"
PREV="${OUT_DIR}/broken-windows-${PREV_MONTH}.md"
WARN_COUNT="${BROKEN_WINDOWS_WARN_COUNT:-0}"
BLOCK_COUNT="${BROKEN_WINDOWS_BLOCK_COUNT:-5}"

# Must match scripts/hooks/pre-push.sh:TIER1_REPOS to stay in sync.
declare -a REPO_NAMES=()
declare -a REPO_PATHS=()
if [[ -n "${BROKEN_WINDOWS_REPOS:-}" ]]; then
    IFS=',' read -ra pairs <<< "$BROKEN_WINDOWS_REPOS"
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

# ── Parse this month's failing set per repo (from cached jsonl) ──────────
# Emits "<repo>\t<test>" lines for failing tests.
TMP_CUR="$(mktemp)"
TMP_PASS="$(mktemp)"
TMP_PREV="$(mktemp)"
TMP_MISSING="$(mktemp)"
trap 'rm -f "$TMP_CUR" "$TMP_PASS" "$TMP_PREV" "$TMP_MISSING"' EXIT

for i in "${!REPO_NAMES[@]}"; do
    name="${REPO_NAMES[$i]}"
    jsonl="${REPO_PATHS[$i]}/.claude/state/test-health.jsonl"
    if [[ ! -f "$jsonl" ]]; then
        echo "$name" >> "$TMP_MISSING"
        continue
    fi
    # Failing + passing rows, keyed by the "test" field.
    awk -v repo="$name" '
        {
            # crude JSON field extract — tests/ only need status/test keys
            if (match($0, /"status" *: *"FAIL"/) > 0 && match($0, /"test" *: *"[^"]+"/) > 0) {
                t = substr($0, RSTART, RLENGTH); sub(/^"test" *: *"/, "", t); sub(/"$/, "", t)
                print repo "\t" t
            }
        }
    ' "$jsonl" >> "$TMP_CUR"
    awk -v repo="$name" '
        {
            if (match($0, /"status" *: *"PASS"/) > 0 && match($0, /"test" *: *"[^"]+"/) > 0) {
                t = substr($0, RSTART, RLENGTH); sub(/^"test" *: *"/, "", t); sub(/"$/, "", t)
                print repo "\t" t
            }
        }
    ' "$jsonl" >> "$TMP_PASS"
done

# ── Parse previous month's failing set from the prior report ─────────────
# Extracts rows from "Persistent failures" + "New failures" sections.
if [[ -f "$PREV" ]]; then
    awk '
        BEGIN{section=""}
        /^## New failures/           {section="new"; next}
        /^## Persistent failures/    {section="persistent"; next}
        /^## Resolved failures/      {section="resolved"; next}
        /^## /                       {section=""; next}
        (section=="new" || section=="persistent") && /^\| / && !/-----/ && !/Repo \| Test/ {
            # row format: "| repo | test | ..."
            n = split($0, p, "|")
            if (n >= 4) {
                gsub(/^ +| +$/, "", p[2])
                gsub(/^ +| +$/, "", p[3])
                if (p[2] != "Repo" && p[2] != "") print p[2] "\t" p[3]
            }
        }
    ' "$PREV" | sort -u > "$TMP_PREV"
fi

sort -u -o "$TMP_CUR" "$TMP_CUR"
sort -u -o "$TMP_PASS" "$TMP_PASS"

# ── Compute diffs ────────────────────────────────────────────────────────
# new = current \ prev
# resolved = prev ∩ current-passing  (i.e., prev failing, now passing)
# persistent = current ∩ prev
TMP_NEW="$(mktemp)"
TMP_RESOLVED="$(mktemp)"
TMP_PERSIST="$(mktemp)"
trap 'rm -f "$TMP_CUR" "$TMP_PASS" "$TMP_PREV" "$TMP_MISSING" "$TMP_NEW" "$TMP_RESOLVED" "$TMP_PERSIST"' EXIT

if [[ -s "$TMP_PREV" ]]; then
    comm -23 "$TMP_CUR" "$TMP_PREV" > "$TMP_NEW"
    comm -12 "$TMP_CUR" "$TMP_PREV" > "$TMP_PERSIST"
    comm -12 "$TMP_PASS" "$TMP_PREV" > "$TMP_RESOLVED"
else
    # First run: every current failure is NEW
    cp "$TMP_CUR" "$TMP_NEW"
    : > "$TMP_PERSIST"
    : > "$TMP_RESOLVED"
fi

new_count=$(wc -l < "$TMP_NEW" | tr -d ' ')
resolved_count=$(wc -l < "$TMP_RESOLVED" | tr -d ' ')
persistent_count=$(wc -l < "$TMP_PERSIST" | tr -d ' ')

status="$(compute_status_band "$new_count" "$WARN_COUNT" "$BLOCK_COUNT")"
summary="${new_count} newly-failing, ${resolved_count} resolved, ${persistent_count} persistent (warn ${WARN_COUNT}, block ${BLOCK_COUNT})"

# ── Write report ─────────────────────────────────────────────────────────
emit_rows() {
    local src="$1" cols="$2"
    if [[ -s "$src" ]]; then
        awk -F'\t' -v cols="$cols" '{
            if (cols == 3) printf "| %s | %s | — |\n", $1, $2
            else printf "| %s | %s |\n", $1, $2
        }' "$src"
    else
        echo "| — | _(none)_ |"
    fi
}

{
    emit_report_header "broken-windows" "$MONTH" "$status" "$summary"
    echo "Baseline: \`$(basename "$PREV")\`$([[ -f "$PREV" ]] || echo ' (not found — first run: all failures are NEW)')"
    echo
    echo "Repos scanned: ${#REPO_NAMES[@]}"
    if [[ -s "$TMP_MISSING" ]]; then
        echo
        echo "Repos without cached test-health.jsonl (no data):"
        while IFS= read -r r; do echo "- \`$r\`"; done < "$TMP_MISSING"
    fi
    echo

    echo "## New failures (first time in this month)"
    echo
    echo "| Repo | Test | Error summary |"
    echo "|------|------|---------------|"
    emit_rows "$TMP_NEW" 3
    echo

    echo "## Resolved failures (now passing; were failing last month)"
    echo
    echo "| Repo | Test |"
    echo "|------|------|"
    emit_rows "$TMP_RESOLVED" 2
    echo

    echo "## Persistent failures (still failing — pre-existing)"
    echo
    echo "| Repo | Test | First seen |"
    echo "|------|------|-----------|"
    emit_rows "$TMP_PERSIST" 3
    echo

    echo "## Source"
    echo
    echo "Generated by \`scripts/cron/broken-windows-sweep.sh\` (#2314, companion digitalmodel#510)."
    echo "Reads cached \`.claude/state/test-health.jsonl\`. Run with \`--run\` (future flag) to re-execute pytest."
} > "$OUT"

echo "[broken-windows] wrote $OUT (status: $status, ${new_count} new / ${resolved_count} resolved / ${persistent_count} persistent)"
