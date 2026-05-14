#!/usr/bin/env bash
# Claude lane — session C3
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2403
# Catalog: Tier 1 #15 performance optimization pass [bidirectional] (embeddings model selection has performance criteria)
# Plan: docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md

set -uo pipefail
ISSUE=2403
SESSION=C3
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2403 (doc-intel embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #15 performance optimization pass [bidirectional] — spike has measurable criteria (latency, quality, cost).

Brain/hands role:
  planning brain:  this session (claude main)
  routing/hands:   claude main direct (spike is bench-and-decide, no autonomous code generation)
  review:          codex T1

Plan: docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md (approved with marker)

DOWNSTREAM: C4 (#2402 — embeddings index build) consumes the model decision from this spike. Post the final model recommendation as a top-line comment on #2403 BEFORE 6 AM local time so C4 can read it on morning startup.

OVERNIGHT run. Commit benchmark scripts + results incrementally. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval, GIT_OPTIONAL_LOCKS=0 for read ops.'

echo "DRY RUN — uncomment your preferred claude invocation:"
echo "  claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
