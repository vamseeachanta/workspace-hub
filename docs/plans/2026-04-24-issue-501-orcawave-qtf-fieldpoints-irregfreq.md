# Plan for #501: OrcaWave — expand QTF config + field points + irregular frequency method

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/501
> **Review artifacts:** scripts/review/results/2026-04-24-plan-501-claude.md | ...-codex.md | ...-gemini.md | ...-adversarial.md

---

## Revision Notes (r2)

This plan has been revised following a Wave 3 adversarial review (MAJOR verdict, 10 defects) and a Claude 2nd-pass review (3 additional MAJOR findings). Each defect is addressed below; the three-sub-task ordering (irregular-freq → QTF → field points) and the "90% plumbed" framing for `control_surface` are preserved.

| # | Defect (class) | Source | How this r2 addresses it |
|---|---|---|---|
| C1 | **CRITICAL — QTF conditional-emission gap** (`_build_headings_section` + `_build_qtf_section` are gated by `solve_type`, not `qtf_calculation`). Enabling `QTFOptions.enabled=True` with non-QTF `solve_type` would silently drop user overrides and regress byte-identity on L03. | Wave 3 D1+D2 | (a) Pseudocode now emits crossing-angle and load-calc-method only **inside** the existing `solve_type in {diagonal_qtf, full_qtf}` gate. (b) New schema-level cross-field validator raises `ValidationError` when `qtf.enabled=True` conflicts with `solve_type` not being a QTF type. (c) `resolved_qtf()` accessor enforces a single source of truth. (d) Dedicated tests `test_qtf_crossing_angle_not_emitted_when_solve_type_nonqtf` and `test_qtf_enabled_raises_when_solve_type_nonqtf` make the gate falsifiable. (e) L03 byte-identity gate mechanism is itemized in Acceptance Criteria §AC-B. |
| C2 | **CRITICAL — `OutputSpec.detect_field_points_inside_bodies` does not exist in schema.** Only the hardcoded backend literal at `orcawave_backend.py:553` exists. | 2nd-pass #1 | Sub-task 3 now explicitly creates the field `OutputSpec.detect_field_points_inside_bodies: bool = True` (default preserves today's `"Yes"` literal). Pseudocode and Files-to-Change call the new field out; backend reads from the new field instead of hardcoding. |
| C3 | **CRITICAL — `tests/hydrodynamics/diffraction/benchmarks/` infrastructure does not exist.** Byte-identity regression gate depends on it. | 2nd-pass #2 | New Sub-task 0 (runs before Sub-task 1) creates the benchmarks directory, the golden-file capture helper, and a precursor TDD test (`test_benchmark_infrastructure_generates_golden_from_pre_change_tree`) that must pass on the unmodified tree before any schema change lands. Golden-file paths are named explicitly under §Files to Change. |
| C4 | **CRITICAL — "L00 fixture" is ambiguous: 10 sub-specs under `docs/domains/orcawave/L00_validation_wamit/`.** Single test name is incomplete. | 2nd-pass #3 | Sub-task 0 enumerates in-scope sub-specs by path (see §Byte-Identity Corpus) and parameterizes the byte-identity test over that list. L02 and L03 are similarly enumerated. |
| H1 | **HIGH — `remove_irregular_frequencies` default-type change could break implicit back-compat.** Today's non-optional `bool` default `True` is load-bearing for specs that omit the field. | Wave 3 D3 | Pseudocode now explicitly documents the `None → interior_panels` mapping and the field-default invariant. New test `test_remove_irregular_frequencies_legacy_unset` covers the most common legacy path. |
| H2 | **HIGH — `DetectAndSkipFieldPointsInsideBodies` misdescription of current state.** | Wave 3 D4 | Resolved by C2 above (new explicit schema field with default that preserves `"Yes"`). Intel-state language corrected in §Resource Intelligence Summary. |
| M1 | **MEDIUM — flat-to-nested QTF default-drift** (int `0` vs. float `0.0` literals at YAML layer). | Wave 3 D5 | `QTFOptions` numeric defaults are declared as the same literal type the current emission uses; backend emission is type-pinned via explicit `int()` cast inside the existing QTF gate. New assertion in byte-identity test asserts token-level (not semantic) equality. |
| M2 | **MEDIUM — byte-identity test implementation unspecified / golden-file source unnamed.** | Wave 3 D6 | Sub-task 0 (C3 fix) names each golden file path explicitly and freezes capture to the pre-change tree. Acceptance Criteria §AC-B enumerates the verification mechanism. |
| M3 | **MEDIUM — `_build_general_section` (lines 414-451) is a downstream consumer of `qtf_calculation` but was ignored.** | Wave 3 D7 | `_build_general_section` added to Files to Change; it will call `spec.solver_options.resolved_qtf().enabled` via the same accessor as headings/qtf. Dedicated test `test_build_general_section_unchanged_under_flat_compat` added. |
| M4 | **MEDIUM (2nd-pass) — modular-mode misdirection / `body` vs. `vessel` naming / silent `remove_irregular_frequencies + control_surface` combo / missed emission site 441-449 / missing `Literal` import / "90% wired" overstatement / small line-range misquote.** | 2nd-pass minors #4-10 | All folded into §Risks, §TDD, and §Files to Change — see the per-item rows. "90% plumbed" replaced with "selector missing but emission path exists"; line ranges re-cited from the live source extracts in §Resource Intelligence Summary. |
| L1 | **LOW — `load_calculation_method` Literal mapping unverified vs. OrcaWave manual.** | Wave 3 D8 | `QTFOptions.load_calculation_method` now passes through OrcaWave's own vocabulary directly (`Literal["Direct", "Indirect", "Both"]`), moving the responsibility to the caller and removing an interpretive layer. Acceptance Criteria §AC-E requires a code-comment cite to the OrcaWave User Manual section. |
| L2 | **LOW — `test_field_points_empty_unchanged` relies on golden without naming it.** | Wave 3 D9 | Absorbed into the Sub-task 0 golden corpus. |
| L3 | **LOW — `load_calculation_method` string-literal drift (lowercase-space vs. title-case).** | Wave 3 D10 | Resolved by L1 — a single canonical vocabulary (OrcaWave's) is used throughout the plan and tests. |

**Residual uncertainty called out for reviewer:** the C1 remediation chooses option (a) — **raise on `enabled=True` with non-QTF `solve_type`** — over auto-upgrading `solve_type` or making `enabled` informational. This is the safest default (no silent surprise) but the strictest; user approval is invited on this decision (see §Risks, TRADEOFF C1).

**Status:** `draft` — this r2 has NOT been re-reviewed. A fresh cross-review is required.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:446-495` — `SolverOptions` currently defines `remove_irregular_frequencies: bool = True` (non-optional, default True), `qtf_calculation: bool`, and optional `qtf_min_frequency` / `qtf_max_frequency`. No QTF crossing-angle, load-calc-method, or irregular-frequency-method fields.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:498-516` — `OutputSpec`. The field `detect_field_points_inside_bodies` **does not currently exist on the schema** (2nd-pass correction); only the hardcoded backend emission `DetectAndSkipFieldPointsInsideBodies: "Yes"` at `orcawave_backend.py:553`. Sub-task 3 creates this schema field.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:591-615` — `ControlSurfaceSpec` exists (mesh-file driven) and is exposed via `BodySpec.control_surface` (L644-647). The `control_surface` emission path in the backend already exists — **the selector is the only missing piece** (intel calls this "90% plumbed"; the corrected framing is "selector missing, emission path intact").
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:254-269` — interior-surface-panel body emission with `BodyInteriorSurfacePanelMethod="Triangulation method"` hardcoded; `control_surface` branch (L261-269) fires only when `body.control_surface` is populated.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:414-451` — `_build_general_section` is a **downstream consumer of `qtf_calculation`** (gates `QuadraticLoadPressureIntegration`, `QuadraticLoadControlSurface`, `PreferredQuadraticLoadCalculationMethod`). Intel flagged this at L29; r1 plan missed it; r2 includes it.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:507-532` — `_build_headings_section` emits `QTFMinCrossingAngle=0`, `QTFMaxCrossingAngle=180` **only inside an `if spec.solver_options.qtf_calculation or is_qtf:` conditional block**. This is the conditional-emission gate that D1 called out; r2 preserves it.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:544-555` — `_build_outputs_section` emits `OutputPanelVelocities` + `DetectAndSkipFieldPointsInsideBodies="Yes"` (hardcoded string). No `FieldPointX, FieldPointY, FieldPointZ` path.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:572-600` — `_build_qtf_section` **returns `{}` early unless `solve_type in ("diagonal_qtf", "full_qtf")`**; only then are `QTFCalculationMethod="Both"` and `PreferredQTFCalculationMethod="Direct method"` emitted. This is the second conditional gate flagged by D2.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:728` — modular-mode `08_outputs.yml` writer.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py:391-393` — documents OrcaWave's combined-key convention `"FieldPointX, FieldPointY, FieldPointZ"` for field-point emission.
- Found: `docs/domains/orcawave/L00_validation_wamit/` — **10 sub-specs** (C4 fix — enumerated in §Byte-Identity Corpus below). Not a single fixture.
- Gap: no `QTFOptions`, `FieldPointSpec`, `IrregularFrequencyMethod`, or `OutputSpec.detect_field_points_inside_bodies` exists in the schema.
- Gap: `tests/hydrodynamics/diffraction/benchmarks/` does not exist — must be created (Sub-task 0).
- Gap: no test coverage for QTF options, field-points, or the three-way irregular-frequency-method selector.

### Standards

| Standard | Status | Source |
|---|---|---|
| QTF / quadratic-transfer-function conventions | not in ledger | `data/document-index/standards-transfer-ledger.yaml` — 0 hits for "QTF", "quadratic transfer function", "WAMIT", or "irregular frequency" |
| DNV-RP-C205 (second-order wave loads) | not promoted | cited by domain name only; no ledger entry |
| WAMIT User Manual (fdf mesh, irregular-freq methods) | not promoted | canonical vocabulary source for OrcaWave |
| OrcaWave User Manual (QTFCalculationMethod, BodyInteriorSurfacePanelMethod, FieldPointX/Y/Z) | not promoted | canonical emission vocabulary — authoritative for L1 (`Direct`/`Indirect`/`Both`) |

No standards-compliance gate is triggered by #501.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/` — 0 hits on QTF, quadratic transfer function, irregular frequency, or second-order wave loads.
- `knowledge/wikis/naval-architecture/wiki/` — only `entities/orcaflex-viv-analysis.md` is adjacent (VIV, not diffraction).
- Result: **no wiki page authoritatively covers the three #501 features.** Optional follow-up only.

### Documents consulted

- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — names `DiffractionSpec` + `OrcaWaveBackend` as scaling lever; #501 is a strict extension.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` — anchors L03 byte-identity test target.
- `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — confirms multi-body `BodySpec.control_surface` plumbing.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — #501 is config-schema lane; #500 is runner lane (disjoint).
- Related issue #500 — runner-layer counterpart; OUT OF SCOPE (flag coupling only).
- `/tmp/orca-batch-2026-04-24/intel-501.md` — authoritative pod intel.
- Issue body (#501) — de-facto spec (proposed Pydantic shapes for `QTFOptions`, `FieldPointSpec`, `IrregularFrequencyMethod`).
- `scripts/review/results/2026-04-24-plan-501-adversarial.md` — Wave 3 MAJOR verdict; 10 defects.
- `scripts/review/results/2026-04-24-plan-501-claude.md` — 2nd-pass MAJOR verdict; 3 additional blocking findings.

### Gaps identified

- `QTFOptions` Pydantic model does not exist — must be created with `enabled`, `min_crossing_angle`, `max_crossing_angle`, `min_frequency`, `max_frequency`, `load_calculation_method` fields + compat shim for flat aliases + cross-field validator that raises when `enabled=True` conflicts with `solve_type`.
- `FieldPointSpec` Pydantic model does not exist — must be created with `name`, `points: list[tuple[float, float, float]]`, `detect_inside_bodies: bool` fields.
- `IrregularFrequencyMethod` enum does not exist — must be created with `none | interior_panels | control_surface` values.
- `OutputSpec.field_points` attribute does not exist.
- `OutputSpec.detect_field_points_inside_bodies` attribute does not exist (C2 fix).
- Backend emission paths for crossing-angle override, load-calculation-method override, field-point arrays, and three-way irregular-freq branch do not exist.
- `tests/hydrodynamics/diffraction/benchmarks/` directory + golden-file capture helper + per-fixture golden YAMLs do not exist (C3 fix — created by Sub-task 0).
- No TDD coverage for any of the above.

### Evidence (embedded verification)

**Issue statuses** (per `/tmp/orca-batch-2026-04-24/issue-501.json`):
- `#501` — OPEN — "OrcaWave: expand QTF config + field points + irregular frequency method" (label: enhancement)
- `#500` — OPEN — runner-layer counterpart; out of scope.

**File existence** (per pod intel + 2nd-pass review verification):
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` (789 lines)
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_input_schemas.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` (301 lines)
- EXISTS: `docs/domains/orcawave/L00_validation_wamit/` (10 sub-specs)
- MISSING (new — created by Sub-task 0): `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/` directory + children.

**Line excerpts** (per pod intel — reviewers should verify against current tree):
- `input_schemas.py:446-495` — `SolverOptions` definition.
- `input_schemas.py:591-615` — `ControlSurfaceSpec` exists.
- `orcawave_backend.py:254-269` — interior-panels vs. control-surface body emission.
- `orcawave_backend.py:414-451` — `_build_general_section` (downstream QTF consumer — M3 fix includes it).
- `orcawave_backend.py:507-532` — `_build_headings_section` with the `if qtf_calculation or is_qtf:` gate.
- `orcawave_backend.py:572-600` — `_build_qtf_section` with the `if solve_type in (...qtf):` early return.

**Gap proofs** (per pod intel):
- Ledger search for "QTF" / "quadratic transfer function" / "irregular frequency" in `data/document-index/standards-transfer-ledger.yaml` → 0 hits.
- Wiki search → 0 hits.
- grep for `QTFOptions` / `FieldPointSpec` / `IrregularFrequencyMethod` / `detect_field_points_inside_bodies` in `digitalmodel/src/` → 0 hits.
- `ls digitalmodel/tests/hydrodynamics/diffraction/benchmarks/` → does not exist (per 2nd-pass review).

<!-- Distinct source count: issue body (1) + intel-501.md (2) + 4 prior plans (3-6) + standards ledger (7) + 2 wiki trees (8-9) + 3 source files + 3 test files (10-15) + adversarial review (16) + 2nd-pass review (17) + L00 fixture tree (18) = 18 sources consulted. -->

### Byte-Identity Corpus (enumerates what "L00/L02/L03 fixture" means)

Per C4: the regression gate runs against concrete sub-specs. **The exact path list is authoritative and must be frozen at Sub-task 0**:

- **L00 — 10 sub-specs under `docs/domains/orcawave/L00_validation_wamit/`** — every `spec.yml` file directly under this tree (the review confirms there are 10). The precise path list will be captured verbatim by the Sub-task 0 helper (no manual transcription; `find docs/domains/orcawave/L00_validation_wamit -name 'spec.yml'` feeds the parametrization).
- **L02 — `docs/domains/orcawave/L02_*/spec.yml`** (multi-body fixture family). The helper enumerates them the same way.
- **L03 — `docs/domains/orcawave/L03_ship_benchmark/spec.yml`** (anchors the #2457 ship roundtrip — the QTF-critical fixture).

**Parametrization:** the byte-identity test is `@pytest.mark.parametrize("spec_path", ALL_BYTE_IDENTITY_FIXTURES)` where `ALL_BYTE_IDENTITY_FIXTURES` is generated by the Sub-task 0 helper at test-collection time. Each sub-spec has a sibling golden YAML (named below in §Files to Change).

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
| **Benchmarks infrastructure (new)** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` |
| **Benchmarks helper (new)** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` |
| **Benchmarks infra test (new)** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_benchmark_infrastructure.py` |
| **Benchmarks golden corpus (new)** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden/<L00-sub-spec-id>.yml` × 10 + L02 family + L03 |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-501-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-501-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-501-gemini.md |
| Plan review — Adversarial (r1) | scripts/review/results/2026-04-24-plan-501-adversarial.md |
| Wiki updates | none required (optional follow-up) |
| Docs updates | docs/plans/README.md (index entry) |

---

## Deliverable

Three orthogonal OrcaWave schema/backend extensions land as a strict superset of the current `DiffractionSpec`: (1) an `IrregularFrequencyMethod` enum that selects `none | interior_panels | control_surface` and drives backend body-panel emission; (2) a nested `QTFOptions` model exposing crossing-angle bounds, period bounds, and load-calculation method (with a backward-compat shim for the legacy flat `qtf_calculation: bool` and a cross-field validator against `solve_type`); (3) a `FieldPointSpec` model hung off `OutputSpec.field_points` that emits the OrcaWave combined-key `FieldPointX, FieldPointY, FieldPointZ` arrays, plus a new `OutputSpec.detect_field_points_inside_bodies: bool = True` field that replaces the backend's hardcoded literal. All pre-change L00 (10 sub-specs) / L02 (family) / L03 fixtures continue to produce byte-identical OrcaWave YAML, verified by a dedicated benchmarks harness built in Sub-task 0.

---

## Pseudocode

### Sub-task 0 — Benchmarks infrastructure + golden capture (precursor; runs first)

```
# tests/hydrodynamics/diffraction/benchmarks/golden_capture.py
def enumerate_byte_identity_fixtures() -> list[Path]:
    # Returns the full corpus — L00 (10 sub-specs), L02 family, L03
    root = repo_root / "docs/domains/orcawave"
    return sorted([
        *root.glob("L00_validation_wamit/*/spec.yml"),   # 10 sub-specs
        *root.glob("L02_*/spec.yml"),                    # L02 family
        repo_root / "docs/domains/orcawave/L03_ship_benchmark/spec.yml",
    ])

def golden_path_for(spec_path: Path) -> Path:
    # Stable 1:1 mapping from spec.yml to golden file under benchmarks/golden/
    return benchmarks_dir / "golden" / f"{spec_path.parent.name}.yml"

def capture_golden(spec_path: Path) -> None:
    # Runs against PRE-CHANGE tree — must be invoked + committed BEFORE any schema edit
    spec = DiffractionSpec.from_yaml(spec_path.read_text())
    orcawave_yaml_bytes = OrcaWaveBackend().render(spec)
    golden_path_for(spec_path).write_bytes(orcawave_yaml_bytes)

# tests/hydrodynamics/diffraction/benchmarks/test_benchmark_infrastructure.py
def test_benchmark_infrastructure_generates_golden_from_pre_change_tree():
    # Runs on the UNMODIFIED tree; asserts every fixture has a reproducible golden
    for spec_path in enumerate_byte_identity_fixtures():
        assert golden_path_for(spec_path).exists()
        # Bit-exact re-rendering from HEAD must match the stored golden
        regenerated = OrcaWaveBackend().render(DiffractionSpec.from_yaml(spec_path.read_text()))
        assert regenerated == golden_path_for(spec_path).read_bytes()
```

Sub-task 0 is committed **before** Sub-tasks 1-3 touch source. Any drift in the golden files after that point indicates a back-compat break.

### Sub-task 1 — Irregular-frequency method (lightest; lands first)

```
enum IrregularFrequencyMethod:
    none
    interior_panels   # default, equivalent to remove_irregular_frequencies=True today
    control_surface

class SolverOptions:
    # new field — default preserves today's non-optional `True` semantics
    irregular_frequency_method: IrregularFrequencyMethod = interior_panels
    # retained as deprecated alias — type-widened to accept None to distinguish unset from explicit False
    remove_irregular_frequencies: bool | None = None

    model_validator(mode="after"):
        # H1 FIX: spell out the None → interior_panels default-preservation
        if remove_irregular_frequencies is None:
            # unset-legacy case: irregular_frequency_method already = interior_panels via field default
            pass
        elif remove_irregular_frequencies is True:
            if user also set irregular_frequency_method explicitly → ValidationError (mutual exclusion)
            else: irregular_frequency_method = interior_panels + emit DeprecationWarning
        elif remove_irregular_frequencies is False:
            if user also set irregular_frequency_method explicitly → ValidationError
            else: irregular_frequency_method = none + emit DeprecationWarning

    model_validator(mode="after"):
        # M4 sub-item: silent combo guard — legacy boolean + control_surface is ambiguous
        if remove_irregular_frequencies is not None and irregular_frequency_method == control_surface:
            raise ValidationError(...)

backend._build_body_dict(body, solver_options):
    method = solver_options.irregular_frequency_method
    match method:
        none             → BodyAddInteriorSurfacePanels = No
                           (no BodyInteriorSurfacePanelMethod emitted)
        interior_panels  → BodyAddInteriorSurfacePanels = Yes
                           BodyInteriorSurfacePanelMethod = "Triangulation method"
        control_surface  → BodyAddInteriorSurfacePanels = No
                           require body.control_surface is populated (else ValidationError at schema load)
                           emit BodyControlSurfaceType etc. via existing L261-269 path
```

### Sub-task 2 — QTF config expansion (C1 FIX — gate-aware)

```
class QTFOptions(BaseModel):
    enabled: bool = False
    min_crossing_angle: int = 0       # M1 FIX: int, matches today's YAML literal
    max_crossing_angle: int = 180     # M1 FIX: int
    min_frequency: float | None = None
    max_frequency: float | None = None
    # L1 FIX: pass-through OrcaWave's own vocabulary; no translation layer
    load_calculation_method: Literal["Direct", "Indirect", "Both"] = "Both"
    # code-comment cite: OrcaWave User Manual §<TBD at landing> enumerates these exact strings

class SolverOptions:
    qtf: QTFOptions | None = None
    # retained deprecated aliases
    qtf_calculation: bool | None = None
    qtf_min_frequency: float | None = None
    qtf_max_frequency: float | None = None

    def resolved_qtf(self) -> QTFOptions:
        # Single source of truth — returns populated QTFOptions, never None
        if self.qtf is not None:
            return self.qtf
        return QTFOptions(
            enabled=bool(self.qtf_calculation),
            min_frequency=self.qtf_min_frequency,
            max_frequency=self.qtf_max_frequency,
        )

    model_validator(mode="after"):
        if self.qtf is not None and any(flat qtf_* field is set):
            raise ValidationError("mutual exclusion")
        if any flat qtf_* field is set:
            emit DeprecationWarning

    # C1 CRITICAL FIX — cross-field validator against solve_type
    model_validator(mode="after"):
        resolved = self.resolved_qtf()
        solve_type = self.solve_type   # or however SolverOptions references DiffractionSpec.solve_type
        if resolved.enabled and solve_type not in ("diagonal_qtf", "full_qtf"):
            raise ValidationError(
                f"QTFOptions.enabled=True requires solve_type in (diagonal_qtf, full_qtf); "
                f"got solve_type={solve_type!r}. Either set a QTF solve_type or leave QTF disabled."
            )
        # Inverse is ALLOWED: solve_type=full_qtf with enabled=False falls back to today's implicit QTF.

backend._build_headings_section(spec):
    qtf = spec.solver_options.resolved_qtf()
    # C1 FIX — preserve the EXISTING conditional gate; do NOT unconditionally emit
    if spec.solver_options.qtf_calculation or is_qtf(spec) or qtf.enabled:
        section["QTFMinCrossingAngle"] = int(qtf.min_crossing_angle)  # M1 FIX: int cast
        section["QTFMaxCrossingAngle"] = int(qtf.max_crossing_angle)  # M1 FIX: int cast
        # ...existing period-bound emission unchanged...

backend._build_qtf_section(spec):
    solve_type = _effective_solve_type(spec)
    if solve_type not in ("diagonal_qtf", "full_qtf"):
        return {}   # PRESERVED: C1 gate — identical early return as today
    qtf = spec.solver_options.resolved_qtf()
    # L1 FIX — direct pass-through; the validator already bounds this to {Direct, Indirect, Both}
    section["QTFCalculationMethod"] = qtf.load_calculation_method
    section["PreferredQTFCalculationMethod"] = (
        "Direct method"   if qtf.load_calculation_method in ("Direct", "Both")
        else "Indirect method"
    )
    emit period bounds from qtf.min_frequency / qtf.max_frequency as today

backend._build_general_section(spec):    # M3 FIX — re-audit downstream consumer
    qtf = spec.solver_options.resolved_qtf()
    # Replace any direct read of spec.solver_options.qtf_calculation with qtf.enabled
    # Gated emission of QuadraticLoadPressureIntegration / QuadraticLoadControlSurface /
    # PreferredQuadraticLoadCalculationMethod unchanged semantically.
```

### Sub-task 3 — Field points + detect-inside-bodies schema field (heaviest; C2 FIX)

```
class FieldPointSpec(BaseModel):
    name: str
    points: list[tuple[float, float, float]]   # (x, y, z)
    # Intel notes OrcaWave likely honors only the global switch; flag remains for
    # schema-level validation/warning when per-group conflicts with global.
    detect_inside_bodies: bool = True

class OutputSpec:
    field_points: list[FieldPointSpec] = []
    # C2 CRITICAL FIX — new schema field; default preserves today's hardcoded "Yes"
    detect_field_points_inside_bodies: bool = True

backend._build_outputs_section(spec):
    # C2 FIX — read from the new schema field instead of hardcoding the literal
    section["DetectAndSkipFieldPointsInsideBodies"] = (
        "Yes" if spec.outputs.detect_field_points_inside_bodies else "No"
    )
    if spec.outputs.field_points:
        xs, ys, zs = zip(*[p for fp in spec.outputs.field_points for p in fp.points])
        # Combined-key convention per benchmark_input_comparison.py:391
        section["FieldPointX, FieldPointY, FieldPointZ"] = [list(xs), list(ys), list(zs)]
        # Optional: schema-level warning if any fp.detect_inside_bodies diverges from the global
    # Modular mode mirror at orcawave_backend.py:728 receives the same section dict

# Byte-identity guarantee:
# When `field_points=[]` and `detect_field_points_inside_bodies=True` (the defaults), the
# emitted YAML is byte-identical to the pre-change output because:
#   (a) the combined-key line is elided when field_points is empty, and
#   (b) "Yes" is the preserved literal.
```

---

## Files to Change

| # | Action | Path | Reason |
|---|---|---|---|
| 0a | **Create** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/__init__.py` | **C3 FIX** — the benchmarks package does not exist. |
| 0b | **Create** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` | Golden-YAML capture helper (`enumerate_byte_identity_fixtures`, `capture_golden`, `golden_path_for`). |
| 0c | **Create** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/test_benchmark_infrastructure.py` | Precursor test that asserts golden corpus reproduces on the unmodified tree. Must pass before Sub-task 1 starts. |
| 0d | **Create** | `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden/*.yml` | One golden YAML per in-scope fixture (L00 ×10, L02 family, L03). Captured from the **pre-change tree** and committed before any schema change (D6/M2 FIX). |
| 1 | Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` | **Sub-task 1:** add `IrregularFrequencyMethod` enum; extend `SolverOptions` with `irregular_frequency_method`; add deprecation validator and `remove_irregular_frequencies + control_surface` combo guard. **Sub-task 2:** add `QTFOptions` (ints, Literal pass-through); add `SolverOptions.qtf` + `resolved_qtf()` accessor; add mutual-exclusion validator; **add C1 cross-field validator against `solve_type`**. **Sub-task 3:** add `FieldPointSpec`; add `OutputSpec.field_points`; **add `OutputSpec.detect_field_points_inside_bodies` (C2)**. Ensure `Literal` import present (M4 minor). Update `__all__`. |
| 2 | Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` | **Sub-task 1:** branch `_build_body_dict` on `irregular_frequency_method` (L254-269). **Sub-task 2:** inside the existing `_build_headings_section` conditional gate (L507-532), replace the `0/180` literals with `int(qtf.min_crossing_angle)` / `int(qtf.max_crossing_angle)`; inside the preserved `_build_qtf_section` solve_type gate (L572-600), replace hardcoded `"Both"` / `"Direct method"` with the Literal pass-through + Preferred mapping. **M3:** re-route `_build_general_section` (L414-451) through `resolved_qtf()`. **Sub-task 3:** read `DetectAndSkipFieldPointsInsideBodies` from `spec.outputs.detect_field_points_inside_bodies` (C2); extend `_build_outputs_section` (L544-555) with combined-key field-point emission; mirror in modular-mode path (L728). |
| 3 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_input_schemas.py` | Add: `IrregularFrequencyMethod` round-trip; `QTFOptions` round-trip; flat → nested alias migration; mutual-exclusion errors; **C1 cross-field validator tests**; `FieldPointSpec` parse + validation; new `detect_field_points_inside_bodies` round-trip. Preserve all existing fixture tests unchanged. |
| 4 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_backend.py` | Extend `TestSolverSettingsMapping` with tests listed in §TDD (irregular-freq × 3 methods + legacy migrations + unset default + mutex; QTF × 3 load-calc methods + crossing-angle override + gate-preservation + `_build_general_section` compat). Extend `TestOrcaWaveBackendModularMode` with field-points-in-`08_outputs.yml` assertion. |
| 5 | Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` | **Byte-identity regression gate**: `@pytest.mark.parametrize` over `enumerate_byte_identity_fixtures()` (imported from benchmarks helper); each case asserts `backend.render(spec) == open(golden_path_for(spec), 'rb').read()` (token-level, not semantic). Add two forward-compat cases exercising new fields. |
| 6 | Update | `docs/plans/README.md` | Add index entry for this plan. |

**Ordering rationale:** Sub-task 0 lands first so the byte-identity gate exists and is verified-empty before any schema change. Then Sub-task 1 (lightest — enum + 3-way branch). Then Sub-task 2 (gate-aware de-hardcoding + cross-field validator). Then Sub-task 3 (greenfield model + combined-key emission + new `detect_field_points_inside_bodies` field). Each sub-task is independently landable; all four must ship to close #501.

---

## TDD Test List

<!-- One row per test. Tests for Sub-task 0 must pass on the UNMODIFIED tree. -->

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| **test_benchmark_infrastructure_generates_golden_from_pre_change_tree** | **C3 FIX** — golden corpus reproduces on unmodified tree | pre-change HEAD + enumerated fixture list | every golden matches `backend.render(spec)` bit-exact |
| **test_enumerate_byte_identity_fixtures_covers_l00_sub_specs** | **C4 FIX** — corpus enumeration includes all 10 L00 sub-specs | fixture enumeration helper | `len(L00-matches) == 10`; L02 family present; L03 present |
| test_irregular_frequency_method_none | enum `none` emits `BodyAddInteriorSurfacePanels=No` | spec with method=`none` | no `BodyInteriorSurfacePanelMethod` emitted |
| test_irregular_frequency_method_interior_panels | enum `interior_panels` preserves legacy emission | spec with method=`interior_panels` | `BodyAddInteriorSurfacePanels=Yes` + `Triangulation method` |
| test_irregular_frequency_method_control_surface | enum `control_surface` uses body's control_surface mesh | spec with body `control_surface` + method=`control_surface` | existing control-surface emission fires |
| test_control_surface_method_without_mesh_fails | schema validator requires mesh when method=`control_surface` | spec with method=`control_surface`, no body control_surface | `ValidationError` |
| test_remove_irregular_frequencies_legacy_true | legacy `True` migrates to `interior_panels` | spec with `remove_irregular_frequencies=true` only | `irregular_frequency_method=interior_panels` + DeprecationWarning |
| test_remove_irregular_frequencies_legacy_false | legacy `False` migrates to `none` | spec with `remove_irregular_frequencies=false` only | `irregular_frequency_method=none` + DeprecationWarning |
| **test_remove_irregular_frequencies_legacy_unset** | **H1 FIX** — unset-both-fields case | spec omits both fields | `irregular_frequency_method=interior_panels` (field default); default emission unchanged |
| test_irregular_frequency_mutual_exclusion | setting both flat + enum raises | spec with both fields set | `ValidationError` |
| **test_remove_irregular_frequencies_plus_control_surface_combo_rejected** | **M4 minor** — legacy + new enum together is ambiguous | spec with `remove_irregular_frequencies=true` + `irregular_frequency_method=control_surface` | `ValidationError` |
| test_qtf_crossing_angle_override | crossing-angle fields emit inside the gate | `QTFOptions(enabled=True, min=30, max=150)` + QTF solve_type | backend YAML has `30`/`150` (int tokens, not `30.0`) |
| **test_qtf_crossing_angle_not_emitted_when_solve_type_nonqtf** | **C1 FIX** — the gate holds; overrides are rejected upstream | spec with `enabled=True` + `solve_type="potential_and_source"` | `ValidationError` at schema load (no silent-drop path) |
| **test_qtf_crossing_angle_not_emitted_when_qtf_disabled** | **C1 FIX** — gate preserved when QTF is off | spec with `enabled=False` + non-QTF solve_type | YAML has no `QTFMinCrossingAngle`/`QTFMaxCrossingAngle` keys |
| **test_qtf_enabled_raises_when_solve_type_nonqtf** | **C1 FIX** — explicit guard test | `QTFOptions(enabled=True)` + `solve_type=potential_and_source` | `ValidationError` |
| test_qtf_load_calc_method_direct | `"Direct"` → `QTFCalculationMethod=Direct` | `QTFOptions(load_calculation_method="Direct")` + QTF solve_type | `QTFCalculationMethod=Direct`, `Preferred=Direct method` |
| test_qtf_load_calc_method_indirect | `"Indirect"` → `QTFCalculationMethod=Indirect` | `QTFOptions(load_calculation_method="Indirect")` + QTF solve_type | `QTFCalculationMethod=Indirect`, `Preferred=Indirect method` |
| test_qtf_load_calc_method_both | `"Both"` preserves today's default | `QTFOptions(load_calculation_method="Both")` + QTF solve_type | `QTFCalculationMethod=Both`, `Preferred=Direct method` |
| test_qtf_legacy_flat_alias | flat `qtf_calculation: true` migrates to nested | spec with flat fields only | `resolved_qtf().enabled=True` + period bounds mapped + DeprecationWarning |
| test_qtf_mutual_exclusion | flat + nested both set raises | spec with `qtf_calculation` and `qtf:` | `ValidationError` |
| **test_build_general_section_unchanged_under_flat_compat** | **M3 FIX** — downstream consumer still byte-identical under compat shim | spec with flat `qtf_calculation=true`, no nested `qtf:` | `_build_general_section` output byte-identical to pre-change |
| test_field_points_emit_combined_key | non-empty field_points emits combined X/Y/Z arrays | `OutputSpec(field_points=[FieldPointSpec(name="deck", points=[(1,2,3),(4,5,6)])])` | YAML has `"FieldPointX, FieldPointY, FieldPointZ": [[1,4],[2,5],[3,6]]` |
| **test_detect_field_points_inside_bodies_default_preserves_yes** | **C2 FIX** — default `True` renders `"Yes"` | `OutputSpec()` with defaults | backend YAML has `DetectAndSkipFieldPointsInsideBodies: Yes` (unchanged from pre-change) |
| **test_detect_field_points_inside_bodies_false_renders_no** | **C2 FIX** — explicit override works | `OutputSpec(detect_field_points_inside_bodies=False)` | backend YAML has `DetectAndSkipFieldPointsInsideBodies: No` |
| test_field_points_modular_mode | field points appear in 08_outputs.yml in modular mode | spec with field_points, modular mode | `08_outputs.yml` contains combined key |
| **test_byte_identical_fixtures** (parametrized) | **C3/C4 FIX — critical regression gate** — every in-scope fixture unchanged after #501 lands | every spec.yml returned by `enumerate_byte_identity_fixtures()` | `backend.render(spec) == read_bytes(golden_path_for(spec))` |

---

## Acceptance Criteria

- [ ] **AC-A (Sub-task 0 first)** Benchmark-infrastructure test passes on the **unmodified tree** and goldens are committed before any schema edit: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/benchmarks/test_benchmark_infrastructure.py -v` (C3/M2 FIX).
- [ ] **AC-B (byte-identity mechanism — specified, not executed now)** After schema changes land, the parametrized byte-identity test `test_byte_identical_fixtures` passes for every path returned by `enumerate_byte_identity_fixtures()` (≥10 L00 sub-specs + L02 family + L03). Pass criterion: `bytes(backend.render(spec)) == Path(golden_path_for(spec)).read_bytes()` — token-level, not semantic. No numeric tolerance; any drift fails. Command at landing: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py::test_byte_identical_fixtures -v` (C3/C4/M2/M1 FIX). **This plan does NOT execute this gate — it specifies the mechanism.**
- [ ] **AC-C (C1 gate preservation)** The three dedicated C1 tests all pass: `test_qtf_crossing_angle_not_emitted_when_solve_type_nonqtf`, `test_qtf_crossing_angle_not_emitted_when_qtf_disabled`, `test_qtf_enabled_raises_when_solve_type_nonqtf`.
- [ ] **AC-D (H1 default-preservation)** `test_remove_irregular_frequencies_legacy_unset` passes and no DeprecationWarning is emitted on the unset-both-fields path (the common legacy case).
- [ ] **AC-E (L1 manual cite)** `QTFOptions.load_calculation_method` includes an in-code comment citing the OrcaWave User Manual section enumerating `Direct` / `Indirect` / `Both`.
- [ ] All new schema tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_input_schemas.py -v`
- [ ] All new backend tests pass: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/test_orcawave_backend.py -v`
- [ ] Full diffraction suite green: `cd digitalmodel && uv run pytest tests/hydrodynamics/diffraction/ -v`
- [ ] No regressions elsewhere: `cd digitalmodel && uv run pytest tests/orcawave/ -v`
- [ ] `IrregularFrequencyMethod`, `QTFOptions`, `FieldPointSpec`, and the new `OutputSpec.detect_field_points_inside_bodies` field exported via `input_schemas.__all__`; `Literal` import present.
- [ ] DeprecationWarnings emitted for flat `qtf_calculation` / explicit `remove_irregular_frequencies` usages (not errors), and NOT emitted on the unset-both-fields path.
- [ ] `docs/plans/README.md` updated with this plan.
- [ ] Review artifacts (r2) posted to `scripts/review/results/` — this plan needs its own review; r1's review does not apply.

---

## Adversarial Review Summary

<!-- r2 has not been reviewed yet. Do not populate until a fresh cross-review completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | _(pending r2 adversarial review)_ |
| Codex | APPROVE / MINOR / MAJOR | _(pending r2 adversarial review)_ |
| Gemini | APPROVE / MINOR / MAJOR | _(pending r2 adversarial review)_ |

**Overall result:** PENDING — fresh review of r2 required.

Revisions made based on r1 + 2nd-pass reviews: see §Revision Notes (r2) at top.

---

## Risks and Open Questions

- **Risk — backward compatibility is load-bearing.** Sub-task 0's golden corpus (L00 ×10 + L02 family + L03) is the sole defense against silent back-compat breaks. The corpus is frozen before any schema edit and diffed byte-for-byte. Any drift fails.

- **Risk — `control_surface` method requires a mesh file but schema can only validate string presence.** Actual mesh-file existence is #500's pre-flight territory. This plan validates `body.control_surface` is populated; does NOT verify the file exists on disk.

- **Risk — field-points combined-key whitespace.** The combined key `"FieldPointX, FieldPointY, FieldPointZ"` is a comma-key convention. Modular-mode writes via PyYAML/Ruamel may normalize whitespace and break OrcaWave's parser. Byte-identity test asserts the exact key form.

- **Risk — QTF load-calculation-method semantics still unverified externally.** The L1 remediation (pass-through `Literal["Direct", "Indirect", "Both"]`) avoids the translation layer but still assumes these three strings are the complete enumeration. Reviewer must confirm against the OrcaWave User Manual before sub-task 2 lands (see AC-E).

- **Risk — `detect_field_points_inside_bodies` boolean-to-string mapping.** The emission is a string literal `"Yes"` / `"No"`, not a bool. The test `test_detect_field_points_inside_bodies_default_preserves_yes` asserts the exact string form. If OrcaWave's YAML reader accepts other casings, the test is stricter than necessary — that is intentional to keep byte-identity.

- **[TRADEOFF C1 — FOR USER] — behavior when `QTFOptions.enabled=True` meets non-QTF `solve_type`.** This plan chooses option (a): **raise `ValidationError`** at schema load. Alternatives considered: (b) auto-upgrade `solve_type` silently (rejected — surprising side effect); (c) keep `enabled` informational and drop overrides silently (rejected — that is the defect we are fixing). **Decision point: accept (a) strict validation, or request an alternative?**

- **[TRADEOFF — FOR USER] — enum conversion default-value migration strategy.** This plan keeps `remove_irregular_frequencies: bool | None = None` as a deprecated alias. Alternative: remove the flat field entirely (clean, but breaks every existing spec.yml that sets it). **Decision point: proceed with compat-preserving migration, or bite the bullet with immediate fixture migration?**

- **[TRADEOFF — FOR USER] — QTF config scope: minimum-viable vs. full parity.** MVP covers the five fields in the issue body. Full Orcina QTF parity would add: `QTFFrequencyTypes`, `QTFHeadingPairs`, `QTFTruncationMethod`, per-body `QTFContributions`. **Decision point: ship MVP now and defer, or expand scope here?** Intel recommends MVP.

- **[TRADEOFF — FOR USER] — `FieldPointSpec` attachment point.** Plan uses `OutputSpec.field_points` (semantic cohesion with `detect_field_points_inside_bodies`). Alternative: top-level `DiffractionSpec.field_points` (mirrors `free_surface_zone`). **Decision point: OutputSpec (recommended) vs. top-level?**

- **Open — per-group `detect_inside_bodies` vs. global switch.** OrcaWave likely honors only the global flag. `FieldPointSpec.detect_inside_bodies` is informational/validated; schema may warn when per-group values conflict with the global `OutputSpec.detect_field_points_inside_bodies`.

- **Open — should `QTFOptions` / `FieldPointSpec` / `IrregularFrequencyMethod` live in their own module?** `input_schemas.py` is 789 lines; splitting is out of scope for #501 — flag as housekeeping follow-up.

- **Open — `body` vs. `vessel` naming for the control-surface attachment point** (2nd-pass minor). Intel and schema use `BodySpec.control_surface`; some OrcaWave docs use "vessel". This plan uses `body` throughout to match the existing code; flag as a doc-cleanup follow-up if the user prefers `vessel` terminology.

---

## Complexity: T2

**T2** — four coordinated sub-tasks (benchmarks infrastructure + three orthogonal schema/backend extensions) across two source files and three test files, plus a new benchmarks subpackage. Two of the three features (irregular-freq, QTF) have emission paths already present; work is enum-ification, de-hardcoding, and adding the C1 cross-field validator. Field-points is the only greenfield addition. Estimated: ~140 lines schema + ~70 lines backend + ~120 lines tests + ~50 lines benchmarks helper + ~12 golden files. Backward-compat gate (byte-identical L00 ×10 / L02 family / L03 YAML) is well-defined, its infrastructure is built by Sub-task 0, and the mechanism is specified (but not executed by this plan). Four distinct sub-tasks with ordering dependencies + explicit cross-field validator work drive this above T1; absence of new external-tool integration, cross-repo work, or architectural refactor keeps it below T3.
