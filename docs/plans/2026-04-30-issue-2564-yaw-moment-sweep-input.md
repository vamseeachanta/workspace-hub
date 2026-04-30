# Plan for #2564: feat(naval-arch): yaw moment sweep input for rudder cases

> **Status:** draft — MAJOR review remediation in progress; implementation blocked until clean re-review and user approval
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2564
> **Latest review artifacts:** `scripts/review/results/2026-04-29-plan-2564-claude.md` | `...-codex.md` | `...-gemini.md` | `...-disagreement.md`

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
| `digitalmodel/pyproject.toml` | Setuptools packages are discovered from `src`; package data must live inside `src/digitalmodel/...` to be `importlib.resources`-addressable. Pytest treats warnings as errors via `filterwarnings = ["error", ...]`. | Put sample YAML inside the package tree and add package-data coverage; avoid warning-prone APIs or filter explicitly in tests only with justification. |
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
| Plan review artifacts | `scripts/review/results/2026-04-29-plan-2564-*.md` | `workspace-hub`; commit/push as evidence |
| Tests | `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` | `digitalmodel`; write before implementation |
| Implementation | `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` | `digitalmodel`; new module with `# ABOUTME:` header |
| Existing rudder basis | `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` | Reused by keyword-argument deep import |
| Packaged sample YAML | `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` | Inside package tree so `importlib.resources.files("digitalmodel.naval_architecture.data")` is viable |
| Package-data update | `digitalmodel/pyproject.toml` | Add e.g. `digitalmodel = ["naval_architecture/data/*.yml"]` or equivalent tested configuration |
| Optional package export | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export new yaw-moment public helpers only if matching package style |
| Usage docs | `digitalmodel/docs/domains/marine-engineering/yaw-moment-sweep.md` | Units, sign convention, sample usage, provenance |

---

## Deliverable

A TDD-backed `digitalmodel` yaw-moment sweep capability that:

1. Loads a packaged typical-ship YAML sample plus user-specified YAML paths.
2. Computes rudder normal force via `digitalmodel.naval_architecture.maneuverability.rudder_normal_force(...)` using keyword arguments.
3. Computes yaw moment about CG using `M_z = x_rudder_from_cg_m * normal_force_N` under a named coordinate/sign convention.
4. Produces in-memory rows and writes CSV and JSON outputs with stable schema, units, sign-convention metadata, and literature/provenance metadata.
5. Documents scope: preliminary rudder-induced yaw moment only; not full MMG, IMO maneuvering, dynamic yaw response, or class-rule compliance.

### YAML/package-data decision

The sample input will live at:

```text
digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml
```

Rationale: reviewers verified `digitalmodel/config/...` at repository root cannot be found via `importlib.resources` because package discovery is rooted at `src`. Keeping the sample inside `src/digitalmodel/...` makes installed-package access testable. Implementation must add package-data coverage in `pyproject.toml` or verify the selected build backend includes the YAML.

Required access tests:

1. `test_load_packaged_typical_ship_yaml_with_importlib_resources` — uses `importlib.resources.files(...)` to load the packaged sample.
2. `test_load_user_yaml_from_explicit_path` — copies/loads a temp YAML path to ensure user-provided files remain supported.

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
- Existing `rudder_normal_force` positive scalar is treated as positive transverse force toward port (`+Y`) only after the precondition probe above confirms `+delta` returns a positive scalar.
- For a stern rudder aft of CG (`x < 0`), `M_z = x * Y`; therefore `+delta` produces negative `M_z` under this convention.

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
normal_force_N > 0
yaw_moment_Nm < 0
yaw_moment_Nm == normal_force_N * (-45.0)
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
  "normal_force_N",
  "yaw_moment_Nm",
  "sign_convention",
]

function validate_finite(name, value): reject NaN, +inf, -inf

function rudder_yaw_moment(...):
    validate finite velocity, angle, area, span, lever arm, density
    validate velocity_m_s >= 0
    validate rho_kg_m3 > 0
    validate rudder_area_m2 > 0 and rudder_span_m > 0
    normal_force_N = rudder_normal_force(
        velocity_m_s=velocity_m_s,
        rho_kg_m3=rho_kg_m3,
        rudder_area_m2=rudder_area_m2,
        rudder_span_m=rudder_span_m,
        rudder_angle_deg=rudder_angle_deg,
        behind_hull=behind_hull,
    )
    yaw_moment_Nm = x_rudder_from_cg_m * normal_force_N
    return typed result with values and metadata

function load_packaged_typical_ship_yaml():
    use importlib.resources.files("digitalmodel.naval_architecture.data")
    load yaw_moment_typical_ship.yml

function load_yaw_moment_input(path):
    parse YAML from explicit path
    validate vessel, rudder, environment, sweep, output sections
    convert speed list from knots or m/s to m/s
    validate rudder angles finite, density > 0, lever arm finite
    return typed scenario object

function run_yaw_moment_sweep(config):
    for each speed in speeds_m_s and rudder_angle in rudder_angles_deg:
        append row with CSV_HEADERS fields
    return {"metadata": units/sign/provenance, "rows": rows}

function write_yaw_moment_results(result, output_path, formats):
    write CSV using exact CSV_HEADERS order
    write JSON with {"metadata", "provenance", "rows"}
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` | TDD tests for sign, validation, package data, output schema, provenance, and sweep shape |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` | Calculation/workflow surface; include `# ABOUTME:` header |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/__init__.py` | Make sample-data directory resource-addressable if needed |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` | Packaged reusable typical-ship sample input |
| Modify | `digitalmodel/pyproject.toml` | Add package-data coverage for `naval_architecture/data/*.yml`; respect warnings-as-errors |
| Modify if needed | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export new yaw-moment helpers only |
| Create | `digitalmodel/docs/domains/marine-engineering/yaw-moment-sweep.md` | Usage, units, sign convention, limitations, provenance |
| Update | `docs/plans/README.md` | Keep plan index status synchronized |

---

## TDD Test List

| Test name | What it verifies | Expected output |
|---|---|---|
| `test_existing_rudder_normal_force_positive_angle_precondition` | Existing helper sign for `+10°` under `behind_hull=False` | `normal_force_N > 0`; if not, stop/replan |
| `test_yaw_moment_positive_angle_stern_rudder_absolute_sign` | Absolute convention for `+delta`, stern rudder | `normal_force_N > 0`, `yaw_moment_Nm < 0`, `Mz = Fn * -45` |
| `test_yaw_moment_negative_angle_stern_rudder_absolute_sign` | Opposite absolute sign | `normal_force_N < 0`, `yaw_moment_Nm > 0` |
| `test_yaw_moment_zero_rudder_angle_is_zero` | zero angle result | force and moment are zero |
| `test_yaw_moment_scales_with_speed_squared` | dynamic pressure scaling | 10 m/s moment is 4× 5 m/s moment |
| `test_yaw_moment_uses_keyword_call_to_rudder_normal_force` | guards existing signature/order | mocked helper receives expected keyword names |
| `test_load_packaged_typical_ship_yaml_with_importlib_resources` | packaged sample accessible after install/source import | sample loads from package resource |
| `test_load_user_yaml_from_explicit_path` | user path support | temp YAML loads and validates |
| `test_load_typical_ship_yaml_converts_knots` | speed unit conversion | `kn * 0.514444` |
| `test_sweep_cardinality_matches_grid` | full grid | 4 speeds × 7 angles = 28 rows |
| `test_write_results_csv_schema` | exact CSV contract | headers exactly equal `CSV_HEADERS` order |
| `test_write_results_json_schema` | exact JSON contract | top-level `metadata`, `provenance`, `rows` |
| `test_output_rows_include_units_and_sign_convention` | self-describing output | units and `+Mz bow-to-port` convention present |
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
- [ ] Plan-review rerun returns no MAJOR findings from at least two substantive reviewers. If Codex/Gemini fail for tooling/capacity, retry with a documented workaround or rerun later; a single-provider “available providers” result is not sufficient for this engineering-critical plan.
- [ ] Any MAJOR finding requires plan revision and fresh re-review; inline explanation alone cannot bypass the gate.
- [ ] User explicitly approves #2564 before implementation and label moves to `status:plan-approved`.
- [ ] Tests are written before implementation and pass from `digitalmodel/`: `uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py -v`.
- [ ] Implementation reuses `rudder_normal_force` with keyword arguments; no duplicated rudder lift formula is introduced.
- [ ] Sign convention has precondition and absolute positive/negative yaw-moment tests.
- [ ] Validation rejects negative speed, nonpositive density, nonfinite density/angle/lever arm, and nonpositive rudder area/span.
- [ ] Packaged sample YAML loads via `importlib.resources`, and explicit user YAML paths also load.
- [ ] CSV output uses exact `CSV_HEADERS`; JSON output includes `metadata`, `provenance`, and `rows`.
- [ ] Usage docs state units, sign convention, limitations, and provenance.
- [ ] `digitalmodel` implementation commit/test evidence is linked back to #2564 before closeout.

---

## Adversarial Review Summary

| Provider | Latest verdict | Findings addressed in this revision |
|---|---|---|
| Claude | MAJOR | Corrected YAML location into package tree; removed unsupported multi-provider evidence claims; added sign precondition, module split rationale, fixed review gate, fixed CSV headers, noted warnings-as-errors. |
| Codex | MAJOR | Added push/retrievability gate, issue comment/label gate, strict MAJOR re-review requirement, and corrected citation/provenance treatment. |
| Gemini | MAJOR | Moved YAML under `src/digitalmodel/...`; separated strict standards `Citation` from research-literature provenance; required keyword arguments for existing helper signature. |

**Overall result:** draft remains blocked until this revision is committed/pushed, issue governance is updated, and review is rerun cleanly.

---

## Risks

- **Sign convention mismatch:** If the precondition probe shows the existing scalar sign is not compatible with the desired convention, stop and revise this plan before coding.
- **Preliminary fidelity:** This is not a full MMG/IMO maneuvering model. Documentation and JSON provenance must state exclusions.
- **Packaging drift:** Package-data changes must be tested; resource access cannot rely on repository-root config files.
- **Warnings-as-errors:** `pyproject.toml` treats warnings as errors; YAML/path code must avoid deprecated APIs.
- **Provider review failures:** Capacity/tool failures are not approvals; engineering-critical approval needs at least two substantive no-MAJOR reviews or explicit user override.

---

## Complexity: T2

**T2** — bounded engineering calculation/workflow with one new module, one test file, one packaged YAML sample, one docs page, and a package-data update. Governance artifacts span `workspace-hub`; implementation artifacts stay in `digitalmodel`.
