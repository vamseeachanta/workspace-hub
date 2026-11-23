# Plan for LLM-Wiki Completeness W3-B: Bounded ISO 19900-Series Offshore-Structures Summary Promotion

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** _not yet filed — this plan file is the deliverable; issue creation is downstream of plan-review (per `feedback_never_offer_to_self_label_plan_approved.md`, no self-approval, no pre-authorization)_
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Sibling precedent (API, W1-A):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) — bounded standards summary promotion pattern this W3-B plan inherits structurally
> **Sibling precedent (DNV, W2-A):** [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) — same bounded-summary contract, applied to DNV
> **Sibling precedent (OCIMF Tandem):** [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) (CLOSED) — bounded preview test pattern (`tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py`) that this plan extends
> **Audit dependency surfaced (W1-C):** [#2588](https://github.com/vamseeachanta/workspace-hub/issues/2588) — engineering wiki gap audit; r1 review's MAJOR-3 fix replaced an unverifiable "SUT taxonomy" with the **ISO 19900-series taxonomy** as the audit's verifiable priority anchor. Promoting the 19900-series summary pages directly strengthens that audit's grounding (the audit cites part numbers; this plan creates the pages those part numbers resolve to).
> **Path sanction (engineering-standards):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for engineering-standards domain). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). In-progress organizational precedent: W1-A plan #2586 (API) and W2-A plan #2590 (DNV). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision **for CSA-Z276 specifically** (verified per memory `project_wiki_standards_path_decision.md`); it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple, not as ISO path authority.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`)
> **Calc-citation pilot:** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors prose-level pilot
> **Review artifact:** `scripts/review/results/2026-05-02-plan-W3B-claude-internal.md` (draft; single-author Claude review acceptable per memory `feedback_permission_gate_blocks_cross_review.md` when Codex/Gemini are unavailable per `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_gemini_sandbox_overlay_blindness.md`)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). This is the downstream consumer that will resolve the wiki pages this plan will create.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/registry.py` — companion resolver. The single live `Citation(...)` constructor on disk lives here (line 52) and currently targets `dnv-os-e301` only.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/component_database.py:17` — module-level docstring already cites `ISO 19901-7: Stationkeeping systems for floating offshore structures`. Highest-frequency 19900-series consumer.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/environment.py:233` — comment `Reference: API RP 2SK Section 6, ISO 19901-7.` confirms 19901-7 is a citation target shared with the W1-A api-rp-2sk page.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/infrastructure/templates/plate_capacity_template.json:397` — citation string `"ISO 19902, Petroleum and natural gas industries - Fixed steel offshore structures"`. Confirms the 19902 fixed-steel page is wired to a real downstream consumer.
- Gap: no engineering-standards wiki page exists for any ISO 19900-series code. The `wiki/standards/` directory currently contains exactly one file: `api-17e.md` (verified 2026-05-02 via `ls`). The W1-A (API, 10 new pages) and W2-A (DNV, 10 new pages) plans are still in `plan-review` — neither has landed yet, so any "after W1-A and W2-A merge, count = 21" arithmetic is forward-looking, not present-tense.
- Gap: no overlap risk in `engineering/wiki/standards/` for ISO 19900-series — verified via the W1-C plan's audit (`engineering/wiki/standards/` contains 9 files: 5 DNV + 1 API + 2 OCIMF + 1 TEMPLATE — **no ISO entries at all**). This is the cleanest cross-wiki collision profile of any of the W1/W2/W3 promotion plans.

### Standards

| Standard | Status | Source |
|---|---|---|
| ISO 19900:2019 — Petroleum and natural gas industries — General requirements for offshore structures | gap (not on disk under `/mnt/ace/O&G-Standards/ISO/`; current 2019 edition referenced via publisher metadata only) | <https://www.iso.org/standard/69761.html> (current revision 2019); ledger row absent — introduced by this plan |
| ISO 19901-1:2015 — Specific requirements for offshore structures — Part 1: Metocean design and operating considerations | gap (raw on disk: `ISO_19901-1_FDIS_SUBMITTED_2_Metocean_Conditions.pdf` and `ISO-DIS-19901-1_(1)_Metocean.pdf` — both pre-publication drafts; current 2015 edition not on disk) | `/mnt/ace/O&G-Standards/ISO/ISO_19901-1_FDIS_SUBMITTED_2_Metocean_Conditions.pdf`; current revision per ISO catalog |
| ISO 19901-2:2017 — Part 2: Seismic design procedures and criteria | gap (raw on disk: `ISO_19901-2_E_Submitted_for_FDIS_Seismic_Design.pdf` — pre-publication FDIS; current 2017 edition not on disk) | `/mnt/ace/O&G-Standards/ISO/ISO_19901-2_E_Submitted_for_FDIS_Seismic_Design.pdf` |
| ISO 19901-4:2016 — Part 4: Geotechnical and foundation design considerations | gap (raw on disk: `ISO_DIS_19901-4_responses.pdf` — DIS-stage responses doc; current 2016 edition not on disk) | `/mnt/ace/O&G-Standards/ISO/ISO_DIS_19901-4_responses.pdf`; <https://www.iso.org/standard/61144.html> |
| ISO 19901-7:2013 — Part 7: Stationkeeping systems for floating offshore structures and mobile offshore units | gap (raw on disk: `ISO_19901-7_DIS_04-02-13_Stationkeeping.pdf` — DIS-stage; current 2013 edition not on disk; **next revision in flight as ISO/FDIS 19901-7 expected ~2026 per <https://www.iso.org/standard/59298.html>**) | `/mnt/ace/O&G-Standards/ISO/ISO_19901-7_DIS_04-02-13_Stationkeeping.pdf` |
| ISO 19902:2019 — Fixed steel offshore structures | gap (raw on disk: only `19902_Annex_C_DIS.pdf` and `19902_Clause_26_DIS.pdf` — partial DIS extracts; current 2019 edition not on disk) | `/mnt/ace/O&G-Standards/ISO/19902_Annex_C_DIS.pdf`; `/mnt/ace/O&G-Standards/ISO/19902_Clause_26_DIS.pdf` |
| ISO 19903:2019 — Fixed concrete offshore structures | gap (no raw on disk; current 2019 edition referenced via publisher metadata only) | publisher catalog pointer only; ledger row absent — introduced by this plan |
| ISO 19904-1:2019 — Floating offshore structures — Part 1: Ship-shaped, semi-submersible, spar and shallow-draught cylindrical structures | gap (no raw on disk; current 2019 edition referenced via publisher metadata only) | <https://www.iso.org/standard/63801.html> |
| ISO 19905-1:2023 — Site-specific assessment of mobile offshore units — Part 1: Jack-ups: Elevated at a site (3rd ed) | gap (raw on disk: multiple draft/FDIS/CD versions — `ISO_FDIS_19905-1_(E)_2011-07-07.pdf`, `ISO_FDIS_19905-1_(E)-2nd-FDIS-2012-03-15.pdf`, `ISO_DIS_19905-1_(E).pdf`, `19905-1_(E)_CD_G-2007-03-20.doc`, `ISO_FDIS_19905_1.pdf`, plus 2012-vs-FDIS-2015 comparison docx — current 2023 edition not on disk) | `/mnt/ace/O&G-Standards/ISO/ISO_FDIS_19905-1_(E)-2nd-FDIS-2012-03-15.pdf` |

**Defer (Open Questions):** ISO 19901-3 (topsides — raw `ISO_CD_19901-3_Topsides.pdf` + `ISO_19901-3_markup.pdf` on disk), ISO 19901-5 (weight control), ISO 19901-6 (marine operations), ISO 19905-2 (technical report — multiple drafts on disk), ISO 19906 (arctic — raw `ISO_FDIS_19906_(E).pdf` on disk), ISO 19901-9 (reliability) — see Open Questions.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards code page; sets metadata-only frontmatter style this plan replicates eight times.
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5` (the `page_count: 5` field tracks `source_count` and is itself stale; live `find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` returns **9** markdown files — 1 index + 5 sources + 1 standards (`api-17e.md`) + 2 other top-level pages). Per the W1-A and W2-A plans both still in plan-review, `page_count` arithmetic must be computed from **present-tense live** state, not assumed-merged state. Present-tense floor before this plan: 9 (live count). After this plan ships standalone: 9 + 9 new ISO pages = 18 (the implementation step's index update MUST also correct the stale `page_count: 5` value to the live count). If W1-A and W2-A both land first, recompute live at write-time; the implementation step MUST recompute against live state at write-time, not hardcode.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply. The schema's example values (`csa-z276`, `api-17j`, `ocimf-meg4`) confirm lowercase-kebab convention.
- `knowledge/wikis/engineering/wiki/standards/` — verified 2026-05-02 via the W1-C audit findings: contains 9 files (DNV ×5, API ×1, OCIMF ×2, TEMPLATE ×1) — **NO ISO 19900-series page exists in the engineering wiki either**. This plan is the first ISO 19900-series promotion across BOTH wiki domains; cross-wiki collision risk is zero.

### Documents consulted

- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — direct precedent (API, 10 codes). This W3-B plan inherits W1-A's bounded-preview frontmatter, no-raw-text test, and citation-resolvability test patterns. **Differences from W1-A**: ISO-specific revision-numbering convention is `<edition-year>` simple (e.g., `2019`, `2013`, `2023`) — no per-edition addendum. ISO part-numbering convention adds a hyphenated suffix (`19901-7`); the `code_id` MUST preserve that hyphen (`iso-19901-7`, not `iso-19901_7` or `iso19901-7`). **Casing matches W1-A** (lowercase-kebab).
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — direct precedent (DNV, 10 codes). Inherits the cross-wiki uniqueness AC, the ledger-alignment AC, the body-shape whitelist test, and the file-reading citation-resolver test (P2-5 fix from r1).
- `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md` — the audit that **made the 19900-series taxonomy a verifiable anchor**. The W1-C r1 review MAJOR-3 fix replaced an unverifiable "SUT taxonomy" with the explicit ISO 19900-series part list. This W3-B plan creates the pages those part numbers resolve to, closing the audit's "rationales must cite a verifiable anchor" loop.
- `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — bounded preview pattern (#2227 closure); the no-raw-text-bleed test pattern at `tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py` is the model this plan extends.
- `data/document-index/standards-transfer-ledger.yaml` — present-tense state: contains zero rows for any ISO 19900-series code (verified via `grep -i "ISO 199"` returning only one prose-context match in another row's `notes` field). This plan introduces 8 new ledger rows.
- `.claude/rules/calc-citation-contract.md` — the citation contract this plan exists to satisfy. After this plan lands, downstream calc modules in `digitalmodel/src/digitalmodel/marine_ops/...` and `digitalmodel/src/digitalmodel/orcaflex/...` can resolve `Citation(code_id="iso-19901-7", ...)` and `Citation(code_id="iso-19902", ...)` against the new pages.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). Path sanction for ISO derives from `engineering-standards/CLAUDE.md` schema + `.claude/rules/calc-citation-contract.md` rule 2 + W1-A/W2-A in-progress organizational precedent.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; this plan keeps phrase lists narrowly scoped to ISO-specific copyright/cover-page strings (see Risks).
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review is acceptable when Codex/Gemini sandboxes are unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — codex-cli 0.124.0 stdin-hang #2479 blocks Codex review.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini sandbox cwd=/tmp blocks workspace-hub overlay reads.
- `feedback_never_offer_to_self_label_plan_approved.md` — this plan does NOT propose self-approval; it does NOT pre-authorize downstream agents.

### Gaps identified

- No engineering-standards wiki pages exist for any of: ISO 19900, ISO 19901-1, ISO 19901-2, ISO 19901-4, ISO 19901-7, ISO 19902, ISO 19903, ISO 19904-1, ISO 19905-1.
- No engineering-domain wiki pages exist for any ISO 19900-series code either (verified via W1-C audit and direct `ls`). Zero cross-wiki collision.
- The standards-transfer-ledger contains zero rows for ISO 19900-series codes — required for traceability per W1-A and W2-A precedent.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any ISO page (since no ISO page exists).
- Calc sites in `digitalmodel/src/digitalmodel/marine_ops/.../component_database.py` and `digitalmodel/src/digitalmodel/orcaflex/environment.py` and `infrastructure/templates/plate_capacity_template.json` cite ISO 19901-7, ISO 19902, ISO 19901-1 in prose; no live `Citation(code_id="iso-19901-7", ...)` resolves today.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"
- `#2588` — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)"
- `#2590` — OPEN — "feat(llm-wiki): bounded DNV standards summary promotion to engineering-standards wiki (W2-A)"

**File existence** (`ls`/`find` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/ISO/` (249 PDFs total directory-wide; the ISO directory is NOT scoped to ISO 19900-series — it contains general-purpose technical-drawing standards (`ISO_2768`, `ISO_6410`, `ISO_7519`), steel/tube standards (`ISO_4200`, `ISO_10474`, `ISO_2063`), and even non-ISO documents — so the 249 figure is corpus-wide, not 19900-series-specific)
- EXISTS (19900-series, drafts/partial only): 24 files matching `*1990[0-9]*` — see inventory below
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing engineering-standards code page)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/iso-19900.md`, `iso-19901-1.md`, `iso-19901-2.md`, `iso-19901-4.md`, `iso-19901-7.md`, `iso-19902.md`, `iso-19903.md`, `iso-19904-1.md`, `iso-19905-1.md` (9 pages — see Files to Change)
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_iso_19900_series_pages.py`
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (the resolver target)
- EXISTS: `digitalmodel/src/digitalmodel/citations/registry.py` (the live `Citation(...)` constructor at line 52)

**ISO 19900-series PDFs/docs on disk** (`find /mnt/ace/O&G-Standards/ISO -iname "*1990*"` 2026-05-02 — full list, 24 files):
```
/mnt/ace/O&G-Standards/ISO/ISO_19901-1_FDIS_SUBMITTED_2_Metocean_Conditions.pdf
/mnt/ace/O&G-Standards/ISO/ISO-DIS-19901-1_(1)_Metocean.pdf
/mnt/ace/O&G-Standards/ISO/ISO-DIS-19901-1_(1).pdf
/mnt/ace/O&G-Standards/ISO/ISO_19901-2_E_Submitted_for_FDIS_Seismic_Design.pdf
/mnt/ace/O&G-Standards/ISO/ISO_CD_19901-3_Topsides.pdf
/mnt/ace/O&G-Standards/ISO/ISO_19901-3_markup.pdf
/mnt/ace/O&G-Standards/ISO/ISO_DIS_19901-4_responses.pdf
/mnt/ace/O&G-Standards/ISO/ISO_19901-7_DIS_04-02-13_Stationkeeping.pdf
/mnt/ace/O&G-Standards/ISO/19902_Clause_26_DIS.pdf
/mnt/ace/O&G-Standards/ISO/19902_Annex_C_DIS.pdf
/mnt/ace/O&G-Standards/ISO/ISO_FDIS_19905_1.pdf
/mnt/ace/O&G-Standards/ISO/ISO_FDIS_19905-1_(E)_2011-07-07.pdf
/mnt/ace/O&G-Standards/ISO/ISO_FDIS_19905-1_(E)-2nd-FDIS-2012-03-15.pdf
/mnt/ace/O&G-Standards/ISO/ISO_DIS_19905-1_(E).pdf
/mnt/ace/O&G-Standards/ISO/19905-1_(E)_CD_G-2007-03-20.doc
/mnt/ace/O&G-Standards/ISO/Pre_Publication_Comments_on_ISO_FDIS_19905-1-at-2011-04-29.doc
/mnt/ace/O&G-Standards/ISO/ISO_TR_19905-2_(E)-2011-04-28.doc
/mnt/ace/O&G-Standards/ISO/ISO_TR_19905-2_(E)-2012-04-27-accepted.doc
/mnt/ace/O&G-Standards/ISO/N_483_ISO_TR_19905-2_E-2011-06-13_-_CD_.pdf
/mnt/ace/O&G-Standards/ISO/19xxx/ISO_19905-1_2012_vs_FDIS_2015.docx
/mnt/ace/O&G-Standards/ISO/ISO_FDIS_19906_(E).pdf
/mnt/ace/O&G-Standards/ISO/19xxx/Future_ISO_19906_Ice_Load_Code_Offshore_Structures.doc
/mnt/ace/O&G-Standards/ISO/N328A_Terminology_for_19900_series.pdf
/mnt/ace/O&G-Standards/ISO/JH22419905K0.pdf
```

**Critical observation:** every on-disk ISO 19900-series file is a draft (DIS, FDIS, CD), pre-publication submission, technical-report, or comment doc — **NOT a published edition**. The published 2013/2015/2016/2017/2019/2023 editions are not on disk under `/mnt/ace/O&G-Standards/ISO/`. Frontmatter `revision_source` MUST cite the ISO portal URL for current revisions; the `/mnt/ace` paths can be cited only as "draft preview" sources, not as canonical revision sources. This plan adopts the W1-A pattern of using `revision: "public-metadata-required-before-citation-use"` for any page where the on-disk file is a draft and the publisher revision cannot be pinned at write-time.

**Internal-reference frequency proof** (`grep -rohE "ISO[ _-]?(19900|19901|19902|19903|19904|19905|19906)([- _][0-9]+)?" /mnt/local-analysis/workspace-hub/ 2>/dev/null | sort | uniq -c | sort -rn | head` 2026-05-02):
```
     34 ISO 19901-7
     26 ISO_19902
     22 ISO 19902
     14 ISO19902
     10 ISO 19901-1
      4 ISO-19902
      1 ISO 19905-1
      1 ISO 19904-1
```

Total ISO 19902 (across spelling variants `ISO 19902`/`ISO_19902`/`ISO19902`/`ISO-19902`): 66 hits — 2nd highest after 19901-7 at 34. ISO 19905-1 and ISO 19904-1 each appear once in the workspace; these are documentation/comment references, not a strong calc-citation signal — but are included in the priority list because the audit (#2588) commits the 19900-series TAXONOMY as the priority anchor, not raw frequency.

**Public-revision evidence (web)**:
- ISO 19900:2019 — General requirements: <https://www.iso.org/standard/69761.html>
- ISO 19901-7:2013 (under FDIS revision ~2026): <https://www.iso.org/standard/59298.html>
- ISO 19901-4:2016 — Geotechnical: <https://www.iso.org/standard/61144.html>
- ISO 19902:2019 — Fixed steel: ISO catalog (per OnePetro `OTC-19608-MS` overview citing 2019 update)
- ISO 19904-1:2019 — Floating: <https://www.iso.org/standard/63801.html>
- BS EN ISO 19901 series landing: <https://landingpage.bsigroup.com/LandingPage/Series?UPI=BS+EN+ISO+19901>

<!-- Distinct sources counted: existing repo code (1), W1-A precedent plan (2), W2-A precedent plan (3), W1-C audit plan (4), engineering-standards CLAUDE.md schema (5), standards ledger (6), online-resource intel via /mnt/ace direct inventory (7), citation rule (8), project memory (9), web ISO catalog (10), W1-C r1 review's verifiable-anchor decision (11). 11 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2595-llm-wiki-W3B-engineering-standards-iso-19900.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19900.md` |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-1.md` |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-2.md` |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-4.md` |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-7.md` |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19902.md` |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19903.md` |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19904-1.md` |
| Wiki page (9) | `knowledge/wikis/engineering-standards/wiki/standards/iso-19905-1.md` |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 9 new rows for the codes above) |
| Test contract | `tests/knowledge/test_engineering_standards_iso_19900_series_pages.py` |
| Plan-index update | `docs/plans/README.md` |
| Cross-link to W1-C audit | `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md` (audit references this plan as the codification of the priority taxonomy; this plan's writeup adds a back-reference. The audit plan itself is NOT modified by this implementation — only cross-linked in prose.) |
| Plan review — Claude (single-author) | `scripts/review/results/2026-05-02-plan-W3B-claude-internal.md` (DRAFT — to be produced after r1 self-review at plan-review handoff) |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |

---

## Deliverable

Nine new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority ISO 19900-series code), each carrying #2471-frontmatter-compliant fields (`code_id`, `publisher`, `revision`) and a links-only pointer (a) to any draft source under `/mnt/ace/O&G-Standards/ISO/` and (b) to the canonical ISO catalog URL — plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream calc modules can resolve `Citation` instances for the offshore-structures family used at 100+ sites in `digitalmodel/`. The deliverable also retroactively grounds the W1-C audit's priority taxonomy: each wiki page IS the resolution target for the part numbers the audit's rationales cite.

---

## Pseudocode

The work is templated 9x repetition. Each new wiki page will follow the same skeleton:

```
---
title: "<Full standard name> — bounded summary"
tags: ["iso", "standards", "offshore-structures", "<discipline-tag>", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: iso-<part-number>            # lowercase-kebab; preserve internal hyphen for parts (iso-19901-7)
publisher: ISO
revision: "<YYYY | 'public-metadata-required-before-citation-use'>"
revision_source: "<https://www.iso.org/standard/NNNNN.html | publisher catalog pointer>"
verified_on: 2026-05-02
public_url: <publisher portal URL>
sources:
  - <one or more /mnt/ace/... paths IF a draft preview exists; else "publisher portal — no draft on disk">
extraction_policy: metadata-only
raw_copy_allowed: false
---

# <Full standard name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.

## Where to find the full text
- Canonical (ISO portal): <URL>
- Draft preview on disk (if any): <absolute /mnt/ace/... path> (read-only,
  vendor-derivative; do not copy into git per #2482; DRAFT — not the
  canonical revision; cite the ISO portal for the published edition)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code>

## Cross-references
- [[iso-19900]] (umbrella; cross-cite from each part)
- [[api-rp-2sk]] (W1-A peer when ISO 19901-7 is co-cited)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file uses a parametrized fixture iterating over the 9 page paths. Citation-resolver test imports the actual `_read_frontmatter` helper from `digitalmodel/src/digitalmodel/citations/schema.py` per the W2-A P2-5 fix (NOT constructor-only validation).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19900.md` | Bounded summary for ISO 19900:2019 — General requirements (umbrella for the series; cross-referenced from every part) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-1.md` | Bounded summary for ISO 19901-1:2015 — Metocean (10 internal hits) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-2.md` | Bounded summary for ISO 19901-2:2017 — Seismic |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-4.md` | Bounded summary for ISO 19901-4:2016 — Geotechnical |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19901-7.md` | Bounded summary for ISO 19901-7:2013 — Stationkeeping (34 internal hits — highest 19900-series frequency in the workspace; resolves the `marine_ops/.../component_database.py` citation) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19902.md` | Bounded summary for ISO 19902:2019 — Fixed steel (66 internal hits across spelling variants — 2nd highest; resolves the `plate_capacity_template.json` citation) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19903.md` | Bounded summary for ISO 19903:2019 — Fixed concrete (no on-disk draft; ISO portal-only; included for series completeness) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19904-1.md` | Bounded summary for ISO 19904-1:2019 — Floating offshore (1 internal hit; included for series completeness — floating is a major calc surface) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/iso-19905-1.md` | Bounded summary for ISO 19905-1:2023 — MODU site assessment (1 internal hit; multiple drafts on disk; included because BSEE study cited in resource intel relies on this code) |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 9 new rows; correct the stale `page_count: 5` to the live count and bump arithmetically against live state at write-time (do NOT hardcode against assumed-merged W1-A or W2-A counts) |
| Modify | `knowledge/wikis/engineering-standards/CLAUDE.md` | Add `revision_source` (required when `revision != "public-metadata-required-before-citation-use"`) and `verified_on` (required) to the "Standards page extra fields" schema table — formalizes the de-facto convention used by `api-17e.md` so future W4 plans cannot drop the field on the grounds that the schema doesn't require it (per r1 review MINOR-2) |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 9 new ledger rows (`iso-19900`, `iso-19901-1`, `iso-19901-2`, `iso-19901-4`, `iso-19901-7`, `iso-19902`, `iso-19903`, `iso-19904-1`, `iso-19905-1`) so all wiki pages map to a real ledger ID. **Casing rule (per r1 review MINOR-5):** ledger `id:` values match wiki `code_id` byte-for-byte (lowercase-kebab; e.g., `iso-19901-7`, NOT `ISO-19901-7`). `test_ledger_alignment` does byte-for-byte equality; no case-insensitive comparison. Implementation step MUST verify W2-A (DNV) and W1-A (API) ledger casing for parity at write-time; if those plans landed with uppercase IDs, raise as a follow-up unifying decision before this plan writes. |
| Create | `tests/knowledge/test_engineering_standards_iso_19900_series_pages.py` | Test contract: frontmatter, no-raw-text, citation resolvability, ledger alignment, cross-wiki uniqueness |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD Test List

All tests in `tests/knowledge/test_engineering_standards_iso_19900_series_pages.py`. Each parametrized over the 9 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of 9 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, **lowercase-kebab** matching engineering-standards CLAUDE.md schema + W1-A + W2-A; filename stem equals `code_id` verbatim (e.g., `iso-19901-7.md` ↔ `iso-19901-7`) |
| `test_frontmatter_has_publisher_iso` | publisher discipline | YAML frontmatter | `publisher == "ISO"` |
| `test_frontmatter_has_revision` | revision presence (per .claude rule 2) | YAML frontmatter | `revision` non-empty string; matches regex `^(\d{4}\|public-metadata-required-before-citation-use)$` (no edition-suffix needed for ISO; simple year is canonical) |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_distinguishes_draft_vs_published_revision` | draft-preview honesty | frontmatter `sources` + `revision` | if any `sources` entry contains `DIS`, `FDIS`, `CD`, or `markup`, then `revision_source` MUST be a publisher-portal URL (NOT the draft path); the draft path may appear in `sources` but cannot be the revision source. Enforces "draft on disk ≠ published revision" |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow phrase set; see Risks) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | 100 < N < 500 (strict `<` on both bounds, matching W1-A and W2-A) | page body | bounded preview budget; import the constant from W1-A or W2-A test module rather than redefining |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only the four allowed structural sections | page body | top-level `##` headings exactly subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` |
| `test_links_only_pointer_to_canonical_url` | the page mentions the ISO portal canonical URL | page body | regex `iso\.org/standard/\d+\.html` present in "Where to find" section (every page; portal is canonical even when on-disk draft exists) |
| `test_citation_schema_resolvable` | downstream resolver — actually reads the wiki page (W2-A P2-5 pattern) | invoke `_read_frontmatter` (or registry-level `Citation` resolver) per page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised |
| `test_ledger_alignment` | every page's `code_id` resolves to a row in `standards-transfer-ledger.yaml` (per r1 review MINOR-5: byte-for-byte equality, NOT case-insensitive) | wiki frontmatter `code_id` | matching `id:` row found in ledger YAML; equality is exact-string (lowercase-kebab on both sides) |
| `test_index_lists_all_nine` | wiki index updated | `index.md` contents | each of 9 page links present in "## Standards" section |
| `test_cross_wiki_code_id_uniqueness` | inherited from W2-A | scan all `knowledge/wikis/*/wiki/standards/*.md` | no `code_id` value duplicated across wiki domains for any ISO code (since `engineering/wiki/standards/` has zero ISO entries today, expected to pass trivially; test exists to catch future regressions) |
| `test_umbrella_cross_reference` | series-cohesion check — every part page back-references the umbrella | each page (8 parts) | body contains `[[iso-19900]]` link; the umbrella page itself is exempted |
| `test_cross_reference_budget_bounded` | enforces the "umbrella + ≤2 normative siblings" budget committed in Risks (per r1 review MINOR-3) | each part page (8 parts) | count of `[[iso-...]]` wiki-link occurrences in body (excluding the page's own `code_id`) is `≤ 3` (umbrella + ≤2). The umbrella page `iso-19900.md` is exempted (it lists every part) |

`RAW_TELLTALE_PHRASES` will be a narrowly-scoped list (≤20 entries) drawn from ISO publication front-matter conventions AND ISO working-draft conventions (per r1 review MINOR-4 — the on-disk 19905-1 corpus contains `.doc`/`.docx` working drafts that carry track-changes annotations and ballot-comment sheets which the published-cover denylist does not catch):

- **Published-edition cover/copyright telltales:** `"© ISO 20"` (matches any year 2000-2099), `"All rights reserved"`, `"Reproduction or use in any form"`, `"International Organization for Standardization"`, `"Case postale 56"`, `"CH-1211 Geneva"`, `"www.iso.org"` (when adjacent to copyright prose, not as a bare URL — see Risks for distinguisher), `"Reference number ISO"`, `"INTERNATIONAL STANDARD ISO"`.
- **Working-draft / ballot / committee telltales** (added per r1 MINOR-4): `"FDIS ballot"`, `"DIS comment"`, `"ISO/TC 67"` (the technical committee for petroleum/natural-gas industries; appears in cover sheets of every working draft in the corpus), `"ISO/TC 67/SC 7"` (the offshore-structures sub-committee), `"Editing committee"`, `"track changes"`.

The list excludes the standard's title and code identifier (which are required). The ISO-specific list will NOT overlap with the OCIMF, API, or DNV denylists. Shingle-match check is documented as a planned W2-B follow-up (inherited from W2-A risk register) and is the durable answer to the partial-denylist class of risks.

---

## Acceptance Criteria

- [ ] All 9 new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_iso_19900_series_pages.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/iso-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` populated; lowercase-kebab `code_id` deterministically maps to filename stem).
- [ ] Citation downstream-resolution check (single canonical revision string per page; the page's frontmatter `revision` and the `Citation(...)` argument MUST match verbatim, since `validate_citation` does literal-equality on the revision string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - For each page where a real publisher revision is asserted in frontmatter, `python -c "from digitalmodel.citations.schema import Citation; Citation(code_id='<id>', publisher='ISO', revision='<frontmatter-revision-verbatim>', section='<placeholder>', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md')"` succeeds without error. Concrete example: `iso-19902.md` will use `revision: "2019"` in BOTH frontmatter AND the `Citation(...)` call.
  - Pages whose revision cannot be pinned to a verifiable publisher edition at write-time MUST set `revision: "public-metadata-required-before-citation-use"` in frontmatter AND be excluded from this resolution check (test parametrization skips them with `pytest.mark.skip(reason="stub-only, revision pending")`).
- [ ] Ledger alignment: every page's `code_id` resolves to a row in `data/document-index/standards-transfer-ledger.yaml` (9 new rows added by this plan; 0 exist today).
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 9 new pages under "## Standards" section; `page_count` recomputed at write-time against live state (NOT hardcoded — see Risk: arithmetic-stale).
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan (the source-summary surface is reserved for raw-corpus pointers, not standards pages).
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified (zero ISO collision, but this AC guards against accidentally creating one).
- [ ] **Draft-vs-published distinction enforced:** `test_frontmatter_distinguishes_draft_vs_published_revision` passes — every page that lists a `/mnt/ace` draft in `sources` MUST cite the ISO portal URL (not the draft path) as `revision_source`.
- [ ] Plan review artifact present at `scripts/review/results/2026-05-02-plan-W3B-claude-internal.md` (single-author Claude review acceptable per memory `feedback_permission_gate_blocks_cross_review.md`). Codex unavailable per `feedback_codex_cli_0_124_upstream_regression.md`; Gemini unavailable per `feedback_gemini_sandbox_overlay_blindness.md`. Cross-provider review NOT a hard gate; if codex-cli 0.123.0 downgrade or Gemini fix lands before implementation, a v2 review SHOULD be dispatched as a non-blocking artifact.
- [ ] **W1-C audit cross-link:** the implementation step adds a one-line back-reference to this plan in the W1-C audit deliverable (`docs/audits/2026-05-02-engineering-wiki-gap-audit.md`, when produced) — the audit's priority rationales cite ISO 19900-series part numbers, and the wiki pages this plan creates are the resolution targets. **This AC is conditional**: it fires only if W1-C lands its deliverable before this plan's implementation runs; otherwise it is deferred to W1-C's own implementation.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MINOR | 5 MINOR — addressed inline; #2471 corrected framing adopted; draft-vs-published revision_source contract retained |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-with-revisions (5 MINOR fixes applied 2026-05-02)

**Revisions made based on review:**
- MINOR-1: corrected resource-intel page-count arithmetic (live `find` floor = 9, not 6); index-update item now also corrects the stale `page_count: 5` value.
- MINOR-2: added `Modify | knowledge/wikis/engineering-standards/CLAUDE.md` line item to formalize `revision_source` and `verified_on` in the Standards page extra-fields schema.
- MINOR-3: added `test_cross_reference_budget_bounded` parametrized test enforcing the umbrella + ≤2 normative-siblings cap (≤3 `[[iso-...]]` links per part page).
- MINOR-4: extended `RAW_TELLTALE_PHRASES` denylist with working-draft / ballot / committee telltales (`"FDIS ballot"`, `"DIS comment"`, `"ISO/TC 67"`, `"ISO/TC 67/SC 7"`, `"Editing committee"`, `"track changes"`) for the `.doc`/`.docx` 19905-1 working-draft corpus.
- MINOR-5: added byte-for-byte ledger-ID casing rule (lowercase-kebab `iso-19901-7`, not `ISO-19901-7`); rewrote Files-to-Change ledger row IDs in lowercase; updated `test_ledger_alignment` to assert exact-string equality.

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk:** ISO standards pricing model. ISO codes are **subscription-only** at the publisher portal — there is no free DNV-style "Rules and Standards Explorer" full-text portal. Reviewers verifying citation correctness against the published revision must obtain the document via institutional ANSI/BSI/IHS subscription or the ISO Online Browsing Platform (OBP) preview. **Mitigation:** every wiki page's `revision_source` cites the ISO catalog URL (which is public and stable, even when full text is paywalled); reviewers are expected to verify against publisher metadata (title, year, scope) rather than full-text comparison. Where a draft preview exists on `/mnt/ace`, it MAY be consulted but MUST NOT be cited as the revision source per the `test_frontmatter_distinguishes_draft_vs_published_revision` AC.
- **Risk (revision-superseded chain):** ISO 19901-7 had multiple revisions: 2005 (1st ed), 2013 (2nd ed, current), and ISO/FDIS 19901-7 expected ~2026 (3rd ed in flight per the ISO catalog page). The on-disk draft is `ISO_19901-7_DIS_04-02-13_Stationkeeping.pdf` — a 2013 DIS, which is the immediate predecessor of the published 2013 edition. **Mitigation:** the page declares `revision: "2013"` and adds a `supersession_note` field flagging the in-flight 2026 revision. When 19901-7:2026 is published, a follow-up issue MUST update the page's revision field; the calc-citation contract literal-equality check will detect drift (any `Citation(code_id="iso-19901-7", revision="2026")` will fail until the page is updated). Similar patterns apply to ISO 19905-1 (2012 → 2016 → 2023), ISO 19902 (2007 → 2019), ISO 19900 (2002/2013/2019), and ISO 19904-1 (2006/2019).
- **Risk (cross-reference link sprawl):** The 19900-series is a tightly cross-referenced family — ISO 19902 normatively references ISO 19900 + 19901 (multiple parts); ISO 19904-1 references ISO 19900 + 19901 + 19905-1; etc. If each part page lists every cross-reference, the body word count budget (≤500) blows. **Mitigation:** the umbrella page `iso-19900.md` is the single hub for series cross-references; each part page lists ONLY the umbrella + the ≤2 most directly normative siblings (e.g., `iso-19902.md` lists `iso-19900` + `iso-19901-1` (metocean inputs) only). Test `test_umbrella_cross_reference` enforces the umbrella back-reference; reviewers manually inspect for cross-ref bloat per page during r1 review.
- **Risk:** Draft-vs-published confusion. Every on-disk file under `/mnt/ace/O&G-Standards/ISO/` matching `*1990[0-9]*` is a DIS, FDIS, CD, or comment doc — NOT a published edition. A naive contributor citing `/mnt/ace/.../ISO_19901-7_DIS_04-02-13_Stationkeeping.pdf` as the revision source would propagate a 2013 DIS as the canonical revision when the published 2013 edition has different (potentially divergent) text. **Mitigation:** the `test_frontmatter_distinguishes_draft_vs_published_revision` test fails any page that cites a draft path in `revision_source`; reviewers flag any prose that conflates DIS with published edition.
- **Risk:** Copyright leakage. The `RAW_TELLTALE_PHRASES` denylist is ISO-specific (`"© ISO"`, `"International Organization for Standardization"`, `"Case postale 56"`, `"INTERNATIONAL STANDARD"`) and brittle — it will not catch a 100-200-word verbatim clause copy that omits cover-page strings. **Mitigation:** word-count ceiling (≤500), positive-shape structural test, `extraction_policy: metadata-only` frontmatter, `raw_copy_allowed: false`, and reviewers MUST manually inspect every revision touching `wiki/standards/iso-*.md` for clause-shaped prose. Shingle-match check is documented as a planned W2-B follow-up (inherited from W2-A risk register).
- **Risk:** Bare-URL false positive. The denylist phrase `"www.iso.org"` may collide with the legitimate `revision_source` and `public_url` URL fields. **Mitigation:** distinguish via context — denylist matches only `"www.iso.org"` when adjacent to copyright prose (`"© ISO" + "www.iso.org"` within same line/paragraph); plain URL alone does not match. Test implementation will use a paragraph-level regex window, not a flat-text match.
- **Risk (arithmetic-stale):** The `page_count` value in `index.md` cannot be hardcoded against an assumption that W1-A (#2586) and W2-A (#2590) have landed. Both are still in `plan-review` as of 2026-05-02. **Mitigation:** the implementation step computes `page_count` via `find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` at write-time and writes the live count.
- **Risk:** Test-file shared-fixture coupling. The W1-A and W2-A test files import shared constants (e.g., word-count bounds, denylist primitive); if those modules don't exist when this W3-B test file is implemented (because W1-A/W2-A haven't merged yet), imports fail. **Mitigation:** the test file MUST be self-contained at write-time — define its own `WORD_COUNT_LOWER = 100`, `WORD_COUNT_UPPER = 500` constants (matching the W1-A/W2-A documented values). When W1-A/W2-A merge, a follow-up issue can refactor to a shared helper module; until then, parity is maintained by code review.
- **Risk:** ISO 19905-1 reference count is 1 in the workspace, weak frequency signal. Including it on the priority list is justified by series-completeness (the audit's #2588 r1 fix explicitly named `19905-1` as part of the verifiable taxonomy). If user prefers frequency-driven prioritization, `iso-19905-1` is the swap candidate.
- **Open:** Should newer ISO 19901-9 (reliability of offshore structures, 2019) be included in this W3-B batch? **Defer to user.** Adding it expands scope from 9 to 10 pages; reliability is a meaningful calc surface (digitalmodel does have probabilistic-design code paths), but the workspace has zero current grep hits for `19901-9`. Recommendation: defer to a W3-C follow-up unless the user explicitly requests.
- **Open:** Should ISO 19906 (arctic structures) be included? Raw on disk: `ISO_FDIS_19906_(E).pdf` (2010 FDIS, current published 2019). This is on the boundary — it's a 19900-series sibling but not in the prompt's list; arctic-specific calc surface in digitalmodel is currently absent. Recommendation: defer to W3-C unless the user requests.
- **Open:** ISO 19905-2 (TR — site assessment for jack-ups, technical report not standard) — multiple drafts on disk (`ISO_TR_19905-2_*.doc`). Technical reports are not normative and cannot be a citation target the way the published standards are. **Recommendation:** exclude from this W3-B batch (TRs are out of scope for the calc-citation contract); defer to a follow-up issue if reviewers demand a "where to find the TR" pointer page.
- **Open:** ISO 19901-3 (topsides), 19901-5 (weight control), 19901-6 (marine operations) — Part 3 has draft on disk; 5 and 6 do not. Each has small but non-zero offshore-design relevance. **Defer to user/W3-C.** This W3-B plan stops at 9 pages to keep the cross-reference budget bounded.
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_iso_19900_series_pages.py` (one file) or be split per-page? Single-file parametrized form proposed for tractability and parity with W1-A/W2-A.
- **Open:** When W1-A and/or W2-A merge before this plan's implementation runs, should this plan's tests be refactored to import shared constants from those test modules? (Currently risk-mitigated by self-contained constants.) Defer the consolidation question to a small follow-up after all three plans merge.

---

## Complexity: T2

**T2** — multi-file documentation work (9 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 13 files), no new code modules, but a real test contract (≥15 parametrized assertions × 9 pages ≈ ~135 effective test cases). Implementation is templated repetition; the design risk is concentrated in (a) the denylist phrasing and bare-URL false-positive distinguisher, (b) the draft-vs-published revision-source contract, and (c) the cross-reference budget management for a tightly-cross-referenced series — not in algorithm correctness. Matches W1-A and W2-A T2 sizing; the ISO scope is narrower (9 pages vs 10) but adds the draft-vs-published acceptance criterion that neither sibling needed.
