# Plan for W4-D: feat(llm-wiki): engineering wiki pipeline sub-domain topical expansion — 8–10 core concept pages

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** to-be-filed (sibling to #2597 W3-D engineering riser expansion under the #2540 Elements wave; will follow the same shape and the #2596 W3-C path-sanction erratum discipline)
> **Review artifacts:** `scripts/review/results/2026-05-03-plan-W4D-engineering-pipeline-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

Wiki target tree: `knowledge/wikis/engineering/wiki/` — 105 markdown files on disk; `index.md` frontmatter `page_count` reads **83** (verified 2026-05-03 via `grep page_count knowledge/wikis/engineering/wiki/index.md`); concepts table heading reads `## Concepts (32 pages)`. Directory schema mandated by `knowledge/wikis/engineering/CLAUDE.md` (concepts/, entities/, sources/, standards/, workflows/).

- Found: 1 existing **pipeline-scope concept page** on disk —
  - `concepts/pipeline-integrity-assessment.md` — corroded pipeline FFS / DNV-RP-F101 / API-579 scope; 86 lines; tags `[pipeline, integrity, dnv-rp-f101, api-579, corrosion, fitness-for-service]`.
- Found: 1 existing pipeline-adjacent **workflow page** —
  - `workflows/orcawave-to-orcaflex-pipeline.md` — this is a **data-handoff "pipeline"** (OrcaWave → OrcaFlex automation), not subsea pipeline engineering; tags include `[orcawave, orcaflex, pipeline, automation, rao]`. The shared word "pipeline" is a homonym; this plan WILL NOT touch the workflow page and the new concept pages WILL be tagged with substantive engineering tags (`subsea`, `pipelay`, `buckling`, `stability`, `coating`, etc.) so a tag-based filter cleanly separates the two clusters.
- Found: 1 pipeline-adjacent concept page that the prompt boundary explicitly carves out —
  - `concepts/free-span-viv-fatigue.md` — pipeline free-span scope per DNV-RP-F105; this page IS pipeline-scope but covers ONE specific design topic (VIV-driven free-span fatigue). The new pages MUST NOT re-cover free-span VIV mechanics.
- Found: 2 codified pipeline standards pages —
  - `standards/dnv-rp-f101.md` — corroded pipelines (FFS).
  - `standards/dnv-rp-f105.md` — free-spanning pipelines.
  - **Not yet codified** as `wiki/standards/<code-id>.md`: DNV-ST-F101 (umbrella submarine pipeline systems), DNV-RP-F109 (on-bottom stability), DNV-RP-F110 (global buckling), DNV-RP-F111 (interference between trawl gear and pipelines), DNV-RP-F114 (pipe-soil interaction), DNV-RP-F116 (integrity management), API RP 1111 (offshore hydrocarbon pipelines design), API RP 1102 (HDD onshore pipeline crossing), ASME B31.4 / B31.8 (onshore liquid / gas), ISO 13623 (pipeline transportation systems).
- Found: digitalmodel **pipeline calc-side module footprint** (verified 2026-05-03 via `find digitalmodel/src/digitalmodel -path '*pipeline*' -name '*.py'`) —
  - `digitalmodel/src/digitalmodel/subsea/pipeline/` package: `pipeline.py`, `pipe_sizing.py`, `pipeline_pressure.py`, `pipeline_pressure_dnv.py`, `pipeline_pressure_workflow.py`, `pressure_loss.py`, `api_rp_1111_installation.py`, `lateral_buckling.py`, `thermal_buckling.py`, `upheaval_buckling.py`, `buckling_common.py`, `calculations/{pipe_properties,stress_calculations}.py`.
  - `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/` sub-package: `_bilinear_sn.py`, `models.py`, `span_allowable_length.py`, `span_fatigue_damage.py`, `span_natural_frequency.py`, `span_onset_screening.py`, `span_viv_response.py`, `wave_velocity.py`, `weibull_current.py`.
  - `digitalmodel/src/digitalmodel/asset_integrity/pipeline_skill.py`.
  - `digitalmodel/src/digitalmodel/cathodic_protection/pipeline_cp.py`.
  - `digitalmodel/src/digitalmodel/solvers/orcaflex/pipeline_schematic.py`.
  - `digitalmodel/src/digitalmodel/web/digitaltwinfeed/{OffshorePipeline,OnshorePipeline}/`.
  - These are all calc-side modules with **zero current cross-references back into `knowledge/wikis/engineering/wiki/concepts/`** (pattern verified for the parallel riser plan #2597; same pattern will hold here). Adding these concept pages will not by itself create calc-side citations — that remains follow-up work under `.claude/rules/calc-citation-contract.md`.
- Gap: every canonical pipeline-engineering design topic OUTSIDE corroded-FFS and free-span-VIV is uncovered — pipelay/installation methods, on-bottom stability, lateral (snake-lay) buckling, upheaval buckling, pipe-soil interaction, pipeline walking, end-expansion / spool / tee / sleeper design, route selection, trawl-impact protection, coatings / cathodic protection scope, HDD onshore crossings. Despite a substantial digitalmodel calc footprint (`lateral_buckling.py`, `thermal_buckling.py`, `upheaval_buckling.py`, `api_rp_1111_installation.py`), there is no concept-side anchor.

### Standards

This plan will create **concept pages**, not standards pages. Per `.claude/rules/calc-citation-contract.md`, only calc modules emit `Citation` instances; concept pages NAME standards bodies and titles by reference but do not enumerate clauses, thresholds, or formulas. Standards-page promotion will follow the engineering wiki's own `CLAUDE.md`-sanctioned schema (`wiki/standards/<code-id>.md`); per memory `project_wiki_standards_path_decision.md` and the W3-C erratum (#2596), the engineering wiki IS in routing-principle scope but **#2471 is CSA-Z276-only** and is NOT cited as a generalised path-sanction. The allowlist test at `tests/governance/test_2471_citation_scope.py` will catch any over-citation.

| Standard | Status | Source |
|---|---|---|
| DNV-ST-F101 (Submarine Pipeline Systems — umbrella) | referenced (no codified standards page yet) | https://www.dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems/ |
| DNV-RP-F101 (Corroded Pipelines) | codified — `wiki/standards/dnv-rp-f101.md` | (existing) |
| DNV-RP-F105 (Free Spanning Pipelines) | codified — `wiki/standards/dnv-rp-f105.md` | (existing) |
| DNV-RP-F109 (On-Bottom Stability Design) | referenced (no codified standards page yet) | https://www.dnv.com/ |
| DNV-RP-F110 (Global Buckling — pipelines) | referenced (no codified standards page yet) | https://www.dnv.com/ |
| DNV-RP-F111 (Interference between Trawl Gear and Pipelines) | referenced (no codified standards page yet) | https://www.dnv.com/ |
| DNV-RP-F114 (Pipe-Soil Interaction for Submarine Pipelines) | referenced (no codified standards page yet) | https://www.dnv.com/ |
| DNV-RP-F116 (Integrity Management of Submarine Pipeline Systems) | referenced — partially scoped on `pipeline-integrity-assessment.md` already | https://www.dnv.com/ |
| API RP 1111 (Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines — Limit-State Design) | referenced (no codified standards page; calc module `api_rp_1111_installation.py` exists) | https://www.api.org/products-and-services/standards |
| API RP 1102 (Steel Pipelines Crossing Railroads and Highways) | referenced (HDD context) | https://www.api.org/ |
| ASME B31.4 (Pipeline Transportation Systems for Liquids and Slurries) | referenced (onshore-pipeline boundary) | https://www.asme.org/codes-standards |
| ASME B31.8 (Gas Transmission and Distribution Piping Systems) | referenced (onshore-pipeline boundary) | https://www.asme.org/codes-standards |
| ISO 13623 (Petroleum and natural gas industries — Pipeline transportation systems) | referenced | https://www.iso.org/standard/65386.html |

**Path-sanction provenance** (per #2596 W3-C erratum discipline): the path `wiki/standards/<code-id>.md` is sanctioned by the engineering wiki's own `CLAUDE.md` directory schema (`Pages: wiki/{concepts,entities,sources,standards,workflows}/`) and by the existence of 8 already-codified standards pages following that pattern. **#2471 is NOT cited** as path-sanction in this plan; #2471 is CSA-Z276-specific per memory `project_wiki_standards_path_decision.md`.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/index.md` (verified 2026-05-03) — `page_count: 83`, concepts table heading `## Concepts (32 pages)`. Last regenerated 2026-04-29.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (`title`, `tags`, `added`, `last_updated` mandatory; `sources`, `domain`, `cross_links` recommended; standards pages additionally use `code_id`, `publisher`, `revision`).
- `knowledge/wikis/engineering/wiki/concepts/pipeline-integrity-assessment.md` (lines 1–10) — confirms current pipeline-page style: H1 title, frontmatter with `[pipeline, integrity, ...]` tags, `sources: career-learnings-seed`. Already cites DNV-RP-F101 + API-579 — **boundary: new pages MUST NOT re-cover corroded FFS / wall-loss assessment scope**.
- `knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md` (lines 1–15) — pipeline-scope VIV-fatigue ONLY; **boundary: new pages MUST NOT re-cover free-span VIV mechanics** (S-N + Strouhal + Iwan-Blevins). New `pipeline-on-bottom-stability.md` will cite this page when describing how a too-long span ⇒ free-span design check.
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-f101.md`, `dnv-rp-f105.md` — frontmatter style for standards pages confirmed; both predate the `code_id`/`publisher`/`revision` triple convention.
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` (line 1–10) — homonym only; data-pipeline, not subsea pipeline. New pages WILL NOT cross-link to it.

### Documents consulted

- `docs/plans/_template-issue-plan.md` — followed verbatim; retrieval contract requires ≥3 distinct sources with embedded evidence.
- `docs/plans/2026-05-02-issue-2597-llm-wiki-W3D-engineering-riser-expansion.md` — same-shape sibling (riser sub-domain) with the post-W3-C path-sanction erratum applied. This plan reuses the section-dominance keyword-ratio test pattern, the ≤400-word per-page cap, the standards-NAME-only rule, the forward-reference HTML-comment marker for not-yet-codified standards (re-tagged here as `TODO(W4-codify)`), and the re-derive-at-execution-time index-bump arithmetic.
- `.claude/rules/calc-citation-contract.md` — concept pages do NOT emit `Citation` instances; standards-page promotion deferred.
- `.claude/rules/coding-style.md` — adhered to (no absolute paths in scripts; future tense; targeted edits).
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — engineering wiki IS in routing-principle scope; `wiki/standards/<code-id>.md` reserved for codified standards; concept pages stay in `wiki/concepts/`. **#2471 is CSA-Z276-only and is NOT a generalized path-sanction.**
- Memory `project_doc_intel_operating_model.md` — engineering wiki is the document-intelligence surface for the digitalmodel calc layer; gap-closure feeds calc-citation provenance.
- #2540 — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- #2588 — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)" — sibling audit; this plan is a forward-pull of one of the gap-buckets W1-C will identify (pipeline sub-domain). The plan's child-issue scope is **independent** of W1-C; if W1-C surfaces a competing prioritization, this plan can be re-sequenced without revision.
- #2596 — OPEN — "erratum(plans): correct #2471 sanction-scope over-citation in W1-A and W1-B (W3-C)" — provides the path-sanction provenance discipline this plan adheres to.
- #2597 — OPEN — "feat(llm-wiki): engineering wiki riser sub-domain topical expansion (W3-D)" — same-shape sibling.
- #2589 — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — distant sibling; provides the standards-NAME-without-thresholds pattern.
- /mnt/ace inventory: `digitalmodel/docs/pipelines/literature/{academic, regulatory-bsee, textbooks, buckling, pressure_loss}` (verified 2026-05-03), including `2007-2-Yablonskikh_buckle_assessment.pdf`, `349567530-Appendix-2-Onshore-Pipeline-Design-Basis.pdf`, `ASME L&D B31.8 Natural Gas Pipelines Guide.pdf`, `co2_pipeline_design_review.pdf`, `hydrogen_pipeline.pdf`, `pipelay_solitaire_stinger_force_analysis.pdf`, `Pipeline_Route_Determination_GN_e-Aug16.pdf`, `precommission.pdf`, `buckling/31_2010_Dr_Thusyanthan_Uplift_resistance_of_buried_pipelines_and_DNV_guidelines_OPT2010.pdf`. Plus `/mnt/ace/saipem/` (Saipem is offshore-pipeline EPCI; subdirs `general/{cp, engg, flexible, reports, slwr, spoolbase, yt_docs}`, `yellowtail/`), `/mnt/ace/docs/0181 KBR Pipeline`, `/mnt/ace/docs/611 Mecor Pipeline Installation Analysis`, `/mnt/ace/docs/0098 Mecor Pipeline Installation Analysis`, `/mnt/ace/0_mrv/9427_2pipeline_engg`, `/mnt/ace/client_projects/energy_pipeline_installation_mp`, `/mnt/ace/docs/0175 TJG Pipelay Analysis`, `/mnt/ace/doris/training/draft presentations/On-Bottom Stability`. Plan will NOT extract from these PDFs (per #2482 deny-list); concept pages will cite them by reference at most, with NO copy-paste of text.
- WebSearch — "Bai Subsea Pipelines and Risers chapter list" → confirms canonical pipeline curriculum: Part I Mechanical Design (wall-thickness, hydrostatic collapse), Part II Pipeline Design (route selection, on-bottom stability, lateral & upheaval buckling, free-span, span fatigue, trawl-pull-over, dropped object), Part III Installation (S-lay, J-lay, reel-lay, tow-out, HDD), separate flow-assurance section (wax, asphaltenes), integrity-management section. Bai/Bai book is the canonical English-language pipeline reference.
- WebSearch — "DNV-OS-F101 / DNV-ST-F101 submarine pipeline systems": confirmed current edition is **DNV-ST-F101** (rebranded from DNV-OS-F101; Aug 2021 edition + Dec 2021 amendment), umbrella standard for design / materials / fabrication / installation / testing / commissioning / operation / re-qualification / abandonment of rigid metallic submarine pipelines. **Plan will use DNV-ST-F101 (current name) but allow citations to DNV-OS-F101 only as legacy.**

### Gaps identified

Coverage matrix vs. canonical offshore-pipeline-engineering curriculum (Bai & Bai *Subsea Pipelines and Risers* chapter list + DNV-ST-F101 + DNV-RP-F109/F110/F111/F114/F116 + API RP 1111 + 2H/Saipem/digitalmodel corpora):

| Canonical topic | Current wiki status | Action |
|---|---|---|
| Pipeline route selection (geohazard avoidance, crossings, corridor) | gap | **NEW** `concepts/pipeline-route-selection.md` |
| On-bottom stability (DNV-RP-F109; absolute / generalised lateral stability; concrete weight coating) | gap | **NEW** `concepts/pipeline-on-bottom-stability.md` |
| Lateral buckling (snake-lay, sleepers, residual lay-tension; DNV-RP-F110) | gap (calc `lateral_buckling.py` exists) | **NEW** `concepts/pipeline-lateral-buckling.md` |
| Upheaval buckling (download / cover / imperfection; DNV-RP-F110 + Hobbs/Palmer) | gap (calc `upheaval_buckling.py` exists; Thusyanthan PDF on /mnt/ace) | **NEW** `concepts/pipeline-upheaval-buckling.md` |
| Pipeline walking (asymmetric thermal cycling, end-expansion, axial creep) | gap | **NEW** `concepts/pipeline-walking.md` |
| Pipe-soil interaction (axial / lateral resistance; berm formation; DNV-RP-F114) | gap | **NEW** `concepts/pipeline-soil-interaction.md` |
| Pipelay installation methods (S-lay, J-lay, reel-lay, tow-out — surface, mid-depth, off-bottom, bottom) | gap (Saipem corpus + Solitaire stinger PDF on /mnt/ace) | **NEW** `concepts/pipeline-installation-methods.md` |
| End-expansion, spool / mid-line tee / PLET / sleeper design | gap | **NEW** `concepts/pipeline-end-expansion-spool-design.md` |
| Trawl-gear interference / dropped-object protection (DNV-RP-F111) | gap | **NEW** `concepts/pipeline-trawl-impact-protection.md` |
| Pipeline coatings (anti-corrosion FBE/3LPE/3LPP, thermal-insulation wet/dry, concrete weight) | gap (Bai Ch3 covers; field-joint coating in /mnt/ace/saipem) | **NEW** `concepts/pipeline-coatings.md` |
| Pipeline cathodic protection (bracelet anodes, attenuation; companion to riser-CP) | partial — generic `cathodic-protection-design.md` | not in this batch — defer; new pages will cross-link |
| HDD onshore-pipeline crossing | gap | not in this batch — defer; flagged as Open Question on onshore-pipeline scope |
| Pipeline integrity / FFS / corrosion | covered (`pipeline-integrity-assessment.md`) | leave |
| Free-span VIV fatigue | covered (`free-span-viv-fatigue.md`) | leave (pipeline-scope but specific to free-span VIV; new on-bottom-stability page WILL cross-link) |
| Riser-pipeline interface (PLET / SCR-flowline tie-in / J-tube) | gap (riser-side covered by W3-D) | not in this batch — boundary risk; defer to a riser-pipeline-interface page in a follow-up batch |

**Top-10 selected for this expansion** (foundational + cross-linkable, citable canonical reference, raw source on /mnt/ace and/or digitalmodel module presence). **Final count: 10 pages.**

1. `concepts/pipeline-route-selection.md` — geohazard / corridor / crossing taxonomy; references Bai Ch (Pipeline Route Determination GN PDF on /mnt/ace).
2. `concepts/pipeline-on-bottom-stability.md` — DNV-RP-F109 absolute / generalised lateral stability; concrete weight coating sizing; cross-link to `free-span-viv-fatigue.md`.
3. `concepts/pipeline-lateral-buckling.md` — snake-lay / sleeper / dual-sleeper triggering; DNV-RP-F110; cross-link to `digitalmodel/subsea/pipeline/lateral_buckling.py`.
4. `concepts/pipeline-upheaval-buckling.md` — download / cover / imperfection / Palmer-Hobbs; DNV-RP-F110; cross-link to `upheaval_buckling.py` and Thusyanthan reference.
5. `concepts/pipeline-walking.md` — asymmetric thermal cycling, axial creep, end-expansion, anchor design; references Carr / Bruton walking-mechanism literature (NAME only).
6. `concepts/pipeline-soil-interaction.md` — axial / lateral resistance models, berm formation, embedment-history dependence; DNV-RP-F114.
7. `concepts/pipeline-installation-methods.md` — S-lay / J-lay / reel-lay / tow-out (surface, mid-depth, off-bottom, bottom); references API RP 1111 installation limits and Saipem-corpus context (NAME only, no extraction).
8. `concepts/pipeline-end-expansion-spool-design.md` — end-expansion, expansion spool, mid-line tee, PLET, sleeper interaction; cross-link to walking and lateral-buckling.
9. `concepts/pipeline-trawl-impact-protection.md` — DNV-RP-F111; rock-dump / mattress / trenching / burial; impact-energy bands.
10. `concepts/pipeline-coatings.md` — corrosion (FBE / 3LPE / 3LPP), thermal-insulation (wet / dry / PIP), concrete weight; field-joint coating; references API RP 5L2 / DNV-RP-F106.

(11th candidate `concepts/pipeline-hdd-crossing.md` and 12th candidate `concepts/riser-pipeline-interface.md` deferred to follow-up batches; surfaced as Open Questions below.)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view --json number,title,state`):

- `#2540` — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- `#2588` — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)".
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)".
- `#2596` — OPEN — "erratum(plans): correct #2471 sanction-scope over-citation in W1-A and W1-B (W3-C)".
- `#2597` — OPEN — "feat(llm-wiki): engineering wiki riser sub-domain topical expansion (W3-D)".

**File existence** (`find … -type f` 2026-05-03):

- EXISTS: `knowledge/wikis/engineering/wiki/index.md` (`page_count: 83`; on-disk count 105).
- EXISTS: `knowledge/wikis/engineering/CLAUDE.md` (frontmatter schema authority; explicit `Pages: wiki/{concepts,entities,sources,standards,workflows}/` directory schema).
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/pipeline-integrity-assessment.md` (86 lines; corroded FFS scope).
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md` (pipeline VIV scope).
- EXISTS: `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` (homonym — data pipeline, not subsea).
- EXISTS: `knowledge/wikis/engineering/wiki/standards/{dnv-rp-f101,dnv-rp-f105}.md`.
- EXISTS: `digitalmodel/src/digitalmodel/subsea/pipeline/{pipeline,pipe_sizing,pipeline_pressure,pipeline_pressure_dnv,pipeline_pressure_workflow,pressure_loss,api_rp_1111_installation,lateral_buckling,thermal_buckling,upheaval_buckling,buckling_common}.py`.
- EXISTS: `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/{models,span_allowable_length,span_fatigue_damage,span_natural_frequency,span_onset_screening,span_viv_response,wave_velocity,weibull_current}.py` (+ `_bilinear_sn.py`).
- EXISTS: `digitalmodel/src/digitalmodel/{asset_integrity/pipeline_skill,cathodic_protection/pipeline_cp,solvers/orcaflex/pipeline_schematic}.py`.
- EXISTS: `/mnt/ace/digitalmodel/docs/pipelines/literature/{academic, regulatory-bsee, textbooks, buckling, pressure_loss}/`.
- EXISTS: `/mnt/ace/saipem/{admin,general,yellowtail}/` and `/mnt/ace/saipem/general/{cp,engg,flexible,reports,slwr,spoolbase,yt_docs}/`.
- EXISTS: `/mnt/ace/docs/{0181 KBR Pipeline, 611 Mecor Pipeline Installation Analysis, 0098 Mecor Pipeline Installation Analysis, 0175 TJG Pipelay Analysis}/`.
- EXISTS: `tests/governance/test_2471_citation_scope.py` — allowlist test that will catch any over-citation of #2471 in this plan or its child pages.
- MISSING (this plan creates): the 10 new `concepts/pipeline-*.md` pages listed above.
- MISSING (this plan creates): `tests/knowledge/test_engineering_pipeline_expansion.py`.

**Line excerpts** (from `concepts/pipeline-integrity-assessment.md` lines 1–9 — frontmatter contract this plan must reproduce in style):

```
---
title: "Pipeline Integrity Assessment"
tags: [pipeline, integrity, dnv-rp-f101, api-579, corrosion, fitness-for-service]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---
```

**Pipeline terminology baseline in current wiki** (`grep -rohE "(SCR pipeline|J-tube pipeline|riser-pipeline|onshore pipeline|offshore pipeline|pipeline buckling|upheaval buckling|on-bottom stability|pipeline walking|free-span|trawl|impact|S-lay|J-lay|reel-lay|tow-out|HDD)" knowledge/wikis/engineering/wiki/ | sort | uniq -c`):

```
  11 free-span
   2 impact
   1 offshore pipeline
   1 on-bottom stability
   0 SCR pipeline
   0 J-tube pipeline
   0 riser-pipeline
   0 onshore pipeline
   0 pipeline buckling
   0 upheaval buckling
   0 pipeline walking
   0 trawl
   0 S-lay
   0 J-lay
   0 reel-lay
   0 tow-out
   0 HDD
```

This confirms strong gap signal: free-span has 11 hits (existing dedicated page), but every other canonical pipeline term is zero or near-zero.

**digitalmodel cross-ref baseline** (zero-cross-ref claim — `grep -rE "knowledge/wikis/engineering" digitalmodel/src/ digitalmodel/scripts/ digitalmodel/tests/ 2>&1 | wc -l`):

- Expected: 0 (matches the W3-D baseline). Adding these concept pages will not by itself create a cross-ref; calc-side adoption follows up under the citation contract.

**Gap proofs**:

- `find knowledge/wikis/engineering/wiki -iname "*pipeline*" -type f` returns ONLY `concepts/pipeline-integrity-assessment.md` and `workflows/orcawave-to-orcaflex-pipeline.md` — confirms 1 substantive pipeline concept page (the workflow is a homonym).
- `ls knowledge/wikis/engineering/wiki/comparisons/` → "(empty)".

**Out-of-scope phrase guard** (per prompt — pipeline-scope ONLY):

- "riser" → existing riser pages (`viv-riser-fatigue.md`) and the eight W3-D pages will not be touched. Riser-pipeline interface (PLET, SCR-flowline tie-in, J-tube pull-in) is **deferred** to a follow-up batch.
- "mooring" → existing mooring pages (`mooring-line-failure-physics.md`, `dnv-os-e301.md`, `ocimf-meg4.md`) will not be touched.
- "umbilical" → existing umbilical pages (`subsea-umbilical-system.md`, `umbilical-tube-sizing-api-17e.md`) will not be touched.
- "structural" — generic page won't be touched.

**Path-sanction provenance check** (per #2596 W3-C erratum):

- This plan does NOT cite #2471 as path-sanction.
- Path-sanction for `wiki/standards/<code-id>.md` is provided by `knowledge/wikis/engineering/CLAUDE.md` line 7 (`Pages: wiki/{concepts,entities,sources,standards,workflows}/`).
- The allowlist test `tests/governance/test_2471_citation_scope.py` will be run as part of acceptance to catch any over-citation in child pages or the plan itself.

<!-- Source count: 12 distinct sources cited above —
  (1) parent wave #2540 (CLOSED — confirmed),
  (2) wiki index.md,
  (3) wiki CLAUDE.md schema,
  (4) #2588 W1-C audit,
  (5) #2596 W3-C erratum,
  (6) #2597 W3-D shape precedent,
  (7) /mnt/ace pipeline literature corpora,
  (8) /mnt/ace/saipem EPCI corpus,
  (9) digitalmodel/src/digitalmodel/subsea/pipeline/ module footprint,
  (10) WebSearch Bai/Bai chapter list,
  (11) WebSearch DNV-ST-F101 (current rebrand),
  (12) calc-citation-contract.md.
  Minimum 3 met (well exceeded). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2602-llm-wiki-W4D-engineering-pipeline-expansion.md` |
| Tests | `tests/knowledge/test_engineering_pipeline_expansion.py` |
| Implementation (10 wiki pages) | `knowledge/wikis/engineering/wiki/concepts/{pipeline-route-selection, pipeline-on-bottom-stability, pipeline-lateral-buckling, pipeline-upheaval-buckling, pipeline-walking, pipeline-soil-interaction, pipeline-installation-methods, pipeline-end-expansion-spool-design, pipeline-trawl-impact-protection, pipeline-coatings}.md` |
| Index update | `knowledge/wikis/engineering/wiki/index.md` |
| Log update | `knowledge/wikis/engineering/wiki/log.md` |
| Plan review — Claude | `scripts/review/results/2026-05-03-plan-W4D-engineering-pipeline-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-03-plan-W4D-engineering-pipeline-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-03-plan-W4D-engineering-pipeline-gemini.md` |
| Plan index update | `docs/plans/README.md` |

---

## Deliverable

Ten new concept pages will exist under `knowledge/wikis/engineering/wiki/concepts/`, each carrying `CLAUDE.md`-compliant frontmatter, ≥1 standards-body cross-reference (DNV / API / ASME / ISO — NAME only, no thresholds), ≥2 cross-links to other engineering-wiki pages, and zero scope overlap with `pipeline-integrity-assessment.md` (corroded FFS) or `free-span-viv-fatigue.md` (free-span VIV mechanics) or any riser/mooring/umbilical scope — with `index.md` updated to surface every new page in its Concepts catalogue table and `log.md` carrying a 2026-05-03 W4-D expand entry.

---

## Pseudocode

```
# Per-page authoring contract (applies to all 10 new pages):
function author_concept_page(slug, scope_summary):
    write frontmatter (per knowledge/wikis/engineering/CLAUDE.md):
        title: human-readable
        tags: [pipeline, <topology-tag>, <standards-tag>]   # 'pipeline' MANDATORY for cluster discoverability
        added: 2026-05-03
        last_updated: 2026-05-03
        sources: [<existing source page if any, else omit>]
    section "Scope" — 1 paragraph stating what the page IS and what it is NOT
        (boundary discipline:
          - on-bottom-stability page must NOT re-cover free-span VIV mechanics
            (those live on free-span-viv-fatigue.md)
          - no page may re-cover corroded-FFS / wall-loss / API-579 scope
            (those live on pipeline-integrity-assessment.md)
          - no page may broaden into riser, mooring, or umbilical scope)
    section "Key Concepts" — 5–10 bulleted definitions, each ≤1 line
    section "Standards / References" — ≥1 bullet NAMING DNV-ST-F101 (umbrella),
        DNV-RP-F109 / F110 / F111 / F114 / F116, API RP 1111, ASME B31.4 / B31.8,
        ISO 13623 — with stable URL — but MUST NOT enumerate specific thresholds,
        formulas, or code clauses (those belong on wiki/standards/<code-id>.md per
        the engineering wiki's local CLAUDE.md directory schema; #2471 is
        CSA-Z276-specific per memory project_wiki_standards_path_decision.md
        and is NOT cited as generalized path-sanction)
    canonical forward-reference marker for not-yet-codified standards:
        for any standards body that does NOT yet have a wiki/standards/<code-id>.md
        page on disk (verified via Path.exists() at write-time), the citation MUST
        be paired with an HTML comment in the canonical form
        `<!-- TODO(W4-codify): replace external URL with [[../standards/<code-id>]] when standards page lands -->`
        immediately after the citation line. For already-codified standards
        (e.g., DNV-RP-F101, DNV-RP-F105 — present on disk today), use a
        relative wikilink `[[../standards/<code-id>]]` instead and emit no marker.
    section "Cross-References" — wiki-style [[link]] entries to ≥2 existing
        engineering-wiki pages (must include free-span-viv-fatigue.md or
        pipeline-integrity-assessment.md from at least one of the 10 new pages
        to cross-stitch the cluster; MUST NOT cross-link to
        workflows/orcawave-to-orcaflex-pipeline.md — that is a homonym)
    forbid: extracted text from PDFs (#2482 deny-list)
    forbid: any reference that broadens scope into risers, mooring lines,
        or umbilicals (per prompt scope discipline)
    forbid: any citation of #2471 as path-sanction (per #2596 W3-C erratum)
    enforce: word count ≤ 400 per page (concept summary, not chapter copy)

function update_index(index_path, new_pages):
    insert each new concept page into "Concepts" table (alphabetical by title)
    re-derive page_count at execution time:
        new_page_count = current page_count (read from frontmatter at execution) + 10
        # parallel-plan tolerant: if #2559 (or other plan) bumped page_count first,
        # this still yields the correct value
    re-derive concepts-table heading at execution time:
        new_heading_count = current concepts-table row count + 10
        rewrite "## Concepts (<old> pages)" → "## Concepts (<new> pages)"
    leave entities/sources/standards/workflows untouched (no new entries from this plan)

function append_log(log_path):
    append "[2026-05-03] expand | engineering W4-D — 10 pipeline sub-domain concept pages"
        - Pages added: <list>
        - Notes: covers route, on-bottom stability, lateral/upheaval buckling,
                 walking, pipe-soil interaction, installation methods, end-expansion/
                 spool, trawl impact, coatings; defers HDD-onshore-crossing,
                 riser-pipeline interface, dedicated CP-on-pipeline page to
                 follow-up batch.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-route-selection.md` | Geohazard avoidance, corridor selection, crossing taxonomy, free-span vs trench economics; references DNV-ST-F101 + Bai Ch (route GN PDF on /mnt/ace) |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-on-bottom-stability.md` | Absolute / generalised lateral stability; concrete weight coating; references DNV-RP-F109; cross-link to `free-span-viv-fatigue.md` for span-formation mechanics |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-lateral-buckling.md` | Snake-lay, sleeper triggering, residual lay-tension, mode shapes; references DNV-RP-F110; cross-link to `digitalmodel/subsea/pipeline/lateral_buckling.py` (NAME only) |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-upheaval-buckling.md` | Download, cover height, imperfection, Palmer-Hobbs; references DNV-RP-F110; cross-link to `digitalmodel/subsea/pipeline/upheaval_buckling.py` (NAME only) |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-walking.md` | Asymmetric thermal cycling, axial creep, end-expansion, anchor design; references Carr / Bruton walking-mechanism literature (NAME only) |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-soil-interaction.md` | Axial / lateral resistance models, berm formation, embedment-history dependence; references DNV-RP-F114 |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-installation-methods.md` | S-lay, J-lay, reel-lay, tow-out (surface, mid-depth, off-bottom, bottom); references API RP 1111 + Saipem EPCI corpus context (NAME only) |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-end-expansion-spool-design.md` | End-expansion, expansion spool, mid-line tee, PLET, sleeper interaction; cross-link to walking + lateral-buckling |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-trawl-impact-protection.md` | DNV-RP-F111; rock-dump / mattress / trenching / burial; impact-energy bands |
| Create | `knowledge/wikis/engineering/wiki/concepts/pipeline-coatings.md` | Anti-corrosion (FBE / 3LPE / 3LPP), thermal-insulation (wet / dry / PIP), concrete weight, field-joint coating; references API RP 5L2 / DNV-RP-F106 |
| Modify | `knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md` | Add ≤3-line "Related design pages" pointer block to the new on-bottom-stability + soil-interaction + lateral-buckling pages (reverse-traversal pattern from W1-D M2). **Maintenance:** review the existing page for any non-pipeline scope drift (none expected). |
| Modify | `knowledge/wikis/engineering/wiki/concepts/pipeline-integrity-assessment.md` | Add ≤3-line "Related design pages" pointer block to the new walking + end-expansion-spool + coatings pages (cluster stitch). |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | Add 10 new concept rows alphabetically into Concepts table; **re-derive at execution time** the Concepts heading row-count and the frontmatter `page_count` (current+10); do NOT hard-code `93` or `(42 pages)` because parallel plans (#2559 OCIMF tandem, #2597 W3-D riser) may shift the baseline before this plan executes |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | Append `[2026-05-03] expand | engineering W4-D — 10 pipeline sub-domain concept pages` entry |
| Create | `tests/knowledge/test_engineering_pipeline_expansion.py` | TDD frontmatter / cross-link / standards-citation / index-resolves / scope-discipline / past-tense-drift / forward-reference-marker / no-#2471-over-citation checks |
| Update | `docs/plans/README.md` | Add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_ten_pages_exist` | Each of the 10 new files is on disk | path list | all 10 `Path.exists()` is True |
| `test_frontmatter_required_fields` | Every new page has `title`, `tags`, `added`, `last_updated` per `knowledge/wikis/engineering/CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_frontmatter_tag_pipeline` | Every new page tags includes `pipeline` (cluster discoverability + boundary against `workflows/orcawave-to-orcaflex-pipeline.md` homonym) | parse YAML | `'pipeline' in tags` |
| `test_frontmatter_added_date_2026_05_03` | Every new page has `added: 2026-05-03` (drift catch — past-tense plan vs. execution date allowed; plan tense remains future) | parse YAML | `added == '2026-05-03'` |
| `test_at_least_one_standards_reference` | Page body cites ≥1 of DNV-ST-F101 / RP-F109 / RP-F110 / RP-F111 / RP-F114 / RP-F116, API RP 1111 / 1102 / 5L2, ASME B31.4 / B31.8, ISO 13623 (NAME ONLY — no thresholds per W1-D-revised pattern) | regex search of body text | match found per page |
| `test_at_least_two_cross_links` | Each page contains ≥2 `[[wikilink]]`-style or relative-markdown cross-references to engineering-wiki pages that exist on disk | parse markdown links + wikilinks | ≥2 resolvable refs per page |
| `test_at_least_one_cross_link_to_existing_pipeline_page` | At least one of the 10 new pages links back to `pipeline-integrity-assessment.md` AND at least one links to `free-span-viv-fatigue.md` (cluster cross-stitch) | grep across 10 new pages | ≥1 page has each link |
| `test_no_cross_link_to_workflows_pipeline` | New pages MUST NOT link to `workflows/orcawave-to-orcaflex-pipeline.md` (homonym disambiguation) | grep | zero matches |
| `test_no_scope_creep_into_riser_mooring_umbilical` | New page bodies do not own riser/mooring/umbilical scope. **Section-dominance check:** tokenise each page into top-level (H2) sections; for each section, count `riser\|SCR\|TTR\|mooring\|umbilical` keyword hits vs. `pipeline\|flowline\|pipelay\|S-lay\|J-lay\|reel-lay\|on-bottom\|free-span\|buckling\|spool\|PLET\|trawl\|coating` hits. Fail if any section's non-pipeline keyword count exceeds the pipeline keyword count. **Whitelist:** sections titled `## Scope` or `## Out of Scope` are exempt (boundary callouts encouraged). | tokenise H2; per-section keyword ratio | every non-whitelisted section has pipeline-keyword count ≥ non-pipeline-keyword count |
| `test_pipeline_topic_dominance_positive` | Each new page contains ≥3 occurrences of `pipeline` OR a pipeline-typology subterm (`flowline`, `pipelay`, `S-lay`, `J-lay`, `reel-lay`, `on-bottom stability`, `lateral buckling`, `upheaval buckling`, `walking`, `spool`, `PLET`, `trawl`, `FBE`, `3LPE`) in body text — guards against synonym-attack (e.g., re-covering riser content under "tendon walking" or umbilical content under "tube installation"). | regex count per page | ≥3 hits per page |
| `test_word_count_under_400` | Concept-summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (e.g. "Page N of M" stamps, very long single paragraphs > 80 words, ALL-CAPS headings) | heuristic | no flagged paragraphs |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts table resolves on disk | walk markdown links | 100% resolve |
| `test_index_page_count_bumped` | `index.md` frontmatter `page_count` updated to **≥93** (floor, not equality, to absorb any parallel-plan arithmetic shift — #2559 OCIMF, #2597 W3-D riser); Concepts table heading is `## Concepts (N pages)` where N matches the actual concepts-table row count after insertion (re-derived at execution time). | parse YAML + count rows | `page_count ≥ 93`; heading number == row count |
| `test_log_entry_appended` | `log.md` contains a 2026-05-03 expand entry naming W4-D | grep | match present |
| `test_no_past_tense_artifact_drift` | No new page contains future-work claimed-as-done phrasing (regex for "we added", "we created", "this page was", "completed", "delivered" outside of explicit "## Cross-References" / link-text region) | regex | zero matches |
| `test_no_redundant_corroded_ffs_content_in_new_pages` | New pages MUST NOT re-introduce corroded-FFS content (DNV-RP-F101 corrosion assessment, API-579 FAD, FFS Level 1/2/3 prose, RSF/RSFa, point-defect / patch-corrosion tables) — that lives only on `pipeline-integrity-assessment.md`. Keyword list: `RSF`, `RSFa`, `Level 1 assessment`, `Level 2 assessment`, `Level 3 assessment`, `point defect`, `patch corrosion`, `Folias factor`. Also caps occurrences of `corrosion` to ≤5 per page. | regex match + count cap | zero matches per new page; `corrosion` ≤5 |
| `test_no_redundant_free_span_viv_content_in_new_pages` | New pages MUST NOT re-introduce free-span VIV mechanics — Strouhal, lock-in, in-line/cross-flow VIV response, Iwan-Blevins, Vortex-Induced-Vibration explicit S-N curves. Keyword list: `Strouhal`, `lock-in`, `cross-flow VIV`, `in-line VIV`, `Iwan-Blevins`. Also caps `VIV` occurrences to ≤3 per page. | regex match + count cap | zero matches per new page; `VIV` ≤3 |
| `test_forward_reference_markers_present` | For every external standards-body URL appearing in a new page where the corresponding `wiki/standards/<code-id>.md` page does NOT exist on disk, the citation line MUST be paired with the canonical HTML comment `<!-- TODO(W4-codify): replace external URL with [[../standards/<code-id>]] when standards page lands -->`. Conversely, if the standards page DOES exist on disk (e.g., `dnv-rp-f101.md`, `dnv-rp-f105.md`), the new page MUST use the relative wikilink `[[../standards/<code-id>]]` and NOT the external URL. Test enumerates all `https://` URLs whose hostname is `dnv.com`, `api.org`, `asme.org`, or `iso.org` and asserts the marker / wikilink invariant. | regex enumerate URLs + Path.exists() + marker check | every URL satisfies the invariant |
| `test_forward_reference_marker_count_emit` | Test emits a count and file-list of pending `TODO(W4-codify):` markers across the 10 new pages so a future plan reviewing standards-codification follow-up can run the test, get the deletion checklist, and discharge the markers deterministically. (Test does not fail on count > 0; it asserts count is recorded in test output for downstream tooling.) | grep across 10 new pages | count + file list emitted |
| `test_no_2471_path_sanction_citation` | Per W3-C (#2596) erratum: this plan and the 10 new pages MUST NOT cite #2471 as a generalized path-sanction. Test greps the plan + new pages + the test file itself for `#2471` and asserts that any occurrence is either (a) absent, or (b) inside a documented "NOT a path-sanction" boundary callout. Complements the allowlist test at `tests/governance/test_2471_citation_scope.py`. | grep #2471 occurrences in plan + 10 new pages | each occurrence is in a boundary-callout context (or zero) |
| `test_governance_allowlist_passes` | `tests/governance/test_2471_citation_scope.py` continues to pass after this plan's 10 new pages land (no over-citation regression). | run pytest on the governance test | pytest exit 0 |
| `test_existing_pipeline_page_pointer_block_added` | `concepts/pipeline-integrity-assessment.md` and `concepts/free-span-viv-fatigue.md` each gain a "Related design pages" pointer block listing ≥2 of the 10 new pages | grep | match present, ≥2 links each |

---

## Acceptance Criteria

- [ ] All 10 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-03`, `last_updated=2026-05-03`, `tags` includes `pipeline`).
- [ ] Each new page will NAME ≥1 standards body (DNV / API / ASME / ISO) with stable URL or relative `[[../standards/<code-id>]]` link, but MUST NOT enumerate specific thresholds, formulas, or code clauses.
- [ ] Each new page will list ≥2 cross-references to other engineering-wiki pages.
- [ ] At least one of the 10 new pages will cross-link to `concepts/pipeline-integrity-assessment.md` AND at least one will cross-link to `concepts/free-span-viv-fatigue.md` (cluster stitch).
- [ ] No new page will cross-link to `workflows/orcawave-to-orcaflex-pipeline.md` (homonym disambiguation).
- [ ] `concepts/pipeline-integrity-assessment.md` and `concepts/free-span-viv-fatigue.md` will each be updated to add a "Related design pages" pointer block listing ≥2 of the new pages.
- [ ] No new page will overlap with `pipeline-integrity-assessment.md` corroded-FFS scope (no RSF/RSFa, no FFS Level prose, no Folias-factor formula).
- [ ] No new page will overlap with `free-span-viv-fatigue.md` VIV-mechanics scope (no Strouhal/lock-in/Iwan-Blevins, ≤3 `VIV` occurrences).
- [ ] No new page will broaden scope into risers, mooring, or umbilicals (enforced via section-dominance keyword-ratio test + positive pipeline-topic-dominance test; legitimate adjacency preserved by H2 `## Scope` / `## Out of Scope` whitelisting).
- [ ] `index.md` Concepts table will list 10 new rows (alphabetical); table heading will read `## Concepts (N pages)` where N == actual row count after insertion (re-derived at execution time, not hard-coded, to absorb parallel-plan arithmetic shift from #2559 OCIMF and #2597 W3-D riser).
- [ ] `index.md` frontmatter `page_count` will read **≥93** (floor; equality holds only if no parallel plan bumped the count first).
- [ ] `log.md` will carry a `[2026-05-03] expand | engineering W4-D` entry.
- [ ] `tests/knowledge/test_engineering_pipeline_expansion.py` will pass: `uv run pytest tests/knowledge/test_engineering_pipeline_expansion.py -v`.
- [ ] `tests/governance/test_2471_citation_scope.py` will continue to pass — no over-citation of #2471 introduced.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Each new page will be ≤400 words (concept-summary discipline per #2482 deny-list).
- [ ] No calc-module is expected to cite these new concept pages as standards-resolution targets; calc-side citations continue to require direct `wiki/standards/<code-id>.md` resolution per `.claude/rules/calc-citation-contract.md`.
- [ ] Every external standards-body URL on a new page is paired with either (a) the canonical HTML comment `<!-- TODO(W4-codify): replace external URL with [[../standards/<code-id>]] when standards page lands -->` for not-yet-codified standards, or (b) a relative `[[../standards/<code-id>]]` wikilink for already-codified standards (DNV-RP-F101, DNV-RP-F105).
- [ ] Review artifacts will be posted under `scripts/review/results/2026-05-03-plan-W4D-engineering-pipeline-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Status remains 'draft' until adversarial review and revisions land. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD (codex-cli 0.124.0 stdin-hang regression #2479 may force UNAVAILABLE per W3-D precedent) |
| Gemini | TBD | TBD (gemini sandbox path resolution may force UNAVAILABLE per W3-D precedent) |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk: terminology drift / homonym.** "Pipeline" is used in this repo for both subsea pipeline engineering (intended scope) AND data-handoff pipelines (`workflows/orcawave-to-orcaflex-pipeline.md`, plus generic CI/CD). Pages will tag with substantive engineering tags (`subsea`, `pipelay`, `buckling`, `stability`, `coating`) on top of the cluster-discoverability `pipeline` tag, and TDD `test_no_cross_link_to_workflows_pipeline` blocks accidental cross-link to the data-pipeline page.
- **Risk: scope creep into riser-pipeline interface.** Subsea production layouts include PLETs, mid-line tees, J-tube pull-ins, and SCR-flowline tie-ins where pipeline and riser scopes overlap. A dedicated `riser-pipeline-interface.md` page (covering PLET, jumper, SCR-flowline tie-in, J-tube pull-in) is **deferred** to a follow-up batch to keep this batch pipeline-only. The TDD test `test_no_scope_creep_into_riser_mooring_umbilical` uses a section-dominance check with `## Scope` / `## Out of Scope` whitelisting so legitimate adjacency mention is preserved.
- **Risk: false-gap from terminology mismatch with existing pages.** `pipeline-integrity-assessment.md` covers corroded FFS; `free-span-viv-fatigue.md` covers free-span VIV. New pages will explicitly cite these in their "Scope" callouts and state the boundary. The TDD tests `test_no_redundant_corroded_ffs_content_in_new_pages` and `test_no_redundant_free_span_viv_content_in_new_pages` enforce non-overlap.
- **Risk: forward-reference debt for not-yet-codified standards** (DNV-ST-F101, DNV-RP-F109, F110, F111, F114, F116, API RP 1111, API RP 1102, ASME B31.4, B31.8, ISO 13623). None of these have a `wiki/standards/<code-id>.md` on disk at the time of writing. New pages will cite each by title and URL only, paired with the canonical HTML comment marker `<!-- TODO(W4-codify): replace external URL with [[../standards/<code-id>]] when standards page lands -->`. The TDD tests `test_forward_reference_markers_present` and `test_forward_reference_marker_count_emit` enforce the marker invariant and emit a deletion checklist. The marker tag `W4-codify` is intentionally distinct from W3-D's `W3-B` tag so a future plan can run a tag-specific deletion sweep without ambiguity.
- **Risk: parallel-plan arithmetic interaction with #2559 OCIMF tandem mooring promotion AND #2597 W3-D riser expansion.** Both may modify `index.md` `page_count` and the Concepts heading row count between this plan's approval and execution. At execution time, the implementer will **re-derive both numbers from the on-disk state** (current `page_count` + 10; recount Concepts rows after insertion). The TDD test `test_index_page_count_bumped` uses a `≥93` floor (not equality), and the heading literal is also re-derived; reviewers should not block PR review on the exact heading number if a parallel plan landed first.
- **Risk: #2471 path-sanction over-citation regression** (per #2596 W3-C erratum). This plan does not cite #2471 as path-sanction. The TDD test `test_no_2471_path_sanction_citation` plus the existing governance allowlist `tests/governance/test_2471_citation_scope.py` will catch regressions in the new pages or the test file itself.
- **Risk: digitalmodel cross-ref deferred.** Adding these concept pages does NOT create calc-side `Citation` instances. Calc-side adoption (e.g., `digitalmodel/subsea/pipeline/lateral_buckling.py` adding a citation to the new `pipeline-lateral-buckling.md`) is a separate follow-up issue under `.claude/rules/calc-citation-contract.md`. This plan's Acceptance Criteria do not require any calc-module change.
- **Risk: no formal seed YAML for engineering wiki.** Same as W3-D: this plan edits `index.md` directly (additive insert into Concepts table). If a seed-based regenerator lands later, the seed file should pick up these 10 entries from disk by directory walk; until then, the manual edit is the single source of truth.
- **Risk: parallel work collision with #2588 W1-C audit.** If the audit's prioritized child-issue list orders the pipeline bucket differently or sub-divides it, this plan may need re-sequencing. Mitigation: this plan is **independent** of W1-C; the 10 concept pages are foundational regardless of order.
- **Risk: 11th and 12th canonical topics deferred.** `concepts/pipeline-hdd-crossing.md` (HDD onshore-pipeline crossing) and `concepts/riser-pipeline-interface.md` (PLET, SCR-flowline tie-in, J-tube pull-in) are deferred to follow-up batches.

- **Open: should onshore-pipeline scope (HDD, ASME B31.4/B31.8 onshore, regulatory frameworks) be in this batch or a separate "onshore-pipeline" sub-domain expansion?** Current plan **excludes onshore-pipeline as primary scope** — the 10 new pages are all offshore-subsea-pipeline-centric. Onshore-pipeline gets a NAME-only mention in `pipeline-route-selection.md` (HDD context) and `pipeline-coatings.md` (FBE applies onshore too). A dedicated onshore-pipeline batch (HDD crossings, regulatory framework, ASME B31.4/8 onshore-specific design) is flagged for a follow-up. **Reviewer may flip this decision** to (a) add `pipeline-hdd-crossing.md` to this batch (making it 11 pages) or (b) split this batch into offshore-only (these 10) and onshore-only (separate W4-onshore plan).
- **Open: should `concepts/cathodic-protection-design.md` get a pipeline-CP pointer-block update in this batch?** Pipelines carry bracelet anodes with attenuation effects different from riser CP; the existing CP page is generic. Current plan leaves it untouched; reviewer may flag.
- **Open: should `concepts/pipeline-installation-methods.md` ALSO cover mid-line repair / hot-tap / hyperbaric welding / commissioning?** Current plan keeps installation-only (S-lay/J-lay/reel-lay/tow-out); commissioning is a separate domain. Reviewer may flag.
- **Open: should the `tags` for new pages include explicit `subsea` to disambiguate from any future onshore-pipeline pages?** Current plan: yes (every page tags `[pipeline, subsea, ...]`).

---

## Complexity: T2

**T2** — 10 new wiki pages + 2 modified existing pages (pipeline-integrity-assessment.md + free-span-viv-fatigue.md pointer blocks) + 2 modified registry files (index.md, log.md) + 1 new test module + 1 doc index update. Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in (a) cross-link discipline, (b) scope-boundary against `pipeline-integrity-assessment.md` and `free-span-viv-fatigue.md`, (c) riser/mooring/umbilical scope-creep, (d) homonym discipline against `workflows/orcawave-to-orcaflex-pipeline.md`, and (e) #2471 path-sanction over-citation — all addressable with regex tests. Not T3 because there is no new module / no calc / no migration / no schema change. Slightly heavier than W3-D (10 vs 8 pages, additional homonym test, additional #2471 over-citation test) but still T2.
