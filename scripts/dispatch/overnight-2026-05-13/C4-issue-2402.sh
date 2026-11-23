#!/usr/bin/env bash
# Claude lane — session C4 (DEPENDS ON C3 OUTPUT)
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2402
# Catalog: Tier 1 #13 schema migration safety review [planning-heavy] (index schema decisions)
# Plan: docs/plans/2026-04-20-issue-2402-embeddings-build-index.md

set -uo pipefail
ISSUE=2402
SESSION=C4
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2402 (doc-intel embeddings index build L2+L3 + query CLI).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

CRITICAL DEPENDENCY: this issue depends on the model selected by C3 (#2403 — embeddings model-selection spike). BEFORE starting any index build, read the most-recent comment on #2403:
  gh issue view 2403 --repo vamseeachanta/workspace-hub --comments | tail -50

If #2403 has not yet posted a final model recommendation, STOP and wait — do NOT pick a default. Re-check #2403 every 30 min. If 4 hours have passed without a #2403 recommendation, file a BLOCKED comment on #2402 and exit cleanly.

Catalog match: Tier 1 #13 schema migration safety review [planning-heavy] — index schema is a one-shot migration.

Brain/hands role:
  planning brain:  this session (claude main)
  routing/hands:   claude main direct
  review:          codex T1

Plan: docs/plans/2026-04-20-issue-2402-embeddings-build-index.md (approved with marker)

OVERNIGHT run (deferred-start: wait for C3). Commit incrementally. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval, GIT_OPTIONAL_LOCKS=0 for read ops.'

echo "DRY RUN — uncomment your preferred claude invocation:"
echo "  claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
