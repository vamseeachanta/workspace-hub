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

Task: fix the run conveyor by producing a durable safe auto-feed policy and next-queue, without unsafe autonomous approval/implementation.

Do:
1. Inspect active cronjobs 3dae8266219b and 5ae81116b608 behavior from available prompts if visible, plus recent result artifacts.
2. Identify why current monitors tracked completion but did not launch enough next safe lanes.
3. Write docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md containing:
   - current run inventory,
   - completion classifier,
   - safe auto-spawn transitions,
   - unsafe transitions requiring user approval,
   - queue of 8-12 next bounded lane prompts with priority and artifact path,
   - exact cronjob update recommendation.
4. Write generated/safe-autofeed-cron-prompt.md: a self-contained cron prompt that can inspect completed result files and launch the next safe generated prompt if no active worker exists. It must never apply status:plan-approved, never send outreach, never implement unapproved code, and must use unique sessions/logs/artifacts.
5. Do not create the cronjob yourself; just write the prompt and result. The orchestrator will create/update cronjob after verifying.
6. Commit/push scoped artifacts if safe.
