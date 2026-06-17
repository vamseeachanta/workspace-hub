# Plan for #3187: git-lock-reaper + return-to-main guard

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3187
> **Client:** N/A
> **Project:**
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3187-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/maintenance/harness-install-doctor.sh` — #3184 repair arm, landed; schedules at `11 */6 * * *`; the triggering artifact that surfaced this issue.
- Found: `scripts/monitoring/equivalence-sentinel.sh` + `equivalence-fingerprint.sh` + `equivalence_compare.py` — the sentinel system this plan extends (new dimensions added in fingerprint + comparator).
- Found: `scripts/cron/lib/git-safe.sh` — contains `git_heal_index()` which does unconditional `rm -f .git/index.lock`; **unsafe as a standalone reaper** (no age check, no pgrep guard).
- Gap: `scripts/maintenance/git-lock-reaper.sh` — does NOT exist; must create.
- Gap: `scripts/maintenance/return-to-main-guard.sh` — does NOT exist; must create.
- Gap: `config/scheduled-tasks/schedule-tasks.yaml` — no `git-lock-reaper` or `return-to-main-guard` task entries; must add both.

### Standards

| Standard | Status | Source |
|---|---|---|
| feedback_orphan_lock_doom_loop_monitor_reap | codified | `.claude/memory/topics/feedback_orphan_lock_doom_loop_monitor_reap.md` |
| feedback_git_status_lock_storm | codified | `.claude/memory/topics/feedback_git_status_lock_storm.md` |

Not a traditional engineering standard issue. Memory feedback rules apply as operational constraints.

### LLM Wiki pages consulted

- No relevant wiki pages for this harness/operational topic.

### Documents consulted

- `scripts/monitoring/equivalence-fingerprint.sh` — current fingerprint schema (6 fields); new `on_main` + `index_lock_stale_min` fields will extend it.
- `scripts/monitoring/equivalence_compare.py` — current 6 divergence checks; new checks 7 + 8 added for on-main and stale-lock.
- Related issue #3059 — equivalence sentinel (what this plan extends with primary-tree dimension).
- Related issue #3184 — `harness-install-doctor.sh` (surfaced this issue during deployment to ace-linux-1).
- Related issue #3058 — ecosystem hardening epic (parent).
- `config/scheduled-tasks/schedule-tasks.yaml` — existing 56 task entries; `equivalence-sentinel` runs at `17 */6 * * *` and `harness-install-doctor` at `11 */6 * * *`; neither addresses lock or branch drift.

### Gaps identified

- No lock-reaper script exists anywhere in the repo.
- No return-to-main guard exists anywhere in the repo.
- Equivalence fingerprint does not capture branch state or lock state.
- `git_heal_index()` in `git-safe.sh` is unconditional removal — would race-reap a live push-hook's lock; cannot reuse as a standalone reaper.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-17T via GitHub MCP):
- `#3187` — OPEN — ace-linux-1 chronically parks off main + stale index.lock froze primary git for 5h
- `#3184` — CLOSED (landed) — harness-install-doctor
- `#3059` — OPEN — equivalence sentinel
- `#3058` — OPEN — harden ecosystem epic

**File existence** (verified 2026-06-17T via resource intel agent):
- EXISTS: `scripts/maintenance/harness-install-doctor.sh`
- EXISTS: `scripts/monitoring/equivalence-sentinel.sh`
- EXISTS: `scripts/monitoring/equivalence-fingerprint.sh`
- EXISTS: `scripts/monitoring/equivalence_compare.py`
- EXISTS: `scripts/cron/lib/git-safe.sh`
- EXISTS: `scripts/maintenance/tests/test_harness_install_doctor.sh` (test pattern to follow)
- MISSING (new — this plan creates): `scripts/maintenance/git-lock-reaper.sh`
- MISSING (new — this plan creates): `scripts/maintenance/return-to-main-guard.sh`
- MISSING (new — this plan creates): `scripts/maintenance/tests/test_git_lock_reaper.sh`
- MISSING (new — this plan creates): `scripts/maintenance/tests/test_return_to_main_guard.sh`

**Line excerpts** — `git_heal_index()` in `git-safe.sh` (unsafe pattern we must NOT copy):
```
rm -f "${git_dir}/.git/index.lock" 2>/dev/null || true
git -C "$git_dir" read-tree HEAD 2>/dev/null
```
No age check, no pgrep guard — unconditional removal.

**Gap proofs**:
- `ls scripts/maintenance/git-lock-reaper.sh` → "No such file or directory"
- `ls scripts/maintenance/return-to-main-guard.sh` → "No such file or directory"
- `grep -c "git-lock-reaper\|return-to-main" config/scheduled-tasks/schedule-tasks.yaml` → `0`

**Reproduction proofs**:
N/A — this issue describes observed infrastructure drift (not a failing test). The "failure mode" is: `.git/index.lock` zero-byte with no holding process + workspace-hub tree off `main` on ace-linux-1. Both states are environmental, not reproducible in unit tests. The lock-reaper and guard scripts must be tested via shunit2/mock approach (stub `pgrep`, stub `git`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-17-issue-3187-git-lock-reaper-return-to-main.md` |
| Lock reaper script | `scripts/maintenance/git-lock-reaper.sh` |
| Return-to-main guard | `scripts/maintenance/return-to-main-guard.sh` |
| Lock reaper tests | `scripts/maintenance/tests/test_git_lock_reaper.sh` |
| Return-to-main tests | `scripts/maintenance/tests/test_return_to_main_guard.sh` |
| Fingerprint emitter (modify) | `scripts/monitoring/equivalence-fingerprint.sh` |
| Comparator (modify) | `scripts/monitoring/equivalence_compare.py` |
| Schedule YAML (modify) | `config/scheduled-tasks/schedule-tasks.yaml` |
| Plan review — Claude | `scripts/review/results/2026-06-17-plan-3187-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-17-plan-3187-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-17-plan-3187-gemini.md` |

---

## Deliverable

Two self-healing maintenance scripts live on ace-linux-1 under cron, the equivalence sentinel gains two new drift dimensions (`on_main` + `index_lock_stale_min`), and TDD test suites cover all safe-reap and guard decision paths.

---

## Pseudocode

```
git-lock-reaper.sh:
  REPO_ROOT = git rev-parse --show-toplevel
  LOCK = "$REPO_ROOT/.git/index.lock"
  AGE_MIN = ${LOCK_REAPER_AGE_MINUTES:-5}    # env-overridable for testing

  if LOCK not exists → exit 0               # nothing to do

  if find LOCK -mmin +AGE_MIN returns empty → exit 0   # too fresh, live op
  if pgrep -x git > /dev/null → exit 0     # live git process, step back

  # Both conditions met → orphan confirmed
  log "REAPER: removing orphan .git/index.lock (age >AGE_MIN min)"
  rm -f LOCK
  alert via stderr (cron captures → mail)
  exit 0

return-to-main-guard.sh:
  REPO_ROOT = ...
  current_branch = git symbolic-ref --short HEAD   (detached → "DETACHED")

  if current_branch == "main" → exit 0             # already correct

  if git diff --quiet && git diff --cached --quiet:
      # Tree is clean (no staged or unstaged work)
      if pgrep -x git > /dev/null → exit 0         # active git op — wait
      log "GUARD: workspace-hub is on $current_branch and idle — returning to main"
      git checkout main
      exit 0
  else:
      # Dirty tree — distinguish regenerable vs real work
      untracked_count = git ls-files --others --exclude-standard | wc -l
      staged_count    = git diff --cached --name-only | wc -l
      if staged_count > 0:
          log "GUARD: staged changes present — NOT returning to main (user in-flight)"
          exit 1   # alert — do not auto-restore
      else:
          log "GUARD: only dirty/untracked (likely regenerable) — stashing + returning to main"
          git stash push -u -m "guard-auto-stash-$(date +%Y%m%dT%H%M%S)"
          git checkout main
          exit 0

equivalence-fingerprint.sh (additions):
  on_main = (git symbolic-ref --short HEAD == "main") ? true : false
  lock_path = "$REPO_ROOT/.git/index.lock"
  if lock_path exists AND pgrep -x git returns empty:
      index_lock_stale_min = stat mtime delta in minutes
  else:
      index_lock_stale_min = null

equivalence_compare.py (new checks 7 + 8):
  check 7: for each fp where role == "full":
      if fp["on_main"] == false → WARNING "primary-off-main"
  check 8: for each fp where index_lock_stale_min is numeric:
      → WARNING "stale-index-lock" with box + age
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/maintenance/git-lock-reaper.sh` | lock-reaper implementation |
| Create | `scripts/maintenance/return-to-main-guard.sh` | return-to-main guard |
| Create | `scripts/maintenance/tests/test_git_lock_reaper.sh` | TDD test suite — reaper |
| Create | `scripts/maintenance/tests/test_return_to_main_guard.sh` | TDD test suite — guard |
| Modify | `scripts/monitoring/equivalence-fingerprint.sh` | add `on_main` + `index_lock_stale_min` fields |
| Modify | `scripts/monitoring/equivalence_compare.py` | add checks 7 + 8 |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add `git-lock-reaper` (every 5 min) + `return-to-main-guard` (every 30 min) tasks for ace-linux-1 |

---

## TDD Test List

Tests use `shunit2` for shell scripts (pattern from `test_harness_install_doctor.sh`) and Python `pytest` for comparator.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_reaper_no_lock` | exits 0 silently when no lock present | LOCK absent | exit 0, no output |
| `test_reaper_fresh_lock` | skips reap when lock is < AGE_MIN minutes old | LOCK mtime=now-1m | exit 0, "too fresh" logged |
| `test_reaper_live_git_process` | skips reap when `pgrep -x git` returns hit | LOCK old + stub pgrep → 1 pid | exit 0, "live git" logged |
| `test_reaper_orphan_confirmed` | reaps and logs when lock is old + no git | LOCK mtime=now-10m + pgrep empty | exit 0, LOCK removed, alert logged |
| `test_reaper_age_env_override` | respects `LOCK_REAPER_AGE_MINUTES` | LOCK mtime=now-3m, AGE_MIN=2 | reaps (3 > 2) |
| `test_guard_already_main` | exits 0 when already on main | symbolic-ref=main | exit 0, no git ops |
| `test_guard_off_main_clean` | checks out main when off-main + clean tree | branch=handoff, no staged/dirty | exit 0, git checkout main |
| `test_guard_off_main_staged` | refuses return when staged changes present | branch=handoff, staged files | exit 1, "staged changes" logged |
| `test_guard_off_main_only_untracked` | stashes + returns to main when only regenerable dirty | branch=handoff, untracked only | stash created, git checkout main |
| `test_guard_off_main_live_git` | skips guard when git op in progress | branch=handoff, pgrep hit | exit 0, "active git op" logged |
| `test_fingerprint_adds_on_main_field` | fingerprint JSON includes `on_main` key | repo on main | `on_main == true` in output |
| `test_fingerprint_adds_on_main_false` | on_main=false when off-branch | repo on handoff branch | `on_main == false` |
| `test_fingerprint_stale_lock_field` | `index_lock_stale_min` is numeric when orphan lock | LOCK present + no pgrep | numeric field in JSON |
| `test_fingerprint_no_lock_null` | `index_lock_stale_min` is null when no lock | LOCK absent | `null` in JSON |
| `test_compare_primary_off_main_warning` | comparator raises WARNING for role=full off-main | fp: role=full, on_main=false | WARNING "primary-off-main" |
| `test_compare_stale_lock_warning` | comparator raises WARNING for stale lock | fp: index_lock_stale_min=8 | WARNING "stale-index-lock" |
| `test_compare_contribute_off_main_no_warn` | comparator ignores off-main for non-full roles | fp: role=contribute, on_main=false | no divergence emitted |

---

## Acceptance Criteria

- [ ] `bash scripts/maintenance/tests/test_git_lock_reaper.sh` — all tests pass
- [ ] `bash scripts/maintenance/tests/test_return_to_main_guard.sh` — all tests pass
- [ ] `uv run pytest scripts/monitoring/` — equivalence comparator tests pass (no regression)
- [ ] `bash scripts/maintenance/git-lock-reaper.sh` exits 0 on ace-linux-1 (no lock present)
- [ ] `bash scripts/maintenance/return-to-main-guard.sh` exits 0 on ace-linux-1 (already on main)
- [ ] `bash scripts/monitoring/equivalence-fingerprint.sh` JSON output includes `on_main` + `index_lock_stale_min` keys
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` has entries for `git-lock-reaper` (schedule: `*/5 * * * *`, machines: ace-linux-1) and `return-to-main-guard` (schedule: `*/30 * * * *`, machines: ace-linux-1)
- [ ] Reaper uses `pgrep -x git` (not `-f`) per `feedback_orphan_lock_doom_loop_monitor_reap`

---

## Adversarial Review Summary

<!-- Filled in after adversarial review step. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | pending |
| Codex | — | pending |
| Gemini | — | pending |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** The `*/5 * * * *` reaper schedule means the reaper runs every 5 min. If a legitimate slow operation (large rebase, `git gc`) takes > 5 min but doesn't hold a live `pgrep -x git` process at the moment the reaper fires, the lock gets reaped mid-op. **Mitigation:** require both `pgrep -x git` empty AND `find -mmin +5`; the intersection of both is very narrow. Consider defaulting `LOCK_REAPER_AGE_MINUTES=10` to allow longer operations.
- **Risk:** `return-to-main-guard.sh` auto-stashing untracked files could hide user intent if those files are actually new work. **Mitigation:** the guard must only auto-stash when `staged_count == 0` (no deliberate staging); alert clearly. Open for user to configure `GUARD_AUTO_STASH=0` to disable.
- **Risk:** The cron worktree alternative (blessed `main` worktree for crons, separate from interactive) is the more robust long-term solution but requires updating all cron scripts' `REPO_ROOT` paths. **Open question for user:** approve the simpler guard approach here, or plan a separate issue for the cron-worktree refactor?
- **Open:** Should the reaper send a `gh issue comment` on #3187 (or a dedicated ops-alert issue) on each reap event, or is stderr → cron mail sufficient? Suggest stderr → mail for now; file a follow-on for structured alerting.

---

## Complexity: T2

**T2** — two new scripts + two test files created, three existing files modified, no external dependencies, TDD required. Single repo (workspace-hub). Touches monitoring + maintenance + scheduling subsystems but no cross-repo changes.
