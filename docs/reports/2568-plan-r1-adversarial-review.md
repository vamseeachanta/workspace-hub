# Adversarial review r1 — [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) turning-circle estimator plan

> **Reviewer:** Team-4 (Claude, ace-linux-1) — single-author hostile review
> **Plan under review:** `docs/plans/2568-turning-circle-estimator-plan.md` (rev: as written 2026-05-02)
> **Sibling draft also on disk:** `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md`
> **Stance:** defect-hunting; charitable readings rejected per `feedback_adversarial_review_stance.md`
> **Date:** 2026-05-02

---

## Verdict: **MAJOR** — 9 defects (4 P1 / 3 P2 / 2 P3)

The plan is well-researched and correctly identifies the existing test stub, but it ships with **four P1 defects that block implementation safety**:

- Sign convention contradicts predecessor [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) and the contradiction is acknowledged but not resolved.
- A pre-existing test stub locks the API and exposes the plan to a stub-was-wrong failure mode that is not addressed.
- The `status:plan-approved` label was already on the issue when Team-4 started; the plan does not interrogate whether earlier autonomous batch dispatch is already in flight.
- The sibling draft plan disagrees with this plan on key model decisions, and the plan does not propose a reconciliation gate.

Recommend MAJOR → re-draft after user resolves O1, O2, O3, O4 listed in the plan, then re-review at r2.

---

## Defect 1 (P1) — Sign-convention conflict with [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) is flagged but not resolved

**Location:** Plan section "YAML Input Schema", `sign_convention.axes` field; plan section "Risks and Mitigations" risk row 2; open question O2.

**Why it matters:** The packaged YAML at `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` line 15 declares `+x forward, +y port, +z up`. This plan proposes `+x forward, +y starboard, +z down`. Both predecessors ([#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564), [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565)) shipped against the port-positive / z-up convention. If [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) ships starboard-positive / z-down, the four maneuvering modules (`maneuverability.py`, `yaw_moment.py`, `rudder_stock_torque.py`, `turning_circle.py`) will silently disagree on yaw-rate and lever-arm sign — exactly the bug class that produces "passes tests, fails in production" outcomes for naval architects who paste outputs from one workflow into another.

The plan flags this as an "Open question O2" but lists implementation acceptance criteria as if it could proceed once approved. **It cannot.** A plan that marks itself as "ready for user approval" while admitting a sign-convention mismatch with the family it joins is internally inconsistent.

**Recommended fix:**
1. Resolve O2 in the plan body, not as an open question. Default to `+y port, +z up` to match [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) / [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) unless the user explicitly elects starboard.
2. Add a regression test that verifies `simulate_nomoto_turning_circle(positive_rudder=+10)` produces a yaw rate sign matching `nomoto_steady_yaw_rate(K, +10)` from `maneuverability.py`. This catches sign drift at the unit-test boundary.
3. Add an explicit acceptance-criterion line item: "All four modules (`maneuverability`, `yaw_moment`, `rudder_stock_torque`, `turning_circle`) declare and use the same body-fixed convention; CI test `test_maneuvering_module_family_sign_consistency` enforces this."

---

## Defect 2 (P1) — Pre-existing test stub locks the API; plan defers risk to "if review rejects"

**Location:** Plan "TDD Test List" preface ("locked to existing test stub"); "Files to Change" row marked "Verify (read-only)"; "Risks and Mitigations" P2 row.

**Why it matters:** A test stub written 2026-05-01 (between [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) close and Team-4 dispatch) precommits the public function names, the metric dict shape (including `metric_status`), the chart-name list, and the wheel-build assertion. The plan accepts this stub as ground truth without adversarial review of the stub itself.

The stub has at least three contestable design choices:

1. `simulate_nomoto_turning_circle()` takes K, T, speed, rudder_angle, duration, dt as keyword arguments — but the family precedent is to take a `vessel`/`rudder`/`environment` dataclass. This stub diverges from [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) / [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) ergonomics.
2. The `test_no_compliance_overclaim` test (line 192) asserts substrings `"preliminary"`, `"not mmg"`, `"imo"`, `"abs"` in the generated docs file. This pre-decides that the docs must mention IMO and ABS, even though the plan correctly argues IMO promotion should be deferred.
3. The `test_packaged_yaml_in_built_distribution` test (line 112) requires both YAML files to be in the built wheel, which works only if `pyproject.toml` package-data glob is broad enough. Plan does not verify this.

The plan's mitigation ("if review rejects an API element, plan must be updated and stub must be modified before TDD-red") **is the wrong direction**: a stub written before plan review is the tail wagging the dog. Team-4 plan should treat the stub as a reviewable artifact, not a precommitment.

**Recommended fix:**
1. Add a "Pre-implementation gate: review the test stub" section. Either ratify each test as load-bearing or rewrite it during TDD-red.
2. Re-justify the `simulate_nomoto_turning_circle(**kwargs)` ergonomic against the [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) `run_yaw_moment_sweep(config)` pattern. Either match the predecessor or document why turning-circle is different.
3. Verify `pyproject.toml` package-data glob currently matches `naval_architecture/data/*.yml`; if not, plan must add a modify row.

---

## Defect 3 (P1) — `status:plan-approved` label already on the issue is not investigated

**Location:** Plan "Evidence (embedded verification)" issue-status block; plan "Risks and Mitigations" final P1 row.

**Why it matters:** The plan correctly notes that [#2568](https://github.com/vamseeachanta/workspace-hub/issues/2568) carries a `status:plan-approved` label that Team-4 did not add. It does not investigate **what** was approved. Possibilities:

- The earlier draft plan (`2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md`) was approved by the user and Team-4 is duplicating work that should not be re-approved.
- An autonomous batch agent self-approved (forbidden per `feedback_never_offer_to_self_label_plan_approved.md`).
- The label was carried over from a parent-issue label propagation script.
- A nightly batch is currently executing under the existing label.

This is a **load-bearing user-in-loop gate**. Team-4 dispatch instructions explicitly say "DO NOT add `status:plan-approved` label" and "deliverable lands at `status:plan-review`". The plan as written does not surface enough evidence for the user to safely make this call.

**Recommended fix:**
1. Immediately before user approval, run `gh issue view 2568 --json timelineItems` (or similar) to identify when and by whom `status:plan-approved` was applied. Include that in the approval-request comment.
2. Add a hard gate in plan acceptance criteria: "`status:plan-approved` label provenance is verified; if applied autonomously or by a prior session, user must re-confirm before any implementation runs."
3. Cross-check whether `.planning/plan-approved/2568.md` marker file exists locally. If yes, what plan does it bind to (SHA-bound per [#2460](https://github.com/vamseeachanta/workspace-hub/issues/2460))?

---

## Defect 4 (P1) — Sibling plan on disk is not reconciled

**Location:** Plan top frontmatter ("Sibling draft on disk"); plan does not call out divergence in body.

**Why it matters:** `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md` exists from a prior session and shipped at `status:plan-review`. The Team-4 plan acknowledges its existence but does not enumerate the divergences. There are at least three:

1. **Path naming.** Earlier plan uses dated `YYYY-MM-DD-issue-NNNN-slug.md`; Team-4 plan uses `NNNN-slug-plan.md`. The dated form matches all 4 plans in the same family. Team-4 path is non-conforming.
2. **Decision framing.** Earlier plan jumps directly to first-order Nomoto without a multi-option decision section. Team-4 plan offers Options A/B/C and recommends A. If the user already approved earlier plan, Team-4's Options B/C are wasted ink.
3. **API surface.** Both plans define the same module/function names (matching the test stub). They do not conflict on the implementation surface, but they do conflict on which document is canonical.

A user comparing the two plans will not know which one to act on. This is exactly the failure mode that drives the "plan past-tense drift" memory entry.

**Recommended fix:**
1. Either: declare Team-4 plan supersedes the earlier draft, with explicit sign-off that the Options B/C analysis was worth re-doing; **or** declare Team-4 plan is a peer-review of the earlier draft that adds option analysis and adversarial findings only.
2. If superseding, move the earlier draft to `docs/plans/_superseded/` or annotate it with a `> superseded by NNNN-slug-plan.md` line.
3. Add a "Plan reconciliation" subsection at the top of the chosen canonical plan listing the divergences from the other.

---

## Defect 5 (P2) — Convergence-window definition is hand-waved

**Location:** Plan "Output Deliverables" row for `steady_turning_diameter_m`; "Hard-stop / model-boundary gate" inherits this from the earlier draft (which the Team-4 plan does not).

**Why it matters:** The plan says steady turning diameter is reported "when convergence trailing-window check passes" but does not define the window length, tolerance, or what "convergence" means quantitatively. This is the kind of unstated hyper-parameter that causes implementations to silently diverge between developers.

**Recommended fix:** add a numerical-contract subsection: e.g., "trailing window = last 10 × T_s of the trajectory; convergence passes when `max(r) - min(r) < 0.01 * mean(r)` over the window; otherwise emit `null_convergence_fail` with metric_status `null`." Make this testable.

---

## Defect 6 (P2) — Tactical diameter sign and reference-point definition are ambiguous

**Location:** Plan "Output Deliverables" `tactical_diameter_m` row.

**Why it matters:** Tactical diameter is defined in PNA / IMO MSC/Circ.1053 as the distance between two parallel headings (initial and 180°-reversed) — i.e., a magnitude, always positive. The test stub at line 49 asserts `port["tactical_diameter_m"] == pytest.approx(-starboard["tactical_diameter_m"], rel=1e-3)` — i.e., it is signed. These two definitions disagree.

If the implementation follows the test stub, the output deviates from textbook convention. If the implementation follows the textbook, the test fails. The plan does not pick a side.

**Recommended fix:** define `tactical_diameter_m` as signed lateral displacement at 180° heading change (i.e., test-stub semantics) AND add a separate `tactical_diameter_abs_m` matching textbook convention. Document both. This mirrors the [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565) precedent of emitting both signed and absolute torque.

---

## Defect 7 (P2) — Default sweep grid is too sparse to validate dt-stability claim

**Location:** Plan YAML proposal `sweep` section (2 speeds × 3 angles = 6 cases).

**Why it matters:** The `test_nomoto_time_step_reduction_stability` test (line 64-77 of stub) asserts coarse vs fine `dt` agree within 3% on tactical diameter. With only 6 cases, a single numerically borderline case (e.g., 35° hard-over) could bring the entire suite below 3% by accident. The earlier draft plan used `[0, 2, 5, 10, 15]` knots × `[-35, -20, -10, 0, 10, 20, 35]` degrees = 35 cases — same as [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564).

**Recommended fix:** match predecessor's 35-case grid for the packaged YAML (consistency benefit) and validate that 600s × 1s × 35 cases = 21,000 trajectory points still produces sub-MB chart artifacts. If too large, reduce duration to 300s for the packaged sample.

---

## Defect 8 (P3) — `behind_hull` field declared "informational only" but conflicts with [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) where it is load-bearing

**Location:** Plan YAML `rudder.behind_hull` field comment.

**Why it matters:** In [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564), `behind_hull: true` doubles the effective rudder aspect ratio (mirror effect) in `rudder_lift_coefficient()`. The Nomoto integrator at constant speed does not use rudder force, so the field is genuinely informational here. But shipping the same YAML key with two different semantics across the family is a confusing footgun for a user who copies their #2564 YAML.

**Recommended fix:** rename to `rudder.behind_hull_informational` OR drop the field entirely from this YAML and document that turning-circle estimator does not consume rudder hydrodynamics. Cleaner.

---

## Defect 9 (P3) — Plan does not state `digitalmodel` is a separate git repo

**Location:** Throughout "Files to Change".

**Why it matters:** Per `digitalmodel/CLAUDE.md` and the global memory entry, `digitalmodel/` is a separately-versioned git repository nested inside workspace-hub. Implementation will require `cd digitalmodel/` before commits; main session must serialize commits in two repos. Plan does not call this out.

**Recommended fix:** add a one-line execution-environment note: "Implementation files under `digitalmodel/src/` and `digitalmodel/tests/` commit to the `digitalmodel` repo, not workspace-hub. Plan/docs/review files under `docs/` commit to workspace-hub."

---

## Specific defect checks requested by dispatch prompt

> Specifically check: is the YAML schema actually compatible with [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564)/[#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565)? Does the model choice have data inputs the user is unlikely to have? Are units explicit? Is "preliminary" disclaimer load-bearing?

| Check | Verdict | Evidence |
|---|---|---|
| YAML schema compatibility | **Partial.** Block structure is compatible, but the `sign_convention.axes` value is incompatible (Defect 1). New `nomoto.*` and `simulation.*` blocks do not collide. | YAML compared field-by-field to both predecessor YAMLs. |
| Inputs the user is unlikely to have | **Mostly OK.** Option A asks for K and T, which are tabulated for typical merchant ships in EN400 Ch.9 and PNA Vol. III. Default values shipped in YAML. **Risk:** the values shipped (K=0.12, T=20) are vessel-class specific and may not match the YAML's `length_between_perpendiculars_m: 180.0` / `displacement` profile. | EN400 Ch.9 worked example for a Mariner-class hull uses K~0.18, T~12. Tankers use K~0.04-0.08, T~30-50. Plan should disclose the reference vessel for the defaults. |
| Units explicit | **Yes**, but inconsistently. `m`, `s`, `rad`, `kg/m³`, `kn` all present and labeled. The new `K_per_s` field reads as `s^-1`; the field name `K_per_s` is correct but visually awkward — consider `K_inverse_seconds` for clarity. Minor. | Inspected all field names. |
| "Preliminary" disclaimer load-bearing | **Yes.** Three-layer enforcement (docstring + provenance sidecar + test). The `test_no_compliance_overclaim` test at line 192 of the stub asserts the substrings in both the JSON sidecar and the docs file. Strong. | Test code inspected. |

---

## Suggested r2 actions

1. User resolves O1 (model choice) — plan recommends Option A.
2. User resolves O2 (sign convention) — recommend port-positive to match [#2564](https://github.com/vamseeachanta/workspace-hub/issues/2564) / [#2565](https://github.com/vamseeachanta/workspace-hub/issues/2565).
3. User resolves O3 (wiki promotion) — recommend defer.
4. User resolves O4 (label provenance) — re-confirm `status:plan-approved` or downgrade to `status:plan-review`.
5. User picks canonical plan: this Team-4 plan or the earlier draft. Move the loser to `_superseded/`.
6. After O1-O5 closed, re-issue plan with defects 5/6/7 fixed inline (numerical contracts, signed/abs tactical diameter, denser default grid).
7. Re-run adversarial review at r2; expect MINOR or APPROVE.

---

## Provenance

- Reviewer: Team-4 (Claude, ace-linux-1) single-author hostile review per `feedback_permission_gate_blocks_cross_review.md` fallback pattern.
- Cross-provider review (Codex / Gemini) not run because Team-4 dispatch did not authorize cross-review.sh wrapper. User can request cross-review at r2.
- Defect-hunting stance per `feedback_adversarial_review_stance.md`.
