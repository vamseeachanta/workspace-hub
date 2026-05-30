# Session handoff — orchestrator consistency (continuation of 2026-05-28)

**Date:** 2026-05-29 · **Repo:** workspace-hub · **No external actions** beyond GitHub issue/PR comments + one authorized live runtime remediation (Hermes SOUL symlink on ace-linux-1, backed up). No emails/posts sent.

Continues `docs/session-handoffs/2026-05-28-orchestrator-consistency-handoff.md`. Umbrella [#2841](https://github.com/vamseeachanta/workspace-hub/issues/2841) (now CLOSED).

## Shipped this session (all merged to main)
| PR | Issue | What |
|----|-------|------|
| [#2861](https://github.com/vamseeachanta/workspace-hub/pull/2861) | #2860 | per-machine Hermes consistency probe (`scripts/readiness/hermes-consistency-check.sh`) |
| [#2863](https://github.com/vamseeachanta/workspace-hub/pull/2863) | #2860 | probe hardening (CRLF-safe SOUL diff, TTY/NO_COLOR guard, ls-remote git-fetch guard, bridge `id:` anchor) |
| [#2868](https://github.com/vamseeachanta/workspace-hub/pull/2868) | #2864 | fix nightly SOUL symlink clobber — single-owner (sync stops touching `~/.hermes/SOUL.md`; `harness-update` re-installs via `install-soul-runtime.sh`) |
| [#2870](https://github.com/vamseeachanta/workspace-hub/pull/2870) | #2847 | leader-failover **Phase 1a** — `dispatch_leader.py` (LeaderState, `may_write_leases` self-fence, `check`, GitLeaderStateStore on a **dedicated ref** via plumbing+CAS), watcher, seed, 19 tests |
| [#2871](https://github.com/vamseeachanta/workspace-hub/pull/2871) | #2847 | leader-failover **Phase 1b** — wire the self-fence into `run_loop` lease origination, opt-in `DISPATCH_ENFORCE_LEADER_FENCE` (default off) |

Issues closed: [#2845](https://github.com/vamseeachanta/workspace-hub/issues/2845), [#2846](https://github.com/vamseeachanta/workspace-hub/issues/2846) (completeness-closed, no CI change — see Hazards), [#2860](https://github.com/vamseeachanta/workspace-hub/issues/2860), [#2841](https://github.com/vamseeachanta/workspace-hub/issues/2841).

## OPEN — next actions

### [#2847](https://github.com/vamseeachanta/workspace-hub/issues/2847) Phase 2 (auto-promotion) — PLANNED, awaiting approval
- Plan on branch **`feat/2847-phase2-plan`** (`docs/plans/2026-05-29-issue-2847-phase2-auto-promotion.md`, commit `27311bd6`); NOT yet a PR.
- Plan-stage adversarial review done → **CHANGES REQUIRED → revised**. **CRITICAL (verified):** auto-promote's no-split-brain guarantee silently depended on `enforce_leader_fence` (a separate default-OFF flag; `is_leader_machine` is hostname-only) → split-brain in default config. Fixed in the plan: fence is now a HARD precondition (`FENCE_REQUIRED` refusal + tests). Review artifact: `scripts/review/results/2026-05-29-plan-2847-phase2-claude-subagent.md`.
- **Next:** USER reviews → (STRONGLY recommended) **Codex cross-review of the plan AND the merged 1a/1b foundation** (highest-stakes: changes live multi-machine leadership; this session's reviews were Claude-subagent-only, degraded T3→1) → approve → implement → Phase 2.
- **Enable runbook (when 1b/2 go live):** the `dispatch-leader-watch --heartbeat` (Phase 1a, cron every 15 min) must bootstrap the `dispatch-leader-state` ref FIRST; only then set `DISPATCH_ENFORCE_LEADER_FENCE=1`; auto-promote (`DISPATCH_ENABLE_AUTO_PROMOTE`) requires the fence on cluster-wide. Both flags default OFF — nothing is live yet.

### [#2864](https://github.com/vamseeachanta/workspace-hub/issues/2864) — fix MERGED ([#2868](https://github.com/vamseeachanta/workspace-hub/pull/2868)) but issue still OPEN
- Needs the completeness close: `gh issue edit 2864 --add-label status:completeness-verified && gh issue close 2864` (agent cannot self-verify).

## Repo / environment state
- Working tree on branch `fix/statusline-codex-quota` (UNRELATED, ~3300 dirty files NOT from this thread — never committed there). All work done in throwaway worktrees off `origin/main` (all removed).
- All session branches pushed + remote-verified. No worktrees of mine remain. `COMPLETENESS_REQUIRE_SEPARATE_CLOSER` still unset (correct).
- Live remediation: `~/.hermes/SOUL.md` on ace-linux-1 re-symlinked to the canonical runtime artifact (stale 4KB copy backed up). **Durable fix is #2868 (merged)**; the interim symlink would have re-drifted at the 01:15 cron until #2868 landed — it has, so it now self-heals.

## Hazards hit (carry forward)
- **Completeness gate (#2798) reopen = freshness/authorized-owner, NOT separate-closer.** The 2026-05-28 handoff misdiagnosed it. The var is opt-in/default-off; the real gate is the verified label applied at/after the last body edit. Read `completeness_gate_check.py` + the label timeline before flipping any `COMPLETENESS_*` var. (memory: `feedback_completeness_gate_reopen_is_freshness_not_separate_closer`)
- **Auto-sync silent pusher + amend/rebase.** Auto-sync pushed my pre-amend commits, so every `git commit --amend`/rebase diverged from the remote branch → push rejected. Reconcile with `--force-with-lease=<branch>:<the-auto-synced-sha>` after verifying it's your own superseded commit. ALWAYS `git ls-remote` to verify push landed.
- **Stale-base merge-race revert.** `main` advanced 4 commits (#2867 #2841-PhaseC) while I worked; my branch's diff vs main showed it *deleting* others' new files → merging would have reverted them. Rebase onto current `origin/main` before every PR and check `git diff --numstat origin/main HEAD` for unexpected deletions.
- **Verify subagent claims + review the merge-target, not a working-tree copy.** One review pass targeted a stale untracked copy of the probe (the PR branch already had the fix). Always diff against the ref that will merge.

## Memory written this session
`feedback_completeness_gate_reopen_is_freshness_not_separate_closer`, `feedback_sync_agent_configs_clobbers_soul_symlink` (root cause of #2864). Index: `MEMORY.md`.

## Recommended resume
1. Close #2864 (one command above).
2. Get a Codex cross-review of the #2847 Phase-2 plan + 1a/1b foundation.
3. On approval, implement Phase 2 (TDD per the plan; the dedicated-ref CAS + concurrency-test harness are the foundation).
