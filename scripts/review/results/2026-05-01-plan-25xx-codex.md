# Codex adversarial review: plans #2569 / #2570 / #2571

## #2569 — MINOR

### Verdict
MINOR — feasible, but tighten the structured-data and downstream-contract boundaries.

### What works
- Scope is appropriately documentation/data oriented.
- Creating a durable source pack before implementation is the right dependency order for #2570/#2571.
- Benchmark YAML is the right artifact shape for downstream tests and reports.

### Required revisions
1. **Define the benchmark YAML contract explicitly.**
   - Current plan says `benchmark_yaml_schema` but does not define required keys.
   - Add a minimal required structure such as: `source`, `datum_id`, `quantity`, `value`, `units`, `confidence`, `derivation`, `citation`, `notes`.
   - This is needed so #2570/#2571 can test against a stable machine-readable contract instead of ad hoc fields.

2. **Separate authoritative vs derived values unambiguously.**
   - The plan mentions this narratively, but downstream issues are at risk of mixing workbook values with derived lever arms and inferred benchmark points.
   - Require explicit flags for each datum: `authoritative`, `derived_from_source`, `narrative_only`, `inferred`.

3. **Add a downstream-safe field for moment-arm semantics.**
   - The extracted `0.6 * LBP = 135.3 m` is dangerous unless the YAML states exactly what it is relative to.
   - Add fields documenting reference origin and meaning, e.g. `x_reference_origin`, `x_reference_target`, `intended_use`.
   - This is necessary to prevent #2570 from treating a workbook yaw lever as the same thing as `x_rudder_from_cg_m`.

4. **State runtime boundary clearly: no source re-mining in downstream code.**
   - #2570/#2571 should consume only the normalized source-pack artifacts, not re-open workbook/docx/remote paths at runtime.
   - Add this as an acceptance criterion.

### Review note
Main risk is not feasibility but ambiguity propagation. Fix the schema/semantics now and downstream implementation gets much safer.

---

## #2570 — MAJOR

### Verdict
MAJOR — implementable, but the current plan leaves critical ambiguity around model identity, moment-arm semantics, and artifact boundaries.

### What works
- Reusing `digitalmodel.naval_architecture.yaw_moment` is the right starting point.
- Package-data approach is feasible: `digitalmodel/pyproject.toml` already includes `naval_architecture/data/*.yml`, so a new YAML in that folder should package cleanly.
- Existing tests already demonstrate the preferred patterns: `importlib.resources`, wheel-content check, temp-dir artifact generation.

### Required revisions
1. **Choose one static model and test to that model only.**
   - The plan currently says “run reusable yaw moment calculation or workbook-compatible regression mode” and test against workbook-like hand values “or documented model-equivalent”.
   - That is too loose for TDD and will allow silently shifting formulas.
   - Revise to one of:
     - **Option A:** project wrapper uses the existing `rudder_yaw_moment` model only, and tests assert that model’s outputs.
     - **Option B:** add an explicit separate workbook-compat mode with a separate function/API and separate expected values.
   - Do **not** allow one implementation with ambiguous acceptance targets.

2. **Resolve the moment-arm definition before implementation.**
   - Existing reusable code computes `M_z = x_rudder_from_cg_m * transverse_force_N`.
   - The plan cites a legacy `yaw lever = 0.6 * LBP = 135.3 m`, which is not obviously the same quantity as `x_rudder_from_cg_m`.
   - Required revision: define exactly which arm the B1528 YAML supplies, relative to what origin, and whether the workbook lever is used as:
     - direct moment arm in the report, or
     - source-only reference retained for comparison, not for computation.
   - Without this, the plan risks a wrong but numerically plausible report.

3. **Tighten regression tests to deterministic expectations.**
   - Replace `+112.143 kN-m approx or documented model-equivalent` with fixed expectations per chosen model.
   - If workbook regression is required, add a dedicated workbook-regression test name and target values.
   - If reusable-model outputs differ from workbook values, assert the reusable-model numbers and document the delta in the report.

4. **Keep generated report artifacts out of package/runtime contracts.**
   - The HTML report under `digitalmodel/outputs/...` should be a generated artifact, not something tests assume is committed.
   - Acceptance should require that tests generate HTML/CSV/JSON/provenance/manifest in a temp directory and verify contents there.
   - The durable checked-in artifact should be the markdown report and packaged YAML, not repo-persistent runtime output.

5. **Avoid unnecessary public-API surface unless truly reusable.**
   - A B1528-specific wrapper can exist, but do not expand `__init__.py` unless there is a real public API need.
   - Prefer a project-scoped module that imports the reusable engine, with tests targeting the module directly.

6. **Add a package-data verification specific to the B1528 YAML.**
   - Existing patterns already test packaged YAML and wheel inclusion for the typical-ship case.
   - Mirror that pattern for the B1528 YAML instead of treating `pyproject.toml` edits as assumed necessary.
   - In fact, the current wildcard likely means `pyproject.toml` may need no change; the plan should say “update if needed after verification,” not assume it.

### Review note
This plan is close, but not safe enough yet. Biggest issue: ambiguous reuse of workbook numbers versus the existing `yaw_moment.py` contract.

---

## #2571 — MAJOR

### Verdict
MAJOR — current dynamic formulation is not cleanly identifiable and risks double-counting yaw response.

### What works
- The need for a bounded preliminary dynamic report is valid.
- The proposed tests for zero-rudder, symmetry, and timestep sensitivity are good foundations.
- Depending on #2569 for normalized benchmark evidence is the right sequencing.

### Required revisions
1. **Separate dynamic model variants explicitly to avoid double-counting `K` and yaw moment.**
   - Current pseudocode computes rudder force/yaw moment from local inflow **and** evolves yaw with `r_dot = (K * alpha_R - r) / T`.
   - That is not clean unless force/moment is diagnostic only.
   - Required revision: define **one** of these architectures:
     - **Variant A: Nomoto-driven** — state update uses only `K`, `T`, and commanded/effective angle; force and moment are diagnostic outputs only and do not drive the state.
     - **Variant B: moment-balance-driven** — state update uses computed yaw moment plus inertia/damping terms; no Nomoto `K` in the state equation.
   - The plan must forbid mixing both in one state update.

2. **Clarify whether `alpha_R` feeds Nomoto as a modeling choice or is just a plotted diagnostic.**
   - Standard first-order Nomoto is already an identified input-output model. Replacing `delta` with dynamic `alpha_R` is a modeling extension and must be labeled as such.
   - Add a test and doc statement for the exact input signal to the dynamic model: `delta_cmd` or `alpha_R`.

3. **Do not make benchmark agreement depend on unknown `K`/`T`.**
   - The plan currently leaves `K` and `T` as calibration/assumption fields while also promising benchmark overlay.
   - Revise acceptance so that if project-specific `K`/`T` are unavailable, the deliverable becomes a scenario/sensitivity report with explicit non-calibrated status, not a benchmark-fit claim.
   - Add required sensitivity cases for at least a small grid of `K`/`T` assumptions if coefficients are not source-backed.

4. **Enforce clean execution boundaries between reusable engine and B1528 wrapper.**
   - Runtime code should consume normalized YAML from package data plus #2569 benchmark YAML, not read docx/workbook directly.
   - The reusable time integrator should be generic; the B1528 module should only assemble config/reporting.
   - Avoid `__init__.py` export unless a stable public API is justified.

5. **Make artifact tests temp-dir based, not repo-output based.**
   - Like #2570, `digitalmodel/outputs/b1528_sirocco/time_trace_report.html` should be generated in tests to a temporary directory.
   - Tests should verify manifest/provenance/time-series columns and chart presence, not committed output paths.

6. **Add explicit tests for model-boundary behavior.**
   - Required new tests:
     - `test_nomoto_variant_does_not_use_computed_yaw_moment_in_state_update`
     - or `test_moment_balance_variant_does_not_use_nomoto_K`
     - `test_zero_K_or_missing_K_handled_per_declared_variant`
     - `test_benchmark_overlay_degrades_to_source_gap_when_coefficients_unavailable`
   - These are needed to prevent accidental hybrid dynamics.

### Review note
This is the highest-risk plan of the three. It is feasible only after the state-equation architecture is made explicit and mutually exclusive.

---

## Overall
- **#2569:** MINOR
- **#2570:** MAJOR
- **#2571:** MAJOR

Primary blockers are:
- ambiguous static-model identity,
- unsafe moment-arm semantics,
- and hybrid dynamic logic that can double-count rudder/yaw effects via both computed moment and Nomoto `K`.
