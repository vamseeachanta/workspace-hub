# Archived Skill: `codex-skill-loader-broken-symlink-recovery`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/codex-skill-loader-broken-symlink-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/codex-skill-loader-broken-symlink-recovery`
Consolidation date: 2026-04-29

---

---
name: codex-skill-loader-broken-symlink-recovery
description: Diagnose Codex startup failures in workspace-hub caused by a broken `.claude/skills/skills` symlink and recover without misattributing the failure to issue scope.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [codex, workspace-hub, symlink, troubleshooting, skills-loader]
---

# Codex skill-loader broken symlink recovery

Use when a Codex run in `workspace-hub` fails early with an error like:

- `failed to stat skills entry ... /workspace-hub/.claude/skills/skills (symlink): No such file or directory`

## Why this matters

This failure happens before issue execution meaningfully begins. It is easy to mistake it for a prompt, auth, or issue-scope problem. In practice, the cause can be a broken repo-local symlink under `.claude/skills/`.

## Detection

1. Inspect the failing process log for `codex_core_skills::loader` errors.
2. Check whether the offending path is a symlink:
   - `test -L .claude/skills/skills && readlink .claude/skills/skills`
3. Check whether the symlink target actually exists from the repo root:
   - `test -e .claude/skills/skills && echo exists || echo missing`

Known bad state observed in `workspace-hub`:
- `.claude/skills/skills -> ../.claude/skills`
- from repo root this resolved to a missing path, so Codex failed before execution.

## Recovery pattern

1. Treat the run as infrastructure-blocked, not issue-blocked.
2. Salvage any other active runs first; do not assume all provider runs are invalid.
3. Verify issue completion independently using:
   - `process list/poll/log`
   - `git status`
   - `git log --oneline -n 5`
   - `gh issue view <n>`
4. If another run already completed the issue, clean leftover drift and close via evidence rather than rerunning blindly.
5. Before launching new Codex work from the root repo, verify the symlink path again.

## Practical notes

- A watch-pattern `error` notification from Codex can be a repo bootstrap defect rather than task failure.
- Keep external git verification authoritative; Codex/Claude may still leave unrelated residue like temp prompt files or runtime drift files.
- In workspace-hub, also check for stray edits to `scripts/testing/coverage-results.json` after agent runs and revert them unless explicitly in scope.

## Minimal verification bundle

Use this bundle before deciding to rerun:

```bash
git -C /path/to/worktree status --short
git -C /path/to/worktree log --oneline -n 5
gh issue view <issue> --json number,title,state,comments,url
```

If the issue is already landed/closed, prefer cleanup + closeout over another Codex launch.
