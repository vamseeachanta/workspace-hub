#!/usr/bin/env bash
# Hermes lane — session H7
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2628
# Catalog: Tier 1 #11 CI/CD pipeline triage [bidirectional]
# Plan: docs/plans/2026-05-03-issue-2628-digitalmodel-domain-divided-ci.md
# Target repo: digitalmodel (REPO-ISOLATED FROM WORKSPACE-HUB — low contention risk)

set -uo pipefail
ISSUE=2628
SESSION=H7
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2628 (digitalmodel domain-divided CI architecture).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #11 CI/CD pipeline triage [bidirectional]. Replaces maxfail-masking pattern noted in feedback_qg_maxfail_undercounts (pytest --maxfail=20 was masking true failure count of 244+).

Brain/hands role:
  planning brain:  hermes routing
  routing/hands:   hermes -> codex (CI YAML + workflow restructure is Codex sweet spot)
  review:          codex T1; claude T2 in morning triage

Plan: docs/plans/2026-05-03-issue-2628-digitalmodel-domain-divided-ci.md (status:plan-approved confirmed; local marker missing — proceed per label-is-the-gate convention).

REPO-ISOLATION: target is digitalmodel at /mnt/local-analysis/digitalmodel (separate git repo from workspace-hub). All git operations in this session use the digitalmodel repo, NOT workspace-hub. This eliminates lock contention with the C-lane sessions and H6/H8 (which touch workspace-hub).

Acceptance criteria (from plan): domain-divided CI replaces single maxfail gate; each domain (orcaflex, openfoam, etc.) gets its own CI job that surfaces full failure count; no silent ceiling clipping.

OVERNIGHT run. Commit incrementally INSIDE digitalmodel repo. Progress comment on workspace-hub#2628 every ~30 min wall-clock. CI changes are high-impact — DO NOT push CI changes that would break a fresh `git clone + uv sync + pytest` flow without surfacing it as a tradeoff in the progress comment.

Hard rules:
  - NEVER use --no-verify
  - NEVER self-approve
  - Surface BLOCKED on persistent failure
  - If CI changes require GitHub Actions runner config that needs human auth, surface and stop'

echo "DRY RUN — adjust for your Hermes v0.13.0 invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/codex --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "  # fallback: codex exec - <<< \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
