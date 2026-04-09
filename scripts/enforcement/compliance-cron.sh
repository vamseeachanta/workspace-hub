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
LOG_DIR="${REPO_ROOT}/logs/compliance"
LOG_FILE="${LOG_DIR}/daily-${DATE_COMPACT}.log"
DASHBOARD_SCRIPT="${SCRIPT_DIR}/compliance-dashboard.sh"
DRY_RUN="${DRY_RUN:-false}"

# Alert thresholds
THRESHOLD_HIGH=50    # Below this: create issue with priority:high
THRESHOLD_CRITICAL=30  # Below this: add priority:critical
THRESHOLD_PASS=80    # At or above this: log as pass, no action

mkdir -p "$LOG_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"; }

# ── Run compliance dashboard ─────────────────────────────────────────────────
log "Starting daily compliance check"

if [[ ! -x "$DASHBOARD_SCRIPT" ]]; then
    log "ERROR: Dashboard script not found or not executable: $DASHBOARD_SCRIPT"
    exit 1
fi

DASHBOARD_OUTPUT="$(bash "$DASHBOARD_SCRIPT" 2>&1)" || true
echo "$DASHBOARD_OUTPUT" >> "$LOG_FILE"

# ── Parse compliance percentage from output ──────────────────────────────────
# The dashboard outputs: "Compliance rate:    NN% (threshold: MM%)"
COMPLIANCE_RATE="$(echo "$DASHBOARD_OUTPUT" | grep -oP 'Compliance rate:\s+\K[0-9]+' || echo "")"

if [[ -z "$COMPLIANCE_RATE" ]]; then
    # Try to parse from JSON output as fallback
    COMPLIANCE_RATE="$(echo "$DASHBOARD_OUTPUT" | grep -oP '"compliance_rate":\s*\K[0-9]+' || echo "")"
fi

if [[ -z "$COMPLIANCE_RATE" ]]; then
    # Check if there were no commits (which is fine)
    if echo "$DASHBOARD_OUTPUT" | grep -q '"total_commits": *0\|No commits in window'; then
        log "No commits in window — nothing to check"
        exit 0
    fi
    log "WARNING: Could not parse compliance rate from dashboard output"
    exit 0
fi

log "Compliance rate: ${COMPLIANCE_RATE}%"

# ── Parse additional details from JSON ───────────────────────────────────────
TOTAL_COMMITS="$(echo "$DASHBOARD_OUTPUT" | grep -oP '"total_commits":\s*\K[0-9]+' || echo "?")"
REVIEWED="$(echo "$DASHBOARD_OUTPUT" | grep -oP '"reviewed":\s*\K[0-9]+' || echo "?")"
UNREVIEWED="$(echo "$DASHBOARD_OUTPUT" | grep -oP '"unreviewed":\s*\K[0-9]+' || echo "?")"
VERDICT="$(echo "$DASHBOARD_OUTPUT" | grep -oP '"verdict":\s*"\K[^"]+' || echo "?")"

# ── Threshold evaluation ─────────────────────────────────────────────────────
if [[ "$COMPLIANCE_RATE" -ge "$THRESHOLD_PASS" ]]; then
    log "PASS: Compliance at ${COMPLIANCE_RATE}% (>= ${THRESHOLD_PASS}%) — no action needed"
    exit 0
fi

# Compliance is below pass threshold — determine severity
PRIORITY_LABEL="priority:medium"
SEVERITY="medium"
if [[ "$COMPLIANCE_RATE" -lt "$THRESHOLD_CRITICAL" ]]; then
    PRIORITY_LABEL="priority:critical"
    SEVERITY="critical"
elif [[ "$COMPLIANCE_RATE" -lt "$THRESHOLD_HIGH" ]]; then
    PRIORITY_LABEL="priority:high"
    SEVERITY="high"
fi

log "ALERT: Compliance at ${COMPLIANCE_RATE}% — severity: ${SEVERITY}"

# ── Deduplication: check for existing open compliance issue this week ────────
# "This week" = same ISO week number
WEEK_NUM="$(date +%V)"
YEAR="$(date +%Y)"
DEDUP_KEY="compliance-alert-${YEAR}-W${WEEK_NUM}"

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
    --search "Compliance alert: W${WEEK_NUM}" \
    --json number,title \
    --jq '.[0].number' 2>/dev/null || true)"

# ── Build unreviewed commits section ─────────────────────────────────────────
UNREVIEWED_SECTION=""
# Extract unreviewed commits from dashboard output (lines starting with "  - ")
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    UNREVIEWED_SECTION="${UNREVIEWED_SECTION}${line}
"
done < <(echo "$DASHBOARD_OUTPUT" | grep -E '^\s+- [0-9a-f]' || true)

# ── Create or update GitHub issue ────────────────────────────────────────────
ISSUE_TITLE="Compliance alert: W${WEEK_NUM} — ${COMPLIANCE_RATE}% (${SEVERITY})"

ISSUE_BODY="## Compliance Alert — ${DATE_ISO}

**Compliance rate:** ${COMPLIANCE_RATE}% | **Severity:** ${SEVERITY}
**Total commits:** ${TOTAL_COMMITS} | **Reviewed:** ${REVIEWED} | **Unreviewed:** ${UNREVIEWED}
**Dashboard verdict:** ${VERDICT}

### Unreviewed Commits
\`\`\`
${UNREVIEWED_SECTION:-No details available — check daily log}
\`\`\`

### Thresholds
| Range | Action |
|-------|--------|
| >= 80% | Pass — no action |
| 50-79% | Medium priority issue |
| 30-49% | High priority issue |
| < 30% | Critical — immediate action |

### Recommended Actions
- [ ] Run cross-review on unreviewed commits
- [ ] Investigate bypass patterns
- [ ] Address root cause if systemic

---
*Auto-generated by \`scripts/enforcement/compliance-cron.sh\` (#2031)*
*Dedup key: ${DEDUP_KEY}*"

if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY RUN] Would create/update issue: $ISSUE_TITLE"
    log "[DRY RUN] Labels: compliance-alert, ${PRIORITY_LABEL}"
    echo "$ISSUE_BODY" >> "$LOG_FILE"
    exit 0
fi

# Ensure labels exist (idempotent)
gh label create "compliance-alert" --description "Automated compliance threshold alert" --color "D93F0B" 2>/dev/null || true
gh label create "priority:high" --description "High priority" --color "FF6600" 2>/dev/null || true
gh label create "priority:critical" --description "Critical — immediate action" --color "B60205" 2>/dev/null || true
gh label create "priority:medium" --description "Medium priority" --color "FBCA04" 2>/dev/null || true

if [[ -n "$EXISTING_ISSUE" && "$EXISTING_ISSUE" != "null" ]]; then
    # Update existing issue with new data
    gh issue comment "$EXISTING_ISSUE" --body "## Update — ${DATE_ISO}

**Compliance rate:** ${COMPLIANCE_RATE}% | **Severity:** ${SEVERITY}
**Total:** ${TOTAL_COMMITS} | **Reviewed:** ${REVIEWED} | **Unreviewed:** ${UNREVIEWED}

${UNREVIEWED_SECTION:-No details available}" >/dev/null 2>&1

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
        log "WARNING: Failed to create GitHub issue: $ISSUE_URL"
    }

    if [[ -n "$ISSUE_URL" && "$ISSUE_URL" == http* ]]; then
        log "Created compliance alert issue: $ISSUE_URL"
    fi
fi

log "Daily compliance check complete"
