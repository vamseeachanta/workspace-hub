# Plan for W3-D: feat(llm-wiki): engineering wiki riser sub-domain topical expansion — 8 core concept pages

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2597 (sibling to #2589 W1-D, #2588 W1-C, #2592 W2-C, #2593 W2-D under the #2540 Elements wave)
> **Review artifacts:** `scripts/review/results/2026-05-02-plan-W3D-engineering-riser-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

Wiki target tree: `knowledge/wikis/engineering/wiki/` — 105 markdown files on disk; `index.md` frontmatter `page_count` reads 82 because the index regenerator counts only the curated catalogue table rows (concepts + entities + sources + standards + workflows = 32 + 22 + 13 + 7 + 4 + 4 ≈ 82) and excludes `index.md`/`log.md`/`overview.md`/`SCHEMA.md`/`SOURCE_INVENTORY.md` plus the un-tabled lunch-and-learn pointer rows. This plan will bump `page_count` 82 → 90 (+8 new pages) while the on-disk file count moves 105 → 113. Directory schema mandated by `knowledge/wikis/engineering/CLAUDE.md` (concepts/, entities/, sources/, standards/, workflows/, plus index/log/overview).

- Found: 1 existing riser page on disk —
  - `concepts/viv-riser-fatigue.md` (vortex-induced vibration, current discretisation, wake interference, S-N curve / DFF for SCR girth welds; references DNV-RP-C203 + DNV-RP-F204).
- Found: 7 riser-adjacent concept pages that touch but do not own riser geometry, configuration, or design-state physics —
  - `concepts/free-span-viv-fatigue.md` (PIPELINE free-span scope per DNV-RP-F105, NOT riser).
  - `concepts/cfd-offshore-hydrodynamics.md` (Morison, VIV CFD validation — generic).
  - `concepts/fatigue-analysis-offshore.md` (S-N + Miner — generic to mooring/riser/hull).
  - `concepts/sn-curve-fatigue-definitions.md` (DNV-RP-C203 weld categories — generic).
  - `concepts/structural-analysis-offshore.md` (ULS/ALS, buckling — generic).
  - `concepts/wave-theory-offshore.md` (JONSWAP, extreme values — generic).
  - `concepts/hydrodynamic-analysis.md` (BEM, RAOs, QTFs — vessel-side, not riser-side).
- Found: 7 codified standards pages — `standards/api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md` (note: `ocimf-tandem-mooring.md` exists on disk but is not yet in `index.md` standards table — out of scope here).
- Found: digitalmodel module footprint —
  - `digitalmodel/src/digitalmodel/drilling_riser/` package (`damping.py`, `operability.py`, `stackup.py`, `tool_passage.py`, `adapter.py`).
  - `digitalmodel/scripts/run_riser_analysis.py`, `benchmark_riser_library.py`, `mesh_sensitivity_riser.py`, `extract_riser_validation.py`, `capture_riser_views.py`.
  - `digitalmodel/tests/test_catenary_riser_summary.py`, `digitalmodel/tests/drilling_riser/`, `digitalmodel/tests/orcaflex/test_riser_config.py`, `digitalmodel/tests/subsea/catenary_riser/`.
  - `digitalmodel/.github/workflows/catenary-riser-tests.yml` (CI runs catenary-riser tests).
  - `digitalmodel/docs/domains/risers/{risers.md, damping.md, _installation.md}` and `digitalmodel/docs/domains/riser_analysis/stackup_schematic/`.
  - All these are calc-side modules with zero current cross-references back into `knowledge/wikis/engineering/wiki/concepts/` (verified via grep — see Evidence). The new concept pages will make those modules reachable from the wiki (concept pages will themselves not edit calc-side files; that is calc-side follow-up work under the citation-contract rule).
- Gap: every riser configuration topology (free-hanging catenary, lazy-wave, steep-wave, lazy-S, pliant-wave, hybrid riser tower) lacks a dedicated concept page; SCR design considerations (touchdown-point migration, soil-riser interaction trench, departure-angle envelope) are scattered across `viv-riser-fatigue.md` only; TTR-specific topics (top-tension envelope, tensioner stroke, taper joint, stress joint, keel joint) are uncovered; flexible-riser annulus integrity and bend-stiffener fatigue are uncovered; drilling-riser air-gap / weak-point / disconnect topics are uncovered despite the `frontierdeepwater/Engineering/risers/Airgap/` corpus and the `digitalmodel/drilling_riser/operability.py` module; J-tube / I-tube pull-in transitions are uncovered; riser global-design load-case taxonomy (extreme, fatigue, accidental, installation) is uncovered.

### Standards

This plan will create **concept pages**, not standards pages. Per `.claude/rules/calc-citation-contract.md`, only calc modules emit `Citation` instances; concept pages name standards bodies and titles by reference but do not enumerate clauses, thresholds, or formulas. Future standards-page promotion (when a calc module imports a constant from one of these standards) will follow the #2471-sanctioned `wiki/standards/<code-id>.md` routing principle, using the precedent set by `dnv-rp-c203.md`, `dnv-os-f201.md` (parallel sibling W3-B per prompt — currently planned, not yet codified at the time of writing), and `api-579-ffs.md`. Standards-page production is therefore **out of scope for this plan**.

| Standard | Status | Source |
|---|---|---|
| API RP 17B (Flexible Pipe — Recommended Practice) | referenced (no codified standards page yet) | https://www.api.org/products-and-services/standards |
| API RP 17J (Specification for Unbonded Flexible Pipe) | referenced (no codified standards page yet) | https://www.api.org/products-and-services/standards |
| API RP 16Q (Design, Selection, Operation, and Maintenance of Marine Drilling Riser Systems) | referenced (no codified standards page yet) | https://www.api.org/products-and-services/standards |
| API RP 2RD (Dynamic Risers for Floating Production Systems) | referenced (no codified standards page yet) | https://www.api.org/products-and-services/standards |
| DNV-OS-F201 (Dynamic Risers — offshore standard) | referenced (W3-B sibling plan handles ISO 19901-7 family; this plan cites DNV-OS-F201 by title and URL) | https://www.dnv.com/oilgas/download/dnv-os-f201-dynamic-risers/ |
| DNV-RP-F202 (Composite Risers — Recommended Practice) | referenced | https://www.dnv.com/ |
| DNV-RP-F204 (Riser Fatigue) | referenced — already cited by `concepts/viv-riser-fatigue.md` | https://www.dnv.com/ |
| ISO 13628-2 (Petroleum and natural gas industries — Subsea production systems — Part 2: Unbonded flexible pipe systems for subsea and marine applications) | referenced | https://www.iso.org/standard/41322.html |
| ISO 13628-7 (Petroleum and natural gas industries — Subsea production systems — Part 7: Completion/workover riser systems) | referenced | https://www.iso.org/ |
| ISO 13624-1 (Petroleum and natural gas industries — Drilling and production equipment — Part 1: Design and operation of marine drilling riser equipment) | referenced (correct ISO part for marine drilling riser; replaces the prior plan's mis-attribution of ISO 19901-7 to riser scope) | https://www.iso.org/standard/41927.html |
| ISO 19901-7 (Petroleum and natural gas industries — Specific requirements for offshore structures — Part 7: Stationkeeping systems for floating offshore structures and mobile offshore units) | referenced for **mooring/stationkeeping context only** (not riser scope); included here because riser-vessel interface boundary depends on the stationkeeping reference frame. **Correction relative to prompt framing:** the prompt's claim that "W3-B handles ISO 19901-7 family" mis-locates 19901-7 in the riser substrate; ISO 19901-7 is stationkeeping-scope. New riser-design pages will cite 19901-7 only as a boundary/reference-frame pointer (e.g., "vessel offset envelope per ISO 19901-7"), not as a riser standard. | https://www.iso.org/standard/77017.html |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/index.md` — 82 catalogued pages; concepts table = 32 rows; entities = 22; sources = 13; standards = 7; workflows = 4; comparisons empty. Last regenerated 2026-04-29.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (`title`, `tags`, `added`, `last_updated` mandatory; `sources`, `domain`, `cross_links` recommended; standards pages additionally use `code_id`, `publisher`, `revision` per #2471).
- `knowledge/wikis/engineering/wiki/concepts/viv-riser-fatigue.md` (lines 1–106) — confirms current concept-page style: H2 sections, tables, `[[wikilink]]` cross-references, ≤2-page typical depth. Already names DNV-RP-C203, DNV-RP-F204, OrcaFlex, SHEAR7, VIVANA. **Risk: any new VIV-adjacent page must explicitly delineate boundary against this page.**
- `knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md` (lines 1–15) — pipeline-only scope per DNV-RP-F105; does NOT cover riser VIV; confirms boundary is intact.
- `knowledge/wikis/engineering/wiki/concepts/fatigue-analysis-offshore.md` (lines 1–15) — generic scope across mooring/riser/hull/joints; no riser-specific load-case taxonomy.
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md`, `dnv-os-e301.md`, `dnv-rp-f105.md`, `api-579-ffs.md` — frontmatter style for standards pages confirmed (`code_id`, `publisher`, `revision` on the newer pages per #2471).

### Documents consulted

- `docs/plans/_template-issue-plan.md` — followed verbatim; retrieval contract requires ≥3 distinct sources with embedded evidence.
- `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md` — identical-shape precedent for the naval-architecture wiki (W1-D); this plan reuses the boundary-page pattern, the ≤400-word cap, the standards-name-without-thresholds rule, and the seed-file-driven index-regen workflow concept (with adaptation: engineering wiki has no formal seed YAML — see Risk below).
- `.claude/rules/calc-citation-contract.md` — concept pages do NOT emit `Citation` instances; standards-page promotion deferred.
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — engineering wiki IS in routing-principle scope; `wiki/standards/<code-id>.md` reserved for codified standards; concept pages stay in `wiki/concepts/`.
- Memory `project_doc_intel_operating_model.md` — engineering wiki is the document-intelligence surface for the digitalmodel calc layer; gap-closure feeds calc-citation provenance.
- #2540 — OPEN, "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- #2588 — OPEN, "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)" — sibling audit; this plan is a forward-pull of one of the gap-buckets W1-C will identify (riser sub-domain). The plan's child-issue scope is **independent** of W1-C; if W1-C surfaces a competing prioritization, this plan can be re-sequenced without revision.
- #2589 — OPEN, "feat(llm-wiki): naval-architecture wiki topical expansion (W1-D)" — sibling shape; same wave; non-overlapping wiki target.
- #2592 — OPEN, "feat(llm-wiki): maritime-law wiki topical expansion (W2-C)" — sibling.
- #2593 — OPEN, "audit(data): online-resource-registry refresh (W2-D)" — sibling.
- /mnt/ace inventory: 32 directories under `/mnt/ace/2H/` including `2100 BLK31 SLOR Design`, `31057 ENI Riser and Subsea Structures Analysis`, `31098 Grupo-R Piklis-1DL Drilling Riser Analysis`, `31242 Shell Prelude Riserless Completion`, `31305 Drilling Risers Wellheads and Conductors`, `31381 Riser Market Study`, `31519 FMOG Marlin TTR Life Extension`, `31584 Drilling Riser IM`, `3425 Repsol Suriname Drilling Riser Analysis`, `3824 BP Macondo Containment Riser Analysis`. Plus `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements/`, `/mnt/ace/digitalmodel/docs/risers/literature/{Catenary Curve.pdf, RP-F105.pdf}`, `/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/`, `/mnt/ace/frontierdeepwater/Engineering/risers/Airgap/`, `/mnt/ace/client_projects/energy_drilling_riser/{Diverter and riser man.pdf, NOV riser man.pdf}`, `/mnt/ace/aceengineer-admin/Experience/{FDAS_Check_RiserAnalysis.pdf, 2016-11_FDAS_MooringRiserAnalysis.pdf}`, `/mnt/ace/client_projects/energy_integrity/0191 KBR MC518 Riser FFS`, `/mnt/ace/client_projects/energy_integrity/0183 KBR Riser FFS`. Plan will NOT extract from these PDFs (per #2482 deny-list); concept pages will cite them by reference.
- WebSearch — "API RP 17B flexible pipe technical content": API RP 17B (4th edition, Mar 2014, errata Aug 2017) covers unbonded flexible pipe configurations (free-hanging catenary, lazy-wave, steep-wave, lazy-S, steep-S, pliant-wave, Chinese lantern, S- and tethered-S), end-fittings, ancillary components (bend stiffener, bend restrictor, buoyancy modules, tether clamp, mid-water arch), failure modes (annulus flooding, tensile-armour buckling/birdcaging, pressure-armour fatigue, polymer-sheath ageing, bend-stiffener fatigue), and design loads. Companion document API RP 17J (4th ed.) is the unbonded-flexible-pipe specification.
- WebSearch — "DNV-OS-F201 riser standards table of contents": DNV-OS-F201 "Dynamic Risers" (current edition Aug 2010 with later amendments) covers metallic-riser design philosophy (LRFD + WSD), design loads, global analysis methods (regular-wave/irregular-wave/Morison/diffraction), strength criteria (ULS, ALS, FLS, SLS), riser materials, fabrication, installation, operation, and decommissioning. Sibling DNV-OS-F101 (Submarine Pipeline Systems) is pipeline-scope and is **explicitly excluded** from this plan.
- digitalmodel cross-refs: `digitalmodel/src/digitalmodel/drilling_riser/operability.py` implements drilling-riser operability envelopes (top tension, weather window, recoil); `damping.py` covers riser structural and hydrodynamic damping; `stackup.py` builds the riser joint stackup; `tool_passage.py` covers tool passage / drift diameter. `digitalmodel/tests/orcaflex/test_riser_config.py` exercises the OrcaFlex riser model bridge.

### Gaps identified

Coverage matrix vs. canonical riser-engineering curriculum (API RP 17B + DNV-OS-F201 + API RP 16Q + 2H Offshore corpus topics):

| Canonical topic | Current wiki status | Action |
|---|---|---|
| Riser configuration topologies (free-hanging, lazy-wave, steep-wave, lazy-S, pliant-wave, tethered) | gap | **NEW** `concepts/riser-configurations.md` |
| Steel catenary riser (SCR) global design — touchdown, departure angle, soil trench | partial — VIV-only on `viv-riser-fatigue.md` | **NEW** `concepts/steel-catenary-riser-design.md` |
| Top-tensioned riser (TTR) — tensioner, stress joint, taper joint, keel joint, stroke envelope | gap | **NEW** `concepts/top-tensioned-riser-design.md` |
| Flexible riser — bonded vs unbonded, layer architecture, annulus integrity, bend stiffener, end-fitting | gap | **NEW** `concepts/flexible-riser-design.md` |
| Hybrid riser tower / single-line offset riser (SLOR) / bundled tower | gap (raw `/mnt/ace/2H/2100 BLK31 SLOR Design`) | **NEW** `concepts/hybrid-riser-tower.md` |
| Drilling riser system — slip joint, telescopic joint, LMRP/BOP, air-gap, weak-point disconnect, recoil | gap (`drilling_riser/operability.py` exists) | **NEW** `concepts/drilling-riser-system.md` |
| Riser global-analysis load-case taxonomy — extreme/strength, fatigue (wave + VIV + slugging + 1st/2nd-order), accidental, installation | gap | **NEW** `concepts/riser-global-analysis-load-cases.md` |
| Riser-soil interaction — touchdown trench, riser soil stiffness models, P-y-equivalent vertical | gap | **NEW** `concepts/riser-soil-interaction.md` |
| J-tube / I-tube pull-in | gap | not in this batch — defer |
| Composite risers (DNV-RP-F202) | gap | not in this batch — defer |
| Workover/completion riser (ISO 13628-7) | gap | not in this batch — defer |
| Riser monitoring / integrity management | partial (digitalmodel `0148 Drilling Riser Integrity` corpus) | not in this batch — defer |
| Riser installation methods (reel-lay, J-lay, S-lay specific to risers, top-down) | gap | not in this batch — defer |
| VIV riser fatigue | covered (`viv-riser-fatigue.md`) | leave |
| Free-span pipeline VIV | covered (`free-span-viv-fatigue.md`) | leave (pipeline scope, NOT riser) |
| Pipeline integrity / FFS | covered (`pipeline-integrity-assessment.md`) | leave (pipeline scope, OUT OF SCOPE per prompt) |
| Mooring physics / mooring failure | covered (`mooring-line-failure-physics.md`) | leave (mooring scope, OUT OF SCOPE per prompt) |
| Subsea umbilical | covered (`subsea-umbilical-system.md`) | leave (umbilical scope, NOT riser) |

**Top-8 selected for this expansion** (foundational + cross-linkable, citable canonical reference, raw source on /mnt/ace and/or digitalmodel module presence):

1. `concepts/riser-configurations.md` — topology taxonomy; cross-links to all 7 below.
2. `concepts/steel-catenary-riser-design.md` — SCR boundary against `viv-riser-fatigue.md`.
3. `concepts/top-tensioned-riser-design.md` — TTR; cross-links to `digitalmodel/drilling_riser/` for shared tensioner physics.
4. `concepts/flexible-riser-design.md` — unbonded-flexible scope per API RP 17B/17J + ISO 13628-2.
5. `concepts/hybrid-riser-tower.md` — SLOR / hybrid tower; cross-link to `2H/2100 BLK31 SLOR Design`.
6. `concepts/drilling-riser-system.md` — drilling-riser operability + recoil; cross-link to `digitalmodel/drilling_riser/operability.py` + `damping.py`.
7. `concepts/riser-global-analysis-load-cases.md` — load-case taxonomy crosscutting all riser types.
8. `concepts/riser-soil-interaction.md` — soil-riser stiffness models for touchdown trench (cross-link to `viv-riser-fatigue.md` TDP discussion + `pile-capacity-alpha-method.md` for soil-shear correlation framing).

(9th candidate `concepts/riser-installation-methods.md` and 10th candidate `concepts/composite-riser-design.md` deferred to a follow-up batch to keep this batch at exactly 8 + index update; surfaces as Open Question below.)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):

- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- `#2588` — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)" — sibling audit identifying riser sub-domain as one gap-bucket.
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion (W1-D)" — same-shape sibling.
- `#2592` — OPEN — "feat(llm-wiki): maritime-law wiki topical expansion (W2-C)".
- `#2593` — OPEN — "audit(data): online-resource-registry refresh (W2-D)".

**File existence** (`find … -type f` 2026-05-02):

- EXISTS: `knowledge/wikis/engineering/wiki/index.md` (82 pages catalogued; on-disk count 105).
- EXISTS: `knowledge/wikis/engineering/CLAUDE.md` (frontmatter schema authority).
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/viv-riser-fatigue.md` (105 lines; sole existing riser page).
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md` (pipeline scope, not riser).
- EXISTS: `knowledge/wikis/engineering/wiki/standards/{api-579-ffs,dnv-os-e301,dnv-rp-c203,dnv-rp-c205,dnv-rp-f101,dnv-rp-f105,ocimf-meg4,ocimf-tandem-mooring}.md`.
- EXISTS: `digitalmodel/src/digitalmodel/drilling_riser/{adapter,damping,operability,stackup,tool_passage}.py`.
- EXISTS: `/mnt/ace/2H/{2100 BLK31 SLOR Design, 31057 ENI Riser and Subsea Structures Analysis, 31098 Grupo-R Piklis-1DL Drilling Riser Analysis, 31242 Shell Prelude Riserless Completion, 31305 Drilling Risers Wellheads and Conductors, 31381 Riser Market Study, 31519 FMOG Marlin TTR Life Extension, 31584 Drilling Riser IM, 3425 Repsol Suriname Drilling Riser Analysis, 3824 BP Macondo Containment Riser Analysis}/`.
- EXISTS: `/mnt/ace/digitalmodel/docs/risers/literature/{Catenary Curve.pdf, RP-F105.pdf}`.
- EXISTS: `/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements/`.
- MISSING (this plan creates): `concepts/riser-configurations.md`, `concepts/steel-catenary-riser-design.md`, `concepts/top-tensioned-riser-design.md`, `concepts/flexible-riser-design.md`, `concepts/hybrid-riser-tower.md`, `concepts/drilling-riser-system.md`, `concepts/riser-global-analysis-load-cases.md`, `concepts/riser-soil-interaction.md`.
- MISSING (this plan creates): `tests/knowledge/test_engineering_riser_expansion.py`.

**Line excerpts** (from `concepts/viv-riser-fatigue.md` lines 1–8 — frontmatter contract this plan must reproduce):

```
---
title: "VIV Riser Fatigue Analysis"
tags: [viv, riser, fatigue, orcaflex, sn-curve, dnv-rp-c203]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---
```

**Riser terminology baseline in current wiki** (`grep -rohE "(SCR|TTR|hybrid riser|catenary riser|J-tube|VIV|riser fatigue|wave-induced)" knowledge/wikis/engineering/wiki/ | sort | uniq -c`):

```
   1 catenary riser
   2 riser fatigue
   2 SCR
  57 VIV
   0 TTR
   0 hybrid riser
   0 J-tube
   0 wave-induced
```

This confirms: VIV is dense (57 hits) but every other riser concept is either zero or near-zero — strong gap signal.

**digitalmodel cross-ref baseline** (zero-cross-ref claim verification — `grep -rE "knowledge/wikis/engineering" digitalmodel/src/ digitalmodel/scripts/ digitalmodel/tests/ 2>&1 | wc -l`):

- Result: 0 — confirms calc-side modules do not yet reference back into the engineering wiki. Adding these concept pages will not by itself create a cross-ref; that will remain calc-side work for a follow-up issue under the citation-contract rule.

**Gap proofs**:

- `find knowledge/wikis/engineering/wiki -iname "*riser*"` returns ONLY `concepts/viv-riser-fatigue.md` — confirms 1 existing riser page.
- `ls knowledge/wikis/engineering/wiki/comparisons/` → "(empty)" — comparisons table is empty per `index.md` line 125.
- `find knowledge/seeds -iname "*engineering*"` returns no result — engineering wiki has **no formal seed YAML** unlike naval-architecture (`naval-architecture-resources.yaml`); index regeneration for engineering wiki is therefore manual edit, not seed-driven (Risk noted below).

**Out-of-scope phrase guard** (per prompt):

- "pipeline" → existing pipeline pages (`pipeline-integrity-assessment.md`, `free-span-viv-fatigue.md`) will not be touched.
- "mooring" → existing mooring pages (`mooring-line-failure-physics.md`, `dnv-os-e301.md`, `ocimf-meg4.md`) will not be touched.
- "structural" → existing `structural-analysis-offshore.md` will not be touched.

<!-- Source count: 11 distinct sources cited above —
  (1) issue context / parent-wave (#2540),
  (2) wiki index,
  (3) wiki CLAUDE.md schema,
  (4) #2588 W1-C audit,
  (5) #2589 W1-D shape precedent,
  (6) /mnt/ace 2H corpora inventory,
  (7) /mnt/ace digitalmodel riser literature inventory,
  (8) digitalmodel module footprint (drilling_riser package),
  (9) WebSearch API RP 17B/17J,
  (10) WebSearch DNV-OS-F201,
  (11) calc-citation-contract.md.
  Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2597-llm-wiki-W3D-engineering-riser-expansion.md` |
| Tests | `tests/knowledge/test_engineering_riser_expansion.py` |
| Implementation (8 wiki pages) | `knowledge/wikis/engineering/wiki/concepts/{riser-configurations, steel-catenary-riser-design, top-tensioned-riser-design, flexible-riser-design, hybrid-riser-tower, drilling-riser-system, riser-global-analysis-load-cases, riser-soil-interaction}.md` |
| Index update | `knowledge/wikis/engineering/wiki/index.md` |
| Log update | `knowledge/wikis/engineering/wiki/log.md` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-W3D-engineering-riser-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-W3D-engineering-riser-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-W3D-engineering-riser-gemini.md` |

---

## Deliverable

Eight new concept pages will exist under `knowledge/wikis/engineering/wiki/concepts/`, each carrying `CLAUDE.md`-compliant frontmatter, ≥1 standards-body cross-reference (API / DNV / ISO), ≥2 `see_also`-equivalent cross-links (using the existing `[[wikilink]]` convention from `viv-riser-fatigue.md`), and zero scope overlap with `viv-riser-fatigue.md` / `free-span-viv-fatigue.md` / `pipeline-integrity-assessment.md` / `mooring-line-failure-physics.md` — with `index.md` updated to surface every new page in its Concepts catalogue table.

---

## Pseudocode

```
# Per-page authoring contract (applies to all 8 new pages):
function author_concept_page(slug, scope_summary):
    write frontmatter (per knowledge/wikis/engineering/CLAUDE.md):
        title: human-readable
        tags: [riser, <topology-tag>, <standards-tag>]
        added: 2026-05-02
        last_updated: 2026-05-02
        sources: [<existing source page if any, else omit>]
    section "Scope" — 1 paragraph stating what the page IS and what it is NOT
        (boundary discipline: SCR page must NOT re-cover VIV fatigue mechanics —
         that lives on viv-riser-fatigue.md; TTR/SCR/flexible pages must NOT
         re-cover free-span pipeline VIV — that lives on free-span-viv-fatigue.md)
    section "Key Concepts" — 5–10 bulleted definitions, each ≤1 line
    section "Standards / References" — ≥1 bullet NAMING API RP 17B/17J/16Q/2RD,
        DNV-OS-F201, DNV-RP-F202, DNV-RP-F204, ISO 13628-2/-7, ISO 13624,
        or ISO 19901-7,
        with stable URL — but MUST NOT enumerate specific thresholds, formulas,
        or code clauses (those belong on wiki/standards/<code-id>.md per the
        engineering wiki's local CLAUDE.md directory schema; #2471 is CSA-Z276-specific
        per memory project_wiki_standards_path_decision.md and does NOT generalize)
    canonical forward-reference marker for not-yet-codified standards:
        for any standards body that does NOT yet have a wiki/standards/<code-id>.md
        page on disk (verified via Path.exists() at write-time), the citation MUST
        be paired with an HTML comment in the canonical form
        `<!-- TODO(W3-B): replace external URL with [[../standards/<code-id>]] when standards page lands -->`
        immediately after the citation line. For already-codified standards
        (e.g., DNV-RP-C203, DNV-RP-F105 — present on disk today), use a
        relative wikilink `[[../standards/<code-id>]]` instead and emit no marker.
    section "Cross-References" — wiki-style [[link]] entries to ≥2 existing
        engineering-wiki pages (must include viv-riser-fatigue.md from at least
        one of the 8 new pages to cross-stitch the cluster)
    forbid: extracted text from PDFs (#2482 deny-list)
    forbid: any reference that broadens scope into pipelines, mooring lines,
        or umbilicals (per prompt scope discipline)
    enforce: word count ≤ 400 per page (concept summary, not chapter copy)

function update_index(index_path, new_pages):
    insert each new concept page into "Concepts" table (alphabetical by title)
    re-derive page_count at execution time:
        new_page_count = current page_count (read from frontmatter at execution) + 8
        # parallel-plan tolerant: if #2559 (or other plan) bumped page_count first,
        # this still yields the correct value
    re-derive concepts-table heading at execution time:
        new_heading_count = current concepts-table row count + 8
        rewrite "## Concepts (<old> pages)" → "## Concepts (<new> pages)"
    leave entities/sources/standards/workflows untouched (no new entries from this plan)

function append_log(log_path):
    append "[2026-05-02] expand | engineering W3-D — 8 riser sub-domain concept pages"
        - Pages added: <list>
        - Notes: covers SCR, TTR, flexible, hybrid, drilling, configs, load-case
                 taxonomy, riser-soil interaction; defers J-tube, composite,
                 workover/completion, monitoring, installation to follow-up batch.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/concepts/riser-configurations.md` | Topology taxonomy: free-hanging, lazy-wave, steep-wave, lazy-S, steep-S, pliant-wave, tethered, Chinese lantern; references API RP 17B configurations |
| Create | `knowledge/wikis/engineering/wiki/concepts/steel-catenary-riser-design.md` | SCR global design: departure angle envelope, touchdown point migration, soil-trench effect, hang-off interface; **scoped to design-state, not VIV (boundary against viv-riser-fatigue.md)** |
| Create | `knowledge/wikis/engineering/wiki/concepts/top-tensioned-riser-design.md` | TTR global design: tensioner stroke, taper/stress/keel joint, top-tension envelope, single vs dual casing |
| Create | `knowledge/wikis/engineering/wiki/concepts/flexible-riser-design.md` | Unbonded-flexible architecture: layer functions (carcass, pressure-armour, tensile-armours, polymer sheaths), end-fittings, bend-stiffener, ancillaries, annulus integrity, mid-water arch; references API RP 17B/17J + ISO 13628-2 |
| Create | `knowledge/wikis/engineering/wiki/concepts/hybrid-riser-tower.md` | Hybrid riser tower / SLOR / bundled tower: rigid-vertical-+-flexible-jumper architecture, tower foundation, top-tension provision, bundle thermal management; references 2H BLK31 SLOR corpus |
| Create | `knowledge/wikis/engineering/wiki/concepts/drilling-riser-system.md` | Drilling-riser system: slip/telescopic joint, LMRP/BOP, air-gap, weak-point disconnect, recoil; references API RP 16Q + digitalmodel `drilling_riser/operability.py`, `damping.py` |
| Create | `knowledge/wikis/engineering/wiki/concepts/riser-global-analysis-load-cases.md` | Load-case taxonomy: extreme/strength (ULS), accidental (ALS), fatigue (FLS — wave + VIV + slugging + 1st/2nd-order), serviceability (SLS), installation; references DNV-OS-F201 + API RP 2RD |
| Create | `knowledge/wikis/engineering/wiki/concepts/riser-soil-interaction.md` | Touchdown trench, soil stiffness models (linear, non-linear, Aubeny-Biscontin), trench-formation timescale, P-y-equivalent vertical for SCR; cross-links to viv-riser-fatigue.md TDP and pile-capacity-alpha-method.md soil framing |
| Modify | `knowledge/wikis/engineering/wiki/concepts/viv-riser-fatigue.md` | Add ≤3-line "Related design pages" pointer block to the new SCR / TTR / configurations / load-cases pages so reverse traversal works (per W1-D review M2 pattern). **Maintenance:** the existing page contains 2 `pipeline\|flowline` mentions (verified 2026-05-02 via `grep -ic "pipeline\|flowline"`); reviewers of the new pages should evaluate whether those existing mentions are material to VIV-fatigue scope; if not, remove them in the same PR for boundary consistency with the section-dominance test. |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | Add 8 new concept rows alphabetically into Concepts table; **re-derive at execution time** the Concepts heading row-count and the frontmatter `page_count` (current+8) — do not hard-code `(40 pages)` / `90` because parallel plans (e.g., #2559 OCIMF) may shift the baseline before this plan executes |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | Append `[2026-05-02] expand | engineering W3-D — 8 riser sub-domain concept pages` entry |
| Create | `tests/knowledge/test_engineering_riser_expansion.py` | TDD frontmatter / cross-link / standards-citation / index-resolves / scope-discipline / past-tense-drift checks |
| Update | `docs/plans/README.md` | Add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_eight_pages_exist` | Each of the 8 new files is on disk | path list | all 8 `Path.exists()` is True |
| `test_frontmatter_required_fields` | Every new page has `title`, `tags`, `added`, `last_updated` per `knowledge/wikis/engineering/CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_frontmatter_tag_riser` | Every new page tags includes `riser` (cluster discoverability) | parse YAML | `'riser' in tags` |
| `test_at_least_one_standards_reference` | Page body cites ≥1 of API RP 17B / 17J / 16Q / 2RD, DNV-OS-F201 / RP-F202 / RP-F204, ISO 13628-2 / 13628-7 / 19901-7 (NAME ONLY — no thresholds per W1-D-revised pattern) | regex search of body text | match found per page |
| `test_at_least_two_cross_links` | Each page contains ≥2 `[[wikilink]]`-style or relative-markdown cross-references to engineering-wiki pages that exist on disk | parse markdown links + wikilinks | ≥2 resolvable refs per page |
| `test_at_least_one_cross_link_to_existing_riser_page` | At least one of the 8 new pages links back to `viv-riser-fatigue.md` (cluster cross-stitch) | grep across 8 new pages | ≥1 page has the link |
| `test_no_scope_creep_into_pipeline_mooring_umbilical` | New page bodies do not own pipeline/mooring/umbilical scope. **Section-dominance check:** tokenise the page into top-level (H2) sections; for each section, count `pipeline\|mooring\|umbilical` keyword hits vs. `riser\|SCR\|TTR\|flexible riser\|hybrid tower\|drilling riser` keyword hits. Fail if any section's non-riser keyword count exceeds the riser keyword count. **Whitelist:** sections titled `## Scope` or `## Out of Scope` are exempt (boundary callouts are encouraged). The legacy per-page total-count cap is **dropped** because legitimate adjacency (riser-pipeline tie-in via PLET/PLEM, riser-mooring shared-pollution, SLOR-bundled umbilical) requires honest mention. | tokenise H2 sections; per-section keyword ratio | every non-whitelisted section has riser-keyword count ≥ non-riser-keyword count |
| `test_riser_topic_dominance_positive` | Each new page contains ≥3 occurrences of `riser` OR a riser-typology subterm (`SCR`, `TTR`, `flexible riser`, `hybrid tower`, `drilling riser`) in body text — proves riser is the dominant topic and complements the section-dominance test by guarding against synonym-attack false negatives (e.g., re-covering `mooring` under "tendon fatigue" or `pipeline VIV` under "spanned-section VIV"). | regex count per page | ≥3 hits per page |
| `test_word_count_under_400` | Concept-summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (e.g. "Page N of M" stamps, very long single paragraphs > 80 words) | heuristic | no flagged paragraphs |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts table resolves on disk | walk markdown links | 100% resolve |
| `test_index_page_count_bumped` | `index.md` frontmatter `page_count` updated to **≥90** (floor, not equality, to absorb any parallel-plan arithmetic shift — e.g., #2559 OCIMF tandem promotion landing in flight); Concepts table heading is `## Concepts (N pages)` where N matches the actual concepts-table row count after insertion (re-derived at execution time). | parse YAML + count rows | `page_count ≥ 90`; heading number == row count |
| `test_log_entry_appended` | `log.md` contains a 2026-05-02 expand entry naming W3-D | grep | match present |
| `test_no_past_tense_artifact_drift` | No new page contains future-work claimed-as-done phrasing. Heuristic: scan for "we added", "we created", "this page was", "completed", "delivered" outside of the explicit "## Cross-References" / link-text region | regex | zero matches |
| `test_viv_page_pointer_block_added` | `concepts/viv-riser-fatigue.md` gains a "Related design pages" pointer block listing ≥4 of the 8 new pages | grep | match present, ≥4 links |
| `test_no_redundant_viv_content_in_new_pages` | New pages MUST NOT re-introduce S-N curve tables, DFF tables, wake-interference S/D tables, or rainflow-counting prose — those live only on `viv-riser-fatigue.md` / `sn-curve-fatigue-definitions.md`. Keyword list extended to cover synonym-attack: `Strouhal`, `lock-in`, `mode-shape participation`, `Iwan-Blevins`. Also caps occurrences of the noun `fatigue` to ≤5 per page (canonical fatigue page is `viv-riser-fatigue.md`; design-state pages should reference fatigue in passing only). | regex match for known phrases + fatigue-noun cap | zero matches per new page; `fatigue` ≤5 |
| `test_forward_reference_markers_present` | For every external standards-body URL appearing in a new page where the corresponding `wiki/standards/<code-id>.md` page does NOT exist on disk, the citation line MUST be paired with the canonical HTML comment `<!-- TODO(W3-B): replace external URL with [[../standards/<code-id>]] when standards page lands -->`. Conversely, if the standards page DOES exist on disk, the new page MUST use the relative wikilink `[[../standards/<code-id>]]` and NOT the external URL. Test enumerates all `https://` URLs whose hostname is `api.org`, `dnv.com`, or `iso.org` and asserts the marker / wikilink invariant. | regex enumerate URLs + Path.exists() + marker check | every URL satisfies the invariant |
| `test_forward_reference_marker_count_emit` | Test emits a count and file-list of pending `TODO(W3-B):` markers across the 8 new pages so a future plan reviewing W3-B's promotion can run the test, get the deletion checklist, and discharge the markers deterministically. (Test does not fail on count > 0; it asserts count is recorded in test output for downstream tooling.) | grep across 8 new pages | count + file list emitted |

---

## Acceptance Criteria

- [ ] All 8 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-02`, `last_updated=2026-05-02`, `tags` includes `riser`).
- [ ] Each new page will NAME ≥1 standards body (API / DNV / ISO) with stable URL or sibling source-page link, but MUST NOT enumerate specific thresholds, formulas, or code clauses (per #2471 routing).
- [ ] Each new page will list ≥2 cross-references to other engineering-wiki pages.
- [ ] At least one of the 8 new pages will cross-link to `concepts/viv-riser-fatigue.md` (cluster stitch).
- [ ] `concepts/viv-riser-fatigue.md` will be updated to add a "Related design pages" pointer block listing ≥4 of the new pages.
- [ ] No new page will overlap with `viv-riser-fatigue.md` VIV-fatigue mechanics scope (no S-N tables, no DFF tables, no wake-interference S/D tables, no rainflow prose).
- [ ] No new page will broaden scope into pipelines, mooring, or umbilicals (enforced via section-dominance keyword-ratio test + positive riser-topic-dominance test; legitimate adjacency is preserved by H2 `## Scope` / `## Out of Scope` whitelisting, not by a per-page word cap).
- [ ] `index.md` Concepts table will list 8 new rows (alphabetical); table heading will read `## Concepts (N pages)` where N == actual row count after insertion (re-derived at execution time, not hard-coded, to absorb parallel-plan arithmetic shift).
- [ ] `index.md` frontmatter `page_count` will read **≥90** (floor; equality holds only if no parallel plan bumped the count first).
- [ ] `log.md` will carry a `[2026-05-02] expand | engineering W3-D` entry.
- [ ] `tests/knowledge/test_engineering_riser_expansion.py` will pass: `uv run pytest tests/knowledge/test_engineering_riser_expansion.py -v`.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Each new page will be ≤400 words (concept-summary discipline per #2482 deny-list).
- [ ] No calc-module is expected to cite these new concept pages as standards-resolution targets until W3-B (or an equivalent follow-up) lands codified `wiki/standards/dnv-os-f201.md`, `wiki/standards/iso-19901-7.md`, `wiki/standards/iso-13624.md`, etc.; per `.claude/rules/calc-citation-contract.md`, calc-side citations continue to require direct standards-page resolution and these concept pages do NOT serve as transitive resolution targets.
- [ ] Every external standards-body URL on a new page is paired with either (a) the canonical HTML comment `<!-- TODO(W3-B): replace external URL with [[../standards/<code-id>]] when standards page lands -->` for not-yet-codified standards, or (b) a relative `[[../standards/<code-id>]]` wikilink for already-codified standards (DNV-RP-C203, DNV-RP-F105, etc.).
- [ ] Review artifacts will be posted under `scripts/review/results/2026-05-02-plan-W3D-engineering-riser-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 2 MAJOR + 5 MINOR — all addressed inline |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (2 MAJOR + 5 MINOR fixes applied 2026-05-02)

**Revisions made based on review:**
- (P1-1) Replaced per-page count cap on `pipeline\|mooring\|umbilical` with section-dominance keyword-ratio test (riser vs. non-riser keyword count per H2 section, with `## Scope` / `## Out of Scope` whitelisted) plus paired positive `test_riser_topic_dominance_positive` (≥3 riser-typology hits per page).
- (P1-2) Defined canonical forward-reference HTML-comment marker `<!-- TODO(W3-B): replace external URL with [[../standards/<code-id>]] when standards page lands -->`; added TDD tests `test_forward_reference_markers_present` and `test_forward_reference_marker_count_emit`; added explicit calc-citation deferral acceptance bullet stating these concept pages are NOT transitive resolution targets.
- (P2-1) Added maintenance note in Files-to-Change for `viv-riser-fatigue.md` flagging the existing 2 `pipeline\|flowline` mentions for reviewer evaluation in the same PR.
- (P2-2) Switched present-tense Resource Intelligence verbs to future tense ("This plan will create", "Plan will NOT extract", "Adding these concept pages will not by itself create a cross-ref") for tense-discipline consistency.
- (P2-3) Extended `test_no_redundant_viv_content_in_new_pages` keyword list with `Strouhal`, `lock-in`, `mode-shape participation`, `Iwan-Blevins`; added per-page cap of ≤5 `fatigue` occurrences.
- (P2-4) Corrected ISO standards table: added ISO 13624-1 (correct part for marine drilling riser) and re-scoped ISO 19901-7 row to stationkeeping-only with explicit correction-of-prompt-framing note.
- (P2-5) Replaced literal `82 → 90` and `(32 pages) → (40 pages)` arithmetic with re-derive-at-execution-time pattern in Pseudocode, Files-to-Change, Acceptance Criteria, and `test_index_page_count_bumped`; added Risk-section paragraph on parallel-plan arithmetic interaction (e.g., #2559 OCIMF tandem promotion).

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk: terminology drift.** "SCR" can mean "Steel Catenary Riser" (offshore) or "Silicon Controlled Rectifier" (electrical). Pages will spell out "Steel Catenary Riser (SCR)" on first occurrence per page. Similar disambiguation for TTR (Top-Tensioned Riser, not Total-Tank-Recirculation) and SLOR (Single-Line Offset Riser).
- **Risk: cross-link explosion.** With 8 new pages plus the existing `viv-riser-fatigue.md`, a fully-meshed cross-link graph would imply 8×8=64 directed links. The Pseudocode caps each page at ≥2 cross-links and the boundary-page pattern (`riser-configurations.md` is the hub) keeps the typical link-count to 3–5 per page. Tests do not enforce an upper bound but reviewers should flag any page with >8 cross-links as over-linked.
- **Risk: false-gap from terminology mismatch.** `viv-riser-fatigue.md` already discusses touchdown point and soil interaction in passing. The new `riser-soil-interaction.md` and `steel-catenary-riser-design.md` will explicitly cite the existing page in Scope and state the boundary (existing page = VIV-fatigue mechanics; new pages = design-state physics + soil model selection). The TDD test `test_no_redundant_viv_content_in_new_pages` enforces this.
- **Risk: scope creep into pipeline / mooring / umbilical.** Risers share VIV physics with pipelines, share fatigue physics with mooring, and share installation transitions with umbilicals. The TDD test `test_no_scope_creep_into_pipeline_mooring_umbilical` uses a **section-dominance keyword-ratio check** (riser-keyword count ≥ non-riser-keyword count per H2 section, with `## Scope` / `## Out of Scope` whitelisted), and a paired positive-presence test `test_riser_topic_dominance_positive` (≥3 riser-typology hits per page) blocks synonym-attack false negatives. The earlier per-page absolute cap was rejected because legitimate adjacency (riser-pipeline tie-in via PLET/PLEM, SLOR-attached umbilical, riser-mooring interface) cannot be described honestly under a count threshold.
- **Risk: no formal seed YAML for engineering wiki.** Unlike `naval-architecture-resources.yaml`, the engineering wiki has no seed file driving `index.md` regeneration. This plan therefore edits `index.md` directly (additive insert into Concepts table, in alphabetical position). If a seed-based regenerator lands later, the seed file should pick up these 8 entries from disk by directory walk; until then, the manual edit is the single source of truth. Reviewers should flag any future plan that introduces a seed file as needing migration of these 8 entries.
- **Risk: digitalmodel cross-ref deferred.** Adding these concept pages does NOT create calc-side `Citation` instances. Calc-side adoption (e.g., `digitalmodel/drilling_riser/operability.py` adding a citation to the new `drilling-riser-system.md`) is a separate follow-up issue under `.claude/rules/calc-citation-contract.md`. This plan's Acceptance Criteria do not require any calc-module change.
- **Risk: parallel work collision with #2588 W1-C audit.** If the audit's prioritized child-issue list orders the riser bucket differently or sub-divides it, this plan may need re-sequencing. Mitigation: this plan is **independent** of W1-C; if W1-C closes with a competing prioritization, the user can pause this plan at `status:plan-review` and re-draft. No work is wasted because the 8 concept pages are foundational regardless of order.
- **Risk: forward-reference debt for not-yet-codified standards (DNV-OS-F201, ISO 19901-7, ISO 13624, API RP 17B/17J/16Q/2RD, DNV-RP-F202, DNV-RP-F204, ISO 13628-2/-7).** None of these standards have a `wiki/standards/<code-id>.md` on disk at the time of writing. New pages will cite each by title and URL only, paired with the **canonical HTML comment marker** `<!-- TODO(W3-B): replace external URL with [[../standards/<code-id>]] when standards page lands -->` defined in Pseudocode. The TDD tests `test_forward_reference_markers_present` and `test_forward_reference_marker_count_emit` enforce the marker invariant and emit a deletion checklist, so a future plan reviewing W3-B promotion (or any equivalent codification follow-up) can run the test to discharge markers deterministically. The marker is intentionally distinct from arbitrary forward-reference prose so that grep-based cleanup is unambiguous. **W3-B may never land**; if it doesn't, the markers persist as well-typed debt rather than dangling prose, and a different follow-up plan can codify each standard independently. Calc-side citation to these new concept pages is explicitly NOT a supported pattern (see Acceptance Criteria) — calc modules continue to cite via direct `wiki/standards/<code-id>.md` resolution per `calc-citation-contract.md`.
- **Risk: 9th and 10th canonical topics deferred.** `concepts/riser-installation-methods.md` (reel-lay, J-lay top-down, S-lay-with-stinger, A&R) and `concepts/composite-riser-design.md` (DNV-RP-F202) are deferred to a follow-up batch to keep this plan at exactly 8 pages.

- **Risk: parallel-plan arithmetic interaction with #2559 OCIMF tandem mooring promotion (and any other in-flight engineering-wiki plan).** This plan literally states `page_count: 82 → 90` and `## Concepts (32 pages) → (40 pages)`. If #2559 (or another concurrent plan) lands between this plan's approval and execution, it will modify `index.md` (e.g., promoting `ocimf-tandem-mooring.md` into the standards table moves a different counter, but any addition to any catalog table changes `page_count`). At execution time, the implementer will **re-derive both numbers from the on-disk state** — read current `page_count`, add 8, and re-count concepts-table rows after insertion — rather than committing the literal `90` / `40 pages` figures. The TDD test `test_index_page_count_bumped` already uses a `≥90` floor (not equality), but the Concepts heading literal `(40 pages)` should also be re-derived; reviewers should not block PR review on the exact heading number if a parallel plan landed first.

- **Open: should `concepts/riser-installation-methods.md` ship in this batch (making it 9 pages) or in a follow-up?** Current plan defers to follow-up. Reviewer may flip the decision.
- **Open: should this plan also touch `concepts/cathodic-protection-design.md` to add a riser-CP mention?** Risers carry CP systems, but the existing CP page is generic enough that no edit is strictly required. Current plan leaves it untouched. Reviewer may flag if CP-on-riser is sufficiently specialized to warrant a callout.

---

## Complexity: T2

**T2** — 8 new wiki pages + 1 modified existing page (viv-riser-fatigue.md pointer block) + 2 modified registry files (index.md, log.md) + 1 new test module. Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in cross-link discipline, scope-boundary against `viv-riser-fatigue.md`, and pipeline/mooring/umbilical scope-creep — all addressable with regex tests. Not T3 because there is no new module / no calc / no migration / no schema change.
