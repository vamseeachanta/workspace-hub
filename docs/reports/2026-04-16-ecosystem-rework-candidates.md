# Ecosystem Rework Candidates — 2026-04-16

Scope: 6 repos, ~3,100 issues (open + closed). Four parallel triage agents
surfaced 29 candidates; this report ranks the top 20 and splits them into
one-shot reworks vs. themes that should be promoted to a recurring cadence.

## Scoring

`leverage × (1 / effort)` where leverage = token-efficiency, performance,
quality, velocity, ecosystem-reach. Tie-breaker: recency of pain.

## Tier 1 — Top 10 (highest leverage)

| # | Issue | Title | Mode | Recurrence | Why now |
|---|-------|-------|------|-----------|---------|
| 1 | wh#1839 | Workflow hard-stops / tool-call ceiling | **in-flight (Phase 2c done 2026-04-09)** — finish remaining phases | one-shot (hook) | Cites 6.1M wasted tool calls on 3 runaway WRKs; plan-approval gate landed, tool-call ceiling still missing |
| 2 | wh#1804 | MCP eval: token-optimizer, omega-memory, evalview, insaits | rework | one-shot + quarterly re-eval | Claimed 95% context reduction is the single highest-leverage token-eff bet; zero owner |
| 3 | dm#483 | curves.py 29,666-line decomposition | rework | one-shot | 20× per-edit token cost; blocks hydrostatics test coverage |
| 4 | wh#1803 | Context-budget audit skill | rework | **monthly** | Measure what 691 skills + MCP + AGENTS.md burn; baseline all trimming |
| 5 | wh#2018 | Agent bypass resistance via hooks/CI | rework | one-shot | Review-gate compliance is 4%; promote text rules to level-3 enforcement |
| 6 | wh#2070 | Guard state sync against oversized session-signal files | rework | one-shot + weekly size report | 103 MB push failure already happened; trivial fix, recurring risk |
| 7 | wh#1525 | Control-plane contract across repo ecosystem | **reopen** | one-shot + quarterly drift audit | Bulk-closed in March with #1517/#1518/#1523/#1526; pain still daily |
| 8 | wh#1902 | Automate memory quality before bridge commit | rework | one-shot + weekly health report | Cron propagates bad memory to all 5 machines without a gate |
| 9 | dm#510 | Fix 20 pre-existing OrcaFlex test failures | rework | one-shot + monthly broken-windows sweep | Polluted baseline hides real regressions in every builder PR |
| 10 | dm#503 | Ingest Orcina/OrcaWave webhelp into LLM doc-index | rework | one-shot + quarterly re-ingest | Unblocks ~50+ OrcaFlex issues; stops API/YAML guessing |

## Tier 2 — Next 10

| # | Issue | Title | Mode | Recurrence |
|---|-------|-------|------|-----------|
| 11 | wh#1720 | Cross-agent session corpus audit — mine tool calls for skill candidates | rework | **monthly** |
| 12 | wh#32 | Raise context window limits (1M Claude, Codex) in harness config | rework | one-shot |
| 13 | wh#1731 | Stale `/command` reference sweep across child repos | **reopen** | **monthly** |
| 14 | dm#109 | Doc-index + agent-persona architecture | rework | one-shot (groundwork for #4, #10) |
| 15 | dm#504 | Buoys builder refactor — split 611-line mega-builder | rework | one-shot |
| 16 | dm#152 | Test coverage for PlatformLoader + PipelineLoader | rework | one-shot |
| 17 | dm#40 | OrcaFlex batch: surface silent failures on re-iterate / save-positions | rework | one-shot |
| 18 | wed#266 | Operationalize EIA scheduler (API key, first write) | rework | one-shot + weekly scheduler health |
| 19 | wed#267 | BSEE scheduler runtime fixes (HTML payloads, archive shapes) | rework | one-shot |
| 20 | ah#31 | assethold quality gates — coverage, mypy, loguru | rework | one-shot + monthly coverage drift report |

## Honorable mentions (ready to swap in)

- au#19 — package `git_all_repos_daily_commit.sh` for cross-repo use
- au#28 — extract shared loguru helper into assetutilities
- au#73 — canonical `uv run pytest` invocation + CI sanity check
- ah#5 — salvage breakout backtester prototype (6 months of fork work)
- wed#271 — wire `output_dir` into all scheduler jobs
- wed#269 — SODIR, Brazil ANP, UKCS adapters
- wed#277 — fix 130×–1570× test perf regressions
- dm#512 — GTM Demo 2 `--from-cache` fix + hermetic tests

## Promote to recurring cadence (the key addition)

These candidates aren't "fix once" — the underlying drift returns. Convert to
scheduled/cron agents or monthly GSD phases:

### Weekly
- **State sync size monitor** (wh#2070 companion) — alert when any
  `.claude/state/**` JSONL crosses 50 MB before it hits GitHub's 100 MB limit
- **Memory health report** (wh#1902 companion) — bridge-commit size, stale
  entries, duplicate topics across machines
- **Scheduler health report** (wed#266 companion) — fresh-data age per source
  (EIA, BSEE, SODIR) with red/yellow/green

### Monthly
- **Context-budget audit** (wh#1803) — token overhead of skills, MCP tools,
  memory; trend line so creeping growth is visible
- **Broken-windows test sweep** (dm#510 companion) — re-run every `pytest`
  suite, list any newly-failing tests, auto-open issues with baseline diff
- **Stale `/command` reference sweep** (wh#1731) — grep child-repo AGENTS.md
  for commands that no longer exist in the parent
- **Coverage drift report** (ah#31 companion) — per-repo line coverage delta
  vs. 30 days ago, threshold-gated
- **Session corpus mining** (wh#1720) — mine ~1M tool calls for the top
  repeated patterns worth skill-ifying

### Quarterly
- **MCP re-evaluation** (wh#1804 companion) — re-test token-optimizer,
  omega-memory claims against current ecosystem; prune MCPs that lost value
- **Control-plane contract drift audit** (wh#1525 companion) — diff each
  child repo's AGENTS.md / CLAUDE.md / MEMORY.md against the canonical
  contract; flag drift
- **External doc re-ingest** (dm#503 companion) — re-pull Orcina webhelp,
  OpenFOAM docs, any vendor references that change versions

## Recommended execution order

1. **Week 1 (guard installs):** wh#2070, wh#1902 gate, wh#2018 → stop the
   bleeding before doing rework.
2. **Week 2 (measure):** wh#1803, wh#1720 → baseline before optimizing.
3. **Week 3 (high-leverage refactors):** dm#503 + dm#109 (doc-index); then
   dm#504 as a warm-up for dm#483.
4. **Week 4 (recurring cadences):** stand up the monthly/quarterly cron
   agents; each should emit a single markdown report to `docs/reports/`.
5. **Month 2+:** wh#1839 runaway governance, dm#483 curves.py, wh#1525
   contract reopen.

## Notes

- achantas-data intentionally excluded — all open items are personal
  (travel, taxes, household) per memory rule `reference_achantas_data.md`.
- Several workspace-hub candidates overlap (#1525 ↔ #1517/1518/1523/1526,
  #1839 ↔ #1876/2012/1882); rework should consolidate rather than reopen
  each separately.
- This report will get stale — re-run this triage quarterly (which is
  itself a recurring-cadence candidate).
