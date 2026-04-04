# Engineering Modules — Detailed Memory

> Detailed records for worldenergydata engineering modules. Referenced from MEMORY.md.

## Wall Thickness Design Code Framework (WRK-144/145/155/158, DONE 2026-02-16)
- **WRK-144**: 2 new strategy classes (API RP 2RD WSD, API STD 2RD LRFD), `958e18a2f`
- **WRK-145**: Edition versioning — CodeEdition dataclass, edition-aware factors, `2a1dc217f`
- **WRK-155**: DNV-ST-F101 edition versioning (2007/2021), M-T report conditions, `74bd37f86`
- **WRK-158**: Parametric sweep Excel export, `0aff96687`
- **Extension pattern**: DesignCode enum + `@register_code` + `CONDITIONS_BY_CODE` + parameterized M-T report
- **Edition pattern**: `EDITION_FACTORS[year]` dict, `Strategy(edition=None)` defaults to latest
- **Key learning**: Reports use `code.value` (hyphenated e.g. "API-RP-2RD"), tests must match
- **Tests**: 325 total wall_thickness tests, 23 parametric tests

## Fatigue Module (WRK-157 Phases 1-2, 2026-02-16)
- **48 S-N curves** across 4 standards (DNV 14, API 5, BS 8, AWS 8, + multislope)
- S-N comparison report: `sn_comparison_report.py` — Plotly overlay, DFF bands, parameter tables
- 513 fatigue tests passing; `data/fatigue/sn_curves.yaml` may be locally deleted — restore via `git checkout HEAD --`

## Cost Data Layer (WRK-019, DONE 2026-02-17)
- **Path**: `src/worldenergydata/bsee/analysis/cost/` (5 source files + config YAML)
- **Tests**: 59 passing in `tests/modules/bsee/analysis/cost/` (5 test files)
- **Components**: CostEstimate (frozen), FieldCostSummary, CostEstimationEngine, DayRateLoader, depth_classifier
- **Config**: `config/analysis/cost_data/day_rates.yml` (GOM rates 2020-2025)
- **Pattern**: Phased `__init__.py` with `try/except ImportError` for incremental delivery
- **Bug fixed**: `day_rate_loader.py` default path needed `parents[5]` not `parents[4]`
- **Follow-up**: WRK-171 — calibrate proxy rates against real sanctioned project costs

## Metocean Statistics Engine (WRK-170, DONE 2026-02-17)
- **Path**: `src/worldenergydata/metocean/statistics/` (9 source files, 1,748 LOC)
- **Tests**: 80 tests (76 pass, 4 skip) in `tests/modules/metocean/statistics/` (5 files, 792 LOC)
- **Components**: EVA (block maxima GEV + POT GPD), scatter diagrams, weather windows/operability, Plotly HTML reports
- **Optional deps**: 3-tier — Tier 0 scipy, Tier 1 metocean-stats, Tier 2 virocon
- **Patterns**: `_backends.py` (lazy import + `has_X()`/`require_X()` with install hint), `_converters.py` (HarmonizedObservation <-> DataFrame bridge), frozen result dataclasses
- **Plotly reports**: CDN-based, f-string HTML template, follows `sn_comparison_report.py` pattern

## EVA / Statistics Testing Learnings
- **Bootstrap CI with small samples**: With <=5 annual maxima, bootstrap CIs degenerate. Use >=10 years for reliable CIs.
- **POT declustering paradox**: Lower percentile threshold + 48h declustering can yield *fewer* independent peaks than higher threshold.
- **EVA test speed**: Bootstrap-heavy tests take ~6 min. Use `--no-cov` and reduced `n_bootstrap=50` for faster iteration.

## BSEE Binary Data State (post WRK-098)
- 129 of 133 `.bin` files are **Git LFS pointer stubs** (~130 bytes each, not materialized)
- Only 4 real files: `production_raw/mv_productionsum.bin`, `mv_productionsumwd.bin`, `mv_production_waterdepth.bin`, `rig_fleet/rig_fleet.bin`
- Detect LFS stubs: check first 40 bytes for `b"version https://git-lfs"`
- All new loaders must handle LFS stubs gracefully (return empty DataFrame)

## Rig Fleet
- **Paths**: `src/worldenergydata/bsee/data/loaders/rig_fleet/`, schema, model, fleet binary
- **Data catalog**: `data/catalog/data-catalog.yml` (9 modules, 356 datasets, 6.8GB)
- **XLS Assessment**: 10 XLS files, ~80 fields, master `DrillRigs.xls` (transposed layout)
- **NEVER reference** `0113` or `Orc DR` in ported code/comments/commits

## AI Tools for Standards & Rules

- **DNV RuleAgent** — AI assistant embedded in DNV Veracity portal for rule/guidance lookup
  - Source: LinkedIn post (DNV, 2026-03-11)
  - Features: natural-language Q&A → direct links to applicable rule sections; vessel-specific filtering (narrows to ship/floater type); used internally at DNV for 1+ year, now external
  - Access: DNV Veracity portal (external DNV customers)
  - **WRK idea**: build analogous capability for workspace — semantic search over DNV/API/ABS/BS PDFs already in `docs/domains/` (CP standards, wall thickness codes, fatigue S-N curves); tie into document-index (1M+ records) + MCP semantic scholar; relevant to WRK-272/277 (CP) and future standards work

## Vessel Loading Software

- **Autoload 6** — offshore vessel loading computer; 3D-based stability, crane ops, cargo management
  - Ref: https://autoship.com/autoload-6-the-new-generation-software/
  - Features: real-time stability/draft survey, drag-and-drop deck cargo, crane load indicators (green/red), damage simulation, wind heeling, dual-lift crane, first-principles 3D calcs (not lookup tables)
  - Relevant to: hull library stability validation, vessel loading simulations, crane sequence planning

## Hull Library Quality Tracking
- **Displacement validation**: Cross-check against `Cb * L * B * T * rho_sw` (rho_sw=1.025 t/m3)
- **Mesh vertical resolution**: Barge=5 waterline offsets, ship/LNGC=7. Keep consistent for fair comparison.
- **Track per hull**: mass (displacement_t), draft_m, Cb, mesh panel density (panels/m2)
- **Catalog fields**: `displacement_t` and `block_coefficient` for all parametric hulls in `hull_panel_catalog.yaml`

## Daily Strategy Tool (WRK-189/WRK-189-ext, DONE 2026-02-18)

- **Repo**: `assethold/src/assethold/analysis/daily_strategy/`
- **Tests**: 197 tests in `tests/unit/analysis/daily_strategy/` (all pass, `uv run`)
- **Output**: `.md` (archival) + `.html` (primary, self-contained Plotly) in `reports/daily-strategy/`
- **Key patterns**:
  - `ComparisonLoader`: synthetic `shares=0, account="Watchlist"` positions — score without weight signal
  - `Optional[T] = None` on dataclass fields extends backward-compatibly (existing tests unmodified)
  - Plotly JSON: `json.dumps(payload, allow_nan=False, default=lambda o: None)` — required for NaN
  - HTML report: inline CSS, CDN Plotly.js, f-string template, `generate()→str` + `write()→Path`
  - Purple gradient header: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` — from plotly_report_template
  - `--compare AAPL,MSFT` CLI + `watchlist:` config auto-loads when flag absent
- **assethold git history**: `src/analysis/` was entirely untracked before WRK-189-ext — first commit included all source
- **uv.lock**: committed alongside pyproject.toml changes; `uv sync` must be run before tests

## Production Engineering Module (WRK-164, DONE 2026-02-19)

- **Repo**: `digitalmodel/src/digitalmodel/production_engineering/`
- **Tests**: 93 tests, 0 failures in `tests/production_engineering/`; commit `7b6067fd1`
- **Core insight**: data quality is the bottleneck in nodal analysis, not algorithm choice (4 AI service companies failed for this reason)
- **Modules**:
  - `test_quality_scorer.py` — 5-criteria scorer (0-100): duration, stabilization, drawdown, separator, gas lift
  - `nonlinearity_flags.py` — transient flow, slug flow, gas lift instability, choke criticality, high watercut
  - `ipr_models.py` — Vogel (1968), Fetkovich (1973), Linear PI, Composite (Klins-Clark)
  - `vlp_correlations.py` — Hagedorn-Brown (1965) + Beggs-Brill (1973) pressure traverses + `vlp_curve()`
  - `nodal_solver.py` — Brent's method on IPR/VLP residual; confidence bounds: Green ±5%, Amber ±15%, Red ±30%
  - `gigo_detector.py` — physics-based divergence diagnosis (watercut change, stabilization, reservoir depletion)
  - `reconciliation_workflow.py` — end-to-end QC → calibrate → confidence → recommendations
- **Key Vogel formula**: `q/qmax = 1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)²`
- **Composite IPR kink**: linear above bubble point (PI model), Vogel below; `qmax = q_b + PI*Pb/1.8`
- **Test command**: `PYTHONPATH=src python3 -m pytest tests/production_engineering/ -v` (no `--noconftest`)

## worldenergydata sodir Module (pre-existing, check before WRK-190)

- **Path**: `worldenergydata/src/worldenergydata/sodir/`
- **Files**: `api_client.py`, `forecasting.py`, `npv_norway.py`, `cross_regional.py`, `analysis.py`, `batch.py`, `cache.py`, `datasets.py`, `visualization.py`, etc.
- **Status**: substantial NCS module already exists; audit before starting WRK-190 (NPD/Sodir integration)
- **Risk**: WRK-190 may be mostly/partly done already — diff against the spec before writing new code

## Cathodic Protection Module (CP-stream, 2026-02-20/21)

- **File**: `digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py`
- **Router**: `CathodicProtection().router(cfg)` dispatches on `cfg["inputs"]["calculation_type"]`
- **Routes implemented**: `ABS_gn_ships_2018`, `DNV_RP_F103_2010` (fixed WRK-279)
- **Routes pending**: `ABS_gn_offshore_2018` (WRK-277, Route C), `DNV_RP_B401_offshore` (WRK-272, Route C)
- **Tests**: 96 passing in `tests/specialized/cathodic_protection/` (5 test files)
- **Standards inventory**: `docs/domains/cathodic_protection/standards-inventory.md` (WRK-269 — authoritative)
- **Calc library**: `docs/domains/cathodic_protection/examples/` — calc-001..011 + example-01/02/03
- **Brochure**: WRK-273 pending (Route A, unblocked — next up)

### DNV F103-2010 cfg structure (after WRK-279 fix)
```python
cfg = {"inputs": {"calculation_type": "DNV_RP_F103_2010",
  "pipeline": {"outer_diameter_m": float, "length_m": float, "wall_thickness_m": float,
               "burial_condition": "non_buried"|"buried",
               "internal_fluid_temperature_C": float,   # Table 5-1 lookup
               "coating_type": "FBE"|"3LPE"|"3LPP"|"asphalt"|...},  # Annex 1 lookup
  "environment": {"seawater_resistivity_ohm_m": float},
  "design_data": {"design_life_years": float, "anode_utilization_factor": float,
                  "electrochemical_capacity_Ah_kg": float}}}
```

### G-1 to G-5 Critical Defect Fixes (WRK-279, commit de6990277)
- **G-1/G-2**: `_dnv_current_densities` — `_F103_2010_TABLE_5_1` (burial × temp mA/m²); removed coating-quality lookup
- **G-3**: Arrhenius correction removed entirely
- **G-4**: `_dnv_coating_breakdown` — linear `f_cm = a + 0.5*b*t_f`; `_F103_2010_TABLE_A1` (FBE, 3LPE, asphalt, bare)
- **G-5**: `_dnv_pipeline_geometry` RL — F103-2010 Eq.11: `rho_Me / (pi * d * (D-d))`; default 0.2e-6 Ω·m (CMn)

### Abstracted Calc Library (WRK-276/280)
- 11 `.md` files: calc-001..009 (WRK-276) + calc-010/011 (WRK-280 FST documents)
- 3 deny lists created: `digitalmodel/`, `saipem/`, `acma-projects/` `.legal-deny-list.yaml`
- Legal CI gate: `digitalmodel/.pre-commit-config.yaml` has `legal-sanity-scan` hook
  - Entry: `scripts/legal/legal-sanity-scan.sh --repo=digitalmodel` (NOT `../scripts/...`)
- Note: saipem and acma-projects have NO pre-commit config — manual scan gate only

### Route C items pending plan gate
- **WRK-272**: DNV-RP-B401 offshore — jacket structures; B401-2021 PDF at `acma-projects/B1522/ctr-2/cal/DNV-RP-B401-2021.pdf`
- **WRK-277**: ABS GN Offshore 2018 — PDF at `digitalmodel/docs/domains/cathodic_protection/codes/ABS cathodic-protection-offshore-gn-dec18.pdf`
- Both require plan gate + Codex cross-review before implementation

## Repo Routing Rule — Wind Energy Work

**Wind resource / AEP** → `worldenergydata` (energy data domain: atlas → production → economics)
**Wind-induced structural loads / fatigue** → `digitalmodel` (engineering calculations)

Boundary test: "Is it energy data/economics?" → worldenergydata. "Is it a structural or hydrodynamic calculation?" → digitalmodel.

## Wind Energy Module (WRK-688, eval in progress)

- **Tool**: pyWAsP — Python API for WAsP (DTU Wind Energy / Ørsted)
- **Docs**: https://docs.wasp.dk/pywasp/latest/
- **Key reference**: https://docs.wasp.dk/pywasp/latest/getting_started/working_with_xarray_and_windkit.html
- **WindKit data structures**: spatial formats = point / raster / cuboid; wind climate types = TSWC / BWC / WWC / GWC; topography = elevation, roughness, land cover; CRS-aware
- **xarray-native**: WindKit Datasets align with worldenergydata metocean module plans (NOAA NDBC)
- **Companion**: PyWake (MIT licence) — AEP + wake modelling without WAsP licence; evaluate as free entry point
- **GTM relevance**: Orsted, Equinor, CVOW (Tier 3 targets, WRK-148) use WAsP daily
- **Spec entry**: `specs/data-sources/worldenergydata.yaml` tools → pywasp
- **Gap entry**: `specs/data-sources/worldenergydata.yaml` gaps → wind-resource-assessment
- **WRK-688**: eval — install, WindKit xarray compat, AEP example, licence assessment, eval report → `specs/data-sources/pywasp-eval.md`

## Archived WRK Items (Condensed)
- **WRK-096** (02-08): Module flatten `worldenergydata.modules.X` → `worldenergydata.X`
- **WRK-097**: Data residence 3-tier policy (Collection→wed, Engineering→dm, Project→repos)
- **WRK-098** (02-08): Git history 4.1GB→177MB, 6 filter-repo passes
- **WRK-011** (02-08): All-fields BSEE analysis, 54 tests, paleowells era classification
- **WRK-067/068/071** (02-10): HSE imports — OSHA 29.5K + BSEE 68.5K + EPA TRI 51.5K
- **WRK-104/135** (02-12/13): Rig fleet 2,268 rigs, hull mapping
- **WRK-102** (02-13): Hull form classification 1,674/2,268 rigs
- **WRK-119** (02-12): 3-tier test runner, 603 tests in 5.6s
- **WRK-014** (02-16): HSE risk index module + website visualization
- **WRK-079** (02-16): Marine safety correlation case study HTML
- **WRK-105** (02-16): Drilling riser component data, 56 tests
- **WRK-170** (02-17): Metocean statistics engine, 80 tests
- **WRK-164** (02-19): Production engineering — well test quality + nodal analysis, 93 tests, `digitalmodel`
