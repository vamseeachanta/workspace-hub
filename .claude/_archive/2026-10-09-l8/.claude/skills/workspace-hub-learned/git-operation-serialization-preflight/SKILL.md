---
name: git-operation-serialization-preflight
description: Before any commit, stash, merge, reset, rebase, or checkout in a multi-agent or shared-checkout environment, run a bounded preflight to detect active git writers and stale index/config locks, then serialize the mutating step under a single-writer guarantee.
version: 1.0.0
category: workspace-hub-learned
tags: [git, concurrency, locks, multi-agent, preflight, serialization, index-lock]
---

# Git Operation Serialization Preflight

Multi-agent workspaces (Claude main + subagents, Hermes batch workers, Codex review helpers, auto-sync daemons, nightly cron) routinely have several git writers active on the same checkout. Without a preflight, mutating git operations collide on `.git/index.lock` / `.git/config.lock`, drop staged work, mislabel commits, or revert another agent's just-landed work. This skill is the standard preflight + serialization wrapper around every mutating git command.

## When to Use

- About to run any of: `git commit`, `git stash push`, `git merge`, `git rebase`, `git reset`, `git checkout <branch>`, `git switch`, `git pull`, `git push` (lock contention is rarer here but possible), `git worktree add/remove`.
- Dispatching N parallel agents where ≥2 will eventually commit on the same checkout.
- About to edit a shared index file (e.g., `docs/plans/README.md`, `MEMORY.md`, planning tracker files) from multiple agents.
- A previous git command was killed, timed out, or hit a tool-budget limit — index/config locks may be stale.
- Auto-sync, scheduled cron, or a background Hermes runner is known to operate on this checkout.

## Source Provenance

- `logs/orchestrator/hermes/session_20260501.jsonl` — session `20260501_075259_54868f` (around line ~431) executed `pgrep -af 'git '` and `stat .git/index.lock` immediately before a skill-directory commit, confirming the preflight is a pre-commit hard precondition in Hermes-driven flows.
- Same log, sessions `20260501_152122_c2a9d7` and `20260501_153626_bc1b96` — repeated `pgrep` + `index.lock` probes before committing skill content, plus secret-scan, before issuing the commit.
- Hard-rule memory `feedback_multi_agent_commit_serialization` (workspace-hub MEMORY.md: "Multi-agent commit serialization") — incident `298d2d729` on 2026-04-20: three parallel plan-revision agents collided on `docs/plans/README.md`; one commit absorbed another's staged edits, degrading attribution.
- Related: `feedback_git_status_lock_storm` (long sessions accumulate 10+ zombie `git status -z -uall` processes blocking commits), `feedback_retry_loop_reset_hazard` (resetting under contention strips staged edits).

## Preflight Procedure

Run all four probes before any mutating git command. Each is bounded and non-mutating.

### 1. Active writer scan

```bash
pgrep -af 'git (commit|merge|rebase|reset|stash push|checkout|switch|pull|push|worktree add|worktree remove)'
```

- Empty output → no active writer; proceed to step 2.
- Non-empty → another agent/session is mid-operation. **Do not proceed.** Options:
  - Wait and re-probe (recommended if the operation is short, e.g., a commit).
  - Switch to a per-agent worktree (`git worktree add .claude/worktrees/<id> <ref>`) so the mutating step lands in an isolated index.
  - Defer the commit phase to a serial dispatcher (see "Serialization patterns" below).

### 2. Status-storm scan (read-only writers can also wedge)

```bash
pgrep -af 'git (status|diff|log|fetch|ls-files)' | head -20
```

If more than ~5 long-running status/diff/log processes accumulate (typical of long Claude sessions issuing background status probes), the commit path can hang on index reads even with no active writer. Two recovery routes:

- `GIT_OPTIONAL_LOCKS=0 git commit ...` — bypasses optional lock acquisition.
- Allow the storm to drain naturally (do not kill the parent agent process; the zombies are children of long-running agent sessions and disappear when their reads return).

### 3. Index-lock inspection

```bash
stat .git/index.lock 2>/dev/null && cat .git/index.lock 2>/dev/null
```

- File absent → safe.
- File present:
  - Read the PID (older Git writes the PID into the lock).
  - Cross-check with `ps -p <pid>` — is that process still alive?
  - If alive: another writer holds the lock legitimately — wait, do not remove.
  - If dead: stale lock. Remove **only** under explicit recovery conditions (no active git process, lock age consistent with the killed command, operator-logged recovery). Never make stale-lock removal a default step in a retry loop — that is the failure mode in `feedback_retry_loop_reset_hazard`.

### 4. Config-lock inspection (branch/worktree mutations only)

```bash
stat .git/config.lock 2>/dev/null
```

`.git/config.lock` warnings during `git branch -d`, `git worktree remove`, or `git remote` mutations follow the same recovery model as index.lock: verify no active git owner, preserve the lock for evidence if needed, remove only under the closeout mutex.

## Serialization Patterns

If the preflight surfaces concurrent writers — or if you are *about* to dispatch N parallel agents that will all need to commit — choose one of:

### A. Centralized commit dispatcher (preferred for plan-batch flows)

Have each agent perform its expensive work (resource intel, edits, `Write` calls) in parallel, but **return its diff or staged file list as output**. The dispatcher then runs `git add <files> && git commit -m '<per-agent-message>'` serially. Inter-commit delay is <2s; the parallelism gain is preserved in the edit phase, and per-agent attribution stays intact.

Memory cross-reference: `feedback_parallel_agent_write_only_pattern` codifies this as the default for workspace-hub.

### B. Per-agent worktrees

```bash
git worktree add .claude/worktrees/agent-<N> <ref>
```

Each agent gets an isolated working tree and index. Commits never collide. Required cleanup: `git worktree remove .claude/worktrees/agent-<N>` after merge/push. Caveat from `feedback_worktree_isolation_large_repo_cost`: on a 33k-file repo, `worktree add` can take minutes and time out; reserve for agents that genuinely must own their commit phase.

### C. Lockfile-guarded serial section

For ad-hoc cases (e.g., a docs commit during an active Hermes session), wrap the mutating block with `flock`:

```bash
flock -x -w 60 .git/serializer.lock -c 'git add <files> && git commit -m "<msg>" && git push'
```

The wait timeout prevents indefinite blocking. `.git/serializer.lock` is a workspace convention, not a Git-native file — it just provides a single coordination point across agent processes on the same host.

### D. Remote-first temporary worktree for non-fast-forward closeout

If a shared `main` checkout has the desired local artifact commit but `git push origin main` is rejected because `origin/main` advanced, do **not** reflexively merge/rebase the whole dirty/divergent checkout. For narrow planning/review closeout, prefer a remote-first worktree:

1. Inspect divergence with `git log --left-right --cherry-pick HEAD...origin/main` and confirm the local commit is a narrow artifact commit.
2. Create a temporary worktree at `origin/main`.
3. Cherry-pick only the intended commit into that worktree.
4. Resolve conflicts only in the intended artifact paths; if unrelated conflicts appear, stop and report.
5. Run the relevant gates in the worktree.
6. Push with `git push origin HEAD:main`.
7. Verify `git ls-remote origin main` matches the pushed commit.
8. Remove the temporary worktree.

This avoids dragging unrelated local-only commits or remote session/config churn into an otherwise narrow closeout. It is especially useful for plan/review artifacts where the remote needs the durable files, but the current checkout is contaminated by parallel-session work.

### E. Absorb remote commits back into a dirty primary checkout

After landing durable artifacts from an isolated reconciliation checkout, the original primary checkout may still be dirty and stale. To absorb the pushed commits without losing unrelated local/session dirt:

1. Run the full writer/lock preflight from this skill.
2. `git fetch origin main` and inspect `git log --left-right --cherry-pick --oneline HEAD...origin/main`.
3. If the local ahead commit is already represented on `origin/main` (for example same subject/content but different SHA), create a named safety stash first: `git stash push -u -m absorb-origin-main-$(date +%Y%m%d-%H%M%S)`.
4. `git reset --hard origin/main` to make the checkout absorb remote commits exactly.
5. Restore only residual dirty-state paths from the stash: runtime logs, still-unclassified review artifacts, and any local files intentionally preserved. Do **not** restore paths that were just committed and pushed.
6. If another remote commit lands during the absorb, inspect touched paths for overlap with current dirt. If no overlap, `git merge --ff-only origin/main`; if overlap, stop and classify instead of forcing a merge.
7. Verify `HEAD`, `origin/main`, and `git ls-remote origin refs/heads/main` all match, then report remaining dirty categories and keep the safety stash until the user approves dropping it.

This pattern is safer than a blind `git rebase origin/main` in shared dirty checkouts because it separates: (a) remote commit absorption, (b) local runtime/noise preservation, and (c) later cleanup classification.

### F. Export-and-drop obsolete safety stashes

When a cleanup/closeout session leaves named safety stashes behind, do not either keep them indefinitely or drop them casually. Treat stash cleanup as a destructive git operation with evidence preservation:

1. Re-run writer/lock preflight before touching the stash stack.
2. Inventory each stash by index, message, date, and SHA.
3. Export patch/stat/name-status/metadata to an off-repo preservation directory before dropping.
4. Classify each stash as `drop`, `preserve`, or `export-only then drop` based on whether unique content is already represented in `HEAD` or is stale runtime/bridge/generated state.
5. Move accidental untracked patch exports out of the repo before final status verification.
6. Record checksums for exported patches and verify the remaining stash list plus `git status --porcelain=v1 --branch`.

Detailed procedure: `references/stash-export-and-drop-cleanup.md`.

### G. Commit post-hook metadata before final clean-state claims

If a mutating operation succeeds but hooks or skill tooling append expected metadata, inspect and commit that follow-up ledger before declaring the checkout clean. Detailed procedure: `references/post-commit-hook-metadata.md`.

## Verification Checklist

Before issuing the mutating git command:

- [ ] If `git status -sb` reports detached HEAD, resolve the intended branch/ref before commit or choose an explicit push ref; see `references/detached-head-closeout.md`.
- [ ] `pgrep -af 'git (commit|merge|rebase|reset|stash push|checkout|switch|worktree)'` returned empty.
- [ ] `.git/index.lock` does not exist, OR its owner process is verified dead AND removal was explicit/logged.
- [ ] `.git/config.lock` (for branch/worktree ops) does not exist or has been recovered the same way.
- [ ] If dispatching ≥2 agents that touch a shared index file: a serialization pattern (A/B/C) is selected before dispatch, not retrofitted after a collision.
- [ ] Auto-sync / Hermes / scheduled cron writer on this checkout has been checked: `feedback_hermes_active_preflight_check` style — if active, switch to a worktree+feature-branch before mutating main.

After the mutating step completes:

- [ ] `git rev-parse HEAD` matches the commit you intended to produce.
- [ ] Immediately re-run `git status --porcelain=v1 --branch` after every commit/merge/push; do not assume hooks left the tree clean.
- [ ] If hooks or skill tooling generated follow-up metadata (for example `logs/orchestrator/hermes/skill-patches.jsonl`), inspect it, classify it as expected ledger/runtime state, and commit it separately before claiming final clean-state.
- [ ] `git status --short` reflects the expected post-state (clean for a finished commit, or the residual untracked you decided to defer).
- [ ] If you pushed: `git ls-remote origin <branch>` matches local `HEAD` (catches the auto-sync race documented in `feedback_merge_race_silent_revert` and `feedback_autosync_silent_pusher`).

## Pitfalls

- **Defaulting `rm -f .git/index.lock` in a retry loop.** Strips legitimate concurrent writers' staged work. Use it only as explicit, logged stale-lock recovery (`feedback_retry_loop_reset_hazard`).
- **Treating `pgrep git` as a one-shot check.** A long pipeline can finish between the probe and the mutating command. For batched operations, wrap the whole sequence in `flock` (pattern C) rather than a single upfront probe.
- **Assuming "I'm the only agent" on workspace-hub.** Auto-sync, nightly cron, scheduled Hermes work, and a parallel `/whats-next` swarm can all be writing concurrently — preflight every time on shared checkouts (`feedback_multi_session_swarm`).
- **Killing the parent agent to clear a status storm.** Status-storm zombies are children of the agent; they exit when their reads complete. Killing the parent loses session state.
- **Removing `.git/index.lock` without verifying its owner is dead.** Live writer + lock removal → corrupted index. Always cross-check PID before removal.
- **Skipping the post-mutation push verification.** A successful local commit + push that races with auto-sync can land a silent revert (`feedback_merge_race_silent_revert`); compare local HEAD to `ls-remote` to catch it.
- **Committing validated staged work while detached without selecting a ref.** A detached HEAD can be safe only when you explicitly attach to the intended branch or push to an explicit ref and verify it; see `references/detached-head-closeout.md`.

## Related Patterns

- `feedback_multi_agent_commit_serialization` — origin incident (commit `298d2d729`).
- `feedback_parallel_agent_write_only_pattern` — the dispatcher-serialized pattern as default.
- `feedback_hermes_active_preflight_check` — extends the preflight to Hermes-owned cleanup loops on main.
- `feedback_git_status_lock_storm`, `feedback_retry_loop_reset_hazard` — the two adjacent recurring failure modes this skill prevents.
- `.claude/skills/workspace-hub/worktree-branch-sync-hygiene/SKILL.md` — for the closeout-mutex and stale-lock recovery references this skill points to.
- `.claude/skills/development/artifact-commit-verification/SKILL.md` — post-commit verification companion (this skill is the pre-commit half).
