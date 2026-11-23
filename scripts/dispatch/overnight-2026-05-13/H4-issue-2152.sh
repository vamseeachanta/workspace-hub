#!/usr/bin/env bash
# Hermes lane — session H4 (touches workspace-hub — contention risk with C-lane)
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2152
# Catalog: Tier 1 #10 test suite hardening [execution-heavy]
# Plan: NO PLAN FILE ON DISK — /goal will plan from scratch ⚠

set -uo pipefail
ISSUE=2152
SESSION=H4
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2152 (reporting golden fixture corpus + validator coverage).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #10 test suite hardening [execution-heavy] — fixture corpus IS test hardening.

⚠ CONTENTION WARNING: this session touches workspace-hub scripts/review/ paths. C1-C5 also touch workspace-hub. Mitigation:
  - Use a worktree: git worktree add /tmp/wh-h4 -b dispatch/h4-2152 main
  - Run all git operations inside the worktree
  - cleanup with git worktree remove after morning triage
  - feedback_worktree_isolation_large_repo_cost warns this is slow (~60% timeout on hub); allow up to 30 min for worktree creation

Brain/hands role:
  planning brain:  hermes routing
  routing/hands:   hermes -> codex (test fixture generation is Codex-friendly)
  review:          codex T1 + claude T2 morning

⚠ NO PLAN FILE ON DISK. PLAN-ONLY MODE — plan to docs/plans/2026-05-14-issue-2152-reporting-golden-fixture-plan.md inside the worktree, stop at end of planning.

OVERNIGHT plan-only run. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval.'

echo "DRY RUN — adjust for your Hermes invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/codex --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
