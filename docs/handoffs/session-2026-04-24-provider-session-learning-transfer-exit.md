# Provider Session Learning Transfer Exit — 2026-04-24

## Scope

Assessed recent/unassessed AI-provider sessions across Codex, Hermes, Gemini,
and the existing Claude corpus. Exported fresh provider logs, regenerated the
cross-provider ecosystem audit, and transferred durable learnings into repo
guidance/memory surfaces.

## Commands Run

- `bash scripts/cron/codex-session-export.sh`
- `bash scripts/cron/hermes-session-export.sh`
- `bash scripts/cron/gemini-session-export.sh`
- `bash scripts/cron/provider-session-ecosystem-audit.sh`
- `scripts/legal/legal-sanity-scan.sh --diff-only`

## Assessment Results

- Codex export added 860 normalized records from 1248 matching sessions.
- Hermes export added 132 sessions and skipped 1728 already-exported sessions.
- Gemini export added 1 normalized record from 1130 matching sessions.
- Provider audit regenerated `analysis/provider-session-ecosystem-audit.json`
  and `docs/reports/provider-session-ecosystem-audit.md`.
- Legal sanity scan passed with no violations.

## Durable Learnings Transferred

- Claude remains the highest known migration-debt source for deleted
  `scripts/work-queue/*` transition/gate reads. Redirect those reads to
  governance docs, current hooks, `.planning/` evidence, and cross-review
  workflows instead of restoring deleted files.
- Gemini still reads deleted local work-queue surfaces and the removed
  `scripts/agents/*` wrapper tree. Treat those as stale compatibility
  references unless a live integration proves otherwise.
- Codex missing reads are often workspace-root assumptions for nested-repo
  tasks. Check `digitalmodel/`, `worldenergydata/`, `assethold/`, and
  `aceengineer-website/` before classifying a path as deleted from
  workspace-hub.
- Hermes missing reads are mostly ephemeral worktree or `/tmp` paths. Promote
  only durable outputs back to repo-root docs, plans, skills, or scripts.
- Hermes, Gemini, and Codex still show meaningful bare `python3` usage. Linux
  prompts and provider handoffs should explicitly preserve `uv run ... python`.

## Files Updated By This Session

- `.claude/memory/agents.md`
- `.claude/memory/context.md`
- `analysis/provider-session-ecosystem-audit.json`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/ops/legacy-claude-reference-map.md`
- `docs/reports/provider-session-ecosystem-audit.md`
- `logs/orchestrator/codex/.export-state.json`
- `logs/orchestrator/hermes/.last-export-ts`
- `logs/orchestrator/hermes/corrections/session_20260421.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260422.jsonl`
- `logs/orchestrator/hermes/session_20260421.jsonl`
- `logs/orchestrator/hermes/session_20260422.jsonl`

New export outputs from this run may also exist under:

- `logs/orchestrator/codex/session_20260423.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260423.jsonl`
- `logs/orchestrator/hermes/session_20260423.jsonl`

## Worktree Caveats

Before this handoff, the wider worktree also showed unrelated modified and
untracked planning/review artifacts, including:

- `docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md`
- `docs/plans/README.md`
- new `docs/plans/2026-04-24-issue-2475-...` and `2476-...` plan artifacts
- new `scripts/review/results/2026-04-23-plan-2475-*` and `2476-*` artifacts

Do not revert or stage those as part of this provider-session transfer unless
they are intentionally included in a separate follow-up.

## Recommended Next Step

If committing this transfer, stage the durable memory/docs files, regenerated
audit artifacts, and intentional exported session logs together. Keep unrelated
planning/review artifacts out of the commit unless they belong to the same
operator batch.
