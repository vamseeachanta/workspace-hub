# Plan for #2568: Preliminary turning-circle and tactical-diameter estimator input workflow

> **Status:** plan-review — adversarial reviewed; awaiting user approval
> **Complexity:** T3
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2568
> **Review artifacts:** scripts/review/results/2026-04-30-plan-2568-claude.md | scripts/review/results/2026-04-30-plan-2568-codex.md | scripts/review/results/2026-04-30-plan-2568-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` contains rudder force primitives but no turning-circle trajectory estimator.
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` references promoted curve CSVs for turning-circle, tactical-diameter, steady turning rate, Nomoto K/T, drift-corrected turning circle, and IMO/US Navy criteria; these are generated/reference curve accessors, not an estimator workflow.
- #2564 and #2565 establish reusable YAML sweep, output sidecar, chart, package-data, and citation patterns to follow.

### Standards
- IMO/USCG/ABS maneuvering metrics exist as validation context, not as proof that a preliminary estimator is compliant.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` captures advance, transfer, tactical diameter, steady turning diameter, initial turning, overshoot, and stopping reach criteria.

### LLM Wiki pages consulted
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` — defines turning metrics and caveats.
- `knowledge/wikis/naval-architecture/wiki/sources/principles-of-naval-architecture-second-revision-volume-i.md` — PNA Vol. I turning path metrics locator.
- `knowledge/wikis/naval-architecture/wiki/sources/uscg-nvic-6-95-maneuvering-standards.md` — IMO-style criteria reproduced in USCG context.
- `knowledge/wikis/naval-architecture/wiki/sources/mctaggart-shipmo3d-maneuvering-2007.md` — ShipMo3D turning-circle validation metric definitions.
- `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` — says maneuvering KPI validation is future work.

### Documents consulted
- #2564/#2565 plans and closeouts for package/YAML/output/citation patterns.
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` line references for turning-circle and Nomoto-related promoted CSVs.
- `/mnt/ace` raw locators embedded in wiki for PNA Vol. III, IMO MSC/Circ.1053, USCG NVIC 6-95, ABS guide, and ShipMo3D report.

### Gaps identified
- No executable turning-circle estimator module, YAML input, test suite, or docs workflow exists.
- No validated MMG/full maneuvering simulator exists in this scope.
- Need to avoid claiming IMO/ABS compliance from a preliminary estimator.

### Evidence
- Wiki `maneuvering-validation-metrics.md` lines 18-25 define advance/transfer/tactical diameter/steady turning diameter.
- Same wiki lines 34-45 list IMO/USCG baseline criteria and line 75 warns these metrics do not validate a simple yaw-moment sweep by themselves.
- `curves.py` has reference placeholders/CSV comments for `steady_turning_rate_versus_rudder_angle`, `effect_of_k_and_t_on_the_path_during_a_turning_test`, and `tactical_diameter_for_a_range_speeds`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md` |
| Tests | `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` |
| Implementation | `digitalmodel/src/digitalmodel/naval_architecture/turning_circle.py` |
| Packaged YAML | `digitalmodel/src/digitalmodel/naval_architecture/data/turning_circle_typical_ship.yml` |
| Docs | `digitalmodel/docs/domains/marine-engineering/turning-circle-estimator.md` |
| Plan review artifacts | `scripts/review/results/2026-04-30-plan-2568-*.md` |

---

## Deliverable

A preliminary first-order Nomoto trajectory/metric generator using user-supplied K/T values, packaged typical-ship YAML, output tables/charts/provenance, tests, and documentation that clearly distinguishes illustrative estimates from maneuvering prediction or IMO/ABS compliance proof.

---

## Hard-stop / model-boundary gate

This plan is review-only until user approval. Implementation must not start until review artifacts are published, the issue is labeled `status:plan-review`, and the user applies `status:plan-approved`. The approved model boundary is constant-speed first-order Nomoto with user-supplied K/T only: no sway/drift dynamics, no speed loss, no hull-propeller-rudder interaction, no environmental loads, no hard-over validity claim, no IMO/ABS pass/fail fields, and no compliance criteria overlays in default outputs.

## Bounded input and metric contract

- `T_s > 0`, finite; `K_per_s` finite with documented sign convention.
- `dt_s > 0` and either `dt_s <= T_s / 20` or convergence/step-sensitivity validation must pass.
- `duration_s > dt_s`; if heading targets are not reached, advance/tactical metrics are `null` with warnings, never extrapolated.
- 90° and 180° heading-crossing metrics must be linearly interpolated between time steps.
- Steady-turn radius/diameter is reported only if yaw-rate convergence over a trailing window is demonstrated; otherwise `null` with warning.

---

## Pseudocode

```text
function first_order_nomoto_response(speed, rudder_angle, K, T, duration, dt):
    validate speed_m_s > 0 for nontrivial metrics, T > 0, finite K, dt > 0, duration > dt
    validate dt <= T/20 or require explicit convergence/step-sensitivity evidence
    document sign convention for K and rudder angle
    integrate yaw_rate_dot = (K * delta_rad - yaw_rate) / T
    integrate heading_dot = yaw_rate
    integrate earth-fixed trajectory:
        x_dot = speed * cos(heading)
        y_dot = speed * sin(heading)
    derive metrics:
        interpolate advance/transfer at 90 deg heading change
        interpolate tactical diameter at 180 deg heading change
        report null metrics + warnings when thresholds are not reached
        report steady turning radius only when trailing yaw-rate convergence passes
    return time series, metrics, warnings if targets/convergence are not reached

function run_turning_circle_sweep(yaml):
    load speeds, rudder angles, K/T inputs, duration/dt, outputs
    run estimator for each grid case
    write time-history CSV/JSON, metrics table, provenance sidecar, manifest, charts
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/naval_architecture/turning_circle.py` | estimator and output writer |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/turning_circle_typical_ship.yml` | packaged sample input |
| Create | `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` | TDD suite |
| Modify | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | public exports |
| Create | `digitalmodel/docs/domains/marine-engineering/turning-circle-estimator.md` | docs and caveats |
| Update | `docs/plans/README.md` | plan index |

---

## TDD Test List

| Test name | What it verifies | Expected output |
|---|---|---|
| `test_nomoto_response_zero_rudder_stays_straight` | zero rudder yields near-zero yaw/transfer | straight path |
| `test_nomoto_response_sign_symmetry` | ±rudder produces mirrored transfer/heading | equal magnitude opposite sign |
| `test_nomoto_time_step_reduction_stability` | smaller dt gives consistent tactical diameter | within tolerance |
| `test_metrics_warn_when_heading_target_not_reached` | insufficient duration does not fake tactical diameter | warning + null metric |
| `test_packaged_turning_circle_yaml` | YAML resource loads with expected fields | pass |
| `test_output_artifacts_and_charts` | CSV/JSON/provenance/manifest/charts generated | expected filenames |
| `test_no_compliance_overclaim` | provenance/docs state preliminary/non-compliance | pass |

---

## Acceptance Criteria

- [ ] TDD suite is written before implementation and fails initially for missing module/YAML.
- [ ] Estimator output schema includes at minimum: case id, time_s, heading_deg, yaw_rate_rad_s, x_m, y_m, advance_m, transfer_m, tactical_diameter_m, steady_turning_diameter_m, metric_status, and warnings.
- [ ] Outputs include metrics table, time-history table, JSON summary, provenance/citation sidecar, artifact manifest, and exact chart families: `trajectory_by_case`, `yaw_rate_vs_time`, `heading_vs_time`, `turning_metrics_vs_rudder_angle`.
- [ ] Packaged YAML loads through `importlib.resources` and survives wheel/package-data smoke without changing `pyproject.toml` unless a failing test proves package-data gap.
- [ ] Documentation and provenance clearly state this is a preliminary constant-speed first-order Nomoto generator, not MMG, CFD, sea-trial validation, hard-over prediction, or IMO/ABS compliance proof.
- [ ] Targeted command passes: `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py tests/naval_architecture/test_rudder_stock_torque_sweep.py tests/naval_architecture/test_turning_circle_estimator.py -q`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Engineering reviewer | MAJOR -> resolved | Reframed deliverable as first-order Nomoto K/T generator, added bounded inputs, interpolation, null metrics, convergence, and no-compliance constraints. |
| Governance reviewer | MINOR -> resolved | Added explicit hard stop and deterministic output/validation acceptance criteria. |
| Package/test reviewer | UNAVAILABLE | Subagent timed out; package-data and numerical-test concerns from other reviews were incorporated. |

**Overall result:** PASS after revisions; ready for user approval gate.

---

## Risks and Open Questions

- **Risk:** K/T values are user inputs; this issue must not derive them from hull form without a separate source-backed model, and outputs are illustrative estimates only.
- **Risk:** metric extraction at heading thresholds can be numerically fragile; tests must cover interpolation and not-reached cases.
- **Risk:** plotting dense time histories can generate large artifacts; default sample grid should stay small.
- **Open:** whether to include second-order Nomoto or zig-zag overshoot. Default: defer to future issue.

---

## Complexity: T3

**T3** — new maneuvering estimator, numerical integration, metrics extraction, output artifacts, and strict compliance caveats.
