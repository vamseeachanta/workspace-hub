# DRAFT — Proposed digitalmodel issue body

> **Status:** local draft for user review BEFORE posting to digitalmodel repo
> **Destination:** `vamseeachanta/digitalmodel` issue tracker
> **Created:** 2026-05-20
> **Author:** Claude (workspace-hub session)
> **Source request:** workspace-hub session 2026-05-20 — user asked to correct polar charts in `digitalmodel/docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` with (a) transparent ship outline in middle, (b) coefficients shown at the appropriate phase angle so lateral force per environmental direction is obvious, AND (c) the resulting capability must be reusable for generic studies including [workspace-hub#2760](https://github.com/vamseeachanta/workspace-hub/issues/2760) (B1528 SIROCCO).
> **Related:** workspace-hub#2768 (OCIMF umbrella), workspace-hub#2760 (SIROCCO force review), digitalmodel#556 (CYw bounding), digitalmodel#563 (OCIMFExcelAdapter)
> **After user approval:** post body below as a new digitalmodel issue; capture the assigned issue number; then transcribe the companion plan draft (`2026-05-20-digitalmodel-plan-draft-ocimf-polar-vessel-force-overlay.md`) to `digitalmodel/docs/plans/2026-05-20-issue-<NNN>-ocimf-polar-vessel-force-overlay.md` and apply `status:plan-review` label.

---

## Proposed title

`feat(marine_ops): polar plot with vessel silhouette and on-body force vectors — reusable across OCIMF explorer, SIROCCO review, future studies`

## Proposed labels

- `enhancement`
- `priority:medium`
- `cat:engineering-calculations`
- `domain:hydrodynamics`
- `domain:visualization`
- `domain:naval-architecture`

---

## Proposed issue body (copy this into the digitalmodel issue)

### Purpose

Build a reusable polar-plot capability in digitalmodel that overlays (a) a transparent vessel silhouette anchoring the angular axis, and (b) explicit on-body force-vector arrows showing the direction the environmental loading actually pushes the vessel — so that any consumer (the OCIMF coefficient explorer, the [B1528 SIROCCO moored-current review](https://github.com/vamseeachanta/workspace-hub/issues/2760), or future force/moment analyses) can render polar diagrams where lateral / longitudinal / yaw load direction is unambiguous from the picture alone.

Today the OCIMF explorer's polar plots (`docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html`) render `r = |C|` against angular axis `θ = incidence heading`, with sign encoded only as line style (solid/dashed). Readers must mentally invert from "incidence direction" to "force direction" via the OCIMF sign convention — exactly the cognitive step that the new on-body force arrows + silhouette will remove.

### Motivating use cases

| Use case | Current pain point | What this delivers |
|---|---|---|
| OCIMF coefficient explorer (`scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py`) | Polar shows `r = |Cy|`; sign as line style only; no vessel reference frame | Bow-up silhouette in middle + on-body force arrows at sampled headings, with arrow length ∝ |Cy| and arrow direction in vessel-fixed +Y/−Y |
| B1528 SIROCCO moored-current review (workspace-hub#2760) | Force-by-force review of X/Y/Z/K/M/N at rudder angles ±5°; existing report renders force magnitudes but not on-body direction relative to vessel | Same polar capability accepts arbitrary `force_vectors(theta, fx, fy, fz, mx, my, mz)` input; not OCIMF-specific |
| Future generic environmental-loading studies | Each study reinvents its own Plotly polar; no shared visual convention; sign-handling drifts | Single `polar_force_overlay()` function used by all consumers; one place to fix bugs, one place to render |

### Scope

#### In scope

1. **New reusable function/module** — `digitalmodel.marine_ops.<canonical-home>.visualization.polar_force_overlay` — producing a Plotly `Figure` parameterized by:
   - `coefficients_or_forces`: pandas DataFrame with columns `(theta_deg, fx, fy, fz, mx, my, mz)` OR `(theta_deg, value, component)` with `component ∈ {'X','Y','Z','K','M','N'}` (long format) — both shapes supported.
   - `vessel_geometry`: dataclass with `loa_m`, `beam_m`, optional `draft_m` and `silhouette_kind ∈ {'tanker','gas_carrier','generic','custom_path'}` — controls the silhouette polygon.
   - `frame_convention`: enum `INCIDENCE_HEADING_BODY_FIXED` (default, matches OCIMF) | `FORCE_DIRECTION_INERTIAL` — explicit declaration of which frame the input `theta_deg` is in.
   - `force_arrow_kind`: enum `LATERAL_ONLY` | `LONGITUDINAL_ONLY` | `RESULTANT_2D` | `NONE` — controls which on-body arrow(s) are rendered.
   - `radial_axis_mode`: `MAGNITUDE` (default, matches today) | `SIGNED` (overplots positive-half and negative-half on the same r axis with color split).
2. **Vessel silhouette assets** — three default silhouettes (tanker, gas-carrier, generic-hull) as transparent Plotly polygon paths defined in body coordinates and scaled to the polar radial axis. Bow-up by convention.
3. **Force-arrow renderer** — for each sampled `theta`, draws a short arrow starting at the silhouette boundary and pointing in the resolved force direction (vessel-body frame), with arrow length proportional to the coefficient/force magnitude. Arrow color/style indicates positive vs negative.
4. **Consumer #1 — OCIMF explorer**: refactor `scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py:make_polar_overlay()` to delegate to the new module. The HTML output at `docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` is regenerated.
5. **Consumer #2 — SIROCCO**: add a hook for the workspace-hub#2760 plan to call the new module once it lands. (Implementation of the SIROCCO side stays gated by #2760's own approval.)
6. **Tests** — TDD against frame-convention correctness (e.g., OCIMF positive Cyc at θ=90° → force-arrow points to +Y starboard), silhouette scaling, dataframe-schema validation, and snapshot of the rendered HTML output.

#### Explicitly out of scope (separate issues)

- Building the `OCIMFExcelAdapter` (digitalmodel#563) — independent ingestion concern; this module accepts already-ingested DataFrames.
- Resolving the `marine_engineering/ocimf.py` vs `marine_analysis/ocimf.py` duplication (umbrella'd at workspace-hub#2768) — this plan must declare which sibling the new visualization module lives under, but does not consolidate the duplicate `ocimf.py` files.
- Extending the existing 660-LOC `marine_ops/marine_analysis/reporting/ocimf_interactive_report.py` — this issue's plan must explicitly decide whether to (a) refactor it to consume the new module, (b) deprecate it, or (c) leave it untouched. The decision lives in the plan, not this issue body.
- 3D vector rendering — keep this to a 2D polar projection (XY plane). Roll/pitch/yaw moments (K/M/N) are rendered as labeled curved-arrow glyphs, not 3D arrows.
- Animating heading sweeps — out of scope for v1.

### Acceptance criteria

- [ ] New module exists at `src/digitalmodel/marine_ops/<canonical-home>/visualization/polar_force_overlay.py` (canonical-home chosen in plan).
- [ ] Function signature accepts the parameters listed in In-scope §1; validates input DataFrame schema; raises explicit error for ambiguous frame.
- [ ] Vessel silhouette renders with bow up, port to left, starboard to right; transparent fill (alpha ≤ 0.3); scales to the polar radial axis without distortion at any radial-axis range.
- [ ] On-body force-arrow renderer produces arrows whose direction visually matches the documented sign convention — verified by a test asserting that at θ=90° (starboard-incidence) with positive `Cy`, the arrow's terminal point has a +Y (starboard) component greater than its origin's +Y component.
- [ ] OCIMF explorer HTML regenerated from refactored build script; visual output preserves all existing 15 figure traces (no data lost); ship outline + force arrows present on every polar diagram.
- [ ] TDD test suite covers: input-schema validation, frame-convention enum behavior, silhouette scaling, arrow-direction correctness for known signed coefficients, and snapshot stability of the rendered HTML on a fixed input.
- [ ] No regression: `cd digitalmodel && uv run pytest tests/marine_ops/` passes.
- [ ] Module is importable and usable from a hypothetical workspace-hub#2760 SIROCCO-side caller — verified by a smoke test in `tests/` that constructs a synthetic SIROCCO-style force DataFrame and calls the module.
- [ ] No external client/project identifiers (e.g., `B1528`, `acma-projects` paths) are embedded in the module code or tests — those references are caller-side only; per `.claude/rules/` legal-compliance baseline.
- [ ] Plan reproduction-proof (Step 1.5): for the OCIMF explorer side, the existing `make_polar_overlay()` HTML output is captured as a "before" snapshot in the plan so reviewers can compare against the "after" snapshot before approval.

### Gate note

Implementation is blocked until:
1. This issue is created in digitalmodel and labeled `status:plan-review`.
2. The companion plan (drafted in workspace-hub at `docs/governance/2026-05-20-digitalmodel-plan-draft-ocimf-polar-vessel-force-overlay.md`) is transcribed to `digitalmodel/docs/plans/2026-05-20-issue-<NNN>-ocimf-polar-vessel-force-overlay.md`.
3. Adversarial review wave runs (Claude r1 + Codex + Gemini per AGENTS.md AI Review Policy).
4. User explicitly approves and applies `status:plan-approved` label + creates `.planning/plan-approved/<NNN>.md` marker.

Per workspace-hub `.claude/rules/`, self-approval is forbidden.

### References

- workspace-hub#2768 — OCIMF MEG3/MEG4 closeout umbrella
- workspace-hub#2760 — B1528 SIROCCO moored-current force review (downstream consumer)
- digitalmodel#556 — CYw=-3.56 out-of-envelope (concurrent fix, independent)
- digitalmodel#563 — OCIMFExcelAdapter (concurrent fix, independent)
- Existing build script: `scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py:396` (`make_polar_overlay`)
- Existing report (potential refactor target): `src/digitalmodel/marine_ops/marine_analysis/reporting/ocimf_interactive_report.py`
- Pre-existing OCIMF tests: `tests/marine_ops/marine_engineering/environmental_loading/test_ocimf.py`, `tests/marine_ops/marine_engineering/integration/test_ocimf_mooring_integration.py`
