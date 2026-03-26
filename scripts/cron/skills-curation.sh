#!/usr/bin/env bash
# skills-curation.sh — Wrapper for claude skills-curation invocation.
# Called by cron; wraps the claude CLI skill invocation.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
cd "$WORKSPACE_HUB"
exec claude --dangerously-skip-permissions -p "Archive stale skills (unused >90 days), validate frontmatter (name, description, type fields) on all .claude/skills/ files, and report findings."
