# Plan for #486: Implement subsea connectors and jumpers module (API 17R)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/486
> **Review artifacts:** scripts/review/results/2026-04-24-plan-486-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

Workspace-hub `src/digitalmodel/` is a near-empty overlay (only `subsea/pipeline/free_span/`). The actual digitalmodel code lives in the sibling submodule repo at `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/`. **All implementation lands in the submodule repo, not the overlay.**

- Found: `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py:1-1200` — installation-time lift-analysis solver (Ballymore manifold-to-PLET V2). Defines `ConnectorProperties` (L213), `PipeSectionLengths`, `BarePipeProperties`, `BuoyancyModuleProperties`, `ClampProperties`, `CraneConfig`, `RiggingProperties`, `StrakeProperties` dataclasses and `compute_orcaflex_sections`. This is load-bearing prior art; new module must coordinate ownership.
- Found: `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_installation.py:1-346` — higher-level jumper installation workflow (crane tip motion, splash zone, go/no-go). Adjacent to issue #471.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/jumper.py:1-20` — thin reporting renderer.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/*` — spec→modular OrcaFlex generator (see #2455 plan, in-flight). Natural handoff for "OrcaFlex export" AC.
- Found: `digitalmodel/src/digitalmodel/subsea/` — existing namespace with `catenary_riser/`, `mooring_analysis/`, `on_bottom_stability/`, `pipeline/`, `vertical_riser/`, `viv_analysis/`. **No `connectors/` subdir exists** — new module lands here.
- Found: `digitalmodel/src/digitalmodel/subsea/pipeline/` — style template (`api_rp_1111_installation.py`, `buckling_common.py`, `pipeline_pressure_dnv.py`, etc.). Dataclass + function-style, standards-tagged.
- Found: `digitalmodel/src/digitalmodel/fatigue/` — `rainflow.py`, `damage.py`, `hotspot_stress.py`, `multiaxial_fatigue.py`, `crack_growth.py`, `environmental_correction.py`, `fatigue_reporting.py`. Integration target for AC "FATIGUE integration".
- Found: `digitalmodel/src/digitalmodel/field_development/subsea_bridge.py:1-30+` — catalog-style analogue for `jumper_catalog.py`.
- Found: `digitalmodel/src/digitalmodel/data_systems/data_procurement/mooring/database_clients/connector_db_client.py` — **mooring** hawser/chain/shackle connectors; naming collision risk — new module must be explicitly subsea-process scope.
- Gap: No native Python module for (a) jumper bending/curvature analysis, (b) jumper thermal expansion, (c) subsea process connector selection/design, (d) dynamic jumper → fatigue pipeline. Only OrcaFlex-centric installation coverage exists.

### Standards

**CRITICAL FINDING — API 17R IS NOT INGESTABLE.** Full-tree grep (`grep -rn "API 17R\|API-17R\|API_17R\|API RP 17R" data/ docs/ knowledge/`) returns only one hit: the LMI-sourced taxonomy doc itself. Ledger has 801 API entries but zero 17R row. No PDF mirror.

| Standard | Ledger status | Source | Usable? |
|---|---|---|---|
| **API 17R (subsea connectors)** | **NOT ledgered, no PDF** | `data/document-index/standards-transfer-ledger.yaml` (grep empty) | **NO — load-bearing blocker** |
| API RP 17B (flexible pipe) 2nd Ed 1998 & 5th Ed 2014 | Ledgered | standards-transfer-ledger.yaml | YES — flexible jumpers |
| API SPEC 17J (unbonded flexible pipe) 4th Ed 2014 | Ledgered | standards-transfer-ledger.yaml | YES — flexible jumpers |
| API SPEC 17K (bonded flexible pipe) | Ledgered | standards-transfer-ledger.yaml | YES — flexible jumpers |
| API RP 17G (completion/workover riser) 2nd Ed 2006 | Ledgered | standards-transfer-ledger.yaml | Adjacent only |
| DNV-OS-F101 (submarine pipeline systems) | In use | `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure_dnv.py` | YES — rigid jumper pipe body |
| DNV-RP-F105 (free-span) | In use | `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/` | YES — jumper VIV lock-in |
| ASME B31.8 / B31.4 (piping code) | Referenced in `asset_integrity/` | | YES — thermal stress / expansion |
| ISO 13628-15 (subsea connectors — ISO equivalent of 17R) | Not present | | Would need procurement |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/` — full-tree grep for `17R`, `subsea connector`, `hydraulic flying lead`, `jumper.*catalog`: **zero matches**.
- `knowledge/wikis/marine-engineering/wiki/sources/fatigue-life-predictions-for-a-threaded-tlp-connector.md` — TLP tether connector fatigue (NOT subsea process; out of scope).
- `knowledge/wikis/marine-engineering/wiki/sources/chen-w-c-1989-fatigue-life-predictions-for-threaded-tlp-tether-connector.md` — same; out of scope.
- No wiki pages for rigid/flexible/vertical jumpers, collet connectors, clamp hubs, mechanical connectors. Knowledge baseline for API 17R is empty.

### Documents consulted

- `digitalmodel/docs/field-development/subsea-production-systems-mapping.md:26` — authoritative taxonomy linking API 17R → "Connectors & Jumpers" → Issue #486 (Medium, Milestone #1). Confirms sibling issues #484 (17D trees), #485 (17P manifolds), #488 (17E/17F umbilicals).
- `docs/plans/2026-04-23-issue-2455-rigid-jumper-plet-to-plem-semantic-proof.md` — active T3 plan proving existing rigid-jumper OrcaFlex forward pipeline; notes API RP 17B is not in ledger as a "jumper" row. Precedent for T3 scoping on jumper-family work.
- `digitalmodel/docs/domains/installation/jumpers.md`, `digitalmodel/docs/domains/orcaflex/jumper/jumper.md` — installation-centric knowledge notes (vertical-jumper ROV tie-in, collet connectors).
- `digitalmodel/docs/session-exits/jumper-installation-analysis-20260405.md` (+ part2, + complete) — historical session context.
- Related issues (cross-module coupling):
  - #471 — jumper-install pipeline (uses `jumper_lift.py`)
  - #475 — jumper_lift test expansion (touches same `ConnectorProperties` dataclass)
  - #484 — subsea trees (API 17D) — interface stub
  - #485 — manifolds (API 17P) — interface stub
  - #488 — umbilicals (API 17E/17F) — interface stub
  - #2455 — rigid-jumper PLET-to-PLEM semantic proof (in-flight, must not collide)

### Gaps identified

1. **No `src/digitalmodel/subsea/connectors/` directory** in either the overlay or submodule — greenfield confirmed against intel.
2. **No analytical solver** for jumper bending/curvature.
3. **No thermal expansion solver** for subsea jumpers (end-constraint model absent).
4. **No subsea-process connector design module** (preload, seal integrity, hub-face loads).
5. **No dynamic-jumper → fatigue bridge** calling into `fatigue/rainflow.py` + `fatigue/damage.py`.
6. **No jumper catalog registry** for type taxonomy (rigid / flexible / vertical × mechanical / clamped / welded connector).
7. **API 17R standard not ingestable** — ledger, grep, PDF mirror, and wiki all empty. See Standards table and `[TRADEOFF FOR USER]` in Risks.

### Evidence (embedded verification)

**Issue statuses** (from intel doc, pod Explorer verified):
- `#486` — OPEN — "Implement subsea connectors and jumpers module (API 17R)" (this issue)
- `#471` — OPEN — jumper installation pipeline (coupling)
- `#475` — OPEN — jumper_lift test expansion (coupling)
- `#484` — OPEN — subsea trees API 17D (sibling)
- `#485` — OPEN — manifolds API 17P (sibling)
- `#488` — OPEN — umbilicals API 17E/17F (sibling)
- `#2455` — OPEN — rigid-jumper PLET-to-PLEM semantic proof (must not collide)

**File existence** (from Explorer sweep 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py`
- EXISTS: `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_installation.py`
- EXISTS: `digitalmodel/src/digitalmodel/subsea/` (namespace dir with 6 siblings)
- EXISTS: `digitalmodel/src/digitalmodel/fatigue/rainflow.py`, `damage.py`, `hotspot_stress.py`, `multiaxial_fatigue.py`
- EXISTS: `digitalmodel/docs/field-development/subsea-production-systems-mapping.md`
- EXISTS: `digitalmodel/docs/domains/orcaflex/templates/subsea/jumper_hybrid/base/jumper_base.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/templates/subsea/jumper_hybrid/variations/rigid_jumper.yml`
- EXISTS: `digitalmodel/examples/demos/gtm/data/rigid_jumpers.json`, `demo_05_deepwater_rigid_jumper_installation.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/subsea/connectors/__init__.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/jumper_catalog.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/bending_analysis.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/thermal_expansion.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/connector_design.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/fatigue_bridge.py`
- MISSING (new): `digitalmodel/src/digitalmodel/subsea/connectors/orcaflex_export.py`
- MISSING (new): `digitalmodel/tests/subsea/connectors/` (test tree mirror)

**Line excerpt — existing `ConnectorProperties`** (for coordination with #475):
```
# digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py:~213
@dataclass
class ConnectorProperties:
    # installation-specific: lift/crane loads for Ballymore V2
    ...
```

**Gap proofs**:
- `grep -rn "API 17R\|API-17R\|API_17R\|API RP 17R" data/ docs/ knowledge/` → only LMI taxonomy doc; no ledgered PDF.
- `ls digitalmodel/src/digitalmodel/subsea/connectors/ 2>&1` → "No such file or directory" → confirms greenfield.
- `grep -c "17R" data/document-index/standards-transfer-ledger.yaml` → 0.

<!-- Distinct sources consulted: issue body + field-dev mapping doc + standards ledger + 9 repo source files + 6 related issues + wiki tree + prior plan #2455 = well over the minimum 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-24-issue-486-subsea-connectors-jumpers-api17r.md` |
| Implementation (Phase 1) | `digitalmodel/src/digitalmodel/subsea/connectors/__init__.py`, `jumper_catalog.py`, `connector_design.py` |
| Implementation (Phase 2) | `digitalmodel/src/digitalmodel/subsea/connectors/bending_analysis.py`, `thermal_expansion.py` |
| Implementation (Phase 3) | `digitalmodel/src/digitalmodel/subsea/connectors/fatigue_bridge.py`, `orcaflex_export.py` |
| Tests | `digitalmodel/tests/subsea/connectors/test_jumper_catalog.py`, `test_connector_design.py`, `test_bending_analysis.py`, `test_thermal_expansion.py`, `test_fatigue_bridge.py`, `test_orcaflex_export.py` |
| Worked example | `digitalmodel/examples/subsea/connectors/tree_to_manifold_jumper_example.py` |
| Plan review — Claude | `scripts/review/results/2026-04-24-plan-486-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-24-plan-486-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-24-plan-486-gemini.md` |
| Docs updates | `digitalmodel/docs/field-development/subsea-production-systems-mapping.md` (mark #486 in-progress); `digitalmodel/docs/domains/orcaflex/jumper/jumper.md` (link to new module) |
| Wiki updates | `knowledge/wikis/marine-engineering/wiki/concepts/subsea-connectors.md` (new, if Path B selected); `knowledge/wikis/marine-engineering/wiki/concepts/subsea-jumpers.md` (new) |

---

## Deliverable

A `subsea.connectors` module in the `digitalmodel/` submodule (`digitalmodel/src/digitalmodel/subsea/connectors/`) providing native-Python modeling of subsea jumpers (rigid / flexible / vertical) and inline connectors (selection, preload/seal integrity, bending, thermal expansion, fatigue integration, and OrcaFlex export for dynamic jumpers) — with TDD coverage and a tree-to-manifold worked example.

**Two-path conditional delivery — see `[TRADEOFF FOR USER]` in Risks section:**
- **Path A (procure API 17R):** deliverable cites API 17R clauses throughout; issue title/ACs unchanged.
- **Path B (scope pivot to ledgered adjacents):** deliverable cites API 17B / 17J / 17K (flexible), DNV-OS-F101 (rigid pipe body), DNV-RP-F105 (VIV), ASME B31.8 (thermal). Issue title/ACs adjusted from "per API 17R" to explicit standard basis.

---

## Pseudocode

```
# jumper_catalog.py — type registry
class JumperType(Enum): RIGID, FLEXIBLE, VERTICAL, HYBRID
class ConnectorType(Enum): COLLET, CLAMP_HUB, MECHANICAL, WELDED, DOGS_AND_GROOVES, HYDRAULIC_STAB
@dataclass Jumper: type, nominal_od, wall_thickness, length, geometry (M_SHAPE|INVERTED_U|HORIZONTAL_S), material, design_pressure, design_temp_shutin, design_temp_flowing, end_A_connector, end_B_connector, standard_basis
@dataclass Connector: type, hub_od, make_up_torque, preload, seal_type (METAL_TO_METAL|ELASTOMERIC), pressure_rating, temperature_rating, standard_basis
function build_catalog() -> dict[str, Jumper]   # reads YAML/JSON catalog
function resolve_connector(design_conditions) -> Connector

# connector_design.py — selection/verification
function verify_preload(connector, external_hydrostatic, internal_pressure, thermal_axial_load)
    compute hub-face normal stress
    check seal compression window
    check make-up torque residual under combined loads
    return PASS/FAIL + margins

# bending_analysis.py — curvature/stress
function geometry_curvature(geometry, end_A, end_B, sag_offset) -> CurvatureProfile
function pipe_bending_stress(curvature, pipe_EI, pipe_OD) -> StressProfile
function check_against_code(stress_profile, standard_basis)  # DNV-OS-F101 § or API 17B §

# thermal_expansion.py — thermal stress
function axial_thermal_load(pipe_area, E, alpha, delta_T, boundary: FIXED_FIXED|FREE|SPRING)
function check_jumper_accommodation(jumper_geometry, thermal_load, end_flexibility)
    check mid-span stress; check connector-hub axial capacity

# fatigue_bridge.py — dynamic-jumper fatigue
function stress_history_at_hotspot(orcaflex_timeseries, hotspot: HUB_A|HUB_B|ELBOW|MID_SPAN) -> np.array
function compute_damage(stress_history, sn_curve):
    import from digitalmodel.fatigue.rainflow + damage + hotspot_stress
    returns annual damage, years-to-failure

# orcaflex_export.py — dynamic-jumper OrcaFlex emitter
function emit_orcaflex_spec(jumper, connectors) -> dict   # hands off to solvers/orcaflex/modular_generator
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/__init__.py` | module init |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/jumper_catalog.py` | AC: jumper type registry |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/connector_design.py` | AC: connector selection/verification + preload/seal |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/bending_analysis.py` | AC: curvature/stress |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/thermal_expansion.py` | AC: thermal stress |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/fatigue_bridge.py` | AC: FATIGUE integration — imports from `digitalmodel.fatigue` |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/orcaflex_export.py` | AC: OrcaFlex export — hands to modular_generator |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/catalog_data/jumpers.yaml` | reference data for `jumper_catalog.py` |
| Create | `digitalmodel/src/digitalmodel/subsea/connectors/catalog_data/connectors.yaml` | reference data for `connector_design.py` |
| Create | `digitalmodel/tests/subsea/connectors/test_jumper_catalog.py` | TDD |
| Create | `digitalmodel/tests/subsea/connectors/test_connector_design.py` | TDD |
| Create | `digitalmodel/tests/subsea/connectors/test_bending_analysis.py` | TDD |
| Create | `digitalmodel/tests/subsea/connectors/test_thermal_expansion.py` | TDD |
| Create | `digitalmodel/tests/subsea/connectors/test_fatigue_bridge.py` | TDD |
| Create | `digitalmodel/tests/subsea/connectors/test_orcaflex_export.py` | TDD |
| Create | `digitalmodel/examples/subsea/connectors/tree_to_manifold_jumper_example.py` | AC: worked example |
| Modify (Path A only, later) | `data/document-index/standards-transfer-ledger.yaml` | add API 17R entry if user provides PDF |
| Modify (coordination) | `digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py` | re-export `ConnectorProperties` from new module OR explicit namespace note (coordinate with #475) |
| Update | `docs/plans/README.md` | add this plan to index |
| Update | `digitalmodel/docs/field-development/subsea-production-systems-mapping.md` | mark #486 in-progress; add link to new module |
| Update | `digitalmodel/docs/domains/orcaflex/jumper/jumper.md` | link native solver to OrcaFlex domain docs |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/subsea-connectors.md` | new wiki entry (under Path B — ledgered-adjacents basis) |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/subsea-jumpers.md` | new wiki entry |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_jumper_catalog_loads_yaml` | YAML → dataclass round-trip for rigid/flexible/vertical | `jumpers.yaml` | ≥3 entries, all required fields populated |
| `test_jumper_catalog_connector_enum` | mechanical/clamped/welded + collet/clamp-hub/hydraulic-stab enumerated | — | enum has all 6 types |
| `test_connector_design_preload_nominal` | preload verification PASS on nominal tree jumper | 8" ID, 10 ksi, −2°C ambient, 120°C flowing | PASS, positive margins |
| `test_connector_design_preload_fails_on_overpressure` | guard against seal unseat at overpressure | 15 ksi internal vs. 10 ksi rating | FAIL with specific margin |
| `test_bending_analysis_m_shape_curvature` | M-shape geometry produces expected peak curvature | published M-shape 30 m × 5 m | peak κ within ±1% of hand calc |
| `test_bending_analysis_stress_matches_DNV_OS_F101` | rigid-pipe bending stress matches DNV-OS-F101 § reference | API 5L X65, 10" OD, κ from above | σ within ±0.5% of closed-form |
| `test_thermal_expansion_fixed_fixed_axial_load` | fixed-fixed thermal axial load matches ASME B31.8 closed-form | 10" X65, ΔT=100°C, L=30 m | F = A·E·α·ΔT within ±0.1% |
| `test_thermal_expansion_free_end_zero_load` | free-end boundary yields zero axial load | same + free-end | F ≈ 0 |
| `test_thermal_expansion_spring_end_intermediate` | spring-end interpolates between fixed and free | k=10 MN/m | F between bounds |
| `test_fatigue_bridge_rainflow_roundtrip` | stress_history → rainflow → damage passes into `fatigue.damage` | synthetic 1-hr sinusoid | damage matches analytic closed-form |
| `test_fatigue_bridge_hotspot_selection` | HUB_A vs. MID_SPAN selects distinct stress histories | OrcaFlex fixture from `jumper_hybrid` | histories differ, both non-empty |
| `test_orcaflex_export_emits_valid_spec` | emitter output round-trips through `solvers/orcaflex/modular_generator` | nominal flexible jumper | spec validates against existing generator schema |
| `test_orcaflex_export_matches_template` | emitted spec aligns with `jumper_hybrid/base/jumper_base.yml` structure | — | all required top-level keys present |
| `test_worked_example_tree_to_manifold` | full-pipeline worked example produces all AC artifacts | 30 m M-shape, 8" rigid | catalog entry + preload PASS + bending PASS + thermal PASS + damage < 0.1/yr + OrcaFlex spec emitted |
| `test_no_regression_jumper_lift` | existing `jumper_lift.py` tests still pass after `ConnectorProperties` coordination | — | `uv run pytest digitalmodel/tests/marine_ops/installation/test_jumper_lift.py -v` → green |
| `test_no_collision_with_2455` | new module does not write into `jumper_hybrid/` template tree | — | no files under `digitalmodel/docs/domains/orcaflex/templates/subsea/jumper_hybrid/` modified by this plan |

---

## Acceptance Criteria

**Shared across both paths:**
- [ ] All new tests pass: `uv run pytest digitalmodel/tests/subsea/connectors/ -v`
- [ ] No regression: `uv run pytest digitalmodel/` passes (in particular `tests/marine_ops/installation/test_jumper_lift.py`, `tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py`, `tests/solvers/orcaflex/reporting/test_jumper_fixture_*`)
- [ ] Worked example `examples/subsea/connectors/tree_to_manifold_jumper_example.py` runs end-to-end under `uv run`
- [ ] Fatigue integration cited: bridge imports `digitalmodel.fatigue.rainflow`, `damage`, `hotspot_stress`; `test_fatigue_bridge_rainflow_roundtrip` passes
- [ ] OrcaFlex export artifact validates against the existing `solvers/orcaflex/modular_generator` schema
- [ ] `ConnectorProperties` naming coordination with `marine_ops/installation/jumper_lift.py` resolved (either re-export or explicit namespace note) — coordinate with #475
- [ ] `digitalmodel/docs/field-development/subsea-production-systems-mapping.md` updated to mark #486 in-progress and link to new module
- [ ] Review artifacts posted to `scripts/review/results/`

**Path A ONLY (user procures API 17R):**
- [ ] `data/document-index/standards-transfer-ledger.yaml` has a new row for API 17R (title, edition, source path) and the PDF lives under the mirrored standards tree
- [ ] Every module docstring cites specific API 17R clause numbers for its design decisions (catalog taxonomy, preload, seal integrity, connector selection)
- [ ] Test `test_connector_design_preload_nominal` references an API-17R worked example (or equivalent table) as its numerical reference
- [ ] Issue title remains "...per API 17R" — ACs unchanged

**Path B ONLY (scope pivot to ledgered adjacents):**
- [ ] Issue title updated (GitHub, via user) from "Implement subsea connectors and jumpers module (API 17R)" to e.g. "Implement subsea connectors and jumpers module (API 17B/17J + DNV-OS-F101 + ASME B31.8)"
- [ ] Module docstrings cite only ledgered standards (API 17B 5th Ed 2014 for flexible; API 17J 4th Ed 2014 for flexible-pipe design; DNV-OS-F101 for rigid pipe body; DNV-RP-F105 for VIV; ASME B31.8 for thermal)
- [ ] `bending_analysis.py` numerical-reference test cites DNV-OS-F101 closed-form
- [ ] `thermal_expansion.py` numerical-reference test cites ASME B31.8 closed-form
- [ ] Module README explicitly states "API 17R was not ingestable at implementation time — this module uses ledgered adjacents as standard basis. Revisit if API 17R is later procured."
- [ ] Wiki entries `knowledge/wikis/marine-engineering/wiki/concepts/subsea-connectors.md` and `subsea-jumpers.md` created citing the ledgered adjacents
- [ ] New GitHub issue opened to track "procure API 17R and revisit #486 citations" as a follow-up

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | _to be filled_ |
| Codex | APPROVE / MINOR / MAJOR | _to be filled_ |
| Gemini | APPROVE / MINOR / MAJOR | _to be filled_ |

**Overall result:** PASS / FAIL (re-draft required) — _to be filled_

Revisions made based on review:
- _(list any changes made to the plan after adversarial review)_

---

## Risks and Open Questions

### [TRADEOFF FOR USER] — PROJECT-LEVEL GATE (must be resolved before implementation starts)

**API 17R is not on the standards ledger and there is no PDF mirror. A module claiming "per API 17R" cannot cite clause numbers.** This is a hard gate, not a design choice. User must pick one of two paths; the plan is written so either path can proceed without re-planning.

- **(A) Procure API 17R access.** Work blocks until user provides the standard (PDF deposited into `/mnt/ace/0000 O&G/0000 Codes & Standards/`, row added to `data/document-index/standards-transfer-ledger.yaml`). Plan then proceeds with API-17R-grounded design decisions; issue title and ACs remain as written. Pro: authoritative, matches original issue intent. Con: gated on external procurement; timeline uncertain.
- **(B) Scope pivot to ledgered adjacents.** Use **API 17B (2nd/5th Ed, ledgered)** + **API 17J (4th Ed, ledgered)** + **API 17K (ledgered)** for flexible jumpers; **DNV-OS-F101** for rigid jumper pipe body; **DNV-RP-F105** for VIV/lock-in checks; **ASME B31.8** for thermal. Plan proceeds immediately; issue title and ACs must be amended. Pro: unblocks now, all standards in ledger, numerically traceable. Con: does not cover subsea-connector-specific design clauses (preload / seal integrity / hub-face loads) that live in 17R proper — those will reference best-available general piping + vendor data only.

**Neither the Planner nor downstream implementers may self-select this path.** User decides during plan-approval.

### [TRADEOFF FOR USER] — Connector-type scope ordering

AC lists "mechanical, clamped, welded". Subsea reality is broader (collet, clamp hub, dogs-and-grooves, hydraulic stab; metal-to-metal vs. elastomeric seals). Which to include in the Phase 1 catalog?

- **(A) Minimal (3 types):** strictly the AC — mechanical, clamped, welded. Fastest Phase 1, smallest fixture burden.
- **(B) Canonical (6 types):** add collet, clamp hub, hydraulic stab. Matches real-world catalogs; larger fixture burden; better long-term fit.
- **(C) Extensible enum + minimal data:** enum includes all 6 but data-sheet only populated for the AC's 3. Deferred completion.

Recommend (C) unless user has specific field-development target that needs a non-AC connector type on day one.

### [TRADEOFF FOR USER] — Jumper-type scope ordering

AC lists "rigid, flexible, vertical". All three need distinct bending / thermal / catalog treatments.

- **(A) All three in Phase 1:** highest scope, matches AC exactly, largest review surface.
- **(B) Rigid first (Phase 1), flexible + vertical in Phase 2:** rigid has the most in-repo prior art (`subsea/pipeline/`, `jumper_lift.py`, `jumper_hybrid` OrcaFlex template, #2455 plan). Fastest to numerically validate.
- **(C) Phase by analysis not by jumper-type:** catalog + connector_design first (all three types, data-only), then bending, then thermal, then fatigue, then OrcaFlex export.

Recommend (C). It matches the Phase 1/2/3 breakdown in this plan and minimizes coupling risk.

### [TRADEOFF FOR USER] — OrcaFlex integration scope

AC says "OrcaFlex export for dynamic jumpers". #2455 (rigid-jumper PLET-to-PLEM semantic proof) is active and owns the `jumper_hybrid` template tree + `solvers/orcaflex/modular_generator/` surface.

- **(A) Full export in this issue:** emit complete OrcaFlex spec from `orcaflex_export.py` that round-trips through `modular_generator`. Couples to #2455; risk of merge conflicts.
- **(B) Thin export here, deep integration in follow-up issue:** emit the spec contract only; deep integration and semantic proof land as separate issue once #2455 settles. Safer.
- **(C) Defer entirely:** mark AC as "deferred to follow-up issue"; Phase 3 becomes documentation + stub only.

Recommend (B). Phase 3 in this plan delivers the spec emitter; a separate follow-up issue handles deep integration post-#2455.

### Other risks (non-tradeoff)

- **Risk — `ConnectorProperties` naming collision with `marine_ops/installation/jumper_lift.py`.** `jumper_lift.py:~213` already defines `ConnectorProperties` (installation-specific). #475 is expanding tests against that definition. Mitigation: new module defines `subsea.connectors.connector_design.Connector` (distinct class). If unification is desired later, re-export in a coordinated PR with #475 — not in this issue.
- **Risk — Naming collision with `data_systems/.../mooring/database_clients/connector_db_client.py`.** That file serves mooring hawser/chain connectors — completely different domain. Mitigation: module README states subsea-process scope explicitly.
- **Risk — #2455 rigid-jumper OrcaFlex work in-flight.** Must not touch `jumper_hybrid/` templates or `solvers/orcaflex/modular_generator/` tree. Mitigation: test `test_no_collision_with_2455`; orcaflex_export.py imports generator as a public API only, never edits it.
- **Risk — Cross-repo placement.** Workspace-hub `src/digitalmodel/` is a near-empty overlay; real submission is in the `digitalmodel/` submodule repo. Mitigation: all file paths in this plan are prefixed `digitalmodel/src/digitalmodel/...` to make the repo explicit. Reviewer gate: confirm every `Create` row in Files-to-Change is against submodule, not overlay.
- **Risk — T3 scope creep.** Full implementation (catalog + connector_design + bending + thermal + fatigue + OrcaFlex export + worked example + tests) is large for a single PR. Mitigation: explicit Phase 1/2/3 breakdown in Artifact Map; phases may be landed as separate PRs under the same issue.
- **Risk — Fatigue integration API not yet specified.** `fatigue/hotspot_stress.py` API is internal. Mitigation: Phase 3 opens with a brief API-design note appended to this plan as an amendment (or referenced from `fatigue_bridge.py` docstring); no behavior change to `fatigue/` module itself.
- **Open question:** Should the worked example use the existing `examples/demos/gtm/data/rigid_jumpers.json` fixture or a new Ballymore-derived fixture? Recommend reusing `rigid_jumpers.json` (demo_05 already validates it) to reduce fixture-drift risk.
- **Open question:** Interface stubs for #484 (17D trees) / #485 (17P manifolds) / #488 (17E/17F umbilicals) — add Protocol/ABC stubs now or defer? Recommend defer — add only a docstring note listing expected coupling points; stubs without a consumer risk Protocol churn.

---

## Complexity: T3

**T3** — justification:
- Net-new module (no prior `subsea/connectors/`) with 7 new source files per AC (catalog, connector_design, bending, thermal, fatigue bridge, OrcaFlex export, plus `__init__`)
- **Missing standard reference (API 17R) is a project-level gate** requiring user decision between procurement and scope pivot — neither is a minor call
- Multi-module coupling: `marine_ops/installation/` (existing jumper code, active in #475), `fatigue/` (integration target), `solvers/orcaflex/modular_generator/` (active in #2455), cross-issues #471 / #475 / #484 / #485 / #488 / #2455
- Engineering content density: bending stress, thermal expansion, seal/preload analysis, fatigue hotspot mapping each need standards-grounded algorithms with reference-value tests
- Test burden: 16 tests listed in TDD table including numerical-reference tests against DNV-OS-F101 and ASME B31.8 closed-forms, plus a full worked-example end-to-end test
- Cross-repo placement risk (overlay vs. submodule) and naming-collision risk (`ConnectorProperties` × `jumper_lift.py`, `connector_db_client.py` × mooring) — both need active management

A pure data-catalog slice (just `jumper_catalog.py` + one connector type enum, Path B minimum-scope) would still be T2; the AC explicitly asks for analysis modules + fatigue + OrcaFlex export, which keeps the full-scope plan firmly in T3.
