#!/usr/bin/env bash
# Tonight's single overnight session — Hermes v0.4.0 -> v0.13.0 upgrade audit
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2696
# Goal: stabilize Hermes routing layer so tomorrow's 10-parallel Hermes lane works
#
# Run this ONE script tonight. Launch in a single terminal; let it run autonomously.
# In the morning, run the pre-launch checklist from README.md before launching the 10 parallel sessions.

set -uo pipefail

ISSUE=2696
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-13
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/00-tonight-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2696 (Hermes v0.4.0 -> v0.13.0 upgrade audit).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md:
  gh issue view 2695 --repo vamseeachanta/workspace-hub --json body
  gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200

Catalog match: this is governance/infrastructure work — closest entry is Tier 2 #28 repo governance gate rollout [bidirectional], with Hermes-specific overlay.

Brain/hands role: planning brain only tonight (no execution layer required for the audit).

Scope (from issue body):
1. Inventory current Hermes v0.4.0 install (skills, configs, auth, cron)
2. Compare against v0.13.0 changelog; identify breaking changes
3. Upgrade path decision
4. Apply upgrade on ace-linux-1
5. Routing-layer audit (delegate_task + Kanban + Anthropic Max base/overage separation)
6. Update project_hermes_installation.md memory once verified

This is an OVERNIGHT autonomous run. Commit incrementally. Post progress comment on #2696 every ~30 min wall-clock. Surface BLOCKED state immediately and stop — do NOT loop on the same error.

Pre-commit gate: this issue has status:plan-approved label but check marker state at /mnt/local-analysis/workspace-hub/.planning/plan-approved/2696.md. If marker missing and an implementation commit blocks on plan-gate, use FORCE_PLAN_GATE=1 ONLY for /goal-authorized work paths.

Hard rules (from feedback memory):
- NEVER use --no-verify
- NEVER self-approve any other issue
- Check for active Hermes cleanup loops before any upgrade step (pgrep -af "git (rebase|stash|commit|merge|reset|checkout)")
- If Hermes is mid-loop, defer the upgrade step and retry after the loop completes'

# Launch — adjust the actual command to match your local claude CLI invocation.
# Recommended: claude with bypassPermissions for autonomous overnight runs.
#
# Example invocations (uncomment ONE):
#
#   claude --dangerously-skip-permissions -p "$PROMPT" 2>&1 | tee "$LOG"
#   claude --print "$PROMPT" 2>&1 | tee "$LOG"
#   claude -p "$PROMPT" 2>&1 | tee "$LOG"

echo "DRY RUN — uncomment your preferred claude invocation in $0 line 51-53"
echo "Prompt to launch (saved at $LOG_DIR/00-tonight-prompt.txt):"
echo "$PROMPT" > "$LOG_DIR/00-tonight-prompt.txt"
echo "Log will land at: $LOG"
