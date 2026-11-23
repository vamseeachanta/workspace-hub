#!/usr/bin/env bash
# Hermes lane — session H3 (DEPENDS ON H2 OUTPUT)
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2055
# Catalog: Tier 1 #2 architecture cleanup [planning-heavy] — cost benchmarking schema is architectural
# Plan: NO PLAN FILE ON DISK — /goal will plan from scratch ⚠

set -uo pipefail
ISSUE=2055
SESSION=H3
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2055 (subsea cost benchmarking from SubseaIQ equipment counts).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #2 architecture cleanup [planning-heavy] — benchmarking architecture decisions.

DEPENDENCY: this issue consumes the equipment-counts data from H2 (#2112 — SubseaIQ backfill). BEFORE starting any benchmarking, check H2 progress:
  gh issue view 2112 --repo vamseeachanta/workspace-hub --comments | tail -30

If H2 has not posted "backfill plan complete" by 4 AM local time, file BLOCKED on #2055 and stop.

Brain/hands role:
  planning brain:  hermes routing
  routing/hands:   hermes -> claude-code
  review:          codex T1 + claude T2 morning

⚠ NO PLAN FILE ON DISK. PLAN-ONLY MODE — plan to docs/plans/2026-05-14-issue-2055-subsea-cost-benchmarking-plan.md, stop at end of planning, do NOT implement.

OVERNIGHT plan-only run. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval.'

echo "DRY RUN — adjust for your Hermes invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/claude-code --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
