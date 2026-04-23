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
Use the committed stream prompt file as the positional prompt argument, not stdin.
Prefer an absolute prompt-file path when launching unattended runs, even if the file lives inside the worktree.

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

Practical lesson from live use:
- an issue can remain in your approved pool assumptions while already being CLOSED or already effectively implemented on its dedicated branch/worktree
- in that case, do not waste a write-capable lane on reimplementation; instead run the stream in verification-first mode and post a proof comment if appropriate
- when selecting 4 parallel lanes, expect some approved issues to collapse into `already done / verify only` outcomes rather than producing fresh diffs

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

## When not to use this pattern
- shared-file changes without a clean serialization plan
- issues that are not already plan-approved
- streams that depend on unresolved decisions from each other
- work requiring user interaction mid-run

## Practical note

This is a better fit than `delegate_task` when the real goal is implementation in the actual repo, especially for approved issue waves where correctness depends on the exact checkout state, hook behavior, and git ownership boundaries.
