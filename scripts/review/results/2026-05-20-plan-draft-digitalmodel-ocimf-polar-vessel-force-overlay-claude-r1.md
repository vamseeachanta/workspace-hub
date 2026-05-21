# Claude r1 adversarial review — digitalmodel OCIMF polar+vessel+force-vector plan (draft)

> **Reviewer:** Claude (workspace-hub session, single-author r1)
> **Plan reviewed:** `docs/governance/2026-05-20-digitalmodel-plan-draft-ocimf-polar-vessel-force-overlay.md`
> **Issue reviewed:** `docs/governance/2026-05-20-digitalmodel-issue-draft-ocimf-polar-vessel-force-overlay.md`
> **Date:** 2026-05-20
> **Stance:** adversarial per `feedback_adversarial_review_stance` — defect-hunt, no praise, bias toward MAJOR/MINOR
> **Provenance:** single-author r1; Codex + Gemini dispatch is user-triggered after issue + plan posted to digitalmodel

---

## Verdict: **MAJOR — plan must revise before user approval**

Two MAJOR + six MINOR + one TRIVIAL. Each finding cites a specific section/line.

---

## MAJOR findings

### M1 — TDD test #5/#6 pre-commits to a specific arrow direction (90.0 / 270.0) for the load-bearing frame-convention test, without independent verification against OCIMF MEG3/MEG4 Annex A

**Where:** §TDD Test List rows 5 and 6 of the draft plan.

**The defect:** Tests #5 and #6 assert that `_resolve_arrow_direction_in_body_frame(90, +1, INCIDENCE_HEADING_BODY_FIXED)` returns `90.0` (force arrow points to +Y starboard) and the negative case returns `270.0`. The plan's §Risks section already flags that this convention is counter-intuitive — physical force on a vessel from a starboard-incidence current pushes the hull *toward port*, so a literal-physical reading would expect "positive Cyc at θ=90° → arrow to PORT (270°)". But the plan derives the +90° direction by quoting the existing build script's docstring (lines 399-405) and comment (line 752), both of which were authored by the same agent recently. The OCIMF MEG3/MEG4 standards themselves were not consulted directly to verify whether positive Cy at starboard-incidence really means "force vector in vessel-fixed +Y" or "drag coefficient defined such that |F_y| = Cy ½ρV²A_y with sign-handling caller-side."

**Why it's MAJOR:** the test as written is the load-bearing correctness assertion for the entire feature. If it pins the wrong direction, every downstream consumer (OCIMF explorer, SIROCCO review, future studies) renders directionally wrong force arrows — and the test passes, providing false confidence. The mitigation in §Risks ("require reviewer to verify against OCIMF MEG3/MEG4 directly") is not enforced by the test — it's hope.

**Required revision:**

- Do NOT pre-commit to `returns 90.0` / `returns 270.0` in the plan's TDD list.
- Replace with a *property* assertion: "test asserts that positive Cy under OCIMF convention produces an arrow whose terminal point's vessel-fixed Y-component has the same sign as the convention defines positive force; this convention must be verified against OCIMF MEG3/MEG4 Annex A by the implementing agent before the test value is pinned."
- Add a §Files-to-Change row: "Modify the plan post-implementation-spike to pin the verified value with citation to OCIMF MEG3/MEG4 Annex A section/page reference."
- Reviewer should not approve the plan until the convention citation is in the plan body (not just §Risks).

### M2 — §Resource Intelligence Summary did not retrieve existing vessel/hull dataclasses in digitalmodel before introducing a competing `VesselGeometry` type

**Where:** §Pseudocode (introduces `@dataclass(frozen=True) class VesselGeometry`); §RIS Existing repo code (omits `hydrodynamics/hull_library/`).

**The defect:** verifying-against-repo-state, the following pre-existing dataclasses/models exist that the plan's §RIS did not enumerate:

- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/profile_schema.py`: `HullProfile`, `HullStation`, `HullType` (BaseModel-based)
- `digitalmodel/src/digitalmodel/hydrodynamics/models.py`: vessel-property dataclasses (header comment: "Data models for hydrodynamic analysis including coefficient matrices, vessel properties, wave parameters, and environmental conditions")
- `digitalmodel/src/digitalmodel/orcawave/vessel_database.py`: vessel database (likely has its own Vessel type)
- `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py`: input schemas (likely includes vessel geometry)
- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/catalog.py`, `lookup.py`, `mesh_generator.py`: hull-library helpers

**Why it's MAJOR:** the retrieval contract per workspace-hub#2208 requires ≥3 distinct sources be consulted. The plan listed 7 sources but missed an entire category — pre-existing vessel-geometry types — which is foundational to the new dataclass design. Introducing a new `VesselGeometry` without explicitly reconciling against the above types creates the exact "duplicate file" anti-pattern that workspace-hub#2768 is umbrella'd to fix.

**Required revision:**

- Add a §RIS row for each of the four pre-existing files above with a concrete finding (e.g., "`HullProfile` covers L, B, draft, stations; lacks `silhouette_kind` field").
- Add a §Open Question or §Decision row: "Reuse `HullProfile` and add an optional `silhouette_kind` field" vs "introduce a new `VesselGeometry` and document the rationale" vs "compose: `VesselSilhouetteSpec` references a `HullProfile` by ID."
- Defer the §Pseudocode dataclass definition until the decision is made; or commit to one of the three options in the plan revision with explicit rationale.

---

## MINOR findings

### m1 — Test #13 (no-regression on trace count) lacks a baseline-capture step in §Files-to-Change

**Where:** §TDD Test List row 13; §Files-to-Change.

The test claims "trace count matches pre-refactor count", but no §Files-to-Change row creates the pre-refactor baseline. The test would need a fixture committed BEFORE the refactor, or a checkpoint of `fig.to_dict()` from the existing build script run at HEAD.

**Fix:** Add a §Files-to-Change row: "Create `tests/marine_ops/marine_engineering/visualization/fixtures/ocimf_explorer_pre_refactor_trace_signature.json` — captured from running the existing `build_coefficient_explorer.py` at the pre-refactor commit SHA."

### m2 — Test #14 (SIROCCO smoke) is too weak to demonstrate consumer-readiness

**Where:** §TDD Test List row 14.

"Returns `go.Figure` with ≥6 data traces" is satisfied trivially even if the figure has 6 wrong/empty/misaligned traces. The acceptance criterion "Module is importable and usable from a hypothetical workspace-hub#2760 SIROCCO-side caller" deserves stronger validation.

**Fix:** Strengthen to assert: (a) all 6 force/moment components produce distinct arrow directions; (b) the figure's legend has 6 distinct entries; (c) if a SIROCCO sample DataFrame can be provided anonymized, use it as the fixture instead of a fully synthetic shape.

### m3 — Test #15 (no client identifiers) hardcodes 3 patterns

**Where:** §TDD Test List row 15.

`grep -E "B1528|SIROCCO|acma-projects"` covers exactly 3 patterns. The legal scan in `scripts/legal/legal-sanity-scan.sh` covers more (per `.legal-deny-list.yaml`). Hardcoding 3 patterns means a 4th leak goes undetected.

**Fix:** either (a) call `scripts/legal/legal-sanity-scan.sh <new-files>` from the test, or (b) read patterns from `.legal-deny-list.yaml` programmatically. If neither is feasible cross-repo, document the limitation explicitly.

### m4 — §RIS Reproduction-proofs promises a "before-snapshot" but §Files-to-Change does not capture it

**Where:** §RIS Evidence > Reproduction proofs; §Files-to-Change.

The reproduction-proofs section says "the existing rendered HTML at `digitalmodel/docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` is captured before any change so reviewers can compare against the after-snapshot." But no §Files-to-Change row creates a snapshot copy.

**Fix:** Add a step to copy the current committed HTML to `tests/marine_ops/marine_engineering/visualization/fixtures/ocimf_explorer_baseline.html` BEFORE refactor lands. Or cite the live commit SHA (`digitalmodel:9796effa`) as the baseline reference.

### m5 — Citation contract (`.claude/rules/calc-citation-contract.md`) applicability not addressed

**Where:** §Risks/Open; nowhere else in the plan.

The rule applies "When a calc module ... uses a standards-derived constant or formula." The polar_force_overlay module itself doesn't compute new coefficients, but: (a) vessel silhouette polygons may be derived from naval-architecture standard references, and (b) the rendered Figure represents OCIMF-sourced data and downstream reports citing the chart need provenance.

**Fix:** Declare in §Risks/Open whether:
- Silhouettes are "conventional, not standards-derived" (no citation required), AND
- The Figure object should carry citation metadata in `fig.layout.meta` so downstream report consumers can emit the right Citation sidecar.

### m6 — §Pseudocode glosses over Plotly's lack of native Scatterpolar arrowheads

**Where:** §Pseudocode (step 5c, "add arrow annotations"); §Risks mentions this but punts to implementer.

Plotly `Scatterpolar` does not render arrowheads natively. The implementer would have to choose between: (a) `layout.annotations` with `xref='paper'/'x domain'` and explicit Cartesian conversion of polar coords, (b) line+marker pairs with `symbol='arrow'` (which only works in Cartesian projections), or (c) custom SVG injection. Each has different correctness/quality tradeoffs. Punting to implementation creates rework risk if the chosen technique fails.

**Fix:** Pre-spike the arrow rendering technique during plan-review (build a 30-line prototype, verify it renders, pin the technique in the plan). Or explicitly add a §Decision-needed row to plan-review.

---

## TRIVIAL findings

### t1 — Both governance draft files should be verified to exist on disk

**Where:** general hygiene per `feedback_subagent_write_phantom` (applies to main-session Write calls in defense-in-depth).

**Status:** verified during this review — both files exist (`10327 B` issue draft, `25124 B` plan draft) at `docs/governance/`.

---

## What the plan does well (for the record — not praise, just calibration)

- §Authorization scope explicitly forbids cross-repo writes without user approval.
- §Files-to-Change "Explicitly not modified" table preempts scope creep.
- §Risks names the frame-convention bug as a real risk (but the mitigation is non-binding; see M1).
- Reproduction-proofs section correctly classifies the plan as "visualization feature, not runtime bug" with the N/A skip-allowed.

These do not change the verdict but reduce the cost of revision: the structure is sound; the content fixes are localized.

---

## Required revisions before user approval

1. **M1:** Remove pre-committed `returns 90.0` / `returns 270.0` from §TDD #5/#6; replace with property assertion + standard-citation requirement.
2. **M2:** Add §RIS rows for the 4-5 missed vessel/hull-related files in digitalmodel; declare a reuse-vs-introduce-new decision for the dataclass design.
3. **m1-m6:** apply the per-finding fixes inline.
4. **Re-review:** the plan author runs a fresh r1 pass (this same artifact, re-issued as r2) after revisions. Or, more honestly, defer to user: surface the findings, let user decide whether revise-inline is sufficient or whether a full re-review wave (Claude r2 + Codex + Gemini) is warranted before approval.

---

## Honest reviewer admission

This is a single-author r1: I authored the plan and reviewed it. Codex and Gemini r1 dispatches are still required for cross-provider coverage per AGENTS.md AI Review Policy, and those dispatches require the issue + plan to be posted to digitalmodel first (`feedback_codex_needs_pushed_artifact`). The user-in-loop gate after revision and cross-provider review is still load-bearing — this artifact does NOT pre-authorize anything.
