# Mooring Design — Code Coverage Preliminary Inventory (R5)

**Issue:** [#2681](https://github.com/vamseeachanta/workspace-hub/issues/2681) (R5 Code Audit, parent [#2676](https://github.com/vamseeachanta/workspace-hub/issues/2676) — Domain Sweep: Mooring Design)
**Date:** 2026-05-12
**Audit author:** R5 subagent
**Scope:** Preliminary inventory of mooring-related modules in `digitalmodel`, the seed corpus at `llm-wiki/seeds/`, and the citation pilot. Full audit (gaps, severity, standards-cross-check) deferred until R1 (Standards) and R2 (Academic) complete.

> **Status note:** All rows below carry `PRELIMINARY — pending R1/R2 validation`. The standards references column is captured verbatim from module docstrings; R1 will validate that the cited code IDs are current, in-print, and match the published revision frontmatter under `knowledge/wikis/*/standards/`. R2 will validate that referenced textbooks (Faltinsen 1990, etc.) point to defensible editions.

> **Read-only audit:** no implementation changes made. Commit is deferred to the main session per R5 dispatch.

---

## 1. Inventory Table

| Component | Module Path | Standards / References (docstring) | Citation Emission | Tests | Status |
|---|---|---|---|---|---|
| Preliminary mooring design (citation pilot) — catenary, line sizing, spread + turret layout, MBL utilisation, material library (R3/R4/R4S/R5 chain, wire, polyester, HMPE, nylon) | `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` | API RP 2SK; DNV-OS-E301; DNV-OS-E302 Table B1; Faltinsen (1990) ch. 6 | **NONE** — module does not import `digitalmodel.citations.*` despite being named as the pilot in `.claude/rules/calc-citation-contract.md`. Safety factors (1.67 intact, 1.25 damaged) are hard-coded as Pydantic field defaults, not emitted as `CitedValue`. | `digitalmodel/tests/orcaflex/test_mooring_design.py` | PRELIMINARY — pending R1/R2 validation. **DEFECT vs. citation contract** (see §4). |
| Citation schema — `Citation`, `CitedValue`, `CitationResolutionError`, `validate_citation` | `digitalmodel/src/digitalmodel/citations/schema.py` | Contract: `docs/standards/calc-output-citation.md`; #2481 D2/D3 | n/a (it IS the schema) | `digitalmodel/tests/citations/test_schema.py` | PRELIMINARY — fail-closed validator present; direct-file-read v1 path. |
| Citation registry — `get_mooring_safety_factor(condition, *, repo_root)` returning DNV-OS-E301 §2.2.3 factors | `digitalmodel/src/digitalmodel/citations/registry.py` | DNV-OS-E301 (2021-07) §2.2.3 | Emits `CitedValue(value, citation, units)` with wiki-path validation | `digitalmodel/tests/citations/test_registry.py` | PRELIMINARY — getter exists but **has zero callers** in `src/` (see §4 surprise #2). |
| Subsea mooring-system designer (FoS verification, intact/damaged condition analysis) | `digitalmodel/src/digitalmodel/subsea/mooring_analysis/designer.py` | DNV-OS-E301 | NONE | `digitalmodel/tests/subsea/mooring_analysis/test_mooring_analysis_unit.py` | PRELIMINARY — duplicates safety-factor logic vs. citation pilot. |
| Subsea mooring catenary analyser — geometry, tension distribution, horizontal/vertical stiffness | `digitalmodel/src/digitalmodel/subsea/mooring_analysis/catenary.py` | DNV-OS-E301 | NONE | (covered by `test_mooring_analysis_unit.py`) | PRELIMINARY |
| Subsea mooring data models — CALM/SALM/spread/turret enums, line types | `digitalmodel/src/digitalmodel/subsea/mooring_analysis/models.py` | (none in docstring) | n/a (dataclasses) | n/a | PRELIMINARY |
| Subsea mooring OrcaFlex generator | `digitalmodel/src/digitalmodel/subsea/mooring_analysis/orcaflex_generator.py` | (none in docstring) | NONE | n/a | PRELIMINARY |
| Subsea mooring CLI | `digitalmodel/src/digitalmodel/subsea/mooring_analysis/cli.py` | n/a | n/a | `digitalmodel/tests/specialized/cli/test_mooring_analysis_cli.py`; `tests/subsea/mooring_analysis/test_mooring_analysis_cli.py` | PRELIMINARY |
| Marine-engineering catenary BVP solver (active version) | `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver.py` | (textbook catenary; no formal code refs) | NONE | `tests/marine_ops/marine_engineering/test_catenary_solver.py`; `test_mooring_catenary.py`; `legacy/test_mooring_catenary.py` | PRELIMINARY — see §4 surprise #3 (5 parallel solver variants on disk). |
| Marine-engineering catenary solver variants — `_backup`, `_v2`, `_fixed`, `_final` | `marine_engineering/mooring_analysis/catenary_solver_{backup,v2,fixed,final}.py` | n/a | NONE | n/a | PRELIMINARY — **clean-up candidate**. |
| Marine-engineering component database | `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/component_database.py` | (none in docstring) | NONE | `tests/marine_ops/marine_engineering/test_component_database.py` | PRELIMINARY |
| Comprehensive mooring analysis orchestrator (pretension, stiffness, fender forces, group comparisons) | `digitalmodel/src/digitalmodel/solvers/orcaflex/mooring_analysis/comprehensive_analysis/` (13 files, 1,971 LOC) | (none surfaced in module docstrings) | NONE | `tests/solvers/orcaflex/mooring-tension-iteration/`; `tests/solvers/orcaflex/reporting/test_mooring_report.py` | PRELIMINARY |
| OrcaFlex mooring solver wrapper | `digitalmodel/src/digitalmodel/solvers/orcaflex/mooring.py` | n/a (OrcaFlex API wrapper) | NONE | n/a (OrcaFlex licence-gated) | PRELIMINARY |
| Mooring router for modular model generator — studless chain MBL/EA/mass coefficient tables | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/routers/mooring_router.py` | DNV-OS-E302 Table 2-2 (simplified) | NONE — coefficients are inline `dict[ChainGrade, ...]` | `tests/solvers/orcaflex/modular_generator/routers/test_mooring_router.py` | PRELIMINARY — **second duplicate chain-property table** vs. `mooring_design.MOORING_MATERIAL_LIBRARY`. |
| Mooring extractor (OrcaFlex results → report data model) | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/mooring_extractor.py` | n/a | n/a | `tests/solvers/orcaflex/reporting/test_mooring_report.py` | PRELIMINARY |
| Mooring report renderer | `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/mooring.py` | n/a | n/a | (covered above) | PRELIMINARY |
| Anchor holding capacity — drag (Stevpris/Bruce/Vryhof) + suction caisson (skin friction + reverse end bearing) | `digitalmodel/src/digitalmodel/geotechnical/anchors.py` | DNV-RP-E302 Table 3-1; DNV-RP-E303; API RP 2SK | NONE — efficiency factors are inline `dict[str, dict[str, float]]` | `digitalmodel/tests/test_geotechnical_anchors.py`; `tests/geotechnical/test_geotechnical.py` | PRELIMINARY |
| Rigging components — slings (sling data from Excel vendor sheets) | `digitalmodel/src/digitalmodel/specialized/rigging/rigging_components.py` | n/a (vendor data) | n/a | n/a | PRELIMINARY — peripheral, included for completeness. |
| OrcaFlex model builder mooring sections | `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` | (none surfaced) | NONE | `tests/orcaflex/test_model_builder.py` | PRELIMINARY |
| OrcaFlex code-check engine (utilisation checks) | `digitalmodel/src/digitalmodel/orcaflex/code_check_engine.py` | (none surfaced) | NONE | `tests/orcaflex/test_code_check_engine.py` | PRELIMINARY |

**Modules audited:** ~20 distinct mooring-pertinent modules across 6 packages (`orcaflex/`, `subsea/mooring_analysis/`, `marine_ops/marine_engineering/mooring_analysis/`, `solvers/orcaflex/mooring_analysis/comprehensive_analysis/`, `solvers/orcaflex/modular_generator/routers/`, `geotechnical/`), plus the citation infrastructure (`citations/{schema,registry}.py`). The full `grep` returned 200+ files but most are tangential (reporting helpers, visualisation, fixtures). The 20 above are the calc-relevant surface.

**Tests scoped:** at least 11 dedicated mooring/anchor test files (mooring_design, mooring_analysis unit + CLI, mooring_catenary, mooring_router, mooring_report, OCIMF integration, comprehensive analysis fixtures, geotechnical anchors). Hundreds of YAML/CSV fixture artifacts under `tests/solvers/orcaflex/mooring-tension-iteration/fsts-l015-test-cases/` and `tests/solvers/orcaflex/analysis/moorings/pretension/`.

---

## 2. Citation Contract Compliance Check

Per `.claude/rules/calc-citation-contract.md` the "Pilot reference" is `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py`.

**Findings:**

1. **Module declares the pilot status in prose** (docstring + comments) but **does NOT import** `digitalmodel.citations.schema` or `digitalmodel.citations.registry`. `grep -c "Citation\|citations" mooring_design.py` returns **0**.
2. Safety factors 1.67 (intact) and 1.25 (damaged) appear as **Pydantic `Field` defaults** on `MooringLineDesign`, with the docstring `"FoS for intact condition (API RP 2SK)"`. The citation contract requires emission of a `Citation` instance **alongside** the numeric value — that emission is absent. Cross-check: the rule says *"Pilot reference: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` demonstrates citation emission for DNV-OS-E301 mooring safety factors"* — this **prose claim is contradicted by the code**.
3. The registry getter `get_mooring_safety_factor(MooringCondition.INTACT_QUASI_STATIC, repo_root=...)` exists at `citations/registry.py:41` and is correctly wired (validates wiki frontmatter under `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`, returns `CitedValue`). It is **covered by `tests/citations/test_registry.py`**. But `grep -rln "get_mooring_safety_factor\|MooringCondition"` across `src/` returns **only `registry.py` itself** — there are **zero in-tree consumers**.
4. Net: the citation pilot is half-wired — schema + registry getter shipped, but the named pilot module has not been migrated to consume the getter. **This is a blocker for any general roll-out** (you can't ship the contract to other domains while the canonical pilot fails it).

**Recommendation (defer to R6 / main session):** open a follow-up issue to (a) correct the rule prose if the pilot is not yet complete, OR (b) wire `MooringLineDesign.safety_factor_intact` and `safety_factor_damaged` defaults to `get_mooring_safety_factor(...).value` with the citation flowing into a sidecar — whichever the maintainer prefers. Do not silently update the rule.

---

## 3. Knowledge Seed Inventory

**Path:** `/mnt/local-analysis/workspace-hub/llm-wiki/seeds/mooring-failures-lng-terminals.yaml` (1,126 lines, MIT/CC-BY-4.0 licensed corpus per `llm-wiki/CLAUDE.md`).

> **Provenance note:** project memory references "40 entries at `knowledge/seeds/`" — that path does **not** exist on disk. The 40 entries are at the `llm-wiki/seeds/` path above (post-spinout 2026-05-05 per `project_llm_wiki_spunout`). The memory entry needs a path update.

**Entry count:** 40 (`MOORING-*` IDs, confirmed by `grep -E "^\s+- id: MOORING" | wc -l`).

**Subcategories covered:**

| Subcategory | Count (approx.) | Examples |
|---|---|---|
| `terminal-investigation` | 3 | NWS LNG overview, SIGTTO 2015, Aktis forensic |
| `incident` | ~10 | NWS LNG 2014, Zarga Milford Haven 2015, Prelude FLNG 2018, Asterix Busan 2023, Ansac Splendor 2018, Veracruz 2024, Cyclone Narelle, Tomakomai, Summit FSRU Bangladesh, Golar Freeze Elba |
| `technical-paper` | ~4 | van der Molen 2003, Grant & Holboke OTC 16718, channel-refraction ICCE |
| `mitigation` | ~5 | SLAM, ShoreTension, automated mooring (Cavotec/Trelleborg), management software (OPTIMOOR, BerthAlert), shore-tension monitoring |
| `standard` | ~7 | OCIMF MEG4, OCIMF Effective Mooring 4th, SIGTTO Terminal Guidelines 2024, IMO SOLAS II-1/3-8 (2024), DNV-OS-E301, API RP 2SK 4th Ed, BS 6349-4 / ROM 2.0-11 / EAU 2012, PIANC working groups |
| `physics` | 1 | Long-period swell resonance (50 mm waves can part lines) |
| `industry-investigation` | ~3 | HMPE failures 2007–2011 industry wide, BW Fleet seven-line failure, DNV Norwegian shelf 18 failures |
| `research` | ~2 | JIP HAWAIII (Deltares/MARIN), CSIR vessel-motion forecast |
| `investigation` | ~5 | Geraldton, Saldanha Bay, Peru LNG, Ngqura, Port Hedland |

---

## 4. Seed-to-Code Map (Coverage / Gaps)

| Seed cluster | Corresponding code in `digitalmodel` | Gap analysis |
|---|---|---|
| **DNV-OS-E301 safety factors** (`MOORING-dnv-os-e301`) | `citations/registry.py:get_mooring_safety_factor`; `orcaflex/mooring_design.py` defaults; `subsea/mooring_analysis/designer.py`; `solvers/orcaflex/modular_generator/routers/mooring_router.py` | **Partially covered.** Code emits the factors but not via the citation pilot (see §2). |
| **API RP 2SK** (`MOORING-api-rp-2sk`) | `orcaflex/mooring_design.py` (referenced in docstring); `geotechnical/anchors.py` | **Partially covered.** No version-locked citation. The 2024 4th-edition update flagged by the seed is **not** reflected anywhere in the code. |
| **DNV-OS-E302 chain properties** | `solvers/orcaflex/modular_generator/routers/mooring_router.py` (studless chain MBL/EA/mass coefficients); `orcaflex/mooring_design.py` `MOORING_MATERIAL_LIBRARY` | **Covered but duplicated** — two parallel chain-property tables exist with no shared source-of-truth. |
| **DNV-RP-E302 / E303 anchor capacity** | `geotechnical/anchors.py` (drag + suction) | **Covered.** No citation emission. |
| **OCIMF MEG4 / Effective Mooring** (`MOORING-ocimf-meg4`, `MOORING-ocimf-effective-mooring-4th`) | `tests/marine_ops/marine_engineering/integration/test_ocimf_mooring_integration.py` (integration test fixture exists) | **Partially covered.** Integration test present; no production source module explicitly references MEG4 wind/current coefficients. |
| **HMPE / polyester / nylon material behaviour** (`MOORING-hmpe-industry-failures-2007-2011`, `MOORING-prelude-flng-2018`, `MOORING-bw-fleet-spain-seven-lines`) | `orcaflex/mooring_design.SegmentMaterial` enum (HMPE/POLYESTER/NYLON); polyester axial-stiffness entries in library | **GAP.** Code carries simple linear EA. Seeds document creep, jacket-vs-unjacketed Dyneema SK78 behaviour, snap-back risk, infield retirement criteria — **no creep model, no time-dependent stiffness, no failure-probability model** in code. |
| **Long-period swell / second-order drift resonance** (`MOORING-physics-long-period-resonance`, `MOORING-nws-paper-otc-16718`, `MOORING-nws-paper-vandermolen-2003`) | (none in mooring code; QTF / drift forces live in `orcawave/drift_forces.py`, the Hydrodynamics domain — see #2668) | **GAP at domain boundary.** Mooring design has no path to consume drift force / response-spectrum results into line-tension forecasting. Cross-domain coordination needed with R5 of #2668. |
| **Snap-back hazard & rope failure modes** (`MOORING-asterix-busan-2023`, `MOORING-ansac-splendor-longview-2018`, OCIMF Snap-back) | (none) | **GAP.** No snap-back energy calculation, no exclusion-zone tooling. |
| **Shore-tension / monitoring systems** (`MOORING-shore-tension-monitoring`, `MOORING-peru-lng-shoretension`) | (none) | **GAP.** No tension-monitoring data ingestion. Not necessarily a code gap (operational), but worth tagging as scope-out. |
| **Automated mooring systems** (`MOORING-automated-mooring-systems`, `MOORING-ngqura-south-africa`) | (none) | **GAP / scope-out.** |
| **Mooring management software** (`MOORING-management-software` — OPTIMOOR, BerthAlert, MIKE 21) | (none — these are competitor products; coverage means interop, not re-implementation) | **Scope decision needed** — R6/R7. |
| **Cyclone / extreme-event response** (`MOORING-cyclone-narelle-wa-2026`) | (none) | **GAP.** No cyclone-event-driven design check. |
| **Forensic investigation pattern** (`MOORING-aktis-forensic-investigation`) | (none) | **GAP — but consistent with scope.** digitalmodel is design-side, not forensic. |
| **Specific terminal incident reports** (Zarga, Prelude, BW, Asterix, Veracruz, Tomakomai, Geraldton, Saldanha, etc.) | (none) | **Not gaps** — incident knowledge informs lessons learned, not code modules. Could feed a test-case library or validation benchmarks (follow-on opportunity). |

**Seed-to-code coverage summary:**
- **Direct calc coverage:** 4 / 40 seeds (DNV-OS-E301, API RP 2SK, DNV-OS-E302 chain, DNV-RP-E302/E303 anchors) — and even these are partial.
- **Test/integration fixture coverage:** +1 (OCIMF MEG4).
- **Gap clusters (explicit):** HMPE creep/failure modelling, long-period swell drift coupling, snap-back energy, cyclone response.
- **Out-of-scope-by-design:** ~25 seeds describing incidents, forensic work, monitoring tech, automated mooring, regulatory updates — useful for knowledge surface, not for code coverage.

---

## 5. Top 3 Surprises (defect-hunt stance per "always adversarial review" memory)

1. **Citation pilot is a paper tiger.** `.claude/rules/calc-citation-contract.md` cites `orcaflex/mooring_design.py` as the **pilot reference that demonstrates citation emission**. The module does not import `digitalmodel.citations` at all. The registry getter exists, is tested, and has zero callers in `src/`. Any agent that reads the rule and looks at the named module will conclude the contract is unenforced — and they would be correct.
2. **Five catenary-solver variants on disk.** `marine_ops/marine_engineering/mooring_analysis/` ships `catenary_solver.py`, `_backup.py`, `_v2.py`, `_fixed.py`, `_final.py`. The naming pattern is the classic "lost ground truth" smell. Subsea has yet another `catenary.py` (in `subsea/mooring_analysis/`), and `orcaflex/mooring_design.py` carries `solve_catenary()` directly. That is **three independent catenary implementations + four shadow copies of one of them**. R6 should pick a canonical solver and depreciate the rest; today there is no way for a reviewer to know which is authoritative.
3. **Two parallel chain-property libraries.** `orcaflex/mooring_design.MOORING_MATERIAL_LIBRARY` ships 8 discrete chain/wire/polyester entries; `solvers/orcaflex/modular_generator/routers/mooring_router.py` ships a coefficient-based library (`mbl_coeff * d^2`, etc.) keyed on `ChainGrade`. The numeric properties are independently editable. Standards updates (e.g., DNV-OS-E302 revisions, API RP 2SK 2024 4th edition flagged in `MOORING-api-rp-2sk`) would need to land in **both** places, and there is no test enforcing consistency.

---

## 6. Follow-on Pointers (for R6 / main-session triage)

- File issue: "Citation pilot for mooring_design.py is incomplete — registry getter has zero consumers and pilot module bypasses citations." Severity HIGH (blocks domain roll-out).
- File issue: "Catenary solver consolidation — pick canonical, deprecate variants." Severity MEDIUM.
- File issue: "Chain-property tables duplicated across `mooring_design.MOORING_MATERIAL_LIBRARY` and `mooring_router` — unify behind citation pilot." Severity MEDIUM.
- File issue: "HMPE / polyester creep model — gap surfaced by 6 seed incidents (Zarga, BW, Prelude, Asterix, Veracruz, industry HMPE)." Severity MEDIUM. Depends on R2 academic input for creep model selection.
- File issue: "Drift-force / long-period-swell coupling into mooring tension — cross-domain gap with #2668 Offshore Hydrodynamics." Severity MEDIUM.
- Update project memory entry "Mooring knowledge — 40 entries at knowledge/seeds/" to point at `llm-wiki/seeds/mooring-failures-lng-terminals.yaml` (post-spinout path correction).
- Update `.claude/rules/calc-citation-contract.md` "Pilot reference" prose to match reality (either complete the pilot or downgrade the claim).
