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

Task on ace-linux-2 overflow: turn known approval-readiness blockers into operator-ready prep packets.

Focus candidates: #2490, #2510, #2474, #2370, #2378, #2541, #2544.
Do not mutate GitHub. Do not implement. Read live/local artifacts, classify the blocker for each, and write docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ace2-blocker-prep.md with one bounded next-lane prompt per blocker. Include exact files to inspect and acceptance criteria. If repo state on ace-linux-2 is stale, note it and avoid changing files.
