# Lane C1 — ace-linux-1 control-plane reconciler and feeder


# 12-hour continuous lane rules

Start: 2026-04-28 21:49:46 local. Stop no later than: 2026-04-29 09:49:46 local.

You are an unattended worker in the workspace-hub repo ecosystem. Do not ask the user questions. Keep ace-linux-1 as the approval/control surface. Respect plan gates:
- Implementation/code changes only for issues that are live `status:plan-approved` and have an appropriate local approval marker if hooks require it.
- For unapproved or ambiguous issues, do planning, verification, blocker classification, runbooks, command packs, and GTM packaging only.
- No force push, hard reset, secret handling, or destructive cleanup.
- Use fresh worktrees for code changes. If worktree creation or permissions fail, write a blocker report instead of trying unsafe parent-checkout edits.
- Use `uv run` for Python unless the target repo documents a venv exception.
- Preserve engineering evidence boundaries: do not turn signals into claims without proof paths.
- Write progress and final output to your assigned result file only; avoid files owned by other lanes.
- Before any GitHub mutation, re-check live issue state. If uncertain, write a draft command/comment pack rather than mutating.


Machine: ace-linux-1. Provider: Claude. Mode: orchestration/read-mostly.

Goal: keep the whole repo ecosystem fed for 12 hours without unsafe duplicate launches.

Allowed writes:
- `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-control-reconciler.md`
- `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/next-dispatch-queue.md`
- `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/github-command-pack.md`

Do not edit code. Do not close/merge issues.

Work loop until stop time or exhaustion:
1. Inspect current prompt packs/results under `docs/plans/overnight-prompts/2026-04-28-night-both-machines/` and this continuation pack.
2. Inspect live open issues using `gh issue list` and the latest comments for top candidates.
3. Build a prioritized queue with buckets: READY_TO_IMPLEMENT, NEEDS_PLAN, NEEDS_REVIEW, BLOCKED_RESOURCE, GTM_PACKAGING, VERIFY_CLOSE.
4. For each bucket, write exact next prompts/commands for another lane to consume.
5. Identify lanes that completed/blocked and propose safe follow-up work, but do not launch new processes yourself.
6. End with a morning action table: issue, current state, next action, provider/machine, approval needed, evidence path.

Priority issue seeds: #2548, #2525, #2524, #2523, #2519, #2515, #2462, #2458, #2433, #2402, #2373, #2369, #2368, #2364, #2346, #2289, #2272, #2269, #2510, #2490.
