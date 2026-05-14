#!/usr/bin/env bash
# Claude lane — session C1
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2533
# Catalog: Tier 2 #28 repo governance gate rollout [planning-heavy]
# Plan: docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md

set -uo pipefail
ISSUE=2533
SESSION=C1
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2533 (repo-portfolio mission/objective statement review across active repos).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md:
  gh issue view 2695 --repo vamseeachanta/workspace-hub --json body
  gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200

Catalog match: Tier 2 #28 repo governance gate rollout [planning-heavy].

Brain/hands role:
  planning brain:  this session (claude main)
  routing/hands:   claude main direct (planning-heavy; no Hermes delegation needed)
  review:          codex T1 (defer; mission/objective edits are doc-only, low-risk)

Plan: docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md (already approved with marker)

OVERNIGHT autonomous run. Commit incrementally. Post progress comment on #2533 every ~30 min.

Hard rules:
- NEVER --no-verify
- NEVER self-approve other issues
- If multiple parallel sessions touch workspace-hub git index, use GIT_OPTIONAL_LOCKS=0 for git status / git diff (feedback_git_status_lock_storm)
- Multi-agent commit serialization: if you hit .git/index.lock contention, wait 30s and retry; do NOT force-clear the lock
- Surface BLOCKED immediately'

echo "DRY RUN — uncomment your preferred claude invocation:"
echo "  claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "Prompt saved at $LOG_DIR/${SESSION}-prompt.txt"
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
