Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved. User approval is required.
- Do not run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, or any state-mutating hermes command.
- Do not create or edit .planning/plan-approved/* markers.
- Do not implement production/code changes. This lane is planning/review/synthesis only.
- Write exactly one primary result artifact and no other files: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md
- Do not overwrite other lanes' result files.
- If evidence is insufficient, write a blocker note to the expected result artifact and stop.

Task: Perform a single-author, plan-only adversarial review of issue #2550's plan. This is a safe review/synthesis lane; it must not mutate GitHub, labels, approval markers, source code, or plan files.

Inputs to read first:
- docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
- docs/plans/_template-issue-plan.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md
- Relevant rules/memories if present: feedback_never_offer_to_self_label_plan_approved.md, feedback_adversarial_review_stance.md, feedback_permission_gate_blocks_cross_review.md, feedback_codex_cli_0_124_upstream_regression.md

Do:
1. Re-check live issue state read-only with `gh issue view 2550 --json number,title,state,labels,updatedAt` and record the timestamp/output summary in the result. If gh is unavailable, state that live verification is unavailable and continue from filesystem evidence only.
2. Read the plan and template end to end. Evaluate whether the plan is internally consistent, acceptance criteria are testable, security/operations risks are bounded, and the implementation scope avoids unsafe automation or public-claim drift.
3. Produce an adversarial review with sections: Executive verdict, Findings table, Required patches before approval, Evidence checked, Boundary compliance.
4. Use verdict exactly one of: APPROVE_FOR_USER_REVIEW, MINOR_PATCH_NEEDED, MAJOR_PATCH_NEEDED, BLOCKED.
5. Write exactly one file at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md and do not write any other artifact.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT apply status:plan-approved or status:plan-review.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT edit the plan file; recommend patches in the result only.
- Do NOT run plan-review-fanout.sh, codex, or gemini.
- Do NOT implement any code or cron changes.

End the result with explicit lane classification: COMPLETED_WITH_RESULT, BLOCKED, or FAILED_NO_RESULT.
