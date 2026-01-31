#!/usr/bin/env bash
#
# daily-reflect-report.sh - Parse reflect-state.yaml and output ecosystem health table
#
# Usage:
#   ./daily-reflect-report.sh              # Output markdown table
#   ./daily-reflect-report.sh --json       # Output raw YAML as-is
#   ./daily-reflect-report.sh --compact    # Compact single-line summary
#
# Reads from:
#   1. WORKSPACE_ROOT/.claude/state/reflect-state.yaml (preferred)
#   2. ~/.claude/state/reflect-state.yaml (fallback)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# Find reflect-state.yaml
STATE_FILE=""
if [[ -f "${WORKSPACE_ROOT}/.claude/state/reflect-state.yaml" ]]; then
    STATE_FILE="${WORKSPACE_ROOT}/.claude/state/reflect-state.yaml"
elif [[ -f "${HOME}/.claude/state/reflect-state.yaml" ]]; then
    STATE_FILE="${HOME}/.claude/state/reflect-state.yaml"
fi

if [[ -z "$STATE_FILE" ]]; then
    echo "ERROR: reflect-state.yaml not found. Run daily-reflect.sh first." >&2
    exit 1
fi

# Parse YAML values using grep/sed (no yq dependency)
get_val() {
    local key="$1"
    grep -E "^\s+${key}:" "$STATE_FILE" | head -1 | sed "s/.*${key}:\s*//" | tr -d '"' | xargs
}

# Status symbol conversion
sym() {
    case "$1" in
        pass) echo "OK" ;;
        warn) echo "WARN" ;;
        fail) echo "FAIL" ;;
        none) echo "--" ;;
        *) echo "?" ;;
    esac
}

# Parse arguments
MODE="table"
[[ "${1:-}" == "--json" ]] && MODE="json"
[[ "${1:-}" == "--compact" ]] && MODE="compact"

if [[ "$MODE" == "json" ]]; then
    cat "$STATE_FILE"
    exit 0
fi

# Extract all checklist values
LAST_RUN=$(grep "^last_run:" "$STATE_FILE" | head -1 | sed 's/last_run:\s*//' | cut -dT -f1)

CROSS_REVIEW=$(get_val "cross_review")
GEMINI_PENDING=$(get_val "gemini_pending")
CODEX_PENDING=$(get_val "codex_pending")
CLAUDE_PENDING=$(get_val "claude_pending")

SKILLS_DEV=$(get_val "skills_development")
SKILLS_CREATED=$(get_val "skills_created")
SKILLS_ENHANCED=$(get_val "skills_enhanced")

FILE_STRUCT=$(get_val "file_structure")
ORPHAN_DOCS=$(get_val "orphan_docs")
ORPHAN_SCRIPTS=$(get_val "orphan_scripts")

CONTEXT_MGMT=$(get_val "context_management")
AVG_SESSION=$(get_val "avg_session_msgs")
CORRECTION_RATE=$(get_val "correction_rate")

BEST_PRACTICES=$(get_val "best_practices")
REPOS_WITH_TESTS=$(get_val "repos_with_tests")
UNCOMMITTED=$(get_val "uncommitted_changes")

SUBMODULE_SYNC=$(get_val "submodule_sync")
SUBS_DIRTY=$(get_val "submodules_dirty")
SUBS_UNPUSHED=$(get_val "submodules_unpushed")

CLAUDE_MD=$(get_val "claude_md_health")
CMD_OVERSIZED=$(get_val "claude_md_oversized")
CMD_TOTAL=$(get_val "claude_md_total")

HOOKS=$(get_val "hook_installation")
HOOKS_COV=$(get_val "hooks_coverage")

STALE_BR=$(get_val "stale_branches")
STALE_COUNT=$(get_val "stale_branch_count")

GH_ACTIONS=$(get_val "github_actions")
ACTIONS_FAIL=$(get_val "actions_failing")
ACTIONS_TOTAL=$(get_val "actions_total")

FOLDER_STRUCT=$(get_val "folder_structure_detailed")
STRUCT_ISSUES=$(get_val "structure_issues")

TEST_COV=$(get_val "test_coverage")
AVG_COV=$(get_val "avg_coverage")
COV_REPOS=$(get_val "coverage_repos")
LOW_COV=$(get_val "low_coverage_repos")

TEST_PF=$(get_val "test_pass_fail")
TEST_PASS=$(get_val "test_pass_count")
TEST_FAIL=$(get_val "test_fail_count")

REFACTOR=$(get_val "refactor")
LARGE_FILES=$(get_val "large_files")
TODO_COUNT=$(get_val "todo_count")

AE_CRON=$(get_val "aceengineer_cron")
AE_STATS=$(get_val "aceengineer_stats_date")
AE_REPORT=$(get_val "aceengineer_report_date")

SESSION_RAG=$(get_val "session_rag")
SR_SESSIONS=$(get_val "session_rag_sessions")
SR_EVENTS=$(get_val "session_rag_events")
SR_DATE=$(get_val "session_rag_date")

CC_INSIGHTS=$(get_val "cc_insights")
CC_VER=$(get_val "cc_version")
CC_REVIEWED=$(get_val "cc_last_reviewed")

WQ_STATUS=$(get_val "work_queue")
WQ_PENDING=$(get_val "wq_pending")
WQ_WORKING=$(get_val "wq_working")
WQ_BLOCKED=$(get_val "wq_blocked")
WQ_STALE=$(get_val "wq_stale")

SKILL_EVAL=$(get_val "skill_eval")
SE_TOTAL=$(get_val "skill_eval_total")
SE_PASSED=$(get_val "skill_eval_passed")
SE_CRITICAL=$(get_val "skill_eval_critical")
SE_WARN=$(get_val "skill_eval_warnings")

CAP_MAP=$(get_val "capability_map")
CAP_REPOS=$(get_val "capability_repos")
CAP_DOMAINS=$(get_val "capability_domains")
CAP_GAPS=$(get_val "capability_gaps")
CAP_DATE=$(get_val "capability_date")

KB_HEALTH=$(get_val "knowledge_base")
KB_TOTAL=$(get_val "kb_total")
KB_ACTIVE=$(get_val "kb_active")
KB_STALE=$(get_val "kb_stale")
KB_CONF=$(get_val "kb_avg_confidence")

# RAGS metrics
REPOS_ANALYZED=$(get_val "repos_analyzed")
COMMITS_FOUND=$(get_val "commits_found")
PATTERNS=$(get_val "patterns_extracted")
SESSIONS=$(get_val "sessions_analyzed")
CONVERSATIONS=$(get_val "conversations_analyzed")
LEARNINGS=$(grep -A5 "^actions_taken:" "$STATE_FILE" | head -6 | grep "learnings_stored:" | sed 's/.*learnings_stored:\s*//' | head -1)
KNOWLEDGE_CAP=$(grep -A5 "^actions_taken:" "$STATE_FILE" | head -6 | grep "knowledge_captured:" | sed 's/.*knowledge_captured:\s*//' | head -1)

if [[ "$MODE" == "compact" ]]; then
    # Count statuses
    PASS=0 WARN=0 FAIL=0 NONE=0
    for s in "$CROSS_REVIEW" "$SKILLS_DEV" "$FILE_STRUCT" "$CONTEXT_MGMT" "$BEST_PRACTICES" \
             "$SUBMODULE_SYNC" "$CLAUDE_MD" "$HOOKS" "$STALE_BR" "$GH_ACTIONS" "$FOLDER_STRUCT" \
             "$TEST_COV" "$TEST_PF" "$REFACTOR" "$AE_CRON" "$SESSION_RAG" "$CC_INSIGHTS" \
             "$WQ_STATUS" "$SKILL_EVAL" "$CAP_MAP" "$KB_HEALTH"; do
        case "$s" in
            pass) PASS=$((PASS + 1)) ;;
            warn) WARN=$((WARN + 1)) ;;
            fail) FAIL=$((FAIL + 1)) ;;
            *) NONE=$((NONE + 1)) ;;
        esac
    done
    echo "Reflect ${LAST_RUN}: ${PASS} OK, ${WARN} warn, ${FAIL} fail, ${NONE} n/a | ${COMMITS_FOUND} commits, ${PATTERNS} patterns"
    exit 0
fi

# Full table output
echo "## Ecosystem Health Report - ${LAST_RUN}"
echo ""
echo "| # | Check | Status | Detail |"
echo "|---|-------|--------|--------|"
echo "| 1 | Cross-Review | $(sym "$CROSS_REVIEW") | ${GEMINI_PENDING}G ${CODEX_PENDING}Cx ${CLAUDE_PENDING}Cl pending |"
echo "| 2 | Skills Dev | $(sym "$SKILLS_DEV") | ${SKILLS_CREATED} new, ${SKILLS_ENHANCED} enhanced |"
echo "| 3 | File Structure | $(sym "$FILE_STRUCT") | ${ORPHAN_DOCS} orphan docs, ${ORPHAN_SCRIPTS} scripts |"
echo "| 4 | Context Mgmt | $(sym "$CONTEXT_MGMT") | ${AVG_SESSION} msgs/session, ${CORRECTION_RATE} corrections |"
echo "| 5 | Best Practices | $(sym "$BEST_PRACTICES") | ${REPOS_WITH_TESTS} repos w/tests, ${UNCOMMITTED} uncommitted |"
echo "| 6 | Submodule Sync | $(sym "$SUBMODULE_SYNC") | ${SUBS_DIRTY} dirty, ${SUBS_UNPUSHED} unpushed |"
echo "| 7 | CLAUDE.md Health | $(sym "$CLAUDE_MD") | ${CMD_OVERSIZED}/${CMD_TOTAL} oversized |"
echo "| 8 | Hook Coverage | $(sym "$HOOKS") | ${HOOKS_COV}% coverage |"
echo "| 9 | Stale Branches | $(sym "$STALE_BR") | ${STALE_COUNT} stale (>30 days) |"
echo "| 10 | GitHub Actions | $(sym "$GH_ACTIONS") | ${ACTIONS_FAIL}/${ACTIONS_TOTAL} failing |"
echo "| 11 | Folder Structure | $(sym "$FOLDER_STRUCT") | ${STRUCT_ISSUES} issues |"
echo "| 12 | Test Coverage | $(sym "$TEST_COV") | ${AVG_COV}% avg, ${LOW_COV}/${COV_REPOS} below 80% |"
echo "| 13 | Test Pass/Fail | $(sym "$TEST_PF") | ${TEST_PASS} pass, ${TEST_FAIL} fail |"
echo "| 14 | Refactor | $(sym "$REFACTOR") | ${LARGE_FILES} large files, ${TODO_COUNT} TODOs |"
echo "| 15 | Aceengineer Cron | $(sym "$AE_CRON") | stats ${AE_STATS}, report ${AE_REPORT} |"
echo "| 16 | Session RAG | $(sym "$SESSION_RAG") | ${SR_SESSIONS} sessions, ${SR_EVENTS} events (${SR_DATE}) |"
echo "| 17 | CC Insights | $(sym "$CC_INSIGHTS") | v${CC_VER}, reviewed: ${CC_REVIEWED} |"
echo "| 18 | Work Queue | $(sym "$WQ_STATUS") | ${WQ_PENDING}P ${WQ_WORKING}W ${WQ_BLOCKED}B (${WQ_STALE} stale) |"
echo "| 19 | Skill Eval | $(sym "$SKILL_EVAL") | ${SE_PASSED}/${SE_TOTAL} pass, ${SE_CRITICAL} critical |"
echo "| 20 | Capability Map | $(sym "$CAP_MAP") | ${CAP_REPOS} repos, ${CAP_DOMAINS} domains (${CAP_DATE}) |"
echo "| 21 | Knowledge Base | $(sym "$KB_HEALTH") | ${KB_TOTAL} entries, ${KB_STALE} stale, avg ${KB_CONF} |"
echo ""

# Count statuses
PASS=0 WARN=0 FAIL=0 NONE=0
for s in "$CROSS_REVIEW" "$SKILLS_DEV" "$FILE_STRUCT" "$CONTEXT_MGMT" "$BEST_PRACTICES" \
         "$SUBMODULE_SYNC" "$CLAUDE_MD" "$HOOKS" "$STALE_BR" "$GH_ACTIONS" "$FOLDER_STRUCT" \
         "$TEST_COV" "$TEST_PF" "$REFACTOR" "$AE_CRON" "$SESSION_RAG" "$CC_INSIGHTS" \
         "$WQ_STATUS" "$SKILL_EVAL" "$CAP_MAP" "$KB_HEALTH"; do
    case "$s" in
        pass) PASS=$((PASS + 1)) ;;
        warn) WARN=$((WARN + 1)) ;;
        fail) FAIL=$((FAIL + 1)) ;;
        *) NONE=$((NONE + 1)) ;;
    esac
done

echo "**Summary:** ${PASS} OK, ${WARN} warnings, ${FAIL} failures, ${NONE} not available"
echo ""

# Action items (failures)
HAS_FAILS=false
for s in "$CROSS_REVIEW" "$FILE_STRUCT" "$CLAUDE_MD" "$HOOKS" "$GH_ACTIONS" "$FOLDER_STRUCT" \
         "$TEST_COV" "$TEST_PF" "$AE_CRON" "$SESSION_RAG" "$WQ_STATUS" "$SKILL_EVAL" \
         "$CAP_MAP" "$KB_HEALTH"; do
    [[ "$s" == "fail" ]] && HAS_FAILS=true
done

if [[ "$HAS_FAILS" == "true" ]]; then
    echo "### Action Items"
    echo ""
    [[ "$CROSS_REVIEW" == "fail" ]] && echo "- Cross-Review: ${GEMINI_PENDING}G + ${CODEX_PENDING}Cx + ${CLAUDE_PENDING}Cl reviews pending"
    [[ "$FILE_STRUCT" == "fail" ]] && echo "- File Structure: ${ORPHAN_DOCS} orphan docs, ${ORPHAN_SCRIPTS} orphan scripts"
    [[ "$CLAUDE_MD" == "fail" ]] && echo "- CLAUDE.md: ${CMD_OVERSIZED} files exceed size limits"
    [[ "$HOOKS" == "fail" ]] && echo "- Hooks: only ${HOOKS_COV}% coverage"
    [[ "$GH_ACTIONS" == "fail" ]] && echo "- GitHub Actions: ${ACTIONS_FAIL} repos failing"
    [[ "$FOLDER_STRUCT" == "fail" ]] && echo "- Folder Structure: ${STRUCT_ISSUES} issues"
    [[ "$TEST_COV" == "fail" ]] && echo "- Test Coverage: ${AVG_COV}% avg (target 80%)"
    [[ "$TEST_PF" == "fail" ]] && echo "- Tests Failing: ${TEST_FAIL} repos with failures"
    [[ "$AE_CRON" == "fail" ]] && echo "- Aceengineer cron not running"
    [[ "$SESSION_RAG" == "fail" ]] && echo "- Session RAG analysis failed"
    [[ "$WQ_STATUS" == "fail" ]] && echo "- Work Queue: ${WQ_STALE} items blocked >7 days"
    [[ "$SKILL_EVAL" == "fail" ]] && echo "- Skill Eval: ${SE_CRITICAL} critical failures"
    [[ "$CAP_MAP" == "fail" ]] && echo "- Capability Map stale (${CAP_DATE})"
    [[ "$KB_HEALTH" == "fail" ]] && echo "- Knowledge Base: ${KB_STALE} stale entries"
    echo ""
fi

# Warnings
HAS_WARNS=false
for s in "$CONTEXT_MGMT" "$BEST_PRACTICES" "$SUBMODULE_SYNC" "$STALE_BR" "$REFACTOR" \
         "$HOOKS" "$GH_ACTIONS" "$TEST_COV" "$AE_CRON" "$SESSION_RAG" "$CC_INSIGHTS" \
         "$WQ_STATUS" "$SKILL_EVAL" "$CAP_MAP" "$KB_HEALTH"; do
    [[ "$s" == "warn" ]] && HAS_WARNS=true
done

if [[ "$HAS_WARNS" == "true" ]]; then
    echo "### Recommendations"
    echo ""
    [[ "$CONTEXT_MGMT" == "warn" ]] && echo "- Context: avg ${AVG_SESSION} msgs/session, ${CORRECTION_RATE} corrections"
    [[ "$BEST_PRACTICES" == "warn" ]] && echo "- Practices: ${UNCOMMITTED} uncommitted changes"
    [[ "$SUBMODULE_SYNC" == "warn" ]] && echo "- Submodules: ${SUBS_DIRTY} dirty, ${SUBS_UNPUSHED} unpushed"
    [[ "$STALE_BR" == "warn" ]] && echo "- Branches: ${STALE_COUNT} stale (>30 days)"
    [[ "$REFACTOR" == "warn" ]] && echo "- Refactor: ${LARGE_FILES} large files, ${TODO_COUNT} TODOs"
    [[ "$HOOKS" == "warn" ]] && echo "- Hooks: ${HOOKS_COV}% coverage, expand to more repos"
    [[ "$GH_ACTIONS" == "warn" ]] && echo "- CI: ${ACTIONS_FAIL} repos with issues"
    [[ "$TEST_COV" == "warn" ]] && echo "- Coverage: ${AVG_COV}% avg, target 80%"
    [[ "$AE_CRON" == "warn" ]] && echo "- Aceengineer: partial - stats or report outdated"
    [[ "$SESSION_RAG" == "warn" ]] && echo "- Session RAG: stale data (${SR_DATE})"
    [[ "$CC_INSIGHTS" == "warn" ]] && echo "- CC Insights: installed v${CC_VER}, reviewed v${CC_REVIEWED}"
    [[ "$WQ_STATUS" == "warn" ]] && echo "- Work Queue: ${WQ_BLOCKED} items blocked"
    [[ "$SKILL_EVAL" == "warn" ]] && echo "- Skill Eval: ${SE_CRITICAL} critical issues"
    [[ "$CAP_MAP" == "warn" ]] && echo "- Capability Map: aging (${CAP_DATE})"
    [[ "$KB_HEALTH" == "warn" ]] && echo "- Knowledge Base: ${KB_STALE} stale entries"
    echo ""
fi

echo "### RAGS Loop"
echo ""
echo "| Phase | Metric | Value |"
echo "|-------|--------|-------|"
echo "| Reflect | Repos analyzed | ${REPOS_ANALYZED} |"
echo "| Reflect | Commits found | ${COMMITS_FOUND} |"
echo "| Abstract | Patterns extracted | ${PATTERNS} |"
echo "| Abstract | Sessions analyzed | ${SESSIONS} |"
echo "| Abstract | Conversations | ${CONVERSATIONS} |"
echo "| Store | Learnings stored | ${LEARNINGS:-0} |"
echo "| Store | Knowledge captured | ${KNOWLEDGE_CAP:-0} |"
echo ""
echo "---"
echo "Source: ${STATE_FILE}"
echo "Legend: OK = good, WARN = attention, FAIL = action needed, -- = not available"
