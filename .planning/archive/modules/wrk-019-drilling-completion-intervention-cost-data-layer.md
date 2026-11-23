---
title: "WRK-019: Drilling, Completion & Intervention Cost Data Layer"
description: "Cost estimation engine for BSEE GOM data using proxy-based day-rate calculations"
version: "1.0"
module: "worldenergydata/bsee/analysis/cost"

session:
  id: "wrk-019-plan"
  agent: "claude-opus-4-6"

review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  ready_for_next_step: false

status: "draft"
progress: 0
priority: "low"
tags: [cost-data, bsee, gom, proxy-estimation]

created: "2026-02-16"
updated: "2026-02-16"
target_completion: "2026-02-17"

links:
  spec: ".claude/work-queue/pending/WRK-019.md"
  branch: "main"
---

# WRK-019: Drilling, Completion & Intervention Cost Data Layer

> **Module**: worldenergydata/bsee/analysis/cost | **Status**: draft | **Created**: 2026-02-16

## Context

Clients need cost context to evaluate field economics. The BSEE field pipeline (WRK-017, done) delivers activity data (drilling days, completion days, intervention records) but no economic layer. This work item adds proxy-based cost estimation: **days x day-rate** with GOM water-depth segmentation.

All 3 blockers are resolved: WRK-017 (field pipeline), existing `financial/` module (day-rate patterns), and `intervention/` module (activity classification).

**Scope refinement from original plan:** The approved 6-phase plan included 5 geographic regions, cross-regional benchmarking, and standalone reports. Since all BSEE data is GOM-only, non-GOM profiles and benchmarking are YAGNI. Reports deferred to follow-up. **4 phases, 10 files** (down from 6 phases, 14 files).

---

## Reuse Matrix

| Existing Code | Path | How Used |
|---|---|---|
| `calculate_drilling_costs()` | `financial/drilling_completion.py:17-50` | Call for per-well drilling cost (days x rate) |
| `calculate_completion_costs()` | `financial/drilling_completion.py:53-85` | Call for per-well completion cost |
| `classify_activity()` | `intervention/activity_aggregator.py` | Map rig type to drilling/intervention category |
| `RigType` + `classify_rig_type()` | `data/loaders/rig_fleet/constants.py` | Rig type -> day rate tier mapping |
| `SMEConfigLoader.DEFAULT_CONFIG` | `financial/config_loader.py:31-67` | Template for day rate config structure |
| `economic_assumptions.yml` | `config/analysis/lower_tertiary/` | Reference benchmarks ($150-250M/well) |
| `FieldContext` / `FieldReport` | `pipeline/field_query.py`, `pipeline_runner.py` | Phase D integration target |

**Key design choice:** Compose with `DrillingCompletionProcessor` free functions, do NOT inherit from the class (it's coupled to SME V20 workflow).

---

## Phases

### Phase A: Cost Models + Estimation Engine

**TDD tests first** (`tests/unit/bsee/analysis/cost/test_models.py`, `test_cost_engine.py`):
- CostEstimate creation, confidence levels, depth band classification
- Drilling cost: shallow/jackup rate vs deepwater/drillship rate
- Zero days -> zero cost, empty DataFrame -> empty result
- Completion cost: conventional vs HPHT
- Intervention cost by workover type
- LFS stub graceful handling

**New files:**

| File | Lines | Purpose |
|---|---|---|
| `src/.../cost/__init__.py` | ~30 | Module init, lazy imports |
| `src/.../cost/models.py` | ~80 | `CostEstimate` (frozen), `FieldCostSummary` dataclasses |
| `src/.../cost/cost_engine.py` | ~200 | `CostEstimationEngine` class: `estimate_drilling_cost()`, `estimate_completion_cost()`, `estimate_intervention_cost()` |
| `config/analysis/cost_data/day_rates.yml` | ~120 | GOM day rates by water depth band + year (2020-2025) |
| `tests/.../cost/__init__.py` | 0 | Test package |
| `tests/.../cost/test_models.py` | ~60 | Model tests |
| `tests/.../cost/test_cost_engine.py` | ~150 | Engine tests (~11 test functions) |

**`CostEstimate` schema:**
```
activity_type: str          # drilling | completion | intervention
environment: str            # offshore (GOM only for now)
water_depth_band: str       # shallow | mid | deep | ultra_deep
well_depth_band: str        # shallow | mid | deep
rig_type: str               # from RigType enum
cost_usd: float
cost_per_day_usd: float
duration_days: float
confidence: str             # high (proxy) | medium (benchmark) | low (extrapolation)
source: str
year: int
```

**Day rate tiers (day_rates.yml):**
- Drilling: shallow/jackup $80-150K, mid/semi-sub $200-350K, deep/drillship $400-600K
- Completion: conventional $50-100K, HPHT $150-250K
- Intervention: workover rig $40-80K, coiled tubing $30-60K, wireline $10-20K

### Phase B: Day Rate Loader + Depth Classifier

**TDD tests first** (`tests/.../cost/test_day_rate_loader.py`):
- Load valid YAML, get rate for known rig/year, fallback to nearest year
- Fallback to environment average when depth band missing
- Reject negative values, handle missing file

**New files:**

| File | Lines | Purpose |
|---|---|---|
| `src/.../cost/day_rate_loader.py` | ~120 | `DayRateLoader`: reads YAML, `get_rate()` with year interpolation + fallback |
| `src/.../cost/depth_classifier.py` | ~60 | `classify_water_depth(ft)`, `classify_well_depth(ft)` — feet-based (NOT meters) |
| `tests/.../cost/test_day_rate_loader.py` | ~100 | Loader tests (~7 test functions) |

**Water depth bands (feet, BSEE convention):**
- Shallow: <500 ft
- Mid: 500-5,000 ft
- Deep: 5,000-7,000 ft
- Ultra-deep: >7,000 ft

Note: `enrichment_engine.py:_DEPTH_BINS` uses meters (0-200, 200-1000...). New classifier uses feet explicitly — no reuse of that function.

### Phase C: Cost Summary + Field Aggregation

**TDD tests first** (`tests/.../cost/test_cost_summary.py`):
- Summarize field with drilling + completion data
- No data -> zero costs
- Aggregate per-well estimates
- Include intervention costs
- Confidence aggregation (lowest wins)
- Per-lease aggregation

**New files:**

| File | Lines | Purpose |
|---|---|---|
| `src/.../cost/cost_summary.py` | ~150 | `summarize_field_costs(context, engine, data, year) -> FieldCostSummary`, `summarize_by_lease()` |
| `tests/.../cost/test_cost_summary.py` | ~100 | Summary tests (~7 test functions) |

### Phase D: Pipeline Integration — DEFERRED

**Recommendation: Defer to follow-up WRK item.** Reasons:
1. `PipelineRunner` and `FieldReport` are shared infrastructure — modification needs careful compat testing
2. Cost engine (Phases A-C) is independently useful without pipeline integration
3. Report generation (original Phase 5) also deferred — use existing comprehensive report templates later

If included later, would add `cost_summary: FieldCostSummary | None = None` to `FieldReport` and a `_run_cost_analysis()` stage.

---

## File Summary

| # | File | Phase | ~Lines |
|---|---|---|---|
| 1 | `src/worldenergydata/bsee/analysis/cost/__init__.py` | A | 30 |
| 2 | `src/worldenergydata/bsee/analysis/cost/models.py` | A | 80 |
| 3 | `src/worldenergydata/bsee/analysis/cost/cost_engine.py` | A | 200 |
| 4 | `config/analysis/cost_data/day_rates.yml` | A | 120 |
| 5 | `src/worldenergydata/bsee/analysis/cost/day_rate_loader.py` | B | 120 |
| 6 | `src/worldenergydata/bsee/analysis/cost/depth_classifier.py` | B | 60 |
| 7 | `src/worldenergydata/bsee/analysis/cost/cost_summary.py` | C | 150 |
| 8 | `tests/unit/bsee/analysis/cost/__init__.py` | A | 0 |
| 9 | `tests/unit/bsee/analysis/cost/test_models.py` | A | 60 |
| 10 | `tests/unit/bsee/analysis/cost/test_cost_engine.py` | A | 150 |
| 11 | `tests/unit/bsee/analysis/cost/test_day_rate_loader.py` | B | 100 |
| 12 | `tests/unit/bsee/analysis/cost/test_cost_summary.py` | C | 100 |
| **Total** | | | **~1,170** |

**Removed from original 14-file plan (YAGNI):**
- `cost_sources.yml` — docs, not code (put in module docstring)
- `regional_profiles.yml` — only GOM data exists; day_rates.yml covers this
- `regional_loader.py` — merged into day_rate_loader.py
- `benchmarking.py` — no second region to benchmark against
- `report.py` — deferred; use existing comprehensive report templates

---

## Verification

```bash
# Run all cost module tests (after each phase)
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/unit/bsee/analysis/cost/ -v --tb=short --noconftest

# Verify no regressions in financial module
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/unit/bsee/analysis/financial/ -v --tb=short --noconftest

# Quick smoke test (Python REPL)
python3 -c "
from worldenergydata.bsee.analysis.cost import CostEstimationEngine, DayRateLoader
loader = DayRateLoader()
engine = CostEstimationEngine(day_rates=loader.load())
est = engine.estimate_drilling_cost({'DRILL_DAYS': 45, 'WATER_DEPTH_FT': 6000, 'RIG_TYPE': 'DRILLSHIP'}, year=2023)
print(f'Cost: \${est.cost_usd:,.0f} ({est.confidence} confidence)')
"
```

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| No ground truth cost data | Medium | `confidence` field on every estimate; document methodology |
| Water depth units (ft vs m) | Low | New `depth_classifier.py` uses feet explicitly; no reuse of meter-based `_classify_water_depth()` |
| WAR data are LFS stubs | Medium | All tests use synthetic fixtures; engine returns empty on empty input |
| Intervention durations less standardized | Low | Default to `confidence: "low"` for interventions; support flat benchmark fallback |

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase A: Models + Engine | Pending | ~4 tests + 3 source files + 1 config |
| Phase B: Loader + Classifier | Pending | ~7 tests + 2 source files |
| Phase C: Summary + Aggregation | Pending | ~7 tests + 1 source file |
| Phase D: Pipeline Integration | Deferred | Follow-up WRK item |
