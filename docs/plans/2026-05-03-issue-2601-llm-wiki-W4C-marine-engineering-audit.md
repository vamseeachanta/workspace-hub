# Plan: audit(llm-wiki) — marine-engineering wiki gap audit + prioritized backfill sequence (W4-C)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2601
> **Review artifacts:** scripts/review/results/2026-05-03-plan-W4C-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/marine-engineering/wiki/` — 19,199 .md files; subdir distribution `comparisons=1, concepts=14, entities=15, sources=19166, visualizations=0` plus 3 root files (`index.md`, `log.md`, `overview.md`). Sources alone is 99.83% of the wiki (19,166 / 19,199).
- Found: `knowledge/wikis/marine-engineering/raw/` — only 5 source PDFs in `raw/papers/`; `raw/articles/`, `raw/assets/`, `raw/standards/` directories exist but are empty. Raw is the *original 5-document seed*; the 19,166 source pages were auto-ingested from external corpora at `/mnt/ace/docs/conferences/...` (verified inline frontmatter `path:` field) — they were never staged through `raw/`. Implication: a raw-vs-wiki delta-on-disk diff (the W1-C engineering pattern) does **not** apply to this domain; the audit must instead diff against the *external* corpora the index claims to cover, and against the canonical practitioner taxonomy.
- Found: `knowledge/wikis/marine-engineering/wiki/sources/` is dominated by conference-proceedings stubs auto-created by `llm-wiki batch-ingest` (verified in sample `omae2008-57873.md` line 13). Each source page carries a near-empty body — `## Metadata` table with collection/filename/path/year and **`tags: []`** in frontmatter — i.e., they are *index entries*, not summaries. The wiki has no concept-extraction pass over the 19,166 papers yet.
- Found: `knowledge/wikis/marine-engineering/wiki/overview.md` — reports `Source documents: 5, Entity pages: 8, Concept pages: 7, Total wiki pages: 20`. Overview is **stale** (still describes the seed-migration state from 2026-04-07); does not reflect the 19,166-source ingest from the OMAE/OTC/SNAME/Offshore-Symposium batch ingests.
- Found: `knowledge/wikis/marine-engineering/CLAUDE.md` — declares `wiki/standards/` as part of the canonical schema (with required `code_id` / `publisher` / `revision` frontmatter), but the directory **does not exist on disk**. Standards subdir is missing entirely. (Verified: `find wiki -maxdepth 2 -type d` returns only comparisons/concepts/entities/sources/visualizations.)
- Found (wiring check): `digitalmodel/` references to `knowledge/wikis/marine-engineering/` — only YAML fixture comments under `digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/` (5 files) and one validation test, none citing specific wiki pages as authoritative-source frontmatter. Unlike the engineering wiki (where `wiki/standards/dnv-os-e301.md` is wired into `digitalmodel/src/digitalmodel/citations/registry.py`), no marine-engineering wiki page is wired into the citation contract today. This means prioritization cannot anchor on existing citation wiring; it must anchor on (a) the canonical practitioner taxonomy and (b) the curated-content gap (concepts/entities thinness vs sources volume).
- Gap: no coverage-gap detector script exists yet (#2392 still OPEN). This audit is the manual marine-engineering precursor.
- Gap: `wiki/standards/` subdir does not exist, despite the CLAUDE.md schema requiring it. CSA Z276 promotion (#2522) and DNV/API/ISO promotion lanes (#2586/#2590/#2595) all target a directory that has not been created.
- Gap: `wiki/visualizations/` and `wiki/comparisons/` are essentially empty (0 and 1 files respectively).

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — audit-only plan; emits no calc constants | n/a | n/a |

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/concepts/` (14 files): cathodic-protection-system, coating-breakdown, corrosion-control, fsru-marine-terminal-interface, lng-berth-operability, lng-marine-terminal-engineering, lng-transfer-system-envelope, long-period-swell-resonance, mooring-line-failure, process-safety, riser-extreme-statistics-orcaflex-workbooks, sour-service, subsea-cable-umbilical-cross-sections, suction-pile-preliminary-sizing-api-py-tz. Topical clusters: corrosion/CP (3), LNG-terminal (4), mooring/resonance (2), process safety (2), riser/cable/pile (3). Whole sub-disciplines absent: seakeeping/hydrodynamics, station-keeping (DP/spread-mooring), naval-architecture-of-offshore-units (intact/damaged stability of floating units), wave-loading and metocean, fatigue/SN-curves (only riser-extreme-statistics is adjacent), motions analysis (RAOs), structural integrity (jacket/topsides/hull), towing/installation engineering, decommissioning.
- `knowledge/wikis/marine-engineering/wiki/entities/` (15 files): ai-dwop, anode, cadquery, cfd-offshore, compressor, energy-economics, fea-structural-analysis, flange, float-collar, float-shoe, gasket, lng-carrier-mooring, orcaflex-viv-analysis, pipeline-integrity, separator. Half are piping/process equipment (anode, compressor, flange, float-collar, float-shoe, gasket, separator); only one mooring entity (lng-carrier-mooring), one riser/VIV entity (orcaflex-viv-analysis), no FPSO/FLNG/semisubmersible/spar/jack-up/TLP/jacket/subsea-tree entities, no buoy/CALM/SPM, no risers (SCR/TTR/lazy-wave/SLWR), no turret, no swivel, no flexjoint, no marine-riser, no umbilical/dynamic-cable.
- `knowledge/wikis/marine-engineering/wiki/sources/` (19,166 files): per `awk` 4-char-prefix histogram, top conferences by file count are OMAE (`omae` prefix, 6,234 files = 32.5%), OTC (`otc1` 2,904 + `otc2` 1,370 + `otc-` 643 + `otc8` 254 = 5,171 files = 27.0%), Offshore Symposium TPC (`14tpc`/`13tpc`/`11tpc` totalling 1,632 files = 8.5%), dated rollups (`2012-` 690 + `2004-` 463 = 1,153 files = 6.0%), ISOPE journal-style (`i07j` 341 = 1.8%), SPE-prefixed (`spe1` 145 + `spe-` 27 = 172 = 0.9%), `pape*` papers (106 = 0.6%), `sname` (68 = 0.4%). Each source page is a `tags: []` empty-body stub — no concept-extraction over the 19K corpus yet.
- `knowledge/wikis/marine-engineering/wiki/comparisons/` (1 file): `offshore-wind-oil-gas-cross-section-assessment.md` (sole curated comparison).
- `knowledge/wikis/marine-engineering/wiki/visualizations/`: 0 files (directory exists but unused).
- `knowledge/wikis/marine-engineering/wiki/standards/`: directory does **not exist**.
- `knowledge/wikis/marine-engineering/wiki/index.md`: 1.4 MB, 21,605 lines, sections at `## Entities` (line 13), `## Concepts` (line 33), `## Sources` (line 52), `## Comparisons` (line 66), `## Topics Covered` (line 72). Sources section is the chunking target of #2378.
- `knowledge/wikis/marine-engineering/wiki/overview.md`: 60 lines, **stale** (claims `Total wiki pages: 20`).

### Documents consulted
- `knowledge/wikis/marine-engineering/CLAUDE.md` — domain schema; declares 7 expected wiki subdirs (entities/concepts/sources/comparisons/visualizations/standards + index.md/log.md/overview.md root files); only 5 of 7 subdirs exist on disk.
- `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md` — sibling W1-C precedent for the engineering domain; shape this audit follows. Key inheritance: distribution table + gap audit table + prioritized backfill list + verifiable-anchor regex on each rationale.
- `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` — chunking plan for the 21,605-line marine `index.md`; orthogonal (navigation), but informs why source-stub-deduplication is a P3 here (chunking already addresses access).
- Issue #2588 — OPEN — engineering wiki gap audit (W1-C parent pattern).
- Issue #2378 — OPEN — marine-wiki chunked index (sibling navigation work).
- Issue #2540 — CLOSED — Elements overnight planning wave (parent of this overnight wave).
- Issue #2522 — OPEN — Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering `wiki/standards/` (currently blocked by missing standards subdir).
- Issue #2586 — OPEN — bounded API standards summary promotion (W1-A); marine-adjacent standards land in `engineering` wiki today, may need cross-link to marine.
- Issue #2590 — OPEN — bounded DNV standards summary promotion (W2-A).
- Issue #2595 — OPEN — bounded ISO 19900-series offshore standards summary (W3-B).
- Issue #2392 — OPEN — wiki coverage-gap detector; this audit is its manual marine-engineering precursor.
- Issue #2368 — OPEN — faceted portal pages for large LLM-wiki domains; marine-engineering is the principal beneficiary.
- Issue #2366 — OPEN — strengthening scorecard / prioritized action queue; this audit's priority list is a feeder.
- Issue #2372 — OPEN — canonical source-title aliasing (acts on the 19,166 source stubs to resolve PDF-filename → human title).
- Issue #2010 — OPEN — career-learnings seed migration (pipeline integrity, OrcaFlex VIV, FEA, CFD, energy-economics).
- Issue #2044 — OPEN — engineering wiki cross-link discovery with domain wikis.
- `.claude/rules/calc-citation-contract.md` — citations must point at `wiki/standards/<code-id>.md` with #2471 frontmatter. Marine-engineering currently cannot satisfy this rule for any code (no standards subdir exists); creating the directory is a prerequisite for any marine-domain calc citation.
- ITTC Recommended Procedures TOC (`https://ittc.info/`) — used as the verifiable external practitioner taxonomy. ITTC Specialist Committees define marine-hydrodynamics sub-disciplines: Ocean Engineering, Stability in Waves, Manoeuvring, Seakeeping, Resistance, Propulsion, CFD/Numerical, Cavitation, Ice (each is a falsifiable English-named anchor with an ITTC procedure number, e.g., 7.5-02-07-03.x).
- SNAME Offshore Section practitioner reference (`https://www.sname.org/SNAME/Sections/`) — second taxonomy anchor; SNAME Offshore Symposium proceedings are already 1,632 files in the source set, so SNAME taxonomy is a natural mapping target.

### Gaps identified
- The wiki **schema-vs-disk delta**: `CLAUDE.md` declares 7 expected child paths but only 5 exist (`comparisons/concepts/entities/sources/visualizations/`). `standards/` and proper population of `comparisons/` + `visualizations/` are both absent. This is the single largest structural gap.
- The **curated-vs-stub ratio**: 30 curated pages (14 concepts + 15 entities + 1 comparison) versus 19,166 source stubs is ~1:639. There is effectively zero concept-extraction layer built atop the ingested papers; the wiki is a paper *index* not a *knowledge* surface today.
- The **stale-overview drift**: `overview.md` claims 20 total pages while the wiki has 19,199 — a 960× understatement that misleads any retrieval-time agent reading the overview first.
- The **conference-paper duplication risk**: 19,166 source stubs across OMAE/OTC/Offshore-Symposium/ISOPE/SNAME/SPE almost certainly contain near-duplicates (same author, same topic, multiple years/venues) and orphan stubs (papers that were ingested but contribute nothing to any concept/entity page); these are #2372 + future-deduplication territory but the audit must flag the magnitude.
- The **sub-discipline coverage gap (priority anchor)**: against ITTC sub-disciplines, the wiki has near-zero coverage of seakeeping (motions, RAOs, wave-frequency response), station-keeping (DP, spread-mooring, single-point), structural integrity of floating units (hull/topsides/jacket fatigue), metocean/wave-environment characterization, and stability in waves. Concepts cover only mooring-failure-physics, LNG-terminal, corrosion, and a few process-safety topics.
- The **citation-contract preflight gap**: zero marine-domain wiki pages are wired into `digitalmodel/src/digitalmodel/citations/registry.py`. Until `wiki/standards/` exists with a #2471-frontmatter page, no marine calc can emit a Citation per the calc-citation contract.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2378` — OPEN — feat(knowledge): chunk and paginate the canonical marine-engineering wiki index
- `#2522` — OPEN — Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering wiki/standards/
- `#2540` — CLOSED — epic(llm-wiki): overnight Elements corpus planning wave after #2536
- `#2588` — OPEN — audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)
- `#2368` — OPEN — feat(knowledge): generate faceted portal pages for large LLM-wiki domains
- `#2392` — OPEN — feat(knowledge): wiki coverage-gap detector
- `#2366` — OPEN — feat(knowledge): add llm-wiki strengthening scorecard
- `#2372` — OPEN — feat(knowledge): add canonical source-title aliasing for wiki source pages
- `#2586` — OPEN — feat(llm-wiki): bounded API standards summary promotion (W1-A)
- `#2590` — OPEN — feat(llm-wiki): bounded DNV standards summary promotion (W2-A)
- `#2595` — OPEN — feat(llm-wiki): bounded ISO 19900-series offshore standards summary (W3-B)
- `#2010` — OPEN — career-learnings seed migration
- `#2044` — OPEN — engineering wiki cross-link discovery with domain wikis

**File counts** (verified 2026-05-02 via `find`/`ls | wc -l`):
- `knowledge/wikis/marine-engineering/wiki/`: 19,199 *.md (find -name "*.md" | wc -l)
  - `wiki/comparisons/`: 1
  - `wiki/concepts/`: 14
  - `wiki/entities/`: 15
  - `wiki/sources/`: 19,166
  - `wiki/visualizations/`: 0
  - `wiki/` root *.md files: 3 (`index.md`, `log.md`, `overview.md`)
- `knowledge/wikis/marine-engineering/raw/`:
  - `raw/articles/`: 0
  - `raw/assets/`: 0
  - `raw/papers/`: 5
  - `raw/standards/`: 0

**Subdir tree** (verified 2026-05-02 via `find -maxdepth 2 -type d`):
```
knowledge/wikis/marine-engineering/raw
knowledge/wikis/marine-engineering/raw/articles
knowledge/wikis/marine-engineering/raw/assets
knowledge/wikis/marine-engineering/raw/papers
knowledge/wikis/marine-engineering/raw/standards
knowledge/wikis/marine-engineering/wiki
knowledge/wikis/marine-engineering/wiki/comparisons
knowledge/wikis/marine-engineering/wiki/concepts
knowledge/wikis/marine-engineering/wiki/entities
knowledge/wikis/marine-engineering/wiki/sources
knowledge/wikis/marine-engineering/wiki/visualizations
```
**Note:** `wiki/standards/` is absent from disk despite being declared in `CLAUDE.md`. This is a structural gap, verifiable by re-running the same `find` command.

**Sources/ filename-prefix distribution** (verified 2026-05-02 via `ls wiki/sources/ | awk '{print substr($0,1,4)}' | sort | uniq -c | sort -rn | head`):
```
   6234 omae   (OMAE conference proceedings)
   2904 otc1   (OTC, 2010s, ~OTC-1xxxx)
   1370 otc2   (OTC, 2000s, OTC-2xxxx)
    690 2012   (dated rollup - 2012 papers)
    643 otc-   (OTC modern dash-format)
    547 14tp   (Offshore Symposium 2014 TPC)
    544 13tp   (Offshore Symposium 2013 TPC)
    541 11tp   (Offshore Symposium 2011 TPC)
    463 2004   (dated rollup - 2004 papers)
    341 i07j   (ISOPE journal-style)
    254 otc8   (OTC, 1980s era OTC-8xxx-9xxx)
    145 spe1   (SPE-1xxxx)
    106 pape   (paper-NN-style)
    103 sess   (sessionN-NN sessions)
     70 i07s   (ISOPE structural)
     68 snam   (SNAME papers)
```
Combined OMAE = 6,234 (32.5%); combined OTC (otc1+otc2+otc-+otc8) = 5,171 (27.0%); combined Offshore Symposium TPC (14tp+13tp+11tp) = 1,632 (8.5%); combined ISOPE (i07j+i07s + small i07-prefix tail ~31+25+18+17+17+15+14 = ~480, est) = ~480 (2.5%); SNAME = 68 (0.4%). Top-5 conferences cover ~70% of sources volume.

**Cross-reference scan from digitalmodel** (verified 2026-05-02 via `grep -rl "knowledge/wikis/marine-engineering" /mnt/local-analysis/workspace-hub/digitalmodel/`):
```
digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/concrete_coated_pipeline.yml
digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/66kv_inter_array_cable.yml
digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/steel_tube_electro_hydraulic_umbilical.yml
digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/220kv_hvac_export_cable.yml
digitalmodel/src/digitalmodel/subsea/cross_sections/fixtures/power_optical_hybrid_umbilical.yml
digitalmodel/tests/subsea/cross_sections/test_validation.py
```
ZERO marine-engineering wiki pages are wired into `citations/registry.py`. The 6 references above are YAML fixtures that name the wiki path as a documentation pointer, not a citation. Confirmed: no marine-domain calc emits a Citation today.

**Sample source-stub body** (verified 2026-05-02 via `cat omae2008-57873.md`):
```
---
title: "OMAE2008-57873.pdf"
slug: omae2008-57873
domain: marine-engineering
added: 2026-04-07
last_updated: 2026-04-07
ingested: 2026-04-07 10:31 UTC
tags: []
---
# OMAE2008-57873.pdf
> Source page auto-created by `llm-wiki batch-ingest` on 2026-04-07 10:31 UTC
> Domain: marine-engineering
## Metadata
| Field | Value |
|-------|-------|
| collection | OMAE |
| filename | OMAE2008-57873.pdf |
| path | /mnt/ace/docs/conferences/OMAE/OMAE 2008/data/pdfs/trk-2/OMAE2008-57873.pdf |
| year | 2008 |
```
Confirms: source pages are filename-as-title stubs with `tags: []`, no extracted concepts, no human-readable summary; #2372 (source-title aliasing) addresses the title surface, not the body.

**Stale overview.md** (verified 2026-05-02 via `head -60 wiki/overview.md`):
```
| Source documents | 5 |
| Entity pages | 8 |
| Concept pages | 7 |
| Total wiki pages | 20 |
```
Actual on-disk count: 19,199 wiki pages (959× understatement). Overview must be regenerated.

**File existence** (`ls -la` 2026-05-02):
- EXISTS: `knowledge/wikis/marine-engineering/CLAUDE.md`
- EXISTS: `knowledge/wikis/marine-engineering/wiki/index.md` (1.4 MB)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/overview.md`
- EXISTS: `knowledge/wikis/marine-engineering/wiki/log.md`
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md` (W1-C precedent)
- MISSING (this plan creates): `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md`
- MISSING (this plan creates): `tests/knowledge/test_marine_engineering_audit_artifact.py`
- MISSING (CLAUDE.md declares but absent): `knowledge/wikis/marine-engineering/wiki/standards/`

**Gap proofs** (verified 2026-05-02):
- `find knowledge/wikis/marine-engineering/wiki -maxdepth 2 -type d | grep -c standards` → `0` → confirms standards/ subdir does not exist.
- `grep -c "knowledge/wikis/marine-engineering/wiki/" /mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/registry.py 2>/dev/null` → `0` → confirms zero marine-engineering wiki citations wired into the citation contract.
- `ls /mnt/local-analysis/workspace-hub/docs/audits/ 2>&1 | head -1` → `No such file or directory` → confirms `docs/audits/` directory will be co-created by W1-C plan #2588 and reused here.

<!-- Source count verification: (1) overnight-wave prompt (this task), (2) W1-C precedent plan #2588, (3) W4 chunked-index sibling plan #2378, (4) marine-engineering CLAUDE.md schema, (5) `.claude/rules/calc-citation-contract.md`, (6) ITTC Recommended Procedures taxonomy, (7) SNAME Offshore Section practitioner reference. Total = 7 distinct sources (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md` |
| Audit report (deliverable) | `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` |
| Tests | `tests/knowledge/test_marine_engineering_audit_artifact.py` |
| Plan review — Claude | `scripts/review/results/2026-05-03-plan-W4C-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-03-plan-W4C-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-03-plan-W4C-gemini.md` |
| Index update | `docs/plans/README.md` |

---

## Deliverable

A single audit report at `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` containing (a) a distribution table of file counts per top-level wiki subdir, raw subdir, and source-filename-prefix bucket; (b) a structural-vs-content gap audit table covering both schema-declared-but-missing paths (e.g., `wiki/standards/`) and ITTC-sub-discipline coverage gaps; (c) a prioritized 5–8-entry child-issue backfill list with one-line rationale per entry, each rationale citing a verifiable taxonomy anchor (ITTC procedure family or SNAME Offshore Section reference) per the W1-C MAJOR-3 lesson; and (d) a deprecation-pass section recommending action on the 19,166-source-stub volume (likely sources for #2372 aliasing + future deduplication, not promotion). NO wiki content will be created or edited. Plus a passing test asserting the audit file exists with the required schema.

---

## Pseudocode

```
audit_report_structure:
    1. Header (date, scope, methodology one-paragraph: distribution + gap + priority)
    2. Distribution tables:
       table_A_wiki_distribution:
         columns = [subdir, file_count, file_count_share_pct, dominant_filename_pattern, content_type]
         rows = comparisons | concepts | entities | sources | visualizations | root
       table_B_raw_distribution:
         columns = [subdir, file_count, content_type]
         rows = articles | assets | papers | standards
       table_C_sources_filename_prefix_buckets:
         columns = [prefix_bucket, file_count, share_of_sources_pct, source_collection]
         rows >= 8 (omae, otc-combined, offshore-symposium-tpc, dated-rollups,
                    isope, sname, spe, paper-NN, session-N, other)
    3. Structural gap audit table:
       columns = [expected_path_per_CLAUDE_md, actual_state, gap_type, action]
       rows include: wiki/standards/ (missing), wiki/comparisons/ (1 file vs schema-implied many),
                     wiki/visualizations/ (0 files), overview.md (stale), entities/ thinness,
                     concepts/ sub-discipline coverage
    4. Sub-discipline coverage matrix (against ITTC taxonomy):
       columns = [ittc_sub_discipline, current_concept_pages, current_entity_pages, gap_severity, ittc_procedure_anchor]
       rows: Seakeeping | Manoeuvring | Stability-in-Waves | Resistance-Propulsion |
             Ocean-Engineering-(station-keeping/mooring) | Ocean-Engineering-(risers/pipelines) |
             Ocean-Engineering-(structures-fatigue) | CFD-Numerical | Ice |
             Metocean-Environmental-Loading
    5. Prioritized backfill sequence:
       5-8 entries, each formatted as:
         - title (suggested child issue title, future-tense)
         - target_path (one or more wiki page paths to be created)
         - priority (P1|P2|P3)
         - rationale (1 line; MUST reference one of: ITTC procedure family
           regex 7\.5-0[0-9]-[0-9]{2}-[0-9]{2}, SNAME-Offshore-Section literal,
           citation-contract literal, or the literal `CLAUDE.md schema gap`)
         - candidate_sources (links to the existing 19K source stubs that would
           feed this priority, e.g., 6,234 OMAE papers for seakeeping/structures)
    6. Deprecation / consolidation pass:
       recommendations on the 19,166 source stubs:
         - which prefix buckets are best resolved by #2372 source-title aliasing
         - which by #2378 chunking
         - which by future deduplication (orphan stub identification)
       NOT a wiki edit — recommendations only.
    7. Open questions section (mirrors Risks & Open Questions in this plan).

test_audit_artifact:
    assert path exists at docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md
    parse markdown
    assert table_A row count == 6 (5 subdirs + root)
    assert table_B row count == 4 (articles, assets, papers, standards)
    assert table_C row count >= 8 (top filename-prefix buckets)
    assert structural-gap table includes a row for wiki/standards/ flagged "missing"
    assert sub-discipline coverage matrix has at least 8 rows aligned to ITTC families
    assert prioritized backfill list length in [5,8]
    assert each priority entry has fields {title, target_path, priority, rationale, candidate_sources}
    assert each priority entry's rationale matches at least one anchor:
        - ITTC procedure family regex (`7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`)
        - literal SNAME Offshore Section reference (`SNAME Offshore Section`)
        - literal citation-contract / citation contract / would cite
        - literal `CLAUDE.md schema gap`
    assert each cited file_count matches a live `find` result within absolute ±5 files tolerance
        (5 files at 19K scale = 0.026% — sufficiently tight to catch deletions, generous enough
         to absorb in-flight ingest drift; W1-C used ±2 at 520-file scale = 0.4%, equivalent posture)
    assert no file under knowledge/wikis/marine-engineering/wiki/ is modified by this plan's commit
        (`git diff --name-only $(git merge-base HEAD origin/main) -- knowledge/wikis/marine-engineering/` empty)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create (or reuse) | `docs/audits/` | top-level audit-artifact directory; will be co-created by W1-C plan #2588 (#2588 plan declares it as MISSING-this-plan-creates); W4-C reuses if extant, or creates if W1-C lands later |
| Create | `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` | the audit report deliverable |
| Create | `tests/knowledge/test_marine_engineering_audit_artifact.py` | TDD test asserting audit file exists, has required tables, ≥5 priority entries with ITTC/SNAME-anchored rationales |
| Update | `docs/plans/README.md` | add this plan to the index |

NO modifications to `knowledge/wikis/marine-engineering/**` of any kind. This plan is audit-only.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_audit_file_exists` | the deliverable file is present | `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` | `Path(...).exists() is True` |
| `test_audit_has_distribution_table_A` | wiki-distribution table is complete | parsed markdown | exactly 6 rows (comparisons, concepts, entities, sources, visualizations, root) with columns {subdir, file_count, file_count_share_pct, dominant_filename_pattern, content_type} |
| `test_audit_has_distribution_table_B` | raw-distribution table is complete | parsed markdown | exactly 4 rows (articles, assets, papers, standards) |
| `test_audit_has_distribution_table_C` | source-prefix bucket table has actionable depth | parsed markdown | row count ≥ 8, columns include {prefix_bucket, file_count, share_of_sources_pct, source_collection} |
| `test_audit_structural_gap_includes_standards_dir` | structural-gap table flags missing standards/ | parsed markdown | a row exists with `expected_path_per_CLAUDE_md` matching `wiki/standards/` and `actual_state` matching `missing` |
| `test_audit_subdiscipline_matrix_min_rows` | ITTC-aligned sub-discipline matrix has ≥8 rows | parsed markdown | row count ≥ 8 |
| `test_audit_priority_list_size` | prioritized backfill is 5–8 entries | parsed markdown | `5 <= len(priority_entries) <= 8` |
| `test_audit_priority_entry_schema` | each entry has required fields | parsed markdown | each entry has `title`, `target_path`, `priority` ∈ {P1,P2,P3}, `rationale`, `candidate_sources` |
| `test_audit_rationales_cite_required_anchors` | each rationale references a verifiable anchor | parsed markdown rationale strings | each rationale matches at least one of: ITTC procedure regex `7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`, literal `SNAME Offshore Section`, literal `citation-contract` / `citation contract` / `would cite`, or literal `CLAUDE.md schema gap` |
| `test_audit_file_counts_verifiable` | cited counts match live `find` | `find knowledge/wikis/marine-engineering/wiki/<sub> -type f -name "*.md"` | every cited count within absolute ±5 files of live count |
| `test_audit_no_wiki_writes` | this plan does not modify the wiki | `git diff --name-only $(git merge-base HEAD origin/main) -- knowledge/wikis/marine-engineering/` | empty |

---

## Acceptance Criteria

- [ ] All audit-artifact tests pass: `uv run pytest tests/knowledge/test_marine_engineering_audit_artifact.py -v`
- [ ] No regression: `uv run pytest tests/knowledge/` passes
- [ ] Distribution tables A+B+C cover every top-level wiki subdir of `marine-engineering`, every raw subdir, and the top ≥8 sources/-prefix buckets identified in this plan's evidence section.
- [ ] Structural-gap table explicitly flags `wiki/standards/` as schema-declared-but-missing.
- [ ] Sub-discipline coverage matrix has ≥8 rows aligned to ITTC sub-disciplines (Seakeeping, Manoeuvring, Stability-in-Waves, Resistance-Propulsion, Ocean-Engineering subdivisions, CFD/Numerical, Ice, Metocean) with current concept/entity counts and gap-severity per row.
- [ ] Prioritized backfill list contains 5–8 entries, each mapping to a single follow-up issue path placeholder (e.g., `docs/plans/<future-date>-issue-<NNNN>-<slug>.md`).
- [ ] Each priority entry's rationale references one of: (a) ITTC procedure family (regex `7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`), (b) literal `SNAME Offshore Section`, (c) citation-contract intent (literal `citation-contract` / `citation contract` / `would cite`), (d) literal `CLAUDE.md schema gap`. Enforced by `test_audit_rationales_cite_required_anchors`.
- [ ] Deprecation/consolidation section names ≥3 actions on the 19,166 source stubs (mapping to #2372 aliasing, #2378 chunking, future-deduplication, etc.).
- [ ] No file under `knowledge/wikis/marine-engineering/` is created or modified by this plan's execution commit.
- [ ] Review artifacts posted to `scripts/review/results/`.
- [ ] Plan-level outcome (audit report) will be the single input for a future child-issue wave; no child issues will be opened by this plan.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | TBD | pending |
| Codex | TBD | pending; codex-cli 0.124.0 stdin-hang regression (#2479) may force fallback |
| Gemini | TBD | pending; sandbox overlay-blindness risk (per memory `feedback_gemini_sandbox_overlay_blindness`) |

**Overall result:** TBD — plan is in `draft`; review fan-out runs after this draft is committed.

**Revisions made based on review:** N/A — none yet.

**Provenance:** TBD after fan-out.

---

## Risks and Open Questions

- **Risk (subdir false-mismatch):** mapping the 19,166 source stubs to ITTC sub-disciplines via filename heuristics will misclassify a non-trivial fraction (conference papers span multiple disciplines and filename like `omae2008-57873` carries no domain signal). Mitigation: priority rationale must cite an ITTC procedure number or SNAME literal — not a filename count alone. Enforced by `test_audit_rationales_cite_required_anchors`.
- **Risk (depth-of-content blindness):** a single curated 4-page concept like `long-period-swell-resonance.md` outweighs hundreds of empty source stubs in actual knowledge value; pure file-count distribution underweights this. Mitigation: gap audit must distinguish *curated* counts (entities + concepts + comparisons = 30) from *stub* counts (sources = 19,166) and only treat curated counts as the meaningful denominator for sub-discipline coverage.
- **Risk (sample-bias from giant subdir):** the OMAE-32% / OTC-27% / Offshore-Symposium-8.5% sources distribution is itself a *publication-venue* bias, not a *discipline* bias; OMAE alone covers seakeeping + manoeuvring + structures + offshore-engineering. Filename-prefix buckets will not surface discipline-mix without paper-level sampling. Mitigation: audit explicitly disclaims "venue ≠ discipline" and uses ITTC families as the discipline taxonomy, not venue prefixes.
- **Risk (drift):** the 19,166 sources/ count is the result of an in-flight ingest pipeline; if `wiki-ingest-cron.sh` fires between this plan's draft and execution, counts will move. The TDD test uses ±5 files absolute (≈0.026% at 19K scale, equivalent rigor to W1-C's ±2 at 520-file scale). If drift exceeds tolerance, audit re-run is required.
- **Risk (taxonomy attribution):** ITTC procedures evolve; citing a specific procedure number that has been renumbered would break the rationale anchor. Mitigation: cite ITTC sub-discipline *family* (e.g., `7.5-02-07` covers Ocean Engineering), not a fully qualified leaf number where revisions are frequent. Alternative literal anchor `SNAME Offshore Section` is independent of ITTC and serves as a fallback.
- **Risk (#2522 dependency inversion):** #2522 (CSA Z276 promotion) targets `wiki/standards/` which does not exist; if this audit is reviewed before #2522, the priority list must surface the missing-directory finding ahead of any standards-content priority. Mitigation: P1 priority is explicitly "create `wiki/standards/` directory and seed with TEMPLATE.md" — a structural action, not a content action.
- **Open:** Should the audit propose a deprecation pass on the 19,166 source stubs? **Proposed default: YES, recommendation-only.** The audit will name buckets best resolved by #2372 (source-title aliasing) vs #2378 (chunking) vs future-deduplication; it will NOT recommend deletions in this audit, only consolidation sequencing. Final classification happens at child-issue time.
- **Open:** Should the priority list include cross-domain concepts that overlap with `naval-architecture` (e.g., hydrostatics, stability) or `engineering` (mooring/riser fatigue physics already in `engineering/wiki/concepts/`)? Flag for user during approval. Current default: yes, but mark each cross-domain entry with a `cross_links` annotation rather than duplicating content.
- **Open:** Should the audit's output be re-run automatically once `#2392`'s `detect_wiki_gaps.py` ships, to validate the script's output against this manual baseline? **Proposed: YES** — same posture as W1-C; out of scope for this plan, captured as a follow-up.

---

## Complexity: T2

**T2** — single new audit deliverable file plus a single TDD test file plus a docs-index update; no production-code modifications, no wiki edits. Substantive work is the ITTC-anchored sub-discipline coverage matrix and the priority-list scoping against curated-vs-stub asymmetry. Heavier than W1-C only in raw file-count handled (19,199 vs 626) and in the addition of an external-taxonomy mapping step; structural shape is identical.
