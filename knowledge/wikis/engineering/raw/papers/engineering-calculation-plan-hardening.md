# Engineering calculation plan hardening reference

Session pattern: yaw-moment / rudder-stock-torque planning in `workspace-hub` and `digitalmodel` exposed recurring adversarial-review blockers for engineering-calculation issues.

## Use when

Use this reference when drafting or reviewing an engineering-calculation GitHub issue plan, especially for marine/offshore calculations with sign conventions, lever arms, output artifacts, citations, and package-data inputs.

## Required plan-hardening checks

1. **Separate physical quantities that are equal/opposite but easy to conflate.**
   - Do not emit one ambiguous field like `rudder_stock_torque_Nm` when the calculation may mean hydrodynamic torque exerted by flow or steering-gear holding torque.
   - Prefer explicit paired fields, e.g.:
     - `hydrodynamic_rudder_stock_torque_Nm`
     - `required_steering_gear_holding_torque_Nm = -hydrodynamic_rudder_stock_torque_Nm`
   - Define positive direction geometrically (e.g. rotation sense viewed from above), not by vague terms like "assists"/"resists".

2. **Define lever arms as force-line moment arms.**
   - A field such as `stock_to_center_of_pressure_arm_m` must state whether it is the perpendicular distance from the stock axis to the resultant force line of action.
   - Do not let a generic chordwise offset pass as a moment arm unless the plan explicitly defines the projection.
   - State excluded effects: center-of-pressure migration, stall, hull interaction, propeller slipstream, dynamic response.

3. **Make output artifacts exact and domain-specific.**
   - Name CSV, JSON, provenance/citation sidecar, manifest, and chart basenames explicitly.
   - Avoid copy/paste drift from predecessor workflows (e.g. yaw-moment chart names in a torque workflow).
   - If predecessor code returns an in-memory manifest but the new plan requires `artifact_manifest.json`, call that delta out and test it.

4. **Add non-tautological tests.**
   - Include one absolute physical sign case, not just `f(+x) == -f(-x)`.
   - Include direct identity tests like `torque == force * arm`, not only scaling ratios.
   - Include negative-angle sign reversal and zero cases.
   - Include provenance tests that state whether key inputs are user-supplied assumptions or standards-derived constants.

5. **Protect package/API behavior outside pytest.**
   - Pytest may pass because `tests/conftest.py` injects `src/` into `sys.path`; add a public import smoke such as:
     ```bash
     PYTHONPATH=src UV_NO_SYNC=1 uv run python -c "from digitalmodel.naval_architecture import load_packaged_example"
     ```
   - For packaged YAML/data, build-wheel tests should assert new package data and at least one existing package-data fixture still survive, preventing package-data regression.

6. **Run the upstream-helper regression slice.**
   - If a new calculation reuses an existing helper (e.g. `rudder_normal_force`) or shared writer, include tests for the helper/predecessor workflow as a mandatory targeted regression.
   - Example slice for rudder-derived workflows:
     ```bash
     UV_NO_SYNC=1 uv run pytest \
       tests/naval_architecture/test_maneuverability.py \
       tests/naval_architecture/test_yaw_moment_sweep.py \
       tests/naval_architecture/test_rudder_stock_torque_sweep.py -q
     ```

7. **Record engineering-registry retrieval evidence even for bounded preliminary calcs.**
   - Check and cite at least:
     - `docs/document-intelligence/README.md`
     - `data/document-index/standards-transfer-ledger.yaml`
     - `data/design-codes/code-registry.yaml`
     - `data/document-index/online-resource-registry.yaml`
     - relevant wiki/promoted glossary pages
   - If registries have no direct match, record the negative finding.

8. **Decide `/mnt/ace` / wiki-promotion explicitly.**
   - If existing promoted wiki pages are sufficient for bounded scope, say so.
   - Add a hard stop: if implementation introduces new coefficients/constants/compliance claims, pause for fresh raw-reference review and wiki promotion before coding.

## Implementation hardening checks

When executing an approved engineering-calculation issue, keep these plan lessons active in the code/tests, not only the plan:

1. **Honor configurable artifact names and subsets.**
   - If YAML declares sidecar filenames (for example `outputs.sidecars.provenance` or `artifact_manifest`), parse them into the validated config, propagate them through result metadata, and have the writer use those names. Do not leave YAML-configured filenames as decorative comments while code hardcodes defaults.
   - If YAML declares `outputs.charts.required`, write exactly that subset (or explicitly document that all charts are always required). Avoid metadata saying one chart set while the manifest/files contain another.
   - Test both the packaged happy path and a reduced chart subset so output contract drift is caught.

2. **Fail early on empty sweeps.**
   - Reject empty speed lists and empty angle/load-case grids during validation with a clear `ValueError`.
   - Do not let empty-but-valid configs reach plotting/writing where they fail as opaque matplotlib/heatmap errors.

3. **Pin physical sign conventions in every surface.**
   - A mathematically consistent sign convention is not enough for engineering consumers. Document rotation sense / axis direction in code metadata, packaged YAML, docs, and tests.
   - For torque about a rudder stock, prefer wording like: right-hand-rule torque about the `+z`/up stock axis; counterclockwise viewed from above for a positive signed force and positive arm; holding torque is equal/opposite.

4. **Use robust module monkeypatch/import tests.**
   - If a package `__init__.py` exports a function with the same name as a module, `import package.module as module` can bind the exported function instead of the submodule in some contexts. Use `import importlib; module = importlib.import_module("package.module")` before monkeypatching module globals.

5. **Preserve subprocess environments.**
   - When tests spawn `uv` or other CLIs with a custom environment, use `env={**os.environ, "PYTHONPATH": "src"}` instead of replacing the whole environment. Replacing it can hide `PATH` and produce false `FileNotFoundError: 'uv'` failures.

6. **Treat adversarial MINORs as cheap hardening opportunities before commit.**
   - For non-trivial engineering calculations, fix actionable MINOR review findings when they are bounded and testable (artifact-contract drift, validation clarity, sign wording) before final commit/push. Then rerun targeted tests, lint, smoke generation, and a follow-up review.

## Expansion-wave hardening checks

When a completed calculation spawns follow-up issues (quality validation, standards expansion, next calculation), keep the same hard gate discipline:

1. **Quality issue first.**
   - Before expanding physics, create/plan a CI-like validation/package-data issue for the just-landed workflows.
   - Reframe vague “full CI” claims as enumerated locally runnable gates plus clean-install/package-data smoke unless the plan mirrors exact GitHub workflow jobs.
   - Acceptance criteria should name exact commands, required output families, version/commit reporting, and failure-classification tables.

2. **Standards issue as source crosswalk before formulas.**
   - For steering gear, rudder stock scantling, SOLAS/class checks, or similar standards-backed topics, default deliverable is a source crosswalk and draft child-issue pack, not formulas.
   - Do not create live child implementation issues by default until clause-ready text is verified and the user approves the crosswalk.
   - Portal entries, metadata-only anchors, and secondary wiki summaries are not formula authority; require edition/year, exact clause locator, extraction/access status, readiness status, and rationale.

3. **Preliminary model issue must be physically bounded.**
   - If a plan title overlaps a validated/compliance metric (turning circle, tactical diameter, overshoot), narrow the deliverable to the actual model class (e.g. “constant-speed first-order Nomoto trajectory/metric generator using user-supplied K/T”).
   - Add no-compliance/no-validation caveats, no default IMO/ABS criteria overlays, and explicit exclusions for missing physics (sway/drift, speed loss, hull-propeller-rudder interaction, environmental loads, hard-over validity).
   - Add metric guardrails: threshold interpolation, null metrics when not reached, convergence checks before steady-state metrics.

4. **Reviewer unavailability is not approval.**
   - If an adversarial lane times out, write an `UNAVAILABLE` artifact with residual-risk language.
   - Do not silently downgrade or count unavailable lanes as approving reviews; proceed to `status:plan-review` only when completed substantive reviews have no unresolved MAJORs and the missing lane is documented.

## Review-gate wording

Plan-review readiness for engineering calculations should require:
- canonical plan file exists under `docs/plans/`;
- review artifacts exist under `scripts/review/results/`;
- at least two substantive reviews plus synthesis, unless a documented waiver exists;
- no unresolved MAJOR findings;
- issue is `status:plan-review` only, not implementation-approved;
- `.planning/plan-approved/<issue>.md` and `status:plan-approved` are synchronized before implementation starts.
