# GitHub Issues to Create — Next Phase

> Generated: 2026-04-06 overnight exit

## Issue 1: Test coverage uplift: 97 tests for new overnight modules (#1843, #1850, #1851, #1861)
**Labels**: agent:codex, cat:engineering, test-coverage

## Context

Tonight's overnight session added 4 new modules with 151 passing tests:
- concept_selection.py (94 tests)
- gyradius.py (21 tests)  
- floating_platform_stability.py (21 tests)
- subsea_bridge.py (15 tests)

However, test coverage is still below the 20% target. Need integration tests, edge case coverage, and parameterized tests to push toward the milestone.

## Scope

### concept_selection.py
- Parameterized tests for all 10 GoM reference fields
- Edge cases: boundary water depths, invalid reservoir sizes
- Integration: concept_selection + subsea_bridge pipeline

### gyradius.py
- Additional platform types: drillship, jack-up
- Property tests: inertia roundtrip invariance
- Benchmark: compare against known platform reference data

### floating_platform_stability.py
- Damaged stability scenarios
- Wind heel edge cases (extreme environments)
- Integration: GZ curve generation with real cross curves

### subsea_bridge.py
- End-to-end: JSON load → query → concept_selection
- Mock data provider for CI
- Host type distribution validation

## Acceptance Criteria
- All 4 modules pass existing 151 tests
- Minimum 300 total tests across the 4 modules
- Coverage report shows >15% for these modules

## References
- #1843 concept_selection framework
- #1850 floating platform stability
- #1851 gyradius calculator
- #1861 SubseaIQ bridge
- #1824 test coverage uplift (parent issue)


---

## Issue 2: Integrate worldenergydata vessel fleet and hull models into digitalmodel
**Labels**: agent:claude, cat:engineering, naval-architecture

## Context

Issue #1859 from the Claude queue. The worldenergydata repository contains vessel fleet data and hull models that should be integrated into digitalmodel/naval_architecture/.

## Scope

1. Review worldenergydata repository structure for vessel/hull data
2. Create vessel_fleet.py module in naval_architecture/
3. Create hull_properties.py module with:
   - Principal dimensions
   - Hydrostatic curves
   - Capacity plan integration
4. Map vessel types to platform types in field_development module
5. Unit tests for all new functionality

## Data Sources
- worldenergydata/vessels/
- worldenergydata/hulls/

## References
- #1849 Naval architecture expansion epic
- #1850 Floating platform stability
- #1851 Gyradius calculator


---

## Issue 3: Integrate worldenergydata FDAS + economics into field_development module
**Labels**: agent:claude, cat:engineering, field-development

## Context

Issue #1858 from the Claude queue. The worldenergydata repository contains Field Development Analysis System (FDAS) data and economic models that complement tonight's concept_selection.py implementation.

## Scope

1. Review worldenergydata economics data structure
2. Create economics.py module in field_development/ with:
   - NPV analysis for field developments
   - Breakeven price calculations
   - CAPEX/OPEX validation against GoM benchmarks
3. Integrate with tonight's capex_estimator.py and opex_estimator.py
4. Link with SubseaIQ bridge (#1861) for analogue-based economics
5. Unit tests

## References
- #1843 Concept selection framework (tonight's work)
- #1861 SubseaIQ bridge (tonight's work)
- worldenergydata/ economics/


---

## Issue 4: Resume Gemini overnight batch when credits refresh — 33 issues pending
**Labels**: agent:gemini, overnight, batch

## Context

The April 6 overnight batch attempted Gemini tasks but encountered credit exhaustion across all 3 providers:
- OpenRouter: HTTP 402 — only 54K tokens remaining (insufficient for large tasks)
- Copilot: HTTP 403 on programmatic access
- Huggingface: HTTP 401 — expired credentials

When credits refresh, resume these high-priority Gemini tasks:

## Tasks

### #1863 — Migrate DDE remote literature (5,456 PDFs)
- 14.6 GB of reservoir engineering and field development textbooks
- Priority: Reservoir Engineering textbooks first
- Plan: docs/document-intelligence/dde-lit-migration-plan.md
- Agent: Gemini (large PDF context ingestion)

### #1770 — Expand standards-ledger
- Add SNAME, OnePetro, BSI, Norsok organizations
- Standards need keyword extraction and mapping to digitalmodel functions
- Agent: Gemini (standards research + classification)

### #1624 — Acquire marine hydrodynamics textbooks
- Faltinsen, Pinkster, Newman, SNAME PNA
- Catalog what's available, what needs acquisition
- Map chapters/topics to digitalmodel modules
- Agent: Gemini (textbook analysis)

### #1769 — Phase B summarization (394K documents)
- Second-pass summarization of already-extracted conference papers
- Agent: Gemini (batch summarization at scale)

## Prerequisites
- Verify OpenRouter credit balance > $50
- Verify Copilot auth still valid: `hermes login copilot`
- Verify Huggingface auth: `hermes login huggingface`

## References
- #1862 Conference indexing (DONE — script created)
- #1823 Standards mapping (DONE — 7947 functions mapped)


---

## Issue 5: Seakeeping module: 6-DOF motion analysis from hydrodynamic coefficients
**Labels**: agent:claude, cat:engineering, hydrodynamics

## Context

Issue #1960 from the Claude queue. The digitalmodel/hydrodynamics module needs a seakeeping module that consumes RAOs, wave spectra, and platform motion data to produce motion statistics and operability analysis.

## Scope

1. Create seakeeping.py module in hydrodynamics/ with:
   - Motion statistics from RAOs and wave spectra (spectral moments)
   - Significant motion amplitudes (heave, roll, pitch, etc.)
   - Motion exceedance probabilities
   - Operability analysis (motion criteria + scatter diagram integration)
2. Integration with tonight's gyradius.py (motion periods)
3. Integration with tonight's floating_platform_stability.py (stability in waves)
4. Unit tests with reference solutions

## Integration Points
- hydrodynamics/wave_spectra.py (wave spectra generation)
- hydrodynamics/diffraction/ (RAO data)
- naval_architecture/gyradius.py (motion natural periods)
- naval_architecture/floating_platform_stability.py (stability check)

## References
- #1850 Floating platform stability (tonight's work)
- #1851 Gyradius calculator (tonight's work)
- DNV-RP-H103 (marine operations modelling)
- ITTC recommended procedures


---

