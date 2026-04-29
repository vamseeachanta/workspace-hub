Global rules for this next-wave follow-up worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Planning/review/synthesis only. Do NOT implement production/code changes.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved. Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, or any mutating hermes command.
- Do NOT mutate GitHub. Use read-only gh issue view/list only if needed.
- Write exactly one primary result artifact and nothing else: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2552-20260429-1333.md
- Do NOT overwrite other lanes' files. If the expected result file already exists, stop and report BLOCKED in stdout only.

Task: cold-context re-review of the patched #2552 plan after the 13:10 plan patch lane.

Inputs to read first:
- docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md
- docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md
- docs/governance/TRUST-ARCHITECTURE.md
- docs/plans/_template-issue-plan.md

Do:
1. Re-check live issue state read-only with `gh issue view 2552 --json number,title,state,labels,updatedAt` if gh is available; if unavailable, mark the live-state field as unavailable and proceed from local artifacts.
2. Review whether the patched plan resolves prior review findings F1-F6 plus L1/L3, and whether L2 is acceptably documented as deferred.
3. Hunt for new regressions introduced by the patch. Stay adversarial; cite precise file/section evidence.
4. Produce one verdict from: APPROVE_FOR_USER_REVIEW, MINOR_PATCH_NEEDED, MAJOR_PATCH_NEEDED, BLOCKED.
5. Write the single result artifact named above with sections: Executive verdict, Prior findings re-check table, New findings, Approval boundary / user decisions, Boundary compliance, Lane classification.

Hard guardrails:
- Do NOT edit the plan file.
- Do NOT write scripts/review/results artifacts; this lane's one artifact is the wave result file only.
- Do NOT mutate GitHub or labels.
- Do NOT approve the issue. If approval-ready, phrase it as "ready for user decision" only.
- If evidence is insufficient, write BLOCKED and stop.

End with explicit lane classification.