# Lane D prompt — #2557 productivity refresh

You are a productivity-review worker in `/mnt/local-analysis/workspace-hub`.

Goal: refresh #2557 plan/report so it reflects live provider/work-queue numbers and does not create duplicate follow-up issues.

Read first:
- `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md`
- `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md`
- `scripts/review/results/2026-04-29-plan-2557-nextwave-claude.md`
- `docs/reports/provider-utilization-weekly.md`
- `docs/reports/provider-work-queue.md`
- `docs/plans/overnight-prompts/2026-04-29-reverse-prompt-48h/master-plan.md`

Allowed writes:
- #2557 plan/report
- generated comment drafts for existing issues #2479/#2519 if needed
- a concise result summary under this prompt pack's `results/` directory

Forbidden:
- do not create new issues until duplicate checks against #2479/#2519 are explicit
- do not block GTM artifact work with productivity-meta work
- no `status:plan-approved`

Required fixes:
1. Refresh Claude/Codex/Gemini utilization numbers from live source.
2. Refresh work-queue ready/routed counts from live source.
3. Correct H1 if the Codex 0.123 pin is only a plain-terminal workaround, not a Claude Bash fix.
4. Collapse H2/H4 into comments or scope questions on #2519 unless a true gap remains.

Return: changed files, corrected live numbers, duplicate-check result, and top 3 owner-time-saving actions.
