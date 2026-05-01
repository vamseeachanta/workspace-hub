# DORIS Codes & Specs — Standards-Aware Inventory Plan

**Issue:** [#2543](https://github.com/vamseeachanta/workspace-hub/issues/2543)  
**Umbrella:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540)  
**Source-of-record:** `/mnt/ace/doris/codes` (read-only; do not copy raw)  
**Wiki target:** `engineering-standards`  
**Generated:** 2026-04-28 (Terminal 3, overnight Elements wave)

---

## 1. Scope and policy posture

This plan is **metadata-first, licensing-aware**. It promotes a faceted index of the DORIS Codes & Specs corpus into the `engineering-standards` LLM-wiki **without** ingesting raw standards text or scanned pages.

The DORIS `Codes and Specs` corpus is large: 35,197 files / 26.4 GB. The structure indicates it is dominated by third-party licensed standards (TechStreet aggregator drop, BV rules, API/ASME publications) and confidential client/EPC company specifications, both of which carry redistribution risk that the wiki must respect.

Policy posture:

- **Raw stays in `/mnt/ace`.** No PDF, image, OCR text, or extracted clause body is copied into git or wiki.
- **Wiki receives metadata.** Source pointer pages, faceted family indices, and provenance back-links — same shape as #2535 already established at `wiki/sources/elements-doris-codes-specs.md`.
- **Frontmatter contract from #2471 is forward-adopted.** Any standards page emitted under `wiki/standards/` carries `code_id`, `publisher`, `revision`. Where revision is unknown, the page is not emitted; we keep the family at `wiki/sources/` instead until a verified revision is in hand.
- **License risk is conservative.** When in doubt, classify HIGH and skip text promotion. We do not assert a copyright opinion. We do not extract content under fair-use rationale. We do not re-host standards.
- **Boundary against #2227 / #2471 is explicit.** OCIMF Tandem Mooring and CSA Z276 (the #2227 promotion candidates) are **not** present in the DORIS Codes & Specs corpus by token search and remain governed by the `acma-codes` workflow. `acma-codes` is not displaced by this plan.

---

## 2. Source metadata snapshot

Pulled from `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` and the engineering-standards batch JSONL (record `elements-doris-codes-specs`). Counts are exact at corpus level; sub-family counts derived from JSON-line token grep are approximate (token-anywhere on path) and labelled with uncertainty.

| Group | Count | Source |
|---|---:|---|
| Total files | 35,197 | batch JSONL `files` |
| Total bytes | 26,411,658,490 (~26.4 GB) | batch JSONL `bytes` |
| PDF files | 14,101 | batch JSONL `content_kinds.pdf` |
| Image files | 15,722 | batch JSONL `content_kinds.image` |
| Document files (.doc/.docx) | 1,003 | batch JSONL `content_kinds.document` |
| Tabular files (.xls/.xlsx) | 559 | batch JSONL `content_kinds.tabular` |
| CAD files (.dwf etc.) | 125 | batch JSONL `content_kinds.cad` |

### Top-level groupings (exact counts from batch JSONL `top_level_sample`)

| Top-level dir | Files | Notes |
|---|---:|---|
| Company Specs | 15,864 | Likely operator/EPC/client confidential specifications. NDA-bound. |
| TechStreet Drop | 12,266 | Aggregator drop of licensed standards (TechStreet/IHS/S&P Global). Mixed publishers, paid. |
| BV Ship and Offshore Rules | 5,325 | Bureau Veritas published rule set. Free public download for many revisions, copyright BV. |
| API | 746 | American Petroleum Institute publications. Paid copyrighted. |
| Perry's Chemical Engineers Handbook | 311 | McGraw-Hill copyrighted handbook (page scans likely). |
| DnV | 149 | DNV publications. Currently DNV (post-merger) hosts free public PDFs but copyright DNV. |
| ASME | 130 | American Society of Mechanical Engineers publications. Paid copyrighted. |
| DeepStar | 113 | JIP membership-restricted deliverables. |
| **Subtotal** | **34,904** | |
| Residual / unclassified top-level | ~293 | Distribution unknown until a follow-up triage. |

### Embedded-token grep counts (uncertainty: token may match outside `relative_path`; treat ±10%)

| Token | Count |
|---|---:|
| API (\bAPI\b) | 7,516 |
| ASME (\bASME\b) | 5,221 |
| BV / Bureau Veritas | 5,325 |
| DnV / DNV | 150 |
| ISO (\bISO\b) | 107 |
| AWS / AWWA | 36 |
| ABS (\bABS\b) | 14 |
| IEC (\bIEC\b) | 11 |
| ASTM | 7 |
| NACE | 7 |
| NORSOK | 1 |
| OCIMF | 0 |
| CSA (\bCSA\b) | 0 |

OCIMF and CSA are absent from this corpus, confirming the `acma-codes` boundary — the #2227 promotion source lives elsewhere.

---

## 3. Standards families and license-risk matrix

Authoritative companion: `doris-codes-standards-families.tsv` (same directory).

The TSV groups 17 families/buckets with `family / approximate_count_or_sample_count / representative_paths / proposed_wiki_target / license_risk / extraction_policy`. Highlights:

- **CRITICAL risk (no extraction, no clause copy, sometimes no wiki page):** TechStreet Drop, Company Specs, Perry's Chemical Engineers Handbook.
- **HIGH risk (metadata-only landing page allowed when volume justifies):** BV Ship and Offshore Rules, API, ASME, DnV/DNV, DeepStar, ISO, ASTM, ABS, IEC, NACE/AMPP, AWS/AWWA.
- **LOW risk (publicly free):** NORSOK (volume too low here to merit a page).
- **Out of scope:** OCIMF and CSA — covered by #2227 / #2471 inside `acma-codes`.

---

## 4. Proposed wiki output (metadata-only)

Five pages under `knowledge/wikis/engineering-standards/wiki/`, **all metadata-only**, all created behind `status:plan-approved`:

1. **`sources/doris-codes-specs-faceted-index.md`** — extends the existing `sources/elements-doris-codes-specs.md` page with the faceted family table from §2 and links into the per-family pages below. Frontmatter: `domain: engineering-standards`, `tags: [elements-ingest, doris, codes, specifications, faceted-index]`, `sources: [/mnt/ace/doris/codes]`.
2. **`sources/doris-techstreet-drop.md`** — pointer page describing the TechStreet Drop sub-corpus, count, license posture, and a *no-extraction* banner. No publisher list yet (requires per-file metadata sweep that is out of scope).
3. **`sources/doris-company-specs.md`** — pointer page documenting that the bucket exists, its size, and that contents are confidentiality-bound. No client list inlined unless a separate confidentiality matrix is built and approved.
4. **`sources/doris-deepstar.md`** — pointer page for the JIP deliverables. License posture: members-only.
5. **`standards/bv-ship-offshore-rules.md`** — *only* publisher landing page proposed for emission in this pass. Frontmatter `code_id: bv-rules`, `publisher: Bureau Veritas`, `revision: <unknown — page noted as L0 stub>`. Body links out to BV's public Rule Notes portal as canonical. No clause text.

Pages **explicitly NOT proposed** in this pass:

- No per-API-code pages (API 17J, API RP 2A-WSD, etc.) — defer until a separate plan defines internal value-add.
- No per-ASME/DNV/ISO pages — same reason.
- No Perry's Handbook page — too high redistribution risk vs. zero standards-utility for this wiki.
- No standards page lacking a verified `revision` field — would violate #2471.

### Backlink targets

- `knowledge/wikis/engineering-standards/wiki/index.md` is updated to link new sources/ pages once #2543 reaches `status:plan-approved` and an implementation issue is opened.
- `knowledge/wikis/engineering-standards/wiki/log.md` records the ingestion of the faceted index with date and source pointer.
- Cross-link from each new page to its source-of-record absolute path under `/mnt/ace/doris/codes` and to the retained-staging twin under `_from_elements/codes-doris/` for provenance.

---

## 5. Cross-checks against existing governance

- **#2526 (parent ingest):** retained `_from_elements/codes-doris/` staging is the provenance twin; this plan references it but does not modify it.
- **#2534 (retention cleanup):** Perry's Chemical Engineers Handbook and any clearly infringing scanned content should be flagged for #2534's retention review. This plan does not delete anything.
- **#2535 (metadata indexing):** the existing `sources/elements-doris-codes-specs.md` is preserved; the faceted index extends rather than replaces it.
- **#2536 (first-pass deep extraction):** DORIS codes is intentionally NOT in #2536's extraction scope; this plan keeps that boundary.
- **#2227 (OCIMF + CSA promotion):** the corpus does not contain those organizations; #2227 work continues against `acma-codes`.
- **#2471 (CSA-Z276 wiki standards/ pages):** this plan forward-adopts the frontmatter contract (`code_id`, `publisher`, `revision`) for the single BV stub page proposed.
- **#2482 (vendor-derivative deny-list):** no `wiki/sources/` entries inside this plan are proposed for citation in calc modules; this stays a one-way pointer.
- **`acma-codes` boundary:** "Codes & Regulations" remains verify-only and out of scope; this plan does not propose displacing or duplicating `acma-codes`.

---

## 6. Hard guardrails (do-not-do list for any downstream implementer)

1. Do not OCR or text-extract any standards file.
2. Do not copy raw PDFs/images/scans into git or wiki.
3. Do not assert a copyright or fair-use opinion in wiki page bodies; describe license posture only with conservative qualifiers ("paid copyrighted", "members-only JIP", etc.).
4. Do not emit a `wiki/standards/<code_id>.md` page without a verified `revision` value.
5. Do not modify `acma-codes` content; do not modify Terminal 1/2/4 scoped paths.
6. Do not delete or move any file under `/mnt/ace`; #2534 governs retention.
7. Do not self-approve. The plan is left at `status:plan-review`.

---

## 7. Open questions (deferred — recorded here, not blocking review)

- Per-publisher breakdown inside `TechStreet Drop` — would require iterating filenames; out of scope without legal review.
- Per-client breakdown inside `Company Specs` — requires confidentiality matrix; out of scope.
- Whether the residual ~293 unclassified top-level entries hide additional standards families (e.g., NORSOK or NACE collections that would change risk posture) — defer to a separate tighter triage if the residual proves substantive.
- Whether DnV dir count (149) overlaps with DNV mentions inside Company Specs (token count 150 — close to top-level dir alone; embedded references appear minimal).
- Volume basis for ASME embedded count (5,221) and API embedded count (7,516) — likely heavy substring inflation through long pathnames; do not treat as "files" counts.

---

## 8. Acceptance gates for the implementation issue spawned from this plan

- [ ] Faceted-index page created under `wiki/sources/` and linked from `wiki/index.md`.
- [ ] Three pointer pages (`doris-techstreet-drop.md`, `doris-company-specs.md`, `doris-deepstar.md`) created with explicit no-extraction banners.
- [ ] BV publisher landing page created or explicitly deferred with rationale.
- [ ] All pages carry `domain`, `tags`, `added`, `last_updated` per `engineering-standards/CLAUDE.md` schema.
- [ ] `wiki/log.md` updated.
- [ ] No raw bytes from `/mnt/ace/doris/codes` appear under git ls-files.
- [ ] PR description cross-links #2526, #2534, #2535, #2536, #2540, #2227, #2471.
- [ ] Approval boundary explicit: this plan does not authorize ingestion; only the implementation issue does.
