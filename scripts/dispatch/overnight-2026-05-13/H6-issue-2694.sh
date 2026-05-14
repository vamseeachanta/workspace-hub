#!/usr/bin/env bash
# Hermes lane — session H6
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2694
# Catalog: Tier 1 #1 complex refactors [bidirectional]
# Plan: docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md
# Picklist alignment: this is week-of-2026-05-14 pick #1 (Hermes->Codex routed per picklist)

set -uo pipefail
ISSUE=2694
SESSION=H6
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2694 (Epic: Cross-domain duplicate-implementation cleanup).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md:
  gh issue view 2695 --repo vamseeachanta/workspace-hub --json body
  gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200

Catalog match: Tier 1 #1 complex refactors [bidirectional]. Picklist (week of 2026-05-14) lists this as pick #1, routed Hermes -> Codex. Routing is honored.

Brain/hands role:
  planning brain:  hermes routing (this prompt is dispatched FROM hermes)
  routing/hands:   hermes -> codex (refactor/dedup work fits Codex style)
  review:          codex T1 self-review; claude T2 in morning triage

Scope: 6-domain duplicate-implementation cleanup spanning catenary, PipeCapacity, cathodic protection, natural-period, hydro-matrix, on-bottom stability. Epic has sub-issues — favor closing the highest-impact sub first; this is execution work informed by the plan, not greenfield design.

Plan: docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md (status:plan-approved label confirmed; local marker missing — proceed per label-is-the-gate convention).

REPO-SCOPE: workspace-hub primarily, with digitalmodel touch-points for some sub-issues. Commit incrementally in the repo where the change lands. Watch for multi-agent-commit-serialization (feedback memory) — if H7/H8 are running concurrently, serialize commits.

OVERNIGHT run. Progress comment on #2694 every ~30 min wall-clock. Sub-issue closures count as progress; post links.

Hard rules:
  - NEVER use --no-verify
  - NEVER self-approve (any issue)
  - On any persistent failure (3+ retries on same error), surface BLOCKED and stop
  - If routing layer (hermes delegate -> codex) returns "not found" or similar, fall back to direct codex CLI and note the fallback in the log
  - Watch for active Hermes cleanup loops before each commit:
      pgrep -af "git (rebase|stash|commit|merge|reset|checkout)"'

echo "DRY RUN — adjust for your Hermes v0.13.0 invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/codex --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "  # fallback if Hermes routing unavailable: codex exec - <<< \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
