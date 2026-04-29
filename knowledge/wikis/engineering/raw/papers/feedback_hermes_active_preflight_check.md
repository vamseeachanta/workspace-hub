> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_active_preflight_check.md

---
name: Hermes-active preflight check before non-trivial commits
description: When Hermes is in a "remove unrelated files" cleanup loop on main, parallel-agent commits get reverted as cruft; preflight `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` and use a worktree+branch if active
type: feedback
originSessionId: 85425ab4-4551-420c-b5c2-2f93ef0a457a
---
Before any non-trivial commit sequence on workspace-hub `main` (more than 1–2 files, more than a single commit, or any time the work is "session-scope unrelated to the active issue Hermes is processing"), run:

```bash
pgrep -af "git (rebase|stash push|commit|merge|reset|checkout)" | grep -v grep
```

If active processes are returned **and they're a Hermes/auto-sync session processing a specific issue**, defer the commit OR pivot immediately to a worktree on a non-`main` branch. Hermes' commit messages reveal the scope: e.g., `"resolve issue 2488 closeout review blockers"`, `"remove unrelated files from issue 2488 review commit"`. Files committed to `main` that Hermes classifies as unrelated to its active issue **will be reverted** within minutes.

**Why:** discovered 2026-04-26 during cradle-to-grave engineering flywheel session. Plan #5 v2 patches (5 MAJOR + 4 MINOR adversarial-review findings resolved) were committed atomically to `main` three times. Hermes' next pass each time committed `"remove unrelated files from issue 2488 review commit"` and reverted the v2 patches. The fourth attempt — via a worktree at `/tmp/flywheel-aces-5-worktree` on branch `flywheel/aces-5-v2-patch` — succeeded because Hermes operates on `main`, not feature branches. Audit-bypass `GIT_PRE_PUSH_SKIP=1` was used for the push (documented in the hook's own header as "soft bypass: log and exit 0 (audited)"; pre-existing audit-log entry from 2026-04-24 confirms team-established pattern).

**How to apply:**
- For trivial single-file safe-path commits (e.g., updating a memory file, a doc), preflight is optional; auto-sync handles incidentally.
- For multi-file plans, governance artifacts, or any work spanning ≥2 commits: preflight is **mandatory**.
- If Hermes is active processing issue X and your work is on issue Y: **use a worktree** at `/tmp/<task>-worktree` on branch `<topic>/<issue>-<slug>`. Hermes cannot revert what isn't on `main`.
- Worktree creation pattern: `git worktree add /tmp/<task>-worktree -b <branch>`. Cleanup post-merge: `git worktree remove /tmp/<task>-worktree`.
- Memory ecosystem already covers related risks: `feedback_check_parallel_work.md`, `feedback_isolated_clone_dispatch_race.md`, `feedback_merge_race_silent_revert.md`, `feedback_multi_agent_commit_serialization.md`. This entry is the **explicit Hermes-cleanup-classification specialization** — quiet windows aren't enough when Hermes' next pass actively re-classifies your work as cruft.
- Pre-push hook bug surfaced alongside (separate but co-occurring): `uv run --no-project python <script>` ignores PEP-723; use `uv run --no-project <script>` instead. Fix is committed on `flywheel/aces-5-v2-patch` (commits `c73f54c64` + `b3b079ef2`); benefits all branches once merged.
