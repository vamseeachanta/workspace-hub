# Archived Skill: `background-claude-worktree-absolute-path-launch`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/background-claude-worktree-absolute-path-launch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/background-claude-worktree-absolute-path-launch`
Consolidation date: 2026-04-29

---

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

## Hermes background-process launch rule

When launching a Claude worker from Hermes, do **not** wrap the shell command with `nohup`, trailing `&`, `disown`, or `setsid` in a foreground `terminal()` call. Hermes rejects shell-level background wrappers and cannot track them reliably.

Use the tool's native background mode instead:

```text
terminal(
  background=true,
  notify_on_complete=true,
  workdir="/abs/path/to/worktree",
  command="claude --print --dangerously-skip-permissions < /abs/path/to/prompt.md"
)
```

For approved issue implementation/landing work where a user asks to "use a subagent", prefer this real background Claude process over `delegate_task`; it writes to the intended checkout and can commit/push, while `delegate_task` may lose repo writes. First verify the issue number exists before dispatching; if the requested number is missing but the current active issue is obvious, state the correction in the worker prompt and proceed only on the verified active issue.

## Verification step

Immediately poll the background process once after launch.

Healthy early signal:
- process status is `running`
- no immediate `No such file or directory` output

Failure signal:
- process status is `exited`
- output preview shows missing prompt path or missing log path

Also persist a small run manifest immediately after launch (for example `logs/overnight/<run>/RUNNING.md` or a shell transcript) with:
- issue / terminal mapping
- Hermes process session ID
- OS PID, if available
- prompt file path
- log file path
- expected result artifact path

Hermes `process(action="list")` can return an empty process list even while direct polling by a known `session_id` still reports `running`. Treat the launch-returned session IDs as authoritative and poll them directly. Do not relaunch solely because `process list` is empty or because Claude logs are still zero bytes; first check direct poll, OS PID liveness, and expected result artifact creation.

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
