# Issue Refinement Drafts: #2055 and #2062

Generated: 2026-04-09
Source dossiers:
- `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md`
- `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md`
- `docs/plans/2026-04-09-agent-team-followup-summary.md`

---

## 1. Issue #2055 — Subsea Cost Benchmarking

### Why Refinement Is Required

The issue assumes SubseaIQ equipment-count data is available for cost correlation, but three independent gaps make the current scope unimplementable:

1. **Data file has no equipment counts.** `data/field-development/subseaiq-scan-latest.json` contains only name, operator, water_depth_m, host, year, and capacity_bopd. Zero equipment-count fields (num_trees, num_manifolds, tieback_distance_km) despite the normalize pipeline being ready to consume them.
2. **Cost schema has no equipment fields.** The 71 sanctioned `CostDataPoint` records in `worldenergydata` carry cost_usd_mm but lack equipment-count columns, so per-project cost-per-tree correlation requires either a schema extension or a separate join structure.
3. **Stated dependency is unmet.** The issue says "Depends on SubseaIQ scraping with equipment count fields." That scraping has not produced populated data. The scaffold (#1861) is done, but the cost layer is entirely absent.

Without refinement, an implementing agent will either (a) block immediately on missing data or (b) invent synthetic data without authorization.

### Refinement Draft

#### Clarified Problem Statement

Build cost-per-equipment-unit benchmark curves (cost/tree, cost/km-flowline, cost/manifold) by water-depth band, using SubseaIQ equipment counts correlated against sanctioned project costs.

**Core constraint:** The correlation requires two data sources joined by project identity or aggregated by depth band. Neither data source currently carries both cost and equipment-count fields in the same record.

#### Explicit Data Prerequisites

Before implementation begins, the following data conditions must be met:

| Prerequisite | Current State | Required State |
|---|---|---|
| Equipment counts in `subseaiq-scan-latest.json` | Absent (0 of 10 records have trees/manifolds/tieback) | At least 10 GoM fields with num_trees, num_manifolds, tieback_distance_km populated |
| Join key between SubseaIQ and CostDataPoint | Name-based, conventions differ, ~10 field overlap | Confirmed name-match mapping for the overlapping fields, documented in a mapping file or constant |
| Correlation architecture decision | Undecided | One of: (A) extend CostDataPoint schema, (B) new CostCorrelation join dataclass, (C) band-level aggregation without per-project join |

#### Scoped v1 Implementation Option

Reduce scope to what is buildable today:

- **v1 target:** Band-level cost-per-equipment aggregation (Option C from the dossier)
- **Data approach:** Manually backfill equipment counts for the 10 GoM reference fields in `subseaiq-scan-latest.json` using publicly available SubseaIQ project pages
- **Correlation method:** Aggregate equipment stats by water-depth band from SubseaIQ, aggregate costs by water-depth band from the 71 sanctioned records, compute ratios at the band level (avoids per-project name-match fragility)
- **Deferred to v2:** Per-project cost-per-tree correlation (requires CostDataPoint schema extension), cross-validation against individual sanctioned projects, full 71-record equipment backfill

#### Acceptance Criteria

- [ ] Equipment counts (num_trees, num_manifolds, tieback_distance_km) populated for at least 10 GoM fields in `subseaiq-scan-latest.json`
- [ ] `cost_per_tree(projects)` returns `dict[depth_band, float]` with values in $10M-$200M range
- [ ] `cost_per_km_flowline(projects)` returns `dict[depth_band, float]` with values in $5M-$50M range
- [ ] `cost_per_manifold(projects)` returns `dict[depth_band, float]` with physically reasonable values
- [ ] `cost_benchmark_bands(projects)` returns `dict[depth_band, dict[str, dict[str, float]]]` with low/base/high structure
- [ ] All existing 27 tests in `test_benchmarks.py` pass without modification
- [ ] New cost tests added and passing
- [ ] `benchmarks` module exported from `digitalmodel.field_development.__init__`

### Paste-Ready GitHub Issue Body Replacement

```markdown
## Summary

Build cost-per-equipment-unit benchmark curves (cost/tree, cost/km-flowline, cost/manifold) by water-depth band, correlating SubseaIQ equipment counts against sanctioned project costs.

## Problem

The scaffold (#1861) provides `SubseaProject` with equipment-count fields and `load_projects()`, but zero cost functions exist. No module currently correlates equipment counts with project costs.

## Data Prerequisites (must be met before implementation)

- [ ] Equipment counts (num_trees, num_manifolds, tieback_distance_km) backfilled for >= 10 GoM fields in `data/field-development/subseaiq-scan-latest.json`
- [ ] Confirmed name-match mapping between SubseaIQ project names and CostDataPoint project names for overlapping records

## v1 Scope (band-level aggregation)

Use depth-band-level aggregation to compute cost-per-equipment ratios. This avoids per-project name-match fragility and works with sparse data.

### New functions in `digitalmodel/src/digitalmodel/field_development/benchmarks.py`:
- `cost_per_tree(projects) -> dict[str, float]` by depth band
- `cost_per_km_flowline(projects) -> dict[str, float]` by depth band
- `cost_per_manifold(projects) -> dict[str, float]` by depth band
- `unit_cost_curves(projects) -> dict` combining all three metrics
- `cost_benchmark_bands(projects) -> dict` with low/base/high by depth band and concept type

### New helper in `worldenergydata/subseaiq/analytics/cost_correlation.py`:
- `correlate_equipment_costs(subseaiq_records, cost_records)` — depth-band-level join
- `aggregate_costs_by_depth_band(merged)` — band-level cost aggregation

## Deferred to v2

- Per-project cost-per-tree correlation (requires CostDataPoint schema extension with equipment fields)
- Cross-validation of equipment-derived costs against individual sanctioned project costs
- Full 71-record equipment-count backfill

## Acceptance Criteria

- [ ] Equipment counts populated for >= 10 GoM fields
- [ ] `cost_per_tree` returns values in $10M-$200M range per depth band
- [ ] `cost_per_km_flowline` returns values in $5M-$50M range per depth band
- [ ] `cost_per_manifold` returns physically reasonable values per depth band
- [ ] `cost_benchmark_bands` returns nested dict with low/base/high structure
- [ ] All 27 existing `test_benchmarks.py` tests pass unchanged
- [ ] New cost-related tests added and passing
- [ ] `benchmarks` exported from `digitalmodel.field_development.__init__`

## Dependencies

- #1861 (scaffold) — DONE
- Equipment-count data backfill — REQUIRED before implementation

## Labels

`enhancement`, `priority:high`, `cat:engineering`, `dark-intelligence`, `agent:claude`
```

---

## 2. Issue #2062 — Drilling Rig Fleet Adapter

### Why Refinement Is Required

The dossier headline ("2,210 rigs into hull form validation") overstates implementable scope. The follow-up review identified this as "lower-confidence" and recommended deferral. Three factors warrant issue clarification:

1. **Geometry data is critically sparse.** The CSV has no DRAFT_M column at all (not just empty — the column doesn't exist). DISPLACEMENT_TONNES is 100% empty across all 2,210 rows. Only 143 records (~6.5%) have any principal dimensions (LOA + BEAM). All 1,009 jack-ups have zero geometric data.
2. **The "2,210 rigs" title is misleading.** After implementation, only ~138 rigs (51 drillships + 87 semi-submersibles) can actually register with dimensions. The title should reflect realistic v1 throughput.
3. **Draft estimation is an unresolved architectural decision.** The dossier proposes hull-type L/D heuristics, but this approach introduces estimated-vs-measured ambiguity into the vessel registry that downstream consumers (stability calculations, mooring loads) must be aware of. The issue should explicitly state the estimation strategy and its limitations.

### Refinement Draft

#### Clarified Geometry/Data Limitations

| Rig Type | Count | Has LOA+BEAM | Has DRAFT | Has Displacement | v1 Registerable |
|---|---|---|---|---|---|
| drillship | 134 | 51 | 0 | 0 | ~51 |
| semi_submersible | 309 | 87 | 0 | 0 | ~87 |
| jack_up | 1,009 | 0 | 0 | 0 | 0 |
| platform_rig | 182 | sparse | 0 | 0 | 0 |
| Other | 576 | sparse | 0 | 0 | 0 |
| **Total** | **2,210** | **~143** | **0** | **0** | **~138** |

**Key facts for implementers:**
- DRAFT_M column does not exist in the CSV schema (23 columns; DRAFT_M is absent)
- Draft will be estimated via hull-type L/D heuristics; all estimated drafts must be flagged with `draft_estimated=True`
- Computed Cb values cannot be validated against measured displacement (no displacement data exists)

#### Scoped v1 Adapter Target

Focus on drillships and semi-submersibles with LOA+BEAM data (~138 rigs):

- **In scope:** rig-type-to-hull-form mapping, hull-form-specific Cb/Cm defaults, draft estimation from L/D heuristics, `register_drilling_rigs()` batch function, coefficient range validation
- **Success metric:** ~138 rigs registered with hull form coefficients, flagged estimated drafts, Cb within published ranges per hull type
- **Title correction:** "drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"

#### Deferred Items List

| Item | Reason for Deferral |
|---|---|
| Jack-up registration (1,009 rigs) | Zero LOA/BEAM data; requires worldenergydata CSV enrichment |
| Platform rig and other types (758 rigs) | Sparse/missing dimensions; hull form classification unclear |
| Displacement-based Cb validation | DISPLACEMENT_TONNES 100% empty; no validation reference data |
| DRAFT_M column addition to CSV | Requires worldenergydata data pipeline work; not blocking v1 with heuristics |
| Integration with stability/mooring downstream | Estimated drafts need consumer-awareness pattern; out of scope for adapter |

#### Acceptance Criteria

- [ ] `_RIG_TYPE_HULL_FORM_MAP` constant maps drillship, semi_submersible, jack_up to hull forms
- [ ] `estimate_rig_hull_coefficients(rig_type)` returns Cb/Cm/Cp dict with Cp = Cb/Cm
- [ ] Drillship Cb in [0.55, 0.70], semi-sub Cb in [0.40, 0.60], jack-up Cb in [0.75, 0.90]
- [ ] `_estimate_draft()` uses hull-type L/D heuristics and marks results with `draft_estimated=True`
- [ ] `register_drilling_rigs(records)` returns (added, skipped) tuple; skips records without LOA+BEAM
- [ ] Smoke test: load full CSV, register ~138 rigs, skip ~2,072
- [ ] All existing `test_vessel_fleet_adapter.py` tests pass unchanged
- [ ] New tests for `TestRigHullFormCoefficients` (5 tests) and `TestRegisterDrillingRigs` (5 tests)
- [ ] New functions exported from `digitalmodel.naval_architecture.__init__`

### Paste-Ready GitHub Issue Body Replacement

```markdown
## Summary

Adapter to register drilling rigs from the vessel fleet CSV into the hull form validation pipeline. v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 of 2,210 rigs).

## Problem

The vessel fleet adapter pattern (#1859) and hull form module (#1319) are complete, but no pipeline connects drilling rig CSV data to hull form coefficient estimation. The CSV lacks draft and displacement columns, so the adapter must estimate draft from hull-type heuristics.

## Data Limitations

- **NO DRAFT_M column** in `drilling_rigs.csv` (column does not exist)
- **DISPLACEMENT_TONNES is 100% empty** across all 2,210 rows
- **Jack-ups (1,009 rigs) have zero LOA/BEAM data** — will be skipped in v1
- **Only ~143 records have any principal dimensions** (51 drillships, 87 semi-subs)
- All computed drafts are heuristic estimates and must be flagged `draft_estimated=True`

## v1 Scope

### New constants in `ship_data.py`:
- `_RIG_TYPE_HULL_FORM_MAP`: drillship -> monohull, semi_submersible -> twin-hull, jack_up -> barge

### New functions in `hull_form.py`:
- `estimate_rig_hull_coefficients(rig_type: str) -> dict` — returns Cb, Cm, Cp, hull_form

### New functions in `ship_data.py`:
- `_estimate_draft(record, rig_type) -> Optional[float]` — L/D heuristics (drillship: LOA/15, semi-sub: BEAM*0.25, jack-up: LOA/8)
- `register_drilling_rigs(records, *, overwrite=False) -> tuple[int, int]` — normalize, estimate draft, map hull form, register

### Draft estimation strategy (Option A from dossier):
- Drillship: draft_ft = loa_ft / 15 (typical L/D ~14-16)
- Semi-submersible: draft_ft = beam_ft * 0.25 (pontoon draft relative to beam)
- Jack-up: draft_ft = loa_ft / 8 (barge hull, shallow draft)

## Deferred (v2 / follow-up issues)

- [ ] Jack-up registration (0 LOA/BEAM data; needs CSV enrichment)
- [ ] Platform rig and other types (sparse dimensions)
- [ ] Displacement-based Cb validation (no displacement data)
- [ ] DRAFT_M column addition to worldenergydata CSV
- [ ] Downstream consumer awareness for estimated drafts in stability/mooring

## Acceptance Criteria

- [ ] `estimate_rig_hull_coefficients` returns Cb/Cm/Cp with Cp = Cb/Cm identity
- [ ] Drillship Cb in [0.55, 0.70]
- [ ] Semi-sub Cb in [0.40, 0.60]
- [ ] Jack-up Cb in [0.75, 0.90]
- [ ] `register_drilling_rigs` skips records without LOA+BEAM, returns (added, skipped)
- [ ] Smoke test: ~138 rigs registered from full CSV, ~2,072 skipped
- [ ] All existing fleet adapter tests pass unchanged
- [ ] 10 new tests (5 hull form coefficients + 5 rig registration)
- [ ] New functions exported from `__init__.py`

## Dependencies

- #1859 (vessel fleet adapter pattern) — DONE
- #1319 (hull form parametric design) — DONE

## Labels

`enhancement`, `cat:engineering`, `domain:code-promotion`, `agent:claude`
```

---

## 3. Summary Comparison

| Dimension | #2055 (Subsea Cost Benchmarking) | #2062 (Drilling Rig Fleet Adapter) |
|---|---|---|
| **Original headline** | Cost benchmarking from SubseaIQ equipment counts | 2,210 rigs into hull form validation |
| **Actual blockers** | Equipment-count data absent; cost schema lacks equipment fields; dependency unmet | No draft column; no displacement; 93.5% of rigs lack geometry |
| **Refinement type** | Scope reduction + data prerequisite gate | Scope clarification + realistic throughput expectation |
| **v1 feasibility** | Feasible with manual 10-field backfill + band-level aggregation | Feasible for ~138 rigs with L/D draft heuristics |
| **Follow-up summary verdict** | NEEDS ISSUE REFINEMENT | Lower-confidence, benefit from clarification |
| **Post-refinement confidence** | Medium-High (if data backfill is done) | High (infrastructure complete, scope realistic) |

RECOMMENDATION: REFINE ISSUES BEFORE PLAN APPROVAL
