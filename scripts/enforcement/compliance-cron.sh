#!/usr/bin/env bash
# ABOUTME: Daily cron wrapper for compliance-dashboard.sh.
# ABOUTME: Runs compliance check, logs output, and creates GitHub alerts when thresholds are breached.
# Registered in config/scheduled-tasks/schedule-tasks.yaml at 06:00 daily.
# Issues: #2031

set -uo pipefail

# ── Ensure PATH for cron environment ────────────────────────────────────────
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: Not inside a git repository" >&2
    exit 1
}

DATE_COMPACT="$(date +%Y%m%d)"
DATE_ISO="$(date +%Y-%m-%d)"
LOG_DIR="${COMPLIANCE_REPORTS_DIR:-${REPO_ROOT}/logs/compliance}"
LOG_FILE="${LOG_DIR}/daily-${DATE_COMPACT}.log"
DASHBOARD_SCRIPT="${SCRIPT_DIR}/compliance-dashboard.sh"
DRY_RUN="${DRY_RUN:-false}"

mkdir -p "$LOG_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"; }

# ── Run compliance dashboard ─────────────────────────────────────────────────
log "Starting daily compliance check"

if [[ ! -x "$DASHBOARD_SCRIPT" ]]; then
    log "ERROR: Dashboard script not found or not executable: $DASHBOARD_SCRIPT"
    exit 1
fi

# Use one machine-readable document; nested diagnostic verdicts are unrelated.
DASHBOARD_STATUS=0
DASHBOARD_OUTPUT="$(cd "$REPO_ROOT" && bash "$DASHBOARD_SCRIPT" --json)" || DASHBOARD_STATUS=$?
printf '%s\n' "$DASHBOARD_OUTPUT" >> "$LOG_FILE"
if [[ "$DASHBOARD_STATUS" -ne 0 && "$DASHBOARD_STATUS" -ne 1 ]]; then
    log "ERROR: Dashboard execution failed (status ${DASHBOARD_STATUS})"
    exit 1
fi

# ISO week year is required at calendar-year boundaries.
ISO_WEEK="$(date +%G-W%V)"
ALERT_OUTPUT="$(printf '%s\n' "$DASHBOARD_OUTPUT" | python3 "${SCRIPT_DIR}/compliance_alert.py" \
    --date "$DATE_ISO" --week "$ISO_WEEK")" || {
    log "ERROR: Dashboard report validation failed"
    exit 1
}
mapfile -t ALERT_LINES <<< "$ALERT_OUTPUT"
ACTION="${ALERT_LINES[0]}"
COMPLIANCE_RATE="${ALERT_LINES[1]}"

# A FAIL report must exit 1; a PASS report must exit 0.
if [[ ( "$ACTION" == "alert" && "$DASHBOARD_STATUS" -ne 1 ) ||
      ( "$ACTION" == "no-alert" && "$DASHBOARD_STATUS" -ne 0 ) ]]; then
    log "ERROR: Dashboard exit status disagrees with report verdict"
    exit 1
fi
if [[ "$ACTION" == "no-alert" ]]; then
    log "PASS: No alert required (compliance ${COMPLIANCE_RATE}%)"
    exit 0
fi

SEVERITY="${ALERT_LINES[2]}"
PRIORITY_LABEL="${ALERT_LINES[3]}"
ISSUE_TITLE="${ALERT_LINES[4]}"
printf -v ISSUE_BODY '%s\n' "${ALERT_LINES[@]:5}"

DEDUP_KEY="compliance-alert-${ISO_WEEK}"
log "ALERT: Compliance at ${COMPLIANCE_RATE}% — severity: ${SEVERITY}"

# Dry runs must work offline and must never invoke the publisher, including auth.
if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY RUN] Would create/update issue: $ISSUE_TITLE"
    log "[DRY RUN] Labels: compliance-alert, ${PRIORITY_LABEL}"
    printf '%s\n' "$ISSUE_BODY" >> "$LOG_FILE"
    exit 0
fi

# Check gh authentication
if ! command -v gh >/dev/null 2>&1; then
    log "WARNING: gh CLI not available — skipping issue creation"
    exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
    log "WARNING: gh CLI not authenticated — skipping issue creation"
    exit 0
fi

# Search for existing open compliance alert this week
EXISTING_ISSUE="$(gh issue list \
    --state open \
    --label "compliance-alert" \
    --search "${DEDUP_KEY} in:body" \
    --json number,title \
    --jq '.[0].number' 2>/dev/null)" || {
    log "ERROR: Failed to search for an existing compliance issue"
    exit 1
}

# Ensure labels exist (idempotent)
gh label create "compliance-alert" --description "Automated compliance threshold alert" --color "D93F0B" 2>/dev/null || true
gh label create "priority:high" --description "High priority" --color "FF6600" 2>/dev/null || true
gh label create "priority:critical" --description "Critical — immediate action" --color "B60205" 2>/dev/null || true
gh label create "priority:medium" --description "Medium priority" --color "FBCA04" 2>/dev/null || true

if [[ -n "$EXISTING_ISSUE" && "$EXISTING_ISSUE" != "null" ]]; then
    # Update existing issue with new data
    gh issue comment "$EXISTING_ISSUE" --body "$ISSUE_BODY" >/dev/null 2>&1 || {
        log "ERROR: Failed to update compliance issue"
        exit 1
    }

    # Update severity label if it changed
    gh issue edit "$EXISTING_ISSUE" --add-label "$PRIORITY_LABEL" >/dev/null 2>&1 || true

    log "Updated existing compliance issue: #${EXISTING_ISSUE}"
else
    # Create new issue
    ISSUE_URL="$(gh issue create \
        --title "$ISSUE_TITLE" \
        --body "$ISSUE_BODY" \
        --label "compliance-alert" \
        --label "$PRIORITY_LABEL" \
        2>&1)" || {
        log "ERROR: Failed to create compliance issue"
        exit 1
    }

    if [[ -n "$ISSUE_URL" && "$ISSUE_URL" == http* ]]; then
        log "Created compliance alert issue: $ISSUE_URL"
    fi
fi

log "Daily compliance check complete"
