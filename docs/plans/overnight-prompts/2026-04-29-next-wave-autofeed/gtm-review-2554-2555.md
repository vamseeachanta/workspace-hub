Global rules for this next-wave worker:
- Workspace: /mnt/local-analysis/workspace-hub.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved. User approval is required.
- Implementation/code changes are forbidden unless a live issue is status:plan-approved AND local approval marker exists; this wave is planning/review/synthesis only.
- If you mutate GitHub, use gh with --body-file for markdown. Prefer drafting command packs unless explicitly safe.
- Write exactly one primary result artifact in docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ plus any review artifacts explicitly requested.
- Before trusting stale context, re-check live issue labels/state and current file contents.
- Run legal sanity scan before committing public-facing GTM/data artifacts.

Task: next safe wave for weekly GTM issues #2554 and #2555.

Inputs:
- docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md
- docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md
- docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md

Do:
1. Re-check GitHub issues #2554 and #2555 live labels/state.
2. Run adversarial plan review for both plans if the local review runner is available. Prefer scripts/review/plan-review-fanout.sh with absolute paths. If Codex/Gemini are blocked, write explicit UNAVAILABLE artifacts and do a strong Claude/Hermes self-review with findings-only stance.
3. Write review artifacts under scripts/review/results/ using names containing 2026-04-29-plan-2554-nextwave and 2026-04-29-plan-2555-nextwave.
4. Patch each plan's Adversarial Review Summary only if review evidence actually exists. If major findings appear, leave as draft and list patch tasks.
5. Prepare safe GitHub progress comments for #2554 and #2555 in generated/*.md using --body-file format. Do not apply status:plan-review unless all evidence supports it; if unsure, draft the exact gh commands only.
6. Write result summary: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2554-2555.md with verdict table, artifacts, blockers, and next safe lane.
7. Commit/push only scoped review/result/plan-summary changes if legal scan passes and no dirty unrelated files are staged.
