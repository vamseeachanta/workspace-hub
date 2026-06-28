---
name: feedback_dev_primary_equality_green_is_self_healing
description: "Don't manually chase dev-primary's equality-matrix \"green\" — STALE-CHECKOUT is a lagging, self-healing indicator; chasing it on the shared churning checkout risks clobbering concurrent cron/session work"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dbfda1bf-331e-48e3-b106-9e6362c91fe4
---

2026-06-26 (reconcile-ecosystem session): dev-primary's equality-matrix column reads **STALE-CHECKOUT** whenever its tree is dirty OR local `main` is behind `origin/main`. This interactive box is *always* a little of both — cron auto-syncs + merges keep `origin/main` advancing, and the collector (`reconcile-ecosystem.sh --apply --equality` / `equality-matrix-cron.sh`) **regenerates provider dashboards on every run**, re-dirtying the tree it just measured. So the "green" is a point-in-time snapshot that decays immediately.

**Why:** I burned many cycles stash→pull→recollect trying to green it; each recollect re-dirtied the tree, and `origin/main` kept moving, so it flipped back to STALE every time. Worse, the workspace-hub checkout had **concurrent activity** (a parallel session/cron mid-work on skill-currency + equality-infra files; local main diverged ahead 1 / behind 2, commit #3249) — more stash/pull/reset would have clobbered it (see [[feedback_amend_clobbers_parallel_branch_in_shared_checkout]], [[feedback_autorun_clobbers_subagent_worktree_commits]]).

**How to apply:** Fix the *substantive* drift (commit real fixes via PR — e.g. a stale generated runtime file) and STOP. Let the scheduled `equality-matrix-cron` re-green dev-primary from a clean, freshly-pulled state. Treat the matrix cell as a lagging indicator, not the work. NEVER manually stash/pull/reset workspace-hub to chase the green when the tree shows unexplained modified source files = a sign of a concurrent session. The real green lever for cross-machine NO-MAJORITY/DIVERGES rows is **operator-only**: run the Windows collectors (`scripts\windows\equality-report.ps1`) so 4/4 boxes report — a Linux box can't collect Windows evidence.
