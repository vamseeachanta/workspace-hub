# Session Exit — Codex-under-Claude route (#2804) + kanban reconciler pilot (#2802)

**Date:** 2026-05-26 · **Machine:** ace-linux-1 · **Author:** Claude (orchestrator session)

## Mission & outcome

Began as: orchestrate Codex's implementation of #2802 (kanban auto-add reconciler) via the plugin broker. The broker delegation was **blocked** by Codex's bwrap sandbox failing nested under Claude. That diagnosis became the larger deliverable.

**Shipped:**
- **#2804 — Codex-under-Claude execution route:** root-caused (Ubuntu 24.04 AppArmor blocks unprivileged userns; Codex execs the *system* `/usr/bin/bwrap`, found via `strace`). Fixed with a surgical AppArmor profile granting `userns` to `/usr/bin/bwrap` + `config.toml [sandbox_workspace_write] network_access=true`. Validated: both `codex exec` and the broker run shell + write files nested under Claude. Codified: guarded installer/teardown + de-hardcoded profile + pilot report (merged **#2809**); orchestrator-handoff correction (merged **#2821**); completeness scorecard (merged **#2819**).
- **#2802 — kanban reconciler (Phase 1 engine):** implemented autonomously by Codex via the route (merged **#2820**); code-stage T2 review (Claude+Codex; Gemini unavailable) found defects; fixes Codex-authored + Claude-committed (merged **#2823**). 13 tests green; engine 100%.
- **Durable pilot handoff** (merged **#2812**).
- **Follow-on plans** (draft) for the deferred work (merged **#2829**).

## Process notes (what worked / lessons)
- 3-round adversarial review killed two bad designs (brain/hands; an oversold "surgical" security claim) before approval — the gate earned its keep.
- Provenance held: Codex authored every patch; Claude orchestrated + did git plumbing only.
- Completeness scoring caught that #2802's *goal* (auto-appear via cron) is **not operational** despite green tests — preventing a premature close.
- Memory updated: `feedback_codex_sandbox_write_blocked` (now "FIXED" with the AppArmor+network_access recipe + the strace/verify lessons).

## Issue states (open, awaiting USER)
| Issue | State | User action |
|---|---|---|
| #2804 | route shipped; scorecard merged (#2819); AC3 closed (#2821) | **close** at 92% (or run AC2 sudo migration → ~100% first) |
| #2802 | re-scoped to **Phase 1**, engine 100% | merge **#2825** (scorecard PR, still OPEN) → apply `status:completeness-verified` → **close** |
| #2826 | Phase 2 (cron+App+nudge) + draft plan | plan-stage adversarial review → approve |
| #2828 | GraphQL fetch hardening + draft plan | review → approve (do before/with #2826) |
| #2827 | Phase 3 Hermes loader + draft plan | review → approve (after #2826) |
| #2813 | route fleet rollout + draft plan | review → approve (independent) |

## Repo / environment state
- **Branch:** session ran on `fix/2795-dispatch-review-findings` (stale/merged, parallel-session-owned). **All my work landed via temp-index snapshots off `origin/main`** — the working tree (141 dirty files, parallel sessions') was never touched; no `git add -A`.
- **Open PR:** #2825 (#2802 scorecard) — awaiting user merge. All other 7 PRs merged.
- **Merged feature branches** linger on remote (repo doesn't auto-delete) — benign; deletable at leisure.
- **Worktrees:** mine (`.claude/worktrees/wt-2802`) removed. Two others listed are other sessions' — left alone.
- **Stashes:** 2 `git-safe-auto-stash` are pre-existing (autosync), not mine — left alone.

## Host changes (user-authorized, reversible) — NO further external action pending
- `/etc/apparmor.d/codex-bwrap` (AppArmor `userns` grant for `/usr/bin/bwrap`). **Security tradeoff accepted by user:** re-enables unprivileged userns for all system-bwrap consumers (VSCode/Firefox/Flatpak), not Codex alone — narrower than the blanket sysctl. Reverse: `scripts/install/teardown-codex-sandbox.sh` (or `apparmor_parser -R` + `rm`).
- `~/.codex/config.toml` → `[sandbox_workspace_write] network_access=true`.

## Cleanup audit
**CLEAN:** my worktree removed; commits isolated via temp-index (no dirty-tree contamination); `/tmp` scratch cleared. **EXPECTED:** #2825 open (user merge); merged remote branches lingering (benign); live AppArmor/config (authorized); memory updates (intended). **UNEXPECTED:** none.

## Next steps (priority order)
1. Merge **#2825**; close **#2802** (Phase 1, 100%) + **#2804** (92%, or after AC2).
2. *(optional)* AC2 sudo migration → I bump #2804 scorecard → close at ~100%.
3. Plan-stage adversarial review → approval for **#2828 → #2826 → #2827**; **#2813** independent.
4. *(housekeeping)* delete merged remote feature branches.
