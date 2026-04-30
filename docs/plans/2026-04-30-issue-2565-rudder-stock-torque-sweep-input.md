# Plan for #2565: feat(naval-arch): rudder stock torque sweep input for typical ship

> **Status:** completed — implemented in `digitalmodel` commit `3609b7dca981de3c6213413ddd6b404920b56f29` and closed after targeted validation + follow-up adversarial review APPROVE.
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2565
> **Review artifacts:** `scripts/review/results/2026-04-30-plan-2565-claude.md` | `...-codex.md` | `...-gemini.md` | `...-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code

| Evidence | Finding | Plan consequence |
|---|---|---|
| `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` | Existing `rudder_normal_force(...)` computes scalar rudder normal force and is already used by #2564. | Reuse this helper; do not rederive rudder-force formula in #2565. |
| `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` at commit `0db57cd564720431213ee659cb1787a55683e922` | #2564 added validated YAML loading, sweep execution, CSV/JSON/chart writing, provenance sidecar, and `scalar_normal_force_N` rows. | Extend by sibling module `rudder_stock_torque.py` or by narrow additive helpers; avoid changing #2564 sign/yaw semantics except where needed for shared utilities. |
| `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` | Typical-ship YAML already has vessel/rudder/environment/speed/rudder-angle grid and output chart contract. | Create `rudder_stock_torque_typical_ship.yml` that reuses the same grid and adds stock/center-of-pressure geometry. |
| `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` | Existing tests cover packaging, speed conversion, cardinality, zero cases, output tables/charts, and citation/provenance style. | Add parallel `test_rudder_stock_torque_sweep.py`; keep #2564 tests as regression slice. |
| `digitalmodel/pyproject.toml` package-data section | #2564 package-data work preserved existing subsea fixtures and added `naval_architecture/data/*.yml`. | Add new YAML inside the same package-data glob; test wheel contents so package data does not regress. |

**Gap:** no existing `rudder_stock_torque.py`, no packaged rudder-stock torque YAML, no tests/docs/output charts for steering/rudder-stock torque.

### Standards and references

| Source | Finding | Plan consequence |
|---|---|---|
| `.claude/rules/calc-citation-contract.md` and `docs/standards/calc-output-citation.md` | New standards-derived constants/formulas require citation sidecars; citation emits to sidecar and fails closed if strict `Citation` targets are introduced. | #2565 must emit provenance. If it introduces only user/YAML lever-arm geometry plus existing force helper, state no new standards-derived numeric constant was introduced. If any class-rule constants are added, implement strict citation objects. |
| `knowledge/wikis/naval-architecture/wiki/concepts/rudder-force-modeling.md` | Bertram §5.4.2 defines rudder normal-force/torque coefficient vocabulary; the page also records propeller/hull interaction caveats and PNA/USNA angle/stall context. | Current scope is preliminary force × lever-arm torque; do not absorb hull/propeller interaction or class-rule scantlings. Mention coefficient vocabulary in docs/provenance. |
| `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` | #2564 source-backed checks include speed-squared scaling, zero cases, non-tautological sign convention, and citation sidecar. | Reuse these checks for torque: torque should scale with scalar normal force and lever arm; zero speed/angle/arm cases must produce zero torque. |
| `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` | PNA and EN400 convention pages pin yaw/rudder sign conventions. | Rudder-stock torque must not silently inherit yaw sign; document torque sign separately as a torque about rudder stock opposing/applied by steering gear, with an explicit `positive_torque_direction` field. |
| `data/standards/promoted/naval-architecture/glossary.yaml` | Promoted SOLAS text defines steering gear vocabulary: auxiliary steering gear, power actuating system, rudder stock, maximum ahead service speed. | Use vocabulary/caveat context only. Do **not** claim SOLAS/class compliance or machinery sizing; keep this issue as preliminary torque envelope. |


### Engineering registry retrieval evidence

| Registry / entry point | Evidence found | Decision for #2565 |
|---|---|---|
| `docs/document-intelligence/README.md` | Confirms the operational retrieval surfaces: corpus index, `standards-transfer-ledger.yaml`, `code-registry.yaml`, maturity tracking, and naval-architecture wiki index. | Retrieval path is recorded here; implementation does not rely on ad-hoc search alone. |
| `data/document-index/standards-transfer-ledger.yaml` | Ledger contains 436 standards records, but targeted searches for `SOLAS`, `Principles-of-Naval`, `PNA`, `Vessel Maneuverability`, `rudder stock`, and `steering gear` returned no direct standards-ledger match for this bounded torque issue. | No standards-ledger implementation target is claimed. If later scope adds class/SOLAS machinery or scantling formulas, stop and add a new retrieval/promotion pass. |
| `data/design-codes/code-registry.yaml` | Current registry is focused on DNV/API/ASME/ISO offshore/pipeline/structural codes; targeted search found no rudder-stock or steering-gear design-code entry. | Do not cite a design-code edition as an active basis for #2565. |
| `data/document-index/online-resource-registry.yaml` | Naval-architecture records include PNA volumes, USNA EN400, and SOLAS 2020 with local backups under `/mnt/ace/docs/_standards/...`; USNA EN400 is also indexed. | Use these as context/vocabulary only; existing wiki-promoted #2564 sources remain the authoritative local knowledge anchors. |
| `data/standards/promoted/naval-architecture/glossary.yaml` | Promoted SOLAS snippets define steering gear, auxiliary steering gear, power actuating system, rudder stock, and maximum ahead service speed. | Include SOLAS terms as vocabulary/caveats only; no SOLAS compliance calculation is in scope. |

### `/mnt/ace` and wiki-promotion decision

No new `/mnt/ace` mining or wiki-promotion is required before implementation **if** #2565 remains bounded to: existing rudder normal force × user-supplied perpendicular stock/center-of-pressure arm, with no new standards-derived coefficients/constants and no compliance claims. Existing #2564 wiki pages (`rudder-force-modeling`, `yaw-moment-rudder-sweep`, `maneuvering-coordinate-conventions`) are sufficient for this bounded scope.

Hard stop: if implementation introduces any new coefficient (`C_QN`, `C_QR`, hull/propeller interaction coefficient, class-rule allowable, stock scantling factor, actuator sizing coefficient, SOLAS/class acceptance criterion), pause implementation and add a fresh raw-reference/wiki-promotion step before coding.

### Documents consulted

- Issue #2565 body — defines rudder stock / steering gear torque sweep scope and explicit out-of-scope boundaries.
- Issue #2564 and `docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md` — prior completed yaw-moment sweep, output contract, and validation pattern.
- `docs/session-handoffs/2026-04-30-yaw-moment-sweep-closeout-next-calculation.md` — recommends this issue as the next bounded calculation after #2564.
- `digitalmodel/docs/domains/marine-engineering/yaw-moment-sweep.md` — user-facing docs and limitations for the immediate predecessor workflow.
- `/mnt/ace` source pages previously promoted to naval-architecture wiki for PNA, EN400, Bertram, ShipMo3D, ABS/IMO/USCG, OrcaFlex/OCIMF yaw references.

### Gaps identified

- No implementation function for `rudder_stock_torque_Nm = scalar_normal_force_N * stock_to_center_of_pressure_arm_m`.
- No validated YAML field for `stock_to_center_of_pressure_arm_m`, `positive_torque_direction`, or optional torque units (`N*m`, `kN*m`).
- No output columns for `stock_to_center_of_pressure_arm_m`, `rudder_stock_torque_Nm`, or `rudder_stock_torque_kNm`.
- No torque-specific charts:
  - torque vs rudder angle by speed,
  - torque vs speed by rudder angle,
  - scalar normal force vs rudder angle by speed,
  - speed/angle torque heatmap.
- No docs explaining that this is a preliminary envelope, not steering-gear actuator sizing, rudder-stock stress, bearing reaction, or SOLAS/class compliance.

### Evidence (embedded verification)

**Issue status** (verified 2026-04-30 via GitHub API):

```json
{
  "issue": 2565,
  "title": "feat(naval-arch): rudder stock torque sweep input for typical ship",
  "state": "open",
  "labels": ["enhancement", "priority:medium", "cat:engineering-calculations", "domain:hydrodynamics", "domain:naval-architecture"]
}
```

**File existence / implementation surface** (verified 2026-04-30):

- EXISTS on `digitalmodel` main commit `0db57cd564720431213ee659cb1787a55683e922`: `src/digitalmodel/naval_architecture/yaw_moment.py`.
- EXISTS on `digitalmodel` main commit `0db57cd564720431213ee659cb1787a55683e922`: `src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml`.
- EXISTS on `digitalmodel` main commit `0db57cd564720431213ee659cb1787a55683e922`: `tests/naval_architecture/test_yaw_moment_sweep.py`.
- MISSING / new in this plan: `src/digitalmodel/naval_architecture/rudder_stock_torque.py`.
- MISSING / new in this plan: `src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml`.
- MISSING / new in this plan: `tests/naval_architecture/test_rudder_stock_torque_sweep.py`.
- MISSING / new in this plan: `docs/domains/marine-engineering/rudder-stock-torque-sweep.md`.

**Line excerpts:**

`yaw_moment.py` #2564 basis:

```text
KNOT_TO_M_PER_S = 0.514444
CSV_HEADERS includes scalar_normal_force_N, transverse_force_N, yaw_moment_Nm
REQUIRED_CHARTS includes transverse_force_vs_rudder_angle_by_speed
rudder_yaw_moment(...) calls rudder_normal_force(...) with keyword arguments
```

`yaw_moment_typical_ship.yml` #2564 input basis:

```yaml
rudder:
  area_m2: 20.0
  span_m: 5.0
  x_from_cg_m: -45.0
sweep:
  speeds:
    units: kn
    values: [0, 2, 5, 10, 15]
  rudder_angles_deg: [-35, -20, -10, 0, 10, 20, 35]
```

`rudder-force-modeling.md` knowledge anchor:

```text
C_QN = Q_N / (q A_R c_m)
C_QR = Q_R / (q A_R c_m)
A bounded first-pass yaw calculation may use a rudder normal force F_N and a CG lever arm.
```

**Minimum distinct source count:** 8+ sources consulted (issue body, #2564 plan, #2564 handoff, digitalmodel source, digitalmodel tests, calc citation contract, naval-architecture wiki pages, promoted SOLAS glossary snippets).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2565-rudder-stock-torque-sweep-input.md` |
| Plan index | `docs/plans/README.md` |
| Implementation module | `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py` |
| Packaged example YAML | `digitalmodel/src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml` |
| Public exports | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` |
| Tests | `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py` |
| Regression tests | `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` |
| User docs | `digitalmodel/docs/domains/marine-engineering/rudder-stock-torque-sweep.md` |
| Plan review — Claude | `scripts/review/results/2026-04-30-plan-2565-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-30-plan-2565-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-30-plan-2565-gemini.md` |
| Review synthesis | `scripts/review/results/2026-04-30-plan-2565-disagreement.md` |
| GitHub plan comment | `https://github.com/vamseeachanta/workspace-hub/issues/2565#issuecomment-4356324863` (update after review remediation) |
| Plan approval marker | `.planning/plan-approved/2565.md` (must exist before implementation) |
| Label transition | `status:plan-review` only after clean review; `status:plan-approved` only after user approval |

---

### Exact output artifact contract

The implementation must write torque-specific artifact names, not copied yaw-moment names:

- `rudder_stock_torque_sweep.csv`
- `rudder_stock_torque_sweep.json`
- `rudder_stock_torque_provenance.json`
- `artifact_manifest.json`
- chart basenames:
  - `rudder_stock_torque_vs_rudder_angle_by_speed`
  - `rudder_stock_torque_vs_speed_by_rudder_angle`
  - `scalar_normal_force_vs_rudder_angle_by_speed`
  - `rudder_stock_torque_speed_angle_heatmap`

If shared writer/chart code is extracted from #2564 `yaw_moment.py`, keep the refactor narrow and run yaw-moment regression tests to prevent filename/JSON contract drift.

---

## Deliverable

A `rudder_stock_torque.py` workflow in `digitalmodel` that loads a typical-ship YAML input, computes preliminary rudder-stock torque over speed/rudder-angle sweeps using existing rudder normal force, and writes CSV/JSON tables, provenance sidecar, manifest, and required charts with TDD coverage.

---

## Scope Boundaries

### In scope

- Preliminary torque envelope using **hydrodynamic torque exerted by the flow on the rudder/stock**:

```text
hydrodynamic_rudder_stock_torque_Nm = scalar_normal_force_N * stock_to_center_of_pressure_arm_m
required_steering_gear_holding_torque_Nm = -hydrodynamic_rudder_stock_torque_Nm
```

- Reuse `rudder_normal_force(...)` through #2564-style keyword arguments.
- User-configurable `stock_to_center_of_pressure_arm_m` in YAML.
- Define `stock_to_center_of_pressure_arm_m` as the assumed constant **perpendicular distance from the rudder stock axis to the line of action of the resultant rudder normal force**. It is not a generic chordwise offset unless the input author has projected it perpendicular to the normal-force line of action.
- Emit both hydrodynamic and required holding torque so sign ambiguity cannot hide equal-and-opposite steering-gear reaction torque.
- Explicit sign convention metadata:
  - `scalar_normal_force_N` preserves existing helper sign.
  - `hydrodynamic_rudder_stock_torque_Nm` is positive when the flow torque acts in the configured positive rudder-stock rotation sense, viewed from above.
  - `required_steering_gear_holding_torque_Nm` is equal and opposite to hydrodynamic torque.
  - `rudder_stock_torque_abs_Nm` / `rudder_stock_torque_abs_kNm` emitted for design-envelope ranking.
- CSV/JSON output tables and required charts.
- Provenance sidecar stating formula, reused force source, limitations, and whether strict citation objects were needed.

### Out of scope

- Full steering gear machinery sizing.
- Rudder-stock diameter/stress/scantling calculations.
- Bearing reactions, actuator ram forces, tiller/quadrant geometry, hydraulic power, relief valve settings.
- SOLAS/class compliance checks.
- Center-of-pressure migration with rudder angle, stall, propeller slipstream correction, hull interaction, MMG/turning-circle simulation.
- Environmental current/wind yaw moment or torque envelopes.

Future issues should cover the out-of-scope items only after this preliminary envelope is validated. #2565 is not computing Bertram/PNA coefficient-based stock torque (`Q_N`, `Q_R`, `C_QN`, `C_QR`); those symbols remain reference vocabulary for later higher-fidelity work.

---

## Pseudocode

```text
function rudder_stock_torque(...):
    validate velocity >= 0, rho > 0, rudder geometry > 0
    validate stock_to_center_of_pressure_arm_m is finite and >= 0
    validate positive_hydrodynamic_torque_direction is a geometric rotation convention
    scalar_normal_force_N = rudder_normal_force(... keyword args ...)
    hydrodynamic_torque_Nm = scalar_normal_force_N * stock_to_center_of_pressure_arm_m
    required_holding_torque_Nm = -hydrodynamic_torque_Nm
    return result with scalar force, hydrodynamic torque, holding torque, absolute torque, units, convention metadata

function validate_rudder_stock_torque_input(payload):
    require case, vessel, rudder, stock, environment, sweep, outputs sections
    reuse speed conversion logic from #2564 or call shared helper if refactored safely
    parse stock_to_center_of_pressure_arm_m
    parse optional torque output units and chart contracts
    validate required chart names exactly
    return immutable/config object

function run_rudder_stock_torque_sweep(config):
    for speed in speeds and angle in rudder_angles:
        result = rudder_stock_torque(...)
        append row with speed_m_s, speed_kn, rudder angle, scalar_normal_force_N,
                   stock_to_center_of_pressure_arm_m, hydrodynamic_rudder_stock_torque_Nm,
                   required_steering_gear_holding_torque_Nm, absolute torque, convention fields
    attach provenance and units metadata
    return rows + metadata

function write_rudder_stock_torque_results(result, output_dir, table_formats, chart_formats):
    write CSV with stable headers
    write JSON with metadata/provenance/rows/artifacts
    write provenance/citation sidecar
    write artifact_manifest.json
    if charts enabled:
        write four required charts in requested png/html formats
    return manifest
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py` | Main calculation, YAML validation, sweep, output writers, chart writers. |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml` | Packaged typical-ship torque input. |
| Modify | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export only top-level workflow helpers with demonstrated downstream value, e.g. `load_packaged_rudder_stock_torque_yaml`, `load_rudder_stock_torque_input`, `rudder_stock_torque`, `run_rudder_stock_torque_sweep`, and `write_rudder_stock_torque_results`; keep validators, chart builders, constants, and internal dataclasses module-private. |
| Create | `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py` | TDD tests for formula, YAML, packaging, outputs, charts, provenance. |
| Update | `digitalmodel/docs/domains/marine-engineering/rudder-stock-torque-sweep.md` | User-facing methodology, inputs, outputs, limitations. |
| Update | `docs/plans/README.md` | Add #2565 plan row. |
| Create/update | `scripts/review/results/2026-04-30-plan-2565-*.md` | Adversarial review artifacts. |

No implementation code may be changed until this plan passes review and the user approves #2565.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_rudder_stock_torque_zero_arm_is_zero_torque` | Zero stock/center-of-pressure arm produces zero torque even with nonzero rudder force | base rudder case, arm `0.0` | torque `0.0`, force nonzero |
| `test_rudder_stock_torque_scales_linearly_with_arm` | Torque is linear in arm for fixed force | arm `0.5` vs `1.0` | torque doubles |
| `test_rudder_stock_torque_scales_with_speed_squared` | Torque inherits `V^2` scaling from rudder force | speed `5` vs `10 m/s` | torque magnitude ×4 |
| `test_rudder_stock_torque_preserves_scalar_force_source` | Calls `rudder_normal_force` with keyword args; no positional scrambling | monkeypatched helper | captured kwargs match expected |
| `test_positive_torque_direction_mapping_is_explicit` | Sign convention is not implicit/tautological | two positive_torque_direction modes | signed torque flips, absolute torque unchanged |
| `test_load_packaged_rudder_stock_yaml_with_importlib_resources` | YAML is packaged and readable | packaged resource | case id and stock arm present |
| `test_packaged_yaml_in_built_distribution_preserves_existing_package_data` | Wheel includes new YAML and existing package data | build wheel | both `rudder_stock_torque_typical_ship.yml` and existing package data present |
| `test_load_rudder_stock_yaml_converts_knots` | Speed unit conversion remains explicit | speed `5 kn` | `5 * 0.514444 m/s` |
| `test_sweep_cardinality_matches_grid` | Sweep rows equal speed count × angle count | 5 speeds × 7 angles | 35 rows |
| `test_zero_speed_all_angles_are_zero_force_and_torque` | Zero speed has zero force/torque | `speed=0` rows | all force/torque zero |
| `test_invalid_negative_stock_arm_rejected` | Input validation prevents invalid arm sign if arm is defined as magnitude | `stock_to_center_of_pressure_arm_m=-0.1` | `ValueError` |
| `test_write_results_csv_json_and_required_chart_manifest` | Output table/chart contract is stable | run default case | CSV, JSON, manifest, sidecar, all charts exist |
| `test_output_rows_include_units_and_abs_torque` | Rows include signed and absolute torque fields | run default case | `hydrodynamic_rudder_stock_torque_Nm`, `required_steering_gear_holding_torque_Nm`, `rudder_stock_torque_abs_Nm`, `rudder_stock_torque_abs_kNm` present |
| `test_provenance_sidecar_states_preliminary_scope` | Sidecar includes formula, force source, limitations, citation status | write results | sidecar references formula and excludes class compliance |
| `test_required_charts_are_torque_specific` | Required charts do not accidentally inherit yaw-moment names | packaged YAML | exact four torque chart names |
| `test_base_case_positive_angle_absolute_torque_sign` | Non-tautological sign check pinned to helper behavior | `rudder_angle_deg=+10`, arm > 0 | hydrodynamic torque sign matches documented convention; holding torque has opposite sign |
| `test_negative_angle_reverses_hydrodynamic_and_holding_torque_signs` | Negative rudder angle reverses both signed torque fields | `+10` vs `-10` | signs flip; magnitudes match |
| `test_single_row_torque_identity` | Direct identity, not just ratios | one row | `hydrodynamic_rudder_stock_torque_Nm == scalar_normal_force_N * arm` |
| `test_provenance_declares_user_supplied_arm_and_constant_arm_assumption` | Prevents coefficient/class-rule confusion | write sidecar | states arm is user input and not a standards-derived coefficient |

---

## Acceptance Criteria

- [ ] New tests are written before implementation and initially fail for missing `rudder_stock_torque` module/YAML.
- [ ] `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_rudder_stock_torque_sweep.py -q` passes after implementation.
- [ ] `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py tests/naval_architecture/test_rudder_stock_torque_sweep.py -q` passes as targeted regression. If any shared helper/writer is touched, this full slice is mandatory.
- [ ] `UV_NO_SYNC=1 uv run --with ruff ruff check src/digitalmodel/naval_architecture/rudder_stock_torque.py tests/naval_architecture/test_rudder_stock_torque_sweep.py src/digitalmodel/naval_architecture/__init__.py` passes.
- [ ] Packaged YAML loads with `importlib.resources` and is present in built wheel without dropping existing package data.
- [ ] Public import/API smoke passes outside pytest path injection: `PYTHONPATH=src UV_NO_SYNC=1 uv run python -c "from digitalmodel.naval_architecture import load_packaged_rudder_stock_torque_yaml, run_rudder_stock_torque_sweep"`.
- [ ] Default case writes 35 sweep rows, CSV, JSON, provenance/citation sidecar, artifact manifest, and all four required charts.
- [ ] Output rows include stable units and both signed and absolute torque values.
- [ ] Documentation explicitly states preliminary scope and excludes steering gear machinery sizing, structural/scantling checks, bearing reactions, and class/SOLAS compliance.
- [ ] Fresh plan-review artifacts exist at canonical paths with at least two substantive provider/reviewer results plus synthesis. `UNAVAILABLE` artifacts do not count toward substantive coverage unless explicitly justified in synthesis.
- [ ] No unresolved MAJOR findings remain before moving to `status:plan-review`.
- [ ] `.planning/plan-approved/2565.md` and `status:plan-approved` label are synchronized before implementation starts.
- [ ] Implementation review/cross-review returns no unresolved MAJOR findings before closeout.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude/Hermes engineering review | MAJOR -> remediated in plan | Required hydrodynamic vs holding torque split, perpendicular-arm definition, non-tautological sign tests, direct identity test, user-supplied arm provenance. |
| Codex/Hermes package/API review | MAJOR -> remediated in plan | Required maneuverability regression slice, exact output artifact names, public import smoke, narrowed public API export boundary. |
| Gemini/Hermes governance review | MAJOR -> remediated in plan | Required engineering registry retrieval evidence, canonical review/approval gate criteria, governance artifacts, explicit `/mnt/ace`/wiki-promotion decision. |

**Overall result:** remediated plan-review candidate. Initial reviews found MAJOR issues; this revision addresses them. Move to `status:plan-review` only after the review artifact files and synthesis are published and a final verification confirms no unresolved MAJOR remains.

Revisions made based on review:
- Split signed output into `hydrodynamic_rudder_stock_torque_Nm` and `required_steering_gear_holding_torque_Nm`.
- Defined `stock_to_center_of_pressure_arm_m` as a perpendicular force-line moment arm, not generic geometry.
- Added constant-arm, no-coefficient, no-SOLAS/class-compliance caveats.
- Added exact torque-specific output filenames and chart basenames.
- Added non-tautological sign, negative-angle, direct-identity, and user-supplied-arm provenance tests.
- Expanded targeted regression to include `test_maneuverability.py`.
- Added public import smoke outside pytest path injection.
- Narrowed public API export boundary.
- Added engineering-registry retrieval evidence and explicit `/mnt/ace`/wiki-promotion decision.
- Added governance artifacts and acceptance gates for review artifacts, `status:plan-review`, and `.planning/plan-approved/2565.md`.

---

## Risks and Open Questions

- **Risk — sign convention ambiguity:** steering/rudder-stock torque sign is not the same as yaw moment sign. The plan now requires separate hydrodynamic and equal/opposite holding torque fields plus a named geometric positive rotation convention and absolute torque for envelope use.
- **Risk — false compliance implication:** SOLAS/class terms are relevant vocabulary only; this issue must not imply steering gear approval or machinery compliance.
- **Risk — package-data regression:** #2564 already exposed package-data risk. The wheel test must preserve existing data while adding new YAML.
- **Risk — copy/paste drift from #2564:** Chart names, output filenames, docs, and provenance must use torque terminology, not yaw-moment labels.
- **Open:** whether to refactor shared YAML/output/chart code from `yaw_moment.py` in this issue. Default decision: avoid broad refactor unless required to keep implementation simple and tests bounded.

---

## Follow-up Issues

Candidate follow-ups after #2565, not in current scope:

1. `feat(naval-arch): rudder stock stress/scantling check for typical ship` — structural sizing and allowable stress/class-rule context.
2. `feat(naval-arch): steering gear actuator force and hydraulic power envelope` — machinery sizing using tiller/quadrant/ram geometry.
3. `feat(naval-arch): rudder hull/propeller interaction correction sweep` — Bertram/ShipMo3D interaction corrections.
4. `feat(naval-arch): Nomoto turning response from yaw moment envelope` — dynamic maneuvering response beyond static torque/yaw sweeps.

No follow-up issue is created yet; create only if review/user asks to split or prioritize one.

---

## Review Readiness Notes

- Complexity: **T2** — bounded new calculation module, packaged YAML, tests, docs, and output artifacts, reusing #2564 infrastructure.
- Agent-team delegation: **not recommended** for implementation; file surface is small and shared with #2564 output patterns, so one execution lane avoids git contention.
- Implementation blocked until plan review passes and user approval is recorded.


## Implementation Closeout — 2026-04-30

Implementation completed in `digitalmodel` commit `3609b7dca981de3c6213413ddd6b404920b56f29` after user approval via GitHub label `status:plan-approved`. Local approval marker was committed before code changes in `/mnt/local-analysis/digitalmodel-issue2565` (`b2095b4e`).

Delivered files in `digitalmodel`:

- `src/digitalmodel/naval_architecture/rudder_stock_torque.py`
- `src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml`
- `tests/naval_architecture/test_rudder_stock_torque_sweep.py`
- `docs/domains/marine-engineering/rudder-stock-torque-sweep.md`
- `src/digitalmodel/naval_architecture/__init__.py` public exports

Delivered output contract:

- `rudder_stock_torque_sweep.csv`
- `rudder_stock_torque_sweep.json`
- `rudder_stock_torque_provenance.json`
- `artifact_manifest.json`
- required PNG/HTML charts:
  - `rudder_stock_torque_vs_rudder_angle_by_speed`
  - `rudder_stock_torque_vs_speed_by_rudder_angle`
  - `scalar_normal_force_vs_rudder_angle_by_speed`
  - `rudder_stock_torque_speed_angle_heatmap`

Validation evidence:

- TDD red: initial `test_rudder_stock_torque_sweep.py` run failed with missing module/YAML as expected.
- Torque test suite: `19 passed`.
- Targeted regression: `62 passed` for `test_maneuverability.py`, `test_yaw_moment_sweep.py`, and `test_rudder_stock_torque_sweep.py`.
- Ruff: `All checks passed!` for new/modified Python files.
- Smoke generation: 35 rows plus CSV/JSON/provenance/manifest and all four PNG+HTML charts.
- Adversarial implementation review: initial MINOR findings fixed; follow-up verdict `APPROVE`.

Final calculation boundary remains unchanged: preliminary constant-arm hydrodynamic rudder-stock torque and equal/opposite steering-gear holding torque only. No class/SOLAS compliance, actuator sizing, steering gear machinery sizing, or rudder stock scantling is claimed.
