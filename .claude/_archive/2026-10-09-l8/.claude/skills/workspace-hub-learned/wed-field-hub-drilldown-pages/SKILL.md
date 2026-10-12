---
name: wed-field-hub-drilldown-pages
description: Build worldenergydata drill-down pages (field hub, well timelines, insight/norm pages) with the proven validate-first playbook, the fractal IA grammar, honesty rules, and the exact wed CI gotchas.
version: 1.0.0
tags: [worldenergydata, pages, lifecycle, drill-down, insights, benchmarking, ci-gotchas]
---

# worldenergydata field-hub drill-down pages — grammar + build playbook

Use this for ANY page work in the wed field-hub family: lifecycle posters, well timelines,
insight front-doors, phase-norm/benchmark pages, atlas/browse, asset drill-downs.
Source epics: wed#754 (fractal IA), wed#764 (engineering↔asset circle), wed#774 (insight family).
Live site: https://vamseeachanta.github.io/worldenergydata/

## IA grammar (non-negotiable contract)

1. **Fractal spine:** the same "stage-gate timeline + you-are-here + deep-dive" grammar recurs at
   every zoom level — Region ▸ Play ▸ Field ▸ Well ▸ Stage. New pages reuse the grammar, never
   invent a new one per page.
2. **Both-altitudes insight contract** (#754 comment issuecomment-4881675172): every life-cycle
   insight ships at TWO altitudes — (a) a standalone indexable front-door page (traffic magnet,
   own URL, specific title) AND (b) a per-well/per-field stage deep-dive card. Same data, two zooms.
3. **Unique live links:** every capability/insight gets its OWN purpose-built page — N distinct
   pages = N front doors. Never fold into a shared "dashboards" section.
4. **Comprehensiveness bar:** thesis + a number ("4.4× vessel shortfall, $375M–$1B/yr"), not
   descriptive stats.
5. **Drill-down CTAs:** poster/hub pages gain deep-dive links only when the target exists
   (generator globs for the artifact — e.g. `wells/<id>_*_well.html` — never hardcode).

## Honesty rules (these have killed 2 pitched theses — load-bearing)

- **Validate numbers BEFORE building.** Scratchpad probe / curated spec first; delegate the build
  only with acceptance targets. Verify the built artifact independently — not the agent's report.
- **Cite-or-null:** for web-sourced facts, 1 agent per item, refuse to borrow values across fields
  (em-dash the cell instead). Curate the spec yourself before build.
- **Honest density badges:** RICH / SAMPLE / ROADMAP per data reality (freshness-scorecard).
  Thin populations → explicit "insufficient (n=X)" badge, never a fabricated norm.
- **Like-for-like bases:** never compare native V30 rig-days against calendar-day proxies; tag
  every metric with its basis and compute deltas only within one basis (wed#848 rule).
- **Curated over raw:** play-level D&C stats come from the curated FDAS_V30 xlsx (drop the blank +
  TOTALS trailer rows — filter on LEASE_NAME notna), NOT raw WAR extraction (wed#846: raw overshoots
  published figures).

## Key data sources (verified 2026-07-06)

| Source | What it gives |
|---|---|
| `docs/modules/bsee/analysis/production/FDAS_V30/drilling_and_completion_days.xlsx` | LT play population, native rig-days (SPUD/TD dates, DRILLING_DAYS, COMPLETION_DAYS, TVD, mud wt) |
| `reports/lower_tertiary/lt_well_benchmark_lower_tertiary_2010_latest.csv` | 56 wells, field-crosswalked: api12, days, first_oil, cum_oil, uptime, interventions, decline |
| `data/modules/bsee/current/wells/well_data.csv` | 57k GoM boreholes: SPUD/TD dates (calendar proxy only), BOTM_FLD_NAME_CD, BOREHOLE_STAT_CD (PA/TA), TVD |
| `reports/lower_tertiary/lifecycle/_facts.json` | list of 10 field dicts (id, play, gates, reservoir, provenance) |
| `config/fields.yml` | #755 canonical crosswalk id ⇄ name ⇄ BSEE block/lease ⇄ surfaces flags |

Join trick: benchmark `api12` ↔ well_data `API_WELL_NUMBER` → discover a field's
`BOTM_FLD_NAME_CD` codes → pull the field's full well population.

## Build pipeline conventions

- Generator scripts live in `scripts/lower_tertiary/` (or `scripts/field_atlas/` etc.); each new
  publish family needs a `build_*` domain entry in `scripts/build_pages.py` AND (if new paths)
  `config/repo_structure.yml` allowlist rows.
- **build_pages renames on publish** (underscore→hyphen, path flatten) → author cross-page hrefs
  for the PUBLIC layout, then link-check the published tree.
- Templates: `reports/lower_tertiary/lifecycle/lifecycle_template.html` (field posters, stage
  cards + engtrack lane) and `lifecycle/wells/well_lifecycle_template.html` (dual-scale well
  timeline: rig-day construction band + calendar-year production band).
- Additive lanes that share a template/`__init__.py` → ONE integration PR (squash-merge breaks
  stacked PRs). After merge, GREP the unique markup on origin/main — bundled commits get lost in
  merge races (#767 lost in #788; re-landed #803).

## wed CI gotchas (every PR)

1. **Lint = THREE steps** on `src/ tests/`: mirror ALL of `uvx black@25.9.0`, `uvx isort@6.0.1`,
   `uvx flake8@7.3.0` (flake8 runs on `src/` only — modules under `packages/*/src/` are NOT
   flake8-gated; put lint-gated modules in `src/worldenergydata/`). black-only is not enough.
   Re-verify pins against `.github/workflows/ci.yml` before pushing (versions drift).
2. "Validate PR Title": conventional type required (`polish:` FAILS) and subject after
   `type(scope):` ≤ 80 chars.
3. Tests via `./.venv/bin/python -m pytest` (plain python3 is sandbox-blocked; uv broken in wed).
4. Branch protection: 11 checks + up-to-date; main churns → `gh pr merge <N> --auto --squash
   --delete-branch` + self-healing `gh pr update-branch` on BEHIND.
5. Agent can verify but NOT self-merge; hand the human the exact merge command.
6. NEVER blind `git stash pop` (pre-existing stale stashes corrupt worktrees); `git stash list`
   first. Single-lane worktree off fresh origin/main for template-touching work.

## Related
- Plan precedent: `docs/plans/2026-07-06-issue-wed-848-phase-norm-layer.md` (phase-norm layer)
- Open family: wed#848 (norms), wed#849 (per-well economics), wed#850 (nav spine), #756/#757 (hub/econ)
- Memory: `project_wed_field_hub_ia_epic`, `feedback_unique_live_links_traffic_credibility`
