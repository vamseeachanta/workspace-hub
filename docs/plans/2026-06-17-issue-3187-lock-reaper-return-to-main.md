# Plan for #3187: ace-linux-1 parks off main + stale index.lock froze primary git 5h — lock-reaper + return-to-main guard

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3187
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3187-claude-*.md (cross-provider via plan-review-fanout.sh recommended before merge)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/lib/git-safe.sh` — `git_heal_index()` does `rm -f .git/index.lock` **but only when `git status` reports a corrupt index**; it does NOT distinguish a live holder from an orphan, has no age threshold, no `fuser`/`pgrep` probe, no alert. Defines the shared flock `GIT_SAFE_LOCK=/tmp/workspace-hub-git.lock` and kill-switch `~/.workspace-hub-git-safe-disabled`. The reaper must reuse this flock + disable flag, not invent a parallel one. (This heal-on-corrupt-only behavior is exactly why the 2026-06-17 zero-byte lock on a non-corrupt index froze git for 5h.)
- Found: `scripts/repository_sync-auto` — `_has_git_lock()` detects `index.lock`/`HEAD.lock`/`rebase-merge/`/`rebase-apply/`/`MERGE_HEAD` and *skips* the repo when locked — detect-only, never reaps. Prior art for the lock-file surface set.
- Found: `scripts/monitoring/equivalence-fingerprint.sh` — emits per-box fingerprint with `behind_origin`/`ahead_origin` vs `origin/main` but **no current-branch field** and **no lock field**.
- Found: `scripts/monitoring/equivalence_compare.py` — pure, unit-tested `compare()` emitting `{severity, code, detail}`; new dimensions add here. No `off-main`/`stale-lock` code exists.
- Found: `scripts/maintenance/harness-install-doctor.sh` (#3184) — the REPAIR-arm pattern this work mirrors: `record OK/REPAIRED/SKIP/NEEDS-ATTENTION`, `DOCTOR_DRY_RUN=1`, exit 0 healthy / 1 needs-attention.
- Gap: no stale-lock reaper, no return-to-main guard, no `current_branch`/`stale_index_lock` sentinel dimension.

### Standards
Not applicable — harness/infrastructure.

### LLM Wiki pages consulted
None — workspace-hub-internal harness work, out of scope of `.claude/rules/wiki-sibling-routing.md`.

### Documents consulted
- `config/scheduled-tasks/schedule-tasks.yaml` — catalog SSoT (HARD RULE: all scheduled tasks declared here). `equivalence-sentinel` (`17 */6`) + `harness-install-doctor` (`11 */6`) define the 6-hourly detect/repair cadence.
- `.claude/skills/workspace-hub/worktree-pre-push-bypass-for-tier1-checks/SKILL.md` — the workspace-hub pre-push hook runs **ecosystem-wide tier-1 repo checks** (digitalmodel etc.), holding the repo for minutes; soft-bypass `GIT_PRE_PUSH_SKIP=1`. This is the long-running lock-holder the reaper must NOT reap.
- `scripts/enforcement/install-hooks.sh` — pre-push chain installer; the installed `.git/hooks/pre-push` is NOT repo-tracked (this clone has none) → the reaper must detect a live pre-push op **behaviorally** (`fuser`/`pgrep`/age), not by reading a tracked hook file.
- `scripts/cron/lib/cadence-common.sh` — shared cron helpers (repo-root resolution, status banding, TZ=UTC).
- Epic #3058 (parent); #3059 (CLOSED, report-only sentinel); #3184 (the repair arm). This issue extends both.

### Gaps to build
1. `scripts/maintenance/git-lock-reaper.sh` — orphan-vs-live lock reaper + alert.
2. `scripts/maintenance/return-to-main-guard.sh` — idle/no-concurrent-session branch restore.
3. Their test suites.
4. `current_branch` + `stale_index_lock` fields in the fingerprint; `off-main` (WARNING) + `stale-index-lock` (CRITICAL) divergence codes in the comparator.

---

## Approach (concrete decisions)

**Location.** Both scripts in `scripts/maintenance/` (repair/healing arms, beside `harness-install-doctor.sh`); detectors stay in `scripts/monitoring/` (the sentinel). Keeps the detect/repair split clean.

**Scheduling** (two new `schedule-tasks.yaml` entries, `machines: [dev-primary, ace-linux-1, dev-secondary, ace-linux-2]`, Linux-only v1):
- `git-lock-reaper`: `7,37 * * * *` — twice hourly, **staggered off** `dispatch-leader-watch` (`*/15`) and `repository-sync` to avoid `GIT_SAFE_LOCK` flock contention (review CRITICAL). A frozen lock takes the git layer offline, so ≤30-min detection is enough. `requires: [bash, git]` only — **do NOT list `psmisc`**: `requires` gates *skip-if-absent* on CLI tools, not package installs; `fuser` may be absent on spare boxes → silent skip (review HIGH). The script detects the lock-holder via `command -v fuser || lsof` with a portable fallback, and degrades to age+`git`-probe if neither exists.
- `return-to-main-guard`: `23,53 * * * *` — staggered off `repository-sync` (`0 */4`) so a guard `checkout` never races a sync `pull` (review CRITICAL). `requires: [bash, git]`.

**Reaper — distinguish live pre-push from orphan. The decisive test is git itself, not the flock (review BLOCKER: holding `GIT_SAFE_LOCK` does NOT stop git from creating/owning `index.lock`).** Fail-closed; reap only if ALL hold:
1. no lock-holder (`fuser`/`lsof` on the lock path) AND no `git push`/pre-push/`pytest`/benchmark process in the repo (advisory, may miss hook children — not load-bearing alone).
2. no `rebase-merge/`/`rebase-apply/`/`MERGE_HEAD`.
3. lock age ≥ `REAP_AFTER_MIN` (default **90**, not 30 — must exceed worst-case pre-push suite; #3187 AC requires measuring actual worst-case on dev-primary and setting ≥1.5× before enable — review MAJOR).
4. **DECISIVE: `git -C <repo> status` succeeds with the lock present** — proving git has actually released it (this is what `git-safe.sh:git_heal_index` keys on; a live op would hold/contend). Only then `rm`.
This 4-test logic is factored into a **shared `_has_stale_orphan_lock()` helper in `git-safe.sh`**, and `git_heal_index` is updated to call it before its own `rm` (review MAJOR: otherwise heal-index bypasses the reaper's guards with a different predicate). Acquire the `git-safe.sh` flock, **re-run test 4**, `rm -f`, alert. Targets the exact 2026-06-17 hazard (zero-byte 06:00 lock, no holder, non-corrupt index → invisible to the old heal-on-corrupt-only path).

**Return-to-main — avoid data loss (Hermes live + concurrent sessions + minutes-long pre-push); fail-closed. Concrete, enumerated guards (review CRITICAL: the prior text was handwavy):**
1. **Concurrent-session guard** — skip if ANY of: `fuser`/`lsof` shows a holder of `.git/`; a `git push`/pre-push process runs in the repo; a `.claude/state/session-signals/*` file has mtime < 15 min; `pgrep` matches the box's role-expected live processes (dev-primary → `claude|hermes`; others → `claude`); the `GIT_SAFE_LOCK` flock is held; or `index.lock` exists. If the detector itself errors, **assume concurrent and skip** (fail-closed).
2. **Unpushed-commit guard** — first verify an upstream exists (`git rev-parse --abbrev-ref '@{u}'`); **no upstream → NEEDS-ATTENTION** (cannot prove the local-only branch is safe — review HIGH, the 2026-06-17 branches had no upstream). If ahead of remote → NEEDS-ATTENTION + alert, do NOT switch.
3. **Stash-safety with recovery** — pre-check free disk; `git stash push -u` (keep, never drop); capture `stash_id=$(git rev-parse stash@{0})`; **if the subsequent `git checkout main` fails, immediately `git stash pop` to restore the tree** and exit NEEDS-ATTENTION (review HIGH). Report `stash_id` + a recovery command to `.claude/state/git-guard-reports/<date>-<branch>.json` so the daily briefing surfaces it (not just stderr). A weekly cleanup note covers unbounded stash growth.
4. **flock coordination** — reuse `GIT_SAFE_LOCK`; honor `~/.workspace-hub-git-safe-disabled`.

**Portability** — all tools wrapped in a shared lib (`_stat_mtime`: `stat -c %Y` || `stat -f %m`; `_git_current_branch`: `git branch --show-current` || `git symbolic-ref --short HEAD`; lock-holder: `fuser` || `lsof` || skip-detection-disabled-with-warning). Linux-only v1; BSD/macOS deferred. **Both scripts use `$(git rev-parse --show-toplevel)`/relative paths only** so they pass `check-no-abs-paths.sh` and don't self-block the pre-push gate (review MEDIUM).

**Sentinel (#3059).** Add `current_branch` + `stale_index_lock` (computed by the same shared `_has_stale_orphan_lock()` predicate) to the fingerprint. **Bump `fingerprint_version` to 2 and emit the new fields only at v2; the comparator treats mixed-version boxes as warn-only** so a not-yet-updated box (emitting `current_branch: null`) doesn't trigger false `off-main` divergences (review HIGH). Severity is **role-aware**: `off-main` → WARNING on control-plane roles (cron-execution-correctness matters), INFO on contribute/sim-worker roles where a feature-branch checkout can be normal (review MEDIUM); `stale-index-lock` → CRITICAL on all roles (active outage). Gives the #3184 install-doctor lane a signal to act on.

**Out of scope (recommended follow-on):** a dedicated `main`-pinned cron worktree (eliminates the root cause vs reactively healing) — larger cross-cron change touching every `cd $WORKSPACE_HUB` + `setup-cron.sh`. Ship the reactive guard now; file a follow-on for the worktree convention.

---

## Files to change
| Action | Path |
|---|---|
| Create | `scripts/maintenance/git-lock-reaper.sh` |
| Create | `scripts/maintenance/return-to-main-guard.sh` |
| Create | `scripts/maintenance/tests/test_git_lock_reaper.sh` |
| Create | `scripts/maintenance/tests/test_return_to_main_guard.sh` |
| Modify | `scripts/monitoring/equivalence-fingerprint.sh` (add `current_branch`, `stale_index_lock`) |
| Modify | `scripts/monitoring/equivalence_compare.py` (`off-main` WARNING, `stale-index-lock` CRITICAL) |
| Modify | `scripts/monitoring/tests/` (cover new dimensions) |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` (declare both crons) |
| Update | docs/plans/README.md (index) |

## TDD test list
Reaper: reap-orphan-old-no-holder; skip-lock-held-by-fuser; skip-pre-push-suite-active; skip-fresh-lock-under-threshold; skip-rebase-in-progress; idempotent; dry-run-no-mutation.
Guard: already-on-main no-op; skip-concurrent-session; skip-unpushed-commits (NEEDS-ATTENTION); stash-safety (stash listed, not dropped); dry-run-no-mutation.
Sentinel: fingerprint emits new fields; compare off-main→WARNING; compare stale-lock→CRITICAL.
All tests use a sandboxed `HOME`/fixture repo; never touch the operator's real `~/` or live primary.

## Adversarial review (T3) — DONE at plan stage, findings incorporated above
Three independent adversarial lenses run 2026-06-17 (Claude subagents; cross-provider via `plan-review-fanout.sh` recommended before CODE-stage merge). All three returned REQUEST-CHANGES; consensus findings folded into Approach (r3 inline):

| # | Sev | Finding | Resolution in plan |
|---|---|---|---|
| 1 | BLOCKER | Holding `GIT_SAFE_LOCK` does NOT stop git creating `index.lock` (TOCTOU) | Decisive test is now `git status` succeeds with lock present (heal-index-style), not flock alone |
| 2 | MAJOR | 30-min threshold unmeasured | Raised default to 90; AC requires measuring worst-case pre-push on dev-primary, set ≥1.5× before enable |
| 3 | MAJOR | reaper vs `git_heal_index` divergent predicates | Factored into shared `_has_stale_orphan_lock()`; `git_heal_index` updated to call it |
| 4 | CRIT | concurrent-session detection handwavy | Enumerated 6 concrete fail-closed predicates |
| 5 | HIGH | no-upstream branch edge case | Explicit upstream check; no-upstream → NEEDS-ATTENTION |
| 6 | HIGH | stash failure/recovery | disk pre-check; checkout-fail → re-pop; report stash_id to state file |
| 7 | CRIT | schedule collision w/ `dispatch-leader-watch` `*/15` + `repository-sync` | reaper `7,37`, guard `23,53` (staggered) |
| 8 | HIGH | `psmisc` not deployable via `requires` | dropped from requires; `fuser`||`lsof`||degrade fallback |
| 9 | HIGH | fingerprint field addition → false `off-main` on mixed-version boxes | bump `fingerprint_version` to 2; comparator warn-only on mixed |
| 10 | HIGH | BSD/GNU portability | wrapper funcs (`_stat_mtime`, `_git_current_branch`, lock-holder) |
| 11 | MED | self-blocking pre-push gate | relative paths / `$(git rev-parse --show-toplevel)` only |
| 12 | MED | `off-main` severity | role-aware (WARNING control-plane, INFO contribute) |

CODE-stage review (T3, 3-provider) still required before merge per SOUL gate 4.

## Risks
- **R1 (LIVE 2026-06-17):** reaping a live pre-push lock corrupts an in-flight push/test. → 4-test conjunction + flock-then-recheck + threshold above worst-case pre-push.
- **R2 (LIVE 2026-06-17):** switching branches under a concurrent session loses/confuses work. → concurrent-session + unpushed-commit guards, fail-closed.
- **R3:** guard `git checkout` races autosync/bridge on live Hermes. → reuse `GIT_SAFE_LOCK` flock + kill-switch.
- **R4:** double-reap with `git-safe.sh:git_heal_index`. → factor orphan predicate into a shared helper; keep additive; don't change `git_heal_index`.
- **Open:** `REAP_AFTER_MIN=30` — confirm worst-case pre-push suite duration on the primary; raise if longer.
- **Open:** ship guard-only now vs pursue the blessed cron-worktree convention in this issue? (recommend guard now + follow-on)

## Acceptance criteria
- [ ] New test suites pass; comparator pytest green; no regression in `scripts/cron/tests/` / `scripts/monitoring/tests/`.
- [ ] Reaper SKIPs (no removal) against a live/fresh/held lock; reaps a true orphan with alert (R1).
- [ ] Guard SKIPs (no switch) under a simulated concurrent session; never strands unpushed commits (R2).
- [ ] `validate-schedule.py` passes; both crons render per Linux box.
- [ ] Sentinel emits `off-main`/`stale-index-lock` divergences on fixture fingerprints.
- [ ] Reaper + guard installed on dev-primary; sentinel flags the drift (issue #3187 AC 1–3).
- [ ] Plan + code adversarial review artifacts posted.
