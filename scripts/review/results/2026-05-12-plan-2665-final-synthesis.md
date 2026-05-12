# Final adversarial review synthesis — #2665

## Scope
Plan: `docs/plans/2026-05-12-issue-2665-provider-credit-approval-dashboard-dispatch-gates.md`

## Review artifacts
- `scripts/review/results/2026-05-12-plan-2665-claude.md`
- `scripts/review/results/2026-05-12-plan-2665-codex.md`
- `scripts/review/results/2026-05-12-plan-2665-gemini.md`
- `scripts/review/results/2026-05-12-plan-2665-disagreement.md`
- `scripts/review/results/2026-05-12-plan-2665-focused-review-a.md`
- `scripts/review/results/2026-05-12-plan-2665-focused-review-b.md`

## Final decision
APPROVAL-READY FOR USER PLAN REVIEW.

Implementation remains blocked until the user approves and the issue has both:
1. `status:plan-approved` label, and
2. `.planning/plan-approved/2665.md` marker.

## Resolved blocker classes
- User-only approval authority; generic operator approval removed.
- Per-issue approval transaction locking and approval/resume race coverage.
- ace-linux-1/Hermes-leader single-writer lease model.
- ace-linux-2 worker-only behavior unless explicit single-writer promotion handoff disables the prior leader.
- #2519 coexistence preflight before lease writes/dispatch launch.
- Strict issue-specific approval gate fails closed on missing/ambiguous issue inference.
- Reuse/integration with `scripts/ai/continuous-planning-pipeline.py` instead of duplicate readiness classifiers.
- Correct provider-work-queue regression path: `tests/analysis/test_provider_work_queue.py`.
- Acceptance command includes all modified/new key surfaces.
