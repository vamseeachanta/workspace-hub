> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-12
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_multi_session_swarm.md

---
name: Multi-session /whats-next swarm — pattern, recovery, and arbitration
description: Two or more concurrent Claude Code sessions running /whats-next on the same machine produce healthy non-colliding plan work; the wip-label gate prevents same-issue collision and auto-sync arbitrates push contention. Don't block, coordinate.
type: feedback
originSessionId: bdc56a6b-6852-40d5-b0af-66c0a71a60de
---
When you /whats-next on ace-linux-1, a second session may be doing the same thing in parallel (e.g., `/tmp/agent-wt` on `agent-dispatch/2026-05-02-whats-next-v2`). Treat this as a healthy operational pattern, not a contention bug.

**Why:** Observed 2026-05-02: two /whats-next sessions ran simultaneously on ace-linux-1. Each picked 5 disjoint issues (the `wip:ace-linux-1` label race prevents same-issue collision). Both produced valid plans. Pushes arrived in any order; auto-sync rebased the loser. Net result: 13 plans landed at `status:plan-review` in one window — better throughput than a single session would achieve.

**How to apply:**

1. **At session start** check `git worktree list` for `/tmp/agent-wt` or `agent-dispatch/*` branches. These are concurrent /whats-next or similar workflows. Note them; don't kill them.
2. **Issue selection** — the wip-label fetch already filters claimed issues. Don't second-guess the filter.
3. **Push contention** — if `git push` returns `[rejected] (fetch first)`, that's the other session's commit landing first. Fetch, rebase, push again. Per `feedback_autosync_silent_pusher`, do NOT retry naively — auto-sync may have already pushed your commit under a different SHA.
4. **SHA rewrites are normal** — your local `be0658303` becomes `b79f47ed6` after rebase. The README rows reference plan files by path, not SHA, so they're stable. Don't add commit SHAs to plan rows.
5. **Stash recovery** — if `git stash pop` conflicts on a `.claude/state/` file, take origin's version (`git checkout HEAD -- <file>`). The non-conflicting parts of the stash apply automatically; the stash stays preserved for safety. Per `feedback_stash_caret_3_for_untracked`, never `git stash drop` until you've verified the high-value content is on origin.
6. **Cross-validate before filing follow-up issues** — a defect "discovered" by an agent in one session may be already-resolved by the other session before you finish your investigation. Diff against current HEAD (`git diff stash@{0}^ stash@{0} -- <file>` then `diff <(git show HEAD:<file>) <(git show stash@{0}:<file>) | wc -l` — 0 means redundant) before assuming the stash content is unique work.

**Anti-pattern to avoid:** Filing 4 GitHub issues for "side channel discoveries" without reproducing them in the post-merge state. Today's investigation found 3 of 4 discoveries were not-reproducible, already-documented, or already-fixed by parallel work. Filing them would have been performative churn.

**Operational rule:** Healthy concurrency means accepting some friction (rebase, SHA rewrites, brief stash) instead of trying to serialize everything. The friction is cheaper than the productivity loss of forcing single-threaded session usage.
