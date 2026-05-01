# Plan for #2570: B1528 SIROCCO yaw-moment input and interactive static report

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-05-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2570
> **Review artifacts:** scripts/review/results/2026-05-01-plan-2570-claude.md | scripts/review/results/2026-05-01-plan-2570-codex.md | scripts/review/results/2026-05-01-plan-2570-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` from #2564 — reusable static yaw-moment sweep workflow, YAML input, provenance, CSV/JSON/chart outputs.
- Found: `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` — existing rudder normal force helper used by #2564/#2565.
- Found: `B1528/excel_to_py/rudder_force_yaw_moment.py` — legacy project workbook conversion; useful for regression hand checks, not a reusable report workflow.
- Gap: no B1528-specific yaw-moment input YAML/report exists.

### Standards
| Standard | Status | Source |
|---|---|---|
| PNA Vol. III / sign conventions | reference only | #2564 resource-intelligence / naval-architecture wiki |
| IMO turning metrics | not implemented | benchmark naming only; no compliance claim |

### LLM Wiki pages consulted
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — B1528 extracted values and static yaw scope.
- `knowledge/wikis/acma-projects/wiki/sources/b1528-rudder-force-yaw-moments-workbook.md` — workbook formulas/values and limitations.
- `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` — reusable yaw-moment methodology from #2564.
- `knowledge/wikis/naval-architecture/wiki/concepts/rudder-force-modeling.md` — rudder-force model caveats.

### Documents consulted

- `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx` — workbook contains `Rudder Area and Geometry`, `Rudder Force`, `Yaw Moment` sheets. Extracted B1528 SIROCCO values include LBP `225.5 m`, rudder area `44.9395631937 m²`, rudder center aft of AP `-1.0520261379 m`, legacy yaw lever `0.6 * LBP = 135.3 m`, `β = 600`, and `Cr = 1.065/0.935`.
- `B1528/excel_to_py/rudder_force_yaw_moment.py` — converted workbook script exposes the legacy calculation family but hardcodes formulas and does not provide a reusable input/report workflow.
- `B1528/ref/SIROCCO breakaway notes.docx` — contains narrative heading/speed/time anchors and a turning/track benchmark, but evidence must be normalized before numerical comparison.
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — newly created pre-work wiki page documenting extracted B1528 inputs and calculation boundaries.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — sign/coordinate convention background from prior yaw-moment work.
- #2564 — completed reusable yaw-moment sweep workflow for typical-ship/rudder cases.
- #2568 — approved/planned preliminary turning-circle/tactical-diameter estimator workflow.


### Gaps identified
- Need a project input file that records B1528 geometry, units, source paths, assumed 2.5 kn speed, ±1° rudder-angle cases, and broader speed/angle sweeps. The input must declare the calculation mode: `workbook_regression`, `digitalmodel_static_yaw`, or both with separately labeled outputs.
- Need interactive charts for yaw moment vs rudder angle by speed and yaw moment vs speed by rudder angle.
- Need source-workbook regression checks against preliminary hand values.
- Need report boundary stating preliminary rudder-induced yaw moment, not full MMG or incident reconstruction.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-01 via `gh issue view`):
- `#2564` — CLOSED/DONE — reusable yaw-moment sweep implemented.
- `#2566` — approved by user via labels — quality validation follow-up.
- `#2569` — OPEN — B1528 source pack prerequisite.
- `#2570` — OPEN — this issue.

**Preliminary hand-check operating point**:
```text
U = 2.5 kn = 1.2861 m/s
Area = 44.9395631937 m^2
LBP = 225.5 m; yaw lever = 135.3 m
+1 deg, Cr=1.065 -> +11.435 mt-m ≈ +112.143 kN-m
-1 deg, Cr=0.935 -> -10.040 mt-m ≈ -98.454 kN-m
```

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-01-issue-2570-b1528-sirocco-yaw-moment-report.md |
| Tests | digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py |
| Input YAML | digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_yaw_moment.yml |
| Report generator / project wrapper | digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_yaw_report.py |
| Static report | digitalmodel/docs/domains/marine-engineering/b1528-sirocco-yaw-moment-report.md |
| Interactive report output | digitalmodel/outputs/b1528_sirocco/yaw_moment_report.html |

---

## Deliverable
A B1528 SIROCCO yaw-moment input file and detailed interactive static report covering 2.5 kn ±1° cases plus speed/angle sweeps.

---

## Pseudocode
```text
load B1528 YAML with geometry, units, source refs, speed grid, rudder-angle grid
validate rudder area > 0, LBP > 0, speed grid includes 2.5 kn, angles include +/-1 deg
run reusable yaw moment calculation or workbook-compatible regression mode
produce row per speed/angle/rotation-factor case
for workbook_regression mode, check 2.5 kn +/-1 deg against hand-check target values within tolerance; for digitalmodel_static_yaw mode, check against deterministic values from that model and label outputs separately
write CSV/JSON/provenance/manifest
build interactive Plotly charts: Mz vs angle by speed; Mz vs speed by angle; +/-1 deg comparison
render detailed markdown/HTML report with assumptions, formulas, sources, caveats
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py | TDD for B1528 input/report |
| Create | digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_yaw_moment.yml | project input file |
| Create | digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_yaw_report.py | report/project wrapper if reusable module needs wrapper |
| Update | digitalmodel/pyproject.toml | package data inclusion if needed |
| Create | digitalmodel/docs/domains/marine-engineering/b1528-sirocco-yaw-moment-report.md | durable report docs |
| Update | docs/plans/README.md | plan index |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_packaged_b1528_yaml_loads | packaged input is available and parseable | package resource | YAML with source refs |
| test_b1528_required_values | B1528 geometry matches source pack | YAML | area 44.9395631937, LBP 225.5 |
| test_b1528_operating_point_plus_one | +1° at 2.5 kn regression | YAML case | +112.143 kN-m approx or documented model-equivalent |
| test_b1528_operating_point_minus_one | -1° at 2.5 kn regression | YAML case | -98.454 kN-m approx or documented model-equivalent |
| test_interactive_report_outputs | report contains expected plots/tables | temp output dir | HTML + CSV/JSON/provenance/manifest |
| test_no_compliance_overclaim | report caveats are present | report text | no IMO/class compliance claims |

---

## Acceptance Criteria
- [ ] HARD STOP: after this plan reaches `status:plan-review`, wait for explicit user approval / `status:plan-approved` before implementation.
- [ ] #2569 is completed or provides an explicitly approved source-pack subset before source values are treated as authoritative.
- [ ] Tests are written before implementation and pass with `UV_NO_SYNC=1 uv run pytest tests/naval_architecture/test_b1528_sirocco_yaw_moment.py -q`.
- [ ] Targeted regression with existing yaw/rudder suites passes.
- [ ] B1528 YAML includes units, source paths, aliases (`SIROCCO`/`Sorrocco`), assumptions, calculation mode, lever-arm mapping evidence, and citation/provenance metadata.
- [ ] Static report includes yaw moment charts for varying forward speed and rudder attack angle.
- [ ] Dedicated 2.5 kn `+1°` and `-1°` case table is included.
- [ ] Interactive charts are generated and referenced by the report.
- [ ] Report explicitly limits scope to preliminary rudder-induced yaw moment, distinguishes workbook-regression vs reusable-model outputs, and does not use #2566 as a substitute for user approval.

---

## Adversarial Review Summary
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR -> RESOLVED | Separate workbook-regression and reusable static-yaw model variants; add lever-arm mapping gate. |
| Codex | MAJOR -> RESOLVED | Replace loose "model-equivalent" tests with deterministic expectations per selected model; verify package data and temp-dir report outputs. |
| Gemini | MAJOR -> RESOLVED | Make #2569 an explicit blocker; treat #2566 as validation/hardening, not execution authority; define interactive artifact placement. |

**Overall result:** PASS after revision — major findings resolved in plan text; implementation remains blocked until user approval.

Revisions made based on review:
- Added #2569 as a hard blocker for source values and benchmark evidence.
- Required explicit method mode: `workbook_regression` and/or `digitalmodel_static_yaw`, with separate outputs and labels if both are used.
- Required a lever-arm mapping gate before any workbook value is mapped into `x_rudder_from_cg_m`.
- Required deterministic regression values per model mode and temp-directory artifact tests.
- Clarified #2566 as a quality-hardening reference, not an approval substitute.


---

## Risks and Open Questions
- **Risk:** #2564 reusable formula may differ from legacy workbook constants; if so, report must label model variants and not silently mix them.
- **Risk:** Propeller rotation factor/sign convention requires explicit mapping to port/starboard source workbook terminology.
- **Open:** Whether final output should live only in `digitalmodel` docs or also be mirrored under `workspace-hub/docs/projects/acma/B1528/`.

---

## Complexity: T3
**T3** — project-specific engineering calculation with packaged input, regression checks, provenance, interactive visualization, and report generation.
