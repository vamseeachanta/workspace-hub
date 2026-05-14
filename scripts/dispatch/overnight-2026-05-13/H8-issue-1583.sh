#!/usr/bin/env bash
# Hermes lane — session H8
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/1583
# Catalog: Tier 2 #29 cross-machine config parity [execution-heavy]  (template-driven config work)
# Plan: NONE — /goal will plan from scratch
# Dovetails with tonight's Hermes v0.13.0 verification (project_hermes_installation memory just refreshed)

set -uo pipefail
ISSUE=1583
SESSION=H8
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #1583 (Hermes config parity via repo ecosystem templates).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 2 #29 cross-machine config parity [execution-heavy] — template + apply mechanical work, ideal Codex hand.

Brain/hands role:
  planning brain:  hermes routing (with mandatory /goal planning step since no plan file exists)
  routing/hands:   hermes -> codex (template/config work is Codex sweet spot)
  review:          codex T1; claude T2 in morning triage

PLAN STATUS: NO plan file exists for #1583. The /goal invocation must FIRST produce a plan (writing-plans skill), achieve adversarial review at MINOR or better, and commit the plan to docs/plans/2026-05-13-issue-1583-hermes-config-parity-plan.md BEFORE any config-template work begins.

DO NOT self-label status:plan-approved. Stop at status:plan-review and post a clear "ready for user approval" comment on #1583. If you produce a plan AND user has already left a pre-authorization in the issue comments, you may proceed; otherwise stop.

Scope (from issue body): Hermes config (~/.hermes/config.yaml + .env structure) should be template-driven so each machine in the ecosystem (ace-linux-1, ace-linux-2, windows hosts) renders an equivalent config from a single source. Touches scripts/cron/, possibly config/, possibly .claude/skills/operations/.

REPO-SCOPE: workspace-hub primarily. Watch for collision with H6 (which also touches workspace-hub commit surface). Use multi-agent-commit-serialization pattern (feedback memory) — write-only-shared for any subagents you spawn.

Hard rules:
  - NEVER use --no-verify
  - NEVER self-approve
  - Stop at status:plan-review if user pre-authorization is not in the issue comments
  - Watch for active Hermes cleanup loops:
      pgrep -af "git (rebase|stash|commit|merge|reset|checkout)"
  - Hermes config under audit is YOUR OWN runtime — do NOT mutate live ~/.hermes/config.yaml mid-run; stage changes in a separate template file and surface for review'

echo "DRY RUN — adjust for your Hermes v0.13.0 invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/codex --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "  # fallback: codex exec - <<< \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
