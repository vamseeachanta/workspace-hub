# Lane D1 — ace-linux-2 digitalmodel/offshore overflow verifier


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


Machine: ace-linux-2 via SSH tmux. Provider: Claude. Mode: bounded verification/planning; implementation only if fresh worktree and approval markers are safe.

Allowed writes on remote repo:
- `/mnt/local-analysis/workspace-hub//mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace2-digitalmodel-overflow.md`
- `/mnt/local-analysis/ace2-worker-reports/ace2-digitalmodel-overflow-20260428.md` if permission allows

Focus issues: #2515, #2462, #2458, #2327, #2272, #2270, #2269.

Work loop:
1. Re-check live issue labels/comments.
2. Inspect repo/tool readiness for digitalmodel and engineering tools, using read-only commands first.
3. For #2515, determine exact blocker to safe worktree implementation and whether a narrower docs/report artifact can be produced.
4. For #2462/#2458, verify whether prior work is complete and produce merge/close/prep evidence.
5. For #2272/#2270/#2269, verify smoke-test docs/tool presence and classify what can be done next on ace-linux-2.
6. Only implement if all gates pass and writes are isolated; otherwise write a precise blocker/next-lane report.
