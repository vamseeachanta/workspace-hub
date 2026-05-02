# Adversarial engineering/resource-intelligence review — plans #2569 / #2570 / #2571

## Cross-issue evidence check
- The three plans repeatedly cite B1528 wiki/source pages under `knowledge/wikis/...`, but a workspace search returned **no local `*b1528*` or `*sirocco*` knowledge files**.
- A workspace search also returned **no local `.docx` benchmark notes** and no local `docs/projects/acma/B1528/...` tree yet.
- `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` is a bounded generic model with explicit scope `M_z = x_rudder_from_cg_m * transverse_force_N`; it is **not** the same thing as the workbook's legacy `0.6*LBP` lever unless that mapping is proven.
- `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` provides a Whicker/Fehlner-type static rudder force and a simple first-order Nomoto helper. Neither file currently supplies a B1528-specific source-backed mapping from AP-based geometry to CG-based lever arm, nor a validated dynamic coupling for SIROCCO.

Those facts make the source-contract and model-boundary language critical. The plans are strongest when they frame outputs as preliminary, source-bounded, and explicitly non-validated.

## #2569 — MINOR

**Why:** This is the right prerequisite issue, but the draft overstates source readiness. It needs a stricter evidence contract so downstream issues do not promote provisional workbook/narrative values into facts.

**Required revisions**
1. **Tighten source-status wording.** Do not say the wiki/source pages were "consulted" unless they exist in-tree or the plan embeds the retrieval evidence. Current workspace search did not find those files.
2. **Separate three distinct B1528 quantities in the source pack contract:**
   - rudder geometry values taken directly from workbook sheets/cells,
   - AP-based rudder-location values,
   - any derived CG-based lever arm required by `digitalmodel`.
   The plan currently risks treating `rudder center aft of AP = -1.052... m` and `yaw lever = 0.6*LBP = 135.3 m` as if they were interchangeable inputs.
3. **Require exact provenance fields for every number**: source file, sheet, cell/range if recoverable, units, extraction method, and status = `authoritative | derived | narrative | inferred | unavailable`.
4. **Add an explicit source-gap outcome** for the breakaway notes: if headings/times/track are too narrative for a numeric benchmark table, the deliverable must emit nulls plus a caveat table instead of a pseudo-precise benchmark.
5. **Normalize naming/alias evidence**: SIROCCO vs Sorrocco/SIROCCO must be captured once in the source pack so downstream reports do not imply separate vessels/cases.
6. **Add a downstream handoff field** stating which inputs are suitable for #2570 static regression, which are suitable only for #2571 descriptive overlays, and which are not numerically reusable.

## #2570 — MAJOR

**Why:** The draft is implementable only after it resolves a core engineering ambiguity: whether it is reproducing the workbook's legacy yaw-moment calculation or using the generic `digitalmodel` static model. Right now it blurs the two.

**Required revisions**
1. **Choose and name the model variants explicitly.** At minimum:
   - `workbook_regression` = legacy B1528 formula family using workbook-specific constants/lever assumptions.
   - `generic_static_model` = `digitalmodel` Whicker/Fehlner force + `M_z = x_rudder_from_cg * F_y`.
   The report may show both, but it must never compare one model's output to the other model's reference values as if they were identical.
2. **Do not hard-code the ±1° targets as universal truth** until #2569 proves the exact workbook formula, constants, unit conversions, and sign conventions. Current targets `+112.143` / `-98.454 kN-m` appear to depend on legacy `Cr` asymmetry and the `0.6*LBP` lever, which the generic `digitalmodel` model does not natively encode.
3. **Add a lever-arm mapping gate.** Before approval, the plan must state how AP-based/source-pack geometry becomes `x_rudder_from_cg_m` for `yaw_moment.py`, or else state that #2570 will remain in workbook-regression mode only.
4. **Bound the sweep domain.** The source evidence cited is strongest at 2.5 kn and ±1°. Any broader speed/angle sweep must be labeled illustrative and should have an explicit angle cap tied to the static rudder-force model's intended range; otherwise the charts invite over-reading.
5. **Keep benchmark language narrow.** Static regression should be against the workbook/source-pack only. Breakaway notes should not be used as quantitative validation for static yaw moment unless #2569 successfully normalizes them into numeric evidence.
6. **Add a required report table that distinguishes**:
   - source-backed workbook reference values,
   - derived `digitalmodel` inputs,
   - illustrative sweep outputs.
7. **Make sign convention reconciliation mandatory.** The plan mentions `Cr = 1.065/0.935` and +/- rudder cases; acceptance criteria should require explicit mapping between workbook port/starboard terminology and `digitalmodel`'s `positive_force_direction` / positive-yaw convention.
8. **Strengthen no-overclaim text.** The report should say this is a preliminary rudder-only static moment estimate, excluding hull drift, sway force balance, propeller slipstream modelling beyond whatever the workbook hard-codes, yaw inertia, and incident reconstruction.

## #2571 — MAJOR

**Why:** This draft still mixes incompatible dynamic abstractions. As written, it risks double-counting rudder effects and overclaiming trajectory fidelity from a first-order model with very sparse source evidence.

**Required revisions**
1. **Resolve the governing dynamic model before approval.** Pick one of these and exclude the other from the mainline deliverable:
   - **Nomoto response model:** `T r_dot + r = K * delta_eff`, where `K,T` already represent aggregate yaw response.
   - **Moment-driven yaw equation:** derive `r_dot` from computed yaw moment and an assumed inertia/damping model.
   The current pseudocode computes rudder-local inflow/yaw moment **and** advances a Nomoto `K/T` response, which is a classic double-counting risk.
2. **If keeping Nomoto, define `delta_eff` carefully.** `alpha_R = delta_cmd - beta_R` is only defensible as an effective rudder angle surrogate under small-angle/constant-speed assumptions and with explicit sign conventions. The plan must say this is a heuristic modifier, not source-validated SIROCCO physics.
3. **Document the geometric sign/reference assumptions for** `v_R = x_R r` and `beta_R = atan2(-x_R r, U)`. This requires `x_R` referenced from CG with aft locations negative; that is not the same as the workbook's AP-based rudder-center value.
4. **Add a hard boundary on track interpretation.** With `x_dot = U cos psi`, `y_dot = U sin psi` and no sway state, the trajectory is a heading-integrated path, not a full ship track model. Benchmark overlays against breakaway track evidence must be labeled descriptive only.
5. **Do not require force/moment time histories unless the model actually uses them consistently.** If the solver is Nomoto-based, force and yaw-moment traces are secondary diagnostics, not governing truth. The acceptance criteria should reflect that.
6. **Add an explicit coefficient-source rule.** If SIROCCO-specific `K` and `T` are unavailable, the report must either:
   - present user-assumed/scenario values with no benchmark-fit claim, or
   - fit illustrative values in a clearly separate calibration appendix.
   It must not imply the notes/workbook contain validated Nomoto coefficients.
7. **Benchmark handling must degrade gracefully.** Require a `source-gap` or `qualitative-only` benchmark mode when the breakaway notes do not support reliable time-history extraction.
8. **Strengthen no-overclaim language beyond MMG.** The report must explicitly disclaim sea-trial equivalence, incident reconstruction, predictive tactical diameter accuracy, and any claim that rudder inflow feedback here represents propeller-rudder-hull interaction physics.
9. **Keep the dependency chain explicit:** #2569 must land first for source normalization, and #2570 should land first unless #2571 fully owns a frozen duplicate of the B1528 input contract.

## Overall recommendation
- **#2569:** MINOR — approve after tightening the source/provenance contract.
- **#2570:** MAJOR — not approval-ready until workbook-vs-generic-model ambiguity is resolved.
- **#2571:** MAJOR — not approval-ready until the dynamic model is deconflicted and benchmark claims are narrowed.
