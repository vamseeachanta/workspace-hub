# Lane A prompt — #2554 review-readiness patch

You are a planning/review-readiness worker in `/mnt/local-analysis/workspace-hub`.

Goal: patch #2554 planning artifacts so the contractor-matrix plan is ready for valid adversarial review.

Read first:
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `scripts/review/results/2026-04-29-plan-2554-nextwave-claude.md`
- `docs/plans/overnight-prompts/2026-04-29-reverse-prompt-48h/master-plan.md`

Allowed writes:
- the #2554 plan file
- the #2554 scaffold file
- a concise result summary under this prompt pack's `results/` directory

Forbidden:
- no emails/outreach
- no `status:plan-approved`
- no broad repo cleanup
- no private contact data in public files

Required fixes:
1. Fix the scaffold heading/test mismatch (`Target N —` vs `Target —`).
2. Resolve High-priority target count inconsistency.
3. Clarify provider-review AC vs documented unavailable-provider fallback.
4. Separate corporate-root evidence from deep-link evidence.
5. Add/plan an evidence slot for pain-point hypotheses.

Return: changed files, exact diffs summary, remaining blockers, and whether #2554 is ready for Gemini/Codex review.
