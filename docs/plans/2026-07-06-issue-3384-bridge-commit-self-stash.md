# Plan for #3384: Bridge memory-freshness — self-stash bug + liveness heartbeat

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-06
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3384
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-3384-claude.md (r1 MAJOR), ...-claude-r2.md (r2 MAJOR) — both folded in via r3 inline patches

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/memory/bridge-hermes-claude.sh:341-390` — `--commit` block. Lines 356-362 stash **before** the commit; `git stash` captures the *staged* changes → `git commit` (:366) finds nothing. Root bug. Confirmed dead ~6 weeks (`git log --grep="auto-refresh memory bridge"` last = 2026-05-21).
- `:370` `git pull --rebase --autostash` already auto-stashes → the manual stash (356-362/383-387) is redundant *and* harmful.
- `:262-263` `SLICE_OWNER=true` for hostname `ace-linux-1` **OR** `dev-primary`; `:380` bare `git push` (no non-FF retry); `:37` `GREEN`/`NC` color globals; `:206` `claude-auto-memory.md` header `Last captured: ${TIMESTAMP}` (date-granular, changes daily — but that file is NOT graded).
- `config/scheduled-tasks/schedule-tasks.yaml:631-634` — `hermes-claude-bridge` runs the script **without `--commit`** (`COMMIT_MODE="${1:-}"`, `bridge:34`); `:650-652` Windows task also omits it.
- `scripts/curation/audit_memory_freshness.py:66-71` — grades 4 git surfaces by `git log -1 %cI`; `categorize`/`audit` `:156-165,180-184` → `worst_age = max(present ages)`; `_git_commit_iso :93-109` returns None (fail-closed) on untracked/empty-log.
- `scripts/memory/curate_readback_slice.py:22-23` — slices deterministic, **no timestamp** → byte-identical on quiet days.

### Host identity (verified 2026-07-06, r2 Finding 1)
`hostname -s` = `ace-linux-1`. `dev-primary` is a **logical alias** (`collect-equality.sh:45` maps `ace-linux-1*`→`dev-primary`), not a distinct host. `setup-cron.sh:40-51` matches by hostname + registry aliases, so this one box may install both the `dev-primary` (04:20) and `ace-linux-1` (04:25) schedule entries → a possible **same-box double-run**. The design below makes that harmless.

### Standards / Wiki
Not applicable (harness/infrastructure).

### Documents consulted
- Issue #3384 (+ 4 diagnostic comments, 2 parallel-agent RCAs).
- r1 review `scripts/review/results/2026-07-06-plan-3384-claude.md` — MAJOR: fix is a no-op (3/4 graded surfaces byte-invariant). r2 review (…-claude-r2.md) — heartbeat closes r1; MAJOR on single-writer + presence-detection.
- `SHARED_SOUL.md` "multi-agent commit serialization" (keep pathspec commit) + "auto-sync may push silently → reflog" (retry).

### Gaps identified
- Scheduled bridge never commits (`--commit` missing); self-stash strands staged content even when run manually; **and** even fixed, byte-invariant surfaces starve the recency clock → the metric needs a **liveness heartbeat**, not content-recency.

### Evidence (embedded)
**Reproduction (Step 1.5):** `bash bridge-hermes-claude.sh --commit` → regenerates rich slices, then `Saved … pre-bridge-stash` → `nothing added to commit` (reproduced twice, 2026-07-05).
**r1 metric-gap proof:** `git log -- .claude/memory/context.md` → **168h gap** (06-26→07-03), 2.3× past 72h; a daily `--commit` bridge would NOT have closed it (context.md byte-identical). `claude-auto-memory.md` absent from `GIT_SURFACES`.
<!-- sources: issue + bridge + schedule + audit + slice-gen + r1 + r2 = 7 -->

---

## Deliverable
A daily-committed, **machine-independent bridge-liveness heartbeat** (`.claude/state/memory-bridge-heartbeat.json`) that `audit_memory_freshness.py` clocks for freshness — so `memory_freshness` reflects "an owner bridge ran & committed in the last 36/72h", independent of whether the deterministic content changed. Plus the self-stash bug fixed so `--commit` actually commits. Freshness is `max(heartbeat age, hermes_memories mtime age)` — heartbeat covers bridge liveness, hermes covers local Hermes liveness (a genuinely-dead Hermes still legitimately trips the cell); content surfaces (context.md/agents.md/slices) become **filesystem presence** checks, not recency-graded.

## Design decisions
- **Heartbeat (r1 Finding 1, user-approved 2026-07-06):** grade *liveness* not *content change*. A tiny committed marker changing once/day guarantees a daily commit clock while slices/context.md keep their deterministic no-churn property. *(Alternative considered — re-grade the daily-changing `claude-auto-memory.md` into `GIT_SURFACES`, no new file; rejected because its per-machine snapshot + volatility (defect #3) make it a noisy liveness signal. A purpose-built single-semantics marker is cleaner.)*
- **Machine-independent blob (r2 Finding 1):** the heartbeat is date-only — `{"last_bridge_commit_utc": "<UTC date>", "schema_version": 1}`, **no `machine` field**. Any owner (or a double-scheduled same box) writing it produces the identical daily blob → whoever commits first wins; a second writer/run sees `git diff --cached --quiet` true → no-op. **Self-serializing** — no single-writer assumption, no cross-machine contention, double-schedule-safe.
- **Presence via filesystem (r2 Finding 2):** content surfaces graded by `Path.exists()` + non-empty, NOT by `git log` (which reports a *deleted* path as still-present via its last commit). Distinct from the heartbeat's git-commit recency clock.

## Pseudocode

Helper `scripts/memory/lib/bridge-commit.sh` (params, no script globals — r1 F3 / r2 F5):
```
bridge_commit_and_push(repo_root, slice_owner, timestamp):
    cd repo_root
    if slice_owner != "true": echo "not slice owner — dry-run"; return 0   # whole commit owner-gated (r1 F2)
    printf '{"last_bridge_commit_utc":"%s","schema_version":1}\n' "$(date -u +%Y-%m-%d)" \
        > repo_root/.claude/state/memory-bridge-heartbeat.json            # date-only, machine-independent
    git add .claude/memory/ config/agents/codex/MEMORY.runtime.md \
            config/agents/gemini/MEMORY.runtime.md .claude/state/memory-bridge-heartbeat.json
    if git diff --cached --quiet: echo "up to date"; return 0            # (heartbeat date-change ⇒ daily diff)
    git commit -m "chore(memory): bridge refresh + heartbeat (${timestamp})" -- \
        .claude/memory/ config/agents/codex/MEMORY.runtime.md \
        config/agents/gemini/MEMORY.runtime.md .claude/state/memory-bridge-heartbeat.json
    for attempt in 1 2 3:                                                # bounded non-FF retry (r1 F2)
        git pull --rebase --autostash || { echo "rebase conflict — resolve manually"; return 1; }
        git push && return 0
    return 1     # 3× fail ⇒ commit stays local (reflog intact), next daily run pushes; not lost
    # NOTE: no colors in helper (or default ${GREEN:-}) so a set -u unit test can't abort on unbound global.
    # manual pre-commit stash (356-362)+pop(383-387) DELETED — the self-stash bug; redundant with --autostash.
```

audit (`audit_memory_freshness.py`):
```
RECENCY_SURFACES  = {"bridge_heartbeat": ".claude/state/memory-bridge-heartbeat.json"}  # git-commit clock
                    + hermes_memories (mtime, unchanged)
PRESENCE_SURFACES = {context_md, agents_md, codex_runtime, gemini_runtime}   # Path.exists()+non-empty
audit():
    recency_ages = [heartbeat git-commit age, hermes mtime age]  (present only)
    worst_age    = max(recency_ages)            # freshness tier from liveness clocks only
    for p in PRESENCE_SURFACES: record present = (path.exists() and path.stat().st_size>0)
    if any present-surface absent: freshness = MISSING-EVIDENCE (fail-closed)   # detects deletion (r2 F2)
    else: freshness = freshness_category(worst_age)
```

schedule (`schedule-tasks.yaml:633`): `--commit` inserted **before** the `>> …log 2>&1` redirect (it is `$1`; r2 F7). Windows task (`:650-652`) left dry-run + a comment noting Windows boxes are neither Hermes hosts nor slice owners → no-op either way (r2 F4 / r1 F4).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/memory/lib/bridge-commit.sh | `bridge_commit_and_push(repo_root, slice_owner, timestamp)` — heartbeat + reorder + owner-gate + non-FF retry; no color globals |
| Modify | scripts/memory/bridge-hermes-claude.sh | source + call helper (replaces buggy 341-390); pass args |
| Modify | scripts/curation/audit_memory_freshness.py | recency = heartbeat + hermes; content surfaces → filesystem presence; absent → MISSING-EVIDENCE |
| Modify | config/scheduled-tasks/schedule-tasks.yaml | add `--commit` **before** redirect (Linux); Windows commented dry-run |
| Create | scripts/memory/tests/test_bridge_commit.py | commit-path regression (bare-remote fixture) |
| Modify | tests/curation/test_audit_memory_freshness.py | heartbeat-liveness + presence(incl. deletion) cases |
| Update | docs/plans/README.md | index row |

Follow-up (separate #3384-child): defect #3 — monotonic step-5 snapshot source (content quality; presence-only grading means a stale-but-present slice is now a *known* uncovered case until #3 lands).

---

## TDD Test List

| Test | Verifies | Input | Output |
|---|---|---|---|
| test_schedule_bridge_commit_flag_position | `--commit` present AND before the `>>` redirect | parse `hermes-claude-bridge.command` | `--commit` index < redirect index |
| test_schedule_win_stays_dryrun | Windows task omits `--commit` (documented) | `hermes-claude-bridge-win.command` | no `--commit` |
| test_commit_lands_heartbeat_no_content_change | owner commits heartbeat even with NO content diff | temp repo, owner=true, no memory change | HEAD = bridge commit; heartbeat in HEAD w/ today's UTC date |
| test_second_same_day_run_noops | idempotent within a day | run twice same date | 2nd run: `git log` unchanged |
| test_commit_lands_staged_change_no_stash | modified memory file committed, not stashed | temp repo + modified agents.md | committed; **no** `pre-bridge-stash` in `git stash list` |
| test_non_owner_no_commit | owner=false → no commit | temp repo, owner=false | `git log` unchanged |
| test_preserves_unrelated_dirty | unrelated dirty neither swept nor lost | + unrelated change | commit pathspec-scoped; unrelated file still present |
| test_push_retry_on_non_ff | advanced upstream → rebase+retry succeeds, not silent exit | bare origin advanced | push succeeds on retry |
| test_audit_fresh_from_heartbeat | liveness from heartbeat, not static surfaces | heartbeat 2h, context.md 200h | MEMORY-FRESH |
| test_audit_expired_dead_heartbeat | dead bridge → EXPIRED | heartbeat 80h | MEMORY-EXPIRED |
| test_audit_missing_on_deleted_surface | a **previously-committed then deleted** presence surface → MISSING-EVIDENCE | commit context.md, then delete from worktree | MISSING-EVIDENCE (filesystem check, not git log) |

**Test harness:** helper takes params (no globals). Fixture: `git init` working repo + `git init --bare` origin + `git remote add origin` + `git push -u` + `git config user.email/name`; drive `bridge_commit_and_push <repo> true <ts>` (owner arg explicit → reachable off ace-linux-1). Non-FF test advances the bare origin from a second clone before the retry.

---

## Acceptance Criteria
- [ ] `uv run pytest scripts/memory/tests/test_bridge_commit.py tests/curation/test_audit_memory_freshness.py -v` — all pass (RED before).
- [ ] Manual on ace-linux-1: `bash bridge-hermes-claude.sh --commit` → `chore(memory): bridge refresh + heartbeat` commit on `main` incl. `.claude/state/memory-bridge-heartbeat.json`; a 2nd same-day run no-ops; no `pre-bridge-stash` left.
- [ ] `audit_memory_freshness.py` → `MEMORY-FRESH` from a fresh heartbeat; simulated 80h heartbeat → `MEMORY-EXPIRED`; deleted context.md → `MISSING-EVIDENCE`.
- [ ] `curate_readback_slice.py` output byte-unchanged.
- [ ] Linux schedule has `--commit` before the redirect; Windows documented dry-run; `setup-cron.sh` re-render reviewed before install.
- [ ] r1+r2 review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

| Round | Verdict | Key findings → resolution |
|---|---|---|
| Claude r1 (fresh subagent) | **MAJOR** | (1) fix no-op — byte-invariant surfaces → **heartbeat** added; (2) all-4-machine thrash+races → **owner-gate + retry**; (3) helper globals → **params**; (4) Windows; (5) defer #3 ok |
| Claude r2 (fresh subagent) | **MAJOR** | confirmed heartbeat **closes r1-F1**; (1) `SLICE_OWNER` = 2 names, "single writer" false → **date-only machine-independent self-serializing blob**; (2) presence-via-git-log misses deletion → **filesystem presence check**; (3) hermes still co-`max` → deliverable clarified; (4) first-run window → risk note; (5) helper machine/colors → dropped; (6) test needs bare-remote → added; (7) schedule flag position → asserted |
| Claude r3 (main-session inline) | RESOLVED | all r2 findings patched inline per `feedback_r3_inline_loop_break_pattern` (r1+r2 were fresh-context; r3 = inline patch, no 3rd dispatch) |

**Overall:** heartbeat concept validated by r2; both MAJORs were scoping defects, resolved inline. **Codex/Gemini cross-provider review not run** (T2 nominally wants 2 providers; two independent fresh-context Claude passes + inline r3 substitute). Recommend: user may approve as-is, or request a Codex/Gemini pass before `plan-approved`.

---

## Risks and Open Questions
- **Risk:** presence-only content surfaces mean a *stale-but-present* slice reads fresh (bridge alive, content old) — a **known** uncovered case until deferred defect #3 (monotonic source) lands. Acceptable: the failure that was actually occurring was total 6-week bridge death, undetected; heartbeat is a net liveness gain.
- **Risk (rollout window):** until the first heartbeat commit lands, the heartbeat surface is absent → on non-owner boxes the cell reads MISSING-EVIDENCE (fail-closed) and on the Hermes owner a fresh hermes mtime could briefly mask it. Short-lived; document as expected at rollout.
- **Risk:** helper extraction from a live control-plane script — keep moved logic identical except reorder+heartbeat+retry; gate behind new tests before the cron uses it.
- **Open (user):** confirm owner-only `--commit` is intended (vs per-machine memory publishing) — matches existing `SLICE_OWNER` intent; flagged for approval.

## Complexity: T2
3 files modified + 1 helper + 2 test files; TDD; one metric-semantics change. Single subsystem (bridge + its metric) → not T3.
