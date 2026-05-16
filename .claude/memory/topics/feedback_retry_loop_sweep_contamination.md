> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-16
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_retry_loop_sweep_contamination.md

---
name: retry-loop-sweep-contamination
description: "retry-loop commits under auto-sync contention can sweep in parallel-session staged files, mislabeling the contaminated commit under your message"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 88b3956a-7a96-4346-9dbe-674f5fb0b4e9
---

Retry-loop bash commits under parallel-session / auto-sync contention can sweep in unrelated staged files, contaminating the commit under your label.

**Why:** 2026-05-15 incident — committing 4 plan revisions (#2708-#2711). First attempt blocked by skill-content scanner false-positive in unrelated comfyui SKILL.md. Retry loop (with sleep + rm -f index.lock) succeeded on attempt 2 — but between attempts a parallel session (auto-sync or Hermes) had `git add -A`-staged ~75 unrelated state files (`.claude/memory/`, `.claude/state/`, drift summaries, session signals, candidate ledgers). My commit `9d9c6e4c7` labeled "revise plan #2708" actually contained 76 files / 2895 insertions / 1011 deletions. Auto-sync pushed to origin/main before I noticed. Recoverable but ugly; reverting would have stripped legitimate parallel-session work.

**How to apply:** For commits on a repo with active auto-sync or parallel Claude sessions, use the positional pathspec form `git commit -m "..." -- <specific-file>`. Per git-commit(1): "When pathspec is given on the command line, commit the contents of the files that match the pathspec without recording the changes already added to the index." Plans #2709/#2710/#2711 (2026-05-15 r1 revision commits 7cab67c99, ae4f1f0ec, fe9b96556) all committed cleanly this way: 1 file each, no sweep. **Syntax order matters**: `--` separator goes AFTER `-m "msg"` and BEFORE pathspec. `git commit -- <file> -m "msg"` treats `-m` and message as additional pathspecs and fails with "did not match any file(s) known to git".

Related: [[feedback_retry_loop_reset_hazard]] (inverse — strips staged edits instead of sweeping in), [[feedback_autosync_silent_pusher]] (the silent push that made the contamination unrecoverable), [[feedback_multi_agent_commit_serialization]] (broader pattern), [[feedback_git_status_lock_storm]] (zombie status processes that trigger the retry loop in the first place).
