# Plan for #2760: B1528 SIROCCO force calculation review updates

> **Status:** ready-for-plan-review; implementation blocked pending explicit user approval.
> **Complexity:** T3
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2760
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2642
> **Review artifacts:**
> - `scripts/review/results/2026-05-20-plan-2760-claude.md` — Round 1 MAJOR, addressed by this patched plan
> - `scripts/review/results/2026-05-20-plan-2760-codex.md` — Round 1 MAJOR, addressed by this patched plan
> - `scripts/review/results/2026-05-20-plan-2760-gemini.md` — Round 1 MAJOR, addressed by this patched plan
> - `scripts/review/results/2026-05-20-plan-2760-r2-hermes.md` — Round 2 synthesis, APPROVE for plan-review transition
> - `scripts/review/results/2026-05-20-plan-2760-focused-source-update-hermes-r3.md` — Focused OCIMF source/provenance re-review synthesis, APPROVE/MINOR/APPROVE with no blocking findings after final patch

---

## Gate State

Implementation remains blocked pending explicit user approval. The issue is currently labeled `status:plan-review`; it is **not** `status:plan-approved`.

The first adversarial review returned three MAJOR verdicts against a draft that left engineering source/model choices unresolved. The owner's latest instruction is to get #2760 to `status:plan-review`; this patched plan converts those blockers into explicit **approval-scope assumptions** and fail-closed implementation gates. Approval of this plan means approval of the assumptions below; if any required source/citation cannot be resolved during implementation, work stops and returns to the issue thread instead of substituting invented data.

### Approval-scope assumptions for user review

1. **OCIMF MEG3/MEG4 coefficient source and citation gate**
   - The earlier `ocimf_coefficients_production.csv` blocker is resolved for planning: the approved source route is the licensed off-repo workbook `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx`, with generated/research artifacts at `/mnt/local-analysis/digitalmodel/docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html`, `/mnt/local-analysis/digitalmodel/docs/data/OCIMF_CORPUS_README.md`, and `/mnt/local-analysis/digitalmodel/scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py`.
   - Treat this as a generic/reference OCIMF tanker-current coefficient basis for B1528 SIROCCO, not as ship-specific SIROCCO coefficients. The report must state that limitation explicitly.
   - Citation/provenance must follow `.claude/rules/calc-citation-contract.md`; implementation must emit a fail-closed `Citation` sidecar tied to the workbook/provenance route and must never commit the licensed workbook or licensed PDFs into a repo. Expected citation target identity is `code_id: ocimf-meg3-current-coefficients` and/or `code_id: ocimf-meg4-current-coefficients`, resolved to standards/concepts wiki pages outside `knowledge/wikis/*/wiki/sources/`; implementation may retarget only if an existing registry-canonical OCIMF code_id is found and documented in the issue thread before calculations run.
   - Licensing boundary: the numeric OCIMF coefficient corpus/table is presumed license-restricted even when derived from the workbook. Do **not** commit extracted coefficient tables/corpora as CSV, JSON, YAML, Python literals, or embedded HTML unless a separate legal/license review or explicit owner decision verifies redistribution is permitted. Default implementation should resolve coefficient values locally from the off-repo workbook or an off-repo derived cache at calculation time.
   - Commit-safe by default: parser code, pointer/provenance metadata, figure identifiers, checksums, citation sidecars, limitation text, and tests that verify fail-closed behavior without embedding a reusable coefficient corpus. Any minimal numeric golden values must be justified as non-redistributive review/test evidence or kept in the issue thread/off-repo artifact rather than committed.
   - The generated HTML explorer is a local/provenance aid, not automatically repo-safe publication material; implementation must verify whether it embeds licensed coefficient data before copying, committing, or publishing any derived content.
   - Known extracted coverage from #2768/#2760 decision ledger: 1033 rows across figures `A5-A14` and `A16-A19`; `A15` is absent. Current-relevant families are loaded tanker current `A5-A11`, ballast 40%T tanker current `A12-A14`, and current velocity correction `A16`.
   - If the workbook/provenance route, license-safe data access path, or required citation target cannot be read and verified during implementation, implementation stops and posts a blocker rather than producing report numbers.

2. **Generic OCIMF curve/class basis**
   - Because no ship-specific coefficients exist, the report will use a clearly labeled **generic/reference OCIMF MEG4 tanker-current basis** for B1528 SIROCCO.
   - Selection rule: choose the nearest available generic MEG4 curve/class by documented geometry fit to existing B1528 dimensions (`LBP/LOA`, beam, draft/projected areas); record the selected class, interpolation domain, and limitation in the report metadata and limitations section.
   - Tie-break rule: if multiple generic curves/classes fit similarly, prefer the more conservative larger-magnitude force/moment envelope and record the rejected alternatives; if required geometry inputs are unavailable, implementation stops for a decision rather than silently choosing a class.
   - If B1528 SIROCCO is not a tanker-class vessel, the report must state that the tanker-current basis is applied off-class as a screening/reference limitation rather than a ship-specific or class-validated coefficient set.
   - This is an owner-approved reference assumption, not hidden implementation discretion.

3. **Default simple rudder model basis**
   - Default rudder model is a bounded screening-level area/drag or normal-force estimate using ambient current at **3.08 kn**, propeller rpm **0**, neutral `Cr=1.0`, default current heading **+5° port/off-bow**, and default rudder angle **28° port w.r.t. ship**.
   - The model must cite its coefficient/CN/Cd basis and emit citation/provenance metadata. Default to the existing `digitalmodel.naval_architecture.maneuverability.rudder_normal_force` / Whicker-and-Fehlner-style normal-force helper where applicable; any simpler area/drag fallback is allowed only if that helper is demonstrably inapplicable and must be explicitly labeled preliminary/screening-level.
   - Fallback criterion: area/drag fallback is allowed only when the helper cannot represent the available B1528 rudder geometry/input set or cannot provide a citation-compatible coefficient basis; the reason must be recorded in the manifest and issue thread before report generation.
   - No additional stall correction is assumed unless the cited model requires it; the report must state the large-angle limitation at 28°.
   - Sign mapping: `+X` forward, `+Y` port, `+N` bow-to-port; the rudder side force and moment signs must be independently asserted in tests.
   - Existing hydrodynamic/Barrass-family behavior remains side-by-side comparison only, not the hidden default.

4. **Heading/current/rudder sweep domains**
   - Default current speed: **3.08 kn**; practical current-speed plots/tables/sweeps use **0..4 kn** with 4 kn as upper bound, not default.
   - Heading plot domain is approved from the original layout comment: **-5°..+5° in 1° increments**, with port positive and +5° as the default marker.
   - Rudder sweep is **0°..28° port in 2° increments**, holding current speed at 3.08 kn and heading at +5° unless a chart explicitly varies those inputs.

5. **OCIMF direct yaw moment vs `Y × arm` verification chart**
   - The side-by-side chart is explanatory/verification-oriented, not an equality criterion.
   - OCIMF direct `CMc` yaw moment and `Y × arm` use different modeling assumptions; magnitude differences are expected and reported as limitations/review notes.
   - The `Y × arm` check must use CoG as the moment reference, with the existing B1528 longitudinal datum at midship unless live implementation preflight proves a different canonical datum.
   - Opposite sign in the approved default case is a hard-fail sign-convention error unless a cited coefficient convention explicitly explains it.

6. **Presentation/output assumptions**
   - Remove resultant-force calculations from the main report, remove heatmap, keep charts single-variable, use kN/kN·m rounded to 0 decimals for result values with magnitude `>= 1.0`, use 2 decimals for smaller displayed force/moment values if any, render all angle columns/labels to 1 decimal, and use readable labels such as `Current heading θ (deg)` and `Rudder angle α (deg)` instead of dense subscript notation.
   - Markdown + generated HTML land in sibling repo `digitalmodel`; generated Word + PDF land under `workspace-hub/acma-projects/B1528/output` unless live implementation preflight finds a different canonical location.

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
| `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx` | Found off-repo/licensed | Approved source route from #2768/#2760 decision ledger. Do not commit workbook/PDFs or extracted coefficient corpora; implementation must read values locally from workbook/off-repo cache, commit only license-safe metadata/code/citation artifacts, and fail closed if unavailable. |
| `/mnt/local-analysis/digitalmodel/docs/domains/charts/phase2/ocimf/ocimf_coefficient_explorer.html` | Found local/provenance aid | Generated explorer: `OCIMF MEG3/MEG4 Coefficient Explorer`, 15 Plotly figures, extracted coverage `A5-A14` and `A16-A19`; `A15` absent. Treat as potentially embedding licensed coefficient data; do not copy/commit/publish derived coefficient content without license review or explicit owner decision. |
| `/mnt/local-analysis/digitalmodel/docs/data/OCIMF_CORPUS_README.md` | Found | Data-routing/provenance map for licensed OCIMF corpus. |
| `/mnt/local-analysis/digitalmodel/scripts/python/digitalmodel/ocimf/build_coefficient_explorer.py` | Found | Parser/prototype route; current verified extraction count is 1033 rows. |
| `ocimf_coefficients_production.csv` | Not required / not found | Earlier blocker is superseded by the workbook/provenance route above; no placeholder fallback remains allowed. |

### Standards / domain sources

| Source | Use | Gate |
|---|---|---|
| OCIMF MEG3/MEG4 current coefficient method | Required current-on-ship force/moment model | Source route resolved to licensed off-repo workbook `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx` plus license-safe metadata/code/citation sidecar only; coefficient values must resolve from workbook/off-repo cache at calc time unless redistribution is explicitly approved. Fail closed if unavailable. |
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
| Current on ship | Use generic/reference OCIMF MEG3/MEG4 tanker-current coefficients through the licensed off-repo workbook route `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx`; no ship-specific coefficients exist; report limitation explicitly; fail closed if workbook/provenance/citation cannot be resolved; do not commit extracted coefficient corpora without license approval | Approval-scope assumption updated after #2768 review |
| Ship geometry | Reuse existing B1528 geometry; CoG longitudinal datum = midship; vertical CoG = 6.1 m above keel | Confirmed |
| Current force/moment display | OCIMF direct yaw moment default; include side-by-side explanatory chart against force × lever-arm method; not an equality criterion | Approval-scope assumption |
| Rudder sweep | 0° to 28° port in 2° increments | Confirmed |
| Rudder models | Default to cited `rudder_normal_force` / Whicker-and-Fehlner-style normal-force basis where applicable; only use a simpler area/drag fallback if that helper is inapplicable and the report labels it preliminary/screening-level. Existing/alternate hydrodynamic model remains side-by-side comparison only | Approval-scope assumption |
| Schematics | Plan views using transparent/small ship outline; each calculation section shows default values, `X`, `Y`, and `N` about CoG | Confirmed |
| Results | Remove resultant force calculations from main presentation; remove heatmap; single-variable charts; kN/kN·m rounded to 0 decimals for values with magnitude `>= 1.0`, 2 decimals for smaller displayed values if any, and angles to 1 decimal | Approval-scope assumption |
| Output split | Markdown + HTML in `digitalmodel`; Word + PDF in `acma-projects` output | Confirmed |

---

## Revised Implementation Outline

Do not execute this section until the user explicitly approves this `status:plan-review` plan. The assumptions above are part of the approval request; implementation remains fail-closed on source/citation availability.

### Phase 0 — Preflight and source locking

1. Re-check `workspace-hub` and `digitalmodel` worktree states; identify unrelated dirty files before any write.
2. Verify the licensed off-repo OCIMF workbook/provenance route (`/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx` plus explorer/README/parser artifacts) or stop with a blocker; no placeholder fallback and no committing licensed source documents or extracted coefficient corpora.
3. Locate or create citation target wiki page(s) for OCIMF MEG3 and/or MEG4 outside `knowledge/wikis/*/wiki/sources/`, with #2471 frontmatter (`code_id`, `publisher: OCIMF`, `revision`). Expected code_ids are `ocimf-meg3-current-coefficients` and/or `ocimf-meg4-current-coefficients` unless an existing registry-canonical target is found. Confirm `digitalmodel.citations.registry` or equivalent resolves the code_id(s). If MEG3 and MEG4 figures both feed coefficients, emit per-figure/per-family citations or document the selected revision explicitly; stop with a blocker if no acceptable target can be created.
4. Define the license-safe coefficient access pattern: default is pointer-only repo metadata plus local/off-repo workbook or off-repo derived-cache resolution at calculation time. Do not commit numeric coefficient tables/corpora as CSV, JSON, YAML, Python literals, or embedded HTML unless legal/license review or explicit owner decision permits redistribution.
5. Pre-stage the default-case numerical oracle in the issue thread or a referenced off-repo/source-controlled review artifact before implementation uses it; do not derive the expected values from production code.
6. Add or identify citation/model source and provenance sidecar for the default rudder model, locking the `rudder_normal_force` / Whicker-and-Fehlner-style basis unless it is demonstrably inapplicable.
7. Define exact output filenames and supersession policy for old Markdown/HTML/Word/PDF outputs.

### Phase 1 — TDD RED tests

Write failing tests before implementation. Required tests include:

| Test | Purpose | Required assertions |
|---|---|---|
| `test_issue_2760_ocimf_source_required` | Fail closed if OCIMF workbook/provenance/citation missing | Missing workbook/provenance/license-safe access route raises explicit error; no placeholder/trigonometric fallback; citation sidecar resolves or raises. |
| `test_issue_2760_ocimf_no_coefficient_corpus_leakage` | Enforce license boundary in generated/repo-bound artifacts | Repo-bound outputs, manifests, sidecars, HTML, JSON/CSV, and code fixtures do not serialize a reusable OCIMF coefficient table/corpus; only pointer/provenance metadata, figure IDs, checksums, selected coefficients needed for the specific report/oracle, and citation metadata may appear unless license approval is recorded. |
| `test_issue_2760_citation_sidecars_resolve` | Verify successful provenance path | Generated outputs include resolvable OCIMF and rudder citation/provenance sidecars with approved code_id/revision mapping, and fail if the registry cannot resolve them. |
| `test_issue_2760_ocimf_placeholder_constants_removed` | Prevent silent reuse of old placeholder functions | Source does not contain `OCIMF_CURRENT_CX_BASE`, `OCIMF_CURRENT_CM_SCALE`, or `ocimf_cy = heading_sin`. |
| `test_issue_2760_current_speed_unit_conversion` | Catch kn→m/s errors | `3.08 kn × 0.51444 = 1.5844752 m/s` within numeric tolerance. |
| `test_issue_2760_current_positive_heading_signs` | Catch sign flips | Approved `+5°` port current asserts explicit expected signs for `Y` and `N` under the cited convention (default expectation: `+Y` port and `+N` bow-to-port unless the OCIMF coefficient convention proves otherwise); opposite-sign yaw comparison in the default case hard-fails unless the approved coefficient convention explains it. |
| `test_issue_2760_current_default_sample_calculation` | Independent numerical oracle | Table-driven expected `CXc/CYc/CMc`, `X/Y/N`, units, signs, and tolerances for default case. Expected values must come from an approved source/hand calculation pre-staged in the issue thread or referenced oracle artifact, not production code. |
| `test_issue_2760_ocimf_coefficients_in_documented_range` | Catch digitization/source mapping errors | Coefficients resolved from the approved workbook/off-repo route remain within documented OCIMF/PHASE3 sanity ranges for `CXc`, `CYc`, and `CMc`; out-of-range values fail unless the cited source explicitly supports them. |
| `test_issue_2760_current_speed_sweep_domain` | Confirm 0..4 kn sweep | Rows/charts include approved speeds and default marker. |
| `test_issue_2760_current_heading_plot_domain` | Confirm approved heading plot domain | Assert exact heading range/step: `-5..+5°` in `1°` increments, with +5° default marker and port-positive sign convention. |
| `test_issue_2760_rudder_model_source_required` | Fail closed for uncited rudder model | Missing rudder model source/citation/provenance raises explicit error; screening-level limitation text is required. |
| `test_issue_2760_rudder_default_signs_and_values` | Catch rudder force/moment sign/value errors | Approved default `28° port` at rpm=0 produces table-driven expected signs and values. |
| `test_issue_2760_rudder_sweep_domain` | Confirm 0..28° port, 2° increments | Row/chart data includes exactly approved sweep and holds current speed at 3.08 kn and heading at +5° unless the chart explicitly varies an input. |
| `test_issue_2760_no_resultant_main_presentation` | Enforce user request | Markdown/HTML/DOCX/PDF text, report-bound JSON, and output manifest keys contain no main-presentation `resultant`, `total horizontal force`, or `heatmap` terms unless explicitly in an internal QA artifact. |
| `test_issue_2760_schematic_svg_contract` | Make schematics testable | Schematic source artifacts are SVG or have stable metadata IDs for ship outline, CoG, X/Y/N arrows, angle labels, and default numeric labels. |
| `test_issue_2760_docx_opens_and_contains_sections` | Verify Word output | Generated `.docx` opens with `python-docx` and contains required headings/sections. |
| `test_issue_2760_yaw_chart_caption_and_contract` | Prevent false equality expectation | Chart contains OCIMF `N` and `Y × arm`, caption says methods differ and are not equality-based, and same-sign/default-case convention is enforced. |
| `test_issue_2760_output_manifest` | Verify output package | Manifest lists Markdown, HTML, DOCX, PDF, CSV/JSON data, schematic assets, source/citation metadata, and supersession information. |
| Existing regression preservation | Ensure old stable behavior is not accidentally broken | Existing moored-current and current-heading tests pass or pre-existing red tests are listed with exact file/test names and baseline evidence. |

### Phase 2 — Calculation/source implementation

1. Replace placeholder current coefficient path with a source-pinned generic/reference OCIMF lookup resolved from the verified workbook/off-repo cache route, or stop with a blocker. Do not commit extracted coefficient corpora unless license approval is explicitly recorded.
2. Use existing OCIMF API where possible; if a new source wrapper is needed, keep formula/reference area/reference length/sign convention explicit and tested.
3. Implement fail-closed citation sidecars for OCIMF coefficients and rudder model constants.
4. Implement the approved screening-level simple rudder default with cited coefficient basis, rpm=0 velocity basis, 28° limitation text, lever arm/reference point, and sign mapping.
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
6. Commit/push actual changed repos with pathscoped staging and clean-worktree evidence; run with `SKIP_PUSH=1` where automation might auto-sync before verification, then verify post-push branch state/reflog evidence before claiming closeout.
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

First review round completed 2026-05-20. All reviewers returned MAJOR against the earlier blocked draft. The plan has now been patched to convert unresolved choices into explicit approval-scope assumptions and fail-closed implementation gates.

| Provider | Verdict | Primary blockers |
|---|---:|---|
| Claude | MAJOR | OCIMF citation/source gap; label-only sign tests; unapproved `-5°..+5°` heading plot; yaw comparison tolerance; rudder model under-specified. |
| Codex | MAJOR | OCIMF source open; uncited pseudocode formulas; rudder model under-specified; no independent numerical oracles; output governance too loose. |
| Gemini | MAJOR | OCIMF fixture hallucination risk; unresolved vessel class/rudder coefficient decisions; Word tooling unspecified; schematic tests need SVG/intermediate-data contract; repo-boundary wording. |

### Review-driven changes applied in this patched draft

- Removed any permission to invent OCIMF data during implementation.
- Converted OCIMF source, vessel class, rudder model basis, heading plot range, and yaw-comparison interpretation from unresolved blockers into explicit approval-scope assumptions.
- Added citation/fail-closed requirements for standards-derived coefficients/model constants.
- Replaced label-only test language with numeric sign/unit/golden-oracle tests.
- Added DOCX parsing and SVG/metadata schematic test requirements.
- Clarified repo boundary: `digitalmodel` is a sibling Git repo; `acma-projects/B1528/output` is under this `workspace-hub` checkout unless live preflight proves otherwise.
- Clarified that old report artifacts should be superseded with new filenames unless the user approves overwrite-in-place.

### Round 2 readiness synthesis

Main-session synthesis plus three read-only subagent reviews concluded that moving to `status:plan-review` is defensible after this patch because the remaining engineering choices are stated as assumptions for explicit owner approval, while source/citation availability remains fail-closed during implementation.

Residual risk: implementation may still stop if the OCIMF source PDFs/tables or rudder model citation cannot be materialized in a repo-safe form. That risk is intentionally preserved as a blocker-return gate, not hidden implementation discretion.

Approval request: user approval of this plan authorizes TDD implementation under the assumptions above, but no implementation begins until `status:plan-approved` is applied after explicit user approval.
