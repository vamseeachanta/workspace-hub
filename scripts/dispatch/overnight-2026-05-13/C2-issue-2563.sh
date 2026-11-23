#!/usr/bin/env bash
# Claude lane — session C2
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2563
# Catalog: Tier 1 #18 error handling standardization [execution-heavy] (closest match for cross-platform messaging integration)
# Plan: docs/plans/2026-05-02-issue-2563-telegram-hermes.md

set -uo pipefail
ISSUE=2563
SESSION=C2
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2563 (Telegram mobile access for Hermes AI control).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #18 error handling standardization [execution-heavy] — closest fit; messaging-integration patterns inherit the standardization shape.

Brain/hands role:
  planning brain:  this session (claude main)
  routing/hands:   claude main direct
  review:          codex T1

Plan: docs/plans/2026-05-02-issue-2563-telegram-hermes.md (approved with marker)

CRITICAL: this work touches Hermes config — check for active Hermes cleanup loops before any commit (feedback_hermes_active_preflight_check). Run:
  pgrep -af "hermes" | grep -v grep

If Hermes is actively running cleanup loops, defer this session until tomorrow morning AFTER #2696 upgrade audit lands.

OVERNIGHT run. Commit incrementally. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval, GIT_OPTIONAL_LOCKS=0 for read ops.'

echo "DRY RUN — uncomment your preferred claude invocation:"
echo "  claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
