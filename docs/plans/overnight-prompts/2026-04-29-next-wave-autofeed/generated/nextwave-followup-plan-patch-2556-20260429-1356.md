Global rules for this next-wave follow-up worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Planning/review/synthesis only. Do NOT implement production/code changes outside the plan document named below.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved. Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, or any mutating hermes command.
- Do NOT mutate GitHub. Use read-only gh issue view/list only if needed.
- Write exactly one primary result artifact: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-20260429-1356.md
- Do NOT overwrite other lanes' files. If the expected result file already exists, stop and report BLOCKED in stdout only.

Task: plan-only patch for issue #2556 after the next-wave Claude MAJOR review. This is a planning patch lane only; no production, report, tracker, brochure, email, or outreach files may be changed.

Inputs to read first:
- docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2556-2557.md
- scripts/review/results/2026-04-29-plan-2556-nextwave-claude.md
- scripts/review/results/2026-04-29-plan-2556-nextwave-codex.md
- scripts/review/results/2026-04-29-plan-2556-nextwave-gemini.md
- docs/plans/_template-issue-plan.md

Do:
1. Re-check live issue state read-only with `gh issue view 2556 --json number,title,state,labels,updatedAt` if gh is available; if unavailable, mark live state unavailable and proceed from local artifacts.
2. Patch only the #2556 plan file to address the three blocking findings from the Claude MAJOR review: existing `vessel-installation-contractors/email-templates.md` factual error, dependency on #2555 chart deliverables, and disposition of the existing canonical-folder email template. Also address any easy MINOR findings in the same plan if doing so does not expand scope.
3. Keep provider-coverage honesty: Codex/Gemini remain UNAVAILABLE until a permitted terminal fanout runs. Do not claim multi-provider consensus. Do not promote to status:plan-review or status:plan-approved.
4. Preserve GTM safety: no outreach sends, no public claims from private/raw data, no private contact details.
5. Write the single result artifact named above with sections: Summary of plan edits, Finding-by-finding resolution table, Remaining blockers/user decisions, Boundary compliance, Lane classification. Include exact plan sections changed.

Hard guardrails:
- Only edit docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md and the single result artifact named above.
- Do NOT write scripts/review/results artifacts; this lane is a patch lane, not a re-review lane.
- Do NOT mutate GitHub or labels.
- Do NOT approve the issue. If the plan is improved, phrase it as ready for re-review only.
- If evidence is insufficient, write BLOCKED in the result artifact and stop.

End with explicit lane classification.