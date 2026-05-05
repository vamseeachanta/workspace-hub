# FOWT × Oil & Gas Crossover — Coverage Mapping

**Date:** 2026-05-04
**Source:** [Mark Prentice — LinkedIn post on FOW adopting deepwater O&G practice](https://www.linkedin.com/posts/mark-prentice-185722115_floatingoffshorewind-fowt-offshorewind-share-7455555454048452609-vusy)
**Skill:** `field-dev-code-recon`
**Author:** Mark Prentice (4.6k followers); engagement = 28 reactions / 4 comments
**Hashtags:** `#FloatingOffshoreWind #FOWT #OffshoreWind #OilAndGas #FPSO #MooringSystems #EnergyTransition`

---

## 1. Source Thesis

The post argues the floating offshore wind (FOWT) sector should **"adopt and adapt"** proven deepwater O&G knowledge across structural design, integrity management, mooring/stationkeeping, classification, monitoring, safety frameworks, marine operations, and environmental compliance — rather than reinvent the wheel.

This thesis is *partially executed* in our digitalmodel codebase already (HostType enum lists TLP/Spar/Semi; SHM module ships FOWT sensor templates; an OrcaFlex K01 5MW spar FOWT example exists; a FloatingWindTurbine web module exists). The recon below distinguishes what is **STRONG** (working module + tests), **PARTIAL** (skeleton or skill-only), and **GAP** (nothing) so we can prioritise the next wave of FOWT extensions and wiki provenance pages.

---

## 2. Component Inventory (from post)

| # | Capability area | Key keywords/standards from post |
|---|---|---|
| 1 | Hull substructure design (semi-sub, spar, TLP) | Adapt deepwater hull designs; site-specific metocean |
| 2 | Mooring & stationkeeping | Hybrid + taut-leg from FPSO practice; tight watch circles in extreme storms |
| 3 | Asset integrity (25+ yr design life) | Fatigue + corrosion programmes; fitness-for-service |
| 4 | Risk-based classification | DNV/ABS class rules; site-specific load tailoring |
| 5 | Structural Health Monitoring (SHM) | Strain gauges, motion sensors, acoustic on hulls + moorings |
| 6 | Safety Cases & Major Accident Hazards (MAH) | ALARP demonstration |
| 7 | Quantitative Risk Assessment (QRA) | Mooring failure, vessel collision |
| 8 | Permit-to-work + dropped-object prevention | OSHA/IADC framework |
| 9 | Marine procedures & SIMOPS | DNVGL-aligned marine ops |
| 10 | Motion-compensated gangways (W2W) | Weather-window-bound personnel transfer |
| 11 | Weather windows | Operability per DNV-RP-H103 / DNV-ST-N001 |
| 12 | Environmental Impact Assessments | Marine mammal protection, spill response |
| 13 | Coupled aero-hydro response (implicit, FOWT-specific) | Turbine thrust + floater response coupling |

---

## 3. Architecture (component relationships)

```
                       ┌─────────────────────────────┐
                       │   Aero-elastic turbine      │  ← IEC 61400-3-2 (GAP — not in code)
                       │   (thrust, torque, RNA)     │
                       └──────────────┬──────────────┘
                                      │ coupling forces
                       ┌──────────────▼──────────────┐
   IEC 61400-3-2 ──→   │   Floating substructure     │   ← naval_architecture/floating_platform_stability.py
   DNV-ST-0119          │   (semi-sub / spar / TLP)   │   ← hydrodynamics/{aqwa,capytaine,bemrosetta}
   DNV-RP-0286          │                             │   ← concept_selection.py (HostType enum)
                       └──────┬─────────────┬────────┘
                              │             │
              ┌───────────────▼──┐    ┌─────▼──────────────┐
              │ Dynamic export   │    │  Mooring system    │  ← orcaflex/mooring_design.py
              │ cable / umbilical│    │  taut / catenary   │  ← DNV-OS-E301, API-RP-2SK (wiki: ✓)
              │ (watch-circle    │    │  hybrid + taut-leg │
              │  envelope)       │    └─────┬──────────────┘
              └───────┬──────────┘          │
                      │                      │
                      ▼                      ▼
         ┌─────────────────────────────────────────────┐
         │  Asset integrity envelope                   │
         │  - Fatigue (DNV-RP-C203)  ← fatigue/        │
         │  - FFS    (BS7910 / API579) ← asset_integrity│
         │  - CP     (DNV-RP-B401)   ← cathodic_protection│
         │  - SHM    (DNV-ST-0126, API-RP-2SIM)        │
         │           ← structural/offshore_resilience  │
         └─────────────────────────────────────────────┘
                              │
                  ┌───────────▼────────────┐
                  │  Marine ops envelope   │
                  │  - Weather window  ✓   │
                  │  - SIMOPS          GAP │
                  │  - W2W gangway     GAP │
                  │  - Safety Case     GAP │
                  │  - QRA             GAP │
                  └────────────────────────┘
```

---

## 4. Coverage Map — digitalmodel

| # | Component | Standard / Ref | Coverage | digitalmodel module / wiki path |
|---|---|---|---|---|
| 1 | Hull substructure types (TLP / Spar / Semi) | (concept-selection only) | **STRONG** | `field_development/concept_selection.py` (HostType enum) |
| 1a | Floating-platform stability | DNV-OS-C301 (intact), DNV-RP-C205 | **STRONG** | `naval_architecture/floating_platform_stability.py`, `damage_stability.py`, `hydrostatics.py` |
| 1b | Diffraction / RAO / wave loading | — | **STRONG** | `hydrodynamics/aqwa`, `capytaine`, `bemrosetta`, `diffraction`, `rao_analysis`, `wave_spectra.py` |
| 1c | FOWT structural design check | **IEC 61400-3-2**, **DNV-ST-0119**, **DNV-RP-0286** | **GAP** | None (referenced loosely via DNV-ST-0126 in SHM only) |
| 1d | Coupled aero-hydro response | IEC 61400-3-2 §7 | **PARTIAL** | OrcaFlex K01 5MW spar example only (`docs/domains/orcaflex/examples/modular/K01/`); no Python facade |
| 1e | Turbine thrust / aero loading | IEC 61400-1 / -3-2 | **GAP** | None (OCIMF wind loading exists for ship-shape only) |
| 2 | Mooring (taut, catenary, hybrid) | DNV-OS-E301, API RP 2SK | **STRONG** | `orcaflex/mooring_design.py` (citation pilot), mooring-analysis skill |
| 2a | FOWT watch-circle vs dynamic-cable curvature | DNV-RP-0360 | **PARTIAL** | mooring_design has offset; no FOWT-specific watch-circle vs cable-bend tolerance check |
| 3 | Fatigue (steel + welded joints) | DNV-RP-C203 | **STRONG** | `fatigue/` (rainflow, sn_curves, multiaxial, hotspot, weld_classification, spectral_fatigue) |
| 3a | Fitness-for-service / fracture | API 579, BS 7910 | **STRONG** | `asset_integrity/` (API579.py, BS7910_critical_flaw_limits.py, FAD, level1/level2 screeners) |
| 3b | Cathodic protection | DNV-RP-B401, ISO 15589-2 | **STRONG** | `cathodic_protection/` (full module) |
| 4 | Risk-based classification | DNV-OSS-300 / ABS RBA | **GAP** | None (no class-society framework module) |
| 5 | Structural Health Monitoring | DNV-ST-0126, API-RP-2SIM | **STRONG** | `structural/offshore_resilience/structural_health.py` (already has FOWT sensor templates) |
| 6 | Safety Case / MAH / ALARP | UK HSE SCR-2015, NORSOK S-001 | **GAP** | None (zero hits across `src/`) |
| 7 | QRA (mooring failure, vessel collision) | NORSOK Z-013, ISO 17776 | **GAP** | None |
| 8 | Permit-to-work + dropped-object | OSHA / DROPS | **GAP** | None (operational, may be out of scope for code) |
| 9 | SIMOPS planning | NORSOK U-100, DNV-ST-N001 | **GAP** | None (zero hits) |
| 10 | W2W motion-compensated gangway | DNV-ST-0358 | **GAP** | None (no operability module) |
| 11 | Weather windows | DNV-RP-H103, DNV-ST-N001, API RP 2MET | **STRONG** | `orcaflex/weather_window.py`, `marine_ops/` |
| 12 | Environmental impact (EIA, marine mammals) | OSPAR / national | **OUT OF SCOPE** | Out of scope for digitalmodel calc layer |
| 13 | Field-development concept selection | (in-house benchmarks) | **STRONG** | `field_development/concept_selection.py`, `benchmarks.py`, `economics.py` |

---

## 5. Coverage Map — knowledge/wikis (standards pages)

Wiki target: `knowledge/wikis/engineering-standards/wiki/standards/`. Citation contract (`.claude/rules/calc-citation-contract.md`) requires a wiki standards page with #2471 frontmatter for any module emitting `Citation` instances.

| Standard | Title | Wiki page | Status |
|---|---|---|---|
| DNV-OS-E301 | Position mooring | `dnv-os-e301.md` | **PRESENT** |
| DNV-RP-B401 | Cathodic protection design | `dnv-rp-b401.md` | **PRESENT** |
| DNV-RP-C203 | Fatigue (steel structures) | `dnv-rp-c203.md` | **PRESENT** |
| DNV-RP-C205 | Environmental conditions / loads | `dnv-rp-c205.md` | **PRESENT** |
| DNV-RP-H103 | Marine operations modelling | `dnv-rp-h103.md` | **PRESENT** |
| API RP 2SK | Mooring design (FPS) | `api-rp-2sk.md` | **PRESENT** |
| API RP 2MET | Metocean design conditions | `api-rp-2met.md` | **PRESENT** |
| **IEC 61400-3-2** | Design of FOWTs | (none) | **GAP** |
| **DNV-ST-0119** | Floating wind turbine structures | (none) | **GAP** |
| **DNV-RP-0286** | Coupled analysis of FOWTs | (none) | **GAP** |
| **DNV-ST-0126** | Wind-turbine support structures | (none) | **GAP** *(referenced in code without provenance)* |
| **DNV-RP-0360** | Subsea power cables (dynamic) | (none) | **GAP** |
| **DNV-ST-0358** | W2W transfer / gangway certification | (none) | **GAP** |
| **API RP 2SIM** | Structural integrity management | (none) | **GAP** *(referenced in code without provenance)* |
| **NORSOK Z-013** | Risk and emergency-preparedness analysis | (none) | **GAP** |

The two GAP rows annotated *referenced in code without provenance* are immediate citation-contract violations under `.claude/rules/calc-citation-contract.md` D2 — `structural_health.py` cites DNV-ST-0126 + API-RP-2SIM in its docstring without a resolvable wiki page.

---

## 6. Standards Quick Reference (FOWT lens)

```
FOWT-specific (post-O&G crossover):
   IEC 61400-1     — Wind turbines (general)
   IEC 61400-3-1   — Fixed offshore wind turbines
   IEC 61400-3-2   — Floating offshore wind turbines  ← critical, missing
   DNV-ST-0119     — Floating wind turbine structures ← critical, missing
   DNV-ST-0126     — Wind-turbine support structures
   DNV-RP-0286     — Coupled analysis of FOWTs        ← critical, missing
   DNV-RP-0360     — Dynamic subsea power cables
   DNV-RP-0416     — Corrosion protection (offshore wind)

O&G-origin, applicable to FOWT:
   DNV-OS-E301 / API RP 2SK    — Position mooring
   DNV-RP-C203 / BS 7608        — Fatigue (welded joints)
   DNV-RP-C205                  — Env conditions / loads
   DNV-RP-B401 / ISO 15589-2    — Cathodic protection
   DNV-RP-H103 / API RP 2MET    — Marine operations / metocean
   DNV-ST-N001                  — Marine operations general
   API 579-1 / BS 7910          — Fitness-for-service
   API RP 2SIM                  — Structural integrity management

Risk / safety:
   NORSOK Z-013                 — QRA framework
   NORSOK S-001                 — Technical safety
   UK HSE SCR-2015              — Safety Case Regulations
   ISO 17776                    — Major-accident hazard ID

Personnel / W2W:
   DNV-ST-0358                  — W2W gangway certification
   ISO 19905-1 (jack-up)        — Gangway-relevant motion limits
```

---

## 7. Prioritised Follow-Up

Filed as digitalmodel issues (see Section 8 commit log). Priority gradient:

| Priority | Why |
|---|---|
| **High** | Wiki standards-page family (IEC 61400-3-2, DNV-ST-0119, DNV-RP-0286, DNV-ST-0126, API RP 2SIM) — unblocks citation contract for any FOWT calc and resolves two existing in-code dangling references |
| **Medium** | FOWT coupled aero-hydro response Python facade — codifies the K01 spar example pattern + IEC 61400-3-2 design-load cases |
| **Medium** | FOWT watch-circle envelope check vs dynamic-cable curvature (extends `mooring_design.py` to DNV-RP-0360) |
| **Medium** | Safety Case / MAH ALARP framework (NORSOK Z-013 + UK HSE SCR-2015) — broader than FOWT but explicitly post-thesis |
| **Lower** | W2W motion-compensated gangway operability module (DNV-ST-0358) — operationally bounded, lower calc payoff |

EIA / spill / marine mammal protection deemed **out of scope** for digitalmodel (calc layer).

---

## 8. Issue Index

This section is back-filled after Phase 4 completes.

| # | Title | Repo | Status |
|---|---|---|---|
| TBD | Wiki standards page family for FOWT (IEC 61400-3-2, DNV-ST-0119, DNV-RP-0286, DNV-ST-0126, API-RP-2SIM) | digitalmodel | filed |
| TBD | FOWT coupled aero-hydro response analysis facade | digitalmodel | filed |
| TBD | FOWT watch-circle envelope check vs dynamic-cable curvature | digitalmodel | filed |
| TBD | Safety Case / MAH ALARP framework module | digitalmodel | filed |
| TBD | W2W motion-compensated gangway operability module | digitalmodel | filed |

---

## 9. References

- Source: LinkedIn post 7455555454048452609-vusy (Mark Prentice, accessed 2026-05-04)
- Existing FOWT artifacts in repo:
  - `src/digitalmodel/field_development/concept_selection.py` — HostType enum (TLP / Spar / Semi)
  - `src/digitalmodel/structural/offshore_resilience/structural_health.py` — FOWT SHM templates, references DNV-ST-0126 + API-RP-2SIM
  - `src/digitalmodel/web/digitaltwinfeed/FloatingWindTurbine/FloatingWindTurbine.py` — web app module
  - `docs/domains/articles/ENG_FloatingWindPower.md` — domain article
  - `docs/domains/orcaflex/examples/modular/K01/K01 5MW spar FOWT/` — OrcaFlex spar FOWT example
  - `knowledge/wikis/marine-engineering/wiki/comparisons/offshore-wind-oil-gas-cross-section-assessment.md` — directly on-thesis crossover note
- Citation contract: `.claude/rules/calc-citation-contract.md`
