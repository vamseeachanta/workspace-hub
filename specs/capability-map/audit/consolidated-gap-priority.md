# Consolidated Gap Priority Map

> Generated: 2026-03-14 | WRK-1179 Day 3
> Sources: 6 audit reports (data-audit-report, public-og-data-sources, 4 repo calc audits)

## 1. Executive Summary

| Metric | Value |
|--------|------:|
| Total standards gaps (capability map) | 455 (digitalmodel) + 235 (doc index) |
| Calculation gaps identified | 29 across 4 repos |
| Public data sources not yet ingested | 17 of 38 cataloged |
| Phase B extraction coverage | 0% (0 of 1,033,933 records) |
| Capability map standards marked "done" | 0 of 17,799 |

**Key surprises from audit:**

1. **WRK-318/321 already implemented** -- Arps decline curves (exponential,
   hyperbolic, harmonic) are fully coded in `production/forecast/decline.py`;
   NPV/MIRR with carbon cost sensitivity is complete in `economics/dcf.py` +
   `economics/carbon.py`. Neither WRK should be closed yet (see Section 4).

2. **assethold more complete than expected** -- ~130 calculation functions across
   risk metrics, fundamentals scoring, options pricing, technical indicators,
   trend detection, insider tracking, and multifamily analysis. 996 tests passing.

3. **Geotechnical entirely missing** -- no `src/digitalmodel/geotechnical/`
   directory exists despite 10 standards identified in the capability map.
   This is the largest single discipline gap.

4. **Capability map status not wired** -- 0 standards marked "done" across all
   17,799 entries. The map tracks gaps but never records implementation. This is
   a process gap, not a code gap.

5. **Hydrodynamics invisible in cap map** -- 825 functions across 132 files, but
   0 standards mapped. The code exists; the map does not reflect it.

6. **162 of 235 doc-index gaps are uncategorized "other"** -- nearly 69% of
   standards gaps cannot be prioritized until reclassified into proper domains.

---

## 2. Stream A -- Data Gaps (Priority Ranked)

### Document Index Gaps

| # | Gap | Impact | Records/Items |
|---|-----|--------|---------------|
| A1 | 0% Phase B extraction | No AI summaries on any record; blocks semantic search and gap triage | 1,033,933 records |
| A2 | 162 "other" domain standards gaps | Cannot prioritize 69% of all gaps until reclassified | 162 standards |
| A3 | Content extraction from og_standards | 27,980 standards docs not yet content-extracted | 27,980 records |
| A4 | Materials domain: 0 done, 0 WRK-captured | 21 gaps with no work started | 21 standards |
| A5 | Structural domain gaps | API RP 2A editions, ASTM fatigue/creep testing | 25 standards |

### Public Data Sources Not Yet Ingested (17 sources)

**HIGH priority:**

| Source | API | Format | Rationale |
|--------|-----|--------|-----------|
| BOEM | Yes | CSV/Excel/API | Offshore lease data, well APIs, platform permits -- complements BSEE |
| Baker Hughes Rig Count | No | Excel | Industry-standard drilling activity indicator; free weekly download |
| ERA5 Reanalysis (ECMWF) | Yes | NetCDF/GRIB | Global hourly atmospheric reanalysis 1940-present; wind/wave/pressure for metocean design |
| Copernicus Marine (CMEMS) | Yes | NetCDF | Global ocean physics at 1/12 deg -- currents, temperature, salinity; critical for offshore engineering |

**MEDIUM priority:**

| Source | API | Format | Rationale |
|--------|-----|--------|-----------|
| OPEC Monthly Oil Market Report | No | Excel/PDF | Global crude production by OPEC members |
| BP Statistical Review (Energy Institute) | No | Excel/CSV | 70+ years of global energy data; free download |
| JODI Oil World Database | No | CSV/Excel | Monthly oil supply/demand for 100+ countries |
| USGS Oil & Gas Assessment | No | Shapefiles/CSV | Undiscovered resource estimates for ~170 basins |
| PUDL (Public Utility Data Liberation) | Yes | SQLite/Parquet | Cleaned US energy data from EIA, FERC, EPA |
| BLM Federal Land Records | Yes | GIS/Shapefile | Federal mineral leases, mining claims |

**LOW priority:**

| Source | API | Format | Rationale |
|--------|-----|--------|-----------|
| IEA Monthly Oil Data Service | No | Excel (subscription) | Requires paid subscription |
| IMO GISIS | No | Web portal | Limited programmatic access; requires registration |
| GainEnergy HuggingFace Dataset | Yes | Parquet/CSV | ML Q&A dataset; niche |
| SEG Open Data Catalog | No | SEG-Y/LAS | Seismic/well logs for subsurface validation |
| Software Underground awesome-open-geoscience | No | Link list | Discovery layer only |
| Alberta Wells Satellite Dataset | Yes | GeoTIFF/CSV | Academic remote sensing dataset |
| Rystad Energy UCube | No | Web (subscription) | Commercial subscription required |

---

## 3. Stream B -- Calculation Gaps (Priority Ranked)

### Top 20 Calculation Gaps for Days 4-12

Ranking criteria: (1) standard doc available, (2) workflow pattern dependency,
(3) complexity, (4) test data available.

#### digitalmodel geotechnical (HIGH -- entire discipline missing)

| # | Gap | Standard | Complexity | Test Data |
|---|-----|----------|-----------|-----------|
| B1 | Pile axial capacity | API RP 2GEO Sec 6-8 | Medium | Textbook examples available |
| B2 | On-bottom stability | DNV-RP-F109 | Medium | DNV examples available |
| B3 | Anchor holding capacity | DNVGL RP E301, DNV RP E303 | Medium | Design examples in RPs |
| B4 | Scour assessment | DNV-RP-F107 | Low | Parametric studies in RP |
| B5 | Soil models (foundation design) | API RP 2GEO, DNV RP C212 | High | Requires soil test data |

#### digitalmodel structural/subsea (MEDIUM -- partial implementation)

| # | Gap | Current State | Standard Needed |
|---|-----|--------------|-----------------|
| B6 | Spectral fatigue completion | 4 methods exist (Dirlik, NB, WL, ZB); not validated against FPSO guides | ABS FPSO fatigue guide, DNV RP F204 |
| B7 | Fracture mechanics BS 7910 | Basic framework only | BS 7910:2013, R6, SINTAP/FITNET |
| B8 | API 579 Level 3 completion | RSF + Level 1/2 exist | API 579 Part 9-13 (creep, fire, dents) |
| B9 | Mooring API RP 2SK full checks | Catenary solver exists | API RP 2SK 3rd Ed, BV NR 493 |

#### assetutilities shared (MEDIUM -- enables other repos)

| # | Gap | Impact | Complexity |
|---|-----|--------|-----------|
| B10 | Interpolation helpers | No shared linear/spline wrapper; calcs use raw numpy | Low |
| B11 | Integration helpers | No trapezoidal/Simpson wrapper for fatigue damage | Low |
| B12 | API 5CT casing grades | casing_pipe.py exists but materials.py lacks J55/K55/N80/L80/P110 | Low |
| B13 | Pipe cross-section geometry | Area, I, Z, S likely duplicated across repos | Low |

#### assethold (MEDIUM)

| # | Gap | Current State | Complexity |
|---|-----|--------------|-----------|
| B14 | Portfolio beta vs energy benchmarks | No beta calculation anywhere; needed for XLE/XOP context | Low |
| B15 | Dividend yield forecasting | Current yield fetched but no projection/growth model | Medium |
| B16 | Factor model (Fama-French 3/5) | No factor decomposition for alpha explanation | Medium |
| B17 | Portfolio correlation matrix | Risk metrics per-position but no correlation heatmap | Low |

#### worldenergydata (LOW -- most calcs already exist)

| # | Gap | Current State | Complexity |
|---|-----|--------------|-----------|
| B18 | Type curve matching (Blasingame/Fetkovich) | Cross-basin compare exists but no type curve fitting | High |
| B19 | P10/P50/P90 resource estimation | No Monte Carlo or probabilistic module | High |
| B20 | Advanced DCA (SEPD, Duong) | Only Arps implemented; unconventional methods missing | Medium |

**Not ranked but noted:** Duplicate decline/NPV implementations across
`production/forecast/`, `economics/`, `fdas/`, and `well_production_dashboard/`
need consolidation (refactor, not new implementation).

---

## 4. Pre-Implementation Tasks

**Required before calculation implementation:**

| Task | Why | Effort |
|------|-----|--------|
| Download geotechnical reference standards (API RP 2GEO, DNV-RP-F109, DNV-RP-F107, DNV RP C212) | Cannot implement B1-B5 without standard equations | Capture as WRK items |
| Cap map reconciliation: update status from "gap" to "done" for implemented standards | 0 currently marked done despite extensive code | Script + manual review |
| WRK-318/321: prepare plan+lifecycle HTML proving data presence and flow | Code exists but WRK evidence trail incomplete; do NOT close without evidence | HTML generation only |
| Create `src/digitalmodel/geotechnical/__init__.py` scaffold | Directory does not exist; need module structure before implementing B1-B5 | Trivial |
| Add `sklearn` to worldenergydata dependency group | 18+ test errors from missing import; blocks cost calibration | One-line fix |

---

## 5. Recommended Phase 2 Focus (Days 4-12)

### Stream A (Data)

| Priority | Action | Expected Outcome |
|----------|--------|-----------------|
| 1 | Phase B extraction on og_standards + ace_standards (83,566 records) | AI summaries enabling semantic search on highest-value docs |
| 2 | Reclassify 162 "other" domain gaps | Unlock targeted WRK creation for 69% of standards gaps |
| 3 | Ingest BOEM (API available) | Offshore lease + platform data complementing BSEE production |
| 4 | Ingest Baker Hughes rig count (Excel scrape) | Industry-standard drilling activity indicator |

### Stream B (Calculations)

| Priority | Action | Unblocks | Est. Effort |
|----------|--------|----------|-------------|
| 1 | assetutilities interpolation + integration helpers (B10, B11) | Fatigue damage, curve fitting across all repos | 1 day |
| 2 | digitalmodel geotechnical scaffold + pile capacity (B1) | Foundation design workflows | 2 days |
| 3 | digitalmodel on-bottom stability (B2) | Pipeline stability assessments | 1 day |
| 4 | Cap map reconciliation pass | Accurate gap tracking; closes process gap | 1 day |
| 5 | assetutilities API 5CT grades + pipe geometry (B12, B13) | Casing design, shared cross-section calcs | 1 day |
| 6 | assethold portfolio beta (B14) | Energy benchmark context for portfolio analysis | 0.5 day |
| 7 | assethold correlation matrix (B17) | Portfolio risk visualization | 0.5 day |
| 8 | digitalmodel spectral fatigue validation (B6) | FPSO/riser fatigue signoff | 2 days |
| 9 | worldenergydata advanced DCA -- SEPD (B20) | Unconventional well forecasting | 1 day |
| 10 | worldenergydata duplicate consolidation | Reduced maintenance; single source of truth for decline/NPV | 1 day |
