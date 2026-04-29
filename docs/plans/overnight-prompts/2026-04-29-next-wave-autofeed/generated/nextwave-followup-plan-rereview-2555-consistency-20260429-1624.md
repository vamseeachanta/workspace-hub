Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- This is a planning/review/synthesis-only lane. Do not implement production/code changes.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved or status:plan-review to any GitHub issue.
- Do not mutate GitHub: no gh issue edit/comment/close, no gh pr *, no labels.
- Do not create, edit, or delete .planning/plan-approved/* markers.
- Do not run scripts/review/plan-review-fanout.sh, codex, gemini, hermes mutating commands, or git push.
- Do not edit the plan, storyboard, telemetry, provider reports, queue files, or prior result artifacts.
- Write exactly one primary result artifact and no other files:
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-consistency-20260429-1624.md
- If evidence is insufficient, write that single result artifact as a blocker note and stop.

Task: Cold-context re-review of issue #2555 after the 15:35 consistency patch lane.

Inputs to read first:
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-20260429-1511.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-consistency-20260429-1535.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-codex.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-gemini.md
- docs/plans/_template-issue-plan.md

Do:
1. Re-check live issue #2555 with read-only `gh issue view 2555 --json state,labels,updatedAt` if gh is available; if unavailable, mark label state as unverified and continue from filesystem evidence.
2. Verify whether the 15:35 consistency patch resolved all three MINOR findings A/B/C from the 15:11 re-review:
   - Storyboard Legal & Evidence Gate no longer allows the rejected provider fallback.
   - Plan Risks no longer says Claude + Gemini cross-coverage can substitute for live Codex evidence.
   - Chart C3 caption now cites DNV-ST-N001 or records an explicit omission rationale.
3. Hunt for regressions introduced by the 15:35 patch, especially cross-provider policy drift, standards-citation overclaims, accidental promotion language, source/report code-edit scope creep, and contradictions with the plan template/user approval gate.
4. Produce a verdict in exactly one of: APPROVE_FOR_USER_REVIEW, MINOR_PATCH_NEEDED, MAJOR_PATCH_NEEDED, BLOCKED.
5. Write exactly the single result artifact named above with: executive verdict, live state observed, finding-by-finding re-check, new-regression hunt, remaining blockers, boundary compliance, lane classification, and exhaustive list of files written.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT overwrite other lanes' result files.
- Do NOT run plan-review-fanout.sh, codex, or gemini.
- Do NOT edit any input file; this is read-only re-review.
- Do NOT propose or draft a command that applies status:plan-approved.
- Do NOT claim multi-provider consensus; existing Codex/Gemini nextwave artifacts are UNAVAILABLE unless live canonical artifacts prove otherwise.
- End with explicit lane classification.
