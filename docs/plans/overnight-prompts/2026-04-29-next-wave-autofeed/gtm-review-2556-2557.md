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

Task: next safe wave for weekly GTM issue #2556 and productivity issue #2557.

Inputs:
- docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md
- docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md
- docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md
- docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2556-summary.md
- docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md
- docs/reports/2026-04-29-weekly-productivity-flow-hacks.md
- docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2557-summary.md

Do:
1. Re-check GitHub issues #2556 and #2557 live labels/state.
2. Run or recover adversarial review for both plans. Prefer scripts/review/plan-review-fanout.sh with absolute paths; if a provider fails, capture an explicit artifact rather than pretending coverage exists.
3. Write review artifacts under scripts/review/results/ using names containing 2026-04-29-plan-2556-nextwave and 2026-04-29-plan-2557-nextwave.
4. Patch plan Adversarial Review Summary sections only with truthful provider evidence.
5. For #2557, extract H1/H2/H4 into follow-up issue draft bodies under generated/ but do not create new issues unless duplicate checks are conclusive and it is clearly safe. Prefer command pack.
6. Prepare GitHub progress comments for #2556/#2557 as generated/*.md. Do not send outreach and do not mutate status:plan-approved.
7. Write result summary: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2556-2557.md.
8. Commit/push scoped changes only after legal scan passes.
