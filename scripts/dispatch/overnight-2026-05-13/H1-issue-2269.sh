#!/usr/bin/env bash
# Hermes lane — session H1
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2269
# Catalog: Tier 2 #24 marine engineering recompute campaigns [execution-heavy]
# Plan: docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md
# Target repo: digitalmodel (REPO-ISOLATED FROM WORKSPACE-HUB — low contention risk)

set -uo pipefail
ISSUE=2269
SESSION=H1
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2269 (openfoam ESI v2312 baseline workflow + validation).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 2 #24 marine engineering recompute campaigns [execution-heavy] — openfoam baseline is a recompute-campaign analogue.

Brain/hands role:
  planning brain:  hermes routing (this prompt is dispatched FROM hermes)
  routing/hands:   hermes -> codex (execution-heavy; openfoam scripting fits Codex style)
  review:          codex T1 (self-review) + claude T2 if available on morning triage

Plan: docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md (approved with marker)

REPO-ISOLATION: target is digitalmodel at /mnt/local-analysis/digitalmodel (separate git repo from workspace-hub). All git operations in this session use the digitalmodel repo, NOT workspace-hub. This eliminates lock contention with the C-lane sessions.

OVERNIGHT run. Commit incrementally INSIDE digitalmodel repo. Progress comment on workspace-hub#2269 every ~30 min wall-clock.

Hard rules: no --no-verify, no self-approval, surface BLOCKED immediately.'

echo "DRY RUN — adjust for your Hermes v0.13.0 invocation (verify routing landed from tonight's #2696 audit):"
echo "  hermes delegate --skill autonomous-ai-agents/codex --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "  # fallback if Hermes routing absent: codex exec - <<< \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
