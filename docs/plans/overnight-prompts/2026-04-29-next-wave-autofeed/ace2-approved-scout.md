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

Task on ace-linux-2 overflow: scout currently plan-approved/open issues for verify/close or execution-pack candidates.

Do not mutate GitHub and do not implement. Re-check live GitHub issues with status:plan-approved if gh auth works; otherwise use local artifacts and record auth limitation. Identify 8 candidates split into: verify/close, execution-ready after marker check, blocked/stale approval. Write docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ace2-approved-scout.md. Include exact next prompt text for the top 3 safe lanes.
