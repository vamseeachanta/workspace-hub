# Plan for worldenergydata#849: Per-well economics drill-down — D&C days → cost, production → revenue on the well timeline

> **Status:** adversarial-reviewed (r1 Claude MAJOR/8 + r2 Codex MAJOR/11 → r3 inline patch, this revision)
> **Complexity:** T2
> **Date:** 2026-07-06 (r3 same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/849 (repo: **worldenergydata** — attestation-vs-repo mismatch is a known tooling artifact; all evidence wed-repo-qualified)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-wed849-claude.md (MAJOR/8, repo-verified @ wed 7ba6821a) | ...-codex.md (MAJOR/11) — local-only dir by convention; durable evidence via issue comment

---

## Resource Intelligence Summary

### Existing repo code (verified against worldenergydata `origin/main`, 2026-07-06; r1 reviewer independently re-verified @ 7ba6821a)
- `reports/lower_tertiary/lifecycle/wells/_wells.json` — 5 Big Foot wells (A001/A002/A004/A006/A008) with `api` (STRING), `drilling_rig_days, completion_rig_days, spud_date, td_date, first_oil, cum_oil_mmbbl, uptime_pct, workovers, max_tvd_ft, status`. A008: spud 2013 → TD 2021 but 118 rig-days → cost MUST use rig-days, never calendar spans.
- **Cost substrate (r1-verified):** `config/analysis/cost_data/day_rates.yml` — GoM `drilling/completion/intervention` × bands × **individually-indexed years 2020-2025** (⇒ interpolation never fires for in-range years; ≤2020 clamps to 2020 inside `_interpolate_year`), `hpht_premium_factor: 1.30`, mob/demob excluded, proxy/medium confidence. `RegionalCostLoader.get_day_rate()` (r1-verified signature/units: USD/day) + **existing `classify_water_depth_band(depth_m)` (METRES) returning the `WaterDepthBand` enum** — the plan does NOT reinvent band mapping (r1 F4); explicit ft→m conversion (× 0.3048) feeds it. Loader default config path is in-tree-relative (`parents[7]`) → builder passes `config_dir` explicitly (r1 F8).
- **Revenue substrate (r1-verified):** `well_benchmark.py` `est_revenue_mm` = **gross revenue, monthly BSEE production × monthly EIA WTI, in $MM** ; `revenue_flag` domain verified; **all 5 Big Foot wells present with non-null est_revenue_mm (2324.5 / 1576.2 / 910.3 / 359.1 / 103.4)**. HAZARD (r1 F2): pandas reads `api12` as int64 while `_wells.json` `api` is a string — the join MUST read `api12` with `dtype=str`; a silent dtype miss degrades ALL 5 revenue rows to "unavailable".
- **bench_row projection rule (r1 F7):** the benchmark CSV also carries calendar-span `drilling_days/completion_days` that contradict `_wells.json` rig-days by up to 29× (A008: 3,400 vs 118). Only `est_revenue_mm` + `revenue_flag` are projected out of the benchmark row; day counts come SOLELY from `_wells.json`.
- `scripts/lower_tertiary/build_well_timelines.py` + `well_lifecycle_template.html` — `__WELL_JSON__` stamping + card structure support an economics block cleanly (r1-verified).
- Big Foot water depth ≈ 5,200 ft = **1,585 m → deep band** (r1-verified); the ft/m trap is real (feeding feet into the metres classifier yields ULTRA_DEEP, ~+20% rate) → conversion is test-pinned at every band boundary.
- #848 (plan-approved, play-norms-only v1): `_norms.json` consumed by comparison chips when present; degradation states below.
- CI fact correction (r1 F8): wed `Lint` = black + isort on `src/ tests/`, **flake8 on `src/` ONLY**.

### Standards
Not applicable — proxy estimates from in-repo rate DB + BSEE production; provenance carried in the economics block schema.

### LLM Wiki pages consulted
None relevant. Ecosystem-data hook: drilling-well domain home = worldenergydata; day-rate DB is in-repo canonical (WRK-171 lineage).

### Documents consulted
wed#849 (contract) · epic #754 (grammar) · #848 approved plan + r1/r2 findings (honesty rules inherited) · #844 (cost-basis time-series = upgrade path; this plan stays config-compatible) · #758 (well-timeline substrate) · #846 (curated-source rule) · `docs/plans/README.md` (no prior #849 plan) · skill `workspace-hub-learned/wed-field-hub-drilldown-pages` · drive-file index (`"rig day rate well cost revenue"`, `--caller plan-resource-intel`): nothing beyond in-repo sources.

### Gaps identified (built from scratch)
`src/worldenergydata/field_development/well_economics.py` · `config/well_economics.yml` · economics card in `well_lifecycle_template.html` · builder enrichment · tests.

### Evidence (embedded verification)
- Issue states: wed#849 OPEN; wed#848 OPEN `status:plan-approved` (marker `.planning/plan-approved/wed-848.md`); wed#844/#758 OPEN.
- Substrate probes: this session's greps + the r1 artifact's "What I verified" (loader signature/units, hpht 1.30, completion tables deep/ultra_deep 2020-2025, revenue computation & flag domain, all-5 benchmark rows with values, template mechanism, 5,200 ft → deep).
- **Reproduction proofs: N/A — new-feature plan**; adversarial repo-verification stands as evidence.
- Parallel-work check (2026-07-06): no open PR/worktree touches the wells family → **single-lane** worktree off fresh origin/main. #848's lane touches the FIELD template (disjoint); only `build_pages.py` shared (trivial-additive).

## Artifact Map
| Artifact | Kind | Path |
|---|---|---|
| Economics engine | new module | `src/worldenergydata/field_development/well_economics.py` |
| Config | new YAML | `config/well_economics.yml` (display policy, per-field hpht flags, fallback hierarchy, disclosure strings) |
| Enrichment | edit | `scripts/lower_tertiary/build_well_timelines.py` (attach `WELL.economics`; explicit `config_dir` to loader; `dtype=str` CSV read) |
| Card UI | edit | `reports/lower_tertiary/lifecycle/wells/well_lifecycle_template.html` |
| Tests | new | `tests/unit/field_development/test_well_economics.py` |
| Regenerated | artifacts | 5 well pages; `_wells.json` byte-identical (facts stay facts) |

## Deliverable
Economics card on each well page — four elements + assumptions block:
1. **Construction cost (proxy)** — `drilling_rig_days × drill rate(vintage year, gom, band, hpht)` + `completion_rig_days × completion rate(vintage year, …)` via `RegionalCostLoader` + `classify_water_depth_band(ft × 0.3048)`. Label: `proxy · medium confidence · excl. mob/demob & services`.
2. **Revenue to date** — benchmark `est_revenue_mm` verbatim, cited "gross · BSEE monthly production × EIA WTI monthly"; `revenue_flag` rendered next to the number when non-clean.
3. **Gross-revenue coverage (indicative)** — revenue ÷ proxy cost, renamed from "payback" (r2 F6): the card states in one line that revenue is **gross** (pre-royalty ~18.75%, pre-working-interest) and cost is **rig-time proxy only** (no services/facilities/opex/P&A/discounting) — both omissions inflate the ratio in the same direction (r1 F6), so it is labelled *indicative, upper bound*. **Degrades**: any clamped rate OR non-clean revenue_flag → ratio shown as "indicative (degraded basis)" with the reason; missing either side → not rendered.
4. **Comparison chips** — well drill-days & days/1000 ft vs field/play medians from `_norms.json` when present; degraded states: absent file → "norms pending (#848)"; malformed/partial → same pending state + build-log warning (never a crash, never a partial fabrication) (r2 F9).
Assumptions block: exact rate cells used (activity/band/year/USD-day/`rate_status`), hpht flag, revenue citation + flag, config links. All policy in `config/well_economics.yml`.

### Correctness rules (r3-hardened)
1. **Units canonical** (r2 F1): internal arithmetic in `cost_usd` (float USD); serialized/display as `cost_mm_usd = cost_usd / 1_000_000` with fixture-exact conversion test; display label "$MM" everywhere; no "MUSD" naming anywhere in code or JSON.
2. **Rig-days only** for cost; benchmark day columns never enter the cost path (structural: `bench_row` projected to `(est_revenue_mm, revenue_flag)` before compute — r1 F7).
3. **Rate vintage hierarchy** (r1 F5, r2 F4): drilling → spud year; completion → `completion_end_year` if ever present → **first-oil year** → TD year (last resort, flagged `early_biased`). Fallback used is recorded in `rate_cells`.
4. **Clamp semantics** (r1 F1/F3, r2 F5): DB year range derived from the loaded YAML itself (no hardcoded 2020/2025); requested year outside range → loader's clamped value + `rate_status='clamped'` (vs `'exact'`); any clamped cell degrades the coverage ratio per Deliverable 3. In-range years hit exact per-year values (interpolation never fires — test reflects reality, not the imagined interpolation).
5. **Join safety** (r1 F2): benchmark CSV read with `dtype={'api12': str}`; join key = zero-padded 12-char string both sides; **golden test against the real CSV** asserts all 5 tracer wells join with non-null revenue.
6. **Depth band** (r1 F4, r2 F3): reuse `classify_water_depth_band(depth_m)` + `WaterDepthBand` enum; ft→m via named constant `FT_TO_M = 0.3048`; boundary tests at every band edge in BOTH units.
7. **hpht config-gated per field** (default false; mud weight never consulted).
8. **Non-producing/missing matrix** (r2 F8) — explicit render table (config-driven strings):
   | condition | cost row | revenue row | ratio |
   |---|---|---|---|
   | producing + clean | value | value | indicative |
   | producing + flagged revenue | value | value+flag | degraded |
   | shut-in / drilling / abandoned | value if days>0 | value or "unavailable" | suppressed |
   | zero/None days | "insufficient data" | value | suppressed |
   | no benchmark row | value | "unavailable" | suppressed |

## Pseudocode (core module)
```python
FT_TO_M = 0.3048
@dataclass(frozen=True)
class RateCell: activity, band, year_requested, year_used, usd_per_day, rate_status, vintage_fallback, hpht_applied
@dataclass(frozen=True)
class WellEconomics:
    drill_cost_usd, completion_cost_usd, construction_cost_usd  # internal USD
    rate_cells: list[RateCell]
    revenue_mm_usd, revenue_flag, revenue_source
    coverage_ratio, coverage_status  # indicative | degraded | suppressed (+reason)
    status, notes
    def to_json(self): ...  # serializes *_mm_usd fields only, schema_version'd

def compute_well_economics(well, field_ctx, revenue: tuple[float,str]|None,
                           loader: RegionalCostLoader, cfg) -> WellEconomics
```
Builder: load benchmark once (`dtype=str` keys) → project revenue tuple per api → compute → embed `WELL["economics"]` → template card. Loader constructed with explicit `config_dir` (repo-root derived, not `parents[7]` default).

## Files to Change
1. `src/worldenergydata/field_development/well_economics.py` (new)
2. `config/well_economics.yml` (new)
3. `scripts/lower_tertiary/build_well_timelines.py` (enrich; `_wells.json` NOT mutated)
4. `reports/lower_tertiary/lifecycle/wells/well_lifecycle_template.html` (card + chips)
5. `tests/unit/field_development/test_well_economics.py` (new)
6. Regenerated: 5 well pages

## TDD Test List (write first, confirm red)
1. `test_cost_units_exact` — 118 days × 175,000 USD/day → `construction_cost_usd=20_650_000`, serialized `20.65` `$MM` (r2 F1).
2. `test_cost_uses_rig_days_never_benchmark_calendar` — A008 fixture: 118 rig-days used; a poisoned bench_row with 3,400 days cannot reach the cost path (projection enforced) (r1 F7).
3. `test_rate_year_exact_in_range_and_clamped_below` — 2023 → exact 2023 value (no interpolation); 2012 → 2020 value + `rate_status='clamped'`; range derived from fixture YAML, not literals (r1 F1/F3).
4. `test_vintage_fallback_hierarchy` — completion with first_oil present → first-oil year; without → TD year + `early_biased` (r1 F5, r2 F4).
5. `test_depth_band_ft_to_m_boundaries` — 5,200 ft → deep; every band edge ± ε in ft and m; feet-into-metres misuse caught (enum + conversion pinned) (r1 F4, r2 F3).
6. `test_loader_contract_against_real_class` — real `RegionalCostLoader` + fixture `day_rates.yml` via explicit `config_dir`: signature, USD/day return, hpht 1.30 (r2 F2, r1 F8).
7. `test_golden_join_real_benchmark_csv` — reads the REAL CSV with `dtype=str`: all 5 tracer apis join, revenues equal (2324.5, 1576.2, 910.3, 359.1, 103.4) (r1 F2).
8. `test_coverage_matrix` — each row of the render matrix incl. clamped→degraded, flagged→degraded, non-producing→suppressed, zero-days→suppressed (r2 F6/F8).
9. `test_norms_degradation_variants` — absent, malformed JSON, partial (field present/play missing) → pending state, build succeeds, warning logged (r2 F9).
10. `test_no_hardcoded_monetary_literals` — guard scans module AND builder diff for USD numerics; `FT_TO_M` whitelisted as named constant (r2 F10).
11. `test_all_five_pages_render_card` — generated HTML for all 5 wells contains card + assumptions links; degraded fixtures render their states; `_wells.json` byte-identical pre/post build (r2 F11).
12. `test_hpht_flag_config_gated` — mud weight never consulted.

## Acceptance Criteria
- [ ] All 5 Big Foot well pages show the economics card (cost / revenue+flag / coverage per matrix) with assumptions block and proxy labelling
- [ ] Monetary policy entirely in `day_rates.yml` + `config/well_economics.yml`; zero hardcoded rates (test-enforced, module+builder)
- [ ] Coverage ratio labelled *indicative, upper bound* with the gross-vs-proxy disclosure; degrades/suppresses per matrix
- [ ] Norms chips consume `_norms.json` with all three degradation variants handled
- [ ] 12 TDD tests pass incl. the real-CSV golden join; regenerated pages link-check clean; `_wells.json` untouched; PR screenshots show nominal + one degraded card
- [ ] Poster → well page → economics chain has no dead ends

## Risks
1. Proxy misread as actual cost → labels + disclosure line + indicative-upper-bound framing (r2 F6 resolved).
2. Old spuds priced at 2020 floor (A001 2012) → clamped status degrades the ratio; #844 time-series is the upgrade path.
3. Completion-vintage residual error even with first-oil fallback (A008 ~17%/$5M scale) → fallback recorded per cell; acceptable for a proxy labelled as such.
4. Template race — wells family disjoint from #848's field template; `build_pages.py` trivial-additive; single-lane + post-merge markup grep.
5. CI: black+isort on `src/ tests/`, **flake8 on `src/` only** (corrected per r1 F8); re-verify pins in `.github/workflows/ci.yml`; PR title subject ≤80; `./.venv/bin/python -m pytest`.
6. Scope guard: no NPV/opex/royalty modelling at well level — field economics page owns that; card language enforces the boundary.

## Adversarial Review Summary
- **r1 (Claude subagent, repo-verified @ wed 7ba6821a): MAJOR/8** — artifact `...-plan-wed849-claude.md`. Verified-clean list: loader signature/units, hpht factor, completion tables, revenue semantics ($MM gross, monthly WTI), flag domain, template mechanism, deep-band placement.
- **r2 (Codex dispatch): MAJOR/11** — artifact `...-plan-wed849-codex.md`.
- **r3 (this revision, inline per `feedback_r3_inline_loop_break_pattern`):** impossible interpolation test → per-year-exact + clamp test tied to fixture-derived range (r1 F1/F3, r2 F5); dtype join hazard → `dtype=str` + real-CSV golden test (r1 F2); band mapping → reuse `classify_water_depth_band` + enum + `FT_TO_M` boundary tests (r1 F4, r2 F3); completion vintage → first-oil-first hierarchy + `early_biased` flag (r1 F5, r2 F4); ratio framing → "gross-revenue coverage (indicative, upper bound)" + royalty/WI disclosure + degrade/suppress matrix (r1 F6, r2 F6/F8); bench_row projection (r1 F7); loader `config_dir` + builder imports + flake8-scope correction (r1 F8); canonical units + conversion test (r2 F1); loader contract test (r2 F2); revenue semantics verified + flag display rule (r2 F7); norms degradation variants (r2 F9); widened hardcode guard (r2 F10); all-5-pages render + `_wells.json` byte-identity tests (r2 F11).
- Awaiting user approval; not self-labeled.
