# Plan for #2569: B1528 SIROCCO rudder source pack and benchmark extraction

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2569
> **Review artifacts:** scripts/review/results/2026-05-01-plan-2569-claude.md | scripts/review/results/2026-05-01-plan-2569-codex.md | scripts/review/results/2026-05-01-plan-2569-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: remote `vamseeachanta/acma-projects/B1528/excel_to_py/rudder_force_yaw_moment.py` — converted workbook logic for rudder-force/yaw-moment hand calculation.
- Found: remote `vamseeachanta/acma-projects/B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx` — authoritative ref-data workbook for B1528 rudder geometry and yaw moment worksheets.
- Gap: no durable B1528 source crosswalk or normalized benchmark table exists in `workspace-hub` knowledge/plans.

### Standards
| Standard | Status | Source |
|---|---|---|
| PNA Vol. III / maneuvering conventions | reference only | prior #2564 naval-architecture resource intelligence |
| IMO MSC/Circ.1053 | reference only | benchmark terminology only; no compliance claim in this issue |

### LLM Wiki pages consulted
- `knowledge/wikis/acma-projects/wiki/entities/b1528-sirocco-breakaway.md` — project/vessel source-intelligence page created before implementation.
- `knowledge/wikis/acma-projects/wiki/sources/b1528-rudder-force-yaw-moments-workbook.md` — workbook extraction and source limitations.
- `knowledge/wikis/acma-projects/wiki/sources/b1528-sirocco-breakaway-notes.md` — benchmark notes source page.
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — calculation inputs, aliases, and boundaries.

### Documents consulted

- `B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx` — workbook contains `Rudder Area and Geometry`, `Rudder Force`, `Yaw Moment` sheets. Extracted B1528 SIROCCO values include LBP `225.5 m`, rudder area `44.9395631937 m²`, rudder center aft of AP `-1.0520261379 m`, legacy yaw lever `0.6 * LBP = 135.3 m`, `β = 600`, and `Cr = 1.065/0.935`.
- `B1528/excel_to_py/rudder_force_yaw_moment.py` — converted workbook script exposes the legacy calculation family but hardcodes formulas and does not provide a reusable input/report workflow.
- `B1528/ref/SIROCCO breakaway notes.docx` — contains narrative heading/speed/time anchors and a turning/track benchmark, but evidence must be normalized before numerical comparison.
- `knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md` — newly created pre-work wiki page documenting extracted B1528 inputs and calculation boundaries.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — sign/coordinate convention background from prior yaw-moment work.
- #2564 — completed reusable yaw-moment sweep workflow for typical-ship/rudder cases.
- #2568 — approved/planned preliminary turning-circle/tactical-diameter estimator workflow.


### Gaps identified
- No canonical B1528 source-pack artifact links exact workbook sheets/cells/values to downstream yaw-moment/time-trace input files. The source pack must classify every value as `authoritative`, `derived`, `inferred`, or `gap` and must not force downstream code to re-mine `.xlsx`/`.docx` files at runtime.
- No normalized turning/track benchmark table exists for SIROCCO; the notes are narrative and require extraction with uncertainty/caveat fields. If no quantitative benchmark is recoverable, deliver a source-gap table instead of inventing a curve.
- Local `acma-projects` checkout is synchronized to origin but sparse; `B1528/` is not materialized locally, so this issue must record remote GitHub source paths and avoid assuming local file presence.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-01 via `gh issue view`):
- `#2569` — OPEN — docs(acma): B1528 SIROCCO rudder source pack and benchmark extraction
- `#2570` — OPEN — feat(naval-arch): B1528 SIROCCO yaw-moment input and interactive static report
- `#2571` — OPEN — feat(naval-arch): B1528 SIROCCO time-trace benchmark report with rudder inflow feedback

**Repo sync evidence**:
```text
## main...origin/main
0	0
B1528-not-materialized-sparse
```

**Extracted workbook evidence**:
```text
LBP = 225.5 m
Rudder area = 44.9395631937 m^2
Rudder center aft of AP = -1.0520261379 m
Yaw lever = 0.6 * LBP = 135.3 m (legacy workbook-derived yaw lever; not automatically equivalent to CG-to-rudder arm)
```

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-01-issue-2569-b1528-sirocco-source-pack.md |
| Wiki entity | knowledge/wikis/acma-projects/wiki/entities/b1528-sirocco-breakaway.md |
| Workbook source page | knowledge/wikis/acma-projects/wiki/sources/b1528-rudder-force-yaw-moments-workbook.md |
| Notes source page | knowledge/wikis/acma-projects/wiki/sources/b1528-sirocco-breakaway-notes.md |
| Input concept page | knowledge/wikis/acma-projects/wiki/concepts/b1528-sirocco-rudder-yaw-moment-inputs.md |
| Benchmark/source pack | docs/projects/acma/B1528/sirocco-rudder-source-pack.md |
| Structured benchmark table | docs/projects/acma/B1528/sirocco-turning-benchmark.yaml |

---

## Deliverable
A durable B1528 SIROCCO source/benchmark pack that downstream static yaw and time-trace issues can cite without re-mining the workbook and narrative notes.

---

## Pseudocode
```text
collect remote source paths from acma-projects/B1528
extract workbook sheet names, relevant cells, formulas, and values
extract breakaway-note time/heading/speed/track anchors into a table
classify each datum as authoritative, derived, narrative, or inferred
write source-pack markdown and benchmark YAML with units/source refs
validate llm-wiki status/lint and plan/source-pack consistency
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | docs/projects/acma/B1528/sirocco-rudder-source-pack.md | durable source crosswalk |
| Create | docs/projects/acma/B1528/sirocco-turning-benchmark.yaml | normalized benchmark evidence |
| Update | knowledge/wikis/acma-projects/wiki/index.md | index source intelligence |
| Update | docs/plans/README.md | plan index |

---

## TDD / Verification List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| wiki_status_acma_projects | wiki is initialized and healthy | acma-projects wiki | status OK |
| wiki_lint_acma_projects | wiki pages have valid frontmatter/links | acma-projects wiki | lint OK |
| source_pack_contains_required_values | extracted source pack includes LBP/rudder area/yaw lever | source pack markdown | values with units and source paths |
| benchmark_yaml_schema | benchmark YAML is parseable and contains uncertainty/source fields | benchmark YAML | valid schema |

---

## Acceptance Criteria
- [ ] HARD STOP: after this plan reaches `status:plan-review`, wait for explicit user approval / `status:plan-approved` before implementation.
- [ ] `UV_NO_SYNC=1 uv run scripts/knowledge/llm_wiki.py status --wiki acma-projects` passes.
- [ ] `UV_NO_SYNC=1 uv run scripts/knowledge/llm_wiki.py lint --wiki acma-projects` passes.
- [ ] Source crosswalk includes exact B1528 file paths, workbook sheet names/cells or named ranges where recoverable, units, extracted values, and derived-value notes.
- [ ] Benchmark table separates direct notes from inferred/calculated fields and states uncertainty/caveats.
- [ ] #2570 and #2571 can cite this source pack for inputs and benchmark evidence.

---

## Adversarial Review Summary
| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Tighten provenance/status handling; separate workbook geometry, AP-location, and yaw-lever semantics; add source-gap mode for narrative benchmark notes. |
| Codex | MINOR | Add machine-readable source-pack/benchmark schema; distinguish authoritative/derived/inferred values; forbid downstream runtime re-mining. |
| Gemini | MINOR | Add explicit approval gate; state not blocked by #2568; strengthen uncertainty/canonical-artifact contract. |

**Overall result:** PASS after revision — all findings addressed in this plan; implementation remains blocked until user approval.

Revisions made based on review:
- Added explicit source-status, sparse-checkout, and benchmark source-gap boundaries.
- Clarified that `0.6 * LBP` is a legacy yaw lever and not automatically a CG-based arm.
- Added machine-readable benchmark/source-pack acceptance criteria and artifact ownership under `workspace-hub`.
- Added explicit hard-stop approval language.


---

## Risks and Open Questions
- **Risk:** Narrative breakaway notes may not contain enough structured time/position data for quantitative benchmark overlay; if so, deliver an explicit source-gap report.
- **Risk:** B1528 remains sparse locally; implementation should use GitHub API/raw downloads or materialize only the needed sparse path after sync.

---

## Complexity: T2
**T2** — documentation/source-intelligence deliverable with structured YAML validation and wiki updates, but no numerical implementation.
