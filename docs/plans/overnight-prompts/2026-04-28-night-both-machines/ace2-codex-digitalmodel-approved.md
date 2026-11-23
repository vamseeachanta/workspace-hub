# B1 — ace-linux-2 Claude digitalmodel approved implementation lane

You are running on `ace-linux-2` via a login shell using Claude Code (`claude -p --permission-mode acceptEdits`). Current parent workspace-hub checkout may be behind/dirty; do not mutate it except to read prompt context. Use fresh worktrees under `/mnt/local-analysis/night-runs/ace2-digitalmodel/`. Do not ask the user questions.

## Hard rules

1. Work only on `status:plan-approved` issues.
2. Use isolated worktrees/clones; never broad-commit the dirty parent checkout.
3. `digitalmodel` is a nested git repo. If changing digitalmodel code, operate inside the digitalmodel repo/worktree and commit/push there, not from workspace-hub parent.
4. For digitalmodel tests, prefer the existing repo `.venv` if `uv run` resolver fails: `PYTHONPATH=src ./.venv/bin/python -m pytest ...`.
5. Post GitHub issue comments only after concrete evidence exists. If `gh` or provider auth fails, write a blocker report and stop.

## Target issues

### 1. #2515 — generate offshore cable umbilical pipeline cross-section reports
URL: https://github.com/vamseeachanta/workspace-hub/issues/2515
Labels: `enhancement`, `priority:medium`, `cat:engineering`, `domain:pipeline`, `domain:marine`, `status:plan-approved`.
Plan: `docs/plans/2026-04-27-issue-2515-cross-section-reporting-demo.md`.

Goal: implement or complete the approved cross-section reporting demo in digitalmodel with tests and a reproducible artifact path. Start by re-reading the plan and latest issue comments. Keep scope narrow.

### 2. #2458 — named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness
URL: https://github.com/vamseeachanta/workspace-hub/issues/2458
Labels: `enhancement`, `priority:medium`, `cat:engineering`, `domain:marine`, `status:working`, `machine:dev-primary`, `agent:codex`, `status:plan-approved`.

Goal: verify whether the canonical benchmark fixture is complete. If incomplete and non-overlapping with #2515, implement a narrow fixture/test/doc improvement. If overlap or completion is detected, write evidence and skip.

## Required workflow per issue

```bash
mkdir -p /mnt/local-analysis/night-runs/ace2-digitalmodel
cd /mnt/local-analysis/workspace-hub/digitalmodel
git fetch origin
# create a unique worktree/branch per issue if implementation is needed
```

For each issue:

1. Fetch latest issue body/comments.
2. Check current branch, remotes, dirty state, and recent commits.
3. Determine if the issue is already done. If yes, verify and comment.
4. If coding: write/repair tests first, implement, run focused tests, then broader smoke if cheap.
5. Commit/push branch or main according to repo policy and existing branch state.
6. Comment with evidence: files changed, commit SHA, tests, artifact paths.

## Deliverable

Write a final lane report to remote path:

`/mnt/local-analysis/ace2-worker-reports/night-20260428-digitalmodel.md`

Also, if the local checkout permits, copy/sync an equivalent markdown report into:

`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/ace2-digitalmodel-report.md`

Include: issue, worktree, branch, commit SHA, test commands/results, GitHub comment URL, blocker if any.
