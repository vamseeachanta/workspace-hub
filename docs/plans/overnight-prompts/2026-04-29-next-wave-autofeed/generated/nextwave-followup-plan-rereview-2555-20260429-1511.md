Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved. User approval is required.
- Do not run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, or gemini.
- Do not create or edit .planning/plan-approved/* markers.
- Do not implement code. This lane is planning/review/synthesis only.
- Do not edit the plan or any production/source/report artifact. Read-only review only.
- Write exactly one primary result artifact: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-20260429-1511.md
- Do not overwrite other lanes' result files.
- If evidence is insufficient, write a blocker note in the single result artifact and stop.

Task: Cold-context re-review of the #2555 plan after the 14:46 patch lane, determining whether the patch resolved the prior MINOR findings and whether any new blockers remain.

Inputs to read first:
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2554-2555.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-20260429-1446.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-codex.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-gemini.md
- docs/plans/_template-issue-plan.md

Do:
1. Re-check live issue state read-only with gh issue view 2555 --json state,labels,updatedAt if gh is available; otherwise mark live-state as unavailable.
2. Defect-hunt the patched plan against the prior five #2555 findings from gtm-review-2554-2555.md and the patch report. Do not give credit for motion; verify evidence directly in the plan and cited artifacts.
3. Identify any new MAJOR/MINOR/LOW findings introduced by the patch. Pay special attention to: Chart C heading/test consistency, provider-coverage honesty, chart-rendering code-home scope, asset directory mkdir gate, and API RP 1111 caption standard coverage.
4. Produce a verdict in {APPROVE_FOR_USER_REVIEW, MINOR_PATCH_NEEDED, MAJOR_PATCH_NEEDED, BLOCKED}. Phrase any approve-like outcome as ready for user decision, never as approval.
5. Write exactly the single result artifact named above with sections: Executive verdict, live issue state, prior findings re-check table, new findings, boundary compliance, lane classification.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT run plan-review-fanout.sh.
- Do NOT edit the plan file or any report/source file.
- Do NOT draft or send outreach.
- Do NOT apply status:plan-review or status:plan-approved.

End with explicit lane classification: COMPLETED_WITH_RESULT or BLOCKED.
