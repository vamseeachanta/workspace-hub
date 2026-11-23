#!/usr/bin/env bash
# weekly-governance-check.sh — Weekly conformance + freshness checks for the intelligence pyramid
#
# Runs pyramid-conformance-check.py and registry-freshness-check.py,
# writes dated JSON reports, and creates GitHub issues for failures.
#
# Usage: bash scripts/knowledge/weekly-governance-check.sh [--dry-run]
# Issues: #2206 (conformance), #1614 (freshness), #2105 (cadences)
set -uo pipefail

export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
DATE_TAG=$(date -u +%Y%m%d)
DRY_RUN=false

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

# ── Directories ─────────────────────────────────────────────────────────────
CONFORMANCE_LOG_DIR="${REPO_ROOT}/logs/conformance"
FRESHNESS_LOG_DIR="${REPO_ROOT}/logs/registry"
CONFORMANCE_REPORT="${CONFORMANCE_LOG_DIR}/pyramid-conformance-${DATE_TAG}.json"
FRESHNESS_REPORT="${FRESHNESS_LOG_DIR}/freshness-${DATE_TAG}.json"
LOG_FILE="${CONFORMANCE_LOG_DIR}/governance-${DATE}.log"

mkdir -p "$CONFORMANCE_LOG_DIR" "$FRESHNESS_LOG_DIR"

log() { echo "[governance] $(date -u +%H:%M:%S) $*" | tee -a "$LOG_FILE"; }

log "=== Weekly governance check: ${DATE} ==="
log "Dry run: ${DRY_RUN}"

# ── Hostname guard ──────────────────────────────────────────────────────────
source "${REPO_ROOT}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── 1. Pyramid conformance check ───────────────────────────────────────────
log "Running pyramid conformance check..."
CONFORMANCE_EXIT=0
cd "$REPO_ROOT" || exit 1

if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would run: uv run scripts/knowledge/pyramid-conformance-check.py --json"
else
    uv run scripts/knowledge/pyramid-conformance-check.py --json > "$CONFORMANCE_REPORT" 2>>"$LOG_FILE" || CONFORMANCE_EXIT=$?

    if [[ $CONFORMANCE_EXIT -ne 0 ]]; then
        # Count failures from JSON output
        FAIL_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('${CONFORMANCE_REPORT}'))
    print(sum(1 for c in data.get('checks', []) if c.get('status') == 'fail'))
except: print('?')
" 2>/dev/null)
        log "WARNING: conformance check found ${FAIL_COUNT} failure(s) (exit ${CONFORMANCE_EXIT})"

        # Create or skip GitHub issue
        EXISTING=$(gh issue list --state open --search '"Pyramid conformance failure"' --json number --jq '.[0].number' 2>/dev/null || true)
        if [[ -z "$EXISTING" ]]; then
            gh issue create \
                --title "Pyramid conformance failure (${DATE})" \
                --body "Weekly conformance check found **${FAIL_COUNT}** failing check(s).

- Date: ${DATE}
- Report: \`logs/conformance/pyramid-conformance-${DATE_TAG}.json\`
- Run locally: \`uv run scripts/knowledge/pyramid-conformance-check.py\`

Issues: #2206, #2105" \
                --label "bug,priority:medium,domain:knowledge-management" 2>>"$LOG_FILE" || \
                log "WARN: Failed to create conformance issue"
        else
            log "Open conformance issue already exists (#${EXISTING}) — skipping"
        fi
    else
        log "Conformance check passed"
    fi
fi

# ── 2. Registry freshness check ───────────────────────────────────────────
log "Running registry freshness check..."
FRESHNESS_EXIT=0

if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would run: uv run scripts/knowledge/registry-freshness-check.py --json"
else
    uv run scripts/knowledge/registry-freshness-check.py --json > "$FRESHNESS_REPORT" 2>>"$LOG_FILE" || FRESHNESS_EXIT=$?

    # Parse dead link count from JSON
    DEAD_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('${FRESHNESS_REPORT}'))
    print(len(data.get('dead_links', [])))
except: print('?')
" 2>/dev/null)
    ALIVE_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('${FRESHNESS_REPORT}'))
    print(data.get('summary', {}).get('alive', '?'))
except: print('?')
" 2>/dev/null)
    TOTAL_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('${FRESHNESS_REPORT}'))
    print(data.get('total_checked', '?'))
except: print('?')
" 2>/dev/null)

    log "Freshness check: ${ALIVE_COUNT}/${TOTAL_COUNT} alive, ${DEAD_COUNT} dead"

    if [[ "$DEAD_COUNT" != "0" && "$DEAD_COUNT" != "?" ]]; then
        EXISTING=$(gh issue list --state open --search '"Registry freshness"' --json number --jq '.[0].number' 2>/dev/null || true)
        if [[ -z "$EXISTING" ]]; then
            gh issue create \
                --title "Registry freshness: ${DEAD_COUNT} dead link(s) (${DATE})" \
                --body "Weekly freshness check found **${DEAD_COUNT}** dead link(s) in \`online-resource-registry.yaml\`.

- Alive: ${ALIVE_COUNT}/${TOTAL_COUNT}
- Report: \`logs/registry/freshness-${DATE_TAG}.json\`
- Run locally: \`uv run scripts/knowledge/registry-freshness-check.py\`

Issue: #1614" \
                --label "bug,priority:medium,cat:document-intelligence" 2>>"$LOG_FILE" || \
                log "WARN: Failed to create freshness issue"
        else
            log "Open registry-health issue already exists (#${EXISTING}) — skipping"
        fi
    else
        log "No dead links found"
    fi
fi

# ── Summary ─────────────────────────────────────────────────────────────────
log ""
log "=== Governance Summary ==="
log "  Date:               ${DATE}"
log "  Conformance exit:   ${CONFORMANCE_EXIT}"
log "  Freshness exit:     ${FRESHNESS_EXIT}"
log "  Dry run:            ${DRY_RUN}"
log "=== Done ==="

# Exit non-zero if either check failed
if [[ ${CONFORMANCE_EXIT} -ne 0 ]] || [[ ${FRESHNESS_EXIT} -ne 0 ]]; then
    exit 1
fi
