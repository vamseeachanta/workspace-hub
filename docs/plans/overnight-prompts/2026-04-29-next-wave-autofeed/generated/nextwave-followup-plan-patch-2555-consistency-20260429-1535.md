Global rules for this next-wave autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- This lane is planning/document-consistency only. Do not implement production/code changes.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved or status:plan-review to any GitHub issue.
- Do NOT run gh issue edit, gh issue comment, gh issue close, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, hermes, or git push.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT touch digitalmodel/, assethold/, worldenergydata/, frontierdeepwater/, ai-orchestrator-template/, or any production/source code.
- Do NOT commit. Leave any plan/report edits in the working tree for user review.
- Write exactly one primary result artifact: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-consistency-20260429-1535.md
- Do NOT overwrite any existing nextwave result file.

Task: Patch the #2555 planning/report consistency drift identified by the cold-context re-review, then write a concise patch report.

Inputs to read first:
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-20260429-1511.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-20260429-1446.md
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/_template-issue-plan.md

Allowed edits (only these):
1. In docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md, rewrite the Legal & Evidence Gate provider-review sentence so it matches the tightened plan AC: Claude + Codex + Gemini live verdicts are required; UNAVAILABLE provenance documents a blocker but does not satisfy promotion.
2. In docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md, rewrite the Risks mitigation that currently says to rely on Claude + Gemini cross-coverage so it instead says live Codex evidence is required before any status escalation, and persistent Codex CLI blockage should be escalated to the operator for pin/downgrade per #2479 / feedback_codex_cli_0_124_upstream_regression.md.
3. In docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md, fix Chart C3's caption or add an inline omission rationale so it satisfies the new inherited-standards AC. Prefer adding DNV-ST-N001 to the caption if factually consistent with the existing storyboard.
4. If a targeted edit cannot be made safely, do not improvise: write BLOCKED in the result artifact and stop.

Verification to run after edits:
- git diff -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- grep checks showing: no remaining "permitted fallback" in the storyboard provider gate; no remaining "rely on Claude + Gemini cross-coverage" in the plan risk; Chart C3 caption now contains DNV-ST-N001 or a clear omission rationale.

Result artifact requirements:
- Path: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-consistency-20260429-1535.md
- Include: executive verdict (COMPLETED_WITH_RESULT or BLOCKED), files changed with bullet summary, exact verification commands + outputs, remaining blockers, and boundary compliance.
- Explicitly state that no GitHub mutation, no labels, no approval markers, no fanout, no production/code changes, no outreach, no commits occurred.

Hard guardrails:
- No GitHub mutation of any kind.
- No approval markers.
- No status:plan-approved or status:plan-review application.
- No production/source code edits.
- No plan-review-fanout.sh / codex / gemini.
- No outreach.
- Exactly one result artifact under the next-wave results directory.

End with explicit lane classification.