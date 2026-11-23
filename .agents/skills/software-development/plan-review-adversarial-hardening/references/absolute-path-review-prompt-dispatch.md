# Archived Skill: `absolute-path-review-prompt-dispatch`

Original path: `/home/vamsee/.hermes/skills/software-development/absolute-path-review-prompt-dispatch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/absolute-path-review-prompt-dispatch`
Consolidation date: 2026-04-29

---

---
name: absolute-path-review-prompt-dispatch
description: Prevent adversarial review dispatch failures caused by relative prompt paths, superseded background sessions, and stale completion notices when launching Codex/Gemini review jobs.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [review, codex, gemini, background-processes, prompt-packaging, governance]
---

# Absolute-Path Review Prompt Dispatch

Use when launching adversarial plan/code reviews through background `codex exec` or `gemini exec` jobs.

## When this skill applies
- You write a review prompt to `.planning/quick/*.md`
- You launch Codex/Gemini in background mode with `terminal(background=true, pty=true)`
- You need review artifacts to remain trustworthy even if an earlier dispatch attempt fails

## Core problem
A review prompt file can exist in the repo, but a background shell may still fail to resolve a relative path like:

`codex exec "$(cat .planning/quick/review-342-prompt.md)"`

Observed failure:
- `cat: .planning/quick/review-342-prompt.md: No such file or directory`

This can happen even when the file exists under the intended workdir. Once you recover and relaunch successfully, Hermes may still deliver stale completion notices for the earlier failed session.

## Reliable pattern

### 1. Write the prompt into the real workspace
Use `terminal()` or another real-filesystem write path so the shell can read it.

### 2. Verify existence before dispatch
Run a real-shell check such as:
- `pwd`
- `find . -maxdepth 3 -type f | grep 'review-342'`
- `ls -la .planning .planning/quick`

### 3. Launch with absolute paths
Prefer absolute prompt and output paths:

```bash
codex exec "$(cat /abs/path/to/review-342-prompt.md)" \
  2>&1 | tee /abs/path/to/review-342-codex.out

gemini exec "$(cat /abs/path/to/review-342-prompt.md)" \
  2>&1 | tee /abs/path/to/review-342-gemini.out
```

This avoids cwd drift and ambiguous shell context in background runs.

### 4. Treat the first successful recovered run as canonical
If the original run fails and you relaunch:
- kill the failed process if still running
- save artifacts only from the recovered canonical run
- ignore later stale completion notices from superseded sessions

### 5. Record unavailable providers explicitly
If Gemini/Codex never yields a substantive review, save a canonical artifact with:
- verdict: `UNAVAILABLE`
- concrete failure reason
- raw log path
- operational decision taken

## Minimal recovery workflow
1. Background run fails with relative-path `cat` error
2. Confirm prompt file actually exists on disk
3. Kill the failed background session
4. Relaunch with absolute prompt path + absolute tee path
5. Wait/poll the new session only
6. Save the canonical review artifact(s)
7. Ignore stale system completion messages for the abandoned session

## Pitfalls
- Relative prompt paths can fail in background shells even when the repo workdir looks correct
- A stale completion notification can arrive after you already saved the real review result
- Raw background logs are not the durable artifact; always write the final canonical review file under `scripts/review/results/`

## Good signs
- `find`/`ls` show the prompt file before launch
- background command uses absolute paths for both `cat` and `tee`
- later system notifications do not change the already-saved canonical outcome
