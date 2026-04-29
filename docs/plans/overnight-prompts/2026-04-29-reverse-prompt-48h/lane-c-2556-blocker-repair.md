# Lane C prompt — #2556 dependency-aware blocker repair

You are a planning worker in `/mnt/local-analysis/workspace-hub`.

Goal: repair #2556 plan MAJOR blockers without pretending #2554/#2555 execution artifacts are complete.

Read first:
- `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`
- `scripts/review/results/2026-04-29-plan-2556-nextwave-claude.md`
- `docs/plans/overnight-prompts/2026-04-29-reverse-prompt-48h/master-plan.md`

Allowed writes:
- #2556 plan/outline/schema only
- a concise result summary under this prompt pack's `results/` directory

Forbidden:
- no email sending
- no private contact data
- no `status:plan-review` unless valid review criteria are actually met
- no `status:plan-approved`

Required fixes:
1. Correct the factual error about existing `vessel-installation-contractors/email-templates.md`.
2. Declare whether existing canonical-folder email templates are reused, superseded, or linked.
3. Make chart-slot checks explicitly dependent on #2555 rendered chart artifacts.
4. Keep send execution gated on user approval and legal/evidence sanity.

Return: changed files, remaining MAJOR blockers, and whether #2556 can be re-reviewed.
