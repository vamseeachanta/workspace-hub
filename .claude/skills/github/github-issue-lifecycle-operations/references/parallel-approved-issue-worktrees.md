# Archived Skill: `parallel-approved-issue-worktrees`

Original path: `/home/vamsee/.hermes/skills/software-development/parallel-approved-issue-worktrees`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/parallel-approved-issue-worktrees`
Consolidation date: 2026-04-29

---

---
name: parallel-approved-issue-worktrees
description: Launch approved GitHub issue implementation in parallel using isolated git worktrees, committed execution-pack prompts, local plan-approved markers, and direct background Claude runs when delegate_task workers are unreliable for real repo writes.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [parallel-execution, git-worktree, claude-code, github-issues, plan-approved, zero-contention]
related_skills:
  - gh-work-execution
  - overnight-parallel-agent-prompts
  - git-worktree-workflow
---

# Parallel Approved Issue Worktrees

Use this when:
- multiple GitHub issues are already `status:plan-approved`
- the streams are file-disjoint or can be serialized by ownership waves
- you want real implementation work to start now
- `delegate_task` workers are too unreliable/slow for repo writes or time out

## Why this exists

In live use, a well-designed approved execution wave still failed when launched through `delegate_task` subagents: both workers timed out before returning usable summaries. The reliable fallback was to run Claude directly in isolated git worktrees with committed prompt artifacts and local plan-approval markers.

This pattern gives:
- real repo writes in the intended checkout
- explicit zero git contention
- auditable prompt artifacts
- easier monitoring/recovery than delegated hidden sandboxes

## Core pattern

### 1. Commit the execution pack first
Before launching workers, commit and push the shared execution pack on `main` so every worktree can read the same immutable prompt files.

Typical artifacts:
- `docs/plans/execution-packs/<date>-approved-<wave>/master-plan.md`
- `docs/plans/execution-packs/<date>-approved-<wave>/execution-readme.md`
- `docs/plans/execution-packs/<date>-approved-<wave>/stream-<issue>.md`

### 2. Create one worktree per parallel stream
Example:
```bash
git worktree add -b issue-335-exec /mnt/local-analysis/worktrees/repo-335 origin/main
git worktree add -b issue-338-exec /mnt/local-analysis/worktrees/repo-338 origin/main
```

Rules:
- one issue/stream per worktree
- each worktree gets its own branch
- do not share owned files across concurrently running worktrees
- before creating a new worktree, check whether a clean existing issue-specific worktree already exists and can be reused

Live-use recovery rule:
- `git worktree add ...` can time out during the checkout/update phase even though the worktree was actually created successfully.
- If the add command times out, do NOT blindly retry with the same path/branch.
- First inspect:
  - `git worktree list`
  - whether the target directory now exists
  - `git status --short`, branch name, and HEAD inside that target worktree
- If the worktree exists and is clean, reuse it.
- Only remove/recreate it if the checkout is incomplete or dirty in a way you cannot trust.

Corrupt-worktree fallback learned in live use:
- A timed-out `git worktree add` can leave a target directory and branch behind while the git metadata under `.git/worktrees/<name>` is missing/corrupt. Symptom: `fatal: not a git repository: .../.git/worktrees/<name>` when running `git worktree list` or `git status` inside the target.
- Recovery sequence:
  1. Confirm the target directory exists and the branch exists: `test -d <path>` and `git branch --list <branch>`.
  2. Remove the broken target directory: `rm -rf <path>`.
  3. Delete the leftover branch if it only came from the failed worktree attempt: `git branch -D <branch>`.
  4. If repeated `git worktree add` is slow/risky in a very large repo, use an isolated shared clone instead: `git clone --shared --branch main <repo-url> <path>`.
  5. In the clone, create/commit the local `.planning/plan-approved/<issue>.md` marker before launching the worker.
- Treat the shared clone as equivalent isolation for a single issue lane: still use absolute prompt/log paths, a dedicated branch before push, and the same owned/read-only/forbidden path contract.

### 3. Add local plan-approved markers inside each worktree
If local hooks enforce `.planning/plan-approved/<issue>.md`, create and commit the marker in the exact worktree that will perform writes.

Example:
```bash
mkdir -p .planning/plan-approved
printf 'Issue #335 plan approved via GitHub label by user on YYYY-MM-DD.\n' > .planning/plan-approved/335.md
git add .planning/plan-approved/335.md
git commit -m "chore(planning): approve issue #335 for execution"
```

Why:
- GitHub `status:plan-approved` alone may not satisfy local hooks
- the marker must exist in the same checkout that writes files
- committing it avoids freshness/self-approval gate failures mid-run

### 4. Post GitHub execution-start comments
For each stream, post a concise comment describing:
- wave/stream name
- isolated worktree execution
- zero-overlap guarantee
- whether another stream is running in parallel

### 5. Launch Claude directly in each worktree
### 5. Launch Claude directly in each worktree
Use the committed stream prompt file as the positional prompt argument, not stdin.

Example:
```bash
PROMPT=$(< /path/to/repo/docs/plans/execution-packs/<wave>/stream-335.md)
cd /path/to/.worktrees/repo-335
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-turns 80 \
  "$PROMPT" </dev/null | tee .claude-stream-335.log
```

Critical launch guardrail learned in live overnight runs:
- when launching from worktrees, use **absolute paths** for both the prompt file and the log file in the shell command, even if the process `workdir` is already set to the target worktree
- create the log directory with an absolute path too when the worktree is nested or when `tee` writes outside the immediate cwd assumptions
- if you use a relative path like `.planning/quick/stream.md` and the shell reports `No such file or directory` even though the file exists, relaunch with `/absolute/path/to/.planning/quick/stream.md`
- similarly, a lane can complete successfully while `tee` exits non-zero because the target log path was relative/nonexistent; treat that as launcher/logging failure first, not task failure

Safer pattern:
```bash
PROMPT=$(< /absolute/path/to/worktree/.planning/quick/stream.md)
mkdir -p /absolute/path/to/worktree/logs
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-turns 80 \
  "$PROMPT" </dev/null | tee /absolute/path/to/worktree/logs/stream.log
```

Important launch hardening learned in live use:
- Prefer absolute paths for both the prompt file and the log file when launching unattended background Claude runs from worktrees.
- A relative prompt read like `.planning/quick/foo.md` can fail with `No such file or directory` even when the file exists in the worktree, especially when the launcher shell/session context is not exactly what you expect.
- Safer pattern:
```bash
PROMPT=$(< /absolute/path/to/worktree/.planning/quick/stream-335.md)
claude -p ... "$PROMPT" </dev/null | tee /absolute/path/to/worktree/logs/stream-335.log
```
- After launch, immediately poll the tracked process once. If it exits instantly with a missing-prompt error, relaunch with absolute paths rather than debugging the worktree contents first.

Critical launch detail learned in live overnight use:
- When launching from background shell commands inside worktrees, prefer **absolute prompt-file paths** in the `PROMPT=$(< ...)` substitution instead of relative paths like `.planning/quick/...`.
- We observed a failure mode where the prompt file definitely existed in the target worktree, but the background shell still errored with `No such file or directory` when using the relative path. Re-launching with the absolute path to the same file succeeded immediately.
- Recommended pattern:
```bash
PROMPT=$(< /absolute/path/to/worktree/.planning/quick/issue-335-prompt.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-turns 80 "$PROMPT" </dev/null | tee /absolute/path/to/worktree/logs/issue-335.log
```
- After launch, poll the process once. If it exits quickly with a missing-prompt error, retry immediately with absolute prompt and log paths before assuming the worktree or prompt generation failed.

Worktree-local prompt pattern:
```bash
PROMPT=$(< /absolute/path/to/.planning/quick/issue-335-overnight-prompt.md)
claude -p --permission-mode acceptEdits --no-session-persistence \
  --output-format text --max-turns 80 "$PROMPT" </dev/null | tee logs/issue-335.log
```

Why:
- in live overnight worktree launches, relative prompt paths failed with `No such file or directory` even though the prompt files existed in the target worktree
- switching to absolute prompt paths fixed the launch immediately

Recommended flags:
- `--permission-mode acceptEdits`
- `--no-session-persistence`
- `--output-format text`
- close stdin with `</dev/null>`
- log to a worktree-local file

### 6. Monitor and serialize any conflicting follow-on stream
If a later stream shares a file/path with an active stream, keep it queued.

Typical pattern:
- Wave 1: run streams A and B in parallel because they are disjoint
- Wave 2: run stream C only after A finishes because A and C both own `src/.../__init__.py`

### 6.5 Log-path guard for nested repos and deep worktrees
When launching unattended Claude runs with `tee`, create the exact target log directory using an absolute path before the run starts.

Observed failure mode:
- the worker command used `mkdir -p logs && ... | tee /abs/path/to/logs/run.log`
- in a nested repo/deep worktree, the absolute `.../logs/` directory did not already exist even though relative `logs/` did
- `tee` failed with `No such file or directory`, the overall process exited non-zero, but the Claude run itself still completed substantial work

Safe launch pattern:
```bash
mkdir -p /abs/path/to/worktree/logs
PROMPT=$(< /abs/path/to/prompt.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-turns 80 \
  "$PROMPT" </dev/null | tee /abs/path/to/worktree/logs/run.log
```

Operational rule:
- treat `tee`/log-path failures separately from task success
- if the process exits non-zero but the terminal output or GitHub comment shows the task completed, classify it as a launcher/logging failure first, not an implementation failure
- after any non-zero exit, inspect the worktree state and issue comments before rerunning the lane

## Handoff template

Each stream prompt should include:
- issue number and URL
- owned paths
- read-only paths
- forbidden paths
- exact TDD targets
- regression boundary tests
- implementation rules
- closeout requirements
- explicit instruction not to close the issue

## Monitoring checklist

For each running worker:
- check process liveness
- check target worktree `git status --short`
- check whether expected test files/source files appear
- treat empty logs cautiously; Claude logs can stay buffered for a while
- if a worker times out or stalls, inspect the worktree before killing it

## Pre-dispatch live-state filter (important)

Before launching an approved-issue overnight wave, verify each candidate issue is still a real implementation target right now.

Required checks per issue:
- issue is still OPEN (`gh issue view <n> --json state,labels`)
- issue still has `status:plan-approved`
- local `.planning/plan-approved/<issue>.md` marker exists in the exact worktree/checkouts that will write
- issue is not already satisfied by an existing branch/commit/worktree outcome
- owned paths are still disjoint from the other selected streams
- if the issue is a prerequisite contract for child issues, verify the contract's exact locked fields on `origin/main` before launching children; do not trust child `status:plan-approved` labels when local plans still contain stale prerequisite/deferred-path language

Practical lesson from live use:
- an issue can remain in your approved pool assumptions while already being CLOSED or already effectively implemented on its dedicated branch/worktree
- in that case, do not waste a write-capable lane on reimplementation; instead run the stream in verification-first mode and post a proof comment if appropriate
- when selecting 4 parallel lanes, expect some approved issues to collapse into `already done / verify only` outcomes rather than producing fresh diffs
- after a prerequisite contract lands, run a read-only child-plan reconciliation wave before implementation; classify each child as `READY_NOW`, `READY_AFTER_PATCH`, or `BLOCKED`, and patch stale plan assumptions such as conditional operator-map host paths, deferred registry filenames, or scorecard-as-authority language before launching write lanes

### Dispatcher/executor drift and sandbox-scope check

A background Claude lane can exit 0 without touching the intended isolated clone when the spawned session is sandboxed to a different root. The worker may correctly detect a concurrent completion and refuse duplicate work, but the dispatcher must still verify where the real commit landed.

Before treating a lane as landed:
- read the worker log for `duplicate-parallel-completion`, sandbox denial, or "no files changed" language
- verify the claimed commit with `git show --stat --name-only <sha>`
- verify which branch contains it: `git branch -a --contains <sha>`
- verify whether it reached `origin/main`: `git merge-base --is-ancestor <sha> origin/main; echo $?`
- if it landed on an integration branch rather than `main`, cherry-pick the validated commit(s) into a clean main-line clone/worktree, re-run targeted tests there, then push `HEAD:main`
- if the contract was missing an exact decision needed by children, make a tiny follow-up commit that locks the decision and updates the test to assert it before starting child work

For future isolated-clone dispatches, ensure the worker's allowed/sandbox directories include the intended clone path (for Claude Code, use the equivalent of `--add-dir` when available) or launch directly from a scope-compatible checkout. Otherwise the prompt may name a path the worker cannot write.
## Post-run recovery when Claude exits on max-turns

If a background Claude worker exits with `Error: Reached max turns (...)`, do not treat the run as a total failure.

Recovery sequence:
1. inspect the worktree immediately:
   - `git status --short`
   - `git log --oneline -5`
   - `git show --stat --oneline -1`
2. determine whether the worker already produced a useful local commit or partial diff
3. run the targeted validation commands yourself from the orchestrator session
4. run an independent adversarial review on the produced diff/commit
5. then choose exactly one outcome:
   - landable: proceed to commit/push/comment flow if validation + review pass
   - blocked: post a GitHub blocker comment summarizing the fresh validation/review findings and leave the issue open
   - no-op: if nothing meaningful changed, treat as failed attempt and relaunch or retire the lane

Practical lesson from live use:
- a max-turns failure can still leave behind a nearly complete local implementation commit
- the correct response is central verification + review, not automatic discard or automatic merge

## Local allowlist / permission fallback

In some repos, Claude can edit files but cannot run the exact validation or GitHub commands you asked for because repo-local settings block commands like:
- `pytest`
- `uv run`
- `python -m pytest`
- `gh`

When that happens, do not discard the worker run.

Use this split-responsibility pattern instead:
1. let the worker finish the implementation inside its isolated worktree
2. read the worker log and inspect the changed files yourself
3. run the planned validation centrally from the parent/orchestrator session in that worktree
4. commit and push from the orchestrator if the worker could not
5. post GitHub validation and closeout comments from the orchestrator

This preserves the implementation value of the worker while moving blocked shell actions to the session that actually has the needed tool permissions.

## Recovery pattern

If a worker stalls:
1. inspect target file diffs in the worktree
2. inspect `git status --short`
3. if intended changes are already present, run the planned tests manually
4. commit/push yourself if the code is sound
5. post the GitHub summary manually

## Nested-repo / cross-repo target guard

When a workspace-hub issue asks for changes in a tier-1 repo such as `digitalmodel`, do not assume a workspace-hub worktree contains the nested repo or that the worker will write to the intended git repository.

Before launching write-capable workers:
- verify the actual target repo root with `git -C <target> rev-parse --show-toplevel`
- verify the active branch in the target repo, not just in workspace-hub
- if the target repo is a separate checkout/submodule/nested repo, create the implementation branch/worktree in that target repo directly
- include the target repo's absolute path in the prompt and validation commands
- after worker completion, run `git status --short`, `git log --oneline -3`, and `git diff --stat origin/main...HEAD` in the target repo, not the parent workspace

Clean PR branch guard:
- before creating a PR, inspect `gh pr view` or `git log origin/main..HEAD` to ensure the branch contains only the intended commits
- if a PR accidentally includes an unrelated prior commit, close it immediately with an explanatory comment
- create a clean branch from `origin/main`, cherry-pick only the validated intended commit(s), re-run targeted tests on the clean branch, push, and open a replacement PR
- post correction comments to the tracking issues with the clean PR URL and superseded PR URL

This prevents a successful implementation wave from producing a polluted PR when the active target repo branch already had unrelated pending work.

## When not to use this pattern
- shared-file changes without a clean serialization plan
- issues that are not already plan-approved
- streams that depend on unresolved decisions from each other
- work requiring user interaction mid-run

## Practical note

This is a better fit than `delegate_task` when the real goal is implementation in the actual repo, especially for approved issue waves where correctness depends on the exact checkout state, hook behavior, and git ownership boundaries.
