# Handoff prompt — remaining 7 cadence implementations

> **Generated:** 2026-04-17 (end of context-heavy session)
> **For:** fresh Claude Code session continuing the approved cadence-cron rollout
> **Parent session last commit:** `6b32a7312` (#2313 memory-health shipped)
>
> **Status:** ✅ **COMPLETE** — 2026-04-17 follow-up session shipped all 7
> remaining cadences + the wed#309 cross-repo sync machinery. All 8 original
> issues CLOSED. Four follow-ups (#2335-#2338) filed per §Followups below.
>
> **Commit chain (workspace-hub, after parent `6b32a7312`):**
> - `ee7f4b333` feat(cron): #2315 monthly coverage-drift report
> - `1b40a98c1` feat(cron): #2317 quarterly control-plane-drift audit
> - `162280413` feat(cron): #2314 monthly broken-windows test sweep
> - `c35d0dbd4` feat(cron): #2318 quarterly external-doc-reingest audit
> - `59b813cf2` feat(cron): #2316 quarterly MCP re-evaluation report
> - `9eb24d080` feat(sync):  cadence-common.sh byte-identical guard (wed#309 support)
> - `99e1f0d57` feat(cron): #2319 quarterly ecosystem-rework re-triage
>
> **Commit (worldenergydata):**
> - `39f7a448`  feat(cron): #309 weekly scheduler-health (vendored helper)
>
> **Verification:** 96 tests green across `tests/cron/` + `tests/sync/`. All
> 8 sample reports committed. Both repos pushed. See §Verification below.
>
> **Follow-ups filed:** #2335 (state-size retrofit), #2336 (retention
> policy), #2337 (schedule-index generator), #2338 (cadence-lib smoke test).

---

## What's already done (this branch, commits on `main`)

| Commit | Content |
|---|---|
| `4528da641` | Ecosystem-rework triage report + #2070 plan |
| `b40a6fa61` | #2070 plan revisions after 3-way adversarial review |
| `45a00c9ad`…`0dd242932` | #2070 implementation (7 atomic commits) + first live rotation |
| `db6e34f40` | Cadence shared design + 8 thin per-issue plans |
| `6059a0bd3` | Cadence shared design revisions after 3-way review |
| `07c246513` | `scripts/cron/lib/cadence-common.sh` shared helpers + 15/15 tests |
| `6b32a7312` | **#2313 weekly memory-health-report** shipped (closes #2313) |

## What's next — 7 cadences approved by user (`status:plan-approved` on GitHub)

All approved and ready to implement TDD-first, one atomic commit per cadence,
using the #2313 + #2070 component pattern as the template.

| Issue | Cadence | Thin plan | Companion | Difficulty |
|-------|---------|-----------|-----------|------------|
| wh#2314 | monthly broken-windows test sweep | `docs/plans/2026-04-17-issue-2314-broken-windows-sweep.md` | digitalmodel#510 | M (cross-repo test enumeration) |
| wh#2315 | monthly coverage-drift report | `docs/plans/2026-04-17-issue-2315-coverage-drift-report.md` | assethold#31 | S (parse coverage.xml) |
| wh#2316 | quarterly MCP re-evaluation | `docs/plans/2026-04-17-issue-2316-mcp-re-eval.md` | #1804 | M (scorecard format TBD) |
| wh#2317 | quarterly control-plane drift audit | `docs/plans/2026-04-17-issue-2317-control-plane-drift.md` | #1525 | S (depends on #1525 baseline — can ship with placeholder) |
| wh#2318 | quarterly external doc re-ingest | `docs/plans/2026-04-17-issue-2318-external-doc-reingest.md` | digitalmodel#503 | M (vendor URL handling) |
| wh#2319 | quarterly ecosystem-rework re-triage | `docs/plans/2026-04-17-issue-2319-ecosystem-rework-retriage.md` | this report (self) | L (scans GH issues) |
| wed#309 | weekly scheduler-health | `docs/plans/2026-04-17-issue-wed309-scheduler-health.md` | worldenergydata#266 | **cross-repo — vendored copy** |

**Suggested order (small → large):** #2315, #2317, #2314, #2318, #2316, wed#309, #2319.

## Conventions to follow (non-negotiable)

1. **Test framework:** pytest (matches `tests/cron/test_cadence_common.py` +
   `tests/cron/test_state_size_report.py` + `tests/cron/test_memory_health_report.py`).
   No bats. Each cadence has its own `tests/cron/test_<name>.py`.
2. **Sourcing the helpers:** every cron starts with:
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   source "${SCRIPT_DIR}/lib/cadence-common.sh"
   cadence_init_repo_root
   ```
3. **Env overrides** every cron exposes: `<NAME>_OUT_DIR`, `<NAME>_WEEK`|`_MONTH`|`_QUARTER`,
   and whatever data-source overrides the tests need. Mirror the pattern in
   `scripts/cron/memory-health-report.sh`.
4. **Threshold semantics:** `value > block → RED`, `warn < value ≤ block → YELLOW`,
   `value ≤ warn → GREEN`. Use `compute_status_band`.
5. **Report path:** `docs/reports/<name>-<period>.md` where `<period>` is
   `YYYY-WNN` (weekly), `YYYY-MM` (monthly), `YYYY-QN` (quarterly).
6. **Atomic commit** per cadence: `feat(cron): #<NNN> <period> <name> report`.
   Include script + test + first sample report.
7. **Closes #<NNN>** in commit trailer to auto-close the GH issue.
8. **First sample report** committed alongside implementation — proves the
   cron works on real data.
9. **Post completion comment** on the GH issue after the commit lands.

## Special cases

### wed#309 (cross-repo vendoring)
The shared helper at `scripts/cron/lib/cadence-common.sh` lives in workspace-hub,
but wed#309's cron lives in the `worldenergydata` repo. Per the revised shared
design (commit `6059a0bd3`):

1. Copy `scripts/cron/lib/cadence-common.sh` to
   `worldenergydata/scripts/cron/lib/cadence-common.sh` (byte-identical).
2. Create `scripts/sync/sync-cadence-helper.sh` that compares the two via sha256
   and exits 1 on drift. Wire into workspace-hub's pre-push hook (mirror the
   pattern in `.git/hooks/pre-push`).
3. worldenergydata needs its own `tests/cron/` with the scheduler-health test.

### #2317 (depends on #1525)
#1525 was reopened but its canonical control-plane contract isn't baseline yet.
The plan explicitly allows shipping #2317 with a placeholder mode: cron runs,
writes a report saying "waiting on #1525 contract baseline", and a single
`scripts/cron/control-plane-drift.sh --verify-baseline` flag can later switch
on real drift detection. Acceptable per the plan.

### #2318 (depends on dm#503)
Same pattern — dm#503 (Orcina doc ingest) hasn't shipped. Report with placeholder
mode; when dm#503 lands, flip a flag.

## Followups (tracked in commit messages, not yet filed)

After all 7 cadences land, open these follow-up issues:

1. **`scripts/cron/state-size-report.sh` retro-refactor** to use shared helpers
   (currently has its own status-band logic; pinned in Claude's P2 finding).
2. **Report retention policy**: auto-archive `docs/reports/<name>-<period>.md`
   older than 12 months / 4 quarters / 12 weeks to `docs/reports/archive/<year>/`.
3. **`scripts/cron/build-cadence-schedule.sh`** generator that reads
   `scripts/cron/crontab-template.sh` and rebuilds `docs/reports/cadence-schedule.md`.
   Add a pre-commit guard ensuring the index stays in sync.
4. **`scripts/cron/lib/smoke-test.sh`** — sources helpers, dry-runs each cadence
   with a `--smoke` flag. Runs in pre-commit for any change under
   `scripts/cron/lib/` to prevent silent fan-out regressions.

## Verification before claiming completion

After all 7 ship, run:

```bash
# All cron tests green
uv run --no-project python -m pytest tests/cron/ -v

# All reports exist
ls docs/reports/ | grep -E "(memory-health|broken-windows|coverage-drift|mcp-re-eval|control-plane-drift|external-doc-reingest|ecosystem-rework|scheduler-health)-"

# All 8 GH issues closed via Closes #<NNN>
for i in 2313 2314 2315 2316 2317 2318 2319; do
    gh issue view $i --repo vamseeachanta/workspace-hub --json state --jq .state
done
gh issue view 309 --repo vamseeachanta/worldenergydata --json state --jq .state
```

All 8 should report `CLOSED` after their respective atomic commits land.

## Session handoff summary prompt

> Continue the cadence-cron rollout from commit `6b32a7312`. #2313 is shipped;
> 7 remain (#2314, #2315, #2316, #2317, #2318, #2319 in workspace-hub and wed#309).
> All approved via `status:plan-approved` label. Follow
> `docs/plans/2026-04-17-cadence-handoff.md` (this file). Ship each cadence as
> one atomic commit (script + pytest + first sample report) using the #2313
> pattern at `scripts/cron/memory-health-report.sh`. Start with the easy ones
> (#2315 then #2317) to build momentum. wed#309 needs the vendored-helper
> machinery — budget extra time for it. After all 7 land, open the 4
> follow-up issues listed in this doc.
