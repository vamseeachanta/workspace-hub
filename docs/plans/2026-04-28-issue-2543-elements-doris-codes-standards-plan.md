# Plan for #2543: feat(llm-wiki) — plan DORIS codes/specs standards metadata promotion

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2543
> **Review artifacts:** _pending — adversarial review not yet run for this overnight wave; provider verdicts to be filed under `scripts/review/results/2026-04-28-plan-2543-<claude|codex|gemini>.md` once a permitted reviewer session runs._

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` — 41,561 records; bucket-filter shows 35,197 DORIS-codes records with full path/extension/content_kind metadata.
- Found: `.planning/intel/elements-to-llm-wiki/batches/engineering-standards.jsonl` — 1 record (`elements-doris-codes-specs`) with corpus totals, top-level sample, and content-kind histogram.
- Found: `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md` — bucket table places DORIS codes at `extract_priority: metadata-only`.
- Found: `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — pre-existing source pointer page from #2535.
- Gap: no faceted family index page exists; no per-publisher landing pages exist; `wiki/standards/` is empty for this corpus.

### Standards
| Standard | Status | Source |
|---|---|---|
| BV Ship and Offshore Rules | gap (no wiki page yet) | `engineering-standards/wiki/standards/` empty; corpus dir holds 5,325 files |
| API (RP/SPEC) — corpus-present | gap (metadata-only proposed) | corpus dir holds 746 top-level files; embedded mentions ~7,516 |
| ASME — corpus-present | gap (metadata-only proposed) | corpus dir holds 130 top-level files; embedded mentions ~5,221 |
| DnV/DNV — corpus-present | gap (cross-link DNV-OS-E301 pilot in `digitalmodel`) | corpus dir holds 149 top-level files |
| OCIMF Tandem Mooring | not applicable to this corpus | 0 OCIMF tokens in DORIS codes; covered by #2227 / `acma-codes` |
| CSA Z276 | not applicable to this corpus | 0 CSA tokens in DORIS codes; covered by #2227 / #2471 |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering-standards/CLAUDE.md` — conventions and standards-page frontmatter contract (`code_id`, `publisher`, `revision`).
- `knowledge/wikis/engineering-standards/wiki/index.md` — current index references only the existing #2535 source page.
- `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — already documents the bucket; this plan extends rather than duplicates.
- No `engineering-standards` standards/* pages exist yet; no contradiction risk against an existing entry.

### Documents consulted
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/` — prompt pack governing this overnight wave; allowed/forbidden writes enforced.
- `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md` — companion inventory plan (this terminal's deeper artifact).
- `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` — family/license-risk matrix.
- `.claude/rules/calc-citation-contract.md` — confirms `wiki/sources/*` are deny-list for calc citations; this plan deliberately does NOT route any calc citations into DORIS source pages.
- Issue #2540 (umbrella), #2526 (parent ingest), #2534 (retention), #2535 (metadata indexing), #2536 (first-pass extraction), #2227 (OCIMF/CSA promotion), #2471 (CSA-Z276-only).

### Gaps identified
- No faceted family index for DORIS codes/specs in `engineering-standards` wiki.
- No publisher-level landing page for BV Ship and Offshore Rules.
- No metadata pointer pages for `TechStreet Drop`, `Company Specs`, `DeepStar` sub-corpora.
- No documented boundary statement against `acma-codes` `Codes & Regulations` in this wiki.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-28 via `gh issue view`):
- `#2543` — OPEN — feat(llm-wiki): plan DORIS codes/specs standards metadata promotion
- `#2540` — OPEN — epic(llm-wiki): overnight Elements corpus planning wave after #2536
- `#2227` — OPEN (status:plan-approved) — feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis

**File existence** (workspace reads, 2026-04-28):
- EXISTS: `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl`
- EXISTS: `.planning/intel/elements-to-llm-wiki/batches/engineering-standards.jsonl`
- EXISTS: `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- EXISTS: `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md`
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/` (empty directory — no pages yet)
- MISSING (this plan does NOT create — implementation issue would): `knowledge/wikis/engineering-standards/wiki/sources/doris-codes-specs-faceted-index.md`
- MISSING (defer): `knowledge/wikis/engineering-standards/wiki/standards/bv-ship-offshore-rules.md`

**Token counts** (`Grep` over `elements-ingested-files.jsonl`, 2026-04-28; "occurrence-anywhere on JSON line" — uncertainty band ±10%):
```
ASTM   :     7    ISO   :   107    API   : 7516    ASME  : 5221
DnV    :   150    NORSOK:     1    OCIMF :    0    CSA   :    0
ABS    :    14    IEC   :    11    NACE  :    7    BV    : 5325
DeepStar:  113    Company Specs: 15864    TechStreet: 12266
```

**Top-level dir histogram** (from batch JSONL `top_level_sample`):
```
Company Specs (15864), TechStreet Drop (12266), BV Ship and Offshore Rules (5325),
API (746), Perry's Chemical Engineers Handbook (311), DnV (149), ASME (130),
DeepStar (113); subtotal 34,904 of 35,197 (residual ≈ 293).
```

<!-- Distinct source count: issue body (1) + #2540 (2) + #2227 (3) + intel JSONL (4) + engineering-standards CLAUDE.md (5) + .claude/rules/calc-citation-contract.md (6). 6 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` |
| Inventory plan | `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md` |
| Families/risk TSV | `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` |
| Terminal-3 result | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md` |
| Future implementation issue | (not created here) — would spawn `feat(llm-wiki): emit DORIS codes faceted index + 3 pointer pages` |
| Future wiki updates | `knowledge/wikis/engineering-standards/wiki/sources/doris-codes-specs-faceted-index.md` (and 3 pointer pages, 1 BV stub) — emitted only after `status:plan-approved` |
| Plan review — Claude | `scripts/review/results/2026-04-28-plan-2543-claude.md` (pending) |
| Plan review — Codex | `scripts/review/results/2026-04-28-plan-2543-codex.md` (pending) |
| Plan review — Gemini | `scripts/review/results/2026-04-28-plan-2543-gemini.md` (pending) |

---

## Deliverable

A reviewable, metadata-only promotion plan for the DORIS Codes & Specs corpus that, when approved, authorizes a small set of `engineering-standards` wiki pages (one faceted index, three pointer pages, optionally one BV publisher stub) without copying or text-extracting any third-party standards or confidential client specifications.

---

## Pseudocode

```
PLAN-AUTHORIZED IMPLEMENTATION (deferred — runs only after status:plan-approved):

create wiki/sources/doris-codes-specs-faceted-index.md:
    frontmatter (title, tags, added, last_updated, sources, domain)
    body: faceted family table from §2 of inventory plan
    body: link to source-of-record /mnt/ace/doris/codes (no embed)
    body: cross-link existing sources/elements-doris-codes-specs.md (#2535)
    body: explicit no-extraction banner

create wiki/sources/doris-techstreet-drop.md:
    frontmatter
    body: existence note + count + license posture (CRITICAL)
    body: no publisher list (deferred)

create wiki/sources/doris-company-specs.md:
    frontmatter
    body: existence note + count + confidentiality posture (CRITICAL)
    body: no client list (deferred)

create wiki/sources/doris-deepstar.md:
    frontmatter
    body: existence note + count + JIP-membership posture (HIGH)

if BV stub viable (revision can be sourced from BV public portal):
    create wiki/standards/bv-ship-offshore-rules.md:
        frontmatter (code_id: bv-rules, publisher: Bureau Veritas, revision: <verified>)
        body: outbound link to BV Rule Notes portal (canonical)
        body: no clause text

update wiki/index.md to list new sources/* entries (append rows)
append wiki/log.md entry with date + page list + source pointer
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` | this plan |
| Create | `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md` | metadata-only inventory and license-risk matrix (companion) |
| Create | `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` | machine-readable families/risk table |
| Create | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md` | overnight-wave result summary |
| (DEFERRED — only if approved) Create | `knowledge/wikis/engineering-standards/wiki/sources/doris-codes-specs-faceted-index.md` | faceted family index page |
| (DEFERRED — only if approved) Create | `knowledge/wikis/engineering-standards/wiki/sources/doris-techstreet-drop.md` | pointer page for licensed-aggregator drop |
| (DEFERRED — only if approved) Create | `knowledge/wikis/engineering-standards/wiki/sources/doris-company-specs.md` | pointer page for confidential client specs bucket |
| (DEFERRED — only if approved) Create | `knowledge/wikis/engineering-standards/wiki/sources/doris-deepstar.md` | pointer page for JIP deliverables |
| (DEFERRED — only if approved + revision verifiable) Create | `knowledge/wikis/engineering-standards/wiki/standards/bv-ship-offshore-rules.md` | BV publisher landing stub |
| (DEFERRED — only if approved) Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | append new sources/* rows |
| (DEFERRED — only if approved) Modify | `knowledge/wikis/engineering-standards/wiki/log.md` | append ingest entry |

This plan does **not** authorize emission of the deferred files. Those land in a separate implementation PR after `status:plan-approved` is set by the user.

---

## TDD Test List

The deliverables in this plan are documentation/metadata pages; the relevant verification is structural rather than numerical. Tests are written against the page set as a whole.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_no_raw_bytes_under_git | no PDF/JPG/DWF copied from `/mnt/ace/doris/codes` is tracked in git | `git ls-files` filtered by `.pdf|.jpg|.png|.dwf|.docx|.doc|.xls|.xlsx|.htm|.db` under `knowledge/wikis/engineering-standards/` | empty result |
| test_frontmatter_required_fields | every new wiki page has required frontmatter (`title`, `tags`, `added`, `last_updated`, `domain`) | each new `.md` page | YAML parse passes; required keys present |
| test_standards_page_revision_present | any page under `wiki/standards/` carries `code_id`, `publisher`, `revision` | `wiki/standards/*.md` | each YAML parse contains all three keys with non-empty values |
| test_index_links_resolve | every link added to `wiki/index.md` resolves to an existing file | parsed index links | each target file exists |
| test_no_extraction_banner_present | each new pointer page contains an explicit no-extraction banner | each new `wiki/sources/doris-*` page | substring `no-extraction` or `metadata-only` is present |
| test_acma_codes_boundary_note | the faceted index documents the `acma-codes` boundary | faceted-index page body | substring referencing `acma-codes`, `OCIMF`, `CSA`, and #2227 |
| test_provenance_backlinks_present | each pointer page links to its source-of-record absolute path | each new pointer page | substring `/mnt/ace/doris/codes` present |

For the planning artifacts in this PR, the analogous gate is `test -s` on each output file (run during overnight verification step).

---

## Acceptance Criteria

- [ ] Plan file exists at `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` and is non-empty.
- [ ] Inventory plan exists at `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md` and is non-empty.
- [ ] Families TSV exists at `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv` and is non-empty.
- [ ] Plan is metadata-first and licensing-aware: zero proposed copy of raw standards content into git/wiki.
- [ ] Standards families are grouped from path/name metadata with explicit uncertainty bands.
- [ ] Plan documents the `acma-codes` boundary against `Codes & Regulations` and confirms #2227 / #2471 corpora are not present here.
- [ ] No raw copyrighted standards content is proposed for git/wiki ingestion.
- [ ] Issue is left at `status:plan-review`; plan is **not** self-approved.
- [ ] Result summary file exists under `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/`.
- [ ] (Deferred to implementation PR) All TDD-test rows above pass on the eventual wiki page set.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | _pending_ | overnight wave dispatched; review not yet run for #2543 |
| Codex | _pending_ | codex-cli 0.124.0 stdin-hang regression open (#2479) — fall back to Codex web/Workbench if `codex exec` blocks |
| Gemini | _pending_ | known sandbox overlay-blindness risk for sparse-checkout paths; verify any "file missing" claims with `git ls-files` before accepting |

**Overall result:** _pending — plan-review pending adversarial round; no self-approval._

Revisions made based on review:
- (to be appended after reviewers run)

---

## Risks and Open Questions

- **Risk:** TechStreet Drop license terms vary per publisher; even *metadata* pointer pages could surface copyrighted titles inadvertently. Mitigation: keep the pointer page free of full standard titles; reference only the bucket and count.
- **Risk:** Company Specs are NDA-bound and may include client identifiers in folder names; even listing top-level subfolders could leak. Mitigation: do **not** enumerate sub-folders in any wiki page; refer to the source-of-record path only.
- **Risk:** BV publisher revision may be ambiguous (BV publishes consolidated rule notes that are reissued semi-annually). Mitigation: do not emit the BV standards page if a verified `revision` is not in hand — leave at the pointer-page level.
- **Risk:** Residual ~293 unclassified top-level entries may hide additional standards families. Mitigation: documented as an open question; not blocking for this plan.
- **Risk:** Past-tense drift (per memory: `feedback_plan_past_tense_artifact_claims.md`) — this plan describes proposed wiki pages as deferred, not committed. The artifact map labels them DEFERRED.
- **Open:** Should the plan include a Perry's Handbook removal recommendation routed to #2534? (deferred to retention review owner)
- **Open:** Should DnV pages cross-link to the DNV-OS-E301 citation pilot in `digitalmodel`, or only to the DNV portal? (deferred to implementation issue)

---

## Approval Boundary

This plan is left at `status:plan-review`. It does **not** carry `status:plan-approved`. The overnight terminal that produced it does not, and must not, set the approval label. Per `feedback_never_offer_to_self_label_plan_approved.md`, that gate is user-in-loop and load-bearing across session boundaries.

---

## Complexity: T2

**T2** — multiple new planning artifacts plus a deferred multi-file wiki ingestion (5 pages + index/log update). No code; all metadata. Cross-corpus boundary check against `acma-codes` is non-trivial.
