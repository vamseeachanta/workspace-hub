# Plan for #2760: B1528 SIROCCO force calculation review updates

> **Status:** patched-after-review; **not approval-ready** until the user resolves the engineering-source/model decisions below.
> **Complexity:** T3
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2760
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2642
> **Review artifacts:**
> - `scripts/review/results/2026-05-20-plan-2760-claude.md` — MAJOR
> - `scripts/review/results/2026-05-20-plan-2760-codex.md` — MAJOR
> - `scripts/review/results/2026-05-20-plan-2760-gemini.md` — MAJOR

---

## Gate State

Implementation is blocked. This plan must **not** be labeled `status:plan-review` or `status:plan-approved` yet.

The first adversarial review returned three MAJOR verdicts. The plan has been patched to turn the findings into explicit blockers and user-decision prompts rather than hiding them as implementation details.

### Approval-blocking user decisions

These decisions define the force results. They must be resolved in the issue thread before a fresh plan-review rerun.

1. **OCIMF MEG4 coefficient source**
   - The named `ocimf_coefficients_production.csv` was **not found** anywhere under `/mnt/local-analysis`.
   - The implementation must not invent or synthesize OCIMF data.
   - Required decision: provide/identify the generic OCIMF tabular coefficient source to use, or explicitly approve a cited, manually digitized limited fixture with stated licensing/provenance constraints.
   - Required citation contract: standards-derived coefficient data must emit a `Citation` sidecar and fail closed if the citation/source is missing.

2. **OCIMF generic vessel class / curve basis**
   - User comments say generic OCIMF MEG4 coefficients are acceptable because no ship-specific coefficients exist.
   - Required decision: select the specific generic OCIMF vessel class/curve basis and interpolation domain for B1528 SIROCCO, or instruct that this remains an explicit report limitation.

3. **Simple rudder model basis**
   - User comments request the simple area/drag-style rudder calculation as the default and the existing hydrodynamic/Barrass-family method as side-by-side comparison.
   - Required decision: approve the simple rudder formula basis, coefficient/Cd/CN source, stall/large-angle handling at 28° port, velocity basis at rpm=0, lever arm, and sign mapping.
   - Until this is settled, no default rudder numbers are approval-ready.

4. **Current-heading plot range**
   - User comments confirm default heading = +5° port/off-bow.
   - The earlier draft incorrectly turned a `-5°..+5°` range into tested scope without explicit approval.
   - Required decision: approve the heading sensitivity plot range and step, or keep only the default/current-speed sweeps requested in comments.

5. **OCIMF direct yaw moment vs `Y × arm` comparison interpretation**
   - User comments request one side-by-side verification chart.
   - Required decision: approve that the chart is explanatory rather than equality-based: OCIMF `CMc` and `Y × arm` are different modeling assumptions and may diverge. The report must caption this and define warn/fail behavior for unexpected discrepancy.

---

## Resource Intelligence Summary

### Existing repository artifacts

| Artifact | Status | Notes |
|---|---:|---|
| `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_moored_current_report.py` | Found | Existing bounded rudder-only report generator for the previous 3.5 kn / ±1–5° package; reports `Z`, `K`, and `M` as zero; excludes hull current loads because no current coefficients were available. |
| `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py` | Found | Existing current-heading/rudder comparison generator; writes CSV/JSON/Markdown/HTML/PDF but uses placeholder “OCIMF-inspired” coefficient functions and includes resultants that #2760 requires removing from the main presentation. |
| `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_moored_current.yml` | Found | Existing B1528 geometry/rudder config for old report. |
| `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_current_heading_rudder.yml` | Found | Existing current-heading/rudder config; defaults/ranges need revision. |
| `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_b1528_sirocco_moored_current.py` | Found | Existing regression coverage for symmetry, `Cr=1.0`, sample points, and report content. |
| `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_b1528_sirocco_current_heading_rudder.py` | Found | Existing current-heading/rudder regression and report content checks. |
| `/mnt/local-analysis/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py` | Found | OCIMF database/interpolation module with `OCIMFDatabase`, `OCIMFCoefficients`, `VesselGeometry`, and current force/moment structures for `CXc`, `CYc`, `CMc`. |
| `/mnt/local-analysis/digitalmodel/docs/domains/marine-engineering/b1528-sirocco-moored-current-report.md` | Found | Existing durable Markdown report; stale for #2760 because it reflects prior scenario/presentation. |
| `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output/b1528_sirocco_moored_current_report.pdf` | Found | Existing ACMA PDF package; confirms old 3.5 kn / ±1–5° report basis. |
| `ocimf_coefficients_production.csv` | **Not found** | Searched `/mnt/local-analysis`; no live copy found. This is now a blocker, not an implementation detail. |

### Standards / domain sources

| Source | Use | Gate |
|---|---|---|
| OCIMF MEG4 current coefficient method | Required current-on-ship force/moment model | Must be tied to actual coefficient data and citation sidecar before implementation. |
| `digitalmodel/docs/domains/project-docs/PHASE3_OCIMF_FINDINGS.md` | Existing OCIMF dataset notes and coefficient ranges (`CXc`, `CYc`, `CMc`) | Useful for bounds/tests, but not sufficient by itself as coefficient source unless backed by source data/citation. |
| Existing B1528/Barrass rudder force family | Retain as alternate comparison model only | Must not become the hidden default if user asked for simple area/drag default. |
| Workspace engineering gate | Issue → resource intel → plan → adversarial review → user approval → TDD implementation | Applies because issue is labeled `cat:engineering-calculations`. |

### Tooling observations

- `digitalmodel` has `python-docx` dependency declared in `pyproject.toml` and `docx` imports under `uv run`; DOCX generation is technically available.
- `pypandoc` is not installed under the `digitalmodel` environment; do not plan on `pypandoc` unless explicitly added.
- Repository boundary is mixed:
  - `digitalmodel` is a sibling Git repository under `/mnt/local-analysis/digitalmodel`.
  - `acma-projects/B1528/output` currently appears under `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output`, not as `/mnt/local-analysis/acma-projects`.
  - Closeout must serialize commits/pushes per actual repo boundary after live preflight.

### Resource-intelligence comment

Posted: https://github.com/vamseeachanta/workspace-hub/issues/2760#issuecomment-4497406319

---

## Decision Ledger from Issue Comments

| Topic | Current decision from issue comments | Status |
|---|---|---:|
| Default current speed | 3.08 kn | Confirmed |
| Current-speed range | 0 to 4 kn where practical; 4 kn upper bound, not default | Confirmed |
| Current heading default | +5° off bow | Confirmed |
| Heading sign | Port positive | Confirmed |
| Axes | `+X` forward, `+Y` port, `+Z` up, `+N` bow-to-port | Confirmed |
| Rudder default | 28° port w.r.t. ship | Confirmed |
| Propeller | rpm = 0; neutral `Cr=1.0` unless a future model explicitly changes it | Confirmed |
| Retired old sweep | Previous 3.5 kn / ±1–5° rudder sweep removed from main report | Confirmed |
| Current on ship | Use generic/digitized OCIMF MEG4 current coefficients; no ship-specific coefficients exist | Confirmed but source data unresolved |
| Ship geometry | Reuse existing B1528 geometry; CoG longitudinal datum = midship; vertical CoG = 6.1 m above keel | Confirmed |
| Current force/moment display | OCIMF direct yaw moment default; include side-by-side comparison against force × lever-arm method | Confirmed but tolerance/caption unresolved |
| Rudder sweep | 0° to 28° port in 2° increments | Confirmed |
| Rudder models | Show simple area/drag-style calculation as default and existing/alternate hydrodynamic model side-by-side; cite model basis | Confirmed but model coefficients/source unresolved |
| Schematics | Plan views using transparent/small ship outline; each calculation section shows default values, `X`, `Y`, and `N` about CoG | Confirmed |
| Results | Remove resultant force calculations from main presentation; remove heatmap; single-variable charts; kN/kN·m rounded to 0 decimals for large values; angles may use 1 decimal | Confirmed but rounding threshold needs testable wording |
| Output split | Markdown + HTML in `digitalmodel`; Word + PDF in `acma-projects` output | Confirmed |

---

## Revised Implementation Outline After Decisions Are Resolved

Do not execute this section until the approval-blocking decisions above are resolved, the plan is rerun through adversarial review, and the user explicitly approves.

### Phase 0 — Preflight and source locking

1. Re-check `workspace-hub` and `digitalmodel` worktree states; identify unrelated dirty files before any write.
2. Locate/provide approved OCIMF coefficient source.
3. Add or identify citation source page/artifact for OCIMF coefficients.
4. Add or identify citation/model source for simple rudder model.
5. Define exact output filenames and supersession policy for old Markdown/HTML/Word/PDF outputs.

### Phase 1 — TDD RED tests

Write failing tests before implementation. Required tests include:

| Test | Purpose | Required assertions |
|---|---|---|
| `test_issue_2760_ocimf_source_required` | Fail closed if OCIMF coefficient source/citation missing | Missing source raises explicit error; no placeholder fallback. |
| `test_issue_2760_ocimf_placeholder_constants_removed` | Prevent silent reuse of old placeholder functions | Source does not contain `OCIMF_CURRENT_CX_BASE`, `OCIMF_CURRENT_CM_SCALE`, or `ocimf_cy = heading_sin`. |
| `test_issue_2760_current_speed_unit_conversion` | Catch kn→m/s errors | `3.08 kn × 0.51444 = 1.5844752 m/s` within numeric tolerance. |
| `test_issue_2760_current_positive_heading_signs` | Catch sign flips | Approved `+5°` port current yields expected sign for `Y` and `N` based on approved coefficient convention. |
| `test_issue_2760_current_default_sample_calculation` | Independent numerical oracle | Table-driven expected `CXc/CYc/CMc`, `X/Y/N`, units, signs, and tolerances for default case. Expected values must come from approved source/hand calculation, not production code. |
| `test_issue_2760_current_speed_sweep_domain` | Confirm 0..4 kn sweep | Rows/charts include approved speeds and default marker. |
| `test_issue_2760_current_heading_plot_domain` | Confirm heading plot only after user approval | If approved, assert exact heading range/step; otherwise this test is omitted. |
| `test_issue_2760_rudder_model_source_required` | Fail closed for uncited rudder model | Missing rudder model source/citation raises explicit error. |
| `test_issue_2760_rudder_default_signs_and_values` | Catch rudder force/moment sign/value errors | Approved default `28° port` at rpm=0 produces table-driven expected signs and values. |
| `test_issue_2760_rudder_sweep_domain` | Confirm 0..28° port, 2° increments | Row/chart data includes exactly approved sweep. |
| `test_issue_2760_no_resultant_main_presentation` | Enforce user request | Markdown/HTML/DOCX/PDF text and report-bound JSON contain no main-presentation `resultant`, `total horizontal force`, or `heatmap` terms unless explicitly in an internal QA artifact. |
| `test_issue_2760_schematic_svg_contract` | Make schematics testable | Schematic source artifacts are SVG or have stable metadata IDs for ship outline, CoG, X/Y/N arrows, angle labels, and default numeric labels. |
| `test_issue_2760_docx_opens_and_contains_sections` | Verify Word output | Generated `.docx` opens with `python-docx` and contains required headings/sections. |
| `test_issue_2760_output_manifest` | Verify output package | Manifest lists Markdown, HTML, DOCX, PDF, CSV/JSON data, schematic assets, source/citation metadata, and supersession information. |
| Existing regression preservation | Ensure old stable behavior is not accidentally broken | Existing moored-current and current-heading tests pass or pre-existing red tests are listed with exact file/test names and baseline evidence. |

### Phase 2 — Calculation/source implementation

1. Replace placeholder current coefficient path with approved OCIMF source lookup.
2. Use existing OCIMF API where possible; if new source wrapper is needed, keep formula/reference area/reference length/sign convention explicit and tested.
3. Implement fail-closed citation sidecar for OCIMF coefficients and rudder model constants.
4. Implement simple rudder model only after its model basis is approved.
5. Retain existing hydrodynamic/Barrass-family rudder method as an explicitly labeled alternate comparison model.
6. Keep `Z`, `K`, `M` as zero/not-applicable only if this is still the approved scope; otherwise mark as out-of-scope rather than silently reporting values.

### Phase 3 — Report and schematic generation

1. Separate report sections:
   - Introduction.
   - Design data and assumptions.
   - Axes/sign conventions and CoG datum.
   - Load due to current on ship.
   - Load due to rudder.
   - Side-by-side checks and limitations.
2. Add per-section plan-view schematics with stable SVG/metadata IDs.
3. Remove main-presentation resultant force sections/tables/charts and heatmap.
4. Include coefficient plots, sample default calculation, current-speed plots, rudder-sweep plots, and the approved yaw comparison chart.
5. Emit Markdown/HTML in `digitalmodel` and DOCX/PDF in the approved `acma-projects/B1528/output` location.
6. Include a supersession note in revised outputs naming the old package basis and issue #2760.

### Phase 4 — Verification, review, and closeout

1. Run targeted tests in `digitalmodel` with `uv run`.
2. Generate the report package.
3. Extract text from PDF/DOCX and verify required/forbidden terms.
4. Visually inspect HTML/PDF schematics if browser/PDF tooling is available.
5. Run implementation adversarial review (Claude + Codex + Gemini or documented fallback).
6. Commit/push actual changed repos with pathscoped staging and clean-worktree evidence.
7. Post final issue comment linking output artifacts, tests, review artifacts, commits, and parent #2642 traceability.

---

## Output Contract Draft

Exact filenames must be finalized before implementation. Proposed names pending approval:

| Artifact | Proposed path | Tracked? |
|---|---|---:|
| Revised Markdown report | `/mnt/local-analysis/digitalmodel/docs/domains/marine-engineering/b1528-sirocco-current-rudder-force-report.md` | Yes |
| Revised HTML report | `/mnt/local-analysis/digitalmodel/outputs/b1528_sirocco/current_rudder_force/b1528_sirocco_current_rudder_force_report.html` | TBD by repo artifact policy |
| Revised DOCX | `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output/b1528_sirocco_current_rudder_force_report.docx` | Yes if ACMA package tracks outputs |
| Revised PDF | `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output/b1528_sirocco_current_rudder_force_report.pdf` | Yes if ACMA package tracks outputs |
| Data/manifest | `.../b1528_sirocco_current_rudder_force_manifest.json` | Yes |
| Schematic SVGs | `.../schematics/*.svg` | Yes or embedded, but must be testable |

Supersession policy to approve: keep old `b1528_sirocco_moored_current_report.*` artifacts as prior package, and create new `current_rudder_force` artifacts rather than overwriting old files in place.

---

## Adversarial Review Summary

First review round completed 2026-05-20. All reviewers returned MAJOR.

| Provider | Verdict | Primary blockers |
|---|---:|---|
| Claude | MAJOR | OCIMF citation/source gap; label-only sign tests; unapproved `-5°..+5°` heading plot; yaw comparison tolerance; rudder model under-specified. |
| Codex | MAJOR | OCIMF source open; uncited pseudocode formulas; rudder model under-specified; no independent numerical oracles; output governance too loose. |
| Gemini | MAJOR | OCIMF fixture hallucination risk; unresolved vessel class/rudder coefficient decisions; Word tooling unspecified; schematic tests need SVG/intermediate-data contract; repo-boundary wording. |

### Review-driven changes applied in this patched draft

- Removed any permission to invent OCIMF data during implementation.
- Promoted OCIMF source, vessel class, rudder model basis, heading plot range, and yaw-comparison interpretation to approval-blocking decisions.
- Added citation/fail-closed requirements for standards-derived coefficients/model constants.
- Replaced label-only test language with numeric sign/unit/golden-oracle tests.
- Added DOCX parsing and SVG/metadata schematic test requirements.
- Clarified repo boundary: `digitalmodel` is a sibling Git repo; `acma-projects/B1528/output` is under this `workspace-hub` checkout unless live preflight proves otherwise.
- Clarified that old report artifacts should be superseded with new filenames unless the user approves overwrite-in-place.

### Remaining blocker

This patched plan is still **not approval-ready** because it requires user/source decisions. After those decisions are posted, rerun adversarial plan review and only then request explicit user approval.
