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
- **Self-verify cron:** session-curation fires `47 */6 * * *`; first unattended run after this session should push a `chore(curation)` / digest update — if the freshness cell ages past 12h again, re-check `logs/monitoring/session-curation-*.log` (dir now exists).
- **memory_freshness: MEMORY-EXPIRED** — `context.md` 143h, hermes memories 121h; content staleness, fleet-wide, needs actual memory-surface refresh, not wiring.
- **R-PRECOMMIT fail:** assetutilities / worldenergydata / assethold `.pre-commit-config.yaml` lack the `legal-sanity-scan` entry → 3 small sibling PRs.
- **dev-primary column is STALE-CHECKOUT from its own evidence** (published 06:54 today with `dirty:true, behind:5` from its interactive checkout) — fix belongs on ace-linux-1; it also skews this box's peer-comparison cells (`behavior/scheduler/memory: DIVERGES`, `harness: NO-MAJORITY`).
- **Legal-scan noise:** full-repo scan FAILs on ~142 pre-existing legacy-log false positives (Prelude FLNG / 2H Offshore in `logs/`), already documented 2026-05-20 with a "scanner should exclude logs/" follow-up — worth a small PR.
- ace-win-1 / ace-win-2 steps from the #3342 rollout prompt (gh auth, Git Bash manual publish, #2815 schedules) remain for those boxes.

## No-external-action status

No emails/messages sent; one GitHub issue comment posted (#3212). Pushes to `vamseeachanta/workspace-hub` main only: `45333ff40`, `adf7efaff`, `5c4927f0d`, `6943b3c70` (equality publishes), `20e71952e` (curation backlog), plus this handoff. Crontab edits backed up under `logs/cron-backups/` (gitignored, on-box).
