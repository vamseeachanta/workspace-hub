---
name: background-claude-worktree-absolute-path-launch
description: Prevent overnight/background Claude worker launch failures in git worktrees by using absolute prompt/log paths and immediate post-launch polling.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [claude, background, worktree, overnight, launch, troubleshooting]
---

# Background Claude Worktree Absolute-Path Launch

Use when:
- launching `claude -p` in the background via Hermes `terminal(background=true)`
- running overnight worker waves from a git worktree
- the prompt file lives under `docs/plans/overnight-prompts/...`

## Symptom

The background process exits immediately with an error like:

```text
bash: docs/plans/.../worker-N.md: No such file or directory
```

This can happen even when `terminal(..., workdir=...)` points at the correct worktree and the prompt file really exists.

## Cause

For unattended/background launches, relative prompt-file or log-file paths are less reliable than they look. In a worktree launch, shell expansion / file redirection may resolve the relative path unexpectedly before the process does useful work.

## Fix

Always use absolute paths for:
1. the prompt file read into `PROMPT=$(< ...)`
2. the `tee` log destination
3. any other launch-critical file arguments

Preferred pattern:

```bash
PROMPT=$(< /abs/path/to/worker.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee /abs/path/to/worker.log
```

## Verification step

Immediately poll the background process once after launch.

Healthy early signal:
- process status is `running`
- no immediate `No such file or directory` output

Failure signal:
- process status is `exited`
- output preview shows missing prompt path or missing log path

## Recovery

If the first launch used relative paths and failed:
1. confirm the prompt file exists with a file search or `read_file`
2. relaunch using absolute prompt and log paths
3. poll again right away before assuming the overnight wave is healthy

## Scope

This is a launch-hygiene fix for planning or implementation waves. It does not replace the other unattended-run requirements:
- `--permission-mode acceptEdits` for write-capable runs
- prompt passed as a positional argument when stdin is closed
- worktree isolation for zero git contention
