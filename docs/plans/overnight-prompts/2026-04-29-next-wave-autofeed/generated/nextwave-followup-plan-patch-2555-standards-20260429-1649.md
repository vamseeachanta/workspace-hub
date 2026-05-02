Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- This lane is planning/review/synthesis only. Do not implement production/code changes.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-review or status:plan-approved. User approval is required for labels/approval.
- Do not run gh issue edit, gh issue close, gh issue comment, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, or hermes mutating commands.
- Do not create or edit .planning/plan-approved/* markers.
- Do not commit or push.
- Write exactly one primary result artifact at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-standards-20260429-1649.md.
- Do not overwrite any existing result artifact.

Task: Apply a narrow plan/storyboard consistency patch for #2555 based on the pre-existing observations recorded by the 16:24 consistency re-review.

Inputs to read first:
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-consistency-20260429-1624.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-consistency-20260429-1535.md
- digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json
- digitalmodel/examples/demos/gtm/data/pipelay_vessels.json

Do:
1. Re-check live issue state with read-only `gh issue view 2555 --json state,labels,updatedAt`; record it in the result artifact. Do not mutate GitHub.
2. Verify the actual `_references` arrays in the two JSON inputs. Patch only documentation/planning text needed to resolve the pre-existing standards drift from the 16:24 artifact:
   - Plan standards table should enumerate all distinct inherited standards present in `csv_hlv_vessels.json` and `pipelay_vessels.json`, including DNV-OS-H101 and DNV-OS-F101 if present.
   - Storyboard C3 caption should either cite DNV-OS-H101 or record an explicit omission rationale inline, consistent with plan AC §214.
   - If DNV-OS-F101 is intentionally omitted because DNV-ST-F101 is the controlling/current citation, ensure the rationale is explicit and consistent between plan and storyboard.
3. Keep the patch narrow: no source JSON edits, no chart rendering, no report generation, no outreach, no status labels, no approval language.
4. Run read-only verification greps/jq commands as needed and `git diff -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` to summarize the patch.
5. Write exactly one result artifact at the path above with: live issue state, files changed, findings resolved, any residual blockers, boundary compliance, and lane classification.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT edit production/code/data files; only the named plan/storyboard docs may be edited.
- Do NOT overwrite other lanes' result files.
- Do NOT run plan-review-fanout.sh, codex, or gemini.
- If evidence is insufficient, write the result artifact as BLOCKED and stop without editing.

End with explicit lane classification.
