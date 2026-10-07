# Batch MAJOR Review Closeout

Use this reference after a batch adversarial plan-review wave when one or more plans return MAJOR.

## Core rule

A preserved or pre-written task list that says "post summaries and move labels to `status:plan-review`" is conditional on the review wave returning approval-ready findings. Fresh MAJOR review evidence overrides that stale task wording.

If any required provider returns MAJOR:
- keep the issue in its earlier state, usually `status:needs-plan` or local `draft`
- do **not** apply `status:plan-review`
- post a blocking review summary comment with artifact links
- update the local plan and index to say revision/re-review is required
- revise the active todo wording so it records the governance decision, e.g. "post summaries; do not move labels because reviews returned MAJOR"

## Safe closeout sequence

1. Verify review artifacts exist and are non-empty for each provider/disagreement artifact.
2. Extract the actual verdicts from artifacts, not from memory.
3. Patch each plan's `Adversarial Review Summary` with:
   - latest verdicts
   - concise blocking themes
   - review artifact paths
   - explicit approval-readiness state
4. Patch `docs/plans/README.md` issue-scoped rows only.
5. If posting to GitHub, use `gh issue comment --body-file` for markdown-safe comments.
6. Leave labels conservative when MAJOR exists:
   - do not add `status:plan-review`
   - remove/downgrade stale advanced labels only if governance cleanup requires it and the issue state supports that action
7. Verify live issue labels/comments and local diff before commit/push.

## Pitfall: broad README replacements

Do not run global replacements like `Awaits adversarial plan review.` → `Round 1 returned MAJOR` across `docs/plans/README.md`. That can corrupt unrelated plan rows that were not in the current review wave.

Use issue-scoped replacements anchored by issue number or plan slug, then inspect the nearby diff. If collateral drift is found, restore unrelated rows before posting or committing.

## Report wording

When reporting to the user, distinguish:
- review completed
- comments posted
- labels intentionally not advanced
- verification/commit/push still pending, if true

Do not frame "not moved to plan-review" as incomplete if MAJOR findings make it the correct governance outcome.
