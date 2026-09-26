#!/usr/bin/env bash
# Tonight's single overnight session — PLANNING for #2702 routing-layer audit
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2702
# Context:
#   - Hermes v0.13.0 upgrade is already DONE (verified 2026-05-13).
#   - Original tonight target #2696 was scoped down + CLOSED earlier this session.
#   - #2702 is the scoped-out residue: empirical delegate_task verification + Anthropic base/overage check.
#   - #2702 is NOT plan-approved — this session PRODUCES the plan, it does NOT implement.
#
# Run this ONE script tonight. In the morning, review the draft plan, label
# #2702 with status:plan-review, and (if approved) status:plan-approved + drop the marker.

set -uo pipefail

ISSUE=2702
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-13
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/00-tonight-issue-${ISSUE}.log"

PROMPT='Run the workspace-hub issue-planning workflow on issue #2702.

CRITICAL: this issue is NOT status:plan-approved. Do NOT run /goal. Do NOT implement.
Produce a draft plan that the user can approve in the morning.

FIRST: load the planning skill per CLAUDE.md:
  .claude/skills/coordination/issue-planning-mode/SKILL.md

Workflow (mandatory per CLAUDE.md):
  Issue -> Resource Intel -> Reproduce (Step 1.5) -> Plan -> Adversarial Review -> status:plan-review
  STOP at status:plan-review. Do NOT self-label status:plan-approved.

Context for #2702 (scoped-out follow-up from closed #2696):
  - Hermes v0.13.0 is verified live on ace-linux-1 (OAuth: OpenAI Codex logged in; Anthropic key not set)
  - Two empirical ACs remain from #2696:
    (1) delegate_task round-trip: one to Claude Code hand + one to Codex hand
    (2) Anthropic Max base-vs-overage consumption diff via dashboard snapshots
  - The brain/hands D7 model in #2695 depends on both checks
  - Test procedure sketch is already in the #2702 body — refine, do not rewrite

Output:
  1. docs/plans/2026-05-13-issue-2702-routing-layer-audit-plan.md (draft plan, template at docs/plans/_template-issue-plan.md)
  2. Adversarial review notes appended at end of plan
  3. Post status comment on #2702 announcing the draft + linking the plan file
  4. Add label status:plan-review on #2702 (NOT status:plan-approved)

Resource Intel checklist:
  - Read parent #2696 + its scope-down comment + the closure context
  - Read #2695 D7 (the three-layer model being tested)
  - Read project_hermes_installation memory (current state)
  - Read feedback_hermes_active_preflight_check (operational gotcha)
  - Reproduce: hermes status + hermes config show + hermes cron list  (capture baseline)

Reproduce step (Step 1.5 mandate):
  Confirm hermes delegate_task primitive exists in v0.13.0 BEFORE writing the plan that depends on it.
  hermes --help | grep -i delegate  OR  hermes delegate --help

Hard rules (from feedback memory):
  - NEVER use --no-verify
  - NEVER self-approve any issue
  - NEVER label status:plan-approved on #2702 (or any other issue)
  - Surface BLOCKED state immediately if any of: delegate_task missing, hermes status unhealthy, Anthropic dashboard inaccessible
  - Watch for active Hermes cleanup loops:
      pgrep -af "git (rebase|stash|commit|merge|reset|checkout)"
  - If Hermes is mid-loop, defer planning step and retry'

# Launch — adjust the actual command to match your local claude CLI invocation.
# Recommended: claude with bypassPermissions for autonomous overnight runs.
#
# Example invocations (uncomment ONE):
#
#   claude --dangerously-skip-permissions -p "$PROMPT" 2>&1 | tee "$LOG"
#   claude --print "$PROMPT" 2>&1 | tee "$LOG"
#   claude -p "$PROMPT" 2>&1 | tee "$LOG"

echo "DRY RUN — uncomment your preferred claude invocation in $0 (lines 53-55)"
echo "Prompt saved at: $LOG_DIR/00-tonight-prompt.txt"
echo "$PROMPT" > "$LOG_DIR/00-tonight-prompt.txt"
echo "Log will land at: $LOG"
