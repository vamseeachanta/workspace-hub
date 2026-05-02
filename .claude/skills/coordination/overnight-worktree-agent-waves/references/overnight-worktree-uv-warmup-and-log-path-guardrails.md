# Archived Skill: `overnight-worktree-uv-warmup-and-log-path-guardrails`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-worktree-uv-warmup-and-log-path-guardrails`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-worktree-uv-warmup-and-log-path-guardrails`
Consolidation date: 2026-04-29

---

---
name: overnight-worktree-uv-warmup-and-log-path-guardrails
description: Prevent false stalls and missing-log failures in overnight Claude worktree batches by pre-warming uv environments, using exact log-path directory creation, and interpreting buffered logs correctly.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [overnight, claude, worktrees, uv, logging, batch-execution]
---

# Overnight worktree uv warmup and log-path guardrails

Use when launching unattended Claude runs in fresh worktrees, especially for Python repos that rely on `uv` and for nested repos like `digitalmodel`.

## Trigger
- Overnight/background Claude batch in isolated worktrees
- Fresh worktree or fresh workspace
- Commands will run `uv run ...`
- You want reliable log capture with `tee`

## Problem patterns observed

1. `uv` first-run warmup can look like a hang
- In a fresh worktree, the first meaningful `uv run ...` can spend 55-60 minutes compiling/importing before useful output appears.
- This can make a healthy worker look blocked or dead.
- We observed this in the `digitalmodel` overnight lane: the real work eventually completed and all tests passed, but the first-use warmup consumed most of the apparent runtime.

2. Buffered Claude logs can stay empty for a long time
- `claude -p ... | tee <log>` may produce no visible log growth for a long period even when the process is healthy.
- Empty logs are not sufficient evidence of failure.

3. `tee` can fail if you create the wrong log directory
- `mkdir -p logs && ... | tee /abs/path/to/logs/run.log` is unsafe if the actual `tee` target differs from the cwd-relative `logs/` you created.
- In the `digitalmodel` overnight lane, the command completed the task but still exited non-zero because `tee` could not open the intended log path.

## Recommended launch pattern

### 1. Pre-warm uv in the exact worktree
Before the real workload, run a disposable warmup in the same worktree:

```bash
uv run python -c "pass"
```

Use this especially when:
- the worktree is fresh
- the repo is large
- the lane is test-heavy
- the first useful command is a long pytest run

### 2. Create the exact log directory for the exact log file
Do not rely on `mkdir -p logs` unless `tee` writes to `./logs/...` in that same cwd.

Safe pattern:

```bash
LOG=/abs/path/to/logs/run.log
mkdir -p "$(dirname "$LOG")"
PROMPT=$(< /abs/path/to/prompt.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-turns 80 \
  "$PROMPT" </dev/null | tee "$LOG"
```

### 3. Monitor health by process state and artifacts, not log growth alone
Preferred signals:
- background PID still alive
- expected output/result artifacts appear
- worktree `git status --short` changes as files are written

Only treat the run as failed after checking those, not merely because the log is empty.

## Recovery pattern when a run exits non-zero after doing useful work
If the background command ends with a logging-related error:
1. inspect the worktree, not just the exit code
2. check `git status --short`
3. inspect target files and test outputs
4. verify whether the actual task completed despite the shell/logging failure
5. if yes, continue from the resulting repo state and post the correct GitHub update

## Practical rule
For overnight worktree batches:
- pre-warm `uv`
- use absolute log paths
- create the exact parent directory of the log file
- do not interpret empty Claude logs as immediate failure

These guardrails reduce false hang diagnoses and prevent task-success/logging-failure confusion in unattended runs.
