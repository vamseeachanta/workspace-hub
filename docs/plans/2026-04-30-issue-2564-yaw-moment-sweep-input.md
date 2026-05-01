# Plan for #2564: feat(naval-arch): yaw moment sweep input for rudder cases

> **Status:** completed — implemented in `digitalmodel` commit [`0db57cd564720431213ee659cb1787a55683e922`](https://github.com/vamseeachanta/digitalmodel/commit/0db57cd564720431213ee659cb1787a55683e922); #2564 closed with `status:done` on 2026-04-30.
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2564
> **Fresh review artifact target:** `scripts/review/results/2026-04-30-plan-2564-claude.md` | `...-codex.md` | `...-gemini.md` | `...-disagreement.md`

---

## Resource Intelligence Summary

### Repository boundary and workflow state

| Concern | Repository | Decision |
|---|---|---|
| Governance issue and plan | `workspace-hub` (`https://github.com/vamseeachanta/workspace-hub.git`) | Issue #2564, plan file, plan index, issue comment, labels, and review artifacts live here. |
| Implementation | nested `digitalmodel` (`https://github.com/vamseeachanta/digitalmodel.git`) | Source, tests, sample YAML, docs, and implementation commit/test evidence live in `digitalmodel/`. |
| Cross-repo sequence | both | Commit/push `workspace-hub` plan/index/review artifacts first so remote reviewers can retrieve them; after user approval, implement/commit/push `digitalmodel` artifacts and link the commit/test evidence back to #2564. |

This is intentionally a cross-repo **governance + implementation** task, not a multi-repo architecture change. Implementation remains blocked until issue #2564 has `status:plan-approved` from explicit user approval.

### Existing code and package facts

| Evidence | Finding | Plan consequence |
|---|---|---|
| `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` | Existing rudder helpers: `rudder_lift_coefficient(...)` and `rudder_normal_force(velocity_m_s, rho_kg_m3, rudder_area_m2, rudder_span_m, rudder_angle_deg, behind_hull=True)`. The scalar lift coefficient is proportional to `math.sin(delta_rad)` and the module docstring names the Whicker & Fehlner lift model. | Reuse `rudder_normal_force`; do not duplicate the rudder-force formula. Call it with **keyword arguments** to avoid positional scrambling. |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Does not export `rudder_normal_force` / `rudder_lift_coefficient`. | New `yaw_moment.py` should deep-import from `maneuverability.py`; optionally export only new public yaw-moment helpers. |
| `digitalmodel/tests/naval_architecture/` | Existing naval-architecture test directory with maneuverability/compliance tests. | Add focused `test_yaw_moment_sweep.py` here. |
| `digitalmodel/pyproject.toml` | Setuptools packages are discovered from `src`; package data must live inside `src/digitalmodel/...` to be `importlib.resources`-addressable. Pytest starts with `filterwarnings = ["error", ...]` but explicitly ignores `UserWarning`, `DeprecationWarning`, and `PendingDeprecationWarning`. | Put sample YAML inside the package tree and add package-data coverage; avoid unexpected warning classes; do not overstate deprecation risk. |
| Current gaps | No `yaw_moment.py`, no yaw-moment tests, no yaw-moment sample YAML, no output writer. | Implement a bounded new module plus sample/data/tests/docs after approval. |

### Document-intelligence / standards retrieval

| Source | Evidence used | Plan implication |
|---|---|---|
| `docs/document-intelligence/README.md` | Identifies canonical registries: `data/document-index/index.jsonl`, `standards-transfer-ledger.yaml`, `code-registry.yaml`, and Naval Architecture wiki. | Use these as retrieval entry points before implementation. |
| `data/design-codes/code-registry.yaml` | No formal maneuvering/yaw-moment class-rule code was identified for this preliminary calculation. | Do not claim class-rule or standards compliance. |
| `data/document-index/standards-transfer-ledger.yaml` | Searched for maneuver/rudder/yaw/ship/SNAME/IMO terms; no directly applicable transferred design standard for this calculation was identified. | The strict `Citation` schema is not triggered by a standards-derived numeric constant in the planned yaw-moment wrapper. |
| `data/document-index/online-resource-registry.yaml:1905+` | Contains USNA EN400 / naval architecture online resource context. | Background context only unless a formula/constant is explicitly adopted. |
| `data/document-index/research-literature-report.md:143+` | Hydrodynamics/maneuvering literature context includes OpenProp, four-quadrant maneuvering, Wageningen resources. | Future fidelity upgrades may add hull/propeller/rudder interaction; out of scope here. |
| `knowledge/wikis/naval-architecture/wiki/index.md` | Lists PNA Vol. III, USNA EN400, Practical Ship Hydrodynamics, Marine Hydrodynamics, Basic Ship Theory. | Source index/background; do not fabricate a `Citation` target without required frontmatter fields. |

### /mnt/ace raw-reference review

Detailed addendum: `docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md`.

LLM-wiki ingestion completed on 2026-04-30 under `knowledge/wikis/naval-architecture/wiki/`; validation returned `llm_wiki.py lint --wiki naval-architecture` = OK. Primary implementation anchors now include:

- `concepts/yaw-moment-rudder-sweep.md`
- `concepts/rudder-force-modeling.md`
- `concepts/maneuvering-coordinate-conventions.md`
- `concepts/maneuvering-validation-metrics.md`
- `concepts/environmental-yaw-moment-coefficients.md`
- `comparisons/yaw-moment-source-extraction-2026-04-30.md`

| Raw reference | Verified relevance | Use in #2564 |
|---|---|---|
| `/mnt/ace/O&G-Standards/SNAME/textbooks/Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability.pdf` | Controllability volume; text hits for turning ability, hydrodynamics of control surfaces, maneuvering trials/performance, rudder/control-device design, yaw sign-convention content. | Primary reference for controllability framework and sign/axis convention. |
| `/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf` | Chapter 5 ship manoeuvring; force coefficients; rudders; simple rudder estimates; rudder/propeller and rudder/hull interactions. | Practical source for first-cut rudder force/yaw-moment caveats and excluded interactions. |
| `/mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf` | McTaggart/ShipMo3D report; metadata and extracted text show hull maneuvering forces, rudder deflection forces, rudder-propeller interaction, `FNrudder`, turning-circle comparisons. | Implementation-oriented reference for future force decomposition and validation-style examples. |
| `/mnt/ace/O&G-Standards/SNAME/textbooks/USNA-EN400-Principles-Ship-Performance-2020.pdf` | Chapter 9 ship maneuverability; rudder dimensions, speed/rudder-angle dependence, slow-speed maneuverability below ~5 kn, DOF/yaw definitions. | Typical sample ranges, engineering explanation, and sanity checks. |
| `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` | Mathematical model, rudder forces, expressions for rudder forces, yawing equation. | Regulatory/design-guide context; do not claim ABS compliance. |
| `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 MSC Circ.1053 Explanatory Notes to Manoeuvrability.pdf` | Steady turning with yaw rate ψ, speed V, drift angle β, `R = V/ψ`; yaw-rate/rudder-angle relation; turning circle and zig-zag definitions. | External maneuverability metrics for future validation, not the first formula derivation. |
| `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Manoeuvringload.md` | Plain-text `fx, fy, fz, mx, my, mz` equations and Munk-moment/current-load double-counting warning. | Guardrail if future yaw models mix added-mass/current load terms with rudder moment. |

Plan consequence: keep #2564 bounded to preliminary rudder-induced yaw moment (`F_N × lever arm`) while adding stronger references for sign convention, caveats, and future extensions. Do not fabricate strict standards `Citation` objects for raw literature; use provenance metadata unless a standards-derived constant is adopted from a resolvable wiki page.

### Related issues

- `#2564` — current requested yaw-moment workflow and typical-ship sweep input.
- `#1317` — `WRK-1375: Maneuverability module — rudder forces and turning circle`; this work extends that rudder-force basis.
- `#1849` — naval architecture expansion epic; #2564 is a bounded calculation slice.

---

## Artifact Map

| Artifact | Path | Ownership / note |
|---|---|---|
| This plan | `docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md` | `workspace-hub`; must be committed/pushed before remote review can retrieve it |
| Plan index | `docs/plans/README.md` | `workspace-hub`; row must stay synchronized |
| Plan review artifacts | `scripts/review/results/2026-04-30-plan-2564-*.md` | `workspace-hub`; latest provider fanout artifacts; UNAVAILABLE is documented tool/capacity failure, not approval evidence |
| Tests | `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` | `digitalmodel`; write before implementation |
| Implementation | `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` | `digitalmodel`; new module with `# ABOUTME:` header |
| Existing rudder basis | `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` | Reused by keyword-argument deep import |
| Packaged sample YAML | `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` | Inside package tree so `importlib.resources.files("digitalmodel.naval_architecture.data")` is viable |
| Package-data update | `digitalmodel/pyproject.toml` | Add e.g. `digitalmodel = ["naval_architecture/data/*.yml"]` or equivalent tested configuration |
| Optional package export | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export new yaw-moment public helpers only if matching package style |
| Usage docs | `digitalmodel/docs/domains/marine-engineering/yaw-moment-sweep.md` | Units, sign convention, sample usage, output schema, chart interpretation, provenance |

---

## Deliverable

A TDD-backed `digitalmodel` yaw-moment sweep capability that:

1. Loads a packaged typical-ship YAML sample plus user-specified YAML paths.
2. Computes rudder normal force via `digitalmodel.naval_architecture.maneuverability.rudder_normal_force(...)` using keyword arguments.
3. Computes yaw moment about CG using `M_z = x_rudder_from_cg_m * normal_force_N` under a named coordinate/sign convention.
4. Produces in-memory rows and writes CSV, JSON, and required chart outputs with stable schema, units, sign-convention metadata, and literature/provenance metadata.
5. Generates review-ready charts for engineering interpretation: yaw moment vs rudder angle by speed, yaw moment vs speed by rudder angle, transverse normal force vs rudder angle by speed, and a speed/angle yaw-moment heatmap.
6. Documents scope: preliminary rudder-induced yaw moment only; not full MMG, IMO maneuvering, dynamic yaw response, or class-rule compliance.

### YAML/package-data decision

The sample input will live at:

```text
digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml
```

Rationale: reviewers verified `digitalmodel/config/...` at repository root cannot be found via `importlib.resources` because package discovery is rooted at `src`. Keeping the sample inside `src/digitalmodel/...` makes installed-package access testable. Implementation must add package-data coverage in `pyproject.toml` or verify the selected build backend includes the YAML.

Required access tests:

1. `test_load_packaged_typical_ship_yaml_with_importlib_resources` — uses `importlib.resources.files(...)` to load the packaged sample.
2. `test_load_user_yaml_from_explicit_path` — copies/loads a temp YAML path to ensure user-provided files remain supported.

### Input YAML contract

The packaged sample and user-provided input files must use a documented YAML shape like:

```yaml
case:
  id: typical_single_screw_ship
  description: Preliminary rudder-induced yaw moment sweep for a typical ship
vessel:
  name: Typical Ship
  length_between_perpendiculars_m: 180.0
  draft_m: 10.0
  displacement_t: 30000.0
rudder:
  area_m2: 20.0
  span_m: 5.0
  x_from_cg_m: -45.0
  behind_hull: false
sign_convention:
  axes: "+x forward, +y port, +z up"
  positive_yaw_moment: "bow_to_port"
  positive_force_direction: port
environment:
  rho_kg_m3: 1025.0
sweep:
  speeds:
    units: kn
    values: [0, 2, 5, 10, 15]
  rudder_angles_deg: [-35, -20, -10, 0, 10, 20, 35]
outputs:
  directory: results/yaw_moment_typical_ship
  tables: [csv, json]
  charts:
    enabled: true
    formats: [png, html]
    required:
      - yaw_moment_vs_rudder_angle_by_speed
      - yaw_moment_vs_speed_by_rudder_angle
      - normal_force_vs_rudder_angle_by_speed
      - yaw_moment_speed_angle_heatmap
```

Implementation must validate required top-level sections (`case`, `rudder`, `environment`, `sweep`, `outputs`) and reject ambiguous/unsupported speed units rather than silently assuming knots or m/s. `outputs.tables` controls CSV/JSON table writers; `outputs.charts.enabled` controls chart generation. A populated `outputs.charts.required` section with `enabled: false` is invalid, so there is no ambiguous `charts` token in the table format list. Use `KNOT_TO_M_PER_S = 0.514444` and `M_PER_S_TO_KNOT = 1 / 0.514444` for all conversions.

### Module split vs colocation decision

Create `yaw_moment.py` rather than adding this workflow directly to `maneuverability.py` because the deliverable includes YAML parsing, sweep orchestration, output writing, citation/provenance metadata, and packaged sample access. `maneuverability.py` remains the low-level hydrodynamic/rudder helper module; `yaw_moment.py` is the higher-level calculation/workflow surface that composes existing helpers.

---

## Citation and Provenance Compliance

### Strict calc-output `Citation` schema

`docs/standards/calc-output-citation.md` is scoped to **standards-derived numeric constants** and requires `code_id`, `publisher`, `revision`, `section`, and `wiki_path` fields that resolve to wiki frontmatter. This issue does not introduce a new standards-derived numeric constant in `yaw_moment.py`.

Therefore:

- Do **not** fabricate a strict `Citation` for Whicker & Fehlner research literature or for the basic mechanics relation `M_z = F_N * x`.
- Do **not** claim USNA EN400/PNA/class-rule citation unless implementation adopts a specific standards-derived value from a resolvable wiki page with required frontmatter.
- If implementation later adds a standards-derived coefficient/limit, then strict `Citation` emission becomes mandatory and must fail closed per the contract.

### Required provenance metadata for this issue

Even though the strict standards `Citation` schema is not applicable, outputs must still include non-schema provenance metadata:

```json
{
  "provenance": {
    "calculation": "rudder-induced yaw moment about CG",
    "yaw_moment_relation": "M_z = x_rudder_from_cg_m * normal_force_N",
    "force_source_module": "digitalmodel.naval_architecture.maneuverability.rudder_normal_force",
    "force_source_note": "Existing maneuverability module documents Whicker & Fehlner rudder lift model; no new standards-derived constants introduced here.",
    "positive_force_direction": "port",
    "scope_limitations": "Preliminary rudder-force lever-arm sweep; excludes hull/propeller/rudder interaction, drift, yaw inertia, MMG derivatives, and class-rule/IMO compliance."
  }
}
```

This provenance lives in JSON metadata and docs; it is intentionally separate from the strict standards `Citation` schema.

---

## Sign Convention Contract

### Precondition probe before writing load-bearing sign tests

Before implementing `rudder_yaw_moment`, write/run a small test or assertion against the existing force helper to establish current scalar sign behavior:

```python
force = rudder_normal_force(
    velocity_m_s=5.0,
    rho_kg_m3=1025.0,
    rudder_area_m2=20.0,
    rudder_span_m=5.0,
    rudder_angle_deg=10.0,
    behind_hull=False,
)
assert force > 0
```

If this precondition fails at HEAD, stop and revise the plan/sign convention before implementation. Do not silently invert signs.

### Named convention

- Ship-fixed axes: `+x` forward, `+y` port, `+z` upward.
- Positive yaw moment `+M_z`: bow turns to port (counterclockwise viewed from above).
- `x_rudder_from_cg_m`: rudder longitudinal position relative to CG; a stern rudder aft of CG is negative.
- Existing `rudder_normal_force` returns a signed scalar, not a documented ship-fixed transverse vector. The new wrapper must therefore expose an explicit computational sign mapping in configuration/metadata instead of claiming the source helper proves physical `+Y`.
- Packaged default mapping: `positive_force_direction: port` means positive scalar normal force is reported as positive transverse force `Y_N`; `positive_force_direction: starboard` means the wrapper multiplies the scalar by `-1` before moment calculation.
- For the packaged default stern rudder aft of CG (`x < 0`) and `positive_force_direction: port`, `M_z = x * Y`; therefore `+delta` produces negative `M_z` under the declared computational convention. This is a transparent sign convention, not a class-rule or literature claim.

Falsifiable required numeric test:

```text
velocity_m_s = 5.0
rho_kg_m3 = 1025.0
rudder_area_m2 = 20.0
rudder_span_m = 5.0
rudder_angle_deg = +10.0
x_rudder_from_cg_m = -45.0
behind_hull = False

Expected:
scalar_normal_force_N > 0
transverse_force_N > 0
yaw_moment_Nm < 0
yaw_moment_Nm == transverse_force_N * (-45.0)
```

Symmetry tests may be added, but they cannot replace the absolute sign tests.

---

## Pseudocode

```text
CSV_HEADERS = [
  "case_id",
  "speed_m_s",
  "speed_kn",
  "rudder_angle_deg",
  "rho_kg_m3",
  "rudder_area_m2",
  "rudder_span_m",
  "x_rudder_from_cg_m",
  "behind_hull",
  "scalar_normal_force_N",
  "transverse_force_N",
  "yaw_moment_Nm",
  "sign_convention",
]

REQUIRED_CHARTS = [
  "yaw_moment_vs_rudder_angle_by_speed",
  "yaw_moment_vs_speed_by_rudder_angle",
  "normal_force_vs_rudder_angle_by_speed",
  "yaw_moment_speed_angle_heatmap",
]
KNOT_TO_M_PER_S = 0.514444
M_PER_S_TO_KNOT = 1.0 / KNOT_TO_M_PER_S
CHART_BACKENDS = {"png": "matplotlib", "html": "plotly-self-contained-html"}

function validate_finite(name, value): reject NaN, +inf, -inf

function rudder_yaw_moment(...):
    validate finite velocity, angle, area, span, lever arm, density
    validate velocity_m_s >= 0
    validate rho_kg_m3 > 0
    validate rudder_area_m2 > 0 and rudder_span_m > 0
    scalar_force_N = rudder_normal_force(
        velocity_m_s=velocity_m_s,
        rho_kg_m3=rho_kg_m3,
        rudder_area_m2=rudder_area_m2,
        rudder_span_m=rudder_span_m,
        rudder_angle_deg=rudder_angle_deg,
        behind_hull=behind_hull,
    )
    transverse_force_N = scalar_force_N if positive_force_direction == "port" else -scalar_force_N
    yaw_moment_Nm = x_rudder_from_cg_m * transverse_force_N
    return typed result with scalar/transverse force values and metadata

function load_packaged_typical_ship_yaml():
    use importlib.resources.files("digitalmodel.naval_architecture.data")
    load yaw_moment_typical_ship.yml

function load_yaw_moment_input(path):
    parse YAML from explicit path
    validate case, vessel, rudder, environment, sweep, output sections
    validate supported speed units exactly: "kn" or "m/s"
    convert speed list from knots or m/s to m/s and include speed_kn in output rows
    validate rudder angles finite, density > 0, lever arm finite
    validate outputs.tables, outputs.charts.enabled, outputs.charts.formats, and outputs.charts.required against supported values
    return typed scenario object

function run_yaw_moment_sweep(config):
    for each speed in speeds_m_s and rudder_angle in rudder_angles_deg:
        append row with CSV_HEADERS fields
    return {"metadata": units/sign/provenance, "rows": rows}

function write_yaw_moment_results(result, output_path, formats):
    write CSV using exact CSV_HEADERS order
    write JSON with {"metadata", "provenance", "rows", "artifacts"}
    if charts requested: call write_yaw_moment_charts(result, output_path, chart_formats)
    return manifest containing generated artifact paths

function write_yaw_moment_charts(result, output_dir, chart_formats):
    create yaw moment vs rudder angle lines grouped by speed
    create yaw moment vs speed lines grouped by rudder angle
    create transverse normal force vs rudder angle lines grouped by speed
    create yaw moment heatmap with speed on one axis and rudder angle on the other
    write requested PNG via Matplotlib and self-contained HTML via Plotly
    validate generated PNG signature and HTML title/Plotly marker before returning
    return chart artifact paths keyed by REQUIRED_CHARTS
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` | TDD tests for sign, validation, package data, output schema, provenance, and sweep shape |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` | Calculation/workflow surface, YAML loader, output writers, chart manifest; include `# ABOUTME:` header |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/__init__.py` | Make sample-data directory resource-addressable if needed |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` | Packaged reusable typical-ship sample input with sweep/output/chart sections |
| Modify | `digitalmodel/pyproject.toml` | Add package-data coverage for `naval_architecture/data/*.yml`; respect warnings-as-errors |
| Modify if needed | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export new yaw-moment helpers only |
| Create | `digitalmodel/docs/domains/marine-engineering/yaw-moment-sweep.md` | Usage, units, sign convention, limitations, provenance |
| Update | `docs/plans/README.md` | Keep plan index status synchronized |

---

## TDD Test List

| Test name | What it verifies | Expected output |
|---|---|---|
| `test_existing_rudder_normal_force_positive_angle_precondition` | Existing helper scalar sign for `+10°` under `behind_hull=False` | `scalar_normal_force_N > 0`; if not, stop/replan |
| `test_yaw_moment_positive_angle_stern_rudder_declared_port_mapping` | Declared computational convention for `+delta`, stern rudder, `positive_force_direction=port` | `scalar_force_N > 0`, `transverse_force_N > 0`, `yaw_moment_Nm < 0`, `Mz = transverse_force_N * -45` |
| `test_yaw_moment_starboard_mapping_flips_transverse_force_and_moment` | Explicit sign-mapping switch is functional | same scalar force, opposite `transverse_force_N` and `yaw_moment_Nm` versus port mapping |
| `test_yaw_moment_zero_rudder_angle_is_zero` | zero angle result | force and moment are zero |
| `test_yaw_moment_scales_with_speed_squared` | dynamic pressure scaling | 10 m/s moment is 4× 5 m/s moment |
| `test_yaw_moment_uses_keyword_call_to_rudder_normal_force` | guards existing signature/order | mocked helper receives expected keyword names |
| `test_load_packaged_typical_ship_yaml_with_importlib_resources` | packaged sample accessible in source tree | sample loads from package resource |
| `test_packaged_yaml_in_built_distribution` | package-data claim survives build/install | temp installed wheel/sdist can load sample via `importlib.resources` |
| `test_load_user_yaml_from_explicit_path` | user path support | temp YAML loads and validates |
| `test_load_typical_ship_yaml_converts_knots` | speed unit conversion | `kn * 0.514444` |
| `test_sweep_cardinality_matches_grid` | full packaged sample grid | 5 speeds × 7 angles = 35 rows |
| `test_write_results_csv_schema` | exact CSV contract | headers exactly equal `CSV_HEADERS` order |
| `test_write_results_json_schema` | exact JSON contract | top-level `metadata`, `provenance`, `rows`, `artifacts` |
| `test_zero_speed_all_angles_are_zero_force_and_moment` | zero-speed branch because packaged sample includes 0 kn | all rows with `speed_m_s == 0` have zero force and yaw moment |
| `test_write_required_chart_manifest` | required chart contract | manifest includes all `REQUIRED_CHARTS` keys |
| `test_write_chart_files_png_or_html` | chart artifacts are created with stable names and real backends | PNG starts with PNG signature; HTML contains expected title and Plotly marker |
| `test_yaw_moment_heatmap_grid_shape` | heatmap matches speed × rudder-angle grid | matrix shape equals `len(speeds) × len(angles)` |
| `test_output_metadata_includes_units_and_sign_convention` | self-describing output | JSON metadata declares units; CSV uses unit-suffixed headers; sign convention states `+Mz bow-to-port` and `positive_force_direction` |
| `test_provenance_metadata_declares_non_standard_literature_basis` | avoids fake strict Citation | provenance has force-source note; no fabricated `code_id` for Whicker & Fehlner |
| `test_invalid_negative_speed_rejected` | invalid speed | `ValueError` |
| `test_invalid_density_rejected` | density positive/finite | `ValueError` for `rho <= 0`, NaN, inf |
| `test_invalid_rudder_angle_rejected` | angle finite | `ValueError` for NaN/inf |
| `test_invalid_rudder_geometry_rejected` | area/span positive | `ValueError` |
| `test_invalid_lever_arm_rejected` | lever arm finite | `ValueError` |

---

## Acceptance Criteria

- [ ] This plan and `docs/plans/README.md` index row are committed and pushed to `workspace-hub/main` before asking remote reviewers to approve retrievability.
- [ ] Issue #2564 has `status:plan-review` while under review and includes a comment linking the plan and review artifacts.
- [ ] Automated plan-review evidence target: no MAJOR findings from at least two substantive reviewers before treating automated review as approval support. If providers fail for tooling/capacity, document the failure and keep #2564 in `status:plan-review` for human/user review rather than implementation.
- [ ] Any MAJOR finding requires plan revision and fresh re-review; inline explanation alone cannot bypass the gate.
- [ ] User explicitly approves #2564 before implementation and label moves to `status:plan-approved`.
- [ ] Tests are written before implementation and pass from `digitalmodel/`: `uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py -v`.
- [ ] Packaging validation proves installed-package resource access, e.g. build a wheel/sdist via the repo-approved `uv` workflow, install into a temporary environment, and verify `importlib.resources.files("digitalmodel.naval_architecture.data")` can read `yaw_moment_typical_ship.yml`.
- [ ] Implementation reuses `rudder_normal_force` with keyword arguments; no duplicated rudder lift formula is introduced.
- [ ] Sign convention has precondition, declared force-direction mapping tests, and explicit metadata; implementation does not claim `rudder_normal_force` alone proves physical transverse direction.
- [ ] Validation rejects negative speed, nonpositive density, nonfinite density/angle/lever arm, and nonpositive rudder area/span.
- [ ] Packaged sample YAML loads via `importlib.resources`, and explicit user YAML paths also load.
- [ ] CSV output uses exact `CSV_HEADERS`; JSON output includes `metadata`, `provenance`, `rows`, and `artifacts`.
- [ ] Required chart outputs are generated with stable names and documented interpretation: yaw moment vs rudder angle by speed, yaw moment vs speed by rudder angle, transverse normal force vs rudder angle by speed, and speed/angle yaw-moment heatmap.
- [ ] Chart backend is pinned to installed/base dependencies: Matplotlib for PNG and Plotly self-contained HTML for HTML. PNG tests verify file signature, not just non-empty bytes; HTML tests verify expected Plotly markup/title.
- [ ] Usage docs state units, YAML schema, sign convention, output schema, chart interpretation, limitations, and provenance.
- [ ] `digitalmodel` implementation commit/test evidence is linked back to #2564 before closeout.

---

## Adversarial Review Summary

| Provider | Latest verdict | Findings addressed in this revision |
|---|---|---|
| Claude | MAJOR | Corrected YAML location into package tree; removed unsupported multi-provider evidence claims; added sign precondition, module split rationale, fixed review gate, fixed CSV headers, noted warnings-as-errors. |
| Codex | MAJOR | Added push/retrievability gate, issue comment/label gate, strict MAJOR re-review requirement, and corrected citation/provenance treatment. |
| Gemini | MAJOR | Moved YAML under `src/digitalmodel/...`; separated strict standards `Citation` from research-literature provenance; required keyword arguments for existing helper signature. |
| 2026-04-30 provider fanout | UNAVAILABLE / UNAVAILABLE / UNAVAILABLE | Provider/tooling failures only: Claude session hook timeout, Codex stdin timeout, Gemini 429 capacity. No substantive provider finding was returned. |
| 2026-04-30 Hermes governance review | Conditional / no calculation-schema blocker | Confirmed `status:plan-review` is defensible as a visible holding state for a blocked plan-review packet, but not as proof automated review passed. |

**Overall result:** #2564 is ready for user review as a `status:plan-review` packet: scope, YAML input, methodology, outputs, charts, tests, provenance, resource-intelligence anchors, and implementation block are explicit. Implementation remains blocked until user approval; automated provider review should be retried when provider/tooling capacity recovers or user explicitly overrides that evidence gap.

---

## Risks

- **Sign convention mismatch:** If the precondition probe shows the existing scalar sign is not compatible with the desired convention, stop and revise this plan before coding.
- **Preliminary fidelity:** This is not a full MMG/IMO maneuvering model. Documentation and JSON provenance must state exclusions.
- **Packaging drift:** Package-data changes must be tested; resource access cannot rely on repository-root config files.
- **Warnings handling:** `pyproject.toml` starts with warnings-as-errors but ignores common user/deprecation warning classes; implementation should still avoid unexpected warning classes and keep tests explicit.
- **Provider review failures:** Capacity/tool failures are not approvals; they are documented evidence gaps. Keep the issue in `status:plan-review` for user review, retry automated review when capacity/tooling recovers, or proceed only with explicit user override/approval.

---

## Complexity: T2

**T2** — bounded engineering calculation/workflow with one new module, one test file, one packaged YAML sample, one docs page, and a package-data update. Governance artifacts span `workspace-hub`; implementation artifacts stay in `digitalmodel`.
---

## Implementation Closeout — 2026-04-30

| Evidence | Result |
|---|---|
| `digitalmodel` implementation commit | [`0db57cd564720431213ee659cb1787a55683e922`](https://github.com/vamseeachanta/digitalmodel/commit/0db57cd564720431213ee659cb1787a55683e922) |
| GitHub issue state | #2564 closed as completed with `status:done` |
| Targeted yaw-moment tests | `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py -q` → 21 passed |
| Regression slice | `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py -q` → 43 passed |
| Lint | `UV_NO_SYNC=1 uv run --with ruff ruff check src/digitalmodel/naval_architecture/yaw_moment.py tests/naval_architecture/test_yaw_moment_sweep.py src/digitalmodel/naval_architecture/__init__.py` → passed |
| Smoke artifact generation | 35 sweep rows, CSV/JSON tables, citation sidecar, artifact manifest, and all four required charts generated |
| Post-fix adversarial review | Hermes follow-up review verdict: APPROVE after package-data and chart-contract fixes |

Implemented artifacts in `digitalmodel`:

- `src/digitalmodel/naval_architecture/yaw_moment.py`
- `src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml`
- `src/digitalmodel/naval_architecture/data/__init__.py`
- `tests/naval_architecture/test_yaw_moment_sweep.py`
- `docs/domains/marine-engineering/yaw-moment-sweep.md`
- `pyproject.toml` package-data extension preserving existing subsea fixtures and adding the new naval-architecture YAML.

Next-calculation preparation is documented in `docs/session-handoffs/2026-04-30-yaw-moment-sweep-closeout-next-calculation.md`.

