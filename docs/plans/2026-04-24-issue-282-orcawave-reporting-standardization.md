# Plan for #282: WRK-130 Standardize OrcaWave Analysis Reporting per Structure Type

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/282
> **Review artifacts:** scripts/review/results/2026-04-24-plan-282-claude.md | scripts/review/results/2026-04-24-plan-282-codex.md | scripts/review/results/2026-04-24-plan-282-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders_header.py:32` — `HULL_TYPE_NOTES` dict already keys 8 hull types (barge, fpso, tanker, semi_pontoon, spar, lngc, cylinder, sphere) with per-section notes (stability, natural_periods, coefficients, roll_damping, excitation); `_get_hull_type_note()` retrieves section notes.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_data_models.py:157` — `DiffractionReportData.hull_type: Optional[str]` field exists; Pydantic model covers RAOs, mesh, hydrostatics, roll damping.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py` (420 LOC, orchestration shim) — post WRK-591/WRK-593 split; composes headers, responses, hydrostatics builders into single HTML.
- Found: `report_builders_hydrostatics.py`, `report_builders_responses.py` — already pull per-section hull notes for stability, natural_periods, coefficients; RAO/infinite added mass/load RAO/roll damping sections render.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/catalog.py` (14.3 KB) + `profile_schema.py` (`HullProfile`) + `rao_database.py` — WRK-115 catalog primitives exist but NOT imported by any `diffraction/report_*` module.
- Found: benchmark plotters (`benchmark_plotter.py`, `benchmark_dof_sections.py`, `benchmark_dof_tables.py`, `benchmark_mesh_schematic.py`, `benchmark_correlation.py`) — r4 barge layout distributed across these modules, not a single template.
- Gap: No per-hull-type template dispatch layer — same section set/ordering runs for every hull; spec implies hull-specific sections (VIM for spar, sloshing for LNGC, column interference for semi-sub).
- Gap: No taxonomy aliasing — spec uses `ship`/`semi-sub`; `HULL_TYPE_NOTES` uses `tanker`/`semi_pontoon`.
- Gap: `hull_library.catalog` not wired into report generator; no lookup contract (by hull_type? by profile_id? by variation?).
- Gap: r4 layout decisions (per-DOF 2-col grid, vertical legends, significance filter) not extracted to config — embedded in benchmark plotter code.

### Standards
Not applicable — this issue is a reporting framework refactor, not a standards implementation. No DNV/API/ISO standards are consumed or produced.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/concepts/` — not consulted in this pass (intel provided by pod explorer covers domain context); reserved for implementation phase to verify hull-type terminology (ship vs tanker, semi-sub vs semi_pontoon).

### Documents consulted
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — OrcaWave/OrcaFlex umbrella; provides r4 barge report context.
- `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — multi-body benchmark; relevant for future LNGC side-by-side reporting.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` — L03 ship roundtrip fixture; informs `ship` hull-type taxonomy.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — batch context; defines pod-level concerns.
- `digitalmodel/docs/domains/orcawave/L02_barge_benchmark/` — canonical r4 artifacts (`spec.yml`, `revision.json` describing `r4_per_dof_report`, `benchmark_results/*.html`).
- Related issue #279 — parallel OrcaFlex reporting pod (scope boundary: shared primitives flagged only).
- Related issue #2458 (multi-body benchmark fixture) — informs LNGC+barge side-by-side template dispatch.
- Issue body (this issue #282) — acceptance criteria list 9 items; scope list 9 items; reuse table names 6 existing assets.

### Gaps identified
1. **No per-hull-type template dispatch** — current `report_generator.py` runs one section set for all hulls; spec requires hull-specific section ordering and optional sections (VIM/sloshing/column interference).
2. **Hull-type taxonomy mismatch** — spec uses `ship`/`semi-sub`; code uses `tanker`/`semi_pontoon`; no alias layer.
3. **WRK-115 catalog lookup unwired** — `hull_library.catalog.HullProfile` not imported by any diffraction report module; no contract for auto-populating hull metadata.
4. **r4 layout implicit** — no single config/template file; layout decisions distributed across benchmark_* modules.
5. **Roll-damping peak-period annotation not verified** — `_build_roll_damping_html` exists but peak-period marker presence not confirmed by intel.
6. **Per-hull golden-file strategy undefined** — 6 hull templates means 6 HTML snapshots; CI drift risk not addressed.

### Evidence (embedded verification)

**Issue status** (verified 2026-04-24 via `/tmp/orca-batch-2026-04-24/issue-282.json`):
- `#282` — OPEN — "WRK-130: Standardize analysis reporting for each OrcaWave structure type" (labels: enhancement, cat:engineering, priority:high, wrk-item)

**File existence** (`ls -la` 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders_header.py` (15013 bytes)
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_data_models.py` (5982 bytes)
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/catalog.py` (14352 bytes)
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/__init__.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/hull_taxonomy.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/template_registry.py`

**Line excerpts** (`sed -n 32,40p report_builders_header.py`):
```
HULL_TYPE_NOTES: Dict[str, Dict[str, str]] = {
    "barge": {
        "stability": "Wide beam typically gives large GM_T. ...",
        "natural_periods": "Roll T_n typically 6-15s. ...",
        "coefficients": "Negligible surge-pitch and sway-roll coupling ...",
        "roll_damping": "Radiation-only roll damping typically 0.5-2% critical. ...",
        "excitation": "Broad frequency excitation expected. ...",
    },
```

**Gap proofs**:
- `grep -l "from digitalmodel.hydrodynamics.hull_library" digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` → no matches (catalog not wired into diffraction reports).
- `HULL_TYPE_NOTES` lacks keys `ship` and `semi-sub` → taxonomy gap confirmed.

<!-- Source count: 8 distinct sources (issue body, intel file, 4 prior plans, 2 related issues, 1 domain artifact dir, multiple file paths verified). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-282-orcawave-reporting-standardization.md |
| Tests — taxonomy | `digitalmodel/tests/hydrodynamics/diffraction/test_hull_taxonomy.py` |
| Tests — template registry | `digitalmodel/tests/hydrodynamics/diffraction/test_template_registry.py` |
| Tests — hull library lookup | `digitalmodel/tests/hydrodynamics/diffraction/test_hull_library_lookup.py` |
| Tests — per-hull rendering | `digitalmodel/tests/hydrodynamics/diffraction/test_per_hull_report_rendering.py` |
| Implementation — taxonomy | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/hull_taxonomy.py` |
| Implementation — registry | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/template_registry.py` |
| Implementation — hull-specific strategies | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/{barge,ship,spar,semi_sub,fpso,lngc}.py` |
| Implementation — catalog adapter | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/hull_library_adapter.py` |
| Modified — report_generator | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py` |
| Modified — report_builders_header | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders_header.py` |
| Example reports | `digitalmodel/docs/domains/orcawave/standardized_examples/{barge,ship}/report.html` |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-282-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-282-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-282-gemini.md |
| Docs updates | docs/plans/README.md (add this plan to index) |

---

## Deliverable

A `report_templates` subpackage in `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` that dispatches one of six hull-type-specific report templates (barge, ship, spar, semi_sub, fpso, lngc) against the existing WRK-591/WRK-593 builder pipeline, with a canonical taxonomy-aliasing layer and an optional `hull_library.catalog` adapter for auto-populating hull metadata — reusing all existing builders, models, and plotters unchanged where possible.

---

## Pseudocode

### hull_taxonomy.py — canonical hull-type name resolution
```
CANONICAL_HULL_TYPES = {barge, ship, spar, semi_sub, fpso, lngc}
ALIAS_MAP = {
    "tanker" -> "ship",           # back-compat with existing HULL_TYPE_NOTES
    "semi_pontoon" -> "semi_sub", # back-compat alias
    "ship" -> "ship",
    "semi-sub" -> "semi_sub",
    ...
}
function resolve_hull_type(raw_name):
    normalized = lowercase(strip(raw_name))
    if normalized in ALIAS_MAP: return ALIAS_MAP[normalized]
    if normalized in CANONICAL_HULL_TYPES: return normalized
    raise UnknownHullTypeError(raw_name, suggestions=fuzzy_match(normalized))
```

### template_registry.py — dispatch to hull-specific template strategy
```
TEMPLATE_STRATEGIES: Dict[canonical_hull_type, TemplateStrategy] = {...}

class TemplateStrategy(Protocol):
    section_order: List[section_id]       # e.g. [header, mesh, hydrostatics, raos, ...]
    optional_sections: Set[section_id]    # e.g. spar -> {vim_note}, lngc -> {sloshing_note}
    def render_hull_specific_notes(data) -> List[html_fragment]

function dispatch(hull_type, report_data):
    canonical = resolve_hull_type(hull_type)
    strategy = TEMPLATE_STRATEGIES[canonical]
    ordered_sections = strategy.section_order
    for section_id in ordered_sections:
        call existing builder (builders_header / builders_hydrostatics / builders_responses)
        if section_id in strategy.optional_sections and data has that section:
            render hull-specific fragment (e.g. spar_vim_note, lngc_sloshing_note)
    assemble_html(sections)
```

### hull_library_adapter.py — optional catalog metadata injection
```
function enrich_report_data_from_catalog(report_data, hull_profile_id=None):
    if hull_profile_id is None and report_data.hull_type is None:
        return report_data                # no-op: no catalog lookup
    if hull_profile_id:
        profile = hull_library.catalog.get_profile(hull_profile_id)
    else:
        profile = hull_library.catalog.find_by_hull_type(report_data.hull_type)  # may be None
    if profile is not None:
        merge profile.metadata -> report_data.catalog_metadata (new optional field)
    return report_data
```

### report_generator.py — integration point (single-site change)
```
# existing: build_html(report_data) -> str
# modified:
function build_html(report_data, hull_profile_id=None):
    report_data = hull_library_adapter.enrich(report_data, hull_profile_id)
    return template_registry.dispatch(report_data.hull_type or "barge", report_data)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/__init__.py` | subpackage init; exports dispatch + resolve_hull_type |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/hull_taxonomy.py` | canonical name + alias resolution |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/template_registry.py` | strategy registry + dispatch function |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/barge.py` | barge section order; no optional sections |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/ship.py` | ship-like coupling note; 360-deg heading emphasis |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/spar.py` | VIM note (optional); deep-draft excitation note |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/semi_sub.py` | column-interference note; high-Tn heave emphasis |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/fpso.py` | turret mooring yaw note; bilge-keel emphasis |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_templates/strategies/lngc.py` | sloshing note (optional); side-by-side preamble hook |
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/hull_library_adapter.py` | catalog lookup contract; no-op when profile_id absent |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/test_hull_taxonomy.py` | TDD for alias resolution + error cases |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/test_template_registry.py` | TDD for dispatch + section ordering per hull |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/test_hull_library_lookup.py` | TDD for adapter no-op + profile merge |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/test_per_hull_report_rendering.py` | integration: dict-input -> HTML per hull type |
| Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py` | wire adapter + dispatch; preserve legacy entry point |
| Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders_header.py` | add deprecation-compat shim on `HULL_TYPE_NOTES` keys via alias lookup (no hard rename) |
| Create | `digitalmodel/docs/domains/orcawave/standardized_examples/barge/report.html` | example output from existing L02_barge fixture |
| Create | `digitalmodel/docs/domains/orcawave/standardized_examples/ship/report.html` | example output from existing L03_ship fixture |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_resolve_canonical_passthrough | canonical names pass through unchanged | "barge" | "barge" |
| test_resolve_tanker_alias | `tanker` -> `ship` back-compat | "tanker" | "ship" |
| test_resolve_semi_pontoon_alias | `semi_pontoon` -> `semi_sub` back-compat | "semi_pontoon" | "semi_sub" |
| test_resolve_semi_sub_hyphen | hyphenated `semi-sub` normalizes | "semi-sub" | "semi_sub" |
| test_resolve_case_insensitive | uppercase input accepted | "BARGE" | "barge" |
| test_resolve_unknown_raises | unknown name raises with suggestions | "catamaran" | UnknownHullTypeError |
| test_registry_has_all_six | all 6 canonical strategies registered | — | {barge, ship, spar, semi_sub, fpso, lngc} present |
| test_dispatch_barge_section_order | barge template excludes VIM/sloshing | barge report_data | sections = [header, mesh, hydrostatics, raos, roll_damping] |
| test_dispatch_spar_includes_vim_note | spar optional VIM note rendered | spar report_data | HTML contains "VIM not captured" fragment |
| test_dispatch_lngc_includes_sloshing | LNGC optional sloshing note rendered | lngc report_data | HTML contains "sloshing" fragment |
| test_dispatch_uses_alias | `tanker` input dispatches ship strategy | tanker report_data | ship strategy invoked |
| test_adapter_noop_without_profile_id | adapter passes through when no profile | report_data, None | report_data unchanged |
| test_adapter_merges_profile_metadata | valid profile enriches data | report_data, profile_id=X | catalog_metadata populated |
| test_adapter_missing_profile_logs_warning | missing profile doesn't crash | report_data, profile_id=nonexistent | report_data unchanged + warning |
| test_render_barge_from_l02_fixture | end-to-end HTML from existing barge fixture | L02_barge data dict | valid HTML, r4 layout, includes hydrostatics + roll damping |
| test_render_ship_from_l03_fixture | end-to-end HTML from existing ship fixture | L03_ship data dict | valid HTML, ship strategy sections present |
| test_render_unlicensed_env | dict-input path works without OrcFxAPI | report_data dict | HTML generated (no OrcFxAPI import) |
| test_roll_damping_peak_period_annotation | peak-period marker rendered in roll damping | report_data with peak_roll_period | HTML contains annotation at that period |
| test_legacy_entry_point_preserved | old `build_html(data)` signature still works | pre-existing call sites | same HTML structure |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/hydrodynamics/diffraction/ -v`
- [ ] No regression: `uv run pytest digitalmodel/tests/hydrodynamics/` passes
- [ ] Hull-type taxonomy resolves all 6 spec names + 2 back-compat aliases (`tanker`, `semi_pontoon`) without breaking existing call sites
- [ ] Template dispatch produces distinct section ordering for at least 3 hull types (barge vs spar vs lngc)
- [ ] Hull library adapter is no-op when `hull_profile_id` is None (unblocks dispatch independent of WRK-115 completion)
- [ ] At least 2 example reports generated and checked into `digitalmodel/docs/domains/orcawave/standardized_examples/` (barge from L02 fixture, ship from L03 fixture)
- [ ] Roll-damping peak-period annotation verified rendered in at least one hull template
- [ ] Unlicensed-env path validated: `build_report_data_from_solver_results` dict input works without `OrcFxAPI` import
- [ ] `HULL_TYPE_NOTES` keys unchanged — compat shim routes alias lookups via `hull_taxonomy.resolve_hull_type()`
- [ ] Docs updated: `docs/plans/README.md` indexes this plan
- [ ] Review artifacts posted to `scripts/review/results/2026-04-24-plan-282-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | _pending_ | _pending_ |
| Codex | _pending_ | _pending_ |
| Gemini | _pending_ | _pending_ |

**Overall result:** _pending_

Revisions made based on review:
- _none yet — awaiting Step 4_

---

## Risks and Open Questions

- **Risk:** Scope creep into #279 (OrcaFlex reporting pod). Shared primitives (Plotly layouts, DOF labels, HTML skeleton) exist in `report_builders_header.py` and plotters. Mitigation: flag shared layer but do NOT refactor under #282; scope stays OrcaWave-only.
- **Risk:** Refactor vs additive drift. Existing pipeline is modular and post-WRK-591/WRK-593 split. Mitigation: strategy-dispatch layer reuses existing builders; no rewrites.
- **Risk:** HULL_TYPE_NOTES taxonomy leakage. Renaming keys (`semi_pontoon` -> `semi_sub`) may break fixtures and `hull_library` lookups. Mitigation: compat shim via alias map; old keys preserved indefinitely with deprecation log.
- **Risk:** Unlicensed-env compat. `extract_report_data_from_owr` is gated on `OrcFxAPI`. Per-hull templates MUST remain generatable from `build_report_data_from_solver_results` (dict input) so CI works without OrcaFlex license. Mitigation: integration test `test_render_unlicensed_env` enforces this.
- **Risk:** Per-hull golden files. 6 hull templates means up to 6 HTML snapshot fixtures; CI time + drift risk. Mitigation: snapshot data-model diffs (Pydantic) rather than full HTML byte-compare; only 2 full HTML examples (barge/ship) as human-readable artifacts.
- **Risk:** Roll-damping peak-period annotation presence is unverified by intel. Mitigation: explicit TDD test `test_roll_damping_peak_period_annotation` catches any missing rendering; add annotation logic if gap confirmed during Red phase.
- **Risk:** Benchmark output duplication. Current pipeline emits 5 HTML files per benchmark (report, amplitude, phase, combined, heatmap). Mitigation: this plan treats them as suite outputs; standardized dispatch produces the per-DOF `benchmark_report.html` only. Auxiliary plots remain on existing path.

### `[TRADEOFF FOR USER]` — Template-dispatch mechanism

Three viable designs. Adversarial reviewers will likely challenge the chosen one — please pick before Step 4:

1. **Registry (dict of callables)** — `TEMPLATE_STRATEGIES: Dict[str, Callable]`. Simplest, fewest files, easy to extend. Weak typing; no per-strategy state. _Recommended for T3 velocity._
2. **Strategy pattern (Protocol + classes)** — `TemplateStrategy(Protocol)` with per-hull classes. Strongest typing, explicit section-order declarations, easiest to test in isolation. Slightly more boilerplate (6 small classes). _Recommended if type safety prioritized._
3. **match-case (PEP 634)** — single `dispatch(hull_type)` function with `match` on canonical name. Most concise. Hardest to extend (adding a hull requires editing the dispatcher); couples all hulls into one file. _Not recommended._

Default choice absent user input: **Strategy pattern (option 2)** — pairs cleanly with Protocol typing already used in `report_data_models.py` and gives reviewers explicit `section_order` lists to critique.

### `[TRADEOFF FOR USER]` — WRK-115 coupling policy

Two options for hull_library catalog integration:

1. **Block on WRK-115 completion** — do not merge #282 until `hull_library.catalog` exposes a stable `find_by_hull_type(name) -> HullProfile` contract. Pro: single coherent release; con: blocks this issue indefinitely, no catalog lookup work may be scheduled yet.
2. **Proceed with stub adapter** — `hull_library_adapter.enrich()` is no-op when `hull_profile_id` is None and falls back to no-op on ImportError or missing profile. Later WRK-115 work lights up the code path without re-architecting. Pro: unblocks #282 independently; con: adapter is dead code until catalog ships.

Default choice absent user input: **Option 2 (proceed with stub)** — aligns with batch-wide "describe the DELTA" pattern; adapter is cheap; removes cross-issue blocking.

### Open questions

- **Open:** Should `ship` canonical key replace `tanker` in `HULL_TYPE_NOTES`, or should we add `ship` as a new key with identical content and keep `tanker` as alias? (Plan assumes add + alias, no rename.)
- **Open:** Should standardized dispatch produce a single `benchmark_report.html` or preserve the 5-file suite? (Plan assumes single canonical report; auxiliary plots unchanged.)
- **Open:** Hull-library lookup key — `hull_type` (e.g. "barge") or `hull_profile_id` (e.g. "L02_OC4_semi_sub")? (Plan supports both; profile_id preferred when available.)

---

## Complexity: T3

**T3** — Multi-module change: new `report_templates/` subpackage (9 files), new `hull_library_adapter.py`, 4 new test modules, modifications to `report_generator.py` and `report_builders_header.py`, 6 hull-type strategy integrations, taxonomy alias layer, and WRK-115 coupling contract. Not T4 because the heavy lifting (Pydantic models, section builders, `HULL_TYPE_NOTES` content, plotters) already exists — this is wiring + abstraction + taxonomy cleanup, not greenfield.
