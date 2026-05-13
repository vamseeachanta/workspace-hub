# Cathodic Protection — DNV-RP-B401 Edition + Canonicalization Investigation

**Issue:** [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) (cross-domain duplicate-implementation cleanup epic), surfaced by Pipelines R5 [#2692](https://github.com/vamseeachanta/workspace-hub/issues/2692) Finding 3
**Investigator:** Claude (read-only recon, 2026-05-13)
**Status:** Findings + recommendation only — no code changes, no commits.
**Severity classification:** **HIGH — regulatory hazard** (DNV-RP-B401 2017 vs 2021 edition drift in production calc paths)

---

## Executive Summary

Three parallel cathodic protection surfaces exist in `digitalmodel/src/`. Two of the three are wired
to **different editions of the same DNV recommended practice** (2017 vs 2021), and both claim
DNV-RP-B401 compliance without surfacing the edition to the caller. This is a calc-defensibility
hazard — DNV-RP-B401 2021 (May 2021) materially revised current-density tables, coating-breakdown
categories, and anode-resistance section numbering relative to the 2010/2017 editions. A customer
auditor (DNV, ABS, BV) would require explicit edition disclosure on every CP deliverable.

Compounding the hazard: the YAML config `infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml`
**advertises three calc types** (`DNV_rp_b401_2011`, `DNV_rp_b401_2021_05`, `ABS_gn_ships_2018`),
but the router only dispatches on `DNV_RP_B401_offshore` (a single edition, 2021). Two of the three
advertised calc types raise `ValueError("not IMPLEMENTED")`.

**Recommended path: Option β — edition-parameterized single surface, executed in phases.**
Functional package retained as canonical implementation substrate; router collapsed into a thin
edition-dispatching adapter; explicit `edition: Literal["2010", "2017", "2021"] = "2021"` exposed at
every public entry point with edition currency surfaced in every result object's `standard` field.

---

## 1. Edition Evidence (verified independently by grep)

### Surface 1 — Functional package `digitalmodel/cathodic_protection/`

| File | Line | Quoted edition citation |
|---|---|---|
| `dnv_rp_b401.py` | 1 | `"""DNV-RP-B401 — Cathodic Protection Design (2005/2017).` |
| `anode_sizing.py` | 9 | `- DNV-RP-B401 (2017) "Cathodic Protection Design" §5-7, §10` |
| `anode_sizing.py` | 36 | `# Al-Zn-In anode properties (DNV-RP-B401 Table 10-6)` (Table 10-x ⇒ 2010/2017 numbering) |
| `coating.py` | 10 | `- DNV-RP-B401 (2017) "Cathodic Protection Design" §10.7, Tables 10-2, 10-4` |
| `coating.py` | 24, 37 | `Coating system categories per DNV-RP-B401 Table 10-2` ; `DNV-RP-B401 Table 10-4: Coating breakdown factor constants` |
| `cp_monitoring.py` | 11 | `- DNV-RP-B401 (2017) "Cathodic Protection Design" §12` |
| `cp_reporting.py` | 10 | `- DNV-RP-B401 (2017) §12 — Documentation requirements` |
| `anode_depletion.py` | 9 | `- DNV-RP-B401 (2017) "Cathodic Protection Design" §7.7, §10.8` |
| `marine_structure_cp.py` | 9 | `- DNV-RP-B401 (2017) "Cathodic Protection Design"` |
| `marine_cp.py` | 9–10 | `- DNV-RP-B401 (2017) "Cathodic Protection Design" §7, Table 10-1` ; `§10.4 — calcareous deposits` |

**Edition signature: DNV-RP-B401 (2017)**, with `dnv_rp_b401.py:1` also acknowledging the 2005 lineage.
All Table refs use the 2010/2017 chapter numbering (Tables 10-1 through 10-8, §7, §10).

### Surface 2 — Router-based `infrastructure/base_solvers/hydrodynamics/cathodic_protection.py`

| File | Line | Quoted edition citation |
|---|---|---|
| `cathodic_protection.py` | 3 | `from ... cp_DNV_RP_B401_2021 import (...)` (single hard dependency on 2021 module) |
| `cathodic_protection.py` | 733 | `"""Cathodic protection for offshore fixed platforms per DNV-RP-B401 (2021).` |
| `cathodic_protection.py` | 738 | `Standard: DNV-RP-B401 May 2021` |
| `cathodic_protection.py` | 754 | `cfg["results"] = { "standard": "DNV-RP-B401-2021", ...}` (result emits "2021" literal) |
| `cp_DNV_RP_B401_2021.py` | 1–2 | `"""DNV-RP-B401-2021 cathodic protection calculations for offshore fixed platforms.` |
| `cp_DNV_RP_B401_2021.py` | 8 | `Standard: DNV-RP-B401 (May 2021 edition)` |
| `cp_DNV_RP_B401_2021.py` | 9 | `Sections: 3.3 (current densities), 3.4 (coating breakdown), 4.9 (anode resistance)` |
| `cp_DNV_RP_B401_2021.py` | 14, 30, 38, 44 | `# B401-2021 Table 3-1: Mean design current densities` ; `# B401-2021 Section 3.4.6: Coating breakdown factors` ; `# Electrochemical capacity (Ah/kg) for sacrificial anode materials — B401-2021 Sec.3.6` ; `# Steel protective potential and anode potential (V vs Ag/AgCl) — B401-2021 Sec.2.4` |
| `cp_sacrificial_anode_b401.py` | 8 | `Reference: DNV-RP-B401 (all editions share the same core sizing equations)` ← **only file claiming edition-agnosticism** |

**Edition signature: DNV-RP-B401 (May 2021)**, using the 2021 chapter renumbering (§3.3, §3.4.6, §4.9 — vs §7, §10 in the 2017 edition).

### Surface 3 — Deprecation shim `infrastructure/common/cathodic_protection.py`

| File | Line | Quote |
|---|---|---|
| `infrastructure/common/cathodic_protection.py` | 1–17 | Pure re-export shim — `"digitalmodel.infrastructure.common.cathodic_protection is deprecated. Import from digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection"`. **Re-exports the 2021-edition router class.** |

**R5 finding verified independently.** The functional package signs **2017**; the router signs **2021**.

---

## 2. Standard Parameter Delta — 2017 vs 2021 (numerical divergences observed in code)

DNV-RP-B401 underwent a substantive revision between Oct 2017 and May 2021. Differences observed
**in the two implementations** (not extrapolated from external knowledge):

| # | Parameter | 2017 (functional pkg) | 2021 (router) | Divergence |
|---|---|---|---|---|
| 1 | **Section reference for design current densities** | §7 / Table 10-1 (`marine_cp.py:9,43`) | §3.3 / Table 3-1 (`cp_DNV_RP_B401_2021.py:14,176`) | Section renumbering — same physical table, different paragraph location |
| 2 | **Section ref for coating breakdown** | §10.7 / Table 10-4 (`coating.py:10,37`) | §3.4.6 (`cp_DNV_RP_B401_2021.py:28,127`) | Section renumbering |
| 3 | **Section ref for anode resistance** | Table 10-7 (`anode_sizing.py:193`, `dnv_rp_b401.py:129`) | §4.9 (`cp_DNV_RP_B401_2021.py:299`) | Section renumbering |
| 4 | **Coating-breakdown table shape** | 9 categories: FBE, 3LPE, 3LPP, coal-tar-enamel, asphalt-enamel, polyurethane, concrete, neoprene, none (`coating.py:39`) | 4 categories: I, II, III, bare. **Category II ("Anti-friction thin film / PTFE")** is new in 2021 (per `cp_DNV_RP_B401_2021.py:32`) | **Material-coverage divergence** — 2017's 9-category scheme cannot be 1:1-mapped to 2021's I/II/III scheme. **Customer would need explicit re-mapping** |
| 5 | **Coating breakdown constants (a, b)** | FBE: (0.02, 0.003); 3LPE: (0.01, 0.002); coal-tar: (0.05, 0.005); polyurethane: (0.03, 0.004) (`coating.py:40-48`) | Cat I: (0.05, 0.020); Cat II: (0.10, 0.030); Cat III: (0.25, 0.050); bare: (1.0, 0.0) (`cp_DNV_RP_B401_2021.py:31-36`) | **Numerically different** — the values aren't comparable until the user picks a category mapping. Cat I (0.05/0.020) is **harsher** than functional pkg's "high quality" FBE (0.02/0.003) — a CP design sized under 2017 categorization may be undersized under 2021 |
| 6 | **Submerged-zone current densities** | Climate-region table: TEMPERATE/submerged → (initial 200, mean 100, final 120) mA/m² (`marine_structure_cp.py:49`). Temperate mean = **0.100 A/m²** | Temperature-banded: submerged @ >12-17 °C → bare 0.100, coated 0.060 A/m² (`cp_DNV_RP_B401_2021.py:18-22`) | **Different axis** — 2017 stratifies by climate region × zone; 2021 stratifies by seawater-temperature band × coated-vs-bare. Both schemes pull from the same physical Table 10-1/Table 3-1 data but the bucketing rules differ |
| 7 | **Splash zone treatment** | Splash zone hard-coded to 0.0 (`marine_structure_cp.py:57-60`) — "not CP-protected" | Splash zone: coated 0.100, bare 0.200 (`cp_DNV_RP_B401_2021.py:24`) — actively current-demanded | **Materially divergent** — 2017 surface treats splash as out-of-scope; 2021 surface treats splash as CP-protected. Sizing answers diverge **significantly** for jacket structures with splash zone |
| 8 | **Anode resistance formula (stand-off / Dwight)** | `(rho/2piL) * (ln(4L/r) - 1)` (`anode_sizing.py:224`, `dnv_rp_b401.py:150`) | `(rho/2piL) * (ln(4L/r) - 1)` (`cp_DNV_RP_B401_2021.py:339`) | **Identical** — equation unchanged across editions |
| 9 | **Anode resistance formula (flush-mount)** | `(rho/piL) * (ln(2L/r) - 0.5)` (`dnv_rp_b401.py:327`, McCoy half-space) | `(rho/2piL) * (ln(4L/r) - 1)` (Dwight — same as stand-off; `cp_DNV_RP_B401_2021.py:332,339`) | **Equation choice differs**. 2017 surface uses McCoy half-space (denominator πL); 2021 surface uses Dwight (denominator 2πL). For the same geometry, McCoy returns **2× higher resistance** than Dwight. **This is the single most impactful numerical divergence** for hull-mounted anodes |
| 10 | **Anode resistance formula (bracelet)** | `0.315 * rho / sqrt(A)` (`cp_sacrificial_anode_b401.py:166` — claimed edition-agnostic) | `(rho/2piL) * (ln(2πL/r) - 1)` modified Dwight (`cp_DNV_RP_B401_2021.py:346`) | **Different formula entirely**. 2021 surface uses an Annex-B modified Dwight requiring L and r; 2017 surface uses the simplified area-based 0.315 form. For typical pipeline bracelets these can disagree by 10-30%. |
| 11 | **Utilization factor defaults** | stand-off 0.90, flush 0.85 (`dnv_rp_b401.py:35-36`, `anode_sizing.py:38-39`), bracelet 0.80 (`anode_sizing.py:40`) | Default 0.85 across all anode types (`cp_DNV_RP_B401_2021.py:367`) | Functional pkg embeds 2017 Table 10-8 per-type values; router uses a single conservative default. For stand-off anodes (90% in 2017 vs 85% in 2021-router) ⇒ **5.9% more anode mass** under router for the same demand |
| 12 | **Electrochemical capacity (Al-Zn-In)** | 2000 A·h/kg (`dnv_rp_b401.py:31`, `anode_sizing.py:37`) | 2000 A·h/kg (`cp_DNV_RP_B401_2021.py:39`) | Identical |
| 13 | **Electrochemical capacity (Zn)** | Not surfaced (functional pkg targets Al only) | 780 A·h/kg (`cp_DNV_RP_B401_2021.py:40`) | Router exposes both materials; functional pkg only Al |
| 14 | **Stubbiness check on Dwight** | Not enforced in `dnv_rp_b401.py:150` (any L, r accepted) | Hard validation: `4L/r > e` else `ValueError` (`cp_DNV_RP_B401_2021.py:334`) | Router is **stricter** — functional pkg can silently return nonsense for stubby geometry |
| 15 | **Driving voltage / protection potential** | -0.800 V structure, -1.050 V anode ⇒ 0.250 V drive (`dnv_rp_b401.py:14-25`) | -0.800 V structure, -1.050 V Al anode ⇒ 0.250 V drive (`cp_DNV_RP_B401_2021.py:43-49`) | Identical |

**Net: 15 dimensions examined; 10 show non-trivial divergence**; 4 of those (items 4, 5, 7, 9) are
likely to produce materially different anode counts for the same input case.

---

## 3. Per-Surface Inventory

### Surface 1: Functional package `digitalmodel.cathodic_protection.*`

- **LOC:** 4 731 lines across 16 modules (excl. `__init__.py`); package facade `__init__.py` is 331 LOC
  re-exporting **100+ public names** (60 functions/classes per `__all__` list + sub-namespace aliases)
- **Public surface (selected):** `current_demand`, `anode_mass_requirement`, `coating_breakdown_factor`,
  `anode_resistance_slender_standoff`, `anode_current_output`, `protected_length`, `flush_anode_resistance`,
  `equivalent_radius_from_mass`, `number_of_anodes` (from `dnv_rp_b401.py`); `design_cp_system`,
  `AnodeSizingInput/Result` (`anode_sizing.py`); `coating_breakdown_factors`, `CoatingCategory`
  (`coating.py`); `design_marine_cp`, `get_seawater_current_density` (`marine_cp.py`); `design_pipeline_cp`,
  `calculate_anode_spacing` (`pipeline_cp.py`); plus marine-structure, ICCP, survey, monitoring,
  corrosion-rate, anode-depletion, stray-current, reporting modules.
- **Standards refs (docstring):** Per §1 above — uniformly **DNV-RP-B401 (2017)** with Table 10-x
  numbering; supplementary references to DNV-RP-F103 (2016), ISO 12473 (2006), ISO 15589-1 (2015) /
  -2 (2004), NACE SP0169 (2013), SP0176, SP0207, SP0502, TM0497 (2018), NORSOK M-506 (2005),
  ASTM G42 (1996), G80 (1998), EN 50162 (2004), EN 15280 (2013), ISO 18086 (2019), API RP 1632
  (1996, 3rd Ed.), de Waard & Milliams (1975), McCoy (1974), Dwight (1936)
- **Tests:** 18 test files under `tests/cathodic_protection/`, 206 `def test_` functions
  (`test_dnv_rp_b401_doc_verified.py` 36, `test_fuel_system_cp.py` 22, `test_iso_15589_2.py` 20,
  `test_api_rp_1632.py` 16, `test_anode_sizing.py` 15, `test_pipeline_cp_design.py` 13, `test_marine_cp.py` 11,
  remaining 30+ smaller). Imports cleanly from `digitalmodel.cathodic_protection.*` — **no shim usage.**
- **Active callers in src/:**
  - `cathodic_protection/__init__.py` (facade self-import)
  - `cathodic_protection/fuel_system_cp.py` (intra-package import of `api_rp_1632`)
  - **No external src/ caller** — the engine.py YAML dispatch does **not** route through this package.
    This is the most consequential finding: the functional package is exercised **only by tests and by
    direct Python users importing it manually**.
- **Last meaningful commit (per `git log -1`):**
  - `__init__.py` — `f65d6b1e 2026-04-02 feat(cathodic_protection): marine structure CP assessment — multi-zone TDD (#1676)`
  - `dnv_rp_b401.py` — `2c185d2d 2026-03-24 chore: fresh repo after slimming`
  - `coating.py` / `anode_sizing.py` / `cp_*.py` — `bf9506da 2026-04-02 Expand cathodic_protection package: add 10 new modules (15 total)`

### Surface 2: Router-based `digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection.CathodicProtection`

- **LOC:** `cathodic_protection.py` 1 853 ; supporting `cp_DNV_RP_B401_2021.py` 459 ; `cp_DNV_RP_F103_2010.py` 378 ; `cp_sacrificial_anode_b401.py` 253 ; `cp_astm_g42.py` 175 ; `cp_astm_g80.py` 141. **Total: 3 259 LOC**.
- **Public surface:** Single class `CathodicProtection` with method `router(cfg) -> cfg` dispatching on
  `cfg["inputs"]["calculation_type"]` ∈ `{"ABS_gn_ships_2018", "DNV_RP_F103_2010",
  "ABS_gn_offshore_2018", "DNV_RP_B401_offshore"}`. Module-level helpers `_b401_*`, `_dnv_*`, `_abs_*`
  are notionally private but consumed by the test suite via `infrastructure.common.cp_DNV_RP_B401_2021`
  shim.
- **Standards refs (docstring):** **DNV-RP-B401 (May 2021)**, DNV-RP-F103 (2010), ABS Guidance Notes for
  Cathodic Protection of Ships (Dec 2017), ABS Offshore (2018), ASTM G42 (1996, in standalone `cp_astm_g42.py`),
  ASTM G80 (1998, in `cp_astm_g80.py`)
- **Tests:** 12 test files under `tests/specialized/cathodic_protection/` + 1 under
  `tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py`. Test count: 230
  `def test_` (`test_cathodic_protection_b401.py` 59, `test_sacrificial_anode_b401.py` 55,
  `test_cathodic_protection_dnv.py` 39, `test_astm_g42.py` 19, `test_astm_g80.py` 19,
  `test_dnv_pipeline_variants.py` 13, `test_abs_ship_variants.py` 13, `test_dnv_f103_2010_calcs.py` 13,
  `test_abs_ship_variants_wrk271.py` 10, `test_dnv_pipeline_variants_wrk271.py` 10, smaller files).
- **Active callers in src/:**
  - `engine.py:9,145-147` — **the YAML config dispatcher routes here**, not the functional pkg.
    Every YAML-driven CP run uses this surface.
  - `infrastructure/common/cathodic_protection.py` (deprecation shim — re-exports)
  - `infrastructure/common/cp_DNV_RP_B401_2021.py` (parallel shim — re-exports `_b401_*` helpers)
  - `infrastructure/common/cp_sacrificial_anode_b401.py` (parallel shim — re-exports)
  - `visualization/reporting/cp_html_report.py` — generates HTML dashboards consuming router result schema
- **Test import quirk (HIGH-SIGNAL FINDING):** all 130+ "router-based" tests import from
  `digitalmodel.infrastructure.common.cathodic_protection` — i.e. they exercise the **deprecation shim**,
  which emits `DeprecationWarning` on every test run. Three deprecation shims (`cathodic_protection.py`,
  `cp_DNV_RP_B401_2021.py`, `cp_sacrificial_anode_b401.py`) under `infrastructure/common/` redirect to
  `base_solvers/hydrodynamics/`. Documented warning is **routinely ignored**.
- **Last meaningful commit (per `git log -1`):**
  - `cathodic_protection.py` / `cp_*.py` (all) — `2c185d2d 2026-03-24 chore: fresh repo after slimming`
    — no commits since end-March

### Surface 3: Deprecation shim `infrastructure/common/cathodic_protection.py`

- **LOC:** 19 (pure re-export + `DeprecationWarning`)
- **Public surface:** `CathodicProtection` only (re-exported from base_solvers)
- **Standards refs:** None (pass-through)
- **Tests:** 0 dedicated, but all `tests/specialized/cathodic_protection/test_*` tests import through it
- **Active callers:**
  - `tests/specialized/cathodic_protection/test_*.py` (12 files) — **130+ tests transit this shim every run**
  - `tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py` (1 file, 39 tests)
- **Last meaningful commit:** `2c185d2d 2026-03-24` — same monolithic landing as the router itself

---

## 4. Canonical Selection — Comparison Matrix

| Criterion | Surface 1 (functional) | Surface 2 (router) | Surface 3 (shim) |
|---|---|---|---|
| **DNV edition signed** | 2017 (legacy production-relevant) | 2021 (current — and the only edition customers can audit against today for new builds) | n/a (passes through Surface 2's edition) |
| **LOC** | 4 731 (16 modules) | 3 259 (6 modules) | 19 |
| **Public functions/classes** | 100+ named exports across 16 modules | 1 class with 1 router method (rest of API is via `cfg` dict mutation) | 1 class re-export |
| **Test functions** | 206 (clean imports) | 230 (transit deprecation shim — emits warnings) | 0 dedicated |
| **Active src/ callers (non-self)** | **0** (only tests + direct Python users) | **2** — `engine.py` (YAML pipeline) + HTML reporting | — |
| **Standards refs in docstring** | Uniform "(2017)" with §7 / §10 / Tables 10-x numbering | Uniform "(May 2021)" with §3.3 / §3.4.6 / §4.9 numbering | n/a |
| **Coverage breadth** | Broader: pipeline_cp + marine_cp + marine_structure_cp + ISO 15589-2 + API RP 1632 + NACE SP0169 + ASTM G42/G80 + coating + corrosion_rate + anode_depletion + cp_monitoring + cp_survey + cp_reporting + stray_current + iccp_design + fuel_system_cp | Narrower: B401 offshore platform, F103 pipeline, ABS Ships 2018, ABS Offshore 2018 |
| **API style** | Functional (each module exports pure functions + pydantic dataclasses) | Class-based router (`cfg` dict input/output, single dispatch on string key) |
| **Configurability** | Per-function parameter exposure (no implicit defaults beyond docstring-declared B401-2017 values) | YAML config-driven — `calculation_type` is the only edition selector |
| **YAML-config integration** | None | Yes — `infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml` |
| **Edition selectability at call site** | **No** — edition is hard-coded as 2017 in module docstrings; numeric constants embed 2017 table values | **No** — edition is hard-coded as 2021 in `_b401_*` module; the router's `DNV_RP_B401_offshore` calc-type does not parameterize edition |
| **Validation / fail-loud behavior** | Lighter — no stubbiness check on Dwight, accepts any `(L, r)` | Heavier — `_require_finite`, `_require_zone_field`, `_require_valid_material`; stubbiness check enforced |
| **Last touch** | Apr 2026 (4 module-level commits since the 2026-03-24 slim) | 2026-03-24 (single monolithic landing, no follow-up) |

### Score (test signal × caller signal × audit-readiness × edition-currency)

| Dimension (0–3) | Functional | Router |
|---|---|---|
| Test breadth (206 vs 230 — both deep) | 3 | 3 |
| Active src/ wiring (0 callers vs 2 prod callers) | 0 | 3 |
| Edition currency for new builds (2017 vs 2021) | 1 | 3 |
| Edition currency for legacy projects (2017 vs 2021) | 3 | 1 |
| Coverage breadth (8 standards vs 4 standards) | 3 | 1 |
| Validation discipline | 1 | 2 |
| Audit-defensibility (single explicit standard string in result) | 1 (no `standard` field in returned objects) | 2 (`cfg["results"]["standard"] = "DNV-RP-B401-2021"`) |
| API ergonomics (Python-callable, type-hinted, dataclass results) | 3 | 1 (cfg-dict mutation) |
| **Total** | **15** | **16** |

**The two surfaces score within 1 point of each other** — neither is the clear winner. This is
substantively different from the catenary investigation (`docs/field-development/catenary-canonicalization-investigation.md`)
where the modern subpackage scored 9 vs the legacy variants at 1–4. The CP case has **two genuinely
useful surfaces with non-overlapping strengths**.

---

## 5. Regulatory Framing

The R5 audit's framing ("DNV edition shadow is a calc-defensibility hazard") is correct but
under-states the issue. A customer auditor (DNV, ABS, BV, Lloyd's Register) reviewing a CP design
deliverable expects, at minimum:

1. **Explicit edition disclosure on every page of the deliverable** — "DNV-RP-B401 (May 2021)" or
   "DNV-RP-B401 (Oct 2017)"; bare "DNV-RP-B401" is non-compliant for IRM (Inspection, Repair,
   Maintenance) handoffs.
2. **Section refs that match the cited edition** — a deliverable citing "§7 / Table 10-1" implies 2010
   or 2017; a deliverable citing "§3.3 / Table 3-1" implies 2021. Section ref mismatch flags the calc.
3. **Edition selection traceable to the contract or project basis-of-design (BOD)** — newbuilds typically
   contract against the latest edition (2021 in 2026); life-extension / FFS work on existing assets
   often contracts against the original-design edition (2017 or earlier) to preserve audit continuity.
4. **Each numeric constant traceable to a table/equation cite** — the citation-emission contract from
   workspace-hub#2685 directly addresses this; CP code is currently 0% compliant
   (Pipelines R5 Finding 5 verified: `grep -rn "from digitalmodel.citations" ...cathodic_protection/`
   returns zero matches).

The current state — two parallel surfaces signing different editions with no edition-selection
mechanism — means:

- **A user importing `digitalmodel.cathodic_protection.dnv_rp_b401.coating_breakdown_factor`** gets 2017
  coating constants regardless of the actual project edition.
- **A user running `digitalmodel cathodic_protection my_cfg.yml`** with the YAML dispatch invariably
  gets 2021 calculations regardless of project edition, AND the YAML advertises a
  `DNV_rp_b401_2011` calc type that **does not actually exist in the router** (raises `ValueError`).

Either is reportable as a calc-defensibility defect at a DNV class survey.

---

## 6. Recommendation — Option β (edition-parameterized merge, phased)

**Selected: Option β.** Rationales (in priority order):

1. **Regulatory framing dominates.** Picking 2017 (Option α-functional) loses currency for newbuild
   audits. Picking 2021 (Option α-router) loses legacy-project defensibility AND drops 4 standards
   (ISO 15589-2, API RP 1632, NACE SP0169, ASTM G42/G80 + corrosion_rate / cp_monitoring / cp_survey /
   stray_current modules) that have no counterpart in the router.
2. **Option γ (keep both, document split) is brittle.** It freezes the contradiction: users will
   continue to import from either surface and silently get edition drift. Test suites will continue to
   exercise the deprecation shim chain. A code-review hook cannot enforce edition consistency across
   two parallel surfaces because the surfaces sign different editions by design.
3. **The functional package's data ergonomics + the router's edition discipline are complementary,
   not competing.** A merged surface keeps the functional API as the implementation substrate
   (broader, better-validated, modern Python idioms) and adds an `edition` parameter that selects
   between 2010/2017 vs 2021 table constants at call time.
4. **The catenary precedent (#2686) is the wrong model here.** Catenary had byte-identical duplicates
   and physically-incorrect variants — there was a clear "modern, correct, well-tested" choice. CP has
   two production-grade surfaces. The PipeCapacity case (5-way duplicate, similar package-level
   collision) is closer, but PipeCapacity duplicates lack the edition-currency dimension. CP is its
   own pattern: **edition-parameterized merge.**

### Proposed phased plan (deferred to a separate plan PR; this doc is investigation only)

> All four phases must comply with `.claude/rules/calc-citation-contract.md`. Edition selection must
> emit a `Citation` instance per #2685 once that pilot lands.

- **Phase α (1 PR, low-risk):** Surface explicit `edition: Literal["2017", "2021"] = "2021"` parameter
  on functional package public entry points (`design_cp_system`, `design_marine_cp`, `design_pipeline_cp`,
  `coating_breakdown_factors`, `current_demand`, `anode_mass_requirement`). Default `"2021"` (current).
  No behavior change until edition tables are populated. Update result dataclasses to carry a
  `standard: str` field that emits the literal `"DNV-RP-B401 (2021)"` or `"DNV-RP-B401 (2017)"`.
- **Phase β:** Populate the 2017 vs 2021 lookup tables (coating constants × 9-vs-4 category mapping,
  current densities × climate-vs-temperature axis, anode resistance Dwight-vs-McCoy choice, utilization
  factor defaults, splash zone treatment). Each table dispatched on the `edition` parameter. Cross-test
  every result against both editions to expose silent divergences.
- **Phase γ:** Re-route the router (`infrastructure/base_solvers/hydrodynamics/cathodic_protection.py`)
  to call the functional package internally. The router becomes a thin YAML→Python adapter dispatching
  on `inputs.calculation_type` AND `inputs.edition`. Remove `cp_DNV_RP_B401_2021.py` as a separate
  module — its logic moves into the functional package's edition tables.
- **Phase δ:** Migrate `tests/specialized/cathodic_protection/test_*.py` away from the
  `infrastructure.common.*` deprecation shims. Delete the three shims (`cathodic_protection.py`,
  `cp_DNV_RP_B401_2021.py`, `cp_sacrificial_anode_b401.py`) after caller migration. Fix the YAML
  config to advertise the actual calc types the router dispatches on (or wire `DNV_rp_b401_2011`
  through the edition table now that the parameter exists).

**Estimated scope:** Phase α: ~150 LOC + 20 tests (1 working day). Phase β: ~600 LOC + 40 tests
(3 working days — most of this is reading the two DNV PDFs against the existing implementations to
populate the table constants). Phase γ: ~400 LOC + 30 caller migrations (1 working day). Phase δ:
~100 LOC + 130 test import edits (1 working day). **Total: ~5–7 working days for a single engineer.**

### Why not Option α or γ

- **Option α-functional (designate functional as canonical, deprecate router, lose 2021 edition support):**
  drops the only YAML-config-driven CP surface and forces every user of the router into a non-trivial
  migration. Loses 2021 edition currency for newbuilds. ❌
- **Option α-router (designate router as canonical, deprecate functional, lose 2017 + 4 standards):**
  drops 8 of the 12 standards the functional package implements (ISO 15589-2, API RP 1632, ASTM G42/G80,
  NACE SP0169/SP0176/SP0207/SP0502, NORSOK M-506, EN 50162/15280, ISO 18086, plus corrosion-rate,
  cp_monitoring, cp_survey, stray_current modules). Loses the broader coverage. Loses 2017 edition
  for legacy projects. ❌
- **Option γ (keep both, document split):** does not fix the YAML config's bad advertisement of
  `DNV_rp_b401_2011`, does not fix the deprecation-shim test-import smell, does not give a customer
  auditor a single defensible code surface to point at. The 2017-vs-2021 split is **not** a
  legacy-vs-current divide — both are simultaneously needed for active project work. Splitting them
  by import path doesn't reflect how engineers select editions (which is by contract / BOD, not by
  Python namespace). ❌

---

## 7. Surprises (3 highest-signal findings beyond the R5 starting point)

1. **The "router-based" tests don't actually import the router — they all import the deprecation
   shim.** Every CP test under `tests/specialized/cathodic_protection/` and
   `tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py` reads:
   `from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection`.
   This shim emits `DeprecationWarning` on every test session. Two parallel shims
   (`cp_DNV_RP_B401_2021.py`, `cp_sacrificial_anode_b401.py`) under `infrastructure/common/` exist
   purely to keep the test imports working. **The R5 inventory captured one shim file; there are
   actually three.**

2. **The YAML config file advertises calculation types that the router cannot dispatch.**
   `cathodic_protection.yml:4` lists `calculation_type: ABS_gn_ships_2018 # DNV_rp_b401_2011,
   DNV_rp_b401_2021_05, ABS_gn_ships_2018` — but the router only handles
   `{"ABS_gn_ships_2018", "DNV_RP_F103_2010", "ABS_gn_offshore_2018", "DNV_RP_B401_offshore"}`.
   Neither `DNV_rp_b401_2011` nor `DNV_rp_b401_2021_05` resolves; both raise `ValueError(...not
   IMPLEMENTED)` at runtime. The YAML is **lying about what the router supports**, with the 2011
   value being especially treacherous since it sounds like a legacy-edition fallback but is
   actually a dead key.

3. **The functional package has zero src/ callers outside its own facade — but it carries the
   broader standards coverage.** The package's 100+ public exports across 16 modules (covering
   ISO 15589-2, API RP 1632, NACE SP0169/SP0176/SP0207, ASTM G42/G80, NORSOK M-506, EN 50162/15280,
   ISO 18086, plus modules for corrosion-rate / cp_monitoring / cp_survey / stray_current /
   anode_depletion / iccp_design / cp_reporting / fuel_system_cp / marine_structure_cp / marine_cp /
   pipeline_cp) are **exercised only by tests and by direct Python users importing modules manually**.
   The engine's YAML dispatcher never routes through them. Deleting the functional package would
   silently remove 8 standards from the runtime — but **no production caller would break** because
   nothing depends on it transitively. The functional package is, paradoxically, both the broader
   implementation and the less-wired one.

---

## 8. Test Coverage Implications

A direct deletion of either surface would lose ~200+ tests. Phase β of the recommended plan must
preserve test signal:

- **Functional package tests (206):** Keep all 18 test files. Update them to assert against both
  editions in parametrized form once Phase β lands.
- **Router tests (230, transit shim):** Re-import from `digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection`
  directly. Delete the three `infrastructure/common/cp_*.py` shims after migration. Tests then
  parametrize on `edition` like the functional ones.
- **Cross-edition reference tests:** Add a new test file `tests/cathodic_protection/test_edition_consistency.py`
  asserting:
  - Coating-category mapping is well-defined (functional pkg's 9-cat scheme ↔ router's I/II/III/bare)
  - For an identical input case, 2017 and 2021 results differ on the documented dimensions (§2 table)
    and agree on the unchanged dimensions (items 8, 12, 15)
  - Each result object emits a `standard` field matching the requested edition

This test scaffolding is the durable artifact that prevents edition drift from regressing post-merge.

---

## 9. Open Questions (for the plan-phase issue)

1. **Which is the "default" edition for new code?** Recommend `"2021"` — it's current and most
   newbuild contracts in 2026 specify the latest edition. Legacy projects pass `edition="2017"`
   explicitly. Confirm with engineering management.
2. **Do we keep the 2010 edition path?** YAML config advertises `DNV_rp_b401_2011` but neither
   surface implements it. Recommend dropping `"2010"` from the `Literal` type unless field projects
   actively need it. (R5 audit did not surface a project requirement for 2010-edition CP.)
3. **Where do `ABS_gn_ships_2018` and `ABS_gn_offshore_2018` calc types live in the merged surface?**
   They're ABS, not DNV. Recommend adding `standard: Literal["DNV-RP-B401", "ABS-CP-Ships",
   "ABS-CP-Offshore", "DNV-RP-F103", "ISO-15589-2"]` as the orthogonal selector, with `edition`
   per-standard.
4. **Citation emission rollout:** does this work block on workspace-hub#2685 (mooring pilot fix),
   or proceed independently with placeholder `Citation` instances? The two are decoupled —
   recommend proceeding independently and back-filling once #2685 lands.

---

**End of investigation. Recommendation: Option β (edition-parameterized merge), 4-phase plan, ~5–7
working days. Awaiting issue creation + plan PR.**
