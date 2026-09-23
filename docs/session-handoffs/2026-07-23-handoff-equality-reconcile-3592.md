# Session handoff — machine-equivalence reconcile → #3592 lifecycle → box-side follow-ups

> **Date:** 2026-07-22 → 2026-07-23 · **Machine:** dev-primary (ace-linux-1) · **Lane:** lane:claude (Fable 5)
> **Scope:** full equality-matrix reconcile, dev-primary checkout integrate, #3592 end-to-end (triage → plan → adversarial reviews → TDD implementation → code review → close), gpu-claw cron enrollment + install, win-box follow-up dispatch, mx-720 watcher root-cause.

## What landed (all content-verified on origin/main)

| Commit | What |
|---|---|
| `f30c7e545` + merges | dev-primary checkout integrate: 355-path curation backlog committed; **root cause of 3-day auto-sync outage = interrupted stash-pop leaving UU entries** on the two generated equality artifacts (no MERGE_HEAD) |
| `231830597`, `c6d34c0fa`, … | equality evidence + matrix publishes (fleet went 4/5 → 5/5 reporting; gpu-claw first-ever publish arrived mid-session) |
| `5fcf20d6e`, `2793ca5c2` | #3592 plan + plan-stage review artifacts (Claude r1 MINOR; Codex r2 MAJOR×2 resolved inline r3; re-scoped after #3591 landed the harness dim in a parallel session) |
| `612cf423f` | **#3592 implementation**: `memory` + `scheduler` become COLD dims graded vs `hermes_home_baseline`/`scheduler_baseline` (harness-config.yaml, 5 active boxes); collector scheduler fields default `"unknown"` (never placeholder false/0), Windows `schtasks` probe, `schema_version` 4→5 with a schema<5-Windows migration gate; 28 new/updated tests |
| (fix, merged via auto-sync) | **provider-row schema gate fix** — `provider_row_verdict` pinned top-level schema==4; schema-5 evidence degraded all 12 capability rows to MISSING-EVIDENCE. Caught by code-stage Codex review; gate now 4+, 3 regression tests |
| cron enrollment commit | gpu-claw added to `repository-sync` machines (schedule-tasks.yaml); identity inventory rebuilt; #3475 CAS `source_digest` refreshed; `check-scheduler-mutation-surfaces.py` clean; 287 cron tests green |
| `59fce14ef` | **schtasks probe PascalCase fix** — Windows tasks are `\Claude\RepoSync`/`EqualityReport`; hyphen-only regex would have measured `has_repo_sync=false` on healthy boxes. Regex now case-insensitive/optional-separator |
| `c49716d88` etc. | plan/README closeout docs; #3592 CLOSED with full evidence comment |

**On gpu-claw (over tailnet):** checkout un-wedged (untracked-evidence pull collision → removed identical-timestamp local copy, ff to origin), `setup-cron.sh --dry-run` reviewed → applied with `--allow-live-reload` (live deckhand daemon gate; CAS transaction). Crontab: repository-sync (4h) + equivalence-sentinel (6h) + equality report (weekly Mon). Schema-5 evidence published (`29639aa94`): measured `has_repo_sync: true, job_count: 3`.

## Live matrix state (post-session)

| row | dev-primary | dev-secondary | gpu-claw | ace-win-1 | ace-win-2 |
|---|---|---|---|---|---|
| harness | CONFORMS | CONFORMS | CONFORMS | CONFORMS | CONFORMS |
| scheduler | CONFORMS | CONFORMS | **CONFORMS** (was the real gap) | MISSING-EVIDENCE | MISSING-EVIDENCE |
| memory | CONFORMS | CONFORMS | CONFORMS | BELOW-BASELINE | BELOW-BASELINE |

Every remaining red/grey cell is a real, on-box-actionable gap (by design — no more vote artifacts).

## Open threads → owners

1. **Owner one-liner (asked 4× now):** `systemctl --user disable --now claude-routine-mx-720-cnh-source-watch.timer` — the mx-720 watcher is a **local systemd user timer on ace-linux-1**, NOT a claude.ai cloud routine (cloud list is empty; `trig_01Q1iVfSehkn7tMGJqKivbhV` gone — that mis-pointer is why prior disable asks failed). Classifier blocks agent systemd mutation. Memory topic + index corrected.
2. **ace-win-1 on-box** ([#2815](https://github.com/vamseeachanta/workspace-hub/issues/2815) comment 2026-07-23): pull → `setup-scheduler-tasks.ps1` → `gh auth login` → **archive (not delete)** leftover `~/.hermes` (CLI absent + home present; may hold creds) → run EqualityReport. Expected: scheduler + memory both CONFORMS.
3. **ace-win-2 on-box** ([#3595](https://github.com/vamseeachanta/workspace-hub/issues/3595)): scheduler cell self-heals next scheduled run (pipeline alive); hands needed for hermes home init (CLI present + home absent; declared intent = full stack, or owner flips both baselines to absent) and **reviving the licensed-runs queue heartbeat (dead since 2026-07-13 on the lane's `licensed_host`)**.
4. **Post-#3580** (gemini uninstall): flip `gemini` in `providers_baseline` to `absent` per box as the uninstall lands (one-liner per box in harness-config.yaml).
5. Pre-existing, not introduced here: `test_telegram_hermes_readiness` fails on gpu-claw missing `telegram_hermes` registry metadata (fleet-join gap); `test_reconcile_ecosystem::test_guard_is_invoked_in_target_repo_cwd` regex drift vs reconcile-ecosystem.sh.

## Dirty state / residue (named, intentional)

- **workspace-hub working tree:** only regenerating cron churn (`config/ai-tools/*.json`, `queue/.watcher-state`) — owned by their crons, do not hand-commit.
- **Stashes 0–4** (`cron-churn …` labels, this session): pure regenerable generated-file churn stashed to un-wedge pulls; safe to `git stash drop` — classifier blocked agent drops. Stashes 5–7 predate this session (owner review).
- **worldenergydata + others:** untouched this session; the 2026-07-22 reconcile plan's ~290 guard-held squash-merged branch deletions remain available via `reconcile-ecosystem.sh` output.
- **No external actions pending:** no unsent emails, no unmerged PRs from this session (all work landed directly on main via the documented cron/sync lanes), #3592 closed, #3595 filed.

## Traps banked this session (for the next agent)

- UU-without-MERGE_HEAD = interrupted stash-pop; it silently blocks every subsequent auto-sync commit while reads keep working.
- Publishing evidence from a box via the sparse worktree creates an untracked-vs-tracked pull collision on that box next pull (gpu-claw hit it; compare `generated_at` before deleting).
- Push races with the auto-sync cron are routine on this checkout: a "failed" push often means auto-sync already pushed your commit — **verify by content on origin, not by push exit code**.
- Cross-platform scheduler naming: Linux kebab-case vs Windows PascalCase; probe match-sets need fixtures with real production names.
- `check-scheduler-mutation-surfaces.py` reads the **git index** — stage schedule-tasks.yaml + inventory + registry digest together or it reports stale.
