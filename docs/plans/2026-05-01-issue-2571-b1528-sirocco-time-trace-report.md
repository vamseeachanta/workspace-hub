# Plan for #2571: B1528 SIROCCO time-trace benchmark report with rudder inflow feedback

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-05-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2571
> **Review artifacts:** scripts/review/results/2026-05-01-plan-2571-claude.md | scripts/review/results/2026-05-01-plan-2571-codex.md | scripts/review/results/2026-05-01-plan-2571-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: #2568 approved plan for preliminary first-order Nomoto turning-circle/tactical-diameter estimator.
- Found: #2570 planned B1528 static yaw-moment input/report that should provide shared B1528 geometry and source references.
- Found: `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` and `maneuverability.py` — static rudder force/yaw-moment calculation surfaces.
- Gap: no time-trace model in `digitalmodel` currently updates rudder-local inflow/attack angle as yaw rate evolves.

### Standards
| Standard | Status | Source |
|---|---|---|
| Nomoto first-order maneuvering model | methodology to document | naval-architecture/manoeuvring references from #2568 |
| IMO turning-circle metrics | terminology only | benchmark naming; no compliance/pass-fail claim |

### LLM Wiki pages consulted
- `knowledge/wikis/acma-projects/wiki/sources/b1528-sirocco-breakaway-notes.md` — benchmark notes requiring normalization.
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — B1528 geometry/inputs.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` — turning-circle/tactical-diameter context.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — coordinate/sign convention basis.

### Documents consulted

- `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx` — workbook contains `Rudder Area and Geometry`, `Rudder Force`, `Yaw Moment` sheets. Extracted B1528 SIROCCO values include LBP `225.5 m`, rudder area `44.9395631937 m²`, rudder center aft of AP `-1.0520261379 m`, legacy yaw lever `0.6 * LBP = 135.3 m`, `β = 600`, and `Cr = 1.065/0.935`.
- `B1528/excel_to_py/rudder_force_yaw_moment.py` — converted workbook script exposes the legacy calculation family but hardcodes formulas and does not provide a reusable input/report workflow.
- `B1528/ref/SIROCCO breakaway notes.docx` — contains narrative heading/speed/time anchors and a turning/track benchmark, but evidence must be normalized before numerical comparison.
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — newly created pre-work wiki page documenting extracted B1528 inputs and calculation boundaries.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — sign/coordinate convention background from prior yaw-moment work.
- #2564 — completed reusable yaw-moment sweep workflow for typical-ship/rudder cases.
- #2568 — approved/planned preliminary turning-circle/tactical-diameter estimator workflow.


### Gaps identified
- Need a bounded time integrator that computes yaw rate, heading, x/y trace, and local rudder inflow feedback.
- Need calibration/assumption fields for Nomoto `K` and `T` or a documented source-gap/sensitivity-mode if project-specific coefficients are unavailable; no benchmark calibration may be invented.
- Need benchmark overlay against SIROCCO turning/track evidence, but only where evidence is quantitative enough.
- Need interactive time-history charts and clear limitations against full MMG/incident reconstruction.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-01 via `gh issue view`):
- `#2568` — user-approved via labels — preliminary turning-circle estimator.
- `#2569` — OPEN — source/benchmark pack prerequisite.
- `#2570` — OPEN — static yaw input/report prerequisite.
- `#2571` — OPEN — this issue.

**Selected numerical method**:
```text
v_R = x_R * r
beta_R = atan2(-x_R * r, U)
alpha_R = delta_cmd - beta_R
U_R = sqrt(U^2 + v_R^2)
r_dot = (K * alpha_R - r) / T  # governing Nomoto state equation; direct rudder force/yaw moment is diagnostic only in this mode
psi_dot = r
x_dot = U * cos(psi)
y_dot = U * sin(psi)
```

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-01-issue-2571-b1528-sirocco-time-trace-report.md |
| Tests | digitalmodel/tests/naval_architecture/test_b1528_sirocco_time_trace.py |
| Input YAML | digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_time_trace.yml |
| Time-trace module/wrapper | digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_time_trace.py |
| Report docs | digitalmodel/docs/domains/marine-engineering/b1528-sirocco-time-trace-report.md |
| Interactive output | digitalmodel/outputs/b1528_sirocco/time_trace_report.html |

---

## Deliverable
A B1528 SIROCCO preliminary time-trace calculation/report with rudder-local inflow feedback, benchmark comparison, and interactive charts.

---

## Pseudocode
```text
load B1528 time-trace YAML with U, delta_cmd, x_R, K, T, dt, duration, benchmark refs
validate U > 0, T > 0, dt > 0, abs(delta_cmd) bounded, K units documented
initialize x=0, y=0, psi=0, r=0
for each time step:
    v_R = x_R * r
    beta_R = atan2(-x_R * r, U)
    alpha_R = delta_cmd - beta_R
    U_R = hypot(U, v_R)
    compute rudder force/yaw moment using local U_R and alpha_R as diagnostics only
    r_dot = (K * alpha_R - r) / T  # do not also feed diagnostic yaw moment into rotational dynamics  # governing Nomoto state equation; direct rudder force/yaw moment is diagnostic only in this mode
    integrate r, psi, x, y with RK4 or semi-implicit Euler per selected numerical method
write time series CSV/JSON/provenance/manifest
compute turning metrics only as descriptive values, not compliance pass/fail
render interactive charts and benchmark overlay where data permits
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | digitalmodel/tests/naval_architecture/test_b1528_sirocco_time_trace.py | TDD for dynamic method/report |
| Create | digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_time_trace.yml | B1528 dynamic input file |
| Create | digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_time_trace.py | project wrapper or method extension |
| Update | digitalmodel/src/digitalmodel/naval_architecture/__init__.py | export if reusable public API is added |
| Create | digitalmodel/docs/domains/marine-engineering/b1528-sirocco-time-trace-report.md | detailed report |
| Update | docs/plans/README.md | plan index |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_b1528_time_trace_yaml_loads | packaged dynamic input loads | package resource | fields present with source refs |
| test_zero_rudder_straight_trace | zero rudder produces near-zero yaw rate | delta=0 | r≈0, y≈0 |
| test_positive_negative_symmetry | ±1° signs mirror under symmetric assumptions | +1/-1 deg | opposite yaw-rate/heading sign |
| test_effective_attack_feedback_changes | yaw rate changes local inflow angle | nonzero K/T | alpha_R differs from delta_cmd after transient |
| test_integration_step_sensitivity | smaller dt yields stable metrics | dt and dt/2 | bounded difference |
| test_report_contains_interactive_charts | report output includes expected charts | temp output | trajectory, heading, yaw rate, alpha, moment |
| test_no_mmg_or_compliance_overclaim | report caveats are present | report text | no IMO/class/MMG overclaims |

---

## Acceptance Criteria
- [ ] HARD STOP: after this plan reaches `status:plan-review`, wait for explicit user approval / `status:plan-approved` before implementation.
- [ ] #2568 method is available/approved and #2569 source-pack evidence is available before B1528 benchmark claims are made.
- [ ] Tests are written before implementation and pass with `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_b1528_sirocco_time_trace.py -q`.
- [ ] The numerical method is explicitly documented, including state variables, units, integrator choice, and timestep-sensitivity check.
- [ ] Outputs include heading, yaw rate, x/y trajectory, rudder-local inflow angle, effective rudder angle, local rudder speed, force, and yaw moment.
- [ ] Interactive charts include trajectory, heading vs time, yaw rate vs time, effective rudder angle vs time, yaw moment vs time, and benchmark overlay or source-gap panel.
- [ ] Benchmark section compares against extracted SIROCCO evidence with caveats and uncertainty notes; if evidence is narrative-only, report source-gap/sensitivity results rather than overlaying fabricated points.
- [ ] Report clearly states preliminary first-order model boundary; no full MMG, compliance, or incident-reconstruction claim.

---

## Adversarial Review Summary
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR -> RESOLVED | Avoid double-counting Nomoto K/T and direct yaw moment; choose a governing dynamic architecture. |
| Codex | MAJOR -> RESOLVED | Use either Nomoto-driven diagnostics-only or moment-balance dynamics; degrade to scenario/source-gap reporting if K/T are unavailable. |
| Gemini | MAJOR -> RESOLVED | Clarify dependency order (#2569 first, #2568 method prerequisite, #2570 preferred static input), artifact placement, and source-gap behavior. |

**Overall result:** PASS after revision — major findings resolved in plan text; implementation remains blocked until user approval.

Revisions made based on review:
- Selected Nomoto-driven state update as the governing preliminary time-trace model.
- Stated rudder force/yaw moment are diagnostics only in the Nomoto mode and must not feed back into `r_dot` unless a separately approved moment-balance model is created.
- Added fallback/source-gap behavior when project-specific `K`/`T` or benchmark tracks are unavailable.
- Tightened dependency chain and interactive artifact deliverability.


---

## Risks and Open Questions
- **Risk:** Project-specific Nomoto coefficients may not exist in B1528 sources; default/calibrated assumptions must be explicitly marked as assumptions and not evidence.
- **Risk:** Rudder force feedback and Nomoto response can be double-counted if yaw moment is used both as direct torque and via calibrated `K`; plan must keep these model variants separated.
- **Risk:** Turning benchmark may be narrative rather than numeric; overlay should degrade to a source-gap/caveat panel.

---

## Complexity: T3
**T3** — numerical method, time integration, project-specific input, benchmark comparison, and interactive reporting with engineering caveats.
