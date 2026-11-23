#!/usr/bin/env bash
# Hermes lane — session H5
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2657
# Catalog: Tier 2 #27 knowledge wiki coverage expansion [bidirectional] — path-drift remediation supports wiki ops
# Plan: docs/plans/2026-05-08-issue-2657-hermes-llm-wiki-spinout-path-drift.md
# ⚠ OVERLAPS with #2696 (Hermes upgrade) — DEFER if tonight's #2696 audit reveals routing changes

set -uo pipefail
ISSUE=2657
SESSION=H5
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2657 (Hermes llm-wiki spinout path drift remediation).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 2 #27 knowledge wiki coverage expansion [bidirectional] — path-drift fix supports wiki operations.

⚠ PRE-LAUNCH CHECK: this work overlaps with #2696 (Hermes upgrade audit from tonight). Before starting:
  gh issue view 2696 --repo vamseeachanta/workspace-hub --comments | tail -50

If tonight'\''s #2696 audit landed routing changes that affect llm-wiki paths, DEFER this session and post a comment on #2657 explaining the deferral. Restart this session only after the #2696 work is fully merged.

Brain/hands role:
  planning brain:  hermes routing
  routing/hands:   hermes -> claude-code (path-drift fix benefits from Claude'\''s file-system reasoning)
  review:          codex T1

Plan: docs/plans/2026-05-08-issue-2657-hermes-llm-wiki-spinout-path-drift.md (approved with marker)

OVERNIGHT run (conditional on pre-launch check). Commit incrementally to workspace-hub AND llm-wiki repos as appropriate. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval, multi-agent-commit-serialization.'

echo "DRY RUN — adjust for your Hermes invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/claude-code --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
