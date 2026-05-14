#!/usr/bin/env bash
# Hermes lane — session H2
# Issue: https://github.com/vamseeachanta/workspace-hub/issues/2112
# Catalog: Tier 1 #13 schema migration safety review [planning-heavy] — data backfill needs schema discipline
# Plan: NO PLAN FILE ON DISK — /goal will plan from scratch ⚠

set -uo pipefail
ISSUE=2112
SESSION=H2
LOG_DIR=/mnt/local-analysis/workspace-hub/logs/overnight-2026-05-14
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${SESSION}-issue-${ISSUE}.log"

PROMPT='Run /goal on issue #2112 (SubseaIQ equipment counts backfill to unblock cost benchmarking).

FIRST: fetch the /goal catalog and rule per .claude/rules/goal-invocation.md.

Catalog match: Tier 1 #13 schema migration safety review [planning-heavy] — data backfill is essentially a one-shot schema-aware migration.

Brain/hands role:
  planning brain:  hermes routing
  routing/hands:   hermes -> claude-code (data backfill needs careful schema reasoning; better than Codex for this)
  review:          codex T1 + claude T2 morning

⚠ NO PLAN FILE ON DISK. /goal MUST plan from scratch tonight. PLAN-ONLY MODE for this session:
  - Read the issue body in full
  - Plan to docs/plans/2026-05-14-issue-2112-subseaiq-backfill-plan.md
  - Stop AT END OF PLANNING — do NOT begin implementation
  - Post the planned approach as a comment on #2112
  - User reviews in the morning; if approved, implementation runs in a separate session

OVERNIGHT plan-only run. Progress comment every ~30 min.

Hard rules: no --no-verify, no self-approval. This session must NOT flip its own status:plan-approved label.'

echo "DRY RUN — adjust for your Hermes invocation:"
echo "  hermes delegate --skill autonomous-ai-agents/claude-code --task \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "  # fallback: claude --dangerously-skip-permissions -p \"\$PROMPT\" 2>&1 | tee \"$LOG\""
echo "$PROMPT" > "$LOG_DIR/${SESSION}-prompt.txt"
