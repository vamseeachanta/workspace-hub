# Entail "Report-as-Backbone" → Ecosystem Mapping

**Date:** 2026-06-25
**Trigger:** Operator directive to incorporate the engineering-report concepts from [Entail's 2026 LinkedIn post](https://www.linkedin.com/posts/we-gave-liv-inger-bangstad-and-julie-anne-share-7475494525399027712-zwEp/) (Liv-Inger Bangstad / Julie Anne Holm) into the llm-wiki and the repo ecosystem.
**Companion (durable concept):** llm-wiki `wikis/engineering/wiki/concepts/report-as-backbone.md` + source `sources/2026-06-25-entail-report-as-backbone.md`.
**Precedent:** mirrors `analysis/prometheus-concepts-ecosystem-mapping-2026-06-11.md` — capture an external convergence, then map it onto what we already run and name the gap.

---

## 1. The four concepts (named for reuse)

Entail describes software as "the backbone of the marine operations analysis workflow," targeting a report that today costs "six months, hundreds of emails, countless meetings." Four ideas:

1. **Report-as-backbone** — the report *is* the workflow spine; it accretes continuously, it is not produced once at the end.
2. **Building blocks** — reports assembled from reusable, independently-maintained components, not authored as bespoke prose each time.
3. **Single source of truth** — one centralized store feeds report generation; nothing re-keyed from email/spreadsheet. The report is a *view*, not a *copy*.
4. **Shift-left analysis** — analysis/reporting moves to the front of operational decision-making; the deliverable informs the decision, it does not merely record it.

## 2. What the ecosystem already does (and where it's named)

| Concept | Realized today | Where |
|---|---|---|
| Report-as-backbone | Parametric report templates created before solver runs; batch fills slots | `digitalmodel` parametric report pipeline; llm-wiki `workflows/parametric-engineering-reports.md` |
| Building blocks | **Already a reference implementation** — `report_builders_header / _hydrostatics / _responses` + `report_data_models.py` + `report_generator.py` | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` |
| Single source of truth | Solver-queue `completed/` results + structured analysis stores read by templates | `digitalmodel` solver queue |
| Shift-left analysis | Staged fidelity (screening → reduced-order → high-fidelity); Deckhand real-time copilot at decision time | Engineering flywheel layer 3 + Deckhand |
| Computed-not-generated | Deterministic, code-edition-pinned engines; deliverables carry provenance | Engineering flywheel |

**The verdict: the doctrine is realized in pieces but not as a named, shared contract.**

## 3. The concrete gap

- The building-block report pattern exists in exactly **one** module — `hydrodynamics/diffraction/` (the `report_builders_*` + `report_data_models` + `report_generator` set).
- **31 other report generators** across `digitalmodel` are snowflakes — each reimplements section structure, rendering, and provenance handling independently: `ansys/report_generator.py`, `cathodic_protection/cp_reporting.py`, `fatigue/fatigue_reporting.py`, `structural/parametric_report.py`, `marine_ops/installation/suitability_report.py`, `asset_integrity/assessment/ffs_report.py`, `naval_architecture/b1528_sirocco_*_report.py`, …
- The Deckhand deliverable drops are **hand-authored standalone HTML** files, not generated from the same block library — so a fix to a block does not propagate, and provenance is not guaranteed.
- There is **no shared `digitalmodel.reporting` package**: no `ReportBlock` protocol, no `ReportDataModel` base, no report skeleton/backbone, no shared HTML/PDF renderer, no single declared data contract against the source-of-truth store.

This is exactly the "snowflake reports" + "copy-in results" anti-pattern named in the concept page. Entail's framing makes the fix legible: **promote the diffraction building-block pattern to a shared library, make every report read from one store through declared block contracts, and assemble deliverables from the catalog.**

## 4. Proposed work (tracer-bullet vertical slices)

PR-only on `digitalmodel` (protected main, never self-merge, CI baseline is red — compare PR check set vs. bare main). Issues to file (drafts in §5):

- **#A — Extract a shared `digitalmodel.reporting` block library.** Generalize the `hydrodynamics/diffraction/report_builders_*` pattern into a reusable package: `ReportBlock` protocol, `ReportDataModel` base, `ReportBackbone` skeleton, shared HTML/PDF renderer. Diffraction becomes the reference implementation that adopts the library (no behavior change).
- **#B — Single-source-of-truth data contract + provenance.** Define how a block reads from solver-queue `completed/` + structured stores via a declared contract; make provenance fields (code edition, assumptions, units, validated-path status) mandatory per block. Lint that fails any block that hand-pastes results.
- **#C — Migrate one snowflake onto the backbone (tracer bullet).** Convert `fatigue/fatigue_reporting.py` (or `structural/parametric_report.py`) to the block library, proving the path end-to-end before mass migration.
- **#D — Skeleton-first report CLI.** `uv run python -m digitalmodel.reporting <skeleton.yml>` instantiates a report backbone (sections + required blocks + acceptance criteria) at engagement kickoff, so analysis fills slots instead of being written up last.
- **#E (cross-repo) — Deckhand deliverables from the block library.** Generate the grounded-card HTML deliverables from the shared block library instead of hand-authoring, so building-block fixes and provenance propagate to client-facing cards (shift-left + building-blocks).

Suggested order: #A → #B → #C (tracer) → then #D and #E in parallel once the library is proven.

## 5. Issue text (FILED 2026-06-25)

> **STATUS:** all 5 filed.
> - #A → [digitalmodel#1018](https://github.com/vamseeachanta/digitalmodel/issues/1018)
> - #B → [digitalmodel#1019](https://github.com/vamseeachanta/digitalmodel/issues/1019)
> - #C → [digitalmodel#1020](https://github.com/vamseeachanta/digitalmodel/issues/1020)
> - #D → [digitalmodel#1021](https://github.com/vamseeachanta/digitalmodel/issues/1021)
> - #E → [workspace-hub#3239](https://github.com/vamseeachanta/workspace-hub/issues/3239) (cross-repo umbrella)

### Issue #A — `digitalmodel`: Extract shared `digitalmodel.reporting` block library
**Body:** The building-block report pattern (modular `report_builders_*`, `report_data_models`, `report_generator`) exists only in `hydrodynamics/diffraction/`; 31 other report generators are snowflakes. Generalize it into `digitalmodel/reporting/`: `ReportBlock` protocol (data contract + render + validate), `ReportDataModel` base, `ReportBackbone` skeleton, shared HTML/PDF renderer. Adopt it in the diffraction module first with **zero behavior change** (regression test: byte/structure-equal output). Reference: llm-wiki `concepts/report-as-backbone.md`. Labels: `domain:reporting`, `enhancement`.

### Issue #B — `digitalmodel`: Single-source-of-truth data contract + mandatory provenance
**Body:** Define the contract by which a `ReportBlock` reads results from solver-queue `completed/` and structured analysis stores — no hand-pasted numbers (the report is a view, not a copy). Make provenance mandatory per block: code edition, assumptions, units, validated-path status. Add a lint that fails any block reaching into ad-hoc paths or embedding literal results. Depends on #A. Reference: llm-wiki `concepts/report-as-backbone.md` (operating rules + anti-patterns). Labels: `domain:reporting`, `provenance`.

### Issue #C — `digitalmodel`: Migrate `fatigue_reporting` onto the block backbone (tracer bullet)
**Body:** Convert one existing snowflake report (`fatigue/fatigue_reporting.py`, fallback `structural/parametric_report.py`) to the shared block library from #A reading through the #B contract. Proves the migration path end-to-end and yields the template for the remaining 30. Depends on #A, #B. Labels: `domain:reporting`, `refactor`.

### Issue #D — `digitalmodel`: Skeleton-first report CLI
**Body:** `uv run python -m digitalmodel.reporting <skeleton.yml>` instantiates a report backbone (sections, required blocks, acceptance criteria) at engagement kickoff so analysis fills slots rather than being written up last (report-as-backbone). Depends on #A. Labels: `domain:reporting`, `enhancement`.

### Issue #E — Deckhand deliverables generated from the block library (cross-repo)
**Body:** Deckhand grounded-card deliverables are currently hand-authored standalone HTML. Generate them from the shared `digitalmodel.reporting` block library so block fixes and provenance propagate to client-facing cards (shift-left + building-blocks). Depends on #A. Repo: TBD (deckhand / deckhand-sandbox). Labels: `domain:reporting`, `deckhand`.

---

## 6. Strategic note

This is convergence, not a threat-first read. An independent team (Entail) reaching "report-as-backbone of the marine operations analysis workflow" in the same market validates the [engineering flywheel](../../llm-wiki/wikis/engineering/wiki/concepts/engineering-flywheel.md) layer-3 → deliverable path — same pattern as the Prometheus "artificial general engineer" bet validating the category at industrial scale. The differentiator stays **loop velocity + computed-not-generated provenance + a validated calc corpus**, not the reporting UI. The value Entail's framing adds here is *naming*: it turns a set of de-facto capabilities into an explicit build-order — every analysis workflow ships a report block; every block reads from one store; screening output exists early enough to inform the decision.
