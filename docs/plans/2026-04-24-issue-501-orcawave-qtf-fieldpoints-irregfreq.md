# Plan for #501: OrcaWave — expand QTF config + field points + irregular frequency method

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/501
> **Review artifacts:** scripts/review/results/2026-04-24-plan-501-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:446-495` — `SolverOptions` currently defines `remove_irregular_frequencies: bool`, `qtf_calculation: bool`, and optional `qtf_min_frequency` / `qtf_max_frequency`. No QTF crossing-angle, load-calc-method, or irregular-frequency-method fields.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:591-615` — `ControlSurfaceSpec` already exists (mesh-file driven) and is exposed via `BodySpec.control_surface` (L644-647). The plumbing for a `control_surface` irregular-frequency method is **90% wired**; only the selector is missing.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:498-516` — `OutputSpec` has `detect_field_points_inside_bodies` but no `field_points` collection.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:254-269` — interior-surface-panel emission with `BodyInteriorSurfacePanelMethod="Triangulation method"` hardcoded; `control_surface` branch (L261-269) fires only when `body.control_surface` is populated, never as a selectable irregular-freq strategy.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:507-532` — `_build_headings_section` hardcodes `QTFMinCrossingAngle=0`, `QTFMaxCrossingAngle=180`.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:544-555` — `_build_outputs_section` emits only `DetectAndSkipFieldPointsInsideBodies`; no `FieldPointX, FieldPointY, FieldPointZ` path.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:572-600` — `_build_qtf_section` hardcodes `QTFCalculationMethod="Both"` and `PreferredQTFCalculationMethod="Direct method"`.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py:391-393` — documents OrcaWave's combined-key convention `"FieldPointX, FieldPointY, FieldPointZ"` for field-point emission.
- Gap: no `QTFOptions`, `FieldPointSpec`, or `IrregularFrequencyMethod` types exist in the schema.
- Gap: no test coverage for QTF options, field-points, or the three-way irregular-frequency-method selector.

### Standards

| Standard | Status | Source |
|---|---|---|
| QTF / quadratic-transfer-function conventions | not in ledger | `data/document-index/standards-transfer-ledger.yaml` — no hits for "QTF", "quadratic transfer function", "WAMIT", or "irregular frequency" |
| DNV-RP-C205 (second-order wave loads) | not promoted | cited by domain name only; no ledger entry |
| WAMIT User Manual (fdf mesh, irregular-freq methods) | not promoted | canonical vocabulary source for OrcaWave |
| OrcaWave User Manual (QTFCalculationMethod, BodyInteriorSurfacePanelMethod, FieldPointX/Y/Z) | not promoted | canonical emission vocabulary |

No standards-compliance gate is triggered by #501.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/` — checked; no pages on QTF, quadratic transfer function, irregular frequency, or second-order wave loads.
- `knowledge/wikis/naval-architecture/wiki/` — checked; only `entities/orcaflex-viv-analysis.md` is adjacent, and it is about VIV, not diffraction.
- Result: **no wiki page authoritatively covers the three #501 features.** This is a knowledge gap; optional follow-up only — do not block the schema plan on wiki authoring.

### Documents consulted

- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — names `DiffractionSpec` + `OrcaWaveBackend` as the scaling lever; Wave 2 Phase 2A depends on schema-level backward compat. #501 is a strict extension, no conflict.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` — anchors the byte-identity test target: L03 spec.yml must continue to produce byte-identical OrcaWave YAML after the schema extension.
- `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — confirms multi-body `BodySpec.control_surface` plumbing is operational, unlocking the `control_surface` irregular-freq route without new multi-body work.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — confirms scope separation: #501 is the **config-schema lane**, #500 is the **runner lane** (disjoint).
- Related issue #500 — runner-layer counterpart; remains OUT OF SCOPE for this plan (flag coupling only).
- `/tmp/orca-batch-2026-04-24/intel-501.md` — authoritative pod intel with gap analysis and complexity ranking.
- Issue body (#501) — de-facto spec (proposed Pydantic shapes for `QTFOptions`, `FieldPointSpec`, `IrregularFrequencyMethod`).

### Gaps identified

- `QTFOptions` Pydantic model does not exist — must be created with `enabled`, `min_crossing_angle`, `max_crossing_angle`, `min_frequency`, `max_frequency`, `load_calculation_method` fields plus a compat shim for the flat `qtf_calculation: bool` alias.
- `FieldPointSpec` Pydantic model does not exist — must be created with `name`, `points: list[tuple[float, float, float]]`, `detect_inside_bodies: bool` fields.
- `IrregularFrequencyMethod` enum does not exist — must be created with `none | interior_panels | control_surface` values.
- `OutputSpec.field_points` attribute does not exist — must be added (recommended attachment per intel).
- Backend emission paths for crossing-angle override, load-calculation-method override, field-point arrays, and the three-way irregular-freq branch do not exist.
- No TDD coverage for any of the above; existing `TestSolverSettingsMapping` tests must be extended (not rewritten) to preserve backward-compat proofs.

### Evidence (embedded verification)

**Issue statuses** (per issue JSON at `/tmp/orca-batch-2026-04-24/issue-501.json`):
- `#501` — OPEN — "OrcaWave: expand QTF config + field points + irregular frequency method" (label: enhancement)
- `#500` — OPEN — runner-layer counterpart (per overnight-batch design doc); out of scope here.

**File existence** (per pod intel):
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` (789 lines)
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_input_schemas.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` (301 lines)

**Line excerpts** (per pod intel — reviewers should verify against current tree):
- `input_schemas.py:446-495` — `SolverOptions` definition with `remove_irregular_frequencies: bool` and flat QTF fields.
- `input_schemas.py:591-615` — `ControlSurfaceSpec` exists (enables deliverable 1 without new plumbing).
- `orcawave_backend.py:254-269` — interior-panels vs. control-surface body emission; the selector is boolean-implicit today.
- `orcawave_backend.py:515-516` — `QTFMinCrossingAngle=0` / `QTFMaxCrossingAngle=180` hardcoded.
- `orcawave_backend.py:579-580` — `QTFCalculationMethod="Both"` and `PreferredQTFCalculationMethod="Direct method"` hardcoded.

**Gap proofs** (per pod intel):
- Ledger search for "QTF" / "quadratic transfer function" / "irregular frequency" in `data/document-index/standards-transfer-ledger.yaml` → 0 hits.
- Wiki search for QTF / irregular-frequency under `knowledge/wikis/marine-engineering/wiki/` and `knowledge/wikis/naval-architecture/` → 0 hits.
- grep for `QTFOptions` / `FieldPointSpec` / `IrregularFrequencyMethod` in `digitalmodel/src/` → 0 hits (types do not exist).

<!-- Distinct source count: issue body (1) + intel-501.md (2) + 4 prior plans (3-6) + standards ledger (7) + 2 wiki trees (8-9) + 3 source files + 3 test files (10-15) = 15 sources consulted. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-501-orcawave-qtf-fieldpoints-irregfreq.md |
| Schema (modify) | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` |
| Backend (modify) | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` |
| Schema tests (modify) | `digitalmodel/tests/hydrodynamics/diffraction/test_input_schemas.py` |
| Backend tests (modify) | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py` |
| Roundtrip regression (modify) | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-501-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-501-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-501-gemini.md |
| Wiki updates | none required this issue (optional follow-up) |
| Docs updates | docs/plans/README.md (index entry) |

---

## Deliverable

Three orthogonal OrcaWave schema/backend extensions land as a strict superset of the current `DiffractionSpec`: (1) an `IrregularFrequencyMethod` enum that selects `none | interior_panels | control_surface` and drives backend body-panel emission; (2) a nested `QTFOptions` model exposing crossing-angle bounds, period bounds, and load-calculation method (with a backward-compat shim for the legacy flat `qtf_calculation: bool`); (3) a `FieldPointSpec` model hung off `OutputSpec.field_points` that emits the OrcaWave combined-key `FieldPointX, FieldPointY, FieldPointZ` arrays. Existing L00/L02/L03 spec.yml fixtures continue to produce byte-identical OrcaWave YAML.

---

## Pseudocode

### Sub-task 1 — Irregular-frequency method (lightest; lands first)

```
enum IrregularFrequencyMethod:
    none
    interior_panels   # default, equivalent to remove_irregular_frequencies=True today
    control_surface

class SolverOptions:
    # new field
    irregular_frequency_method: IrregularFrequencyMethod = interior_panels
    # retained, now deprecated alias
    remove_irregular_frequencies: bool | None = None

    model_validator:
        if remove_irregular_frequencies is not None:
            if user also set irregular_frequency_method explicitly → raise mutual-exclusion error
            else derive: False → none, True → interior_panels (emit DeprecationWarning)

backend._build_body_dict(body, solver_options):
    method = solver_options.irregular_frequency_method
    match method:
        none             → BodyAddInteriorSurfacePanels = No
        interior_panels  → BodyAddInteriorSurfacePanels = Yes
                           BodyInteriorSurfacePanelMethod = "Triangulation method"
        control_surface  → BodyAddInteriorSurfacePanels = No
                           require body.control_surface is populated (schema validator)
                           emit BodyControlSurfaceType etc. via existing L261-269 path
```

### Sub-task 2 — QTF config expansion

```
class QTFOptions(BaseModel):
    enabled: bool = False
    min_crossing_angle: float = 0.0
    max_crossing_angle: float = 180.0
    min_frequency: float | None = None
    max_frequency: float | None = None
    load_calculation_method: Literal["near field", "far field", "both"] = "near field"

class SolverOptions:
    qtf: QTFOptions | None = None
    # retained deprecated aliases (read-only via model_validator)
    qtf_calculation: bool | None = None
    qtf_min_frequency: float | None = None
    qtf_max_frequency: float | None = None

    model_validator:
        if any flat qtf_* field is set AND qtf is set → mutual-exclusion error
        if any flat field is set → synthesize qtf from them + DeprecationWarning
        if neither is set → qtf = QTFOptions(enabled=False)  (preserves today's default)

backend._build_headings_section(spec):
    qtf = spec.solver_options.resolved_qtf()   # returns QTFOptions, never None
    QTFMinCrossingAngle = qtf.min_crossing_angle     # was 0
    QTFMaxCrossingAngle = qtf.max_crossing_angle     # was 180

backend._build_qtf_section(spec):
    qtf = spec.solver_options.resolved_qtf()
    map qtf.load_calculation_method → (QTFCalculationMethod, PreferredQTFCalculationMethod):
        "near field" → ("Direct",   "Direct method")
        "far field"  → ("Indirect", "Indirect method")
        "both"       → ("Both",     "Direct method")   # preserves current default
    emit period bounds from qtf.min_frequency / qtf.max_frequency as today
```

### Sub-task 3 — Field points (heaviest)

```
class FieldPointSpec(BaseModel):
    name: str
    points: list[tuple[float, float, float]]   # (x, y, z)
    detect_inside_bodies: bool = True          # informational if OrcaWave only honors global switch

class OutputSpec:
    field_points: list[FieldPointSpec] = []    # default empty → today's emission unchanged
    # existing detect_field_points_inside_bodies flag retained

backend._build_outputs_section(spec):
    # existing emission unchanged when field_points is empty
    if spec.outputs.field_points:
        xs, ys, zs = zip(*[p for fp in spec.outputs.field_points for p in fp.points])
        emit combined key "FieldPointX, FieldPointY, FieldPointZ" → [list(xs), list(ys), list(zs)]
        # respect existing detect_field_points_inside_bodies global override
    modular-mode equivalent: same emission inside 08_outputs.yml (orcawave_backend.py:728)
```

---

## Files to Change

| # | Action | Path | Reason |
|---|---|---|---|
| 1 | Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` | **Sub-task 1:** add `IrregularFrequencyMethod` enum; extend `SolverOptions` with `irregular_frequency_method`; add deprecation validator for `remove_irregular_frequencies`. Then **sub-task 2:** add `QTFOptions` model; add `SolverOptions.qtf`; add compat shim for flat `qtf_calculation` / `qtf_min_frequency` / `qtf_max_frequency`. Then **sub-task 3:** add `FieldPointSpec` model; add `OutputSpec.field_points`. Update `__all__`. |
| 2 | Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` | **Sub-task 1:** branch `_build_body_dict` on `irregular_frequency_method` (L254-269). **Sub-task 2:** replace hardcoded 0/180 in `_build_headings_section` (L515-516) and the hardcoded `"Both"` / `"Direct method"` in `_build_qtf_section` (L579-580). **Sub-task 3:** extend `_build_outputs_section` (L544-555) to emit `FieldPointX, FieldPointY, FieldPointZ` combined key; mirror in modular-mode path (L728). |
| 3 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_input_schemas.py` | Add cases: `IrregularFrequencyMethod` round-trip; `QTFOptions` round-trip; legacy flat → nested alias migration; `FieldPointSpec` parse + validation. Preserve all existing L00/L02/L03 fixture tests unchanged. |
| 4 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py` | Extend `TestSolverSettingsMapping` (L542-586) with: `test_irregular_frequency_method_none`, `..._interior_panels` (back-compat proof), `..._control_surface` (requires body control_surface); `test_qtf_crossing_angle_override`, `test_qtf_load_calc_method_{near_field,far_field,both}`; `test_field_points_emit_combined_key`. Extend `TestOrcaWaveBackendModularMode` (L594-705) with field-points-in-`08_outputs.yml` assertion. |
| 5 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` | Add a **byte-identical backward-compat** gate: existing L00/L02/L03 spec → YAML must match golden file exactly after the schema extension. Add two forward-compat cases: spec with new fields roundtrips cleanly. |
| 6 | Update | `docs/plans/README.md` | Add index entry for this plan. |

**Ordering rationale (per intel):** sub-task 1 is lightest (90% plumbed — enum + 3-way branch); sub-task 2 is medium (mostly de-hardcoding with a compat shim); sub-task 3 is heaviest (greenfield model + combined-key YAML emission). Each sub-task is independently landable and testable, so reviewers can approve incrementally if desired. All three must ship to fully close #501.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_irregular_frequency_method_none | enum `none` emits `BodyAddInteriorSurfacePanels=No` | spec with `irregular_frequency_method="none"` | backend YAML lacks `BodyInteriorSurfacePanelMethod` |
| test_irregular_frequency_method_interior_panels | enum `interior_panels` preserves legacy emission | spec with `irregular_frequency_method="interior_panels"` | `BodyAddInteriorSurfacePanels=Yes` + `BodyInteriorSurfacePanelMethod="Triangulation method"` |
| test_irregular_frequency_method_control_surface | enum `control_surface` uses body's control_surface mesh | spec with body `control_surface` populated + method=`control_surface` | `BodyAddInteriorSurfacePanels=No` + existing control-surface emission path fires |
| test_control_surface_method_without_mesh_fails | schema validator requires mesh when method=`control_surface` | spec with method=`control_surface`, no body control_surface | `ValidationError` at YAML load |
| test_remove_irregular_frequencies_legacy_true | legacy `True` migrates to `interior_panels` | spec with `remove_irregular_frequencies=true` only | `irregular_frequency_method=interior_panels` + DeprecationWarning |
| test_remove_irregular_frequencies_legacy_false | legacy `False` migrates to `none` | spec with `remove_irregular_frequencies=false` only | `irregular_frequency_method=none` + DeprecationWarning |
| test_irregular_frequency_mutual_exclusion | setting both flat + enum raises | spec with both fields set | `ValidationError` |
| test_qtf_crossing_angle_override | crossing-angle fields emit instead of 0/180 | `QTFOptions(min_crossing_angle=30, max_crossing_angle=150)` | backend YAML has 30/150, not 0/180 |
| test_qtf_load_calc_method_near_field | `"near field"` → `QTFCalculationMethod=Direct` | `QTFOptions(load_calculation_method="near field")` | `QTFCalculationMethod=Direct`, `Preferred=Direct method` |
| test_qtf_load_calc_method_far_field | `"far field"` → `QTFCalculationMethod=Indirect` | `QTFOptions(load_calculation_method="far field")` | `QTFCalculationMethod=Indirect`, `Preferred=Indirect method` |
| test_qtf_load_calc_method_both | `"both"` preserves today's default | `QTFOptions(load_calculation_method="both")` | `QTFCalculationMethod=Both`, `Preferred=Direct method` |
| test_qtf_legacy_flat_alias | flat `qtf_calculation: true` migrates to nested | spec with flat fields only | `qtf.enabled=True` + period bounds mapped + DeprecationWarning |
| test_qtf_mutual_exclusion | setting both flat + nested raises | spec with `qtf_calculation` and `qtf:` | `ValidationError` |
| test_field_points_emit_combined_key | non-empty field_points emits combined X/Y/Z arrays | `OutputSpec(field_points=[FieldPointSpec(name="deck", points=[(1,2,3),(4,5,6)])])` | YAML has `"FieldPointX, FieldPointY, FieldPointZ": [[1,4],[2,5],[3,6]]` |
| test_field_points_empty_unchanged | empty field_points preserves current emission | `OutputSpec(field_points=[])` | backend YAML byte-identical to pre-#501 output |
| test_field_points_modular_mode | field points appear in 08_outputs.yml in modular mode | spec with field_points, modular output mode | `08_outputs.yml` contains combined key |
| test_byte_identical_L00_fixture | **critical regression gate** — L00 fixture unchanged after #501 lands | existing `L00` spec.yml | OrcaWave YAML byte-identical to golden file |
| test_byte_identical_L02_fixture | same for L02 | existing `L02` spec.yml | byte-identical |
| test_byte_identical_L03_fixture | same for L03 (QTF + ship benchmark) | existing `L03` spec.yml | byte-identical |

---

## Acceptance Criteria

- [ ] All new schema tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_input_schemas.py -v`
- [ ] All new backend tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_orcawave_backend.py -v`
- [ ] Byte-identity regression gate passes: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py -v`
- [ ] Full diffraction suite green: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/ -v`
- [ ] No regressions elsewhere in digitalmodel: `cd digitalmodel && uv run pytest tests/orcawave/ -v`
- [ ] `IrregularFrequencyMethod`, `QTFOptions`, `FieldPointSpec` exported via `input_schemas.__all__`
- [ ] Backward-compat: every existing L00/L02/L03 fixture produces unchanged OrcaWave YAML (verified by byte-identity tests)
- [ ] DeprecationWarnings emitted for flat `qtf_calculation` / `remove_irregular_frequencies` usages (not errors)
- [ ] docs/plans/README.md updated with this plan
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | _(pending adversarial review)_ |
| Codex | APPROVE / MINOR / MAJOR | _(pending adversarial review)_ |
| Gemini | APPROVE / MINOR / MAJOR | _(pending adversarial review)_ |

**Overall result:** PASS / FAIL (re-draft required) — _(pending)_

Revisions made based on review:
- _(to be filled after cross-review)_

---

## Risks and Open Questions

- **Risk — backward compatibility is load-bearing.** The L03 ship benchmark roundtrip (#2457) and Wave 2 parametric generator (2026-04-01 intensive plan) both assume stable OrcaWave YAML output. The byte-identity regression gate (three fixture tests + `test_orcawave_semantic_roundtrip.py`) is the sole defense — it must be written **before** the schema changes, fail deterministically on any drift, and block merge.

- **Risk — `control_surface` method requires a mesh file but schema can only validate string presence.** Actual mesh-file existence is #500's pre-flight territory. This plan adds a schema-level check that `body.control_surface` is populated when `irregular_frequency_method="control_surface"`, but does NOT verify the file exists on disk. Flag coupling to #500, do not plan the runner-side check here.

- **Risk — field-points modular-mode emission.** The combined-key `"FieldPointX, FieldPointY, FieldPointZ"` is a comma-key convention (per `benchmark_input_comparison.py:391`). Modular-mode writes into `08_outputs.yml` (`orcawave_backend.py:728`); a YAML emitter that normalizes key whitespace could break OrcaWave's parser. Test must assert byte-level key form, not just semantic equality.

- **Risk — QTF load-calculation-method mapping assumption.** This plan maps `"near field"→Direct`, `"far field"→Indirect`, `"both"→Both`. The `"both"` mapping preserves today's default (`QTFCalculationMethod=Both`, `PreferredQTFCalculationMethod="Direct method"`), which is the back-compat anchor. If OrcaWave's actual semantic for `"near field"` differs from `Direct`, the mapping needs a correction in the OrcaWave manual citation step. Reviewer must confirm mapping against the OrcaWave User Manual before landing sub-task 2.

- **[TRADEOFF FOR USER] — enum conversion default-value migration strategy.** This plan keeps `remove_irregular_frequencies: bool | None = None` as a deprecated alias with a model-validator that derives `irregular_frequency_method` from it. Alternative A: remove the flat field entirely (clean, but breaks every existing spec.yml that sets it — full regeneration of fixtures required). Alternative B (this plan): keep flat field, emit `DeprecationWarning`, plan removal for a later release. **Decision point: proceed with B (compat-preserving), or bite the bullet with A (breaking change with immediate fixture migration)?**

- **[TRADEOFF FOR USER] — QTF config scope: minimum-viable vs. full parity.** Minimum-viable (this plan) covers the five fields in the issue body: `enabled`, crossing-angle bounds, frequency bounds, load-calculation method. Full Orcina QTF parity would also include: `QTFFrequencyTypes` (sum/difference), `QTFHeadingPairs` (sparse heading-pair specification), `QTFTruncationMethod`, and per-body `QTFContributions` filtering. **Decision point: ship MVP now and defer the remaining four options to a follow-up issue, or expand scope here?** Intel recommends MVP — the four extra options have no known downstream consumer in digitalmodel today.

- **[TRADEOFF FOR USER] — `FieldPointSpec` attachment point.** Intel recommends `OutputSpec.field_points` (co-locates with `detect_field_points_inside_bodies`). Alternative: top-level `DiffractionSpec.field_points` (mirrors `free_surface_zone`). The issue body does not disambiguate. **Decision point: OutputSpec (recommended, semantic cohesion) vs. top-level (symmetry with `free_surface_zone`)?**

- **Open — per-group `detect_inside_bodies` vs. global switch.** OrcaWave appears to honor only the global `DetectAndSkipFieldPointsInsideBodies` flag. `FieldPointSpec.detect_inside_bodies` is likely informational/validated only, not emitted per-group. Needs confirmation against OrcaWave User Manual before the field-points backend emission is finalized; if unsupported, emit a schema-level warning when per-group values conflict with the global.

- **Open — should `QTFOptions` live in its own module?** `input_schemas.py` is 789 lines. Moving `QTFOptions`, `FieldPointSpec`, `IrregularFrequencyMethod`, `FreeSurfaceZoneSpec`, `ControlSurfaceSpec` into a new `input_schemas_extensions.py` module would split cleanly, but is out of scope for #501 — flag as housekeeping follow-up.

---

## Complexity: T2

**T2** — three orthogonal schema + backend extensions across two files plus three test files. Two of the three features (irregular-freq, QTF) have most plumbing already present; work is enum-ification and de-hardcoding. Field-points is the only greenfield addition. Estimated: ~130 lines schema + ~65 lines backend + ~18 tests. Backward-compat gate (byte-identical L00/L02/L03 YAML) is well-defined. Three distinct sub-tasks with ordering dependencies drive this above T1; absence of new external-tool integration, cross-repo work, or architectural refactor keeps it below T3.
