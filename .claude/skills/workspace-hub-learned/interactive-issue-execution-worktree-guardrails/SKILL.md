---
name: interactive-issue-execution-worktree-guardrails
description: Execute approved GitHub issues in isolated worktrees with interactive Claude Code/Codex runs, while containing agent drift and salvaging progress when provider/runtime problems occur.
triggers:
  - User asks to implement GitHub issue work via tmux or interactive Claude Code
  - Multiple provider lanes are being run in parallel across issue clusters
  - Main checkout is dirty, behind remote, or otherwise unsafe for direct execution
  - Autonomous agent drift or provider quota failures threaten a run
---

# Interactive issue execution worktree guardrails

Use this for approved issue execution waves in `workspace-hub`-style repos when the user wants tmux/interactive Claude Code and/or parallel provider dispatch.

## Core pattern
1. Start from a clean isolation boundary.
   - `git fetch origin`
   - create a dedicated worktree per issue or tightly bounded issue cluster
   - base from `origin/main`
   - do not use the dirty main checkout for implementation
2. Materialize plan approval locally.
   - if the issue is approved by user direction or GitHub label but local `.planning/plan-approved/<issue>.md` is missing, add the approval marker inside the worktree and commit it first
3. Write a prompt file in the worktree.
   - keep the mission bounded
   - list owned paths and forbidden paths explicitly
   - require final validation, commit, push, issue comment, and close when complete
4. Launch the provider in an isolated lane.
   - Claude Code: use tmux + interactive `claude --dangerously-skip-permissions` when explicitly approved by the user
   - Codex: use autonomous `codex exec --dangerously-bypass-approvals-and-sandbox` for bounded doc/report/readiness tasks
   - Gemini: treat as opportunistic; expect quota failures and have fallback lanes ready
5. Monitor and intervene early.
   - capture pane / inspect status frequently
   - if the agent touches forbidden files, revert those files externally immediately and restate scope in the session
6. Salvage instead of restarting from zero.
   - if Claude stalls or drifts repeatedly, switch to deterministic local generation (`execute_code`, focused scripts, or another provider) to finish the bounded deliverable
   - preserve useful artifacts, remove temporary prompt files, then validate and land
7. Rebase before push.
   - multiple parallel lanes move `main`; expect `fetch` + `rebase origin/main` before pushing
8. Close only after verification.
   - confirm landed commit, owned-file-only diff, issue comment with commit hash/artifacts, and issue closure where scope is fully implemented

## Prompt design rules
Include these sections explicitly:
- repo/worktree/branch/issue number
- mission in one sentence
- owned paths
- read-only context paths
- forbidden paths
- required deliverables
- validation minimum
- instruction to remove temporary prompt artifacts before final commit if they are not durable deliverables

## Known failure modes and mitigations

### 1) Claude Code drifts into unrelated files
Observed recurring hazard: `scripts/testing/coverage-results.json` was repeatedly modified during unrelated issue work.

Mitigation:
- declare forbidden paths in the prompt
- monitor early output, not just the final result
- if drift occurs, externally revert the file immediately
- send a corrective instruction in tmux constraining the scope to owned paths only
- verify `git status` before commit shows only expected files

### 2) Provider quota exhaustion
Observed:
- Gemini lanes can fail with HTTP 429 or credit exhaustion
- parallel waves can leave one provider unusable mid-run

Mitigation:
- do not block the whole wave on one provider
- keep a fallback Claude or Codex lane ready for planning/readiness/doc generation
- comment on the issue if a provider-specific run fails so the execution trail remains visible

### 3) Worktree hook / pre-push environment drift
Observed: valid doc-only changes can fail pre-push due to unrelated repo hook environment issues.

Mitigation:
- validate the actual scope independently
- if the failure is clearly unrelated and the user has authorized aggressive execution, `--no-verify` may be acceptable for low-risk doc/report changes
- document that choice in the issue comment

### 4) Agent run becomes unproductive
Mitigation:
- stop the session instead of letting it burn budget
- switch to a deterministic local method (`execute_code`) for machine-generated artifacts such as inventories, manifests, and validation reports
- use the agent again only for review/final polish if needed

## Verification checklist
- `git status --short` contains only owned files
- no forbidden files remain modified
- temp prompt files are removed unless intentionally part of the deliverable
- outputs numerically reconcile with their authoritative ledgers or sources
- worktree branch rebased onto latest `origin/main`
- push succeeded (or exception documented)
- issue comment includes what landed and the commit hash
- issue closed only if implementation, not planning-only artifacts, actually completed the approved scope

## When to keep issue open
Keep the issue open if the run only produced readiness dossiers, planning artifacts, or partial reconnaissance without the approved implementation landing.

## Good fit
- bounded doc/report reconciliation
- metadata-only sweeps
- readiness dossiers
- governance or portability doc changes

## Bad fit
- large code changes without tests
- issues lacking approval
- mixed-scope waves without clear owned paths
