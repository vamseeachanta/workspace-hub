#!/usr/bin/env bash
# Stop hook: Warn if no WRK item was created or modified during this session.
# Enforces: "ALL work must have a WRK item" (CLAUDE.md > Work Items & Approval Gates)
set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo "")}"
[[ -z "$REPO_ROOT" ]] && exit 0

WQ_DIR="$REPO_ROOT/.claude/work-queue"
[[ -d "$WQ_DIR" ]] || exit 0

# Read active WRK from state file (fast) or fall back to working/ scan
active_wrk=""
state_file="${REPO_ROOT}/.claude/state/active-wrk"
if [[ -f "$state_file" ]]; then
    active_wrk="$(cat "$state_file" 2>/dev/null || true)"
fi
if [[ -z "$active_wrk" && -d "${WQ_DIR}/working" ]]; then
    # Glob is alphabetically ordered; take first match as canonical active item
    for _f in "${WQ_DIR}/working"/WRK-*.md; do
        [[ -f "$_f" ]] && { active_wrk="$(basename "$_f" .md)"; break; }
    done
fi
# Validate format to prevent terminal injection from a tampered state file
[[ "$active_wrk" =~ ^WRK-[0-9]+$ ]] || active_wrk=""

# Check uncommitted WRK changes and commits from last 12 hours.
# NOTE: 12h window is a heuristic; true session-scoping requires session-start
# timestamp infrastructure (tracked as future improvement in WRK-285 follow-up).
wrk_uncommitted=$(cd "$REPO_ROOT" && git status --porcelain -- ".claude/work-queue/" \
    2>/dev/null | grep -c 'WRK-' || true)
wrk_committed=$(cd "$REPO_ROOT" && git log --since="12 hours ago" --name-only --pretty=format: \
    -- ".claude/work-queue/" 2>/dev/null | grep -c 'WRK-' || true)
wrk_changes=$(( wrk_uncommitted + wrk_committed ))

if (( wrk_changes == 0 )); then
    echo ""
    if [[ -n "$active_wrk" ]]; then
        echo "⚠️  WRK TRACEABILITY: ${active_wrk} was active but no work-queue changes found."
    else
        echo "⚠️  WRK TRACEABILITY: No work items were created or modified this session."
    fi
    echo "   All work — trivial, harness, or work streams — must be tracked."
    echo "   Create a WRK item: .claude/work-queue/pending/WRK-<NNN>.md"
    echo ""
fi
