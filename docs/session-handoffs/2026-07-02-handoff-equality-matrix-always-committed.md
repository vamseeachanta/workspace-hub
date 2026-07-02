# Session handoff — equality matrix: always committed, fleet-comparable (2026-07-01/02)

**Scope:** user directives "review and assess reconcile equality work" → "the equality matrix
should always be committed to the repo so all machines can be compared equally" →
"update the equality matrix always."

## Shipped (all merged to main)

| PR | What | Key commits/evidence |
|---|---|---|
| #3332 | Collector false-DIVERGES fixes: `kanban` LC_ALL=C collation (+ order-insensitive compare in builder), cron-PATH provider probes (`claude: absent` was a PATH artifact), SHA-aware `skills` verdict (cross-SHA count skew → EXPECTED-DIFF; same-SHA → DIVERGES). 7 new tests. | DIVERGES 27→21 on live rebuild |
| #3343 | **`scripts/readiness/publish-equality.sh`** (issue #3342): publishes equality artifacts to origin/main via a disposable sparse worktree — works from a dirty/diverged/mid-rebase checkout; copies only evidence with `generated_at` strictly newer than origin's (never clobbers a fresher peer); `--rebuild` re-renders the matrix inside the worktree from the union of freshest evidence; staged-path allowlist; FF push + race retry. Wired into `equality-matrix-cron.sh` (+ `refresh-equality-matrix.sh` delegates; `schedule-tasks.yaml` routes both equality tasks through the wrapper, closing the #2972 drift). 9 new tests. | Live pushes `91ce20b9d`, `e9faac2a7`, `e6151f032` from the mid-rebase checkout; correct `noop` when nothing newer |
| #3344 | Regenerated stale `config/agents/skill-index-full.yaml` (Skill-Index Coherence was baseline-red on clean main; #3208 class, regrows on skill merges). | Coherence green fleet-wide |
| #3350 | Matrix refresh cadence daily → **6-hourly** (`50 */6 * * *`, trailing the :47 curation cron by 3 min). | Catalog + crontab now agree |

## Fleet state at exit

- **dev-primary (ace-linux-1):** crons installed + repaired (weekly Mon 04:30; 6-hourly refresh
  00:50/06:50/12:50/18:50; crontab deduped — was cleanup ×6/deckhand ×4; backup
  `~/crontab-backup-20260702-060408.txt`). Column reads **STALE-CHECKOUT by design**: evidence
  was collected while the interactive checkout is mid-rebase (`dirty: true, behind_main: 5`,
  another session's dde work) — self-clears at the first cron after that rebase finishes.
- **dev-secondary (ace-linux-2):** publishing through the new pipeline (`6943b3c70`, clean
  provenance); curation cron revived → `CURATED-FRESH` (had been silent since 06-30).
- **ace-win-1 / ace-win-2:** evidence still 06-27/28; all curation-family cells
  MISSING-EVIDENCE. Run the fleet prompt (below) under Git Bash. ace-win-1 additionally needs
  `gh auth login`; Windows Task Scheduler rollout is #2815/#2998.
- **Canonical matrix (same for every machine):**
  <https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html>

## Open items (filed, not blocking)

- **#3347** — `setup-cron` fingerprint bugs: false-SKIP (script-name collision across schedules
  kept `equality-matrix-refresh` uninstalled since 06-26; worse now that both equality tasks
  share the wrapper) + false-ADD (notifications-cleanup / deckhand-sync duplicate on every
  `--apply`). Until fixed, converge the equality crontab lines manually.
- `test_guard_is_invoked_in_target_repo_cwd` — pre-existing baseline-red (stale regex vs
  `reconcile-ecosystem.sh` `"$PY"` subshell); one-line test fix, separate PR.
- Minor nit: `collect-equality.sh` honors `$WORKSPACE_HUB` for its state dir while
  `publish-equality.sh` reads evidence from its own repo root — they disagree only when the
  wrapper runs from a worktree with the env var set (never in production cron).
- Fleet-wide `memory_freshness: MEMORY-EXPIRED` — `context.md` regenerates byte-identical so
  its git-commit age never resets; a genuine surface signal, not a machine gap. Don't game it.
- State-ref publish (`equivalence-state`): the historic "push hang" is the pre-push tier-1 hook
  running full repo checks on a new branch and failing — exempting dedicated state-refs from
  that gate is a human decision.

## Runbook

- Manual refresh (any machine): `cd <workspace-hub> && git pull --ff-only origin main; bash scripts/readiness/equality-matrix-cron.sh`
- Publish-only, from ANY checkout state (what the agent runs after equality-touching work):
  `bash scripts/readiness/publish-equality.sh --repo /mnt/local-analysis/workspace-hub --rebuild`
- Fleet prompt for remaining machines: see `#3342` issue body / memory topic
  `project_equality_matrix_reconcile_2026_07` (per-machine steps incl. Windows Git Bash form).

## No-external-action status

Nothing outward-facing was sent or published beyond the repo itself and its GitHub Pages
surface. All pushes to `main` were made by the sanctioned publisher script or user-merged PRs.
