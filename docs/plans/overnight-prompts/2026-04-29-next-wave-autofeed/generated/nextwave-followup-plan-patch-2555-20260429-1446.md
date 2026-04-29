Global rules for this next-wave autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before work.
- ace-linux-1 is the control plane; ace-linux-2 is overflow only.
- Planning/review/synthesis only. Do not implement production/code changes outside the explicitly named plan file.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not mutate GitHub: no gh issue edit/comment/close, no gh pr commands.
- Do not apply status:plan-approved. Do not apply status:plan-review.
- Do not create/edit .planning/plan-approved/* markers.
- Do not run scripts/review/plan-review-fanout.sh, codex, gemini, or mutating Hermes commands.
- Do not edit digitalmodel/, assethold/, worldenergydata/, frontierdeepwater/, ai-orchestrator-template/.
- Write exactly one primary result artifact at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-20260429-1446.md.
- If evidence is insufficient, write the result artifact with BLOCKED and stop.

Task: Safely patch the #2555 plan after the next-wave Claude MINOR review. This is a plan-only patch lane, not an approval lane and not a GitHub/comment lane.

Inputs to read first:
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2554-2555.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-claude.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-codex.md
- scripts/review/results/2026-04-29-plan-2555-nextwave-gemini.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/_template-issue-plan.md

Do:
1. Re-check live issue #2555 read-only with gh issue view --json state,labels,updatedAt. Do not mutate.
2. Verify the Claude MINOR findings against the current plan and storyboard before editing.
3. Apply only low-risk plan-file edits to docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md addressing these findings where safe:
   - fix the chart-count grep pattern so it matches actual `### Chart C...` headings;
   - preserve AC #5 as blocked on real Codex+Gemini evidence or explicitly frame UNAVAILABLE as not sufficient for status:plan-review;
   - resolve the chart-rendering implementation-home ambiguity without allowing edits under digitalmodel/**;
   - add mkdir/asset-directory creation gate for docs/reports/gtm/assets/ at the plan level;
   - add standards-citation/caption defensibility requirement for API RP 1111 or explicit omission rationale.
4. Do not edit the storyboard/report files; plan may require future edits to them via TDD/AC only.
5. Write the result artifact with: live state, files changed, finding-by-finding resolution table, remaining blockers, boundary compliance, and lane classification.

Hard guardrails:
- No GitHub mutations. No status label changes.
- No approval markers.
- No outreach drafts/sends beyond existing unposted generated files.
- No production/source/subrepo edits.
- No cross-provider fanout.
- No public claims from private/raw data.

End with explicit lane classification: COMPLETED_WITH_RESULT or BLOCKED_WITH_RESULT.
