# A1 — ace-linux-1 Codex approved recovery lane

You are running on `ace-linux-1` from `/mnt/local-analysis/workspace-hub`. Use Codex strengths: bounded implementation, test repair, verification, and closeout. Do not ask the user questions.

## Hard rules

1. Respect plan gate. Only implement issues already carrying `status:plan-approved`.
2. Use fresh per-issue worktrees under `/mnt/local-analysis/night-runs/ace1-codex/` whenever changing code.
3. Do not modify or commit parent-checkout session files: `.claude/state/*`, provider telemetry JSON/MD, or this prompt pack unless the issue explicitly requires it.
4. For Python commands, use `uv run` unless the target repo has a documented existing `.venv` workaround.
5. Before each issue: `gh issue view`, inspect latest comments, check whether work is already complete, and skip/verify rather than duplicate.
6. Commit and push only issue-scoped changes. Post a GitHub issue comment with commit SHA, verification commands, and remaining blockers.
7. Stop on destructive ambiguity: no force push, no hard reset of primary checkout, no secret handling.

## Work queue, in order

### 1. #2289 — Plan rollback/recovery for enforcement bypasses detected after commit or push
URL: https://github.com/vamseeachanta/workspace-hub/issues/2289
Labels: `priority:high`, `cat:harness`, `domain:workflow`, `status:working`, `agent:codex`, `status:plan-approved`.

Goal: verify whether the planned rollback/recovery enforcement work is already landed; if not, implement the narrow missing tests/docs/scripts described in the latest issue body/comments. Produce a closeout-ready comment.

### 2. #2433 — worldenergydata main CI collection errors blocking Dependabot PRs
URL: https://github.com/vamseeachanta/workspace-hub/issues/2433
Labels: `priority:high`, `cat:infrastructure`, `status:blocked`, `agent:codex`, `status:plan-approved`.

Goal: first reproduce or verify current blocker state in an isolated `worldenergydata` worktree/checkout. If a narrow fix is obvious and safe, implement with tests. If still blocked by dependency/environment drift, write a blocker report with exact command output and next issue split.

### 3. #2459 — assethold python-tests lint/mypy/quality-gate hardening
URL: https://github.com/vamseeachanta/workspace-hub/issues/2459
Labels: `priority:medium`, `cat:infrastructure`, `status:blocked`, `agent:codex`, `status:plan-approved`.

Goal: verify current assethold failure state and either land a narrow test/lint fix or write an evidence-backed blocker report. Do not broaden into repo-wide lint cleanup.

### 4. #2269 — OpenFOAM ESI v2312 baseline workflow and validation
URL: https://github.com/vamseeachanta/workspace-hub/issues/2269
Labels: `priority:high`, `cat:engineering`, `cat:documentation`, `status:working`, `machine:dev-secondary`, `agent:codex`, `status:plan-approved`.

Goal: validate current work; if incomplete, add/repair narrowly scoped baseline workflow docs/smoke validation. Keep engineering-tool assumptions explicit.

### 5. #2346 — GTM prospect-data customized-demo pipeline
URL: https://github.com/vamseeachanta/workspace-hub/issues/2346
Labels: `priority:high`, `cat:engineering`, `domain:gtm`, `status:working`, `agent:codex`, `status:plan-approved`.

Goal: verify if current pipeline work is already complete. If not, land a bounded artifact/test/doc improvement aligned with the issue plan and comment evidence.

## Deliverable

Write a final lane report to:

`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/ace1-codex-approved-recovery.md`

Include a table: issue, action taken, branch/worktree, commit SHA(s), verification, GitHub comment URL, remaining blocker.
