# Lane D2 — ace-linux-2 knowledge/doc-intel overflow feeder


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


Machine: ace-linux-2 via SSH tmux. Provider: Claude. Mode: planning, blocker collapse, command packs.

Allowed writes:
- `/mnt/local-analysis/workspace-hub//mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace2-knowledge-docintel-overflow.md`
- `/mnt/local-analysis/ace2-worker-reports/ace2-knowledge-docintel-overflow-20260428.md` if permission allows

Focus issues: #2402, #2403, #2373, #2369, #2368, #2364, #2378, #2375, #2374, #2372, #2370, #2363, #2540.

Work loop:
1. Reconcile prior B2 blocker report with live issue state.
2. For each blocked issue, identify the one upstream gate to collapse and the exact next command/comment/plan edit.
3. If any issue is actually safe to implement in isolated paths, do the smallest bounded work; otherwise prepare a blocker-collapse command pack.
4. Produce an ordered queue that can feed a next 12-hour wave.
