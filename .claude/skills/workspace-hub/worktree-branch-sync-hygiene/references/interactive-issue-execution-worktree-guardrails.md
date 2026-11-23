# Archived Skill: `interactive-issue-execution-worktree-guardrails`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/interactive-issue-execution-worktree-guardrails`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/interactive-issue-execution-worktree-guardrails`
Consolidation date: 2026-04-29

---

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

### 3b) Plan-approved worktree still blocks late commits for ignored `.claude/*` runtime paths
Observed in `feat/ecosystem-sync` execution:
- `.planning/plan-approved/<issue>.md` existed locally and was committed
- normal code/test commits passed
- a later commit that added `.claude/cron/...` and `.claude/state/...` files required `git add -f` because those paths were ignored
- the subsequent commit was blocked by the plan gate with `NO APPROVAL` despite the existing marker

Mitigation:
- before starting work that must land files under ignored/runtime directories (especially `.claude/cron/`, `.claude/state/`, other force-added paths), probe repo policy early rather than discovering it at the final commit
- explicitly check both:
  - whether `.gitignore` ignores the intended deliverable path
  - whether the local enforcement hooks treat those paths as implementation requiring a different approval route
- if the path requires `git add -f`, treat that as a risk signal and do a small preflight commit experiment or hook inspection before spending a full execution wave on dependent tasks
- when the hook blocks, stop and escalate; do not use `FORCE_PLAN_GATE=1`, `--no-verify`, or similar bypasses unless the user explicitly authorizes that exact bypass
- preserve the staged tree and report the exact blocked paths, hook message, and marker-file evidence so the user can resolve policy vs plan mismatch quickly

### 4) Agent run becomes unproductive
Mitigation:
- stop the session instead of letting it burn budget
- switch to a deterministic local method (`execute_code`) for machine-generated artifacts such as inventories, manifests, and validation reports
- use the agent again only for review/final polish if needed

### 5) Repo-local wrappers and audit scripts break in worktrees due to inherited environment
Observed:
- repo-local wrappers that trust inherited `WORKSPACE_HUB` can accidentally execute against the dirty main checkout instead of the isolated worktree
- direct/manual script runs can also mis-read config or policy files from the wrong checkout when `WORKSPACE_HUB` points elsewhere

Mitigation:
- for repo-local wrappers, derive repo root from the wrapper/script path (`BASH_SOURCE` / `__file__`) instead of trusting inherited `WORKSPACE_HUB`
- treat environment variables like `WORKSPACE_HUB` as optional overrides only when that is explicitly intended and tested
- add a wrapper test that sets a stale `WORKSPACE_HUB` and verifies dry-run output still points at the worktree-local script path
- when validating a new deterministic script in a worktree, test both:
  - normal dry-run/runtime
  - stale-env dry-run/runtime

### 6) Baseline/delta artifact identity churn hides real changes
Observed in deterministic weekly audit work:
- using absolute checkout/worktree paths in `audit_scope` makes baseline reuse fail across worktrees
- including volatile path lists inside the finding identity key causes path-footprint changes to look like brand-new findings instead of `is_changed`
- carry-forward sections can silently omit unchanged lower-confidence findings unless explicitly reconciled into the markdown/report totals

Mitigation:
- derive a stable audit scope from repo-relative semantics when possible (for example `.claude/skills`) rather than absolute worktree paths
- define finding identity from semantic fields that should survive normal location churn (classification + canonical names), not from volatile path lists
- detect path/canonical-name/classification changes in delta comparison so scope changes are surfaced as changed findings
- ensure carry-forward markdown/report sections reconcile with summary counts, including unchanged non-high-confidence findings that remain active
- if `_core` / `_internal` findings are meant to be informational-only, propagate that flag through every finding path (including leaf-collision findings), not just duplicate-name findings

### 7) Approved issue scope is stale relative to current main / current CI
Observed in worldenergydata #2451 execution:
- the approved issue was based on an earlier failing CI run with three clustered signatures
- on a fresh worktree from current `origin/main`, one planned cluster (benchmark fixture/plugin failure) no longer reproduced when tested under CI-like extras
- two other signatures were still real and worth fixing, but the broader directory still had unrelated pre-existing failures
- PR CI stayed red overall even after the bounded fix, so closure had to rely on proving the original signatures disappeared rather than waiting for a fully green repo

Mitigation:
- before editing, rerun a verification-first precheck on current `origin/main` in the isolated worktree and mirror CI conditions as closely as practical (`--all-extras`, issue-specific test targets, log inspection)
- treat the issue body/old CI run as a hypothesis, not ground truth; narrow scope to the failures that still reproduce on current head
- if a planned cluster no longer reproduces, do not force a speculative fix just to match the old plan; document the non-reproduction and keep the patch bounded to live failures
- when adjacent failures appear outside the approved cluster, open explicit follow-up issues instead of silently absorbing them into the execution issue
- if PR CI remains red for unrelated repo debt, grep the matrix logs for the original signatures and record evidence that those signatures are gone across all relevant jobs
- only declare the issue materially complete when the approved failure signatures are removed or intentionally converted into tracked skips, even if unrelated checks still fail

### 8) Background `claude -p` worktree runs can implement successfully but still be blocked from validation/commenting by repo-local allowlists
Observed in worldenergydata cost-wave execution (#335/#338/#337):
- delegated/subagent launch was not reliable for the parallel wave, so execution switched to direct background `claude -p` runs in isolated worktrees
- Claude finished the code changes, but the repo-local `.claude/settings.json` allowlist blocked commands like `uv run`, `python -m pytest`, `pytest`, and `gh issue comment`
- the worker logs asked for approval to run those commands even though the implementation itself had completed
- closeout still succeeded by running validation and GitHub comments centrally from Hermes after inspecting the worktree diff and worker log

Mitigation:
- for parallel worktree waves, treat background `claude -p` as an implementation engine, not necessarily the authority for final validation or GitHub reporting
- after each worker exits, inspect three things before trusting the run:
  - `git status --short` / changed files in the worktree
  - the worker log for any approval-blocked commands
  - targeted tests run centrally from Hermes in the same worktree
- if the worker was blocked on `pytest`, `uv run`, or `gh`, do not rerun the whole agent immediately; keep the produced diff, validate it centrally, then commit/push/comment from Hermes
- post an issue note when execution ownership changes (for example: delegated worker timed out, switching to direct background Claude; worker could not comment, so closeout was posted centrally)
- verify pre-existing regression blockers explicitly instead of treating them as worker failures; in this run a planned regression target referenced a module absent on current main, so the right outcome was: document blocker, prove it is pre-existing, and keep the issue-scoped patch bounded
- if this allowlist pattern is expected in a repo, prefer a two-layer plan from the start:
  - worker owns code/test-writing inside the isolated worktree
  - Hermes owns final validation, commit/push, and GitHub comments unless the repo settings explicitly allow those commands

### 8b) Parallel approved worktrees can still produce later PR merge conflicts through shared export/barrel files
Observed in worldenergydata cost-wave landing:
- #335, #337, and #338 were executed in separate worktrees and validated independently
- after #335 merged first, #337 became `DIRTY` at PR level because both branches modified `src/worldenergydata/cost/data_collection/__init__.py`
- the original execution wave had serialized #337 after #335 for implementation ownership, but the later PR-merge step still required an explicit rebase onto updated `origin/main`
- resolving the conflict correctly required preserving both surfaces in the barrel/export file, then rerunning a combined targeted suite (`test_disclosure_ingest_contract.py`, `test_linkage.py`, `test_calibration_schema.py`) before force-pushing the rebased branch

Mitigation:
- when parallel/semi-parallel issue branches touch the same package export file, `__init__.py`, registry file, or shared manifest, assume the merge stage may still serialize even if implementation work was isolated
- before merging the second/third PR in a wave, inspect `gh pr view <n> --json mergeStateStatus` and be ready to rebase the branch onto current `origin/main`
- resolve shared export conflicts by composing both validated surfaces, not by picking one side mechanically
- after rebase conflict resolution, rerun a combined targeted validation set that covers:
  - the branch's own new tests
  - the already-merged adjacent boundary tests touched by the shared file
- if the rebased branch was already pushed, use `git push --force-with-lease` and document that the force-push was only to land the conflict-resolved, revalidated branch
- treat PR mergeability as a separate verification gate from worktree-local implementation success

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
