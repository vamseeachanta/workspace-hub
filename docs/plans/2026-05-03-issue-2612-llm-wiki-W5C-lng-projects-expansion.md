# Plan for W5-C: feat(llm-wiki): lng-projects wiki topical expansion — 6-8 concept pages (W5-C)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2612
> **Review artifacts:** scripts/review/results/2026-05-03-plan-W5C-lng-projects-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

The lng-projects wiki target tree at `knowledge/wikis/lng-projects/wiki/` currently contains 6 markdown files (plus the domain `CLAUDE.md`). Per `find knowledge/wikis/lng-projects -type f -name "*.md" | sort`:

```
knowledge/wikis/lng-projects/CLAUDE.md
knowledge/wikis/lng-projects/wiki/index.md
knowledge/wikis/lng-projects/wiki/log.md
knowledge/wikis/lng-projects/wiki/overview.md
knowledge/wikis/lng-projects/wiki/sources/elements-acma-projects-31522-woodfibre.md
knowledge/wikis/lng-projects/wiki/sources/elements-doris-62092-sesa.md
knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md
```

Inventory readout:

- 0 concept pages (`wiki/concepts/` directory does not yet exist on disk).
- 0 entity pages (`wiki/entities/` does not yet exist on disk).
- 0 standards pages (`wiki/standards/` does not yet exist on disk; see Open Question on standards routing sanction).
- 3 source pages (the 2 Elements batch-ingest catalogues from 2026-04-28, plus the Woodfibre corpus pointer from 2026-05-01 #2544).
- `wiki/index.md` lists `_No concept pages yet._` and `_No entity pages yet._`; `page_count: 3`, `source_count: 3`.
- `wiki/overview.md` is the bare placeholder ("This page serves as a placeholder. Replace with LLM-maintained content.") emitted by `llm-wiki init` on 2026-04-28.

This plan will introduce the first concept directory under this wiki and bump `page_count` 3 → ≥9 (the new concept pages plus retained existing pages, excluding `index.md` itself per the W1-D regenerator-quirk note).

### Standards

Standards-page production for lng-projects is **not yet bootstrapped**. The wiki has no `wiki/standards/` directory. Per `.claude/rules/calc-citation-contract.md`, a calc module emitting an LNG-derived constant would currently have nowhere to resolve a citation. **No standards page promotion is in this plan's scope** — concept pages will reference standards bodies (NFPA, EN, IGC code, SIGTTO, OCIMF, IACS, ABS, DNV, IMO) by NAME with a stable URL or a sibling source-page link, leaving downstream codification to follow-up issues.

| Standard | Status | Source |
|---|---|---|
| NFPA 59A (Production, Storage, Handling of LNG) | referenced (no codified standards page) | https://www.nfpa.org/codes-and-standards |
| EN 1473 (Installation and equipment for LNG — onshore design) | referenced (URL-cited) | https://www.cencenelec.eu/ |
| IMO IGC Code (gas carriers, sea transport) | referenced (URL-cited) | https://www.imo.org/en/OurWork/Safety/Pages/IGC-Code.aspx |
| SIGTTO guidance (LNG/LPG terminal operations) | referenced (URL-cited) | https://www.sigtto.org/publications |
| OCIMF MEG4 / SIRE-related guidance | referenced (URL-cited) | https://www.ocimf.org/ |
| EEMUA Pub. 147 / 159 (LNG storage tanks, in-service inspection) | referenced (URL-cited) | https://www.eemua.org/ |
| IACS class rules (gas-carrier / floating LNG) | referenced (URL-cited) | https://iacs.org.uk/ |

### LLM Wiki pages consulted

- `knowledge/wikis/lng-projects/CLAUDE.md` — frontmatter schema (title, tags, added, last_updated mandatory; sources/cross_links recommended); standards-page extra fields (`code_id`, `publisher`, `revision`) reserved for future standards routing; lines 13–24 declare the canonical directory layout.
- `knowledge/wikis/lng-projects/wiki/index.md` — confirms entity/concept tables empty and source count = 3.
- `knowledge/wikis/lng-projects/wiki/sources/elements-doris-62092-sesa.md` — SESA FLNG Terminal source page (metadata-only, frontmatter-only ingest from 2026-04-28).
- `knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md` — explicit metadata-only pointer; no abstracts or full-text per #2540/#2482 deny-list. The body line "This page does **not** authorize or contain document abstracts, direct quotes, tables, figures, or full-text extraction" sets the boundary that this plan must not cross.
- Sibling: `knowledge/wikis/marine-engineering/wiki/` — partial overlap on cryogenic / process-safety topics; this plan will cross-link rather than duplicate (boundary-page pattern from naval-arch #2589 W1-D).
- Sibling: `knowledge/wikis/naval-architecture/wiki/concepts/ship-structures.md` — gas-carrier hull-girder cross-link target if relevant; not duplicated here.

### Documents consulted

- `docs/plans/_template-issue-plan.md` — followed structure verbatim; retrieval contract requires ≥3 distinct sources with embedded evidence.
- `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md` — direct precedent (W1-D shape) — adopted: per-page authoring contract, frontmatter spec, ≥2 see_also requirement, ≤400-word cap, standards-NAME-only discipline (no enumerated thresholds/clauses), reservation-overlap regex tests, redundant-content tests, log entry append, seed-file source-of-truth pattern (where applicable).
- `.claude/rules/calc-citation-contract.md` — concept pages do not emit `Citation` instances (citations are calc-module artifacts); standards-page promotion is deferred to a follow-up after user sanction (Open Question).
- `.claude/rules/coding-style.md` — single-site edits only; verify each `index.md` insertion does not delete adjacent rows.
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` routing principle is sanctioned **only** for the {marine-engineering, engineering, naval-architecture} trio; lng-projects is **NOT** on that list (verified 2026-05-03 — see Open Question). This plan stays inside `wiki/concepts/` and `wiki/entities/` only.
- #2540 — CLOSED, "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent-wave epic; this plan is a W5 sibling under that wave focused on lng-projects topical concepts.
- #2541 — OPEN (`status:plan-review`), "feat(llm-wiki): plan curated SESA LNG corpus extraction from Elements" — **SOURCE-PAGE work**; reserves SESA-specific extraction. This plan is concept-only and will not draft any SESA-specific source content.
- #2544 — CLOSED (`status:plan-approved`), "feat(llm-wiki): scout Woodfibre LNG corpus for bounded extraction candidates" — produced the Woodfibre corpus pointer. This plan does not author or modify Woodfibre source-pages.
- #2589 — OPEN (`status:plan-review`), "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — review-shape precedent for this plan.
- /mnt/ace inventory awareness only: `/mnt/ace/doris/62092_sesa/{000 Client Supplied,001 Transfer,002 Project Filing,_from_elements,data,analysis,999 Work Space}` confirms SESA raw material is locally accessible — out of scope for this concept-only plan, citable only by reference.
- WebSearch — LNG project lifecycle phases — confirms canonical phases: Conceptualization/Pre-FEED → FEED (12-18 months) → EPC → Commissioning/Startup → Operations → (Decommissioning) (sources: whatispiping.com, epcintel.com, energy.gov Global LNG Fundamentals, 2b1stconsulting.com, engimates.com).
- WebSearch — FLNG vs onshore LNG — confirms canonical comparison: FLNG 1.0-2.0 mtpa vs onshore 3.0-8.0 mtpa; FLNG 3-5 yr vs onshore 5-7 yr build; FLNG ~25% footprint; relocatable vs permanent (sources: en.wikipedia.org/wiki/Floating_liquefied_natural_gas, sciencedirect.com Floating LNG overview, oxfordenergy.org NG149 Floating LNG Update).

### Gaps identified

Coverage matrix vs. canonical LNG-project topic skeleton (after excluding #2541 SESA-specific and #2544 Woodfibre-specific source-page reservations):

| Canonical topic | Current wiki status | #2541/#2544 reserved? | Action |
|---|---|---|---|
| LNG project lifecycle (pre-FEED → decommissioning) | gap | no | **NEW** `concepts/lng-project-lifecycle.md` |
| Liquefaction technology families (APC AP-X, Shell DMR, ConocoPhillips Optimized Cascade, Air Products MR, Linde MFC) | gap | no | **NEW** `concepts/lng-liquefaction-processes.md` |
| LNG storage tanks (full-containment, in-ground, FLNG storage) | gap | no | **NEW** `concepts/lng-storage-tanks.md` |
| LNG marine loading / jetty / ship-to-ship / FSRU regas | gap | no | **NEW** `concepts/lng-marine-transfer-systems.md` |
| LNG process safety (vapor cloud, BOG management, rollover, pool fire) | gap | no | **NEW** `concepts/lng-process-safety.md` |
| LNG project shapes (onshore greenfield/brownfield, FLNG, FSRU, mid-scale, SS-LNG) | gap | no | **NEW** `concepts/lng-project-shapes.md` |
| LNG regulatory framework (NFPA 59A, EN 1473, IGC Code, SIGTTO, OCIMF) | gap (entity-style) | no | **NEW** `entities/lng-regulatory-framework.md` |
| Boil-off gas and reliquefaction concepts (cross-link target) | gap | no | **NEW** `concepts/lng-boil-off-gas-management.md` |
| SESA-specific FLNG terminal narrative | reserved | **YES — #2541** | **EXCLUDE** |
| Woodfibre-specific document abstracts/quotes | reserved | **YES — #2544** | **EXCLUDE** |

**Top-8 selected for this expansion** (foundational + cross-linkable, citable canonical references, raw source on /mnt/ace or stable URL, zero SESA/Woodfibre noun-phrase overlap):

1. `concepts/lng-project-lifecycle.md`
2. `concepts/lng-liquefaction-processes.md`
3. `concepts/lng-storage-tanks.md`
4. `concepts/lng-marine-transfer-systems.md`
5. `concepts/lng-process-safety.md`
6. `concepts/lng-project-shapes.md`
7. `concepts/lng-boil-off-gas-management.md`
8. `entities/lng-regulatory-framework.md`

(Decommissioning sub-page deferred to W6 to keep batch ≤ 8.)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):

- `#2540` — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent-wave epic, status:done.
- `#2541` — OPEN — "feat(llm-wiki): plan curated SESA LNG corpus extraction from Elements" — status:plan-review; SOURCE-PAGE scope, reserves SESA-specific extraction.
- `#2544` — CLOSED — "feat(llm-wiki): scout Woodfibre LNG corpus for bounded extraction candidates" — status:plan-approved; produced corpus-pointer (no abstracts).
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — status:plan-review; precedent shape.

**File existence** (`find … | sort` 2026-05-03):

- EXISTS: `knowledge/wikis/lng-projects/CLAUDE.md`
- EXISTS: `knowledge/wikis/lng-projects/wiki/index.md` (page_count=3, source_count=3, last_updated=2026-05-01)
- EXISTS: `knowledge/wikis/lng-projects/wiki/log.md`
- EXISTS: `knowledge/wikis/lng-projects/wiki/overview.md` (placeholder)
- EXISTS: `knowledge/wikis/lng-projects/wiki/sources/{elements-acma-projects-31522-woodfibre,elements-doris-62092-sesa,woodfibre-corpus-pointer}.md`
- MISSING (this plan creates): `wiki/concepts/lng-project-lifecycle.md`, `wiki/concepts/lng-liquefaction-processes.md`, `wiki/concepts/lng-storage-tanks.md`, `wiki/concepts/lng-marine-transfer-systems.md`, `wiki/concepts/lng-process-safety.md`, `wiki/concepts/lng-project-shapes.md`, `wiki/concepts/lng-boil-off-gas-management.md`, `wiki/entities/lng-regulatory-framework.md`
- MISSING (this plan creates): `tests/knowledge/test_lng_projects_expansion.py`
- MISSING (parent dir does not yet exist): `wiki/concepts/`, `wiki/entities/`

**Line excerpts** (from `knowledge/wikis/lng-projects/CLAUDE.md` lines 30–41 — frontmatter contract this plan must reproduce):

```
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | **required** | string | Page title |
| `tags` | **required** | list | Classification tags |
| `added` | **required** | date | ISO date when page was created (`YYYY-MM-DD`) |
| `last_updated` | **required** | date | ISO date of last modification (`YYYY-MM-DD`) |
| `sources` | recommended | list | Source documents referenced |
```

**SESA/Woodfibre reservation proof** (excerpt from `knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md`):

> "This page does **not** authorize or contain document abstracts, direct quotes, tables, figures, or full-text extraction."

This plan's selected topics avoid every SESA-specific and Woodfibre-specific noun-phrase. No new page will mention "SESA", "Woodfibre", "ACMA project 31522", "Doris project 62092", or any project-name-bound facts; standards-body NAMING and generic LNG-industry concepts only.

**Gap proofs** (`ls knowledge/wikis/lng-projects/wiki/concepts 2>&1`):

- "No such file or directory" — confirms `concepts/` directory does not exist; this plan creates it.

**Path-sanction flag (per memory `project_wiki_standards_path_decision.md`):**

- The `wiki/standards/<code-id>.md` routing principle is sanctioned only for {marine-engineering, engineering, naval-architecture}. lng-projects is **NOT** in that list.
- This plan does NOT add any `wiki/standards/` content. Standards bodies (NFPA, EN, IGC, SIGTTO, OCIMF, IACS) are NAMED in concept-page bodies with stable URLs only.
- Whether lng-projects should adopt `wiki/standards/` routing is captured under **Open Questions** below for explicit user sanction. **Do not** treat the existing #2471 sanction as covering lng-projects.

<!-- Source count: 11 distinct sources cited above —
  (1) wiki CLAUDE.md schema, (2) wiki index, (3) Elements SESA source page,
  (4) Woodfibre corpus pointer, (5) #2540, (6) #2541, (7) #2544, (8) #2589,
  (9) WebSearch lifecycle, (10) WebSearch FLNG, (11) /mnt/ace SESA inventory.
  Minimum 3 met; 11 actual. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2612-llm-wiki-W5C-lng-projects-expansion.md` |
| Tests | `tests/knowledge/test_lng_projects_expansion.py` |
| Implementation (8 wiki pages) | `knowledge/wikis/lng-projects/wiki/concepts/*.md` (7) + `entities/lng-regulatory-framework.md` (1) |
| Index update | `knowledge/wikis/lng-projects/wiki/index.md` |
| Log update | `knowledge/wikis/lng-projects/wiki/log.md` |
| Plan review — Claude | `scripts/review/results/2026-05-03-plan-W5C-lng-projects-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-03-plan-W5C-lng-projects-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-03-plan-W5C-lng-projects-gemini.md` |

---

## Deliverable

Eight new concept/entity pages will exist under `knowledge/wikis/lng-projects/wiki/`, each carrying `CLAUDE.md`-compliant frontmatter, ≥1 standards-body NAME-only cross-reference (NFPA / EN / IGC / SIGTTO / OCIMF / IACS / ABS / DNV / IMO), ≥2 `see_also` cross-links, and zero overlap with #2541 SESA-specific or #2544 Woodfibre-specific source-page deliverables — with `index.md` updated to surface every new page in its catalogue table.

---

## Pseudocode

```
# Per-page authoring contract (applies to all 8 new pages):
function author_lng_concept_page(slug, scope_summary):
    write frontmatter:
        title: human-readable
        tags: [lng-projects, sub-topic-tag, standards-tag-where-relevant]
        added: 2026-05-03
        last_updated: 2026-05-03
        sources: [<sibling source-page slug if applicable>]
        see_also: [≥2 sibling-page paths]
    section "Scope" — 1 paragraph stating what the page IS and what it is NOT (boundary page pattern from #2567/#2589)
    section "Key Concepts" — 5–10 bulleted definitions, each ≤1 line
    section "Standards / References" — ≥1 bullet NAMING NFPA|EN|IGC|SIGTTO|OCIMF|IACS|ABS|DNV|IMO with stable URL, but MUST NOT enumerate specific thresholds, formulas, or code clauses (those would belong on `wiki/standards/<code-id>.md` if/when path-sanction lands — see Open Question)
    section "Cross-References" — markdown links to ≥2 see_also targets
    forbid: extracted text from PDFs (#2482 deny-list)
    forbid: any reference to "SESA", "Woodfibre", "ACMA project 31522", "Doris project 62092", or any project-bound name (#2541/#2544 reservation)
    enforce: word count ≤ 400 per page (concept summary, not chapter copy)

function update_index(index_path, new_pages):
    create "Concepts" table with 7 new rows (alphabetical by title)
    create "Entities" table with 1 new row replacing the empty placeholder
    bump page_count from 3 → 9 in frontmatter
    leave source_count untouched (no new sources)

function append_log(log_path):
    append "[2026-05-03] expand | lng-projects W5-C — 8 concept/entity pages"
        - Pages added: <list>
        - Notes: covers LNG industry topical skeleton; excludes #2541/#2544 source-page reservations.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-project-lifecycle.md` | Pre-FEED → FEED → EPC → commissioning → operations → decommissioning phase taxonomy; NAMES industry sources (e.g. DOE Global LNG Fundamentals) without enumerating gate-criterion thresholds |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-liquefaction-processes.md` | Liquefaction technology families: APC AP-X, Shell DMR, ConocoPhillips Optimized Cascade, Air Products MR, Linde MFC — neutral overview, no licensor-bias |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-storage-tanks.md` | Full-containment, in-ground, membrane vs. self-supporting (Moss-type) — NAMES EN 1473 / API 625 / NFPA 59A without restating clause text |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-marine-transfer-systems.md` | Jetty design, marine loading arms, ship-to-ship transfer, FSRU regas, tandem mooring — cross-links to OCIMF MEG4 by NAME (not the recently authored OCIMF tandem mooring page in `knowledge/wikis/engineering/wiki/standards/`) |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-process-safety.md` | Vapor cloud explosion (VCE), pool fire, BLEVE, rollover risk — NAMES NFPA 59A / SIGTTO guidance without restating exclusion-zone formulas |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-project-shapes.md` | Onshore greenfield/brownfield, FLNG, FSRU, mid-scale modular, small-scale SS-LNG — capacity ranges as canonical (1.0–8.0 mtpa onshore, 1.0–2.0 mtpa FLNG per Oxford NG149) |
| Create | `knowledge/wikis/lng-projects/wiki/concepts/lng-boil-off-gas-management.md` | BOG generation, reliquefaction, vapor handling, BOG compressor sizing — NAMES SIGTTO BOG guidance; cross-links to `lng-storage-tanks.md` and `lng-marine-transfer-systems.md` |
| Create | `knowledge/wikis/lng-projects/wiki/entities/lng-regulatory-framework.md` | NFPA 59A, EN 1473, IGC Code (sea transport), SIGTTO, OCIMF, EEMUA 147/159, IACS gas-carrier rules — first entity page; one-paragraph publisher-and-scope per body |
| Modify | `knowledge/wikis/lng-projects/wiki/index.md` | Add 7 concept rows + 1 entity row; bump `page_count` 3 → 9 |
| Modify | `knowledge/wikis/lng-projects/wiki/log.md` | Append `[2026-05-03] expand | lng-projects W5-C — 8 concept/entity pages` entry |
| Create | `tests/knowledge/test_lng_projects_expansion.py` | TDD frontmatter / cross-link / standards-citation / index-resolves / no-SESA-Woodfibre-overlap / see-also-resolves / word-count checks |
| Update | `docs/plans/README.md` | Add this plan to plan index |

Note: no seed-file (`knowledge/seeds/`) is used for lng-projects (verified 2026-05-03: only `mooring-failures-lng-terminals.yaml` exists, scope is mooring-failure events not topical-page generation). `index.md` is hand-edited here — flagged as Risk below.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_eight_pages_exist` | Each of the 8 new files is on disk | path list | all 8 `Path.exists()` is True |
| `test_frontmatter_required_fields` | Every new page has `title`, `tags`, `added`, `last_updated` per `CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_frontmatter_see_also_min_two` | Each page lists ≥2 entries in `see_also` | parse YAML | `len(see_also) >= 2` |
| `test_at_least_one_standards_body_named` | Page body NAMES ≥1 of NFPA / EN / IGC / SIGTTO / OCIMF / IACS / ABS / DNV / IMO | regex search of body text | match found per page |
| `test_no_sesa_or_woodfibre_noun_phrases` | Body contains zero #2541/#2544 reserved phrases in the 8 NEW pages | regex `r'\b(SESA\|Woodfibre\|ACMA[- ]?project[- ]?31522\|Doris[- ]?project[- ]?62092)\b'` (case-insensitive) | zero matches in new pages |
| `test_word_count_under_400` | Concept summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts + Entities tables resolves | walk markdown links | 100% resolve |
| `test_see_also_paths_resolve` | Every `see_also` entry in each new page's frontmatter points to a real file on disk | parse YAML, `Path.exists()` per entry | 100% resolve |
| `test_index_page_count_bumped` | `index.md` frontmatter `page_count` updated to ≥9 | parse YAML | `page_count >= 9` |
| `test_log_entry_appended` | `log.md` contains a 2026-05-03 expand entry | grep | match present |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (long paragraphs > 80 words, "Page N of M" stamps) | heuristic | no flagged paragraphs |
| `test_no_standards_directory_created` | No `wiki/standards/` directory will be added by this plan (path-sanction guard) | `Path('knowledge/wikis/lng-projects/wiki/standards').exists()` | False (until separate sanction lands) |
| `test_no_thresholds_or_clauses_enumerated` | Concept bodies do not enumerate specific NFPA / EN / IGC clause numbers or numeric thresholds (heuristic regex for clause-number patterns like `\bNFPA\s+59A\s+\d+\.\d+`, `\bEN\s+1473\s+§`, `\bIGC\s+Code\s+\d+\.\d+`) | regex search | zero matches |

---

## Acceptance Criteria

- [ ] All 8 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-03`, `last_updated=2026-05-03`).
- [ ] Each new page will NAME ≥1 standards body (NFPA / EN / IGC / SIGTTO / OCIMF / IACS / ABS / DNV / IMO) with stable URL or sibling source-page link, but MUST NOT enumerate specific thresholds, formulas, or code clauses (those would belong on `wiki/standards/<code-id>.md` if/when path-sanction is granted).
- [ ] Each new page will list ≥2 `see_also` cross-links, and every entry will resolve to a real file on disk.
- [ ] No new page will reference any noun-phrase reserved by #2541 (SESA / Doris project 62092) or #2544 (Woodfibre / ACMA project 31522).
- [ ] No new page will duplicate scope of an existing source page in `wiki/sources/` — concept pages are project-agnostic, source pages are project-bound.
- [ ] `index.md` Concepts table will list 7 new rows (alphabetical); Entities table will list 1 new row replacing the empty placeholder.
- [ ] `index.md` frontmatter `page_count` will read ≥9.
- [ ] `log.md` will carry a `[2026-05-03] expand | lng-projects W5-C` entry.
- [ ] `tests/knowledge/test_lng_projects_expansion.py` will pass: `uv run pytest tests/knowledge/test_lng_projects_expansion.py -v`.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Each new page will be ≤400 words (concept-summary discipline per #2482 deny-list).
- [ ] No `wiki/standards/` directory will be created (path-sanction guard).
- [ ] Review artifacts will be posted under `scripts/review/results/2026-05-03-plan-W5C-lng-projects-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

<!-- To be filled after adversarial review pass. Plan currently in draft. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk: overlap with #2541 SESA extraction.** #2541 is a SOURCE-PAGE plan (project-bound facts about SESA FLNG terminal). This concept-only plan must not draft SESA narrative. Tests will hard-fail on the reserved-phrase regex `\bSESA\b`.
- **Risk: overlap with #2544 Woodfibre.** Same shape as above. Tests guard with `\bWoodfibre\b` and corpus-pointer noun-phrases.
- **Risk: technology-vendor-naming bias toward Western suppliers.** APC (Air Products), Shell, ConocoPhillips, Linde dominate the Western canonical set. Eastern licensors (e.g. Wison, CSSC FLNG) and Russian designs may be under-represented in `lng-liquefaction-processes.md`. Mitigation: concept page will NAME at least one non-Western FLNG hull-builder/licensor for completeness with a stable URL.
- **Risk: process-safety ambiguity (deterministic vs. probabilistic safety distance).** NFPA 59A and EN 1473 use different exclusion-zone methodologies. The `lng-process-safety.md` page will NAME both standards but will NOT enumerate specific zone formulas — that scope belongs to a future `wiki/standards/` page (Open Question).
- **Risk: index regenerator quirk.** The naval-arch wiki uses an `llm-wiki` index regenerator driven by a `knowledge/seeds/<domain>-resources.yaml` file (per #2589 W1-D review m7). lng-projects has **no equivalent seed file** (verified). This plan hand-edits `index.md`. If a future `llm-wiki` regenerate run later overwrites the index, the catalogue will need re-emission. Mitigation: log entry references this plan path so a regenerator can be backfilled.
- **Risk: terminology drift.** "LNG terminal" (often = receiving/regas) vs "LNG plant" (often = liquefaction) vs "LNG facility" (catch-all). `lng-project-shapes.md` will define the boundary explicitly to prevent silent topic-collision.
- **Risk: false-gap from broader MARLA/maritime-law scope.** LNG involves IGC Code (sea transport), bunkering rules, port-state control. This plan keeps the regulatory entity page LNG-project-scoped (NFPA + EN + SIGTTO + OCIMF + IACS gas-carrier rules); maritime-law-domain expansion (e.g. transit clearance, port liability) is reserved for the maritime-law wiki.

- **Open: should lng-projects adopt `wiki/standards/<code-id>.md` routing?** Per memory `project_wiki_standards_path_decision.md`, the principle is currently sanctioned only for {marine-engineering, engineering, naval-architecture}. lng-projects is not on the list. A natural fit exists (NFPA 59A, EN 1473, IGC Code are heavily-cited industry standards) but routing requires **separate user sanction**. This plan deliberately stays inside `wiki/concepts/` and `wiki/entities/`; no `wiki/standards/` content is added.
- **Open: should `concepts/lng-decommissioning.md` ship as a 9th page in this batch or defer to W6?** Current plan defers to W6 to keep the batch ≤ 8 and to avoid forcing topic-set growth before the first batch lands.
- **Open: should `wiki/overview.md` (currently a placeholder) be replaced as part of this batch?** Current plan leaves it as-is; replacement is an obvious follow-up but is out of scope here (concept pages take precedence).

---

## Complexity: T2

**T2** — 8 new wiki pages + 2 modified registry files (`index.md`, `log.md`) + 1 new test module. Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in cross-link discipline, SESA/Woodfibre noun-phrase hygiene, and the path-sanction boundary against `wiki/standards/`. Not T3 because there is no new module / no calc / no migration / no schema change.
