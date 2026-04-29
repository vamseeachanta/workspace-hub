> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_git_switch_discard_changes_pattern.md

---
name: git switch --discard-changes for dirty .claude/state
description: Use `git switch --discard-changes` to switch branches when .claude/state/ is auto-modified; plain `git checkout` aborts silently and `git reset --hard` then retargets the wrong branch
type: feedback
originSessionId: 565cae05-779f-49b7-9225-34a1444fdbef
---
When `.claude/state/corrections/.edit_sequence_counter`, `.claude/state/corrections/.recent_edits`, or `.claude/state/session-signals/*.jsonl` are auto-modified mid-session, use `git switch --discard-changes <branch>` to change branches. Plain `git checkout <branch>` aborts with "Your local changes would be overwritten" but downstream tooling (cp + commit chains, agent dispatchers) doesn't always check the checkout exit code, then proceeds to commit on the still-current branch.

**Why:** Recurred TWICE in the 2026-04-25 planning session (wave-3 and wave-5 cross-branch contamination). In both cases:
1. `.claude/state/` files were auto-dirty
2. Plain `git checkout plan/issue-NNNN-...` aborted silently
3. Subsequent `cp /tmp/plan-drafts/v3.md docs/plans/...` + `git add` + `git commit` ran on the WRONG branch (whichever was checked out previously, often `main` or another plan branch)
4. Recovery required `git revert <sha>` on `main` — see commit `1434f2209 Revert "plan(#2103): v4..."` for the recovery template
5. The "auto-sync as silent pusher" pattern (`feedback_autosync_silent_pusher.md`) compounds this by quietly pushing the contaminated commit before the human notices

**How to apply:**
- Default branch-switch command for ALL plan-branch operations in this workspace: `git switch --discard-changes <branch>` (NOT `git checkout`)
- If you must use `git checkout`, explicitly check `$?` after each call and abort the script on non-zero exit
- After ANY branch switch in a multi-step pipeline, verify `git rev-parse --abbrev-ref HEAD` matches the expected branch BEFORE the next commit
- For agent prompts that dispatch git operations across multiple branches: include an explicit "verify HEAD before commit" guard in the prompt
- Recovery pattern when contamination is detected: `git revert <bad-sha> --no-edit` on `main`, then re-do the work on the correct branch with `git switch --discard-changes` first

**Related:**
- `feedback_autosync_silent_pusher.md` — auto-sync amplifies misplaced commits by pushing before discovery
- `feedback_retry_loop_reset_hazard.md` — `git reset HEAD -- .` in a retry loop has a related class of cross-branch failure mode
- `feedback_multi_agent_commit_serialization.md` — parallel agents touching shared index files race on git lock; the `--discard-changes` pattern is also the safe way to recover from a lost race
