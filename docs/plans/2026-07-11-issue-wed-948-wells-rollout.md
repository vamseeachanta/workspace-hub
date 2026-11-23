# Plan for worldenergydata#948: Per-well timelines — Big Foot → all producing LT wells (benchmark-wide rollout)

> **Status:** adversarial-reviewed (r1 Fable subagent MAJOR/4 + MINOR/6, COMPUTED evidence @ wed 1d9a0bc → r2 this revision, all findings folded)
> **Complexity:** T2 — `_wells.json` becomes generated from committed sources; downstream (well pages, posters, Explorer) updates automatically through the shipped contracts.
> **Date:** 2026-07-11 (r2 same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/948 (parent epic #942, program #939)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** r1 findings summarized in the #948 evidence comment (subagent RAN the join, slot derivation, and Big Foot identity diff); local-only by convention.

---

## Resource Intelligence Summary

### Sources consulted (LOCAL shallow clone of origin/main @ `1d9a0bc`; r1 re-computed every join)
- **Issue #948 + epic #942 + program #939**; #946 shell + #947 global feed SHIPPED — the Explorer renders whatever lands in `_wells.json`/`_explorer.json`, zero JS changes needed.
- **`reports/lower_tertiary/lt_well_benchmark_lower_tertiary_2010_latest.csv`** — per-well production source: **56 producing wells / 7 fields** (Jack St Malo 24, Stones 10, Big Foot 8, Julia 4, Shenandoah 4, Cascade Chinook 3, Anchor 3). `api12, well(=API12), field, lease, spud, drilling_days, completion_days, first_oil, cum_oil_mmbbl, uptime_pct, interventions, intervention_history("Type YYYY-MM-DD"), decline/eur + flags`. All 56 rows have `first_oil`. kaskida/north_platte/tiber absent (0 producers) — honest no-wells state stays.
- **`reports/lower_tertiary/data/all_fields_wells.json`** (committed; extracted from V30 xlsx by `scripts/extract_all_well_data.py` which needs pandas+FUSE — its OUTPUT is committed so this wave consumes JSON with stdlib): per-bore `api, well_name, spud, td, drilling_days, completion_days, md_ft, tvd_ft, producing` for 10 LT fields (217 bores / 49 flagged). Construction side + **slot names** (`well_name`). **⚠️ r1: this file contains 93 literal `NaN` tokens; 5 matched wells carry `tvd_ft: NaN, md_ft: NaN` (Shenandoah SA007/SA010, Big Foot A003, JSM PS012/PS014).**
- **`reports/lower_tertiary/lifecycle/wells/_wells.json`** — current contract: hand-curated, Big Foot only. `mud_weight_ppg` exists ONLY here (benchmark + extract both drop it). r1-verified: derived (benchmark+V30) vs committed differs ONLY on `cum_oil_mmbbl`, and **1-dp rounding reproduces the committed value exactly for all 5 wells** (32.2351→32.2 etc.); spud/td/rig-days/tvd/first_oil/uptime/workovers all byte-identical.
- **`scripts/lower_tertiary/build_well_timelines.py`** (321 lines) — stamps `_wells.json` into `well_lifecycle_template.html`; dual-scale geometry; per-well **economics card (#849)** via `worldenergydata.field_development.well_economics` + `RegionalCostLoader` + `config/well_economics.yml`. **r1-verified: imports are stdlib+yaml only (NO pandas); runs pandas-free for all 56; venv-min needs only pyyaml.** Degrade/suppress matrix handles thin wells (0/0 rig-days → `coverage: suppressed`).
- **`reports/lower_tertiary/lifecycle/_facts.json`** — per-field `operator, host_type, region_block, play, water_depth_ft` (all 10). **⚠️ r1: has NO `lease`/`block`/`host` keys** — committed `_wells.json` `fields.big_foot` block (`lease:"G16942", block:"Walker Ridge 29", host:...`) is NOT mechanically reproducible from `_facts.json` alone (`region_block:"Walker Ridge 29 (G16942)"` — parens vary per field; JSM = `"Walker Ridge 678 (St. Malo) / 758-759 (Jack)"`, 6 leases in benchmark).
- **Downstream contracts (from #946/#947):** poster generator globs `wells/<id>_*_well.html` → `wellsHref`/`wellsCount` (L271, L285-286) and is the ONLY writer of `_explorer.json` (so posters MUST regenerate this wave); `_explorer.json` embeds `_wells.json` verbatim (L450-468) → **a NaN in `_wells.json` becomes invalid JSON in `_explorer.json` → shell `JSON.parse` throws → Explorer goes dark**; link-graph `scoped_pages()` iterates `WELLS["wells"]` and needs `WELLS["fields"][fid]["display_name"]` for all 7 producing fields; `test_explorer_wells_pages_exist` enforces page-per-well; `build_pages.py` auto-copies `*_well.html` (L446); `wells_index` nav entry already exists (nav_spine.json L66); shell route regex admits `[A-Za-z0-9-]+` slots.
- Drive-file search: not applicable.

### Gaps identified
`_wells.json` hand-curated/Big-Foot-only; no API join in code; NaN in the source extract; slot collisions (JSM PS001-008 each ×2, Big Foot A011 ×2); mud weight only in the curated file; fields-block lease/block/host not in `_facts.json`; stage-card insight links A004-only; hardcoded generator date stamps.

### Parallel-work check
No open lane touches `build_well_timelines.py` or the wells data. Re-verify open PRs at implementation start; fresh local clone (never FUSE).

## Goal

Every producing LT well in the benchmark — **56 wells / 7 fields** — gets a granular timeline page and a `_wells.json` record; posters gain `Wells (n) →`; the Explorer's wells/stage panels light up automatically. kaskida/north_platte/tiber keep the honest "no producing wells yet" state.

## Non-goals
- NO pages for non-producing bores (161 others stay in the drilling-insights aggregate; index says so).
- NO WAR re-derivation of workovers (benchmark `intervention_history` is the source).
- NO shell/template redesign — proves the #946/#947 contracts absorb 10× data.
- NO re-derivation of the V30 extract (consumes committed `all_fields_wells.json`).

## Artifact Map

| Artifact | Kind | Path |
|---|---|---|
| Wells-facts generator | new (stdlib) | `scripts/lower_tertiary/build_wells_facts.py` → regenerates `_wells.json` |
| Curated overlay | new (committed) | `reports/lower_tertiary/lifecycle/wells/_wells_overrides.json` (Big Foot mud; per-field block/host) |
| Wells contract | regenerated | `_wells.json` (56 wells / 7 field blocks) |
| Well pages | regenerated ×56 | `wells/<field>_<slot>_well.html` + `wells/index.html` |
| Posters + explorer | regenerated | `*_lifecycle.html`, `_explorer.json` |
| Generator edits | edit | `build_well_timelines.py` (NaN/null tolerance, universal insight links, dynamic date stamp) |
| Atlas note | edit + regen | `reports/field-atlas/atlas_template.html` (Explorer note copy) → regen `field-atlas/index.html` |
| Allowlist | edit | `config/repo_structure.yml`: `_wells_overrides.json` + all 56 well-page paths ENUMERATED (verify_repo_structure has NO glob, r1 f7) |
| Tests | new + edit | identity guard (wells + fields block), no-NaN gate, slot uniqueness, join contract, nulls render |

## Design decisions (r2 — r1 findings folded)

**D1 — `_wells.json` GENERATED, single-sourced, NaN-sanitized (r1 f1).**
`build_wells_facts.py` (stdlib csv/json/re/math) joins benchmark (production: `first_oil, cum_oil_mmbbl→round(_,1), uptime_pct, workovers` parsed from `intervention_history`, `status:"producing"`) with `all_fields_wells.json` (construction: `spud→spud_date, td→td_date, drilling_days→drilling_rig_days, completion_days→completion_rig_days, tvd_ft→max_tvd_ft, well_name→slot`) on **API12**. **Every numeric value passes through a sanitizer that maps `NaN`/`inf` → `None`** (`math.isnan`), because the V30 extract carries 93 NaN tokens and a raw NaN becomes invalid JSON in `_explorer.json` and kills the shell. `cum_oil_mmbbl` rounds to 1 dp and rig-days normalize to int (matches committed; r1 f2). Field blocks (D4). Curated overlay merges last (per-API + per-field patch). **Benchmark `drilling_days`/`completion_days` are CALENDAR spans (r1 f5: mismatch V30 36/55 and 34/55) — they are NEVER written to rig-days; V30 native rig-days only, per the #754 rule.**

**D2 — Identity guard extended to wells AND fields block (RED-first; r1 f2, f4).**
Test pins: the 5 Big Foot well records (derived+overlay, with the 1-dp cum rule + int rig-days) == current committed, key-for-key; AND `fields.big_foot` == committed. Big Foot legitimately GAINS 3 wells (benchmark has 8) — guard covers value identity for the 5 existing slots + the field block, not set equality.

**D3 — Slot rule incl. the one benchmark-only well (r1 f3, f6).**
`slot = V30 well_name`; on collision within a field, `slot = <name>-<api12 last4>` (JSM PS001-008 ×2 + Big Foot A011 ×2 → 18/56 hyphenated; all valid unique `[A-Za-z0-9-]`, r1-confirmed). **The 1 unmatched well — Anchor `608114076101` (a sidetrack absent from V30; empty benchmark spud/days) — gets `slot = w<api12 last4>` (= `w6101`), a thin HONEST record: first_oil/cum/uptime present, spud_date/td_date/rig-days/tvd = null (rendered as omitted, NOT calendar-span-as-rig-days).** A test asserts pairwise uniqueness of (field_id, slot) and filenames.

**D4 — Fields block sourcing (r1 f4).**
Per-field block = `{display_name, operator, host, lease, block, play}` assembled from `_facts.json` (`operator, host_type→host, play`) + a per-field entry in `_wells_overrides.json` for `lease`/`block` (NOT derivable from `_facts.json`; Big Foot `G16942`/`Walker Ridge 29` seeded from the committed file, other 6 fields curated from benchmark leases + region_block). D2 pins the Big Foot block; a schema test asserts every producing field has a non-empty block.

**D5 — Generator tolerance + universal insight links (r1 f9).**
`build_well_timelines.py`: (a) **`mud_weight_ppg` null handling fixed at L163 — `.get(k,'—')` prints "None ppg" when the key is present-but-null; use `w.get(k) or '—'`**; same omit-not-"null" rule for tvd/td (metrics L146-147, Drill card L161); (b) economics card runs for all 56 via #849, degrading/suppressing honestly (no fabrication); (c) stage cards carry two-altitude insight links (Drill→drilling-insights, Workover→intervention brief, Abandon→decom) for ALL wells (public-layout hrefs, #780); (d) **`GENERATED`/`TODAY_YEAR` hardcoded stamps → derive from a passed date or drop the date** (56 pages must not get a stale "Generated 2026-07-04").

**D6 — Honest boundaries + Explorer note (r1 f10).**
Wells index: "56 producing wells (benchmark-covered); 161 further V30 bores in the drilling-insights aggregate". kaskida/north_platte/tiber keep `wellsHref: null`. **The `atlas_template.html` Explorer note "Big Foot only today — #948" (L336-337) is now FALSE → reword ("well timelines cover benchmark producing wells; pre-production fields have none yet") AND regenerate `field-atlas/index.html`** (T-step added; reconciles the old D7/T5 conflict).

**D7 — Gates.**
(a) **No `NaN`/`Infinity` token in ANY generated JSON** (`_wells.json`, `_explorer.json`) — regex scan (r1 f1); (b) D2 identity (wells + Big Foot fields block); (c) join contract: 55 matched + 1 thin = 56 records, each with a page (`test_explorer_wells_pages_exist` → 56); (d) slot/filename uniqueness (D3); (e) no "null"/"None"/"nan" string in any generated well page; (f) exactly 7 posters carry `wellsHref`, counts == per-field record counts; (g) link-graph BFS/marker/trail green with 56 pages + all 7 field display_names present; (h) `_explorer.json` identity with the new wells block; (i) every producing field block non-empty (D4).

## Implementation steps

| # | Step | Files |
|---|---|---|
| T1 | RED-first: D2 identity test (wells + fields block) against current `_wells.json` | tests |
| T2 | `build_wells_facts.py` (D1/D3/D4 + NaN sanitizer) + `_wells_overrides.json` (Big Foot mud + 7 field blocks) | new script + overlay |
| T3 | Regenerate `_wells.json`; run D2 guard + no-NaN scan; commit | artifact |
| T4 | `build_well_timelines.py` edits (D5); regenerate 56 pages + index | generator + artifacts |
| T5 | Regenerate posters + `_explorer.json`; edit atlas note + regenerate `field-atlas/index.html` (venv-min + pyyaml) | artifacts |
| T6 | Enumerate 56 well-page paths + overlay in repo_structure.yml; full gate suite + new tests (D7) | config + tests |
| T7 | Lint mirror; PR `feat(explorer): …` ≤80ch; auto-merge; post-deploy live verify (Stones + JSM wells tables in shell, a JSM stage panel, Big Foot A004 unchanged, kaskida honest note, Explorer NOT dark = no NaN) | — |

## Acceptance mapping (issue #948 → plan)

| Criterion | Delivered by |
|---|---|
| Every rich LT field with V30 rows → wells pages + `_wells.json` (dual-scale, native rig-days) | D1-D4 (7 producing fields; 3 pre-production honest, D6) |
| Posters gain `wellsHref` where wells exist | auto via poster glob (D7f) |
| Stage cards link insights beyond A004 | D5(c) |
| Gate asserts data-driven hrefs resolve | existing + D7 |
| Honest handling of sparse fields | D3 thin record, D5 economics degrade, D6 |

## Risks & mitigations
- **R1 NaN kills Explorer** → sanitizer (D1) + no-NaN gate (D7a); r1 already proved 5 wells carry it.
- **R2 Big Foot regression** → D2 guard (wells + block) + overlay + 1-dp cum rule.
- **R3 unmatched Anchor sidetrack** → explicit `w<last4>` slot + thin honest record (D3).
- **R4 fields block silent regression** → D4 sourcing + D2 extended + non-empty gate (D7i).
- **R5 slot collisions** → D3 rule + uniqueness test (18/56 hyphenated, r1-confirmed valid).
- **R6 economics on thin wells** → #849 degrade/suppress; pandas-free (r1 f8); venv-min+pyyaml.

## Ops notes for the implementer
Local shallow clone (FUSE git hangs), venv-min (+pyyaml), heredoc python, `-o addopts="" --noconftest`, agent verifies / human merges. `all_regions_atlas.html` embeds `date.today()` — never commit its regeneration. Verify the Explorer does NOT throw in the browser (the NaN failure mode is silent in Python, fatal in JS).
