# Dead Ends Registry

> Formally documented paths that were investigated and ruled out.
> **Before creating a WRK item for data acquisition or integration, check here first.**
> Last updated: 2026-02-18

---

## Data Source Dead Ends

### Australia NOPTA — Offshore Production Data
- **Verdict**: PERMANENTLY BLOCKED — do not pursue
- **Reason**: Production data is permanently confidential by statute under Australian
  Offshore Petroleum and Greenhouse Gas Storage (Resource Management and Administration)
  Regulations 2011, Regs 8.02(3) and 10.02(3). No pathway exists, even via FOI.
  NOPTA tightened seismic data release policy further in November 2025 (now requires
  Ministerial approval). Australia produces ~400,000 boe/d offshore (Ichthys, Gorgon,
  North West Shelf, Prelude FLNG) — none of it publicly reportable at field level.
- **What IS available**: Well and seismic survey data via NOPIMS after confidentiality
  embargo (2–15 years). Titles registry (NEATS) is public. Not useful for production analysis.
- **Investigated**: 2026-02-18

### IEA Monthly Oil Data Service (MODS)
- **Verdict**: COMMERCIAL — do not pursue for worldenergydata open-source module
- **Reason**: MODS is a paid subscription (~€15,000/yr enterprise). Country-level
  monthly aggregate only (no field-level). EIA international data covers the same
  country aggregates for free via REST API.
- **Free alternative**: EIA international country series (WRK-195) + IEA free-tier
  publications (Annual Statistical Supplement PDF, MOMR headlines).
- **Investigated**: 2026-02-18

### Angola ANPG — Production Data
- **Verdict**: NO USABLE DATA — monitor only
- **Reason**: ANPG has no open data portal. Production data is released only via
  aggregate press releases and limited EITI pilot disclosures. Legal framework
  (Petroleum Activities Law) restricts contract and production transparency.
  Angola left OPEC Jan 2024 — even OPEC secondary source data no longer tracks
  it reliably. No bulk CSV, no API, no field-level data.
- **What exists**: EITI pilot reports (Angola not fully EITI compliant) with
  ~18–24 month lag, covering payment data only (not production volumes).
- **Future**: Monitor EITI accession. Angola produces ~1M bopd (key deepwater
  fields: Agogo, CLOV, Begonia, Block 32/Greater Plutonio via TotalEnergies/BP).
- **Investigated**: 2026-02-18

### OPEC ASB / MOMR — Field-Level Data
- **Verdict**: COUNTRY AGGREGATE ONLY — not useful for field development analysis
- **Reason**: OPEC publishes free PDFs (Monthly Oil Market Report, Annual Statistical
  Bulletin) but data is country-level only. No field or well granularity.
  PDF format requires scraping. Secondary source estimates (Argus/Platts) used
  to fill gaps — i.e., OPEC re-packages commercial data in PDF form.
- **Use case**: Country-level context/crosscheck only. Covered by EIA international
  (WRK-195) which is free API with same or better coverage.
- **Investigated**: 2026-02-18

### Guyana — Field/Well Level Production Data
- **Verdict**: NO GRANULAR DATA — stub only (WRK-196 Part B)
- **Reason**: ExxonMobil/Hess/CNOOC JV does not release well-level or field-level
  monthly data. Guyana's Department of Energy / EPA lack the regulatory framework
  to compel operator disclosure. A December 2025 op-ed in Stabroek News explicitly
  called for data release — indicating this remains unresolved.
  Country-level via EIA. EITI reports have 18–24 month lag, cover payments only.
- **Production scale**: ~900,000 bopd across 4 FPSOs (Liza Destiny, Liza Unity,
  Prosperity, Yellowtail) as of Nov 2025. Hammerhead FID 2025 (~150k bopd, 2029).
- **Activation trigger**: Guyana achieves EITI full compliance with production
  disclosure, or government mandates field-level reporting.
- **Investigated**: 2026-02-18

### Suriname Staatsolie — Field/Well Level Production Data
- **Verdict**: NO OFFSHORE DATA YET — stub only (WRK-196 Part B)
- **Reason**: Offshore production (GranMorgu, Block 58) does not exist yet.
  First oil expected 2028. Onshore production (~17,000 bopd) is too small to
  warrant a module. Annual PDF reports only; no structured open data.
- **Activation trigger**: GranMorgu first oil (est. 2028). Then check if
  Staatsolie / TotalEnergies establish production reporting framework.
- **Investigated**: 2026-02-18

### Namibia NAMCOR — Production Data
- **Verdict**: NO PRODUCTION — stub/watch only (WRK-196 Part B, WRK-191 catalog)
- **Reason**: Namibia has no commercial offshore oil production. Venus (TotalEnergies,
  FID deferred to 2026, first oil late 2020s) and Mopane (Galp/TotalEnergies,
  pre-FID) are discoveries, not yet in development. NAMCOR has no open data portal.
- **Activation trigger**: TotalEnergies Venus FID (expected 2026). Then monitor
  whether NAMCOR establishes a production reporting framework pre-first-oil.
- **Investigated**: 2026-02-18

### Canada CNSOPB (Nova Scotia Offshore) — Production Data
- **Verdict**: EXPLORATION ONLY — not worth pursuing now
- **Reason**: Nova Scotia offshore has no current commercial production.
  Sable Island is depleted and decommissioned. Deep Panuke is decommissioned.
  Any production data is historical (pre-2010) and of limited relevance to
  current field development analysis. Registration required for well data.
- **Future**: If a new development is sanctioned (Deep Panuke area or new
  discoveries), revisit. C-NLOER (NL) is the useful Canadian offshore source (WRK-196).
- **Investigated**: 2026-02-18

---

## Technical / Approach Dead Ends

### ML/Statistical Models for Well Production Optimization
- **Verdict**: KNOWN FAILURE MODE — do not propose as a solution
- **Reason**: Documented in WRK-164 user voice. Four premier AI O&G service
  companies attempted ML-based production optimization and failed. Root cause:
  multiphase flow is dynamically nonlinear — watercut, GOR, pressure, choke,
  separator, flowline, and stabilization time interact in ways that violate
  ML/statistical stationarity assumptions. More data → more confident wrong answers (GIGO).
- **Correct approach**: Physics-based nodal analysis with production test quality
  scoring as the entry point (WRK-164).
- **Source**: WRK-164 user voice (production/reservoir engineer testimony)

### Message-Count-Based Claude Usage Estimation
- **Verdict**: WASTED EFFORT — use OAuth API instead
- **Reason**: `GET /api/oauth/usage` provides exact weekly usage % directly.
  Building heuristics from message counts was unnecessary.
- **Source**: MEMORY.md (patterns rule: check for official API before building estimators)

---

## How to Use This Registry

1. **Before creating a data acquisition WRK item**: search this file for the source/region.
2. **If a dead end has changed** (e.g., Australia changes statute, Guyana mandates
   disclosure): update the entry, change verdict to "MONITOR" or "REOPEN", and
   create a new WRK item with reference to this entry.
3. **When you hit a new dead end**: add an entry here and reference it in the relevant WRK.
