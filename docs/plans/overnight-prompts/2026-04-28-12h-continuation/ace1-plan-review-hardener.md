# Lane C3 — plan-review hardener for engineering/GTM candidates


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


Machine: ace-linux-1. Provider: Claude. Mode: planning/review only unless already approved.

Allowed writes:
- `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-hardener.md`
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/plan-review-command-pack.md`

Do not implement code.

Focus issues: #2510, #2490, #2509, #2507, #2513, #2516, #2474, #2473, #2472, #2454.

Work loop:
1. Re-check each issue live with `gh issue view --json number,title,labels,body,comments,url`.
2. For `status:plan-review` issues (#2510, #2490), adversarially review plan readiness and write exact changes needed for approval.
3. For high-value unapproved engineering issues, draft implementation-ready plan skeletons or issue refinement comments, but do not apply labels.
4. Produce a command pack with draft `gh issue comment --body-file` payloads stored in the result, not executed unless unquestionably safe.
5. Rank by GTM boundary-pushing value and implementation readiness.
