# Archived Skill: `absolute-path-review-dispatch-guard`

Original path: `/home/vamsee/.hermes/skills/software-development/absolute-path-review-dispatch-guard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/absolute-path-review-dispatch-guard`
Consolidation date: 2026-04-29

---

---
name: absolute-path-review-dispatch-guard
description: Prevent Codex/Gemini adversarial review dispatch failures caused by relative prompt-file paths and background workdir drift.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [review, codex, gemini, prompt-dispatch, pathing, background-processes]
---

# Absolute Path Review Dispatch Guard

Use this when dispatching adversarial plan/code reviews to Codex or Gemini via `terminal(background=true, pty=true)`.

## Problem
A prompt file can exist in the target repo, but the reviewer process still fails with:
- `cat: .planning/quick/review-<n>-prompt.md: No such file or directory`

This can happen even when:
- the file was successfully written,
- `find`/`ls` confirms it exists,
- and `terminal(workdir=...)` was set correctly.

## Root cause
In background PTY runs, Codex/Gemini may start with an effective working directory different from the requested repo `workdir`.
A real observed case:
- requested workdir: `/mnt/local-analysis/workspace-hub/worldenergydata`
- Codex startup banner reported: `/mnt/local-analysis/workspace-hub`

So relative prompt references like:
- `$(cat .planning/quick/review-342-prompt.md)`
can fail because they resolve from the wrong directory.

## Reliable pattern
1. Write the prompt file to a real repo path.
2. Verify it exists with `find` or `ls`.
3. Dispatch reviewers using absolute paths for:
   - prompt file
   - tee output file

Example:

```bash
codex exec "$(cat /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-342-prompt.md)" \
  2>&1 | tee /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-342-codex.out

gemini exec "$(cat /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-342-prompt.md)" \
  2>&1 | tee /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-342-gemini.out
```

## Verification steps
Before waiting on the process:
1. confirm prompt file exists at the absolute path
2. check initial process output for immediate `cat: ... No such file or directory`
3. if that error appears, kill and relaunch with absolute paths
4. do not assume the issue is the file write itself until you verify the reviewer startup workdir/path resolution

## Artifact rule
When a provider still fails after dispatch:
- save a canonical review artifact anyway
- mark verdict as `UNAVAILABLE` if no substantive review was produced
- include concrete failure reason and raw log path

## When this skill helps
- adversarial plan review waves
- adversarial implementation review waves
- any Codex/Gemini background CLI dispatch that reads prompt files with `$(cat ...)`

## Anti-pattern
Do not use repo-relative prompt paths in background reviewer commands just because `workdir` was set. That assumption is not reliable enough.
