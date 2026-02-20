#!/usr/bin/env bash
# Stop hook: Warn if no WRK item was created or modified during this session.
# Enforces: "ALL work must have a WRK item" (CLAUDE.md > Work Items & Approval Gates)
set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo "")}"
[[ -z "$REPO_ROOT" ]] && exit 0

WQ_DIR="$REPO_ROOT/.claude/work-queue"
[[ -d "$WQ_DIR" ]] || exit 0

# Check git status for any WRK-*.md changes (modified, added, or untracked)
wrk_changes=$(cd "$REPO_ROOT" && git status --porcelain -- ".claude/work-queue/" 2>/dev/null | grep -c 'WRK-' || true)

if (( wrk_changes == 0 )); then
    echo ""
    echo "⚠️  WRK TRACEABILITY: No work items were created or modified this session."
    echo "   All work — trivial, harness, or work streams — must be tracked."
    echo "   Create a WRK item: .claude/work-queue/pending/WRK-<NNN>.md"
    echo ""
fi
