Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved. User approval is required.
- Do not run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, or gemini.
- Do not create or edit .planning/plan-approved/* markers.
- Do not implement production/code changes. This lane is plan-patching only for an unapproved issue currently in review.
- Write exactly one primary result artifact at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md. Do not write any other result/review artifact.
- Before trusting stale context, re-check only read-only local/live state as needed; if GitHub is used, read-only gh issue view only.
- If evidence is insufficient, write the one result artifact as BLOCKED and stop.

Task: Patch the #2552 plan to resolve the safe single-author review findings from the next-wave autofeed lane, without promoting or implementing anything.

Inputs to read first:
- docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md
- docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md
- docs/governance/TRUST-ARCHITECTURE.md
- docs/plans/_template-issue-plan.md

Do:
1. Read the inputs and identify the exact patches recommended in the review artifact for F1-F6, plus low-risk L1/L3 if they can be addressed without scope expansion: fix pytest path, add tests/security file to Files-to-Change, include HIDE_CHECKLIST in AC/tests, add #2550 sibling enforcement reference, add collaborators_only caveat for Scenario 3, resolve the docs/security path open question, avoid naming the external commenter inline in the runbook acceptance criteria, and align README/index expectations if applicable.
2. Edit only docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md. Do not edit docs/security, tests, TRUST-ARCHITECTURE, issue labels, or approval markers.
3. Preserve the issue as status:plan-review / awaiting user approval. Update the Adversarial Review Summary/front-matter truthfully to reference the single-author review artifact and note that Codex/Gemini fanout is still not run unless the plan explicitly uses the T1 deferred-review path.
4. Run read-only validation commands sufficient to verify the plan text contains the patched guardrails (grep/read-only checks are fine). Do not run implementation tests.
5. Write exactly one result artifact at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md with: summary of plan edits, findings resolved, any residual blockers, validation commands/output summary, git diffstat for the plan file only, and lane classification.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT apply or draft status:plan-approved.
- Do NOT implement docs/security/external-contributor-runbook.md, tests, TRUST-ARCHITECTURE changes, or any source/config file. Plan file only.
- Do NOT run plan-review-fanout.sh, codex, or gemini.
- Do NOT overwrite any other lane's result file.

End with explicit lane classification: COMPLETED_WITH_RESULT, BLOCKED, or FAILED_NO_RESULT.
