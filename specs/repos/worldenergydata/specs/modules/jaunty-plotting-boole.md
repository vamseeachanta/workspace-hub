---
title: "HSE Risk Index — Client-Facing Risk Scoring Framework"
description: "Three-dimensional risk index (Acute, Chronic, Compliance) computed across all HSE data sources with interactive Plotly dashboard output."
version: "1.0"
module: "safety_analysis"
session:
  id: "jaunty-plotting-boole"
  agent: "claude-opus-4.5"
  started: "2026-02-02"
  last_active: "2026-02-02"
  conversation_id: "2058e5fa-33b3-4700-a42e-e113066b0add"
review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
work_item: WRK-014
depends_on: [WRK-012, WRK-013]
implementation:
  phases_complete: [1, 2, 3, 4, 5]
  next_phase: 6
  commit: "3bff1cb7"
  tests: "137 passing (5 test files)"
  status: "phases 1-5 complete, phase 6 pending"
---

# WRK-014: HSE Risk Index Implementation Plan

## 1. Objective

Translate the HSE incident analysis from WRK-013 into a **composite risk index** that scores each activity/subactivity on a 1-10 scale across three dimensions. Output is a client-ready interactive HTML dashboard with methodology documentation.

## 2. Risk Model Design

### 2.1 Three Dimensions

| Dimension | What It Measures | Primary Sources |
|-----------|-----------------|-----------------|
| **Acute Risk** | Immediate harm — fatalities, injuries, incident frequency | BSEE incidents, OSHA accidents, Marine Safety, PHMSA pipeline |
| **Chronic Risk** | Long-term exposure harm — toxic releases, carcinogen exposure | EPA TRI releases (NAICS-filtered to O&G) |
| **Compliance Risk** | Regulatory violations and enforcement intensity | BSEE INCs, OSHA violations, PHMSA enforcement |

### 2.2 Scoring Method

1. **Raw metrics** per activity/subactivity:
   - `fatality_rate` = fatalities / total_incidents
   - `injury_rate` = injuries / total_incidents
   - `frequency` = incidents / exposure_years
   - `tri_carcinogen_lbs` = total carcinogen releases
   - `inc_rate` = violations / inspections (where available)

2. **Percentile-rank normalization** to 1-10 scale:
   - Rank each metric across all activities
   - Map percentile to 1-10 integer bucket
   - Avoids outlier distortion from magnitude differences

3. **Dimension scores** (weighted sub-metric average):
   - Acute = 0.40 * fatality_rate_score + 0.35 * injury_rate_score + 0.25 * frequency_score
   - Chronic = 1.0 * tri_carcinogen_score (single metric)
   - Compliance = 1.0 * inc_rate_score (single metric)

4. **Composite Risk Index** = 0.50 * Acute + 0.25 * Chronic + 0.25 * Compliance

5. **Categorical buckets**: LOW (1-3), MEDIUM (4-5), HIGH (6-7), CRITICAL (8-10)

### 2.3 Source Reliability Weights

When aggregating incidents across sources for the same activity, weight by source reliability:

| Source | Weight | Rationale |
|--------|--------|-----------|
| BSEE | 0.30 | Mandatory federal reporting, high completeness |
| Marine Safety | 0.25 | Multi-authority (USCG BARD, TSB, MAIB, NOAA) |
| OSHA | 0.20 | Broad coverage but delayed reporting |
| PHMSA | 0.15 | Pipeline-specific, limited activity overlap |
| EPA TRI | 0.10 | Chronic exposure proxy, not incident-based |

## 3. Module Architecture

New package: `src/worldenergydata/modules/safety_analysis/risk_index/`

```
risk_index/
  __init__.py           # Exports: RiskIndex, RiskScorer, RiskDashboard
  models.py             # Pydantic: ActivityRiskScore, DimensionScore, CompositeScore
  data_assembler.py     # Loads + merges data from all source DBs/CSVs
  normalizer.py         # Percentile-rank normalization engine
  scorer.py             # Computes dimension + composite scores
  dashboard.py          # Plotly HTML dashboard generation
  methodology.py        # Generates methodology documentation section
  cli.py                # CLI entry: compute, dashboard, export commands
  __main__.py           # python -m ... entry point
```

### 3.1 Files to Create (8 files, ~1,200 lines estimated)

| File | Purpose | ~Lines |
|------|---------|--------|
| `models.py` | `ActivityRiskScore`, `DimensionScore`, `CompositeScore`, `RiskCategory` enum | 120 |
| `data_assembler.py` | Load BSEE, OSHA, Marine, PHMSA, EPA TRI; classify with `IncidentClassifier`; aggregate per activity | 200 |
| `normalizer.py` | `percentile_rank()`, `normalize_to_scale()`, `NormalizationResult` | 80 |
| `scorer.py` | `RiskScorer` class — compute acute/chronic/compliance/composite per activity | 180 |
| `dashboard.py` | Plotly: heatmap, radar charts, bar charts, risk matrix, treemap | 300 |
| `methodology.py` | Generate methodology HTML section for transparency | 100 |
| `cli.py` | argparse CLI with `compute`, `dashboard`, `export` subcommands | 120 |
| `__init__.py` + `__main__.py` | Exports and entry point | 30 |

### 3.2 Files to Modify

| File | Change |
|------|--------|
| `safety_analysis/__init__.py` | Add `risk_index` to exports |
| `safety_analysis/cli.py` | Add `risk-index` subcommand group |

### 3.3 Tests (TDD — written first)

New: `tests/modules/safety_analysis/risk_index/`

| Test File | Covers |
|-----------|--------|
| `test_models.py` | Pydantic model validation, category bucketing |
| `test_normalizer.py` | Percentile ranking, edge cases (ties, zeros, single value) |
| `test_scorer.py` | Dimension weighting, composite calculation, known-answer verification |
| `test_data_assembler.py` | Multi-source loading, classification integration |
| `test_dashboard.py` | HTML output generation, chart presence |

## 4. Data Pipeline

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│  BSEE DB    │   │  OSHA CSVs  │   │  Marine DBs │   │  PHMSA DB    │
│  EPA TRI    │   │             │   │             │   │              │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬───────┘
       │                 │                 │                  │
       └────────────┬────┴────────┬───────┘                  │
                    │             │                           │
              ┌─────▼─────────────▼───────────────────────────▼───┐
              │              DataAssembler                         │
              │  1. Load raw records from each source              │
              │  2. Classify via IncidentClassifier → activity     │
              │  3. Aggregate metrics per activity/subactivity     │
              └───────────────────┬───────────────────────────────┘
                                  │
              ┌───────────────────▼──────────────────────────┐
              │              Normalizer                       │
              │  Percentile-rank each metric → 1-10 scale    │
              └───────────────────┬──────────────────────────┘
                                  │
              ┌───────────────────▼──────────────────────────┐
              │              RiskScorer                       │
              │  Weighted dimension scores → composite index  │
              └───────────────────┬──────────────────────────┘
                                  │
              ┌───────────────────▼──────────────────────────┐
              │              Dashboard / Export               │
              │  Plotly HTML + CSV + methodology docs         │
              └──────────────────────────────────────────────┘
```

## 5. Dashboard Outputs

The interactive HTML dashboard will include:

1. **Risk Heatmap** — Activity vs. Dimension grid, color-coded by score
2. **Composite Bar Chart** — All activities ranked by composite risk index
3. **Radar Charts** — Per-activity 3-axis dimension profile
4. **Risk Matrix** — Frequency vs. Severity scatter (classic 5x5)
5. **Treemap** — Hierarchical activity > subactivity risk breakdown
6. **Methodology Section** — Inline HTML explaining weights, sources, caveats

Output location: `reports/hse/wrk014_hse_risk_index.html`

## 6. Implementation Phases

### Phase 1: Models + Normalizer (TDD) -- COMPLETE
- [x] Write `test_models.py` (37 tests) and `test_normalizer.py` (24 tests)
- [x] Implement `models.py` and `normalizer.py`

### Phase 2: Data Assembler -- COMPLETE
- [x] Write `test_data_assembler.py` (30 tests)
- [x] Implement `data_assembler.py` — load from actual DB/CSV files, classify, aggregate

### Phase 3: Risk Scorer -- COMPLETE
- [x] Write `test_scorer.py` (32 tests)
- [x] Implement `scorer.py` — dimension weights, composite formula

### Phase 4: Dashboard -- COMPLETE
- [x] Write `test_dashboard.py` (14 tests)
- [x] Implement `dashboard.py` — Plotly figures, HTML assembly

### Phase 5: Methodology + CLI -- COMPLETE
- [x] Implement `methodology.py` — transparency documentation
- [x] Implement `cli.py` + `__main__.py` — CLI entry points (Typer-based)

### Phase 6: Integration + Validation -- PENDING (next pickup)
- [ ] Run full pipeline end-to-end on real data:
  ```bash
  uv run python -m worldenergydata.safety_analysis.risk_index compute
  uv run python -m worldenergydata.safety_analysis.risk_index dashboard
  uv run python -m worldenergydata.safety_analysis.risk_index export --format csv
  ```
- [ ] Validate risk rankings against domain knowledge:
  - DIVE/CRANE activities must score HIGH/CRITICAL acute risk
  - PROD/ENV activities must show elevated chronic risk
  - Marine Transport should rank high on acute due to fatality count (9,527 from WRK-013)
  - Pipeline Operations should show compliance risk
- [ ] Cross-reference composite ranking with WRK-013 mishap frequency ranking (expect high correlation)
- [ ] Review low-confidence flags (activities with <10 incidents across all sources)
- [ ] Generate final HTML dashboard: `reports/hse/wrk014_hse_risk_index.html`
- [ ] Update WRK-014 status to COMPLETE

## 7. Validation Approach

1. **Known-answer tests**: Hand-computed scores for 3-4 activities with synthetic data
2. **Sanity checks**: DIVE/CRANE activities must score HIGH/CRITICAL acute risk; PROD/ENV must show chronic risk
3. **Boundary tests**: All-zero inputs, single-source activities, tied percentiles
4. **Cross-reference**: Compare composite ranking with WRK-013 mishap frequency ranking — high correlation expected
5. **End-to-end**: `uv run python -m worldenergydata.safety_analysis.risk_index compute` produces valid CSV; `dashboard` produces valid HTML

## 8. Key Dependencies

- `IncidentClassifier` from `safety_analysis.taxonomy` (exists, WRK-013)
- `ActivityTaxonomy` from `safety_analysis.taxonomy` (exists, WRK-013)
- SQLite databases: `data/modules/hse/database/hse.db`, `data/modules/marine_safety/database/marine_safety.db`, `data/modules/pipeline_safety/database/pipeline_safety.db`
- CSV/raw files: `data/modules/hse/raw/osha/`, `data/modules/hse/raw/epa_tri/`
- Plotly, pandas, pydantic (all in existing deps)

## 9. Caveats for Client Documentation

- Risk scores are relative rankings, not absolute probabilities
- Source coverage varies: BSEE offshore-only, OSHA onshore-heavy, PHMSA pipeline-only
- Chronic risk dimension relies on EPA TRI as proxy (facility-level, not incident-level)
- Activities with fewer than 10 incidents across all sources are flagged as "low confidence"
- Historical data (various date ranges per source) — not normalized to single time window yet

## 10. Session Log

### Session 1 (2026-02-02) — Phases 1-5 Implementation

**Commit**: `3bff1cb7` on `feature/hse-data-acquisition`
**Agent**: claude-opus-4.5 | **Session**: `jaunty-plotting-boole`

**Completed**:
- All 8 source files created in `src/worldenergydata/modules/safety_analysis/risk_index/`
- 137 tests across 5 test files (all passing)
- Legal compliance scan: zero violations
- Pre-commit hooks: all 17 passed (black, isort, flake8+simplify, bandit, gitleaks)

**Files created** (17 total, 5,219 lines):
| File | Lines | Purpose |
|------|-------|---------|
| `models.py` | 145 | Pydantic v2: RiskCategory, DimensionScore, ActivityRiskScore, CompositeScore |
| `normalizer.py` | 113 | Percentile-rank normalization engine |
| `data_assembler.py` | 548 | Multi-source loading (BSEE, OSHA, Marine, PHMSA, EPA TRI) + classification |
| `scorer.py` | 319 | Weighted dimension + composite scoring |
| `dashboard.py` | 527 | Plotly HTML: heatmap, radar, bar, risk matrix, treemap |
| `methodology.py` | 329 | Transparency documentation generator |
| `cli.py` | 579 | Typer CLI: compute, dashboard, export subcommands |
| `__init__.py` | 45 | Package exports |
| `__main__.py` | 7 | Entry point |

**Next pickup**: Phase 6 — end-to-end validation on real data (see checklist above)

**Known considerations for Phase 6**:
- Only `marine_safety.db` SQLite exists; BSEE/PHMSA data are in raw CSV/pipe-delimited files
- OSHA data in `data/modules/hse/raw/osha/`, EPA TRI in `data/modules/hse/raw/epa_tri/`
- `DataAssembler` has static loaders for each source format
- `IncidentClassifier` from `safety_analysis.taxonomy` handles activity classification
- Activities with <10 incidents get "low confidence" flag — review these in output
