# OrcaWave / OrcaFlex Research Gap Analysis

> **Date:** 2026-04-02
> **Issue:** #1575 (Holistic Document & Resource Intelligence)
> **Domain:** Marine Hydrodynamics — Diffraction, Radiation, Mooring, Seakeeping
> **Author:** AI Agent (Gemini/Codex seat 2, Terminal 6)
> **Cross-reference:** docs/roadmaps/orcawave-orcaflex-capability-roadmap.md, docs/assessments/hull-library-audit.md

---

## Executive Summary

The OrcaWave/OrcaFlex domain has **344 Python modules**, **43 AI agent skills**, and **13 spec.yml validation cases** — architecturally the most mature domain in the ecosystem. However, the **research and standards backing is thin**: only **33 marine standards** are tracked (4 done, 2 gaps, 26 reference, 1 WRK-captured), and **32,060 marine documents** in the enhancement plan remain largely unprocessed. Meanwhile, **26,242 conference papers** (OMAE, OTC, ISOPE) sit unindexed on `/mnt/ace/docs/conferences/`, and only **7 of 41 cataloged marine OSS tools** are cloned locally.

**Bottom line:** The codebase is ready; the knowledge base is not. Closing this gap requires targeted acquisition of ~50 key resources and systematic indexing of the conference paper archive.

---

## 1. Marine/Hydrodynamics Standards in the Transfer Ledger

### 1.1 Summary

| Status | Count | % of Marine |
|--------|-------|-------------|
| **Done** | 4 | 12.1% |
| **Gap** | 2 | 6.1% |
| **Reference** | 26 | 78.8% |
| **WRK Captured** | 1 | 3.0% |
| **Total** | 33 | 100% |

### 1.2 Done Standards (4)

These are read, understood, and have calculation implementations:

| ID | Title |
|----|-------|
| API-RP-2I | API RP 2I 3rd Ed (2008) — In-service Inspection of Mooring Hardware |
| API-RP-2P | API 2P — Analysis of Spread Mooring Systems |
| API-RP-2SM | API RP 2SM — Design, Manufacture, Installation of Synthetic Fiber Ropes for Mooring |
| DNV-OS-E301 | DNV OS E301 (2010) — Position Mooring |

### 1.3 Gap Standards (2) — Missing, Need Acquisition

| ID | Title | Priority |
|----|-------|----------|
| API-RP-17A | API RP 17A — Design and Operation of Subsea Production Systems | **Critical** — core subsea engineering reference |
| API-RP-2T | API 2T — Planning, Designing, and Constructing Tension Leg Platforms | **High** — TLP design reference for floating platforms |

### 1.4 Reference Standards (26) — On Disk, Not Yet Read

Key marine/hydro references awaiting processing:

| ID | Title | Relevance to OrcaWave/OrcaFlex |
|----|-------|-------------------------------|
| API-RP-2MET | Metocean conditions | **Critical** — wave/wind/current input data |
| API-RP-2RD | Design of Risers for FPSs and TLPs | **High** — riser analysis |
| API-RP-2SK | Design of Stationkeeping Systems | **High** — mooring analysis |
| API-RP-2T-1ST-ED / 2ND-ED | TLP design (1987/1997) | High — historical TLP reference |
| ABS-GUI-00 | Guide for Thrusters and DP Systems | Medium — DP modeling |
| ABS-GUI-002 | Guide for FPS Systems | Medium — floating production |
| OTC-13109 | SCR Fatigue vs Hydrodynamic Loading | **High** — directly relevant to OrcaFlex SCR models |
| OTC-4587 | Wave Kinematics From Wave Staff Arrays | Medium — wave input validation |
| OTC-5468 | Fatigue Life Analysis of Production Risers | **High** — riser fatigue |
| GUDMESTAD | Regular Water Wave Kinematics | Medium — wave theory reference |
| PIERSON-JR | Pierson-Moskowitz Spectral Form | **Critical** — wave spectrum used in all analyses |
| PUB101-FPSO-DLA | FPSO Design Load Analysis | High — floating vessel analysis |
| N/A (VIV comparison) | Comparison of VIV models for marine structures | **High** — VIV validation |

### 1.5 Gap Assessment

**Critical missing standards for OrcaWave/OrcaFlex work:**

| Standard | Why Needed | Status |
|----------|-----------|--------|
| DNV-RP-C205 | Environmental Conditions and Environmental Loads — **the** reference for wave loads, Morison, diffraction | Not in ledger (exists in research literature) |
| DNV-OS-E301 | Position Mooring — already done ✓ | Done |
| DNV-RP-F105 | Free Spanning Pipelines (VIV) | Not in marine ledger (may be in pipeline) |
| API-RP-2MET | Metocean conditions | Reference (not read) |
| SNAME T&R Bulletins | Various marine procedures | Not in ledger |
| ISO 19901-1 | Metocean design and operating considerations | Not in ledger |
| DNVGL-RP-N103 | Modelling and Analysis of Marine Operations | Not in ledger |

---

## 2. Enhancement Plan — Marine/Hydro Domain

### 2.1 Marine Domain in Enhancement Plan

| Metric | Value |
|--------|-------|
| **Total marine documents:** | 32,060 |
| **Sample items listed:** | 500 (capped per domain) |
| **Status of listed items:** | Predominantly "gap" |

The marine domain is the **6th largest** in the enhancement plan (32,060 docs), behind cad (474K), pipeline (187K), other (177K), portfolio (55K), and materials (48K).

### 2.2 Diffraction/OrcaWave-Specific Entries

Found in the enhancement plan:

| Entry | Path | Type |
|-------|------|------|
| diffraction-spec-converter.md | /mnt/local-analysis/workspace-hub/specs/modules/ | workspace-spec |
| integrate-engineering-units-into-diffraction-analysis.md | /mnt/local-analysis/workspace-hub/specs/modules/ | workspace-spec |
| orcaflex-modular-builder-enhancement.md | /mnt/local-analysis/workspace-hub/specs/modules/ | workspace-spec |

These are **specification documents**, not research literature — they describe how to build features, not domain knowledge inputs.

### 2.3 Domain Knowledge Gap

The enhancement plan's marine section contains **32,060 documents** but no systematic domain-specific breakdown by subcategory (diffraction, mooring, seakeeping, wave loads, etc.). This makes it impossible to assess which marine sub-domains have coverage and which do not.

**Recommendation:** Create a marine-domain sub-classification taxonomy:
- Diffraction/radiation
- Mooring analysis
- Seakeeping/vessel motions
- VIV (vortex-induced vibration)
- Wave loads (Morison, diffraction)
- Marine operations
- Naval architecture (hydrostatics, stability)

---

## 3. Conference Papers on `/mnt/ace/docs/conferences/`

### 3.1 Marine-Relevant Conference Archives

| Conference | Files | Years Available | Marine Relevance |
|-----------|-------|----------------|-----------------|
| **OMAE** | 13,126 | 1998-2014 (16 years) | **Critical** — International Conference on Ocean, Offshore and Arctic Engineering. Primary venue for wave loads, diffraction, VIV, mooring, marine operations. |
| **OTC** | 8,500 | Multiple years | **High** — Offshore Technology Conference. Platform design, risers, mooring, subsea. |
| **ISOPE** | 4,516 | 2003-2014 (8 years) | **High** — Ocean, Polar engineering. Wave loads, ice loads, floating structures. |
| **SNAME** | 99 | — | **High** — Naval architecture, ship design, hydrostatics. |
| **SUT** | 1 | — | Medium — Subsea technology. |
| **Flow Induced Vibration** | — | — | **Critical** — Directly relevant to VIV modeling in OrcaFlex. |
| **Euroforum Offshore Risers** | — | — | **High** — Riser design and analysis. |
| **DeepGulf** | — | — | High — Deepwater technology. |
| **DOT** | — | — | Medium — Deepwater Offshore Technology. |

### 3.2 Indexing Status

**None of these 26,242+ conference papers are indexed in the document-intelligence pipeline.**

They are not listed in `mounted-source-registry.yaml` as a source. To index them:
1. Add `/mnt/ace/docs/conferences/` as a new source in `config.yaml`
2. Run Phase A to index all 26K+ files
3. Run Phase B to extract/summarize (can focus on OMAE + OTC first)
4. Run Phase C to classify by marine sub-domain

### 3.3 Estimated High-Value Papers (OMAE)

OMAE papers typically cover:
- **Hydrodynamics track:** Diffraction/radiation, added mass/damping, QTF, second-order loads
- **Structures track:** Fatigue, fracture, S-N curves for marine structures
- **Pipelines and Risers track:** VIV, fatigue, installation
- **Ocean Engineering track:** Mooring, station-keeping, floating platforms
- **CFD track:** Wave-structure interaction, green water, sloshing

Given 13,126 OMAE papers over 16 years, an estimated **3,000-5,000 are directly relevant** to OrcaWave/OrcaFlex work (hydrodynamics + risers + mooring tracks).

---

## 4. Open-Source Tools — Catalog vs. Installed

### 4.1 Marine/Hydro Tools in OSS Catalog

The `data/oss-engineering-catalog.yaml` lists **41 marine/hydro-related tools**. Status:

| Tool | Domain | Cloned to /mnt/ace? | Integration Priority |
|------|--------|---------------------|---------------------|
| **Capytaine** | BEM solver (Python) | ✅ Yes | **Critical** — open-source OrcaWave alternative |
| **HAMS** | BEM solver (Fortran) | ✅ Yes | **Critical** — fast BEM, pyHAMS wrapper |
| **WEC-Sim** | Wave energy converter sim | ✅ Yes | Medium |
| **MoorDyn** | Mooring dynamics | ✅ Yes | **High** — complements OrcaFlex mooring |
| **MoorPy** | Quasi-static mooring | ✅ Yes | **High** — quick mooring design |
| **OpenFAST** | Aero-hydro-servo-elastic | ✅ Yes | Medium |
| **OPM** | Open Porous Media | ✅ Yes | Low (reservoir focus) |
| BEMRosetta | BEM format converter | ❌ Not cloned | **High** — converts between Nemoh/WAMIT/AQWA/HAMS formats |
| Nemoh | BEM solver (Fortran) | ❌ Not cloned | High — open-source reference BEM |
| pyHAMS | Python wrapper for HAMS | ❌ Not cloned | High — pip-installable BEM |
| RAFT | Floating wind platform tool | ❌ Not cloned | Medium |
| WEIS | Wind energy integrated sim | ❌ Not cloned | Low |
| DualSPHysics | SPH solver (GPU) | ❌ Not cloned | Medium — wave-structure interaction |
| REEF3D | CFD hydrodynamics | ❌ Not cloned | Medium |
| Thetis | Marine/coastal FEM | ❌ Not cloned | Low |
| OpenDrift | Marine drift simulation | ❌ Not cloned | Low |
| py-fatigue | Fatigue analysis | ❌ Not cloned | Medium |
| pycatenary | Mooring catenary | ❌ Not cloned | Medium |
| OCEANLYZ | Wave spectral analysis | ❌ Not cloned | **High** — wave analysis toolbox |
| OSP (libcosim) | Co-simulation (DNV-backed) | ❌ Not cloned | Medium — marine operations |

### 4.2 Gap: Cloned vs. Available

| Metric | Value |
|--------|-------|
| **Total marine/hydro OSS tools cataloged:** | 41 |
| **Cloned to /mnt/ace:** | 7 (17%) |
| **Not cloned:** | 34 (83%) |
| **Critical gaps (not cloned):** | BEMRosetta, Nemoh, pyHAMS, OCEANLYZ |

### 4.3 Actual Installation Status

None of the cloned tools appear to be pip-installed in the current environment. The tools exist as source code repositories on `/mnt/ace/` but are not available as importable Python packages.

---

## 5. Research Literature on Disk

### 5.1 Domain Literature Folders

Located at `/mnt/ace-data/digitalmodel/docs/domains/`:

| Domain Folder | Files | Notes |
|---------------|-------|-------|
| hydrodynamics/literature/ | 20+ PDFs | VIV, wave loads, propeller, textbooks, MIT lectures, DNV standards |
| orcawave/examples+tutorials/ | 3 items | Minimal — examples and tutorial files only |
| orcaflex/mooring+pipeline+notes/ | 9 items | Mooring, pipeline application notes |
| naval_architecture/ | 16 files | Hull form, stability references |
| catenary/ | — | Catenary theory |
| structural/ | — | Structural engineering |
| subsea/ | — | Subsea engineering |
| metocean/ | — | Metocean data |

### 5.2 Key Hydrodynamics Literature Already on Disk

| File | Topic | Value |
|------|-------|-------|
| journee-massie-2001-offshore-hydromechanics.pdf | **Textbook** — core reference | Critical |
| dnvgl-2017-rp-c205-environmental-conditions-loads.pdf | Wave loads standard | Critical |
| dnv-2007-rp-c205-environmental-conditions-loads.pdf | Wave loads (older edition) | High |
| dnv-2006-rp-f105-free-spanning-pipelines-viv.pdf | VIV standard | High |
| mit-2002-2.24-lecture22-wave-interaction-offshore.pdf | MIT wave theory | Medium |
| mit-13.012-reading9-wave-loads-potential-theory.pdf | Potential flow theory | High |
| le-cunff-2002-viv-risers-theoretical-numerical-experimental.pdf | VIV riser analysis | High |
| akademia-2022-design-analysis-viv-offshore.pdf | Modern VIV review | High |
| ittc-2005-specialist-committee-vortex-induced-vibration.pdf | VIV committee report | Medium |
| carlton-2007-marine-propellers-and-propulsion.pdf | Propeller theory | Low (not OrcaWave focus) |

### 5.3 What's Missing from Research Literature

| Topic | What Exists | What's Missing |
|-------|------------|----------------|
| **Diffraction/radiation theory** | MIT lectures, Journée textbook | Lee & Newman (WAMIT), Babarit (Capytaine), Faltinsen's "Sea Loads" |
| **Added mass & damping** | Partial via DNV-RP-C205 | DNV CN 30.5, Korotkin "Added Masses of Ship Structures" |
| **QTF & second-order** | None | Pinkster (1980) thesis, Newman's QTF approximations |
| **Wave spectra** | Pierson-Moskowitz (ledger) | JONSWAP validation data, Ochi-Hubble, Torsethaugen |
| **Mooring dynamics** | DNV-OS-E301 (done) | API RP 2SK implementation details, chain mechanics |
| **VIV** | 4 papers + DNV-F105 | Vandiver (MIT) monograph, Williamson & Govardhan review |
| **Sloshing** | None | Faltinsen & Timokha "Sloshing" textbook |
| **Gap resonance** | None | Molin et al. (2001), Sun et al. (2015) gap resonance papers |

---

## 6. Web Resources to Prioritize for Download

From the online resources catalog, these are the highest-priority resources for OrcaWave/OrcaFlex domain advancement:

| Resource | URL | Why Priority |
|----------|-----|-------------|
| **DNV Standards Explorer** | standards.dnv.com/explorer | 650+ standards, free full-text search — DNV-RP-C205, C203, OS-E301 updates |
| **CMEMS Marine Service** | data.marine.copernicus.eu | Free metocean hindcast/forecast data for validation |
| **wavespectra** (Python) | github.com/metocean/wavespectra | Wave spectral analysis — fills hydrodynamics gap |
| **SNAME T&R Bulletins** | sname.org | Marine engineering procedures, structural FEA, hydro |
| **The Well** (physics ML) | polymathic-ai.org | 15 TB simulation data incl. shear flow — hydro validation |
| **Open-Meteo Marine API** | open-meteo.com/en/docs/marine-weather-api | Free wave/swell API for metocean inputs |
| **MIT OpenCourseWare 13.024** | ocw.mit.edu | Hydrodynamics of ships and offshore structures |
| **NTNU Marine Technology** | ntnu.edu/imo | Norwegian marine tech research papers |
| **IMarEST Proceedings** | imarest.org | Marine engineering journal — some free |
| **NOAA Wave/Current Data** | tidesandcurrents.noaa.gov | Current profile validation data |

---

## 7. Top 10 Highest-Value Resources to Acquire/Index/Extract

Ranked by impact on OrcaWave/OrcaFlex domain advancement:

### Rank 1: Index OMAE Conference Papers
- **Action:** Add `/mnt/ace/docs/conferences/OMAE` to Phase A config
- **Volume:** 13,126 papers (1998-2014)
- **Impact:** Fills massive gap in wave loads, diffraction, VIV, mooring literature
- **Effort:** Config change + 1 overnight batch run

### Rank 2: Clone and Install BEMRosetta
- **Action:** `git clone https://github.com/BEMRosetta/BEMRosetta` → `/mnt/ace/BEMRosetta`
- **Impact:** Enables format conversion between AQWA/Nemoh/WAMIT/HAMS/OrcaWave — unblocks multi-solver benchmark pipeline
- **Effort:** 30 minutes

### Rank 3: Acquire "Sea Loads on Ships and Offshore Structures" (Faltinsen, 1990)
- **Action:** Purchase or locate PDF
- **Impact:** **The** reference for wave-structure interaction, diffraction, added mass — underpins all BEM work
- **Effort:** Purchase ($50-100)

### Rank 4: Process 26 Reference Marine Standards
- **Action:** Run Phase B batch on the 26 reference-status marine standards already on disk
- **Impact:** Takes marine from 4 done → potentially 30 done (12% → 91% of marine ledger)
- **Effort:** 1 overnight Claude worker run

### Rank 5: Install pyHAMS and OCEANLYZ
- **Action:** `pip install pyHAMS oceanlyz wavespectra`
- **Impact:** Adds Python BEM solver + wave analysis toolbox — enables rapid prototyping without OrcaWave license
- **Effort:** 15 minutes + validation

### Rank 6: Index OTC Conference Papers
- **Action:** Add `/mnt/ace/docs/conferences/OTC` to Phase A config
- **Volume:** 8,500 papers
- **Impact:** Offshore platform design, deepwater technology, mooring
- **Effort:** Config change + shared batch run with OMAE

### Rank 7: Download DNV-RP-C205 Latest Edition from DNV Standards Explorer
- **Action:** Download from standards.dnv.com (free viewer, may need account)
- **Impact:** **The** standard for environmental loads — Morison equation, diffraction screening, wave spectra, current profiles
- **Effort:** 1 hour

### Rank 8: Acquire Pinkster (1980) "Low Frequency Second Order Wave Exciting Forces"
- **Action:** Locate thesis/paper
- **Impact:** Foundation for QTF calculation validation — directly relevant to OrcaWave QTF module
- **Effort:** University library access

### Rank 9: Index ISOPE Conference Papers
- **Action:** Add `/mnt/ace/docs/conferences/ISOPE` to Phase A config
- **Volume:** 4,516 papers
- **Impact:** Floating structures, ice loads, ocean engineering
- **Effort:** Config change + shared batch run

### Rank 10: Create Marine Sub-Domain Taxonomy in Enhancement Plan
- **Action:** Extend Phase C classification to split marine (32,060 docs) into 7+ sub-domains
- **Impact:** Enables targeted gap analysis per marine sub-topic (diffraction, mooring, VIV, etc.)
- **Effort:** 2-4 hours of Phase C extension + 1 batch run

---

## 8. Summary Scorecard

| Dimension | Current State | Target | Gap |
|-----------|--------------|--------|-----|
| Marine standards tracked | 33 | 50+ | Need ~20 more (DNV-RP-C205, ISO 19901, SNAME T&Rs) |
| Marine standards done | 4 (12%) | 30 (60%+) | Process 26 reference standards |
| Conference papers indexed | 0 | 26,242 | Add 3 conference sources to pipeline |
| OSS tools cloned | 7/41 (17%) | 15/41 (37%) | Clone BEMRosetta, Nemoh, pyHAMS, OCEANLYZ, RAFT, DualSPHysics, py-fatigue, pycatenary |
| OSS tools installed | 0 | 5+ | pip install Capytaine, pyHAMS, OCEANLYZ, wavespectra, MoorPy |
| Research PDFs on disk | 52 | 200+ | Acquire key textbooks + download OMAE/OTC papers |
| Marine sub-domain taxonomy | None | 7+ categories | Extend Phase C classification |
