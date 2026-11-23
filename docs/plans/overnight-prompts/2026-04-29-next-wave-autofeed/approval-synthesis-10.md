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

Task: synthesize the approval-readiness batch into a truthful 10-issue promotion table.

Inputs:
- docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/approval-pack-elements-2540-2544.md
- docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/approval-pack-additional-5.md
- docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/adversarial-readiness-review.md
- Remote results if present: ace2-next5-plan-prep.md and ace2-approved-execution-scout.md under the same results dir, or /mnt/local-analysis/ace2-worker-logs.
- Live GitHub issue labels for candidates #2540 #2541 #2542 #2543 #2544 #2490 #2510 #2370 #2375 #2378 #2538 #2509 #2474 #2363 plus any higher-confidence live status:plan-review issues.

Do:
1. Re-query live GitHub state for all candidate issues.
2. Read the local plans and review artifacts for each candidate; do not trust stale labels.
3. Build a table with: issue link, title, live status labels, plan artifact, latest review evidence, legal/provenance gate, blocker summary, readiness verdict (READY_NOW / NEEDS_MINOR / BLOCKED), exact user action.
4. Goal is 10 candidates, but do not fabricate readiness. If fewer than 10 are ready, provide the top 10 with blockers and the next run needed for each.
5. Write docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md.
6. Also write generated/approval-promotion-command-pack.md containing only draft gh commands/comments for user-approved promotions; no execution.
7. Commit/push scoped synthesis artifacts if safe.
