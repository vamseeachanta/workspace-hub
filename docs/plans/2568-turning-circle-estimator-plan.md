# Plan for [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568): Preliminary turning-circle and tactical-diameter estimator input workflow

> **Status:** plan-review (Team-4 dispatch deliverable; awaiting user approval)
> **Complexity:** T3
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2568
> **Adversarial review:** `docs/reports/2568-plan-r1-adversarial-review.md` (Team-4, r1)
> **Predecessor plans:** [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) yaw-moment sweep (closed); [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) rudder-stock torque (closed)
> **Sibling draft on disk:** `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md` — earlier draft from a prior session; this Team-4 plan supersedes only if user prefers the multi-option decision framing here. Both must reconcile before approval.

---

## Resource Intelligence Summary

Issue-class bundle: **engineering-calculation**. Sources consulted: 8 distinct (issue body, [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) thread, [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) thread, digitalmodel source surface, naval-architecture wiki, /mnt/ace IMO/USCG/ABS PDFs, prior 2568 draft plan, existing TDD test stub).

### Existing repo code

| Path | Finding | Plan consequence |
|---|---|---|
| `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` | Has `rudder_normal_force()`, `nomoto_steady_yaw_rate()`, `steady_turning_radius()` (V/r), `speed_in_turn()` (loss factor `f * (delta/35)^2`), `drift_angle()` (`atan(L/2R)`), `directional_stability_criterion()`. **No** trajectory integrator, **no** advance/transfer extraction, **no** tactical-diameter calculator. | The chosen estimator must integrate the Nomoto ODE in time and extract heading-crossing metrics; we cannot just call existing scalar steady-state helpers. |
| `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` ([#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564), commit `0db57cd5`) | Establishes YAML loader, sweep runner, CSV/JSON writer, provenance sidecar, artifact manifest, four-chart contract, `KNOT_TO_M_PER_S = 0.514444`. | Reuse loader/writer style. **Do not** silently extract a shared base writer in this issue — keep refactor narrow per the [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) precedent. |
| `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py` ([#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565), commit `3609b7dc`) | Confirms the YAML schema convention: top-level keys `case`, `vessel`, `rudder`, `<computation-specific>`, `sign_convention`, `environment`, `sweep`, `outputs`, `warnings.scope_limitations`. | Extend with a `nomoto` (or generalized `dynamics`) section; do not redesign `case/vessel/rudder/sweep`. |
| `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` and `.../rudder_stock_torque_typical_ship.yml` | Both use `sweep.speeds.{units, values}`, `sweep.rudder_angles_deg`, `outputs.{directory, tables, charts.{enabled, formats, required}}`, and a `warnings.scope_limitations` list (in #2565 only). | New YAML must reuse these block structures verbatim. |
| `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` | **Test stub already exists** (213 lines, written 2026-05-01). Expects `simulate_nomoto_turning_circle()`, `load_packaged_turning_circle_yaml()`, `run_turning_circle_sweep()`, `write_turning_circle_results()`, packaged YAML at `data/turning_circle_typical_ship.yml`, four chart names: `trajectory_by_case`, `yaw_rate_vs_time`, `heading_vs_time`, `turning_metrics_vs_rudder_angle`, and a `metrics.metric_status` field. | This pre-commits the API surface. Plan must lock to it OR explicitly justify a breaking change. |
| `digitalmodel/src/digitalmodel/naval_architecture/curves.py` | **DOES NOT EXIST.** The earlier 2568 draft plan claims it does (line 15 of `2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md`). Verified by `find /mnt/local-analysis/workspace-hub/digitalmodel -name 'curves.py' -path '*naval*'` returning only `build/lib/...` cached copy. | Reject the prior plan's curves.py claim. No promoted curve CSVs are available — the estimator must generate trajectories from first principles. |

### Standards consulted

| Standard | Local copy | Status | Plan consequence |
|---|---|---|---|
| IMO MSC.137(76) (2002) Standards for Ship Manoeuvrability | `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 Annex 6 Resolution MSC.137(76) Maneouvrability.pdf` | Available, **not yet wiki-promoted to standards/** for [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) | Acceptance criteria reproduced in `maneuvering-validation-metrics.md` concept page (advance ≤ 4.5L, tactical diameter ≤ 5L). Use as **caveat-only** context; do not claim IMO compliance. |
| IMO MSC/Circ.1053 (2002) Explanatory Notes to Manoeuvrability | `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 MSC Circ.1053 Explanatory Notes to Manoeuvrability.pdf` | Available, source-page already promoted (`knowledge/wikis/naval-architecture/wiki/sources/imo-msc-circ-1053-manoeuvrability-explanatory-notes.md`) | Defines spiral test and steady-turning relation `R = V / psi_dot`. Provides the directional-stability vocabulary. |
| USCG NVIC 6-95 Maneuvering Standards | `/mnt/ace/acma-codes/USCG/NVIC's/1995 NVIC 6-95 Maneuvering Standards.pdf` | Wiki-promoted source page exists | Reproduces IMO trial criteria; same caveat-only role. |
| ABS Vessel Maneuverability Guide (2017) | `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` | Wiki source page exists | Defines ABS rating structure `Rt = 0.25 * (Rtd + Rt_alpha + Rti + Rts)`. Caveat-only. |

**Standards-derived numeric constants introduced by this plan: zero.** All numerics (K, T, geometry, speeds, rudder angles) are user inputs from YAML. No `Citation` schema obligation per `.claude/rules/calc-citation-contract.md` (constants from user input or derived from code, not a standard).

### LLM Wiki pages consulted

- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` — defines advance / transfer / tactical diameter / steady turning diameter; reproduces IMO criteria; explicitly warns these "do not validate a simple yaw-moment sweep by themselves" (line 75).
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — pins yaw/rudder sign conventions PNA + EN400.
- `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` — flags maneuvering KPI validation as future work.
- `knowledge/wikis/naval-architecture/wiki/sources/mctaggart-shipmo3d-maneuvering-2007.md` — turning-circle metric definitions (advance/transfer extracted at heading milestones).
- `knowledge/wikis/naval-architecture/wiki/sources/principles-of-naval-architecture-second-revision-volume-i.md` — PNA Vol. I turning-path metrics locator.
- `knowledge/wikis/naval-architecture/wiki/sources/uscg-nvic-6-95-maneuvering-standards.md` — IMO criteria re-statement.

### Documents consulted

- Issue body — bounded scope; explicit "needs its own resource intelligence, plan, adversarial review, and explicit approval".
- Closed [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) and [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) plan/closeout comments — establishes typical-ship YAML pattern, packaged-data discipline, output-contract style, and the explicit caveat phrasing "preliminary, not MMG/CFD/sea-trial validation".
- `docs/session-handoffs/2026-04-30-rudder-stock-torque-closeout.md` — recommends turning-circle as next bounded calc.
- Prior session draft `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md` — earlier T3 plan; selected first-order Nomoto with K/T as user inputs. **Reviewed and partially adopted; the curves.py claim there is wrong (verified).**

### Gaps identified

- **No** turning-circle estimator module; must create.
- **No** packaged turning-circle YAML; must create.
- **No** trajectory-integration helper; the existing `nomoto_steady_yaw_rate()` is steady-state scalar only.
- **No** advance/transfer/tactical-diameter extraction helpers.
- **No** wiki page for turning-circle methodology specifically (validation metrics page exists but is criteria-only).
- **No** [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) standards-page promotion (IMO MSC.137(76)) under `wiki/standards/` — currently only criteria are reproduced inline in concepts/. **Decision below: promote or defer?**

### Evidence (embedded verification)

**Issue status** (verified 2026-05-02 via `gh issue view 2568`):
- [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) — OPEN — "feat(naval-arch): preliminary turning-circle and tactical-diameter estimator input workflow"
- Labels: `enhancement`, `priority:medium`, `cat:engineering-calculations`, `domain:hydrodynamics`, `domain:naval-architecture`, `wip:ace-linux-1`, `status:plan-approved` (preexisting from a prior session — Team-4 did NOT add this label)

**File existence** (`ls -la` 2026-05-02):
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py`
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py`
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py`
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml`
- EXISTS: `digitalmodel/src/digitalmodel/naval_architecture/data/rudder_stock_torque_typical_ship.yml`
- EXISTS: `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` (test stub written 2026-05-01)
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/naval_architecture/turning_circle.py`
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/naval_architecture/data/turning_circle_typical_ship.yml`
- MISSING (this plan creates): `digitalmodel/docs/domains/marine-engineering/turning-circle-estimator.md`
- DOES NOT EXIST: `digitalmodel/src/digitalmodel/naval_architecture/curves.py` (contradicts prior 2568 draft)

**Distinct sources counted: 8 (issue body + #2564 + #2565 + digitalmodel source + 6 wiki pages + 4 /mnt/ace standards PDFs + prior draft plan).**

---

## Decision: Estimator Model Choice

Three viable preliminary models. **Recommendation = Option A (first-order Nomoto with user-supplied K/T).** Rationale embedded.

### Option A — First-order Nomoto K/T trajectory integrator (RECOMMENDED)

| Dimension | Detail |
|---|---|
| Model | `T * dr/dt + r = K * delta`; integrate `r`, then `psi`, then earth-fixed `(x, y) = ∫ V*(cos psi, sin psi) dt` at constant `V`. |
| Inputs needed | `K_per_s`, `T_s`, `speed_m_s`, `rudder_angle_deg`, `duration_s`, `dt_s`. All user-supplied via YAML. No hull-form derivation. |
| Outputs supported | advance, transfer, tactical diameter, steady turning diameter (when convergence trailing-window check passes), turn-rate response, time histories. |
| Fidelity | Order-of-magnitude design estimate. Captures the right speed/rudder-angle scaling trends. **Misses:** speed loss in turn, sway/drift coupling, hull-propeller-rudder interaction, transient overshoot (those need 2nd-order Nomoto or MMG). |
| Scope risk | Low. ODE is one-line, deterministic, well-conditioned for `T > 0`, `dt ≤ T/20`. |
| Validation pathway | (1) zero-rudder ⇒ straight path; (2) sign symmetry ±delta; (3) dt-refinement convergence; (4) `r_ss = K*delta` matches existing `nomoto_steady_yaw_rate()`; (5) tactical diameter consistent with `R = V / r_ss` envelope at infinite duration. |
| Data the user is likely to have | K and T are commonly tabulated for typical ships in EN400, PNA Vol. III, Bertram. The packaged sample YAML can ship with reasonable defaults (e.g., K=0.12 s⁻¹, T=20 s for a tanker per the existing test stub). |

**Why recommended:** matches existing test stub already on disk; matches `maneuverability.py` `nomoto_steady_yaw_rate()` vocabulary; constant-speed simplification is documented as out-of-scope for speed loss; metric set in test stub maps directly; complexity stays T3 not T4.

### Option B — Empirical Lyster-Knoll regression for tactical diameter

| Dimension | Detail |
|---|---|
| Model | Lyster & Knoll (1974) regression: `tactical_diameter / L = f(L/B, B/T, Cb, A_R / (L*T), delta)`. Curve-fit from 200+ vessels. |
| Inputs needed | `length_m`, `beam_m`, `draft_m`, `block_coefficient`, `rudder_area_m2`, `rudder_angle_deg`. **No K/T required.** |
| Outputs supported | tactical diameter only. Advance/transfer would need a second regression (Inoue or Clarke 1983). No turn-rate time history. |
| Fidelity | Statistical for "typical merchant ship"; degraded outside training envelope. |
| Scope risk | Medium. Requires sourcing and validating the regression coefficients — that means a new wiki promotion of Lyster & Knoll, and a `Citation` schema obligation per `.claude/rules/calc-citation-contract.md`. |
| Validation pathway | Reproduce a published worked example from Lyster & Knoll within ±5%. |
| Data the user is likely to have | Hull-form principal dimensions are easier to obtain than K/T. |

**Why not recommended:** introduces standards-derived constants ⇒ citation contract trigger ⇒ wiki promotion of Lyster-Knoll ⇒ blocks on a separate ingest step. Issue body says "preliminary"; regression is single-output.

### Option C — Simplified MMG-lite (3-DOF Abkowitz/Norrbin truncated)

| Dimension | Detail |
|---|---|
| Model | 3-DOF surge/sway/yaw with non-dimensional hydrodynamic derivatives (`Y_v'`, `N_r'`, `Y_r'`, `N_v'`, etc.). |
| Inputs needed | 12-20 hull/rudder hydrodynamic derivatives. Captive-model or PMM-derived. |
| Outputs supported | Full turning trajectory, advance/transfer/tactical diameter, zig-zag, spiral. |
| Fidelity | High when derivatives are accurate. Low when they are not. |
| Scope risk | **High.** User is unlikely to have 12+ derivatives for a "typical ship" without a separate database. Issue body explicitly excludes "full MMG". |
| Validation pathway | Cross-check against published trial data (e.g., KVLCC2, Mariner). |
| Data the user is likely to have | **Not realistic for a preliminary estimator.** |

**Why not recommended:** out-of-scope per issue body.

### Decision

**Option A — first-order Nomoto with user-supplied K/T.** Fallback question for user (open question O1 below): would you prefer Option A be deferred and Option B planned with a Lyster-Knoll wiki promotion as a paired follow-up issue?

---

## Deliverable

A `turning_circle.py` module in `digitalmodel/src/digitalmodel/naval_architecture/` that loads a packaged typical-ship YAML, integrates a first-order Nomoto model over a speed × rudder-angle grid at constant speed, extracts advance / transfer / tactical-diameter / steady-turning-diameter metrics with explicit null+warning behavior when targets are not reached, and writes CSV/JSON tables, provenance sidecar, artifact manifest, and four required charts. **Outputs are preliminary engineering estimates, NOT validated against MMG, CFD, or sea-trial data, and do NOT constitute IMO/ABS compliance proof.**

---

## YAML Input Schema (extends [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) / [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) convention)

```yaml
# digitalmodel/src/digitalmodel/naval_architecture/data/turning_circle_typical_ship.yml
case:
  id: typical_single_screw_turning_circle
  description: >-
    Preliminary first-order Nomoto turning-circle / tactical-diameter
    estimator for a typical ship. Constant forward speed, user-supplied K/T,
    no MMG/CFD/sea-trial validation, no IMO/ABS compliance claim.

vessel:
  type: typical_single_screw_ship
  length_between_perpendiculars_m: 180.0
  beam_m: 28.0
  draft_m: 10.0
  design_speed_kn: 15.0

rudder:
  area_m2: 20.0
  span_m: 5.0
  behind_hull: true   # informational only; not used by Nomoto integrator

# NEW SECTION (extension over #2564/#2565)
nomoto:
  K_per_s: 0.12
  T_s: 20.0
  K_T_source: >-
    User-supplied first-order Nomoto indices. Typical merchant ship defaults
    derived from EN400 Ch.9 and PNA Vol. III worked examples. Replace with
    vessel-specific values from spiral-test or zig-zag-test fitting before
    using outputs for any design decision.
  K_sign_convention: >-
    Positive K means positive rudder angle (starboard) produces positive
    yaw rate (bow-to-starboard) under the +x forward / +y starboard / +z down
    body-fixed convention reused from existing maneuverability module.

simulation:
  duration_s: 600.0
  dt_s: 1.0
  # Hard constraint: dt_s <= T_s / 20 unless step-sensitivity test is run.

sign_convention:
  axes: "+x forward, +y starboard, +z down (body-fixed); earth-fixed (X,Y) reported in rows"
  positive_rudder_angle: starboard
  positive_yaw_rate: bow_to_starboard
  heading_zero: initial_heading_at_t0

environment:
  rho_kg_m3: 1025.0   # informational; not used by Nomoto integrator at constant speed

sweep:
  speeds:
    units: kn
    values: [10.0, 15.0]
  rudder_angles_deg: [10.0, 20.0, 35.0]

outputs:
  directory: results/turning_circle_typical_ship
  tables: [csv, json]
  sidecars:
    provenance: turning_circle_provenance.json
    artifact_manifest: artifact_manifest.json
  charts:
    enabled: true
    formats: [png, html]
    required:
      - trajectory_by_case
      - yaw_rate_vs_time
      - heading_vs_time
      - turning_metrics_vs_rudder_angle

warnings:
  scope_limitations:
    - Preliminary first-order Nomoto trajectory estimator at constant forward speed.
    - K and T are user inputs; outputs are illustrative engineering estimates only.
    - Does NOT model speed loss in turn, sway/drift dynamics, hull-propeller-rudder interaction, or environmental loads.
    - Does NOT validate IMO MSC.137(76), ABS, or USCG NVIC 6-95 compliance.
    - Not a substitute for MMG simulation, CFD, or sea-trial data.
    - Steady turning diameter reported only when trailing-window yaw-rate convergence test passes.
    - Advance/transfer/tactical diameter reported as null with warning when heading targets (90°/180°) are not reached within `duration_s`.
```

**Compatibility verification with [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) / [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565):**
- `case`, `vessel`, `rudder`, `environment`, `sweep`, `outputs` blocks: identical structure (verified).
- New blocks `nomoto`, `simulation`, `sign_convention.positive_rudder_angle/positive_yaw_rate`: do not collide with existing field names in either predecessor YAML (verified).
- `warnings.scope_limitations` list: matches [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) precedent.
- `outputs.charts.required` exact 4-chart list: matches existing test stub (verified line 99-104 of `test_turning_circle_estimator.py`).

**Sign-convention divergence flagged:** The packaged YAML in [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) uses `+y port` (line 15 of `yaw_moment_typical_ship.yml`). The Nomoto code in `maneuverability.py` is silent on body-fixed handedness. **Open question O2 below:** does the user want this estimator to use `+y port` (matching #2564) or `+y starboard` (the more common naval-architecture textbook convention)? The plan currently proposes `+y starboard`, which is INCONSISTENT with #2564 and must be reconciled before implementation.

---

## Output Deliverables

| Output | Source | Caveat |
|---|---|---|
| `advance_m` | linear interpolation of `(x_m, y_m)` between time steps when `heading_deg` crosses 90° (sign of rudder angle aware) | null + warning if target not reached in `duration_s` |
| `transfer_m` | lateral displacement at the same 90°-crossing instant | null + warning if not reached |
| `tactical_diameter_m` | lateral displacement at the 180°-crossing instant | null + warning if not reached |
| `steady_turning_diameter_m` | `2 * V / r_ss` where `r_ss` is mean yaw rate over a trailing window when convergence passes | null + warning if convergence fails |
| `turn_rate_response` | full `r(t)` time history written to time-history CSV | always emitted |
| Trajectory | full `(x_m, y_m, heading_deg)` time history | always emitted |
| Steady-state checks | `r_ss_predicted = K * delta_rad` (from existing `nomoto_steady_yaw_rate()`) included in metrics row for cross-validation | warning if observed `r_ss_observed` differs from predicted by > 5% |

**Explicit `metric_status` field per row:** one of `ok`, `warning`, `null_target_not_reached`, `null_convergence_fail`. Test stub already expects this (line 86).

**Charts (matches existing test stub):**
1. `trajectory_by_case` — `(x_m, y_m)` paths by speed/rudder-angle case.
2. `yaw_rate_vs_time` — `r(t)` curves by case.
3. `heading_vs_time` — `psi(t)` curves by case.
4. `turning_metrics_vs_rudder_angle` — advance/transfer/tactical-diameter vs rudder angle, grouped by speed.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/naval_architecture/turning_circle.py` | Estimator + YAML loader + sweep runner + CSV/JSON/chart writers + provenance sidecar |
| Create | `digitalmodel/src/digitalmodel/naval_architecture/data/turning_circle_typical_ship.yml` | Packaged sample input |
| Modify | `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Public exports `simulate_nomoto_turning_circle`, `load_packaged_turning_circle_yaml`, `run_turning_circle_sweep`, `write_turning_circle_results` |
| Verify (read-only) | `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` | Already exists; this plan locks the API surface to it. **Do not modify** unless the user approves an API change. |
| Create | `digitalmodel/docs/domains/marine-engineering/turning-circle-estimator.md` | Methodology, inputs, outputs, caveats |
| Update | `digitalmodel/pyproject.toml` package-data glob | Only if `naval_architecture/data/*.yml` glob does not already match new YAML. Verify before editing. |
| Update | `docs/plans/README.md` | Add this plan row |

---

## TDD Test List (locked to existing test stub)

| Test name (already in `test_turning_circle_estimator.py`) | What it verifies |
|---|---|
| `test_nomoto_response_zero_rudder_stays_straight` | Zero rudder ⇒ straight path, null advance/transfer |
| `test_nomoto_response_sign_symmetry` | ±delta produces mirrored y/heading/tactical-diameter |
| `test_nomoto_time_step_reduction_stability` | dt-refinement converges within 3% |
| `test_metrics_warn_when_heading_target_not_reached` | Short duration ⇒ null metrics + warning + `metric_status="warning"` |
| `test_packaged_turning_circle_yaml` | YAML loads via `importlib.resources`; required 4 chart names exact |
| `test_packaged_yaml_in_built_distribution` | Wheel build includes new YAML AND existing `yaw_moment_typical_ship.yml` (no package-data regression) |
| `test_output_artifacts_and_charts` | CSV time-history + metrics, JSON, provenance, manifest, all 4 charts in PNG+HTML |
| `test_no_compliance_overclaim` | provenance + docs both contain "preliminary" + "not MMG" + "not...compliance" + "IMO" + "ABS" |
| `test_public_import_surface` | Top-level `digitalmodel.naval_architecture` exports the 4 public symbols |

**Plan adds (not in stub yet — must be added during TDD-red phase):**
| Test name | What it verifies |
|---|---|
| `test_steady_state_yaw_rate_matches_nomoto_helper` | Long-duration steady r_ss matches `nomoto_steady_yaw_rate(K, delta)` within 1% |
| `test_steady_turning_radius_matches_V_over_r_ss` | Tactical diameter ≈ `2 * V / r_ss` for long-duration runs (sanity envelope) |
| `test_invalid_dt_exceeds_T_over_20_rejected_or_warned` | `dt_s > T_s / 20` raises ValueError OR emits explicit step-sensitivity warning |
| `test_metric_status_field_present_in_every_row` | every metrics row has `metric_status` ∈ `{ok, warning, null_target_not_reached, null_convergence_fail}` |

---

## Acceptance Criteria

- [ ] All existing tests in `test_turning_circle_estimator.py` pass.
- [ ] Plan-added tests above are implemented and pass.
- [ ] `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_maneuverability.py tests/naval_architecture/test_yaw_moment_sweep.py tests/naval_architecture/test_rudder_stock_torque_sweep.py tests/naval_architecture/test_turning_circle_estimator.py -q` passes (regression slice).
- [ ] `UV_NO_SYNC=1 uv run --with ruff ruff check src/digitalmodel/naval_architecture/turning_circle.py tests/naval_architecture/test_turning_circle_estimator.py src/digitalmodel/naval_architecture/__init__.py` passes.
- [ ] Smoke run: `PYTHONPATH=src UV_NO_SYNC=1 uv run python -c "from digitalmodel.naval_architecture import load_packaged_turning_circle_yaml, run_turning_circle_sweep, write_turning_circle_results; ..."` produces 6 sweep rows (2 speeds × 3 angles), CSV, JSON, provenance, manifest, 4 charts × 2 formats.
- [ ] Wheel build includes both new and existing package-data YAML files.
- [ ] Documentation explicitly states preliminary scope and excludes MMG/CFD/sea-trial validation and IMO/ABS compliance.
- [ ] Provenance sidecar includes formula `T*dr/dt + r = K*delta`, K/T source as user input, list of unmodeled physics.
- [ ] No new standards-derived numeric constants introduced (verified by code review).
- [ ] Adversarial review on implementation returns no unresolved MAJOR before close.

---

## Wiki Promotion Decision

**Recommendation: defer wiki standards-page promotion of IMO MSC.137(76) until a separate validation issue.** Rationale:

1. This estimator does not use IMO MSC.137(76) constants computationally; it only references the criteria in the docs caveat.
2. Wiki promotion under `wiki/standards/` requires `code_id`, `publisher`, `revision` frontmatter and a `Citation` schema target. Adding it for caveat-only context would trigger fail-closed citation resolution at runtime for no engineering benefit.
3. Existing concept page `maneuvering-validation-metrics.md` already reproduces the criteria with raw locators — sufficient for caveat reference.

**If the user disagrees**, open question O3 below: should IMO MSC.137(76) be promoted to `wiki/standards/imo-msc-137-76.md` as a paired prerequisite issue before implementation?

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| **Silent overconfidence in preliminary estimator** — users treat tactical-diameter output as design-grade. | P1 | Three layers: (a) docstring on every public function says "preliminary, not validated"; (b) provenance sidecar lists 6 unmodeled physics items; (c) `test_no_compliance_overclaim` enforces caveat phrasing in both provenance and docs. |
| Sign-convention drift from [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) (port vs. starboard). | P1 | Open question O2 must resolve before implementation. Plan currently proposes starboard; #2564 uses port. **DO NOT IMPLEMENT until reconciled.** |
| Pre-existing test stub (`test_turning_circle_estimator.py`) locks API to a design that a reviewer might reject. | P2 | Plan calls out the stub explicitly; if review rejects an API element, plan must be updated and stub must be modified before TDD-red. |
| Metric extraction at heading thresholds is numerically fragile (one-step overshoot of 90°/180°). | P2 | Linear interpolation between adjacent time steps is required; covered by `test_metrics_warn_when_heading_target_not_reached`. Add a finer test for interpolation accuracy at default dt. |
| K/T defaults shipped in packaged YAML may be misinterpreted as canonical "typical ship" values. | P2 | Provenance sidecar and YAML `K_T_source` field both label them as "user-supplied; replace before design use". |
| Plotting dense time histories (600s × 1s × 6 cases = 3,600 points) creates large HTML chart files. | P3 | Default sweep grid is small (2 × 3 = 6 cases); HTML chart reasonable size; PNG always small. |
| Existing `status:plan-approved` label on issue (preexisting) could trigger autonomous batch execution before user reviews this Team-4 plan. | P1 | **Mitigation: Team-4 final action will surface this in the approval-request comment so user can re-confirm or downgrade label.** |

---

## Out of Scope

- Full MMG (sway/yaw coupling, hull/propeller/rudder interaction modeling).
- CFD verification.
- Sea-trial correlation studies.
- Speed loss in turn during the trajectory (could be added as Option A.5 in a follow-up; existing `speed_in_turn()` helper is available but not wired).
- Zig-zag / overshoot tests (10°/10°, 20°/20°).
- Spiral test simulation.
- Stopping-distance simulation.
- IMO MSC.137(76) compliance pass/fail evaluation.
- ABS rating computation `Rt = 0.25 * (Rtd + ...)`.
- Second-order Nomoto, Norrbin nonlinear extension, or Bech 1968 extension.
- Standards-page wiki promotion of IMO MSC.137(76).

---

## Adversarial Review Summary

See `docs/reports/2568-plan-r1-adversarial-review.md` (Team-4, r1).

| Reviewer | Verdict | Defect count |
|---|---|---|
| Team-4 r1 (this plan) | MAJOR | 4 P1, 3 P2, 2 P3 |

**Overall result:** plan-review (FAIL until P1 defects acknowledged or fixed by user decision on O1/O2/O3).

---

## Open Questions for the User

1. **O1 — Model choice.** Plan recommends Option A (first-order Nomoto with K/T). Confirm? Or prefer Option B (Lyster-Knoll regression — adds wiki promotion prerequisite) or defer?
2. **O2 — Sign convention.** [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) packaged YAML uses `+y port`. This plan proposes `+y starboard` (more common in textbook Nomoto). **Which should this estimator use?** Implementation cannot start until reconciled; mismatched sign conventions across the maneuvering calc family create subtle bugs.
3. **O3 — Wiki promotion.** Plan defers IMO MSC.137(76) standards-page promotion. Confirm defer, or pair with a prerequisite promotion issue?
4. **O4 — Pre-existing `status:plan-approved` label.** Was this carried over from an earlier session that Team-4 cannot see? Confirm whether the existing draft plan (`2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md`) was the one approved, or whether label needs to be downgraded to `status:plan-review` while you compare both plans.

---

## Complexity: T3

**T3** — new estimator module with numerical ODE integration, metric extraction with interpolation, output artifact contract with provenance, packaged YAML, regression-test slice across 4 test files, explicit caveat enforcement.
