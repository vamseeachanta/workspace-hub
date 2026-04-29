# Lane D3 — ace-linux-2 adversarial review + GSD hygiene feeder


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


Machine: ace-linux-2 via SSH tmux. Provider: Claude. Mode: read-only adversarial review / issue hygiene.

Allowed writes:
- `/mnt/local-analysis/workspace-hub//mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace2-review-and-gsd.md`
- `/mnt/local-analysis/ace2-worker-reports/ace2-review-and-gsd-20260428.md` if permission allows

Focus: recent agent work and stale-open approved issues.

Work loop:
1. Review last 24h commits, issue comments, and overnight result artifacts.
2. Find false completion claims, duplicate blockers, stale `status:working`, missing plan docs, and ready-to-close candidates.
3. Produce a prioritized issue hygiene pack: reopen/close/comment/label proposals with evidence.
4. Do not mutate GitHub; write exact `gh` commands and body text for ace-linux-1 control surface to approve/use.
