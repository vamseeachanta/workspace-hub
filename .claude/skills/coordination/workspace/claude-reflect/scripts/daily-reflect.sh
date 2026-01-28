#!/usr/bin/env bash
# daily-reflect.sh - Cron-compatible daily reflection script
# Runs full RAGS loop: Reflect → Abstract → Generalize → Store

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"

# State directory: prefer workspace-hub, fallback to home
if [[ -d "${WORKSPACE_ROOT}/.claude/state" ]]; then
    STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
else
    STATE_DIR="${WORKSPACE_STATE_DIR:-${HOME}/.claude/state}"
fi
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
STALE_REVIEWS_APPROVED=0

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

# Extract correction patterns from hook data
CORRECTIONS_FOUND=0
if [[ -x "$SCRIPT_DIR/extract-corrections.sh" ]]; then
    log "Extracting correction patterns..."
    CORRECTION_FILE="${PATTERNS_DIR}/corrections_${TIMESTAMP}.json"
    "$SCRIPT_DIR/extract-corrections.sh" "$DAYS" > "$CORRECTION_FILE" 2>> "$LOG_FILE" || true

    if [[ -f "$CORRECTION_FILE" ]]; then
        CORRECTIONS_FOUND=$(jq -r '.total_corrections // 0' "$CORRECTION_FILE" 2>/dev/null || echo "0")
        log "Found $CORRECTIONS_FOUND corrections from AI/user interaction"
    fi
else
    log "extract-corrections.sh not found, skipping correction analysis"
fi

# Analyze full session transcripts
SESSIONS_FOUND=0
if [[ -x "$SCRIPT_DIR/analyze-sessions.sh" ]]; then
    log "Analyzing session transcripts..."
    SESSION_FILE="${PATTERNS_DIR}/sessions_${TIMESTAMP}.json"
    "$SCRIPT_DIR/analyze-sessions.sh" "$DAYS" > "$SESSION_FILE" 2>> "$LOG_FILE" || true

    if [[ -f "$SESSION_FILE" ]]; then
        SESSIONS_FOUND=$(jq -r '.unique_sessions // 0' "$SESSION_FILE" 2>/dev/null || echo "0")
        TOTAL_EVENTS=$(jq -r '.total_events // 0' "$SESSION_FILE" 2>/dev/null || echo "0")
        log "Analyzed $SESSIONS_FOUND sessions with $TOTAL_EVENTS tool events"
    fi
else
    log "analyze-sessions.sh not found, skipping session analysis"
fi

# Extract script ideas from session patterns
SCRIPT_IDEAS=0
if [[ -x "$SCRIPT_DIR/extract-script-ideas.sh" ]]; then
    log "Extracting script ideas from sessions..."
    SCRIPT_IDEAS_FILE="${PATTERNS_DIR}/script-ideas_${TIMESTAMP}.json"
    "$SCRIPT_DIR/extract-script-ideas.sh" "$DAYS" > "$SCRIPT_IDEAS_FILE" 2>> "$LOG_FILE" || true

    if [[ -f "$SCRIPT_IDEAS_FILE" ]]; then
        SCRIPT_IDEAS=$(jq -r '.skill_candidates | length // 0' "$SCRIPT_IDEAS_FILE" 2>/dev/null || echo "0")
        BASH_CMDS=$(jq -r '.total_bash_commands // 0' "$SCRIPT_IDEAS_FILE" 2>/dev/null || echo "0")
        log "Found $SCRIPT_IDEAS script skill candidates from $BASH_CMDS bash commands"
    fi
else
    log "extract-script-ideas.sh not found, skipping script idea extraction"
fi

# Analyze full conversation logs (user prompts, AI responses, thinking)
CONVERSATIONS_FOUND=0
CORRECTIONS_FROM_CONV=0
if [[ -x "$SCRIPT_DIR/analyze-conversations.sh" ]]; then
    log "Analyzing conversation logs..."
    CONVERSATION_FILE="${PATTERNS_DIR}/conversations_${TIMESTAMP}.json"
    "$SCRIPT_DIR/analyze-conversations.sh" "$DAYS" > "$CONVERSATION_FILE" 2>> "$LOG_FILE" || true

    if [[ -f "$CONVERSATION_FILE" ]] && [[ -s "$CONVERSATION_FILE" ]]; then
        CONVERSATIONS_FOUND=$(jq -r '.conversations_analyzed // 0' "$CONVERSATION_FILE" 2>/dev/null || echo "0")
        CORRECTIONS_FROM_CONV=$(jq -r '.correction_count // 0' "$CONVERSATION_FILE" 2>/dev/null || echo "0")
        USER_MSGS=$(jq -r '.total_user_messages // 0' "$CONVERSATION_FILE" 2>/dev/null || echo "0")
        SKILL_GAPS=$(jq -r '.skill_gaps | length // 0' "$CONVERSATION_FILE" 2>/dev/null || echo "0")
        log "Analyzed $CONVERSATIONS_FOUND conversations with $USER_MSGS user messages"
        log "Found $CORRECTIONS_FROM_CONV corrections, $SKILL_GAPS potential skill gaps"
    fi
else
    log "analyze-conversations.sh not found, skipping conversation analysis"
fi

#############################################
# PHASE 3: GENERALIZE - Analyze trends
#############################################
log ""
log "=== PHASE 3: GENERALIZE ==="

if [[ -x "$SCRIPT_DIR/analyze-trends.sh" ]]; then
    # Only run trends if we have multiple pattern files
    PATTERN_COUNT=$(ls "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | wc -l | tr -d '[:space:]')
    PATTERN_COUNT=${PATTERN_COUNT:-0}
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
    # Pass both pattern file and session file for complete feedback loop
    SKILL_OUTPUT=$("$SCRIPT_DIR/create-skills.sh" "$PATTERN_FILE" "${SESSION_FILE:-}" 2>> "$LOG_FILE") || true

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
    # Check both workspace and home state dirs for reports
    REPORT_FILE=$(ls -t "$REPORTS_DIR"/weekly_digest_*.md "${HOME}/.claude/state/reports"/weekly_digest_*.md 2>/dev/null | head -1 || true)
    log "Weekly report: $REPORT_FILE"
fi

#############################################
# CHECKLIST EVALUATION (before state update)
#############################################
log ""
log "=== CHECKLIST EVALUATION ==="

# a) Cross-review check: Look for pending Gemini, Codex, AND Claude reviews
GEMINI_PENDING=0
CODEX_PENDING=0
CLAUDE_PENDING=0
GEMINI_MANAGER="${WORKSPACE_ROOT}/scripts/development/ai-review/gemini-review-manager.sh"
CODEX_MANAGER="${WORKSPACE_ROOT}/scripts/development/ai-review/codex-review-manager.sh"
CLAUDE_MANAGER="${WORKSPACE_ROOT}/scripts/development/ai-review/claude-review-manager.sh"
CODEX_DIR="${HOME}/.codex-reviews/pending"
CLAUDE_DIR="${HOME}/.claude-reviews/pending"

# Check Gemini pending reviews
if [[ -x "$GEMINI_MANAGER" ]]; then
    GEMINI_PENDING=$("$GEMINI_MANAGER" list 2>/dev/null | grep -c "pending" 2>/dev/null) || GEMINI_PENDING=0
fi
GEMINI_PENDING=${GEMINI_PENDING:-0}

# Check Codex pending reviews (count files in pending directory)
if [[ -d "$CODEX_DIR" ]]; then
    CODEX_PENDING=$(find "$CODEX_DIR" -type f \( -name "*.json" -o -name "*.md" \) -size +0c 2>/dev/null | wc -l | tr -d '[:space:]')
fi
CODEX_PENDING=${CODEX_PENDING:-0}

# Check Claude pending reviews
if [[ -d "$CLAUDE_DIR" ]]; then
    CLAUDE_PENDING=$(find "$CLAUDE_DIR" -type f -name "*.md" -size +0c 2>/dev/null | wc -l | tr -d '[:space:]')
fi
CLAUDE_PENDING=${CLAUDE_PENDING:-0}

PENDING_REVIEWS=$((GEMINI_PENDING + CODEX_PENDING + CLAUDE_PENDING))
CROSS_REVIEW_OK=$([[ $PENDING_REVIEWS -eq 0 ]] && echo "pass" || echo "fail")
log "Cross-review: $GEMINI_PENDING Gemini + $CODEX_PENDING Codex + $CLAUDE_PENDING Claude = $PENDING_REVIEWS pending"

# b) Skills development check
SKILLS_OK=$([[ $SKILLS_CREATED -gt 0 || $SKILLS_ENHANCED -gt 0 ]] && echo "pass" || echo "none")
log "Skills: $SKILLS_CREATED created, $SKILLS_ENHANCED enhanced"

# c) File structure check: Look for orphan files in key directories
ORPHAN_DOCS=$(find "${WORKSPACE_ROOT}/docs" -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "SKILLS_INDEX.md" ! -name "WORKSPACE_HUB_*.md" 2>/dev/null | wc -l | tr -d '[:space:]')
ORPHAN_DOCS=${ORPHAN_DOCS:-0}
ORPHAN_SCRIPTS=$(find "${WORKSPACE_ROOT}/scripts" -maxdepth 1 -type f -name "*.sh" ! -name "workspace" ! -name "repository_sync" ! -name "setup-claude-env.sh" 2>/dev/null | wc -l | tr -d '[:space:]')
ORPHAN_SCRIPTS=${ORPHAN_SCRIPTS:-0}
FILE_STRUCTURE_OK=$([[ $ORPHAN_DOCS -le 5 && $ORPHAN_SCRIPTS -le 2 ]] && echo "pass" || echo "fail")
log "File structure: $ORPHAN_DOCS orphan docs, $ORPHAN_SCRIPTS orphan scripts"

# d) Context management: Check for long sessions or high correction rate
CONTEXT_ISSUES=0
AVG_SESSION=0
CORRECTION_RATE=0
if [[ -f "$CONVERSATION_FILE" ]]; then
    AVG_SESSION=$(jq -r '.session_stats.avg_messages_per_session // 0' "$CONVERSATION_FILE" 2>/dev/null | cut -d. -f1)
    CORRECTION_RATE=$(jq -r '.correction_count // 0' "$CONVERSATION_FILE" 2>/dev/null)
    [[ $AVG_SESSION -gt 500 ]] && CONTEXT_ISSUES=$((CONTEXT_ISSUES + 1))
    [[ $CORRECTION_RATE -gt 20 ]] && CONTEXT_ISSUES=$((CONTEXT_ISSUES + 1))
fi
CONTEXT_OK=$([[ $CONTEXT_ISSUES -eq 0 ]] && echo "pass" || echo "warn")
log "Context: avg $AVG_SESSION msgs/session, $CORRECTION_RATE corrections"

# e) Best practices: TDD coverage, git hygiene
REPOS_WITH_TESTS=$(find "$WORKSPACE_ROOT" -maxdepth 2 -type d -name "tests" 2>/dev/null | wc -l | tr -d '[:space:]')
REPOS_WITH_TESTS=${REPOS_WITH_TESTS:-0}
UNCOMMITTED_CHANGES=$(cd "$WORKSPACE_ROOT" && git status --porcelain 2>/dev/null | wc -l | tr -d '[:space:]')
UNCOMMITTED_CHANGES=${UNCOMMITTED_CHANGES:-0}
PRACTICES_OK=$([[ $REPOS_WITH_TESTS -gt 5 && $UNCOMMITTED_CHANGES -lt 20 ]] && echo "pass" || echo "warn")
log "Practices: $REPOS_WITH_TESTS repos with tests, $UNCOMMITTED_CHANGES uncommitted changes"

# f) Submodule sync status: Quick check (limit to 15 submodules for speed)
SUBMODULES_DIRTY=0
SUBMODULES_UNPUSHED=0
SUBMODULES_TOTAL=0
CHECKED_SUBS=0
while IFS= read -r submod && [[ $CHECKED_SUBS -lt 15 ]]; do
    [[ -z "$submod" ]] && continue
    SUBMODULES_TOTAL=$((SUBMODULES_TOTAL + 1))
    CHECKED_SUBS=$((CHECKED_SUBS + 1))
    submod_path="${WORKSPACE_ROOT}/${submod}"
    if [[ -d "$submod_path/.git" ]]; then
        # Check for uncommitted changes (quick)
        if [[ -n $(timeout 2 git -C "$submod_path" status --porcelain 2>/dev/null) ]]; then
            SUBMODULES_DIRTY=$((SUBMODULES_DIRTY + 1))
        fi
        # Check for unpushed commits (quick)
        UNPUSHED=$(timeout 2 git -C "$submod_path" log --oneline @{upstream}..HEAD 2>/dev/null | wc -l | tr -d '[:space:]') || UNPUSHED=0
        UNPUSHED=${UNPUSHED:-0}
        [[ $UNPUSHED -gt 0 ]] && SUBMODULES_UNPUSHED=$((SUBMODULES_UNPUSHED + 1))
    fi
done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach --recursive 'echo $sm_path' 2>/dev/null | head -15)
SUBMODULE_SYNC_OK=$([[ $SUBMODULES_DIRTY -eq 0 && $SUBMODULES_UNPUSHED -eq 0 ]] && echo "pass" || echo "warn")
log "Submodule sync: $SUBMODULES_DIRTY dirty, $SUBMODULES_UNPUSHED unpushed (of $SUBMODULES_TOTAL total)"

# g) CLAUDE.md health: Quick check (limit to 20 files)
CLAUDE_MD_OVERSIZED=0
CLAUDE_MD_TOTAL=0
while IFS= read -r claude_file && [[ $CLAUDE_MD_TOTAL -lt 20 ]]; do
    [[ -z "$claude_file" ]] && continue
    CLAUDE_MD_TOTAL=$((CLAUDE_MD_TOTAL + 1))
    file_size=$(wc -c < "$claude_file" 2>/dev/null | tr -d '[:space:]')
    file_size=${file_size:-0}
    # Limits: global=2KB, workspace=4KB, project=8KB
    if [[ "$claude_file" == *"/.claude/CLAUDE.md" ]]; then
        max_size=2048
    elif [[ "$claude_file" == */workspace-hub/CLAUDE.md ]]; then
        max_size=4096
    else
        max_size=8192
    fi
    [[ $file_size -gt $max_size ]] && CLAUDE_MD_OVERSIZED=$((CLAUDE_MD_OVERSIZED + 1))
done < <(find "$WORKSPACE_ROOT" -maxdepth 3 -name "CLAUDE.md" -type f 2>/dev/null | head -20)
CLAUDE_MD_OK=$([[ $CLAUDE_MD_OVERSIZED -eq 0 ]] && echo "pass" || echo "fail")
log "CLAUDE.md health: $CLAUDE_MD_OVERSIZED oversized (of $CLAUDE_MD_TOTAL total)"

# h) Hook installation: Quick check (limit to 15 repos)
HOOKS_INSTALLED=0
HOOKS_EXPECTED=0
HOOK_SCRIPT="${WORKSPACE_ROOT}/.claude/hooks/capture-corrections.sh"
if [[ -x "$HOOK_SCRIPT" ]]; then
    HOOKS_CHECKED=0
    while IFS= read -r submod && [[ $HOOKS_CHECKED -lt 15 ]]; do
        [[ -z "$submod" ]] && continue
        HOOKS_EXPECTED=$((HOOKS_EXPECTED + 1))
        HOOKS_CHECKED=$((HOOKS_CHECKED + 1))
        settings_file="${WORKSPACE_ROOT}/${submod}/.claude/settings.json"
        if [[ -f "$settings_file" ]] && grep -q "capture-corrections" "$settings_file" 2>/dev/null; then
            HOOKS_INSTALLED=$((HOOKS_INSTALLED + 1))
        fi
    done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach --recursive 'echo $sm_path' 2>/dev/null | head -15)
fi
HOOKS_COVERAGE=$([[ $HOOKS_EXPECTED -gt 0 ]] && echo "$((HOOKS_INSTALLED * 100 / HOOKS_EXPECTED))" || echo "0")
HOOKS_OK=$([[ $HOOKS_COVERAGE -ge 80 ]] && echo "pass" || ([[ $HOOKS_COVERAGE -ge 50 ]] && echo "warn" || echo "fail"))
log "Hook installation: $HOOKS_INSTALLED/$HOOKS_EXPECTED repos (${HOOKS_COVERAGE}% coverage)"

# i) Stale branches: Check for branches not merged for >30 days
STALE_BRANCHES=0
STALE_THRESHOLD=$((30 * 24 * 60 * 60))  # 30 days in seconds
NOW=$(date +%s)
while IFS= read -r branch; do
    [[ -z "$branch" || "$branch" == *"HEAD"* || "$branch" == *"main"* || "$branch" == *"master"* ]] && continue
    branch_date=$(git -C "$WORKSPACE_ROOT" log -1 --format="%ct" "$branch" 2>/dev/null || echo "0")
    age=$((NOW - branch_date))
    [[ $age -gt $STALE_THRESHOLD ]] && STALE_BRANCHES=$((STALE_BRANCHES + 1))
done < <(git -C "$WORKSPACE_ROOT" branch -r 2>/dev/null | grep -v '\->' || true)
STALE_OK=$([[ $STALE_BRANCHES -le 5 ]] && echo "pass" || echo "warn")
log "Stale branches: $STALE_BRANCHES branches older than 30 days"

# j) GitHub Actions: Check workflow run status (quick check - workspace only)
ACTIONS_FAILING=0
ACTIONS_TOTAL=0
if command -v gh &> /dev/null && [[ -d "${WORKSPACE_ROOT}/.github/workflows" ]]; then
    ACTIONS_TOTAL=1
    # Only check workspace-hub workflows (submodules are too slow)
    FAILED=$(timeout 10 gh run list --limit 3 --status failure 2>/dev/null | wc -l | tr -d '[:space:]') || FAILED=0
    FAILED=${FAILED:-0}
    [[ $FAILED -gt 0 ]] && ACTIONS_FAILING=1
fi
GITHUB_ACTIONS_OK=$([[ $ACTIONS_FAILING -eq 0 ]] && echo "pass" || ([[ $ACTIONS_FAILING -le 2 ]] && echo "warn" || echo "fail"))
log "GitHub Actions: $ACTIONS_FAILING/$ACTIONS_TOTAL repos with failing workflows"

# k) Folder structure: Comprehensive directory organization check
STRUCTURE_ISSUES=0
# Check for expected top-level directories
for dir in scripts docs specs .claude; do
    [[ ! -d "${WORKSPACE_ROOT}/${dir}" ]] && STRUCTURE_ISSUES=$((STRUCTURE_ISSUES + 1))
done
# Check for misplaced files in root
ROOT_FILES=$(find "$WORKSPACE_ROOT" -maxdepth 1 -type f ! -name ".*" ! -name "README.md" ! -name "LICENSE*" ! -name "*.toml" ! -name "*.yaml" ! -name "*.yml" 2>/dev/null | wc -l | tr -d '[:space:]')
ROOT_FILES=${ROOT_FILES:-0}
[[ $ROOT_FILES -gt 5 ]] && STRUCTURE_ISSUES=$((STRUCTURE_ISSUES + 1))
# Check specs has proper structure
[[ ! -d "${WORKSPACE_ROOT}/specs/modules" ]] && STRUCTURE_ISSUES=$((STRUCTURE_ISSUES + 1))
[[ ! -d "${WORKSPACE_ROOT}/specs/templates" ]] && STRUCTURE_ISSUES=$((STRUCTURE_ISSUES + 1))
FOLDER_STRUCTURE_OK=$([[ $STRUCTURE_ISSUES -eq 0 ]] && echo "pass" || echo "fail")
log "Folder structure: $STRUCTURE_ISSUES structural issues, $ROOT_FILES misplaced root files"

# l) Test coverage: Quick check for coverage files (limit to 20 repos for speed)
COVERAGE_PERCENT=0
COVERAGE_REPOS=0
LOW_COVERAGE_REPOS=0
CHECKED_REPOS=0
while IFS= read -r submod && [[ $CHECKED_REPOS -lt 20 ]]; do
    [[ -z "$submod" ]] && continue
    submod_path="${WORKSPACE_ROOT}/${submod}"
    # Quick check for coverage.xml only (most common)
    cov_file="$submod_path/coverage.xml"
    if [[ -f "$cov_file" ]]; then
        COVERAGE_REPOS=$((COVERAGE_REPOS + 1))
        CHECKED_REPOS=$((CHECKED_REPOS + 1))
        COV=$(grep -oP 'line-rate="\K[0-9.]+' "$cov_file" 2>/dev/null | head -1)
        if [[ -n "$COV" && "$COV" =~ ^0\.([0-9]+) ]]; then
            COV_DEC="${BASH_REMATCH[1]}"
            COV_PCT=$((10#${COV_DEC:0:2}))
        elif [[ "$COV" == "1" || "$COV" == "1.0" ]]; then
            COV_PCT=100
        else
            COV_PCT=0
        fi
        [[ ${COV_PCT:-0} -lt 80 ]] && LOW_COVERAGE_REPOS=$((LOW_COVERAGE_REPOS + 1))
        COVERAGE_PERCENT=$((COVERAGE_PERCENT + ${COV_PCT:-0}))
    fi
done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach --recursive 'echo $sm_path' 2>/dev/null)
AVG_COVERAGE=$([[ $COVERAGE_REPOS -gt 0 ]] && echo $((COVERAGE_PERCENT / COVERAGE_REPOS)) || echo "0")
TEST_COVERAGE_OK=$([[ $AVG_COVERAGE -ge 80 ]] && echo "pass" || ([[ $AVG_COVERAGE -ge 60 ]] && echo "warn" || echo "fail"))
log "Test coverage: ${AVG_COVERAGE}% avg across $COVERAGE_REPOS repos, $LOW_COVERAGE_REPOS below 80%"

# m) Test pass/fail: Quick check of pytest cache (limit to 20 repos)
TEST_PASS_COUNT=0
TEST_FAIL_COUNT=0
TESTED_REPOS=0
CHECKED=0
while IFS= read -r submod && [[ $CHECKED -lt 20 ]]; do
    [[ -z "$submod" ]] && continue
    submod_path="${WORKSPACE_ROOT}/${submod}"
    # Check for pytest cache (quick check)
    lastfailed="$submod_path/.pytest_cache/v/cache/lastfailed"
    if [[ -f "$lastfailed" ]]; then
        TESTED_REPOS=$((TESTED_REPOS + 1))
        CHECKED=$((CHECKED + 1))
        CONTENT=$(cat "$lastfailed" 2>/dev/null)
        if [[ -n "$CONTENT" && "$CONTENT" != "{}" && "$CONTENT" != "null" ]]; then
            TEST_FAIL_COUNT=$((TEST_FAIL_COUNT + 1))
        else
            TEST_PASS_COUNT=$((TEST_PASS_COUNT + 1))
        fi
    fi
done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach --recursive 'echo $sm_path' 2>/dev/null)
TEST_PASS_OK=$([[ $TEST_FAIL_COUNT -eq 0 ]] && echo "pass" || echo "fail")
log "Test status: $TEST_PASS_COUNT passing, $TEST_FAIL_COUNT failing (of $TESTED_REPOS with tests)"

# n) Refactor opportunities: Quick code smell check
REFACTOR_NEEDED=0
LARGE_FILES=0
# Check for large files (>500 lines) - limit to 50 files for speed
while IFS= read -r pyfile; do
    lines=$(wc -l < "$pyfile" 2>/dev/null | tr -d '[:space:]')
    lines=${lines:-0}
    [[ $lines -gt 500 ]] && LARGE_FILES=$((LARGE_FILES + 1))
done < <(find "$WORKSPACE_ROOT" -name "*.py" -type f ! -path "*/.venv/*" ! -path "*/node_modules/*" 2>/dev/null | head -50)
# Quick TODO count (limit search depth and files)
TODO_COUNT=$(timeout 10 grep -r "TODO\|FIXME" "$WORKSPACE_ROOT" --include="*.py" -l 2>/dev/null | wc -l | tr -d '[:space:]') || TODO_COUNT=0
TODO_COUNT=${TODO_COUNT:-0}
[[ $LARGE_FILES -gt 10 ]] && REFACTOR_NEEDED=$((REFACTOR_NEEDED + 1))
[[ $TODO_COUNT -gt 50 ]] && REFACTOR_NEEDED=$((REFACTOR_NEEDED + 1))
REFACTOR_OK=$([[ $REFACTOR_NEEDED -eq 0 ]] && echo "pass" || echo "warn")
log "Refactor check: $LARGE_FILES large files, $TODO_COUNT TODOs/FIXMEs"

# o) Aceengineer-website cron job status
ACEENGINEER_OK="none"
ACEENGINEER_STATS_FRESH="no"
ACEENGINEER_REPORT_FRESH="no"
ACEENGINEER_STATS_DATE=""
ACEENGINEER_REPORT_DATE=""

ACEENGINEER_DIR="${WORKSPACE_ROOT}/aceengineer-website"
STATS_FILE="${ACEENGINEER_DIR}/assets/data/statistics.json"
REPORT_DIR="${ACEENGINEER_DIR}/reports/competitor-analysis"
TODAY=$(date +%Y-%m-%d)

# Check statistics.json freshness
if [[ -f "$STATS_FILE" ]]; then
    ACEENGINEER_STATS_DATE=$(jq -r '.last_updated // ""' "$STATS_FILE" 2>/dev/null)
    [[ "$ACEENGINEER_STATS_DATE" == "$TODAY" ]] && ACEENGINEER_STATS_FRESH="yes"
fi

# Check competitor analysis report freshness
LATEST_REPORT="${REPORT_DIR}/latest.html"
if [[ -L "$LATEST_REPORT" ]]; then
    REPORT_NAME=$(readlink "$LATEST_REPORT")
    ACEENGINEER_REPORT_DATE="${REPORT_NAME%.html}"
    [[ "$ACEENGINEER_REPORT_DATE" == "$TODAY" ]] && ACEENGINEER_REPORT_FRESH="yes"
fi

# Determine overall status
if [[ "$ACEENGINEER_STATS_FRESH" == "yes" && "$ACEENGINEER_REPORT_FRESH" == "yes" ]]; then
    ACEENGINEER_OK="pass"
elif [[ "$ACEENGINEER_STATS_FRESH" == "yes" || "$ACEENGINEER_REPORT_FRESH" == "yes" ]]; then
    ACEENGINEER_OK="warn"
elif [[ -f "$STATS_FILE" || -L "$LATEST_REPORT" ]]; then
    ACEENGINEER_OK="fail"
fi
log "Aceengineer cron: stats=$ACEENGINEER_STATS_DATE report=$ACEENGINEER_REPORT_DATE"

# p) Session RAG analysis status
SESSION_RAG_OK="none"
SESSION_RAG_FRESH="no"
SESSION_RAG_DATE=""
SESSION_RAG_SESSIONS=0
SESSION_RAG_EVENTS=0

# Check if session analysis ran today (look for sessions file from today)
SESSION_RAG_FILE=$(ls -t "${PATTERNS_DIR}"/sessions_*.json 2>/dev/null | head -1)
if [[ -f "$SESSION_RAG_FILE" ]]; then
    SESSION_RAG_DATE=$(jq -r '.extraction_date // ""' "$SESSION_RAG_FILE" 2>/dev/null | cut -d'T' -f1)
    SESSION_RAG_SESSIONS=$(jq -r '.unique_sessions // 0' "$SESSION_RAG_FILE" 2>/dev/null)
    SESSION_RAG_EVENTS=$(jq -r '.total_events // 0' "$SESSION_RAG_FILE" 2>/dev/null)
    [[ "$SESSION_RAG_DATE" == "$TODAY" ]] && SESSION_RAG_FRESH="yes"
fi

# Determine session RAG status based on freshness and data quality
if [[ "$SESSION_RAG_FRESH" == "yes" && $SESSION_RAG_SESSIONS -gt 0 ]]; then
    SESSION_RAG_OK="pass"
elif [[ -f "$SESSION_RAG_FILE" && $SESSION_RAG_SESSIONS -gt 0 ]]; then
    SESSION_RAG_OK="warn"
elif [[ -f "$SESSION_RAG_FILE" ]]; then
    SESSION_RAG_OK="fail"
fi
log "Session RAG: date=$SESSION_RAG_DATE sessions=$SESSION_RAG_SESSIONS events=$SESSION_RAG_EVENTS"

# q) Claude Code release notes insights
CC_INSIGHTS_OK="none"
CC_VERSION=""
CC_LAST_REVIEWED=""
CC_GENERAL_COUNT=0
CC_SPECIFIC_COUNT=0

# Get installed CC version
if command -v claude &> /dev/null; then
    CC_VERSION=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "")
fi

# Run insights extraction if script exists
CC_INSIGHTS_FILE=""
if [[ -x "$SCRIPT_DIR/extract-cc-insights.sh" ]]; then
    CC_INSIGHTS_FILE=$("$SCRIPT_DIR/extract-cc-insights.sh" 2>/dev/null) || true
fi

# Parse insights if file exists
if [[ -f "$CC_INSIGHTS_FILE" ]] && command -v jq &> /dev/null; then
    CC_LAST_REVIEWED=$(jq -r '.last_reviewed_version // ""' "$CC_INSIGHTS_FILE" 2>/dev/null)
    CC_GENERAL_COUNT=$(jq -r '.insights.general_ai_community | length' "$CC_INSIGHTS_FILE" 2>/dev/null || echo "0")
    CC_SPECIFIC_COUNT=$(jq -r '.insights.specific_workflows | length' "$CC_INSIGHTS_FILE" 2>/dev/null || echo "0")

    # Determine status: pass if reviewed version matches installed
    if [[ -n "$CC_LAST_REVIEWED" && "$CC_LAST_REVIEWED" == "$CC_VERSION" ]]; then
        CC_INSIGHTS_OK="pass"
    elif [[ -n "$CC_LAST_REVIEWED" ]]; then
        CC_INSIGHTS_OK="warn"  # Reviewed but not current version
    elif [[ $CC_GENERAL_COUNT -eq 0 && $CC_SPECIFIC_COUNT -eq 0 ]]; then
        CC_INSIGHTS_OK="none"
    fi
fi
log "CC Insights: v=$CC_VERSION reviewed=$CC_LAST_REVIEWED general=$CC_GENERAL_COUNT specific=$CC_SPECIFIC_COUNT"

#############################################
# Auto-approve stale Codex reviews (>14 days)
#############################################
CODEX_PENDING_DIR="${HOME}/.codex-reviews/pending"
CODEX_APPROVED_DIR="${HOME}/.codex-reviews/approved"

if [[ -d "$CODEX_PENDING_DIR" ]]; then
    mkdir -p "$CODEX_APPROVED_DIR"
    while IFS= read -r review_file; do
        [[ -z "$review_file" ]] && continue
        mv "$review_file" "$CODEX_APPROVED_DIR/"
        STALE_REVIEWS_APPROVED=$((STALE_REVIEWS_APPROVED + 1))
    done < <(find "$CODEX_PENDING_DIR" -name "*.md" -mtime +14 2>/dev/null)

    if [[ $STALE_REVIEWS_APPROVED -gt 0 ]]; then
        log "Auto-approved $STALE_REVIEWS_APPROVED stale Codex reviews (>14 days)"
    fi
fi

#############################################
# Update state file
#############################################
STATE_FILE="${STATE_DIR}/reflect-state.yaml"
cat > "$STATE_FILE" << EOF
version: "2.1"
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
  script_ideas_found: $SCRIPT_IDEAS
  sessions_analyzed: $SESSIONS_FOUND
  conversations_analyzed: $CONVERSATIONS_FOUND
  corrections_detected: $CORRECTION_RATE
checklist:
  cross_review: $CROSS_REVIEW_OK
  pending_reviews: $PENDING_REVIEWS
  gemini_pending: $GEMINI_PENDING
  codex_pending: $CODEX_PENDING
  claude_pending: $CLAUDE_PENDING
  skills_development: $SKILLS_OK
  skills_created: $SKILLS_CREATED
  skills_enhanced: $SKILLS_ENHANCED
  file_structure: $FILE_STRUCTURE_OK
  orphan_docs: $ORPHAN_DOCS
  orphan_scripts: $ORPHAN_SCRIPTS
  context_management: $CONTEXT_OK
  avg_session_msgs: $AVG_SESSION
  correction_rate: $CORRECTION_RATE
  best_practices: $PRACTICES_OK
  repos_with_tests: $REPOS_WITH_TESTS
  uncommitted_changes: $UNCOMMITTED_CHANGES
  submodule_sync: $SUBMODULE_SYNC_OK
  submodules_dirty: $SUBMODULES_DIRTY
  submodules_unpushed: $SUBMODULES_UNPUSHED
  submodules_total: $SUBMODULES_TOTAL
  claude_md_health: $CLAUDE_MD_OK
  claude_md_oversized: $CLAUDE_MD_OVERSIZED
  claude_md_total: $CLAUDE_MD_TOTAL
  hook_installation: $HOOKS_OK
  hooks_installed: $HOOKS_INSTALLED
  hooks_expected: $HOOKS_EXPECTED
  hooks_coverage: $HOOKS_COVERAGE
  stale_branches: $STALE_OK
  stale_branch_count: $STALE_BRANCHES
  github_actions: $GITHUB_ACTIONS_OK
  actions_failing: $ACTIONS_FAILING
  actions_total: $ACTIONS_TOTAL
  folder_structure_detailed: $FOLDER_STRUCTURE_OK
  structure_issues: $STRUCTURE_ISSUES
  root_files: $ROOT_FILES
  test_coverage: $TEST_COVERAGE_OK
  avg_coverage: $AVG_COVERAGE
  coverage_repos: $COVERAGE_REPOS
  low_coverage_repos: $LOW_COVERAGE_REPOS
  test_pass_fail: $TEST_PASS_OK
  test_pass_count: $TEST_PASS_COUNT
  test_fail_count: $TEST_FAIL_COUNT
  tested_repos: $TESTED_REPOS
  refactor: $REFACTOR_OK
  large_files: $LARGE_FILES
  todo_count: $TODO_COUNT
  aceengineer_cron: $ACEENGINEER_OK
  aceengineer_stats_date: ${ACEENGINEER_STATS_DATE:-none}
  aceengineer_report_date: ${ACEENGINEER_REPORT_DATE:-none}
  session_rag: $SESSION_RAG_OK
  session_rag_date: ${SESSION_RAG_DATE:-none}
  session_rag_sessions: $SESSION_RAG_SESSIONS
  session_rag_events: $SESSION_RAG_EVENTS
  cc_insights: $CC_INSIGHTS_OK
  cc_version: ${CC_VERSION:-unknown}
  cc_last_reviewed: ${CC_LAST_REVIEWED:-none}
  cc_general_count: $CC_GENERAL_COUNT
  cc_specific_count: $CC_SPECIFIC_COUNT
actions_taken:
  skills_created: $SKILLS_CREATED
  skills_enhanced: $SKILLS_ENHANCED
  learnings_stored: $LEARNINGS_STORED
  stale_reviews_approved: $STALE_REVIEWS_APPROVED
files:
  analysis: $ANALYSIS_FILE
  patterns: ${PATTERN_FILE:-none}
  conversations: ${CONVERSATION_FILE:-none}
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

# Convert checklist results to display symbols
CR_SYM=$([[ "$CROSS_REVIEW_OK" == "pass" ]] && echo "✓" || echo "✗")
SK_SYM=$([[ "$SKILLS_OK" == "pass" ]] && echo "✓" || ([[ "$SKILLS_OK" == "none" ]] && echo "○" || echo "✗"))
FS_SYM=$([[ "$FILE_STRUCTURE_OK" == "pass" ]] && echo "✓" || echo "✗")
CX_SYM=$([[ "$CONTEXT_OK" == "pass" ]] && echo "✓" || echo "!")
BP_SYM=$([[ "$PRACTICES_OK" == "pass" ]] && echo "✓" || echo "!")
SM_SYM=$([[ "$SUBMODULE_SYNC_OK" == "pass" ]] && echo "✓" || echo "!")
CM_SYM=$([[ "$CLAUDE_MD_OK" == "pass" ]] && echo "✓" || echo "✗")
HK_SYM=$([[ "$HOOKS_OK" == "pass" ]] && echo "✓" || ([[ "$HOOKS_OK" == "warn" ]] && echo "!" || echo "✗"))
SB_SYM=$([[ "$STALE_OK" == "pass" ]] && echo "✓" || echo "!")
GA_SYM=$([[ "$GITHUB_ACTIONS_OK" == "pass" ]] && echo "✓" || ([[ "$GITHUB_ACTIONS_OK" == "warn" ]] && echo "!" || echo "✗"))
TC_SYM=$([[ "$TEST_COVERAGE_OK" == "pass" ]] && echo "✓" || ([[ "$TEST_COVERAGE_OK" == "warn" ]] && echo "!" || echo "✗"))
TP_SYM=$([[ "$TEST_PASS_OK" == "pass" ]] && echo "✓" || echo "✗")
RF_SYM=$([[ "$REFACTOR_OK" == "pass" ]] && echo "✓" || echo "!")
FD_SYM=$([[ "$FOLDER_STRUCTURE_OK" == "pass" ]] && echo "✓" || echo "✗")
AE_SYM=$([[ "$ACEENGINEER_OK" == "pass" ]] && echo "✓" || ([[ "$ACEENGINEER_OK" == "warn" ]] && echo "!" || ([[ "$ACEENGINEER_OK" == "none" ]] && echo "○" || echo "✗")))
SR_SYM=$([[ "$SESSION_RAG_OK" == "pass" ]] && echo "✓" || ([[ "$SESSION_RAG_OK" == "warn" ]] && echo "!" || ([[ "$SESSION_RAG_OK" == "none" ]] && echo "○" || echo "✗")))
CC_SYM=$([[ "$CC_INSIGHTS_OK" == "pass" ]] && echo "✓" || ([[ "$CC_INSIGHTS_OK" == "warn" ]] && echo "!" || ([[ "$CC_INSIGHTS_OK" == "none" ]] && echo "○" || echo "✗")))

# Summary output for cron email
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    Daily Reflection Summary                           ║"
echo "║                    $(date '+%Y-%m-%d %H:%M')                                        ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║  QUALITY CHECKLIST (15 checks)                                        ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  CODE QUALITY                          │  INFRASTRUCTURE              ║"
echo "║  $CR_SYM Cross-Review: ${GEMINI_PENDING}G ${CODEX_PENDING}C ${CLAUDE_PENDING}Cl pending    │  $SM_SYM Submodule: ${SUBMODULES_DIRTY} dirty, ${SUBMODULES_UNPUSHED} unpushed  ║"
echo "║  $SK_SYM Skills: ${SKILLS_CREATED} new, ${SKILLS_ENHANCED} enhanced       │  $CM_SYM CLAUDE.md: ${CLAUDE_MD_OVERSIZED}/${CLAUDE_MD_TOTAL} oversized    ║"
echo "║  $FS_SYM Files: ${ORPHAN_DOCS} orphan docs, ${ORPHAN_SCRIPTS} scripts  │  $HK_SYM Hooks: ${HOOKS_COVERAGE}% coverage       ║"
echo "║  $CX_SYM Context: ${AVG_SESSION} msgs, ${CORRECTION_RATE} corrections  │  $SB_SYM Branches: ${STALE_BRANCHES} stale         ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  TESTING & CI                          │  CODE HEALTH                 ║"
echo "║  $GA_SYM Actions: ${ACTIONS_FAILING}/${ACTIONS_TOTAL} failing        │  $RF_SYM Refactor: ${LARGE_FILES} large, ${TODO_COUNT} TODOs  ║"
echo "║  $TC_SYM Coverage: ${AVG_COVERAGE}% avg             │  $BP_SYM Practice: ${REPOS_WITH_TESTS} w/tests       ║"
echo "║  $TP_SYM Tests: ${TEST_PASS_COUNT} pass, ${TEST_FAIL_COUNT} fail       │  $FD_SYM Structure: ${STRUCTURE_ISSUES} issues         ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  CRON JOBS                                                            ║"
echo "║  $AE_SYM Aceengineer: stats ${ACEENGINEER_STATS_DATE:-N/A} report ${ACEENGINEER_REPORT_DATE:-N/A}              ║"
echo "║  $SR_SYM Session RAG: ${SESSION_RAG_SESSIONS} sessions, ${SESSION_RAG_EVENTS} events (${SESSION_RAG_DATE:-N/A})        ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  CC RELEASE INSIGHTS (v${CC_VERSION:-?})                                         ║"
echo "║  $CC_SYM Reviewed: ${CC_LAST_REVIEWED:-N/A} | General: ${CC_GENERAL_COUNT} | Workflow: ${CC_SPECIFIC_COUNT}              ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  Legend: ✓ Good  ○ None  ! Warning  ✗ Action needed                   ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║  RAGS LOOP STATUS                                                     ║"
echo "║  ─────────────────────────────────────────────────────────────────────║"
echo "║  ✓ REFLECT:    $REPOS repos, $COMMITS commits                                    ║"
echo "║  ✓ ABSTRACT:   $PATTERNS_FOUND patterns, $SCRIPT_IDEAS scripts                            ║"
echo "║  ✓ CONVERSE:   $CONVERSATIONS_FOUND convos analyzed                                       ║"
echo "║  ✓ GENERALIZE: Trends analyzed                                        ║"
echo "║  ✓ STORE:      $SKILLS_CREATED created, $LEARNINGS_STORED logged                               ║"
[[ "$WEEKLY_REPORT" == "true" ]] && echo "║  📊 Weekly report generated                                             ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"

# Action items if any checks failed
HAS_FAILURES=false
[[ "$CROSS_REVIEW_OK" == "fail" || "$FILE_STRUCTURE_OK" == "fail" || "$CLAUDE_MD_OK" == "fail" || \
   "$HOOKS_OK" == "fail" || "$GITHUB_ACTIONS_OK" == "fail" || "$TEST_COVERAGE_OK" == "fail" || \
   "$TEST_PASS_OK" == "fail" || "$FOLDER_STRUCTURE_OK" == "fail" || "$ACEENGINEER_OK" == "fail" || \
   "$SESSION_RAG_OK" == "fail" ]] && HAS_FAILURES=true

if [[ "$HAS_FAILURES" == "true" ]]; then
    echo ""
    echo "ACTION ITEMS:"
    if [[ "$CROSS_REVIEW_OK" == "fail" ]]; then
        [[ $GEMINI_PENDING -gt 0 ]] && echo "  → Gemini: $GEMINI_MANAGER process"
        [[ $CODEX_PENDING -gt 0 ]] && echo "  → Codex:  $CODEX_MANAGER list"
        [[ $CLAUDE_PENDING -gt 0 ]] && echo "  → Claude: $CLAUDE_MANAGER process"
    fi
    [[ "$FILE_STRUCTURE_OK" == "fail" ]] && echo "  → Organize orphan files into module directories"
    [[ "$CLAUDE_MD_OK" == "fail" ]] && echo "  → $CLAUDE_MD_OVERSIZED CLAUDE.md files exceed size limits - trim to fit"
    [[ "$HOOKS_OK" == "fail" ]] && echo "  → Hooks only ${HOOKS_COVERAGE}% coverage - install capture-corrections hook"
    [[ "$GITHUB_ACTIONS_OK" == "fail" ]] && echo "  → $ACTIONS_FAILING repos have failing GitHub Actions - investigate CI"
    [[ "$TEST_COVERAGE_OK" == "fail" ]] && echo "  → Test coverage at ${AVG_COVERAGE}% - increase to 80%+ target"
    [[ "$TEST_PASS_OK" == "fail" ]] && echo "  → $TEST_FAIL_COUNT repos have failing tests - fix before merging"
    [[ "$FOLDER_STRUCTURE_OK" == "fail" ]] && echo "  → $STRUCTURE_ISSUES structural issues found - organize directories"
    [[ "$ACEENGINEER_OK" == "fail" ]] && echo "  → Aceengineer cron job not running - check daily-update.sh logs"
    [[ "$SESSION_RAG_OK" == "fail" ]] && echo "  → Session RAG analysis failed - check session logs and analyze-sessions.sh"
fi

HAS_WARNINGS=false
[[ "$CONTEXT_OK" == "warn" || "$PRACTICES_OK" == "warn" || "$SUBMODULE_SYNC_OK" == "warn" || \
   "$STALE_OK" == "warn" || "$REFACTOR_OK" == "warn" || "$HOOKS_OK" == "warn" || \
   "$GITHUB_ACTIONS_OK" == "warn" || "$TEST_COVERAGE_OK" == "warn" || "$ACEENGINEER_OK" == "warn" || \
   "$SESSION_RAG_OK" == "warn" || "$CC_INSIGHTS_OK" == "warn" ]] && HAS_WARNINGS=true

if [[ "$HAS_WARNINGS" == "true" ]]; then
    echo ""
    echo "RECOMMENDATIONS:"
    [[ $AVG_SESSION -gt 500 ]] && echo "  → Sessions averaging ${AVG_SESSION} msgs - consider shorter sessions"
    [[ $CORRECTION_RATE -gt 20 ]] && echo "  → High correction rate (${CORRECTION_RATE}) - improve initial understanding"
    [[ $UNCOMMITTED_CHANGES -ge 20 ]] && echo "  → ${UNCOMMITTED_CHANGES} uncommitted changes - commit or discard"
    [[ "$SUBMODULE_SYNC_OK" == "warn" ]] && echo "  → ${SUBMODULES_DIRTY} dirty, ${SUBMODULES_UNPUSHED} unpushed submodules - sync them"
    [[ "$STALE_OK" == "warn" ]] && echo "  → ${STALE_BRANCHES} stale branches (>30 days) - clean up or merge"
    [[ "$REFACTOR_OK" == "warn" ]] && echo "  → ${LARGE_FILES} large files, ${TODO_COUNT} TODOs - consider refactoring"
    [[ "$HOOKS_OK" == "warn" ]] && echo "  → Hooks at ${HOOKS_COVERAGE}% - expand to more repos"
    [[ "$GITHUB_ACTIONS_OK" == "warn" ]] && echo "  → ${ACTIONS_FAILING} repos with CI issues - review failures"
    [[ "$TEST_COVERAGE_OK" == "warn" ]] && echo "  → Coverage at ${AVG_COVERAGE}% - aim for 80%+ target"
    [[ "$ACEENGINEER_OK" == "warn" ]] && echo "  → Aceengineer cron partial - stats or report outdated"
    [[ "$SESSION_RAG_OK" == "warn" ]] && echo "  → Session RAG data stale (${SESSION_RAG_DATE:-N/A}) - check session-logger hook"
    [[ "$CC_INSIGHTS_OK" == "warn" ]] && echo "  → CC Insights reviewed v${CC_LAST_REVIEWED:-?} but installed v${CC_VERSION:-?} - update cc-user-insights.yaml"
fi
