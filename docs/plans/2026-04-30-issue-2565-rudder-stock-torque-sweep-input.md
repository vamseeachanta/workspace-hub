# Plan for #2565: feat(naval-arch): rudder stock torque sweep input for typical ship

> **Status:** draft — resource-intelligence and initial plan prepared; implementation blocked until adversarial review passes and user approval moves #2565 to `status:plan-approved`.
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

---

## Deliverable

A `rudder_stock_torque.py` workflow in `digitalmodel` that loads a typical-ship YAML input, computes preliminary rudder-stock torque over speed/rudder-angle sweeps using existing rudder normal force, and writes CSV/JSON tables, provenance sidecar, manifest, and required charts with TDD coverage.

---

## Scope Boundaries

### In scope

- Preliminary torque envelope:

```text
rudder_stock_torque_Nm = scalar_normal_force_N * stock_to_center_of_pressure_arm_m
```

- Reuse `rudder_normal_force(...)` through #2564-style keyword arguments.
- User-configurable `stock_to_center_of_pressure_arm_m` in YAML.
- Explicit sign convention metadata:
  - `scalar_normal_force_N` preserves existing helper sign.
  - `rudder_stock_torque_Nm` sign follows `positive_torque_direction` and the signed scalar force convention.
  - `rudder_stock_torque_abs_Nm` / `rudder_stock_torque_abs_kNm` emitted for design-envelope ranking.
- CSV/JSON output tables and required charts.
- Provenance sidecar stating formula, reused force source, limitations, and whether strict citation objects were needed.

### Out of scope

- Full steering gear machinery sizing.
- Rudder-stock diameter/stress/scantling calculations.
- Bearing reactions, actuator ram forces, tiller/quadrant geometry, hydraulic power, relief valve settings.
- SOLAS/class compliance checks.
- Propeller slipstream correction, hull interaction, MMG/turning-circle simulation.
- Environmental current/wind yaw moment or torque envelopes.

Future issues should cover the out-of-scope items only after this preliminary envelope is validated.

---

## Pseudocode

```text
function rudder_stock_torque(...):
    validate velocity >= 0, rho > 0, rudder geometry > 0
    validate stock_to_center_of_pressure_arm_m is finite and >= 0
    validate positive_torque_direction in {"resists_positive_rudder_force", "assists_positive_rudder_force"} or equivalent explicit enum
    scalar_normal_force_N = rudder_normal_force(... keyword args ...)
    signed_torque_Nm = scalar_normal_force_N * stock_to_center_of_pressure_arm_m
    if positive_torque_direction maps positive scalar force to negative applied steering torque:
        signed_torque_Nm *= -1
    return result with scalar force, signed torque, absolute torque, units, convention metadata

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
                   stock_to_center_of_pressure_arm_m, rudder_stock_torque_Nm,
                   rudder_stock_torque_kNm, abs torque, convention fields
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
| Modify | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Export approved public helpers such as `rudder_stock_torque`, `run_rudder_stock_torque_sweep`, loaders/writers. |
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
| `test_output_rows_include_units_and_abs_torque` | Rows include signed and absolute torque fields | run default case | `rudder_stock_torque_Nm`, `rudder_stock_torque_abs_Nm`, `rudder_stock_torque_kNm` present |
| `test_provenance_sidecar_states_preliminary_scope` | Sidecar includes formula, force source, limitations, citation status | write results | sidecar references formula and excludes class compliance |
| `test_required_charts_are_torque_specific` | Required charts do not accidentally inherit yaw-moment names | packaged YAML | exact four torque chart names |

---

## Acceptance Criteria

- [ ] New tests are written before implementation and initially fail for missing `rudder_stock_torque` module/YAML.
- [ ] `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_rudder_stock_torque_sweep.py -q` passes after implementation.
- [ ] `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py tests/naval_architecture/test_rudder_stock_torque_sweep.py -q` passes as targeted regression.
- [ ] `UV_NO_SYNC=1 uv run --with ruff ruff check src/digitalmodel/naval_architecture/rudder_stock_torque.py tests/naval_architecture/test_rudder_stock_torque_sweep.py src/digitalmodel/naval_architecture/__init__.py` passes.
- [ ] Packaged YAML loads with `importlib.resources` and is present in built wheel without dropping existing package data.
- [ ] Default case writes 35 sweep rows, CSV, JSON, provenance/citation sidecar, artifact manifest, and all four required charts.
- [ ] Output rows include stable units and both signed and absolute torque values.
- [ ] Documentation explicitly states preliminary scope and excludes steering gear machinery sizing, structural/scantling checks, bearing reactions, and class/SOLAS compliance.
- [ ] Implementation review/cross-review returns no unresolved MAJOR findings before closeout.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | pending review |
| Codex | pending | pending review |
| Gemini | pending | pending review |

**Overall result:** pending — do not move to `status:plan-review` until review artifacts are created and any MAJOR findings are resolved.

Revisions made based on review:
- Pending.

---

## Risks and Open Questions

- **Risk — sign convention ambiguity:** steering/rudder-stock torque sign is not the same as yaw moment sign. The implementation must define a torque-specific convention and emit absolute torque for envelope use.
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
