# B2 — ace-linux-2 knowledge/doc-intel approved implementation lane

You are running on `ace-linux-2` via a login shell using Claude Code (`claude -p --permission-mode acceptEdits`). Use bounded implementation, data-pipeline/doc generation, tests, and verification. Do not ask the user questions.

## Machine caveat

The ace-linux-2 parent `/mnt/local-analysis/workspace-hub` checkout may be behind/dirty. Treat it as read-only. Create fresh worktrees/clones under `/mnt/local-analysis/night-runs/ace2-knowledge/` before code/doc changes.

## Hard rules

1. Only implement issues with `status:plan-approved`.
2. Before each issue, read latest issue body/comments and check if already completed by another run.
3. Use issue-scoped worktrees/branches. Avoid overlapping files between issues; if two issues touch the same wiki/doc index, finish one before starting the next and pull/rebase before continuing.
4. Use `uv run` for Python commands. Do not require network/licensed tools unless the issue explicitly requires it.
5. Commit/push only issue-scoped changes. Post evidence comments.
6. Stop and write blocker evidence on auth/env/data gaps.

## Work queue, in order

### 1. #2364 — Batch Pack 1: promote API/standards-portal metadata into thin wiki domains
URL: https://github.com/vamseeachanta/workspace-hub/issues/2364
Labels: `priority:high`, `cat:documentation`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved`.

### 2. #2368 — generate faceted portal pages for large LLM-wiki domains
URL: https://github.com/vamseeachanta/workspace-hub/issues/2368
Labels: `priority:high`, `cat:documentation`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved`.

### 3. #2369 — Batch Pack 2: promote indexed conference summaries into wiki topic stubs
URL: https://github.com/vamseeachanta/workspace-hub/issues/2369
Labels: `priority:high`, `cat:data-pipeline`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved`.

### 4. #2373 — Batch Pack 4: non-ACMA standards summary promotion
URL: https://github.com/vamseeachanta/workspace-hub/issues/2373
Labels: `priority:high`, `cat:data-pipeline`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved`.

### 5. #2403 — embeddings model-selection spike
URL: https://github.com/vamseeachanta/workspace-hub/issues/2403
Labels: `priority:medium`, `cat:data-pipeline`, `cat:research`, `domain:document-intelligence`, `status:working`, `agent:codex`, `status:plan-approved`.

### 6. #2227 — promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis
URL: https://github.com/vamseeachanta/workspace-hub/issues/2227
Labels: `priority:medium`, `cat:documentation`, `agent:codex`, `status:plan-approved`, `status:needs-data`.

## Execution strategy

- First pass: classify each issue as `already complete`, `safe to implement`, or `blocked` using live evidence.
- Implement at most 3 issues in one night; prefer highest confidence and least file overlap.
- For blocked items, write blocker report and exact next data request; do not spin.
- If a wiki/domain promotion batch has an existing script, use it rather than manual editing. Add/repair tests for script behavior where possible.

## Deliverable

Write final lane report to remote path:

`/mnt/local-analysis/ace2-worker-reports/night-20260428-knowledge-docintel.md`

If safe, also write/copy:

`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/ace2-knowledge-docintel-report.md`

Report table columns: issue, classification, files changed, commit SHA, verification command/result, GitHub comment URL, blocker/next action.
