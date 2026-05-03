# Plan for LLM-Wiki Completeness W1-A: Bounded API Code Body Summary Promotion

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2586
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Sibling precedent:** [#2559](https://github.com/vamseeachanta/workspace-hub/issues/2559) (OCIMF Tandem) — bounded preview pattern this plan inherits
> **Path sanction (API):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for engineering-standards domain). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision **for CSA-Z276 specifically** (verified per memory `project_wiki_standards_path_decision.md`); it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple. **(Amended 2026-05-02 per W3-C erratum.)**
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`)
> **Review artifacts:** scripts/review/results/2026-05-02-plan-API-W1-claude.md | …-codex.md | …-gemini.md (to be produced by main session)
>
> _This plan was amended on 2026-05-02 (W3-C erratum, #2596) to correct an over-citation of #2471 as a generalized path-sanction. The frontmatter-contract citations to #2471 are unchanged; the path-sanction has been re-anchored to the local engineering-standards `CLAUDE.md` schema._

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). This is the downstream consumer that will resolve the wiki pages this plan will create.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/registry.py` — companion resolver.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — prose-level pilot reference cited by `.claude/rules/calc-citation-contract.md` for **DNV-OS-E301** mooring safety factors (NOT API RP 2SK). The actual sole `Citation(...)` constructor in `digitalmodel/src/` lives at `digitalmodel/src/digitalmodel/citations/registry.py:52`; no Citation instance has yet been wired into `mooring_design.py`. The api-rp-2sk wiki page proposed below is therefore *future-needed* by calls that will be wired post-W1-A, not by a live caller today.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/calm_buoy_fatigue.py` — references API RP 2SK S-N curves.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/component_database.py` — references API RP 2SK Section 6.2 / Table 1.
- Gap: zero summary-promotion runner exists for the `/mnt/ace/O&G-Standards/API/` corpus; no wiki page yet exists for any of the 10 priority codes proposed below (the only existing API standards page is `wiki/standards/api-17e.md`, a metadata stub).

### Standards

| Standard | Status | Source |
|---|---|---|
| API RP 2A-WSD (22nd Ed, 2014; reaffirmed R2025) | gap (raw present in /mnt/ace; no wiki page) | `data/document-index/standards-transfer-ledger.yaml` `id: API-RP-2A-WSD`; `/mnt/ace/O&G-Standards/API/Recommended-Practice/API_RP_2A-WSD_22nd_Edition_Nov_2014.pdf` |
| API STD 2RD (3rd Ed, 2025; supersedes RP 2RD) | gap | ledger `id: API-STD-2RD`; `/mnt/ace/.../Standards/API_STD_2RD_2nd_Ed_(2013)_Dynamic_Risers_for_Floating_Production_Systems.pdf` (3rd Ed referenced via public publisher metadata only) |
| API RP 2SK (3rd Ed, 2005 (R2008 addendum)) | gap (cited in code but no wiki standards page) | `/mnt/ace/.../Recommended-Practice/API_RP_2SK_3rd_Ed_(2005)…pdf` + `…_Addendum_1_(2007)…pdf`; 66 occurrences in digitalmodel |
| API RP 2GEO (1st Ed, 2011 + Addendum 1, 2014) | gap | `/mnt/ace/.../Recommended-Practice/API_RP_2GEO_1st_Edition_Addendum_1,_Oct_2014.pdf` |
| API RP 2MET (1st Ed, 2014) | gap | `/mnt/ace/.../Recommended-Practice/API_RP_2MET_1st_Edition_Nov_2014.pdf` |
| API RP 16Q (drilling risers) | gap | `/mnt/ace/.../Recommended-Practice/API_RP_16Q_(Searchable).pdf` |
| API RP 17B (5th Ed, 2014; Flexible pipe) | gap | `/mnt/ace/.../Recommended-Practice/API_RP_17B_5th_Ed_(2014)_Flexible_Pipe.pdf` |
| API SPEC 17J (4th Ed, 2014; Unbonded flexible pipe) | gap | `/mnt/ace/.../Specifications/API_SPEC_17J_4rd_Ed_(2014)_Unbonded_Flexible_Pipe.pdf` |
| API SPEC 5L (Line pipe) | gap | `/mnt/ace/.../Specifications/API_SPEC_5L_44th_Ed_(2007)_Line_Pipe.pdf` |
| API RP 1111 (4th Ed, 2009; offshore hydrocarbon pipelines, LSD) | gap; ledger row mismatch — existing ledger ID is `API-RP-1111-3RD-ED` (3rd Ed); a new ledger row `API-RP-1111-4TH-ED` is required for the 4th Ed source on disk | `/mnt/ace/.../Recommended-Practice/API_RP_1111_4th_Ed_(2009)_Design,_Construction,_Operation,_and_Maintenance_of_Offshore_Hydrocarbon_Pipelines_(Limit_State_Design).pdf` |

### LLM Wiki pages consulted

- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing API standards page; metadata stub with `code_id: api-17e`, `publisher: API`, `revision: public-metadata-required-before-citation-use`. Pattern this plan will replicate ten times for the priority codes.
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/index.md` — page_count=5, source_count=5; will need an "## Standards" section appended.
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply.
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — Elements ingest catalog already references the broader DORIS standards corpus; this plan's API subset is a complementary path through `/mnt/ace/O&G-Standards/API/` (146 entries top-level; 517 PDFs total at depth 3).
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` — cross-domain precedent (OCIMF page in engineering wiki, not engineering-standards) for bounded summary structure under #2559.

### Documents consulted

- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-23-issue-2364-batch-pack-1-api-standards-portal-promotion.md` — Batch Pack 1 (online API portal metadata, not raw PDFs); shares the bounded-stub pattern, scopes are disjoint.
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — recent precedent for bounded preview-only promotion; this plan inherits the no-raw-text and frontmatter contracts.
- `/mnt/local-analysis/workspace-hub/data/document-index/standards-transfer-ledger.yaml` — already contains canonical IDs for every priority code (`API-RP-2A-WSD`, `API-STD-2RD`, `API-RP-1111-3RD-ED`, `API-SPEC-17J-4RD-ED`, etc.); the wiki promotion will not invent new IDs.
- `/mnt/local-analysis/workspace-hub/data/document-index/online-resource-registry.yaml` — does not currently list per-API-code entries (only generic `data_api` references); the new wiki pages may eventually be cross-linked to publisher portal URLs, but that is out of scope for W1-A.
- `.claude/rules/calc-citation-contract.md` — the citation contract this plan exists to satisfy: every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter. Currently 9 of the 10 priority codes have no such page.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (referenced via project CLAUDE.md) — the issue-planning workflow this plan obeys.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — #2471 codified the path-routing decision **for CSA Z276 specifically**; per memory the routing principle generalizes only to {marine-engineering, engineering, naval-architecture} via each wiki's local CLAUDE.md schema, not via #2471 itself. (Amended 2026-05-02 per W3-C erratum.)
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; this plan keeps phrase lists narrowly scoped.

### Gaps identified

- No wiki standards pages exist for: API RP 2A-WSD, API STD 2RD, API RP 2SK, API RP 2GEO, API RP 2MET, API RP 16Q, API RP 17B, API SPEC 17J, API SPEC 5L, API RP 1111.
- Calc module `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/component_database.py` cites API RP 2SK at runtime; the citation cannot today be resolved against a wiki standards page (no such page exists).
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any API page (the OCIMF Tandem test at `tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py` is the pattern to extend, narrowly).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2559` — OPEN — "feat(acma-codes): promote OCIMF Tandem preview into LLM-wiki source summary"
- `#2373` — OPEN — "feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion"

**File existence** (`ls` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/API/` (146 top-level entries; 517 PDFs at depth 3 via `find -maxdepth 3 -type f \( -name "*.pdf" -o -name "*.PDF" \)`)
- EXISTS: `/mnt/ace/O&G-Standards/API/Recommended-Practice/`, `Specifications/`, `Standards/`, `Bulletins/`, `Technical-Reports/`
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing API standards page)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2a-wsd.md`, `api-std-2rd.md`, `api-rp-2sk.md`, `api-rp-2geo.md`, `api-rp-2met.md`, `api-rp-16q.md`, `api-rp-17b.md`, `api-spec-17j.md`, `api-spec-5l.md`, `api-rp-1111.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_api_pages.py`
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (the resolver target)

**Line excerpts** (existing OCIMF guard pattern this plan inherits — `tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py`):
```
RAW_OCR_DENYLIST = (
    "First Published 2009",
    "ISBN 978 1 905331 62 8",
    ...
)
def test_wiki_page_does_not_contain_raw_ocr_phrases() -> None:
    text = _read_page_or_skip()
    leaks = [phrase for phrase in RAW_OCR_DENYLIST if phrase in text]
    assert leaks == []
```

**Internal-reference frequency proof** (`grep -rohE "API[ _-]?(RP|Spec|Std|TR|BUL)[ _-]?[0-9A-Za-z]+" digitalmodel/src/ | sort | uniq -c | sort -rn | head -10`):
```
    100 API RP 1111
     68 API RP 2A
     66 API RP 2SK
     47 API_RP_1111
     32 API RP 2RD
     23 API RP 2GEO
     17 API RP 16Q
     15 API TR 5C3
     12 API_RP_2RD
     10 API RP 1632
```

**Public-revision evidence (web)**:
- API RP 2A-WSD — 22nd Edition (Nov 2014), reaffirmed R2025: <https://store.accuristech.com/standards/api-rp-2a-wsd-r2025>
- API STD 2RD — Third Edition released 2025; supersedes RP 2RD: <https://www.worldoil.com/news/2025/10/23/api-strengthens-offshore-safety-standards-with-new-updates/>
- (Additional URL pointers will be added per page; these two are anchor citations for the priority subset.)

<!-- Distinct sources counted: existing repo code (1), standards ledger (2), wiki pages (3), prior plans (4), citation rule (5), project memory (6), web (7). 7 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2a-wsd.md` |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/api-std-2rd.md` |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2sk.md` |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2geo.md` |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2met.md` |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-16q.md` |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-17b.md` |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/api-spec-17j.md` |
| Wiki page (9) | `knowledge/wikis/engineering-standards/wiki/standards/api-spec-5l.md` |
| Wiki page (10) | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-1111.md` |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Test contract | `tests/knowledge/test_engineering_standards_api_pages.py` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-API-W1-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-API-W1-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-API-W1-gemini.md` |

---

## Deliverable

Ten new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority API code), each carrying #2471-compliant frontmatter and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/API/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream calc modules can resolve `Citation` instances for the ten most-referenced API codes without any verbatim source text entering git.

---

## Pseudocode

The work is a templated 10x repetition. Each new wiki page will follow the same skeleton:

```
---
title: "<Full standard name> — bounded summary"
tags: ["api", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: <kebab-case id matching filename without extension>
publisher: API
revision: "<edition + year, OR 'public-metadata-required-before-citation-use' if uncertain>"
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
- Publisher catalog: <URL>
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code>

## Cross-references
- [[api-17e]] (when applicable)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file will use a parametrized fixture iterating over the 10 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2a-wsd.md` | Bounded summary for API RP 2A-WSD (22nd Ed, R2025) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-std-2rd.md` | Bounded summary for API STD 2RD (3rd Ed, 2025) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2sk.md` | Bounded summary for API RP 2SK mooring (resolver for `mooring_design.py` pilot) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2geo.md` | Bounded summary for API RP 2GEO geotech foundations |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-2met.md` | Bounded summary for API RP 2MET metocean |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-16q.md` | Bounded summary for API RP 16Q drilling risers |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-17b.md` | Bounded summary for API RP 17B flexible pipe |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-spec-17j.md` | Bounded summary for API SPEC 17J unbonded flexible pipe |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-spec-5l.md` | Bounded summary for API SPEC 5L line pipe |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/api-rp-1111.md` | Bounded summary for API RP 1111 offshore hydrocarbon pipelines (LSD); maps to ledger ID `API-RP-1111-4TH-ED` (added in this plan via the new ledger row below) |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 10 new rows; bump `page_count` to 15 |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add new ledger row `API-RP-1111-4TH-ED` so the new `api-rp-1111.md` wiki page (4th Ed, 2009) maps to a real ledger ID instead of the existing 3rd-Ed-only `API-RP-1111-3RD-ED` row |
| Create | `tests/knowledge/test_engineering_standards_api_pages.py` | Test contract: frontmatter, no-raw-text, citation resolvability |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_api_pages.py`. Each test parametrized over the 10 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 10 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per #2471 | YAML frontmatter | `code_id` non-empty, kebab-case, matches filename stem |
| `test_frontmatter_has_publisher_api` | publisher discipline | YAML frontmatter | `publisher == "API"` |
| `test_frontmatter_has_revision` | revision presence (per .claude rule 2) | YAML frontmatter | `revision` non-empty string |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow phrase set; see Open Questions) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | 100 < N < 500 | page body | bounded preview budget (tightened from 1500 to 500 to harden against clause-excerpt bleed-through; bare-minimum scope/why/where/cross-refs fits well under 500 words) |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only the four allowed structural sections | page body | top-level `##` headings are exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}`; any other top-level section (e.g. "Clauses", "Formulas", "Tables", "Excerpt") fails the test |
| `test_links_only_pointer_to_mnt_ace` | the page mentions the raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/API/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolution | `Citation(code_id=<id>, publisher="API", revision=<rev>, section="placeholder", wiki_path=<path>)` constructs without error | `CitationValidationError` not raised; `wiki_path` exists |
| `test_index_lists_all_ten` | wiki index updated | `index.md` contents | each of the 10 page links present in the "## Standards" section |

`RAW_TELLTALE_PHRASES` will be a small, narrowly-scoped list (≤15 entries) drawn from API publication front-matter conventions — e.g. "American Petroleum Institute", "1220 L Street, NW", "Washington, DC 20005", "Reproduction or translation of any part of this work" — phrases that would appear only if raw cover/copyright pages were copied. The list will deliberately exclude the standard's title (which is allowed) and code identifier (which is required).

---

## Acceptance Criteria

- [ ] All ten new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_api_pages.py -v` passes (all parametrized cases green).
- [ ] No new test in `tests/knowledge/` regresses: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No raw-PDF clause text is committed: a `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/api-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated, kebab-case `code_id` matches filename stem).
- [ ] Citation downstream-resolution check (single canonical revision string per page; the page's frontmatter `revision` and the `Citation(...)` argument MUST match verbatim, since `validate_citation` does literal-equality on the revision string per `digitalmodel/src/digitalmodel/citations/schema.py:127-132`):
  - For each page where a real publisher revision is asserted in frontmatter, `python -c "from digitalmodel.citations.schema import Citation; Citation(code_id='<id>', publisher='API', revision='<frontmatter-revision-verbatim>', section='<placeholder>', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md')"` succeeds without error. Concrete example: `api-rp-2sk.md` will use `revision: "3e-2005-r2008"` in BOTH frontmatter AND the `Citation(...)` call.
  - Pages whose revision cannot be pinned to a verifiable publisher edition at write-time MUST set `revision: "public-metadata-required-before-citation-use"` in frontmatter AND be excluded from this resolution check (the test parametrization will skip them with a `pytest.mark.skip(reason="stub-only, revision pending")`).
  - The resolver module's existence is independently verified at `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` (this is an attestation about the resolver module only; it does NOT attest that any wiki page already exists — those are created by this plan).
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 10 new pages under a "## Standards" section; `page_count` bumped to 15.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan (the source-summary surface is reserved for raw-corpus pointers, not standards pages).
- [ ] Plan review artifacts present at `scripts/review/results/2026-05-02-plan-API-W1-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MINOR | 6 findings — calc-citation pilot misattribution; API RP 2SK edition mismatch; ledger ID/edition mapping; revision-string consistency hidden hazard; body-bleed test denylist insufficient; parenthetical implies non-existent wiki page |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479); fanout dispatch hung; killed at 2026-05-02T12:21Z |
| Gemini | UNAVAILABLE | gemini CLI cwd=/tmp sandbox cannot resolve repo paths (`/tmp/knowledge/wikis/...` not found); err logged to scripts/review/results/.failed-fanout-2026-05-02/ |

**Overall result:** PASS-with-revisions (MINOR fixes applied 2026-05-02)

**Revisions made based on review:**
- Finding 1 (line ~21): rewrote `mooring_design.py` description as a prose-level pilot reference for DNV-OS-E301 (NOT API RP 2SK), pointed to the actual `Citation(...)` constructor at `citations/registry.py:52`, and clarified the api-rp-2sk page is future-needed not live-needed.
- Finding 2 (line ~32): corrected API RP 2SK edition to "3rd Ed, 2005 (R2008 addendum)" matching the on-disk filename; also corrected the Open-Questions priority-list entry (line ~283) to the same string.
- Finding 3 (line ~39 + Files-to-Change): annotated the API RP 1111 ledger row mismatch (`API-RP-1111-3RD-ED` exists; new `API-RP-1111-4TH-ED` row required), added a new Files-to-Change row to add the ledger entry, and annotated the `api-rp-1111.md` Create row with its target ledger ID.
- Finding 4 (Acceptance Criterion line ~245): rewrote the Citation downstream-resolution check to commit to a single canonical revision string per page used both in frontmatter and `Citation(...)`; pinned `api-rp-2sk.md` to `revision: "3e-2005-r2008"`; added explicit skip-path for stub-only pages (`revision: "public-metadata-required-before-citation-use"`).
- Finding 5 (TDD line ~230 + Risks line ~271): tightened body word-count ceiling from 1500 to 500; added positive-shape `test_body_structure_is_whitelisted_only` enforcing the structural-section whitelist; updated the corresponding mitigation in Risks.
- Finding 6 (Acceptance Criterion line ~250): rephrased the parenthetical to attest only the resolver module's existence, not the wiki page's existence (the page is created by this plan and does not exist yet).

**Provenance:** Single-author Claude review (per memory `feedback_permission_gate_blocks_cross_review.md`); Codex/Gemini both unavailable today. The single-provider basis is acceptable under the documented fallback for planning-only sessions.

---

## Risks and Open Questions

- **Risk:** Copyright leakage. If a future contributor pastes scope text from the PDF, the denylist may miss novel phrases. **Mitigation:** word-count ceiling tightened to ≤500 (was 1500 in r1; reduced after adversarial review #2586-r1 Finding 5) + positive-shape structural test (`test_body_structure_is_whitelisted_only`) + extraction_policy frontmatter + `raw_copy_allowed: false` + cross-review on every revision touching `wiki/standards/api-*.md`.
- **Risk:** Revision staleness. API publishes errata frequently (e.g. RP 2A-WSD has 21st Ed Errata + Supplements 2&3, plus R2025 reaffirmation). The bounded summaries will state the *anchor* edition explicitly; downstream `Citation.revision` must match. **Mitigation:** `revision_source` frontmatter field carries either a URL or `/mnt/ace` path so reviewers can re-verify.
- **Risk:** Cross-citation explosion. Pages may grow inbound links from many digitalmodel modules. **Mitigation:** the bounded budget keeps each page small; an "Internal callers" section names the ≤5 highest-frequency callers and refers reviewers to a `grep` for the rest.
- **Risk:** ID-collision with the existing `api-17e.md` stub naming convention. The stub uses `code_id: api-17e` (no `spec/rp/std` prefix), but the new pages will use `api-rp-2a-wsd`, `api-spec-17j`, etc. — a richer scheme. **Mitigation:** the pre-existing `api-17e.md` stays unchanged; the plan does not retro-rename it. Reviewers may flag this as inconsistency in W1-A review and we may resolve in a follow-up issue (out of scope here).
- **Open:** **Which 10?** This plan proposes the following ten priority codes, biased by (a) digitalmodel internal-reference frequency, (b) verifiable raw source under `/mnt/ace`, (c) E&P upstream/offshore relevance:
  1. API RP 2A-WSD (22nd Ed, R2025) — fixed offshore platforms, WSD
  2. API STD 2RD (3rd Ed, 2025) — dynamic risers for FPS (supersedes RP 2RD)
  3. API RP 2SK (3rd Ed, 2005 (R2008 addendum)) — stationkeeping; future Citation target (no live caller wired today)
  4. API RP 2GEO (1st Ed, 2011 + Add. 1, 2014) — geotechnical/foundation design
  5. API RP 2MET (1st Ed, 2014) — metocean design conditions
  6. API RP 16Q — drilling riser systems
  7. API RP 17B (5th Ed, 2014) — flexible pipe
  8. API SPEC 17J (4th Ed, 2014) — unbonded flexible pipe
  9. API SPEC 5L (44th Ed) — line pipe
  10. API RP 1111 (4th Ed, 2009) — offshore hydrocarbon pipelines (LSD); highest internal reference count (100)

  **User confirmation required during plan-review.** If different priorities are preferred (e.g. swap API RP 1111 for API SPEC 17D wellhead/Christmas tree, or include API TR 5C3 which has 23 internal hits), they can be substituted before approval.
- **Open:** Should the existing `api-17e.md` metadata stub be retro-renamed to `api-spec-17e.md` for naming consistency, or left as-is for backwards compatibility? Flag for reviewer.
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_api_pages.py` (one file) or be split per-page (`test_engineering_standards_api_<id>.py`, ten files)? The single-file parametrized form is proposed for tractability; reviewers may prefer per-page files for granular CI signals.

---

## Complexity: T2

**T2** — multi-file documentation work (10 new wiki pages + 1 test file + 1 index update + 1 docs/plans/README.md update = 13 files), no new code modules, but a real test contract (≥10 parametrized assertions × 10 pages = ~100 effective test cases). Implementation is templated repetition; the design risk is concentrated in the denylist phrasing and the frontmatter schema choice, not in algorithm correctness.
