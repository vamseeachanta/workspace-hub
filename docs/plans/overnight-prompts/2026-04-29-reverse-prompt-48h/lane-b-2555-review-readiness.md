# Lane B prompt — #2555 review-readiness patch

You are a planning/review-readiness worker in `/mnt/local-analysis/workspace-hub`.

Goal: patch #2555 planning artifacts so the capability-chart plan is ready for valid adversarial review.

Read first:
- `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`
- `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
- `scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md`
- `docs/plans/overnight-prompts/2026-04-29-reverse-prompt-48h/master-plan.md`

Allowed writes:
- the #2555 plan file
- the #2555 storyboard file
- a concise result summary under this prompt pack's `results/` directory

Forbidden:
- no chart rendering yet unless the plan is already approved (it is not)
- no `digitalmodel/` source edits
- no `status:plan-approved`

Required fixes:
1. Clarify provider-review acceptance criterion or fallback.
2. Name the exact future chart-rendering entry point outside `digitalmodel/` edits.
3. Lock asset home recommendation: `docs/reports/gtm/assets/` unless review rejects it.
4. Clarify which headline numbers are verified now vs later.

Return: changed files, exact diffs summary, remaining blockers, and whether #2555 is ready for Gemini/Codex review.
