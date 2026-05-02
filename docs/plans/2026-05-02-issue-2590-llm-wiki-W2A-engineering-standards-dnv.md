# Plan for LLM-Wiki Completeness W2-A: Bounded DNV Code Body Summary Promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** _not yet filed — this plan is the deliverable; issue creation is downstream of plan-review_
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Sibling precedent (API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN, status:plan-review) — the W1-A pattern this W2-A plan inherits
> **Sibling precedent (OCIMF Tandem):** [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) (CLOSED) — bounded preview test pattern (`tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py`) that this plan extends
> **Path sanction:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) — `wiki/standards/<code-id>.md` routing
> **Citation contract:** `.claude/rules/calc-citation-contract.md` — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`)
> **Calc-citation pilot:** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors prose-level pilot
> **Review artifacts:** scripts/review/results/2026-05-02-plan-DNV-W2-claude.md | …-codex.md | …-gemini.md (to be produced post-plan-review by main session)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). This is the downstream consumer that will resolve the wiki pages this plan will create.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/registry.py` — companion resolver. The single live `Citation(...)` constructor on disk lives here at line 52.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — prose-level pilot reference for **DNV-OS-E301** mooring safety factors (per `.claude/rules/calc-citation-contract.md`); cited as the pilot but not yet wired to a `Citation(...)` instance.
- Gap: no summary-promotion artifact exists for the `/mnt/ace/O&G-Standards/DNV/` corpus in the `engineering-standards` wiki. The single existing DNV wiki page (`knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`) sits in the **engineering** wiki, not **engineering-standards** — see Risks for the cross-wiki-duplication question.

### Standards

| Standard | Status | Source |
|---|---|---|
| DNV-ST-F101 (2021, 10th Ed; formerly DNV-OS-F101) — Submarine pipeline systems | gap (raw 2000/2007/2008/2010/2012/2013 editions present in `/mnt/ace`; current 2021 edition not on disk; no engineering-standards wiki page) | `data/document-index/standards-transfer-ledger.yaml` `id: DNV-OS-F101`; `/mnt/ace/O&G-Standards/DNV/DNV_OS_F101_(2013)_Submarine_Pipeline_Systems.pdf` (most recent on disk); current revision per <https://www.dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems/> |
| DNV-RP-C203 (2024-10, amended 2025-10) — Fatigue design of offshore steel structures | gap (raw 2000/2005/2008/2011 editions present; current 2024 edition not on disk; no wiki page) | `/mnt/ace/.../DNV_RP_C203_(2011)_Fatigue_Design_of_Offshore_Steel_Structure.pdf`; current revision per <https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/> |
| DNV-RP-C205 (2007/2010) — Environmental conditions and environmental loads | gap | `/mnt/ace/.../DNV_RP_C205_(2010)_Environmental_Conditions_and_Environmental_Loads.pdf`; also referenced by `data/document-index/online-resource-registry.yaml` entry `rules_dnv_com_docs_pdf_dnvpm_8a23de` |
| DNV-RP-B401 (2011) — Cathodic protection design | gap | `/mnt/ace/.../DNV_RP_B401_(2011)_Cathodic_Protection_Design.pdf`; ledger row `id: DNV-RP-B401-2011` exists |
| DNV-OS-E301 (2010 on disk; 2021-07 current per existing pilot) — Position mooring | partial — page exists in `engineering/wiki/standards/dnv-os-e301.md`, NOT in `engineering-standards/wiki/standards/`. This W2 plan creates a parallel page in `engineering-standards` with the #2471-compliant frontmatter; the existing `engineering/` page is unchanged. See Open Questions for retro-merge proposal. | `/mnt/ace/.../DNV_OS_E301_(2010)_Position_Mooring.pdf`; existing pilot at `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` |
| DNV-OS-F201 (2010) — Dynamic risers | gap | `/mnt/ace/.../DNV_OS_F201_(2010)_Dynamic_Risers.pdf`; ledger row `id: DNV-OS-F201` exists |
| DNV-RP-F101 (2010) — Corroded pipelines | gap | `/mnt/ace/.../DNV_RP_F101_(2010)_Corroded_Pipelines.pdf`; ledger row `id: DNV-RP-F101` exists |
| DNV-RP-F105 (2006) — Free spanning pipelines | gap | `/mnt/ace/.../DNV_RP_F105_(2006)_Free_Spanning_Pipelines.pdf`; ledger row `id: DNV-RP-F105` exists |
| DNV-RP-F109 (2007/2011) — On-bottom stability of pipelines | gap | `/mnt/ace/.../DNV_RP_F109_(2011)_On_bottom_stability_of_pipelines.pdf`; ledger row `id: DNV-RP-F109` exists |
| DNV-RP-H103 (2010) — Modelling and analysis of marine operations | gap | `/mnt/ace/docs/_standards/SNAME/hydrostatics-stability/DNV-RP-H103-Marine-Operations-2010.pdf` (per `online-resource-registry.yaml` `local_backup_path`); 34 internal references |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards-domain code page; metadata stub frontmatter style this plan replicates ten times.
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`; will need an "## Standards" section and `page_count` bump to 15.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply.
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — the existing DNV-OS-E301 pilot. Frontmatter uses `code_id: DNV-OS-E301` (uppercase, with hyphens), `publisher: DNV`, `revision: 2021-07`. This W2 plan adopts the SAME case-style for `code_id` (matching the existing pilot rather than the API plan's lowercase-kebab choice — see Risks).
- `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — Elements ingest catalog already references the broader DORIS standards corpus; the DNV subset of `/mnt/ace/O&G-Standards/DNV/` (99 PDFs, 213 MB) is a complementary path through the same corpus.

### Documents consulted

- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — direct precedent. This W2-A plan inherits W1-A's bounded-preview frontmatter, no-raw-text test, and citation-resolvability test patterns. **Differences from W1-A** documented inline: (a) DNV revision-numbering convention is `<edition>-<year-month>` (e.g., `2024-10`) or simple year (e.g., `2010`), not API's "Nth Edition + addendum" convention; (b) DNV's 2021 rebranding renamed all `OS-` codes to `ST-` (e.g., DNV-OS-F101 → DNV-ST-F101) — the wiki page must declare BOTH the legacy and current code identifiers; (c) the existing pilot at `engineering/wiki/standards/dnv-os-e301.md` uses `code_id: DNV-OS-E301` (uppercase) whereas the W1-A plan adopted lowercase-kebab (`api-rp-2a-wsd`) — this W2-A plan adopts uppercase to match the existing DNV pilot, and flags the inter-plan inconsistency as an open question for harmonization.
- `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — bounded preview pattern (#2227 closure).
- `data/document-index/standards-transfer-ledger.yaml` — already contains canonical IDs for most priority codes (`DNV-OS-F101`, `DNV-OS-F201`, `DNV-RP-F101`, `DNV-RP-F105`, `DNV-RP-F109`, `DNV-RP-B401`, `DNV-RP-B401-2011`, `DNV-RP-F103`, `DNV-RP-F103-2010`, `DNV-006`); does NOT yet contain `DNV-RP-C203`, `DNV-RP-C205`, `DNV-RP-H103`, or `DNV-OS-E301` rows — those are introduced by this plan via new ledger rows.
- `data/document-index/online-resource-registry.yaml` — entries for `dnv_standards_explorer` (the DNV Rules and Standards Explorer at <https://standards.dnv.com/explorer/>) and per-document URLs for DNV-RP-C205 and DNV-RP-H103. The new wiki pages will cross-link these.
- `.claude/rules/calc-citation-contract.md` — the citation contract this plan exists to satisfy. Names DNV-OS-E301 explicitly as the pilot reference. After this plan lands, downstream calc modules in `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` and the broader marine_ops modules can resolve `Citation(code_id="DNV-OS-E301", ...)` against the new engineering-standards page (the existing engineering-domain page does NOT carry the `extraction_policy: metadata-only` frontmatter the contract expects).
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (referenced via project CLAUDE.md) — the issue-planning workflow this plan obeys.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` is the sanctioned path; #2471 codified it for CSA Z276 and the principle now generalizes to API (W1-A) and DNV (this W2-A plan).
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; this plan keeps phrase lists narrowly scoped to DNV-specific copyright/cover-page strings.

### Gaps identified

- No engineering-standards wiki pages exist for any DNV code: DNV-ST-F101, DNV-RP-C203, DNV-RP-C205, DNV-RP-B401, DNV-OS-E301 (in this wiki domain), DNV-OS-F201, DNV-RP-F101, DNV-RP-F105, DNV-RP-F109, DNV-RP-H103.
- Calc-citation pilot `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` cites DNV-OS-E301 in prose; no live `Citation(code_id="DNV-OS-E301", ...)` resolves today because the existing `engineering/wiki/standards/dnv-os-e301.md` page lacks the `extraction_policy: metadata-only` and `raw_copy_allowed: false` frontmatter the contract assumes.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any DNV page.
- The standards-transfer-ledger does not contain rows for DNV-RP-C203, DNV-RP-C205, DNV-RP-H103, DNV-OS-E301 — required for traceability per the W1-A precedent.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"
- `#2227` — CLOSED — "feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis"
- `#2482` — CLOSED — "docs(knowledge): reconcile llm-wiki → GTM content boundary — resolve #2022 vs firm-copy-out-of-scope decision"
- `#2481` — CLOSED — "feat(llm-wiki): calculation-output citation contract — engineering modules cite wiki-backed provenance"

**File existence** (`ls` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/DNV/` (99 PDFs at depth 3 via `find -maxdepth 3 -type f \( -name "*.pdf" -o -name "*.PDF" \)`)
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing engineering-standards code page; the 9 files claim in the prompt counts the wiki tree under the engineering-standards domain more broadly, but `wiki/standards/` itself contains 1 file)
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (the calc-citation pilot, in engineering domain)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/dnv-st-f101.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-b401.md`, `dnv-os-e301.md`, `dnv-os-f201.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `dnv-rp-f109.md`, `dnv-rp-h103.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_dnv_pages.py`
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (the resolver target)
- EXISTS: `digitalmodel/src/digitalmodel/citations/registry.py` (the live `Citation(...)` constructor at line 52)

**Sample DNV PDFs on disk** (`find /mnt/ace/O&G-Standards/DNV -maxdepth 3 -type f \( -name "*.pdf" -o -name "*.PDF" \) | head` 2026-05-02):
```
DNV_OS_E301_(2008)_Position_Mooring.pdf
DNV_OS_E301_(2010)_Position_Mooring.pdf
DNV_OS_F101_(2000)_Submarine_Pipeline_Systems.pdf … DNV_OS_F101_(2013)_Submarine_Pipeline_Systems.pdf
DNV_OS_F201_(2001)_Dynamic_Risers.pdf … DNV_OS_F201_(2010)_Dynamic_Risers.pdf
DNV_RP_B401_(1993)_Cathodic_Protection_Design.pdf … DNV_RP_B401_(2011)_Cathodic_Protection_Design.pdf
DNV_RP_C203_(2000)…2011 series
DNV_RP_C205_(2007)…2010 series
DNV_RP_F101_(2004)/(2010)
DNV_RP_F105_(2002)/(2006)
DNV_RP_F109_(2007)/(2011)
```

**Internal-reference frequency proof** (`grep -rohE "DNV[ _-]?(OS|RP|SE|GL|OSS|CN|ST)[ _-]?[A-Z]?[0-9]+" digitalmodel/src/ | sort | uniq -c | sort -rn | head -20`):
```
    160 DNV-RP-C203
     75 DNV-ST-F101
     63 DNV-RP-C205
     56 DNV-RP-B401
     35 DNV-RP-C201   ← noted but excluded from top-10 (no raw on disk; out of scope)
     35 DNV-OS-E301
     34 DNV-RP-H103
     24 DNVSTF101     ← variant spelling, maps to DNV-ST-F101
     23 DNV_RP_F103   ← noted but excluded (cathodic-protection sibling of B401, lower freq)
     22 DNV-OS-F201
     19 DNV-RP-F109
     19 DNV-RP-F105
     16 DNV-RP-F103
     13 DNV-OS-F101   ← legacy; rolled into DNV-ST-F101 page
     12 DNV-ST-N001   ← noted but excluded (no raw on disk; out of scope)
```

**Public-revision evidence (web)**:
- DNV-ST-F101 (formerly DNV-OS-F101) — current 10th Ed (2021): <https://www.dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems/>
- DNV-RP-C203 — current edition 2024-10, amended 2025-10: <https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/>
- DNV Rules and Standards Explorer (free full-text portal): <https://standards.dnv.com/explorer/>

<!-- Distinct sources counted: existing repo code (1), standards ledger (2), engineering-standards CLAUDE.md schema (3), engineering-domain DNV pilot wiki page (4), W1-A precedent plan (5), W2-A OCIMF precedent plan (6), online-resource-registry (7), citation rule (8), project memory (9), web (10). 10 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-st-f101.md` (carries `legacy_code_id: DNV-OS-F101`) |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-c203.md` |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-c205.md` |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-b401.md` |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-os-e301.md` (parallel to engineering-domain pilot) |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-os-f201.md` |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f101.md` |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f105.md` |
| Wiki page (9) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f109.md` |
| Wiki page (10) | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-h103.md` |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 4 new rows: `DNV-RP-C203`, `DNV-RP-C205`, `DNV-RP-H103`, `DNV-OS-E301`) |
| Test contract | `tests/knowledge/test_engineering_standards_dnv_pages.py` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-DNV-W2-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-DNV-W2-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-DNV-W2-gemini.md` |

---

## Deliverable

Ten new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority DNV code), each carrying #2471-compliant frontmatter (`code_id`, `publisher`, `revision`) and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/DNV/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream calc modules can resolve `Citation` instances for the ten most-referenced DNV codes (collectively ~530 grep hits across digitalmodel) without any verbatim source text entering git.

---

## Pseudocode

The work is a templated 10x repetition. Each new wiki page will follow the same skeleton:

```
---
title: "<Full standard name> — bounded summary"
tags: ["dnv", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: DNV-<TYPE>-<NUMBER>          # uppercase to match existing engineering-domain pilot
legacy_code_id: <DNV-OS-...>          # only on the dnv-st-f101 page (rebranding artifact)
publisher: DNV
revision: "<YYYY-MM | edition + year>"
revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"
verified_on: 2026-05-02
public_url: <publisher portal URL when known>
sources:
  - <one or more /mnt/ace/... paths — pointer only, never quoted>
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
- Raw PDF: <absolute /mnt/ace/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: <URL> (DNV Rules and Standards Explorer is free full-text)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code>

## Cross-references
- [[dnv-rp-c203]] (when applicable for fatigue cross-cite)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file will use a parametrized fixture iterating over the 10 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-st-f101.md` | Bounded summary for DNV-ST-F101 (2021, 10th Ed); declares `legacy_code_id: DNV-OS-F101` to bridge pre-2021 callers |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-c203.md` | Bounded summary for DNV-RP-C203 (2024-10 amended 2025-10); highest internal reference count (160) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-c205.md` | Bounded summary for DNV-RP-C205 (2010 on disk) — environmental conditions and loads |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-b401.md` | Bounded summary for DNV-RP-B401 (2011) — cathodic protection design |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-os-e301.md` | Bounded summary for DNV-OS-E301 (2010 on disk; 2021-07 current); resolver target for the calc-citation pilot in `mooring_design.py`. **Parallel to** existing `engineering/wiki/standards/dnv-os-e301.md` (different wiki domain) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-os-f201.md` | Bounded summary for DNV-OS-F201 (2010) — dynamic risers |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f101.md` | Bounded summary for DNV-RP-F101 (2010) — corroded pipelines |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f105.md` | Bounded summary for DNV-RP-F105 (2006) — free spanning pipelines |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f109.md` | Bounded summary for DNV-RP-F109 (2011) — on-bottom stability |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-h103.md` | Bounded summary for DNV-RP-H103 (2010) — modelling and analysis of marine operations |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 10 new rows; bump `page_count` to 15 |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 4 new ledger rows (`DNV-RP-C203`, `DNV-RP-C205`, `DNV-RP-H103`, `DNV-OS-E301`) so all 10 wiki pages map to a real ledger ID |
| Create | `tests/knowledge/test_engineering_standards_dnv_pages.py` | Test contract: frontmatter, no-raw-text, citation resolvability, registry alignment |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_dnv_pages.py`. Each test parametrized over the 10 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 10 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per #2471 | YAML frontmatter | `code_id` non-empty, uppercase-with-hyphens (matches existing DNV pilot style), kebab-cased filename stem maps deterministically to `code_id` (e.g., `dnv-st-f101.md` ↔ `DNV-ST-F101`) |
| `test_frontmatter_has_publisher_dnv` | publisher discipline | YAML frontmatter | `publisher == "DNV"` |
| `test_frontmatter_has_revision` | revision presence (per .claude rule 2) | YAML frontmatter | `revision` non-empty string; matches DNV regex `^(\d{4}(-\d{2})?\|public-metadata-required-before-citation-use)$` |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_legacy_code_id_only_on_renamed_codes` | rebrand bridge | YAML frontmatter | only `dnv-st-f101.md` carries `legacy_code_id`, and its value is `"DNV-OS-F101"` |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow phrase set; see Risks) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | 100 < N < 500 | page body | bounded preview budget (matches W1-A's tightened 500-word ceiling) |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only the four allowed structural sections | page body | top-level `##` headings are exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` |
| `test_links_only_pointer_to_mnt_ace` | the page mentions the raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/DNV/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolution | `Citation(code_id=<id>, publisher="DNV", revision=<rev>, section="placeholder", wiki_path=<path>)` constructs without error | `CitationValidationError` not raised; `wiki_path` exists |
| `test_ledger_alignment` | every page's `code_id` resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `code_id` | matching `id:` row found in ledger YAML |
| `test_index_lists_all_ten` | wiki index updated | `index.md` contents | each of the 10 page links present in the "## Standards" section |

`RAW_TELLTALE_PHRASES` will be a small, narrowly-scoped list (≤15 entries) drawn from DNV publication front-matter conventions — e.g. "Det Norske Veritas AS", "DNV-Veritasveien", "Veritasveien 1", "1322 Høvik, Norway", "© Det Norske Veritas", "All rights reserved", "Reproduction or transmission of any part" — phrases that would appear only if raw cover/copyright pages were copied. The list will deliberately exclude the standard's title (which is allowed) and code identifier (which is required). The DNV-specific list will NOT overlap with the OCIMF or API denylists.

---

## Acceptance Criteria

- [ ] All ten new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_dnv_pages.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/dnv-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated, uppercase-with-hyphens `code_id` deterministically maps to filename stem).
- [ ] Citation downstream-resolution check (single canonical revision string per page; the page's frontmatter `revision` and the `Citation(...)` argument MUST match verbatim, since `validate_citation` does literal-equality on the revision string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - For each page where a real publisher revision is asserted in frontmatter, `python -c "from digitalmodel.citations.schema import Citation; Citation(code_id='<id>', publisher='DNV', revision='<frontmatter-revision-verbatim>', section='<placeholder>', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md')"` succeeds without error. Concrete example: `dnv-rp-c203.md` will use `revision: "2024-10"` in BOTH frontmatter AND the `Citation(...)` call.
  - Pages whose revision cannot be pinned to a verifiable publisher edition at write-time MUST set `revision: "public-metadata-required-before-citation-use"` in frontmatter AND be excluded from this resolution check (the test parametrization will skip them with a `pytest.mark.skip(reason="stub-only, revision pending")`).
- [ ] Ledger alignment: every page's `code_id` resolves to a row in `data/document-index/standards-transfer-ledger.yaml` (4 new rows added by this plan; 6 already exist).
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 10 new pages under a "## Standards" section; `page_count` bumped to 15.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan (the source-summary surface is reserved for raw-corpus pointers, not standards pages).
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` is modified (the existing engineering-domain pilot is left intact; cross-domain harmonization deferred — see Open Questions).
- [ ] Plan review artifacts present at `scripts/review/results/2026-05-02-plan-DNV-W2-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

<!-- Filled in after the adversarial-review step completes. Per memory `feedback_permission_gate_blocks_cross_review.md`,
     a single-author Claude review is acceptable for planning-only sessions when Codex/Gemini are unavailable. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | (to be filled) |
| Codex | TBD | (to be filled; per memory `feedback_codex_cli_0_124_upstream_regression.md`, may be UNAVAILABLE pending downgrade) |
| Gemini | TBD | (to be filled) |

**Overall result:** TBD

**Revisions made based on review:** none yet — this plan is in `draft` status.

---

## Risks and Open Questions

- **Risk:** Copyright leakage. If a future contributor pastes scope text from the PDF, the denylist may miss novel phrases. **Mitigation:** word-count ceiling ≤500 (matches W1-A) + positive-shape structural test (`test_body_structure_is_whitelisted_only`) + `extraction_policy: metadata-only` frontmatter + `raw_copy_allowed: false` + cross-review on every revision touching `wiki/standards/dnv-*.md`. Reviewers should specifically watch for "DNV-Veritasveien" or "Det Norske Veritas AS" cover-page phrases as the highest-leak-risk strings.
- **Risk:** DNV revision-staleness and rebranding. DNV rebranded `OS-` → `ST-` in 2021 (e.g., DNV-OS-F101 → DNV-ST-F101); the raw PDFs on disk use the legacy `OS-` prefix in their filenames but the publisher's current canonical is `ST-`. **Mitigation:** the dnv-st-f101 page declares both `code_id: DNV-ST-F101` (current) and `legacy_code_id: DNV-OS-F101` (pre-2021), plus `revision_source` URL pointing to the live DNV portal. The test `test_legacy_code_id_only_on_renamed_codes` enforces that only the rebranded code carries the legacy field.
- **Risk:** Cross-wiki duplication. `engineering/wiki/standards/dnv-os-e301.md` already exists (the calc-citation pilot). This plan creates a parallel `engineering-standards/wiki/standards/dnv-os-e301.md` page rather than retro-renaming or moving the existing page. Two same-`code_id` pages may confuse a future resolver. **Mitigation:** the new engineering-standards page carries a `cross_links: ["engineering/wiki/standards/dnv-os-e301.md"]` field that the existing page lacks the `extraction_policy: metadata-only` contract; the resolver should prefer the engineering-standards page when both match. **Open** — see below: harmonization deferred.
- **Risk:** Code-style inconsistency between W1-A and W2-A. The W1-A plan uses lowercase-kebab `code_id` (`api-rp-2a-wsd`); the existing DNV pilot uses uppercase-with-hyphens (`DNV-OS-E301`); this W2-A plan adopts uppercase-with-hyphens to match the existing pilot. The two plans therefore disagree on case. **Mitigation:** flag for harmonization in plan-review; if user prefers a single case-style across all wikis, this plan can be respun in lowercase before approval. Test `test_frontmatter_has_code_id` enforces whichever style the plan commits to (currently uppercase).
- **Risk:** Cross-citation explosion. DNV-RP-C203 is the highest-cited DNV code (160 occurrences in digitalmodel/src/); pages may grow inbound links from many modules. **Mitigation:** the bounded budget keeps each page small; an "Internal callers" section names the ≤5 highest-frequency callers and refers reviewers to a `grep` for the rest.
- **Risk:** Some DNV codes on the priority list (DNV-RP-C201, DNV-ST-N001) have high digitalmodel reference counts (35, 12) but no raw PDF on disk under `/mnt/ace/O&G-Standards/DNV/`. **Mitigation:** these are excluded from this W2-A top-10; they may be addressed in a W2-B follow-up that uses online-resource-registry pointers without a `/mnt/ace` source. Frontmatter for the W2-A pages always cites `/mnt/ace` since every priority code has at least one revision on disk.
- **Open:** **Which 10?** This plan proposes the following ten priority DNV codes, biased by (a) digitalmodel internal-reference frequency, (b) verifiable raw source under `/mnt/ace/O&G-Standards/DNV/`, (c) offshore/pipeline/mooring relevance:
  1. DNV-ST-F101 (2021, 10th Ed; legacy DNV-OS-F101) — submarine pipeline systems (75 + 24 + 13 = 112 internal hits across spelling variants)
  2. DNV-RP-C203 (2024-10) — fatigue design of offshore steel structures (160 hits — highest)
  3. DNV-RP-C205 (2010 on disk) — environmental conditions and environmental loads (63 hits)
  4. DNV-RP-B401 (2011) — cathodic protection design (56 hits + 10 underscore variant)
  5. DNV-OS-E301 (2010 on disk) — position mooring (35 hits; resolves the calc-citation pilot)
  6. DNV-RP-H103 (2010) — modelling and analysis of marine operations (34 hits + 10 no-hyphen variant)
  7. DNV-OS-F201 (2010) — dynamic risers (22 hits)
  8. DNV-RP-F109 (2011) — on-bottom stability of pipelines (19 hits)
  9. DNV-RP-F105 (2006) — free spanning pipelines (19 hits)
  10. DNV-RP-F101 (2010) — corroded pipelines (covers full pipeline-integrity triplet alongside RP-F109/RP-F105)

  **User confirmation required during plan-review.** If different priorities are preferred (e.g. swap DNV-RP-F101 for DNV-RP-F103 cathodic-protection-of-pipelines, or DNV-RP-F116 integrity-management, or DNV-OS-J101 wind-turbine), they can be substituted before approval.
- **Open:** Should the existing `engineering/wiki/standards/dnv-os-e301.md` be retro-renamed/moved/merged into the new `engineering-standards/wiki/standards/dnv-os-e301.md`, or kept as a parallel page in a different domain? The existing pilot is referenced by `.claude/rules/calc-citation-contract.md` directly, so any move risks breaking that link. **Deferred — out of scope for W2-A.** Flag as a follow-up issue post-approval.
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_dnv_pages.py` (one file) or be split per-page? The single-file parametrized form is proposed for tractability; reviewers may prefer per-page files for granular CI signals.
- **Open:** Should the `code_id` case-style be harmonized across W1-A (lowercase) and W2-A (uppercase) before either lands? **Deferred — flag for plan-review.** A harmonization pass could be a small follow-up issue that touches both plans' wiki pages without re-opening the substantive content.

---

## Complexity: T2

**T2** — multi-file documentation work (10 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 14 files), no new code modules, but a real test contract (≥13 parametrized assertions × 10 pages = ~130 effective test cases). Implementation is templated repetition; the design risk is concentrated in (a) the denylist phrasing, (b) the rebrand-bridge legacy_code_id contract, and (c) the cross-wiki duplication question for DNV-OS-E301 — not in algorithm correctness. Matches W1-A's T2 sizing.
