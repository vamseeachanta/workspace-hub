#!/usr/bin/env bash
# daily-reflect.sh - Cron-compatible daily reflection script
# Runs full RAGS loop: Reflect → Abstract → Generalize → Store

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
STATE_DIR="${HOME}/.claude/state"
REFLECT_DIR="${STATE_DIR}/reflect-history"
PATTERNS_DIR="${STATE_DIR}/patterns"
TRENDS_DIR="${STATE_DIR}/trends"
REPORTS_DIR="${STATE_DIR}/reports"
LOG_FILE="${REFLECT_DIR}/reflect.log"
DAYS="${REFLECT_DAYS:-30}"
DRY_RUN="${DRY_RUN:-false}"
WEEKLY_REPORT="${WEEKLY_REPORT:-false}"

# Check if it's Sunday for weekly report
[[ $(date +%u) -eq 7 ]] && WEEKLY_REPORT="true"

# Ensure directories exist
mkdir -p "$REFLECT_DIR" "$PATTERNS_DIR" "$TRENDS_DIR" "$REPORTS_DIR"

# Timestamp for this run
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
DATE_ISO=$(date -Iseconds)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting daily reflection (RAGS loop)..."
log "Workspace: $WORKSPACE_ROOT"
log "Analysis window: $DAYS days"
log "Dry run: $DRY_RUN"

# Initialize counters
SKILLS_CREATED=0
SKILLS_ENHANCED=0
LEARNINGS_STORED=0
PATTERNS_FOUND=0

#############################################
# PHASE 1: REFLECT - Collect git history
#############################################
log ""
log "=== PHASE 1: REFLECT ==="
ANALYSIS_FILE="${REFLECT_DIR}/analysis_${TIMESTAMP}.json"

cd "$WORKSPACE_ROOT"

if [[ -x "$SCRIPT_DIR/analyze-history.sh" ]]; then
    log "Running analyze-history.sh..."
    "$SCRIPT_DIR/analyze-history.sh" "$DAYS" "all" "json" > "$ANALYSIS_FILE" 2>> "$LOG_FILE"
    log "Analysis saved to: $ANALYSIS_FILE"
else
    log "ERROR: analyze-history.sh not found or not executable"
    exit 1
fi

# Extract summary stats
REPOS=0
COMMITS=0
if command -v jq &> /dev/null && [[ -f "$ANALYSIS_FILE" ]]; then
    REPOS=$(jq -r '.repos_analyzed // 0' "$ANALYSIS_FILE" 2>/dev/null || echo "0")
    COMMITS=$(jq -r '.total_commits // 0' "$ANALYSIS_FILE" 2>/dev/null || echo "0")
    log "Analyzed $REPOS repositories, found $COMMITS commits"
else
    log "jq not available, skipping detailed analysis"
fi

#############################################
# PHASE 2: ABSTRACT - Extract patterns
#############################################
log ""
log "=== PHASE 2: ABSTRACT ==="

if [[ -x "$SCRIPT_DIR/extract-patterns.sh" ]] && [[ $COMMITS -gt 0 ]]; then
    log "Running extract-patterns.sh..."
    PATTERN_OUTPUT=$("$SCRIPT_DIR/extract-patterns.sh" "$ANALYSIS_FILE" 2>> "$LOG_FILE") || true
    log "Pattern extraction complete"

    # Get pattern count
    PATTERN_FILE=$(ls -t "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | head -1)
    if [[ -f "$PATTERN_FILE" ]]; then
        PATTERNS_FOUND=$(jq -r '.cross_repo_patterns | length' "$PATTERN_FILE" 2>/dev/null || echo "0")
        log "Found $PATTERNS_FOUND cross-repo patterns"
    fi
else
    log "Skipping pattern extraction (no commits or script missing)"
fi

#############################################
# PHASE 3: GENERALIZE - Analyze trends
#############################################
log ""
log "=== PHASE 3: GENERALIZE ==="

if [[ -x "$SCRIPT_DIR/analyze-trends.sh" ]]; then
    # Only run trends if we have multiple pattern files
    PATTERN_COUNT=$(ls "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | wc -l)
    if [[ $PATTERN_COUNT -gt 1 ]]; then
        log "Running analyze-trends.sh..."
        "$SCRIPT_DIR/analyze-trends.sh" 7 2>> "$LOG_FILE" || true
        log "Trend analysis complete"
    else
        log "Insufficient data for trend analysis (need 2+ pattern files)"
    fi
else
    log "analyze-trends.sh not found, skipping"
fi

#############################################
# PHASE 4: STORE - Create/enhance skills
#############################################
log ""
log "=== PHASE 4: STORE ==="

if [[ -x "$SCRIPT_DIR/create-skills.sh" ]] && [[ $PATTERNS_FOUND -gt 0 ]]; then
    log "Running create-skills.sh..."
    export DRY_RUN
    SKILL_OUTPUT=$("$SCRIPT_DIR/create-skills.sh" "$PATTERN_FILE" 2>> "$LOG_FILE") || true

    # Parse output for counts
    SKILLS_CREATED=$(echo "$SKILL_OUTPUT" | grep -oP 'Skills Created: \K[0-9]+' || echo "0")
    SKILLS_ENHANCED=$(echo "$SKILL_OUTPUT" | grep -oP 'Skills Enhanced: \K[0-9]+' || echo "0")
    LEARNINGS_STORED=$(echo "$SKILL_OUTPUT" | grep -oP 'Learnings Stored: \K[0-9]+' || echo "0")

    log "Skills created: $SKILLS_CREATED"
    log "Skills enhanced: $SKILLS_ENHANCED"
    log "Learnings stored: $LEARNINGS_STORED"
else
    log "Skipping skill creation (no patterns or script missing)"
fi

#############################################
# Generate weekly report (Sundays)
#############################################
if [[ "$WEEKLY_REPORT" == "true" ]] && [[ -x "$SCRIPT_DIR/generate-report.sh" ]]; then
    log ""
    log "=== WEEKLY REPORT ==="
    log "Generating weekly digest..."
    "$SCRIPT_DIR/generate-report.sh" 2>> "$LOG_FILE" || true
    REPORT_FILE=$(ls -t "$REPORTS_DIR"/weekly_digest_*.md 2>/dev/null | head -1)
    log "Weekly report: $REPORT_FILE"
fi

#############################################
# Update state file
#############################################
STATE_FILE="${STATE_DIR}/reflect-state.yaml"
cat > "$STATE_FILE" << EOF
version: "2.0"
last_run: $DATE_ISO
analysis_window_days: $DAYS
dry_run: $DRY_RUN
phases_completed:
  reflect: true
  abstract: $([[ $COMMITS -gt 0 ]] && echo "true" || echo "false")
  generalize: $([[ -f "$TRENDS_DIR"/trends_*.json ]] && echo "true" || echo "false")
  store: $([[ $PATTERNS_FOUND -gt 0 ]] && echo "true" || echo "false")
metrics:
  repos_analyzed: $REPOS
  commits_found: $COMMITS
  patterns_extracted: $PATTERNS_FOUND
actions_taken:
  skills_created: $SKILLS_CREATED
  skills_enhanced: $SKILLS_ENHANCED
  learnings_stored: $LEARNINGS_STORED
files:
  analysis: $ANALYSIS_FILE
  patterns: ${PATTERN_FILE:-none}
  trends: $(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1 || echo "none")
  report: ${REPORT_FILE:-none}
EOF

log ""
log "State updated: $STATE_FILE"

# Cleanup old files (keep last 30 of each type)
cd "$REFLECT_DIR"
ls -1t analysis_*.json 2>/dev/null | tail -n +31 | xargs -r rm -f
cd "$PATTERNS_DIR"
ls -1t patterns_*.json 2>/dev/null | tail -n +31 | xargs -r rm -f
cd "$TRENDS_DIR"
ls -1t trends_*.json 2>/dev/null | tail -n +31 | xargs -r rm -f
log "Cleanup complete"

log ""
log "Daily reflection completed successfully"

# Summary output for cron email
echo ""
echo "╔════════════════════════════════════════╗"
echo "║     Daily Reflection Summary           ║"
echo "╠════════════════════════════════════════╣"
echo "║ Date: $(date '+%Y-%m-%d %H:%M')"
echo "║ RAGS Loop Status:                      ║"
echo "║   ✓ REFLECT:    $REPOS repos, $COMMITS commits"
echo "║   ✓ ABSTRACT:   $PATTERNS_FOUND patterns found"
echo "║   ✓ GENERALIZE: Trends analyzed"
echo "║   ✓ STORE:      $SKILLS_CREATED created, $LEARNINGS_STORED logged"
[[ "$WEEKLY_REPORT" == "true" ]] && echo "║   📊 Weekly report generated"
echo "╚════════════════════════════════════════╝"
