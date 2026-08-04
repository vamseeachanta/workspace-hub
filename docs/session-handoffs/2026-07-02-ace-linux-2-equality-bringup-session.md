# Session handoff — ace-linux-2 (dev-secondary) equality bring-up + curation-cron revival

**Date:** 2026-07-02 · **Host:** ace-linux-2 · **Scope:** workspace-hub [#3342](https://github.com/vamseeachanta/workspace-hub/issues/3342) rollout prompt (merged PRs #3343/#3332)

## Outcome

dev-secondary is live in the equality publish loop. Final equality publish **`6943b3c70`**, evidence `generated_at: 2026-07-02T07:18:43` with clean provenance (`dirty:false, behind:0, ahead:0`). Column verdicts: `session_curation: CURATED-FRESH`, `compute/solvers/data_access: CONFORMS`, `skill_link_health: OK`, provider parity all PARITY. Session-curation backlog merged as **`20e71952e`** (4 session report pages + state snapshots + seismic handoff; diff-scoped legal scan PASS).

Live matrix: <https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html>

## Root cause of the dead curation cron — known issue #3212

`cron_render.py:_ensure_log_dir()` prepends a literal `$WORKSPACE_HUB` mkdir guard AFTER `expand_command()` has run; with no `WORKSPACE_HUB=` env line in the crontab, every managed entry died on `mkdir -p /logs/...: Permission denied` (proven by simulating cron's exact env). The 2026-06-30T00:01Z curation stamp was the install-time manual run — the cron likely never fired successfully. Evidence + mitigation posted: [#3212 comment](https://github.com/vamseeachanta/workspace-hub/issues/3212#issuecomment-4865605018).

## Machine state changed (crontab only, no repo code)

1. **Env fix:** `WORKSPACE_HUB=/mnt/local-analysis/workspace-hub` added at crontab top. Backup `logs/cron-backups/dev-secondary-20260702T120759Z-pre-envfix.crontab`.
2. **Dedupe (#3347-adjacent):** removed the superseded pre-#2972 inline weekly equality chain (`collect-equality.sh && uv run ... build-equality-matrix.py`) that duplicated the new Monday-04:30 `equality-matrix-cron.sh` entry. Backup `...T120556Z-pre-dedupe.crontab`. `cron-audit.py`: cataloged=12, preserved_external=9, **uncataloged=0**.
3. `setup-cron.sh` added the weekly `equality-matrix-cron.sh` entry. NOTE: it applies even WITHOUT `--apply`.
4. Readiness refreshed (was stale 2026-06-23 `overall: fail`): now 22/24 pass. `model-registry.yaml` re-stamped after verified currency (update-model-ids dry-run: 0 replacements; R-MODEL-DRIFT pass).

## Gotchas learned (for anyone re-running this on another box)

- **Worktree collect artifact:** running `collect-equality.sh` with `WORKSPACE_HUB=<worktree>` breaks sibling detection (`dirname($WS)`) → `data_access` falsely `absent` (first publish `45333ff40` shipped this; corrected in `adf7efaff`).
- **Collect/publish self-race:** publish advances the local `origin/main` ref, so a collect run immediately after records `behind_main:1` → whole column grades STALE-CHECKOUT (happened at `5c4927f0d`). `git pull --ff-only` before re-collecting; production cadence (4-hourly repo-sync) mostly avoids it.

## Remaining reds / next steps (not done)

- **#3212 fix** is in `status:plan-review` — the real fix (expand the var in the mkdir prefix, or have setup-cron guarantee the env line) needs the plan approved. My crontab env line is a per-box mitigation only; other boxes rendered after #3122 without the env line are suspect.
- ~~**Self-verify cron**~~ **VERIFIED 12:47 CDT:** the first unattended run fired and pushed — log `session-curation-2026-07-02.log` (`curate-session-memory OK`, 44 sessions/24h, 4 providers) + fingerprint `d59da8bc0` on origin `session-curation-state`. The equivalence-sentinel cron (12:17) also revived — the env fix covers all managed entries. Follow-up publish `a77115c23` carried `last_curated_at: 2026-07-02T17:47:01Z` to origin; cell grades CURATED-FRESH.
- **UNFILED cadence gap:** `curate-session-memory.sh` refreshes this box's equality evidence LOCALLY but never publishes it to main, and the 6-hourly `equality-matrix-refresh` (#3350) covers only control-plane boxes — dev-secondary's next scheduled publish is Monday 04:30, so its curation cell on the live matrix will age orange (>12h) / red (>24h) between publishes despite a healthy cron (dead-man's-switch fires on a live man). Fix shape: add dev-secondary (and win boxes once wired) to `equality-matrix-refresh` machines, OR have the curation task publish its own evidence. Needs an issue.
- **memory_freshness: MEMORY-EXPIRED** — `context.md` 143h, hermes memories 121h; content staleness, fleet-wide, needs actual memory-surface refresh, not wiring.
- **R-PRECOMMIT fail:** assetutilities / worldenergydata / assethold `.pre-commit-config.yaml` lack the `legal-sanity-scan` entry → 3 small sibling PRs.
- **dev-primary column is STALE-CHECKOUT from its own evidence** (published 06:54 today with `dirty:true, behind:5` from its interactive checkout) — fix belongs on ace-linux-1; it also skews this box's peer-comparison cells (`behavior/scheduler/memory: DIVERGES`, `harness: NO-MAJORITY`).
- **Legal-scan noise:** full-repo scan FAILs on ~142 pre-existing legacy-log false positives (deny-list field-name / vendor-name patterns in `logs/`; names withheld 2026-08-04), already documented 2026-05-20 with a "scanner should exclude logs/" follow-up — worth a small PR.
- ace-win-1 / ace-win-2 steps from the #3342 rollout prompt (gh auth, Git Bash manual publish, #2815 schedules) remain for those boxes.

## No-external-action status

No emails/messages sent; one GitHub issue comment posted (#3212). Pushes to `vamseeachanta/workspace-hub` main only: `45333ff40`, `adf7efaff`, `5c4927f0d`, `6943b3c70`, `a77115c23` (equality publishes), `20e71952e` (curation backlog), plus this handoff. Crontab edits backed up under `logs/cron-backups/` (gitignored, on-box).

**Exit-state note (parallel session):** a concurrent casing-design session on this box committed `docs/reports/casing-design-worklog.html` to local main (pushed with this closeout) and may hold further uncommitted edits to that file — left untouched. Remaining dirty `.claude/state/*` files are 6-hourly-regenerated curation state; the newest equality evidence is already on origin (`a77115c23`), so this dirt is the box's normal steady-state (`.claude/state` is outside the MEASURED allowlist and cannot STALE the column).
