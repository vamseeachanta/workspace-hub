# Plan for #2514: Schema for subsea cable, umbilical, and pipeline cross-sections

> **Status:** plan-approved
> **Complexity:** T3
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2514
> **Review artifacts:** `scripts/review/results/2026-04-27-plan-2514-claude.md` | `scripts/review/results/2026-04-27-plan-2514-codex.md` | `scripts/review/results/2026-04-27-plan-2514-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/sections.py` — production structural section-property wrapper around `sectionproperties` for CHS/RHS/I/angle/channel/custom sections. It returns `SectionProperties` values such as area, Ixx/Iyy, section modulus, J, and radii of gyration. This is useful downstream but should not be overloaded with cable/umbilical product semantics.
- Found: `digitalmodel/tests/test_sections.py` and `digitalmodel/tests/test_sectionproperties_integration.py` — existing tests validate CHS/RHS/I-section structural calculations against analytical/AISC values. New tests for this issue should be independent schema/validation tests, with optional future interop to `digitalmodel.sections` only for rigid-pipe equivalent CHS calculations.
- Found: `digitalmodel/src/digitalmodel/subsea/` — existing shared namespace with `__init__.py` and sibling subpackages: `catenary_riser`, `mooring_analysis`, `on_bottom_stability`, `pipeline`, `vertical_riser`, and `viv_analysis`. This issue must add `subsea/cross_sections/` without refactoring or renaming existing `digitalmodel.subsea.pipeline` or other sibling packages.
- Found: `digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/pipeline/pipeline.yml` — legacy pipeline config has a `crossection` block with Nominal_OD, Design_WT, corrosion allowance, internal/external fluids, material, and coating rows. It proves pipeline cross-section concepts exist, but spelling, units, and structure are not suitable as the canonical multi-family schema. New naming must use `cross_section`/`cross_sections`; the legacy spelling is read-only context, not a compatibility requirement for this issue.
- Found: `digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/umbilical_analysis/umbilical_analysis.yml` — umbilical analysis config covers installation phases and FE model placeholders, not a reusable product cross-section schema.
- Found: `digitalmodel/docs/domains/orcaflex/templates/pipelines/pipeline_hybrid/README.md` and `digitalmodel/docs/domains/orcaflex/templates/umbilicals/umbilical_hybrid/README.md` via repository file inventory — OrcaFlex templates exist as downstream consumers, but this issue creates neutral schema/fixtures first and does not bind directly to OrcaFlex export behavior.
- Found: `digitalmodel/pyproject.toml` already declares `pydantic>=2.7.0,<3.0.0`, `pint>=0.25.3,<1.0.0`, `pyyaml>=6.0.0,<7.0.0`, and `ruamel.yaml>=0.18.0,<1.0.0`.

### Standards and registries

| Standard / registry surface | Status | Source | Finding |
|---|---|---|---|
| DNV-ST-F101 | current | `data/design-codes/code-registry.yaml` | Registered as `Submarine Pipeline Systems`, disciplines `[pipeline, subsea]`, repos `[digitalmodel, doris]`; relevant to rigid pipeline family and provenance metadata. |
| API 5L / API RP 1111 entries | indexed | `data/document-index/standards-transfer-ledger.yaml` | Ledger contains pipeline standards, including API line pipe and offshore hydrocarbon pipeline entries; use as provenance anchors where examples cite line pipe/pressure-containment concepts. |
| Online resource registry | partial | `data/document-index/online-resource-registry.yaml` | Contains O&G/pipeline public data surfaces, but not yet a complete offshore cable/umbilical vendor catalogue. That broader catalogue remains #2513 scope. |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/concepts/subsea-cable-umbilical-cross-sections.md` — first-pass taxonomy covering offshore wind array/export cables, O&G umbilicals, rigid pipelines, and flexible pipe/riser layer families; explicitly recommends a family + layer schema and separates electrical/thermal/hydraulic functions from mechanical section properties.
- `knowledge/wikis/marine-engineering/wiki/comparisons/offshore-wind-oil-gas-cross-section-assessment.md` — prioritizes the implementation unit as a layer/component schema with representative fixtures for 66 kV inter-array cable, 220 kV HVAC export cable, steel-tube umbilical, and concrete-coated rigid pipeline; defers full flexible-pipe mechanics.
- `knowledge/wikis/marine-engineering/wiki/sources/offshore-cable-umbilical-cross-section-recon-2026-04-26.md` — source-backed reconnaissance for cable/umbilical/pipeline families; fixture dimensions in this issue must carry provenance and avoid hardcoded vendor defaults.

### Documents consulted

- Issue #2514 — defines schema scope, families, fixtures, validation constraints, provenance, and acceptance criteria.
- Related issue #2513 — source catalogue/backfill work; this plan depends on existing wiki anchors but does not need #2513 completed first.
- Related issue #2515 — report/demo generation; intentionally downstream of this schema.
- Related issue #2516 — flexible pipe/dynamic riser mechanics; explicitly deferred from first implementation except for extension hooks.
- Related issue #1498 — production `digitalmodel.sections` module; open issue body confirms structural-section property module scope and downstream JSON/dict output expectations.
- `docs/document-intelligence/README.md` and `docs/document-intelligence/data-intelligence-map.md` — confirm registry/ledger locations required for engineering/data-pipeline retrieval.

### Gaps identified

- No existing neutral `subsea.cross_sections` package for multi-family subsea product schemas.
- No typed model for ordered radial layers versus packed non-radial bundle components.
- No validator for required units, positive thickness/diameter, contiguous layer order, family names, duty classification, or provenance.
- No source-backed example fixtures for 66 kV inter-array cable, 220 kV HVAC export cable, steel-tube electro-hydraulic umbilical, power/optical hybrid umbilical, or concrete-coated pipeline.
- No fixture loader/serializer contract for YAML/JSON schema examples.
- No direct reporting/demo generation in this issue; that is #2515.
- No detailed flexible pipe/riser layer mechanics in this issue; that is #2516.

---

## Decisions Locked by Plan Review

1. **Schema technology:** Use Pydantic v2 because `digitalmodel/pyproject.toml` pins `pydantic>=2.7.0,<3.0.0`. Use `@field_validator`, `@model_validator(mode="after")`, `model_config = ConfigDict(...)`, and `ValidationError.errors()` assertions in tests.
2. **Unit policy v1:** Use controlled unit strings for v1 rather than free-form units. Minimum supported set: length `{mm, m, inch}`, density `{kg/m^3}`, voltage `{kV, V}`, pressure `{bar, MPa}`, temperature `{degC}`, force-per-length `{kN/m}`, mass-per-length `{kg/m}`. Comparable radial dimensions within one cross-section must use the same length unit unless conversion through Pint is explicitly implemented in the same patch. Add tests for unknown units and mixed-unit radial comparisons.
3. **Geometry policy v1:** Radial layers require enough geometry to derive a contiguous stack. Each layer must provide at least two of `{inner_diameter, outer_diameter, thickness}`; if all three are supplied, validate `outer_diameter == inner_diameter + 2 * thickness` within tolerance. Adjacent radial layers must be contiguous: previous `outer_diameter` equals next `inner_diameter` within tolerance. Gaps and overlaps are invalid unless explicitly represented as named layers.
4. **Provenance policy:** `Provenance.source_type` may include `wiki`, `standard`, `vendor_catalogue`, `project_assumption`, and `calculation`. If `source_type == calculation`, require `derived_from: list[str]` with at least one upstream `source_id`.
5. **Fixture provenance policy:** Every layer/component must cite a known source ID. Where dimensions are representative assumptions rather than directly source-derived, provenance must use `source_type: project_assumption` with a note.
6. **YAML/JSON I/O:** Use `ruamel.yaml` for YAML fixture load/dump because it is already declared and preserves round-trip ordering/comments better than PyYAML. Use stdlib `json` with `indent=2`, `sort_keys=True`, and `ensure_ascii=False` for JSON.
7. **Citation model boundary:** `Provenance` is a fixture-data schema and intentionally separate from any calc-output citation model. It should be easy to map to citation records later by `source_id`, but this issue does not retrofit calc-output citations.
8. **Public API:** `digitalmodel.subsea.cross_sections.__all__` must include `CrossSectionDefinition`, `RadialLayer`, `PackedComponent`, `Provenance`, `UnitValue`, `ValidationIssue`, `ValidationReport`, `validate_cross_section`, `load_cross_section_fixture`, and `dump_cross_section_fixture`.
9. **Package data:** If fixtures live under `src/digitalmodel/subsea/cross_sections/fixtures/`, update packaging metadata in `digitalmodel/pyproject.toml` or equivalent so `*.yml` fixture files are included in installed packages.
10. **Cross-repo topology:** Planning artifacts are in the `workspace-hub` repo. Implementation artifacts are in the nested `digitalmodel` repo. Implementation must use `git -C digitalmodel ...` or operate from `digitalmodel/`; do not stage digitalmodel implementation changes from workspace-hub root.

---

## Fixture Provenance Table

| Fixture | Required source anchors | Dimension status |
|---|---|---|
| `66kv_inter_array_cable.yml` | `knowledge/wikis/marine-engineering/wiki/sources/offshore-cable-umbilical-cross-section-recon-2026-04-26.md`; Prysmian 66 kV example noted there; Guide to Floating Offshore Wind 66 kV values noted there | Use source-derived voltage/conductor/insulation examples where cited; assumptions must be tagged `project_assumption`. |
| `220kv_hvac_export_cable.yml` | Same recon page; Guide to Floating Offshore Wind 220 kV export-cable values noted there | Use source-derived voltage/conductor/insulation examples where cited; assumptions must be tagged. |
| `steel_tube_electro_hydraulic_umbilical.yml` | Same recon page; SUT umbilical and Prysmian power/optical umbilical sources noted there | Use component roles/counts as representative unless source has exact exemplar; mark assumptions. |
| `power_optical_hybrid_umbilical.yml` | Same recon page; Prysmian power/optical umbilical source noted there | Plan-added fixture beyond the four examples in the issue body; included to validate the packed-component schema across a second service-role mix. Assumptions must be explicit. |
| `concrete_coated_pipeline.yml` | Same recon page; DNV-ST-F101 registry entry; Vallourec coating and Octal concrete-weight-coating sources noted there | Use source-backed layer taxonomy; representative coating thickness/density assumptions must be tagged. |

---

## Artifact Map

| Artifact | Repo | Path |
|---|---|---|
| This plan | workspace-hub | `docs/plans/2026-04-27-issue-2514-subsea-cross-section-schema.md` |
| Plan index | workspace-hub | `docs/plans/README.md` |
| Review artifacts | workspace-hub | `scripts/review/results/2026-04-27-plan-2514-{claude,codex,gemini}.md` |
| Review disagreement/synthesis | workspace-hub | `scripts/review/results/2026-04-27-plan-2514-disagreement.md` |
| Implementation package | digitalmodel | `src/digitalmodel/subsea/cross_sections/` |
| Public exports | digitalmodel | `src/digitalmodel/subsea/cross_sections/__init__.py` |
| Existing parent namespace docstring | digitalmodel | `src/digitalmodel/subsea/__init__.py` |
| Schema models | digitalmodel | `src/digitalmodel/subsea/cross_sections/schema.py` |
| Validation logic | digitalmodel | `src/digitalmodel/subsea/cross_sections/validation.py` |
| Fixture loader/serializer | digitalmodel | `src/digitalmodel/subsea/cross_sections/io.py` |
| Fixture examples | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/*.yml` |
| Package data metadata | digitalmodel | `pyproject.toml` or equivalent setuptools package-data config |
| Tests | digitalmodel | `tests/subsea/cross_sections/test_schema.py` |
| Validation tests | digitalmodel | `tests/subsea/cross_sections/test_validation.py` |
| Fixture/roundtrip tests | digitalmodel | `tests/subsea/cross_sections/test_fixtures.py` |
| Test package markers if discovery requires them | digitalmodel | `tests/subsea/__init__.py`, `tests/subsea/cross_sections/__init__.py` |

---

## Deliverable

A new additive `digitalmodel.subsea.cross_sections` package that defines typed, provenance-carrying schemas, validators, and example fixtures for offshore wind cables, O&G umbilicals, and rigid pipelines without binding the first implementation to OrcaFlex reporting or flexible-pipe mechanics.

---

## Scope Boundaries

### In scope now

- Family enum / controlled family names:
  - `offshore_wind_inter_array_cable`
  - `offshore_wind_hvac_export_cable`
  - `offshore_wind_hvdc_export_cable`
  - `steel_tube_electro_hydraulic_umbilical`
  - `thermoplastic_electro_hydraulic_umbilical`
  - `power_optical_hybrid_umbilical`
  - `rigid_pipeline_flowline`
- Duty metadata: `static`, `dynamic`, `transition`, plus optional water depth/design temperature/design pressure metadata where relevant.
- Ordered contiguous radial layer model for cables and pipelines.
- Packed component/bundle model for umbilicals.
- Materials/service roles/provenance on every layer/component.
- Unit-bearing scalar fields represented as `{value, unit}` objects with controlled units rather than implicit bare floats.
- Validation for unsupported family, missing/unknown/mixed units, negative/zero thickness or diameter where invalid, radial layer continuity, missing provenance, invalid duty, and invalid component count.
- YAML fixture examples for the five target families in the fixture provenance table.
- TDD tests written before implementation, split into schema/validation and fixture-bound slices.

### Out of scope now

- OrcaFlex export, report/dashboard generation, or HTML/PDF diagrams — #2515.
- Full flexible pipe/riser layer mechanics, annulus/collapse/fatigue models, or detailed unbonded flexible pipe calculations — #2516.
- Vendor-specific catalogue completeness — #2513.
- Replacing legacy pipeline configs in `infrastructure/base_configs` or rewriting OrcaFlex templates.
- Refactoring or renaming existing `digitalmodel.subsea.pipeline` or other `digitalmodel.subsea` sibling packages.
- Electrical ampacity, thermal rating, hydraulic pressure drop, or structural capacity calculations beyond schema fields and basic aggregate/metadata properties.

---

## Pseudocode

```text
class UnitValue(BaseModel):
    value: float
    unit: Literal["mm", "m", "inch", "kg/m^3", "kV", "V", "bar", "MPa", "degC", "kN/m", "kg/m"]
    validate numeric value is finite

class Provenance(BaseModel):
    source_id: str
    source_type: Literal["wiki", "standard", "vendor_catalogue", "project_assumption", "calculation"]
    citation: optional string
    url_or_path: optional string
    note: optional string
    derived_from: list[str] = []
    validate source_id is non-empty
    validate derived_from is non-empty when source_type == "calculation"

class RadialLayer(BaseModel):
    name, role, material
    inner_diameter: optional UnitValue
    outer_diameter: optional UnitValue
    thickness: optional UnitValue
    density: optional UnitValue
    provenance: Provenance
    validate at least two of inner_diameter, outer_diameter, thickness are present
    if all three present, validate OD == ID + 2 * thickness within tolerance
    validate all positive dimensions and dimension-compatible units

class PackedComponent(BaseModel):
    name, component_type, service_role, material
    count: int >= 1
    diameter: optional UnitValue
    wall_thickness: optional UnitValue
    pressure_rating: optional UnitValue
    voltage_rating: optional UnitValue
    provenance: Provenance
    validate count positive and geometry positive when provided

class DesignMetadata(BaseModel):
    water_depth: optional UnitValue
    design_temperature: optional UnitValue
    design_pressure: optional UnitValue
    voltage_class: optional UnitValue
    notes: optional string
    extra_metadata: dict[str, str] = {}

class ValidationIssue(BaseModel):
    code: str
    path: str
    message: str
    severity: Literal["error", "warning"]

class ValidationReport(BaseModel):
    is_valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    summary: str

class CrossSectionDefinition(BaseModel):
    id, name, family, duty, description
    design_metadata: DesignMetadata
    radial_layers: list[RadialLayer]
    packed_components: list[PackedComponent]
    provenance: list[Provenance]
    validate family/duty enum
    validate family requires radial_layers and/or packed_components as appropriate
    validate radial layers contiguous inner-to-outer within tolerance
    validate every layer/component has provenance
    validate every provenance.source_id is in fixture/source whitelist

function validate_cross_section(definition):
    parse object into CrossSectionDefinition
    run schema validators
    run family-specific validators
    return ValidationReport(is_valid, errors, warnings, summary)

function load_cross_section_fixture(path):
    read YAML via ruamel.yaml or JSON via stdlib json
    parse CrossSectionDefinition
    validate
    return definition

function dump_cross_section_fixture(definition, path):
    validate definition
    emit stable YAML/JSON preserving field order, units, and provenance
```

---

## Files to Change

| Action | Repo | Path | Reason |
|---|---|---|---|
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/__init__.py` | Public import surface with explicit `__all__`. |
| Modify | digitalmodel | `src/digitalmodel/subsea/__init__.py` | Existing namespace docstring: extend to mention `cross_sections`; do not remove existing riser/mooring/pipeline references. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/schema.py` | Pydantic v2 models for families, units, provenance, radial layers, packed components, design metadata, validation report, and definitions. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/validation.py` | Family-specific validators and normalized validation report. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/io.py` | YAML/JSON fixture load/dump helpers. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/66kv_inter_array_cable.yml` | Source-backed example fixture. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/220kv_hvac_export_cable.yml` | Source-backed example fixture. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/steel_tube_electro_hydraulic_umbilical.yml` | O&G umbilical packed-component fixture. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/power_optical_hybrid_umbilical.yml` | Plan-added hybrid umbilical fixture to validate second service-role mix. |
| Create | digitalmodel | `src/digitalmodel/subsea/cross_sections/fixtures/concrete_coated_pipeline.yml` | Rigid pipeline radial-layer fixture. |
| Modify | digitalmodel | `pyproject.toml` or package-data config | Ensure fixture `*.yml` files ship in installed package. |
| Create | digitalmodel | `tests/subsea/cross_sections/test_schema.py` | TDD tests for successful parsing/model construction/public imports. |
| Create | digitalmodel | `tests/subsea/cross_sections/test_validation.py` | TDD tests for invalid units, negative dimensions, bad family, layer gaps/overlaps, missing provenance. |
| Create | digitalmodel | `tests/subsea/cross_sections/test_fixtures.py` | TDD tests that shipped fixtures load, validate, and roundtrip. |
| Create if needed | digitalmodel | `tests/subsea/__init__.py`, `tests/subsea/cross_sections/__init__.py` | Only if pytest discovery/import checks show nested tests need package markers. |
| Update | workspace-hub | `docs/plans/README.md` | Add/update this plan in the planning index. |

---

## TDD Slice Plan

1. **Pre-check slice:** confirm nested pytest discovery/import behavior and packaging backend from `digitalmodel/pyproject.toml`. If required, include test package markers and package-data config in the first patch.
2. **Schema/validation RED slice:** write `test_schema.py` and `test_validation.py` first. Expected initial failure: `ImportError` for missing `digitalmodel.subsea.cross_sections` plus explicit validation failures once stubs exist.
3. **Fixture RED slice:** add fixture YAMLs and `test_fixtures.py` after schema contracts are visible. Expected initial failure: validation/report errors until loader/validator logic is complete.
4. **GREEN slice:** implement schema, validation, and I/O until all new tests pass.
5. **Regression slice:** run existing `sections.py` structural tests to confirm no accidental coupling/regression.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_public_api_exports_expected_names` | Stable downstream import surface | `from digitalmodel.subsea.cross_sections import ...` | all public names import |
| `test_unit_value_requires_unit` | Unit-bearing scalar cannot omit unit | `UnitValue(value=10)` | validation error |
| `test_unit_value_rejects_nonfinite` | NaN/inf values rejected | `value=float('nan')` | validation error |
| `test_unknown_unit_rejected` | Unit whitelist enforced | unit `mms` | validation error |
| `test_mixed_radial_length_units_rejected_or_converted` | Mixed comparable length units handled explicitly | layers in `mm` and `inch` | either normalized by Pint or rejected per implemented policy |
| `test_provenance_requires_source_id_and_type` | Source traceability is mandatory | empty provenance object | validation error |
| `test_calculation_provenance_requires_derived_from` | Calculation provenance cannot dead-end | `source_type=calculation`, empty `derived_from` | validation error |
| `test_radial_layer_requires_two_geometry_terms` | Geometry is not underdetermined | layer with only thickness | validation error unless chained/materialized by explicit implementation |
| `test_radial_layer_triplet_consistency_checked` | ID/OD/thickness over-specification is mathematically consistent | contradictory ID/OD/thickness | validation error |
| `test_radial_layer_gap_rejected` | Physical radial stack continuity enforced | gap between layer OD and next ID | validation error |
| `test_radial_layer_overlap_rejected` | Physical radial stack continuity enforced | next ID less than prior OD | validation error |
| `test_valid_66kv_inter_array_cable_layers` | Cable fixture supports radial electrical/mechanical layer stack | 66 kV fixture | parses with family `offshore_wind_inter_array_cable` and ordered layers |
| `test_valid_220kv_hvac_export_cable_layers` | Export cable has higher-voltage family/duty metadata and layers | 220 kV fixture | parses and validates |
| `test_valid_steel_tube_umbilical_packed_components` | Umbilical supports non-radial packed tubes/cables/fibres | steel-tube umbilical fixture | packed components include tube, electrical, fibre roles |
| `test_valid_power_optical_hybrid_umbilical` | Plan-added hybrid umbilical supports power/optical service roles | hybrid fixture | validates with components and provenance |
| `test_valid_concrete_coated_pipeline_layers` | Pipeline supports line pipe + coating + concrete radial layers | pipeline fixture | layers validate inner-to-outer |
| `test_invalid_unsupported_family_rejected` | Controlled family names enforced | family `generic_cylinder` | validation error |
| `test_negative_thickness_rejected` | Negative thickness invalid | radial layer thickness `-1 mm` | validation error |
| `test_zero_component_count_rejected` | Component count must be positive | packed component count `0` | validation error |
| `test_missing_component_provenance_rejected` | Every component must trace to source | component without provenance | validation error |
| `test_every_fixture_layer_provenance_resolves_to_known_source_page` | Fixture provenance is auditable | all fixtures | every source_id belongs to known whitelist/source table |
| `test_fixture_roundtrip_preserves_family_units_and_provenance` | Loader/dumper stable enough for downstream reports | any fixture | roundtrip family, units, provenance unchanged |
| `test_validation_report_has_stable_shape` | Validator returns actionable automation contract | fixture with multiple invalid fields | `is_valid`, `errors[]`, `warnings[]`, `code`, `path`, `message`, `severity` present |
| `test_fixture_package_data_available_after_install_metadata` | YAML fixtures are packaged | package-data config | fixtures discoverable through package resources |

---

## Acceptance Criteria

- [ ] Tests are written first in the two-slice TDD order above. Schema/validation tests initially fail for missing package/stubs; fixture-bound tests initially fail with validation/report errors after fixture files land.
- [ ] New `digitalmodel.subsea.cross_sections` package exists with typed Pydantic v2 schema models, validation report, and YAML/JSON load/dump helpers.
- [ ] Public imports from `digitalmodel.subsea.cross_sections` expose `CrossSectionDefinition`, `RadialLayer`, `PackedComponent`, `Provenance`, `UnitValue`, `ValidationIssue`, `ValidationReport`, `validate_cross_section`, `load_cross_section_fixture`, and `dump_cross_section_fixture`.
- [ ] Schema fixtures represent layer/component geometry, material, density, service role, duty, and provenance without hardcoded vendor defaults masquerading as universal values.
- [ ] Validation catches missing units, unknown units, non-finite values, negative thickness/diameter, invalid radial gaps/overlaps, unsupported family names, invalid component counts, and missing/invalid provenance.
- [ ] Fixtures cover: 66 kV inter-array cable, 220 kV HVAC export cable, steel-tube electro-hydraulic umbilical, plan-added power/optical hybrid umbilical, and concrete-coated rigid pipeline.
- [ ] Fixture `*.yml` files are included in package data so installed-package consumers can load them.
- [ ] New test command passes from `digitalmodel/`: `PYTHONPATH=src uv run pytest tests/subsea/cross_sections -q`.
- [ ] Existing structural section tests still pass from `digitalmodel/`: `PYTHONPATH=src uv run pytest tests/test_sections.py tests/test_sectionproperties_integration.py -q`.
- [ ] No OrcaFlex/reporting/flexible-pipe mechanics are added under this issue except documented extension hooks.
- [ ] Closeout comment cites consumed sources and defers report generation to #2515 and flexible-pipe mechanics to #2516.

---

## Execution Prerequisites

- Run implementation commands from `digitalmodel/` or with `git -C digitalmodel ...` because `digitalmodel` is a nested git repo.
- Keep workspace-hub plan/index/review artifacts separate from digitalmodel implementation commits.
- Before writing tests, check pytest discovery/package-marker needs for `tests/subsea/cross_sections/` and packaging metadata for `src/.../fixtures/*.yml`.
- Do not modify existing `digitalmodel.subsea.pipeline` implementation except by adding independent imports only if explicitly necessary; this plan does not require that.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings | Resolution |
|---|---|---|---|
| Claude | MAJOR | Existing `digitalmodel.subsea` namespace omitted; Pydantic v2 left unresolved; nested-repo commit topology omitted; TDD fixture ordering inconsistent; pytest discovery not prechecked. | Revised plan adds namespace inventory, Pydantic v2 decision, repo topology, TDD slice plan, pytest/package-data pre-checks. |
| Codex | MAJOR | Test commands violated `uv run` policy; schema tech unresolved; unit comparison/validation underspecified; fixture provenance too vague. | Revised plan uses `uv run`, locks Pydantic v2, adds unit policy/tests, and adds fixture provenance table. |
| Gemini | MINOR | YAML fixtures may not be packaged; unit validation too loose; geometry consistency checks incomplete; dependency verification needed. | Revised plan adds package-data requirement/test, unit whitelist, geometry triplet/continuity tests, and dependency decision. |

**Overall result:** Initial MAJOR findings addressed in this revision. No remaining known CRITICAL/HIGH blockers after edits; user approval is represented by the live GitHub `status:plan-approved` label and local `.planning/plan-approved/2514.md` marker, so this plan is ready for Lane B execution under the TDD implementation gate.

Review artifacts:
- `scripts/review/results/2026-04-27-plan-2514-claude.md`
- `scripts/review/results/2026-04-27-plan-2514-codex.md`
- `scripts/review/results/2026-04-27-plan-2514-gemini.md`

---

## Risks and Open Questions

- **Risk:** Fixture dimensions are typical/source-backed examples, not design defaults; every example must carry provenance and caveats.
- **Risk:** Existing repo has both `sections.py` structural section semantics and this new product-schema semantics. Naming must prevent users from treating cable/umbilical schema as a mechanical capacity calculator.
- **Risk:** Umbilical packing geometry is project/vendor-specific; first implementation should support components and provenance rather than overpromising exact spatial packing/clearances.
- **Open:** Whether to add JSON Schema export in the first implementation. Recommendation: only if trivial from Pydantic v2; otherwise defer to #2515/reporting or a future schema-publication issue.

---

## Follow-up Issues

- Existing #2513 — complete source/vendor/standards catalogue and enrich fixture provenance.
- Existing #2515 — generate reports/demos/visual comparison outputs from the schema.
- Existing #2516 — flexible pipe and dynamic riser cross-section mechanics follow-up.
- Candidate only: add OrcaFlex line-type property export after schema fixtures stabilize; do not include in #2514 unless user creates/approves a separate issue.

---

## Delegation Decision

Do not split #2514 into parallel execution streams for the first implementation. The schema, validator, fixtures, packaging metadata, and tests are tightly coupled and share the same small file set; parallel implementation would risk git contention. A single TDD implementation lane is preferred after approval.

---

## Complexity: T3

**T3** — cross-domain engineering schema spanning offshore wind cables, O&G umbilicals, and rigid pipelines; requires source-backed fixtures, validation design, tests, package-data handling, nested-repo topology discipline, and explicit scope boundaries against #2515/#2516. The implementation footprint is moderate, but the schema semantics and provenance requirements make it architectural rather than a simple T2 feature.
