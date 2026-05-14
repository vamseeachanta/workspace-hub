#!/usr/bin/env bash
# Claude lane — session C5
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2665
# Catalog: Tier 2 #26 cross-provider AI review apparatus config [planning-heavy]
# Plan: docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md

set -uo pipefail
ISSUE=2665
SESSION=C5
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2665 (kanban provider-credit approval dashboard and dispatch gates).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 2 #26 cross-provider AI review apparatus config / quota rebalancing [planning-heavy] — direct fit.

Brain/hands role:
  planning brain:  this session (claude main)
  routing/hands:   claude main direct (governance/config work is brain-heavy)
  review:          codex T1

Plan: docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md (approved with marker)

CRITICAL: this work touches scripts/ and .claude/ paths — the [plan-gate] hook may fire on commits to those paths. If so:
  1. Verify status:plan-approved label IS set on #2665 (it is, per pre-launch checklist)
  2. Verify marker at .planning/plan-approved/2665.md EXISTS (it does, per checklist)
  3. The hook should pass. If it still rejects, capture the error and use FORCE_PLAN_GATE=1 ONLY after confirming both gates are set; log the bypass to the issue comment.

OVERNIGHT run. Commit incrementally. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval of other issues, GIT_OPTIONAL_LOCKS=0 for read ops, multi-agent-commit-serialization (wait+retry on .git/index.lock).'

echo "DRY RUN — uncomment your preferred claude invocation:"
echo "  claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
