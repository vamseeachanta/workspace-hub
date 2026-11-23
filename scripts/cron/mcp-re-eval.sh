#!/usr/bin/env bash
# mcp-re-eval.sh — Quarterly re-evaluation of MCP server value across repos.
# Issue: #2316 (https://github.com/vamseeachanta/workspace-hub/issues/2316)
# Companion: #1804 (MCP eval: token-optimizer, omega-memory, evalview, insaits)
#
# Scans all .mcp.json files under the scan root, counts how many repos use
# each MCP server, and diffs the usage counts against last quarter's report.
# MCPs whose usage declined are flagged for review in "Recommended prunes".
#
# V1 scope: usage-count only. Token-saved / latency metrics depend on
# telemetry not yet wired — deferred to a follow-up bench per plan.
#
# Env overrides (testing):
#   MCP_OUT_DIR          — override docs/reports output dir
#   MCP_QUARTER          — override quarter (e.g. 2026-Q2)
#   MCP_PREV_QUARTER     — override previous quarter
#   MCP_SCAN_ROOT        — override scan root (default REPO_ROOT)
#   MCP_WARN_COUNT       — warn threshold (default 0)
#   MCP_BLOCK_COUNT      — block threshold (default 3)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/cadence-common.sh"
cadence_init_repo_root

QUARTER="${MCP_QUARTER:-$(cadence_period quarterly)}"
OUT_DIR="${MCP_OUT_DIR:-${REPO_ROOT}/docs/reports}"
OUT="${OUT_DIR}/mcp-re-eval-${QUARTER}.md"
PREV_QUARTER="${MCP_PREV_QUARTER:-}"
SCAN_ROOT="${MCP_SCAN_ROOT:-${REPO_ROOT}}"
WARN_COUNT="${MCP_WARN_COUNT:-0}"
BLOCK_COUNT="${MCP_BLOCK_COUNT:-3}"

# Auto-compute previous quarter if caller didn't provide one.
if [[ -z "$PREV_QUARTER" ]]; then
    year="${QUARTER%-Q*}"
    q="${QUARTER##*-Q}"
    if (( q == 1 )); then PREV_QUARTER="$((year - 1))-Q4"; else PREV_QUARTER="${year}-Q$((q - 1))"; fi
fi
PREV="${OUT_DIR}/mcp-re-eval-${PREV_QUARTER}.md"

mkdir -p "$OUT_DIR"

# ── Enumerate MCP servers across all .mcp.json under scan root ───────────
# Emits "server_name\trepo_name" for each server seen.
TMP_USAGE="$(mktemp)"
trap 'rm -f "$TMP_USAGE"' EXIT

# Iterate .mcp.json files at top-level of each child repo (depth <= 3).
while IFS= read -r cfg; do
    [[ -f "$cfg" ]] || continue
    # Repo = first path component under scan root (or "root" for root-level).
    rel="${cfg#${SCAN_ROOT}/}"
    if [[ "$rel" == .mcp.json ]]; then
        repo="_root"
    else
        repo="${rel%%/*}"
    fi
    # Parse JSON with python3 — avoids fragile awk brace tracking.
    python3 -c "
import json, sys
try:
    with open('$cfg') as f:
        cfg = json.load(f)
    for name in cfg.get('mcpServers', {}):
        print(name + '\t$repo')
except Exception:
    sys.exit(0)
" >> "$TMP_USAGE"
done < <(find "$SCAN_ROOT" -maxdepth 3 -name ".mcp.json" -type f 2>/dev/null)

# Deduplicate (repo, server) pairs and count repos per server.
sort -u -o "$TMP_USAGE" "$TMP_USAGE"
TMP_COUNTS="$(mktemp)"
trap 'rm -f "$TMP_USAGE" "$TMP_COUNTS"' EXIT
awk -F'\t' '{counts[$1]++} END {for (s in counts) printf "%s\t%d\n", s, counts[s]}' "$TMP_USAGE" | sort > "$TMP_COUNTS"

total_servers=$(wc -l < "$TMP_COUNTS" | tr -d ' ')

# ── Parse previous quarter's counts ──────────────────────────────────────
declare -A prev_counts=()
if [[ -f "$PREV" ]]; then
    while IFS=$'\t' read -r name count; do
        [[ -n "$name" ]] && prev_counts["$name"]="$count"
    done < <(awk '
        BEGIN{section=""}
        /^## Per-MCP scorecard/ {section="scorecard"; next}
        /^## /                  {section=""; next}
        section=="scorecard" && /^\| / && !/-----/ && !/MCP \|/ {
            n=split($0, p, "|")
            if (n >= 4) {
                gsub(/^ +| +$/, "", p[2])
                gsub(/^ +| +$/, "", p[4])
                if (p[2] != "MCP" && p[2] != "" && p[4] ~ /^[0-9]+$/) print p[2] "\t" p[4]
            }
        }
    ' "$PREV")
fi

# ── Build scorecard rows + prune candidates ──────────────────────────────
TMP_ROWS="$(mktemp)"
TMP_PRUNES="$(mktemp)"
TMP_NEW="$(mktemp)"
trap 'rm -f "$TMP_USAGE" "$TMP_COUNTS" "$TMP_ROWS" "$TMP_PRUNES" "$TMP_NEW"' EXIT

declined_count=0
# Current servers
while IFS=$'\t' read -r name count; do
    [[ -z "$name" ]] && continue
    prev="${prev_counts[$name]:-}"
    if [[ -z "$prev" ]]; then
        prev_cell="—"
        decision="new — evaluate"
        printf "| %s | newly added this quarter |\n" "$name" >> "$TMP_NEW"
    else
        prev_cell="$prev"
        if (( count < prev )); then
            decision="⚠️ declining — review"
            declined_count=$((declined_count + 1))
            printf "| %s | usage dropped %d → %d | per-repo \`.mcp.json\` |\n" "$name" "$prev" "$count" >> "$TMP_PRUNES"
        elif (( count > prev )); then
            decision="📈 growing"
        else
            decision="keep"
        fi
    fi
    printf "| %s | %d | %d | %s | %s |\n" "$name" "$count" "$count" "$prev_cell" "$decision" >> "$TMP_ROWS"
    unset 'prev_counts[$name]'
done < "$TMP_COUNTS"

# Servers that were in prev but are gone now → count=0, prune candidates.
for gone in "${!prev_counts[@]}"; do
    prev="${prev_counts[$gone]}"
    printf "| %s | 0 | 0 | %s | 🗑️ removed — confirm prune |\n" "$gone" "$prev" >> "$TMP_ROWS"
    printf "| %s | usage dropped %s → 0 | per-repo \`.mcp.json\` |\n" "$gone" "$prev" >> "$TMP_PRUNES"
    declined_count=$((declined_count + 1))
done

status="$(compute_status_band "$declined_count" "$WARN_COUNT" "$BLOCK_COUNT")"
summary="${declined_count} MCP(s) declined since ${PREV_QUARTER} (warn ${WARN_COUNT}, block ${BLOCK_COUNT}); ${total_servers} distinct servers in current configs"

# ── Write report ─────────────────────────────────────────────────────────
{
    emit_report_header "mcp-re-eval" "$QUARTER" "$status" "$summary"
    echo "Scan root: \`${SCAN_ROOT}\`"
    echo "Previous quarter report: \`$(basename "$PREV")\`$([[ -f "$PREV" ]] || echo ' (not found — first run)')"
    echo
    echo "## Per-MCP scorecard"
    echo
    echo "| MCP | Repos using | This Q | Last Q | Decision |"
    echo "|-----|-------------|--------|--------|----------|"
    if [[ -s "$TMP_ROWS" ]]; then
        sort "$TMP_ROWS"
    else
        echo "| — | 0 | 0 | — | _(no MCPs configured)_ |"
    fi
    echo
    echo "## Recommended prunes"
    echo
    if [[ -s "$TMP_PRUNES" ]]; then
        echo "| MCP | Reason | Config path |"
        echo "|-----|--------|-------------|"
        sort "$TMP_PRUNES"
    else
        echo "_No MCPs declined this quarter._"
    fi
    echo
    echo "## New this quarter"
    echo
    if [[ -s "$TMP_NEW" ]]; then
        echo "| MCP | Note |"
        echo "|-----|------|"
        sort "$TMP_NEW"
    else
        echo "_No new MCPs added this quarter._"
    fi
    echo
    echo "## Source"
    echo
    echo "Generated by \`scripts/cron/mcp-re-eval.sh\` (#2316, companion #1804)."
    echo "V1 reports usage count only. Tokens-saved / latency metrics deferred — require telemetry instrumentation."
} > "$OUT"

echo "[mcp-re-eval] wrote $OUT (status: $status, ${total_servers} servers, ${declined_count} declined)"
