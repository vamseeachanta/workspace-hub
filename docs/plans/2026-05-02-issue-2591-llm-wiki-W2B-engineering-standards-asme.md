# Plan for LLM-Wiki Completeness W2-B: Bounded ASME Code Body Summary Promotion

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2591
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Sibling precedent (W1-A):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) — bounded API code-body summary promotion (this plan inherits the same shape; in-progress organizational precedent for `wiki/standards/<code-id>.md` routing under engineering-standards wiki)
> **Path sanction (re-anchored after r1 review):**
>   - **Local sanctioning authority:** `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema, which already allocates `wiki/standards/` with required `code_id`, `publisher`, `revision` frontmatter fields.
>   - **Frontmatter schema authority:** `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`, `publisher`, `revision` triple).
>   - **Organizational precedent:** W1-A plan [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (in progress) establishing the bounded-summary shape under the same target wiki.
>   - **Note on #2471:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) is **CSA-Z276-specific**; its path-routing decision does NOT generalize to arbitrary publishers. The rule's #2471 reference applies only to the frontmatter schema, not path-routing. See memory `project_wiki_standards_path_decision.md`.
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`)
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2591-claude-internal.md (r1 single-author Claude review; Codex + Gemini unavailable — see Adversarial Review Summary below)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError`; downstream resolver target for the ASME wiki pages this plan will create (same target shared with the API W1-A plan).
- Found (high-frequency callers, via `grep -rohE "ASME[ _-]?(B|BPV|PCC|VIII|IX|II|FFS)[A-Za-z0-9._-]*" /mnt/local-analysis/workspace-hub/digitalmodel/src/`):
  - `ASME VIII` — 33 occurrences (pressure-vessel calcs)
  - `ASME B31.4` / `ASMEB314*` — 17 + 15 occurrences (liquid-pipeline stress checks)
  - `ASME B31.8` / `ASMEB318*` — 16 + 15 occurrences (gas-transmission stress checks)
  - `ASME FFS-1` — 13 occurrences (fitness-for-service callers)
  - `ASME B31` (generic) — 11 occurrences
  - `ASME BPVC` — 4 occurrences
- Gap: the standards-transfer ledger has zero ASME rows (verified by grep: `grep -i ASME data/document-index/standards-transfer-ledger.yaml` returns empty); a single ASME journal/proceedings entry (`asme_jomae_omae`) exists in `online-resource-registry.yaml` (see line 58 below) — code-level catalog presence is zero. This plan does NOT modify either registry (out of scope; scoped to wiki promotion only — ledger registration is a follow-up).
- Gap: zero summary-promotion runner exists for the `/mnt/ace/O&G-Standards/ASME/` corpus; only `api-579-ffs.md` exists in the `engineering/` wiki (not the `engineering-standards/` wiki this plan targets), and that page covers the joint API 579-1 / ASME FFS-1 standard from the API-side framing, not the ASME-side framing.

### Standards

| Standard | Status | Source |
|---|---|---|
| ASME B31.3 (2012; Process Piping) | gap (raw present in /mnt/ace; no wiki page) | `/mnt/ace/O&G-Standards/ASME/ASME B31.3 - Process Piping/ASME B31.3 2012 - Processing Piping.pdf` |
| ASME B31.4 (2009; Pipeline Transportation Systems for Liquid Hydrocarbons) | gap | `/mnt/ace/O&G-Standards/ASME/ASME B31.4/ASME B31.4 (2009) Pipeline Transportation Systems for Liquid Hydrocarbons and Other Liquids.pdf` |
| ASME B31.8 (2007; Gas Transportation and Distribution Piping) | gap | `/mnt/ace/O&G-Standards/ASME/ASME B31.8/ASME B31.8 (2007) Gas Transportation and Distribution Piping Systems.pdf` |
| ASME B31.G (2012; Remaining Strength of Corroded Pipelines) | gap | `/mnt/ace/O&G-Standards/ASME/ASME B31.G/ASME B31.G (2012) Manual for Determining the Remaining Strength of Corroded Pipelines.pdf` |
| ASME BPVC Section VIII Div 1 (2010; Construction of Pressure Vessels) | gap | `/mnt/ace/O&G-Standards/ASME/ASME VIII/ASME VIII DIV 1 (2010) Rules for Construction of High Pressure Vessels.pdf` |
| ASME BPVC Section VIII Div 2 (2010; Alternative Construction Rules) | gap | `/mnt/ace/O&G-Standards/ASME/ASME VIII/ASME VIII DIV 2 with Addenda (2010) Rules for Construction of High Pressure Vessels.pdf` |
| ASME BPVC Section II Part D (2010; Material Properties — allowable stresses) | gap | `/mnt/ace/O&G-Standards/ASME/ASME II/ASME_II D (2010).pdf` |
| ASME BPVC Section IX (2010; Welding & Brazing Qualifications) | gap | `/mnt/ace/O&G-Standards/ASME/asme.bpvc.ix.2010.pdf` |
| ASME PCC-1 (2000; Guidelines for Bolted Flanges Assembly) | gap | `/mnt/ace/O&G-Standards/ASME/ASME PCC 1-2000/ASME PCC 1-2000 2D Guidelines for Bolted Flanges Assembly.pdf` |
| ASME B16.5 (2013; Pipe Flanges and Flanged Fittings) | gap | `/mnt/ace/O&G-Standards/ASME/BS/ASME B16.5-2013.pdf` |

### LLM Wiki pages consulted

- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing page in the target `engineering-standards` wiki (frontmatter pattern this plan replicates 10x).
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/index.md` — `page_count=5`, `source_count=5`; needs a "## Standards" section appended (will be appended jointly by W1-A + W2-B).
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply.
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` — existing joint API 579-1 / ASME FFS-1 page in the *other* wiki (`engineering/`, not `engineering-standards/`). This plan does NOT touch it; FFS-1 is intentionally **excluded** from the W2-B priority list to avoid double-coverage (see Open Questions).
- `/mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md` and siblings — existing engineering-wiki standards pages that follow a richer prose format than the new bounded-summary contract; W2-B intentionally inherits the **bounded** W1-A skeleton, not the engineering-wiki prose density.

### Documents consulted

- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — the W1-A precedent this plan mirrors (same target wiki, same frontmatter contract, same TDD test shape).
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — bounded preview pattern this plan ultimately inherits via W1-A.
- `/mnt/local-analysis/workspace-hub/data/document-index/standards-transfer-ledger.yaml` — confirmed empty for ASME (no rows).
- `/mnt/local-analysis/workspace-hub/data/document-index/online-resource-registry.yaml` — contains only `asme_jomae_omae` (journal/proceedings entry); no per-ASME-code entries; out of scope for W2-B.
- `.claude/rules/calc-citation-contract.md` — the citation contract this plan satisfies for the ten priority ASME codes.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — load-bearing constraint: workspace-hub #2471 is **scoped strictly to CSA Z276**; its path-routing decision does NOT generalize. The local sanctioning authority for `wiki/standards/<publisher>-<code-id>` under the engineering-standards wiki is that wiki's own `CLAUDE.md` directory schema (which already requires `code_id`/`publisher`/`revision` frontmatter); calc-citation-contract rule 2 sanctions only the frontmatter triple, not the path.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant: ASME-specific denylist phrases must be narrow (avoid matching legitimate wiki prose).
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex unavailable for r1 cross-review (stdin-hang regression; #2479 filed).
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review is the sanctioned fallback when cross-review.sh dispatch is unavailable.

### Gaps identified

- No wiki standards pages exist under `knowledge/wikis/engineering-standards/wiki/standards/` for: ASME B31.3, B31.4, B31.8, B31.G, BPVC VIII-1, BPVC VIII-2, BPVC II-D, BPVC IX, PCC-1, B16.5.
- No regression test exists asserting "wiki page does not contain raw ASME PDF text bleed-through" for any ASME page (the OCIMF Tandem test at `tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py` is the inheritable pattern; W1-A is creating its own API variant).
- The standards-transfer ledger has zero ASME rows; this plan flags the gap but does NOT resolve it (out-of-scope follow-up).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"
- `#2482` — CLOSED — "docs(knowledge): reconcile llm-wiki → GTM content boundary — resolve #2022 vs firm-copy-out-of-scope decision"

**File existence** (`ls`/`find` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/ASME/` — 984 MB; 88 PDFs at depth-4 (verified: `find /mnt/ace/O&G-Standards/ASME -maxdepth 4 -type f \( -name "*.pdf" -o -name "*.PDF" \) | wc -l` → `88`).
- EXISTS: top-level subdirs `ASME B31.3 - Process Piping/`, `ASME B31.4/`, `ASME B31.8/`, `ASME B31.G/`, `ASME B36.10M/`, `ASME II/`, `ASME PCC 1-2000/`, `ASME STP-PT-049/`, `ASME V/`, `ASME VIII/`, `ASME Y14.5/`, `BS/` (B16-series collection), `FFS-1/`, `The Stress Analysis of Cracks Handbook/`.
- EXISTS: each of the 10 priority PDFs (paths listed in the Standards table above).
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing page in target wiki).
- EXISTS: `knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` (joint API 579-1 / ASME FFS-1 page in the *other* wiki).
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-3.md`, `asme-b31-4.md`, `asme-b31-8.md`, `asme-b31-g.md`, `asme-bpvc-viii-1.md`, `asme-bpvc-viii-2.md`, `asme-bpvc-ii-d.md`, `asme-bpvc-ix.md`, `asme-pcc-1.md`, `asme-b16-5.md`.
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_asme.py`.

**Internal-reference frequency proof** (`grep -rohE "ASME[ _-]?(B|BPV|PCC|VIII|IX|II|FFS)[A-Za-z0-9._-]*" /mnt/local-analysis/workspace-hub/digitalmodel/src/ | sort | uniq -c | sort -rn | head -10`):
```
     33 ASME VIII
     17 ASME B31.4
     16 ASME B31.8
     13 ASME FFS-1
     11 ASME B31
     10 ASMEB31
      8 ASME B31.8-2016
      7 ASME B31.4-2016
      5 ASME_VIII_DIV1
      5 ASMEB318LogitudinalStress
```

**Standards ledger gap proof** (`grep -i ASME data/document-index/standards-transfer-ledger.yaml`):
```
(no output; exit code 1 — confirms zero ASME rows in ledger)
```

**Public-revision evidence (web — to be added per page; anchor citations below)**:
- ASME B31.3 — publisher catalog active edition cycle is **2024/2026** (per WebSearch evidence 2026-05-02; the 2024/2026 cycle moved Stress Intensification Factor calculation away from the simplified Appendix D charts to the now-mandatory ASME B31J method — a methodology rupture). Catalog: <https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping>
- ASME B31.4 currently active edition: 2022 (<https://www.asme.org/codes-standards/find-codes-standards/b31-4-pipeline-transportation-systems-liquids-slurries>)
- ASME B31.8 currently active edition: 2022 (<https://www.asme.org/codes-standards/find-codes-standards/b31-8-gas-transmission-distribution-piping-systems>)
- ASME BPVC revises every 2 years on ~July 1; 2023 edition is currently active; 2025 edition publishes July 2025 (<https://www.asme.org/codes-standards/bpvc-standards>)

> Note: the on-disk PDFs are older editions (e.g., B31.3 2012 vs current 2024/2026 cycle — a 14-year lag that crosses a methodology rupture). Each wiki page's `revision` frontmatter will pin to the **on-disk** edition (since that is the citable, locally-readable text), and the `publisher_current_edition` field will note the publisher's currently-active edition for reviewer awareness. **For B31.3 specifically**, the page body MUST include a one-sentence advisory that the SIF calculation method changed at the 2024/2026 cycle (no quoting), AND the page MUST carry a new `methodology_status: "stale-as-of-publisher-cycle"` frontmatter field (see Pseudocode skeleton below) so downstream calc callers cannot silently rely on a retired methodology. Pages whose on-disk revision cannot be authoritatively pinned to a verifiable publisher edition default to the api-17e stub pattern (`revision: "public-metadata-required-before-citation-use"`); the bounded-summary mode is opt-in for pages with a verifiable on-disk edition.

<!-- Distinct sources counted: existing repo code (1), standards ledger gap (2), wiki pages (3), prior plans (4), citation rule (5), project memory (6), web (7). 7 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-3.md` |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-4.md` |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-8.md` |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-g.md` |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-viii-1.md` |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-viii-2.md` |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-ii-d.md` |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-ix.md` |
| Wiki page (9) | `knowledge/wikis/engineering-standards/wiki/standards/asme-pcc-1.md` |
| Wiki page (10) | `knowledge/wikis/engineering-standards/wiki/standards/asme-b16-5.md` |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Test contract | `tests/knowledge/test_engineering_standards_asme.py` |
| Plan review — Claude (r1, internal single-author) | `scripts/review/results/2026-05-02-plan-2591-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang regression; #2479) |
| Plan review — Gemini | UNAVAILABLE (gemini sandbox path resolution failure) |

---

## Deliverable

Ten new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority ASME code), each carrying frontmatter that complies with the engineering-standards wiki `CLAUDE.md` directory schema and `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision` triple), and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/ASME/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream calc modules can resolve `Citation` instances for the ten most-referenced ASME codes (pressure piping, BPVC, bolted joints, flanges) without any verbatim source text entering git.

---

## Pseudocode

The work is a templated 10x repetition. Each new wiki page will follow the same skeleton:

```
---
title: "<Full standard name> — bounded summary"
tags: ["asme", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: <kebab-case id matching filename without extension>
publisher: ASME
revision: "<edition + year of the on-disk PDF, OR 'public-metadata-required-before-citation-use'>"
revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"
publisher_current_edition: "<currently-active edition per ASME catalog, for reviewer awareness>"
methodology_status: "<one of: 'current', 'stale-as-of-publisher-cycle', 'unknown'>"  # required for B31.3 (set to 'stale-as-of-publisher-cycle' due to 2024/2026 SIF change); other pages set to 'current' or 'unknown'
verified_on: 2026-05-02
public_url: <publisher catalog URL when known>
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
- [[asme-b31-3]] (when applicable — e.g. BPVC II-D ↔ B31.x for allowable stresses)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file will use a parametrized fixture iterating over the 10 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-3.md` | Bounded summary for ASME B31.3 (2012 on-disk; Process Piping) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-4.md` | Bounded summary for ASME B31.4 (2009 on-disk; Liquid Pipelines) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-8.md` | Bounded summary for ASME B31.8 (2007 on-disk; Gas Pipelines) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-b31-g.md` | Bounded summary for ASME B31.G (2012 on-disk; Corroded-Pipeline Remaining Strength) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-viii-1.md` | Bounded summary for BPVC Section VIII Division 1 (2010 on-disk) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-viii-2.md` | Bounded summary for BPVC Section VIII Division 2 (2010 on-disk; alternative rules) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-ii-d.md` | Bounded summary for BPVC Section II Part D (2010 on-disk; allowable stresses) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-bpvc-ix.md` | Bounded summary for BPVC Section IX (2010 on-disk; welding qualifications) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-pcc-1.md` | Bounded summary for ASME PCC-1 (2000 on-disk; bolted flange assembly) |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/asme-b16-5.md` | Bounded summary for ASME B16.5 (2013 on-disk; flanges + flanged fittings) |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append/extend "## Standards" section with 10 new rows; bump `page_count` (jointly with W1-A; final value depends on landing order). |
| Create | `tests/knowledge/test_engineering_standards_asme.py` | Test contract: frontmatter, no-raw-text, citation resolvability |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_asme.py`. Each test parametrized over the 10 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 10 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per engineering-standards `CLAUDE.md` schema + calc-citation-contract rule 2 | YAML frontmatter | `code_id` non-empty, kebab-case, matches filename stem |
| `test_frontmatter_has_publisher_asme` | publisher discipline | YAML frontmatter | `publisher == "ASME"` |
| `test_frontmatter_has_revision` | revision presence (per .claude rule 2) | YAML frontmatter | `revision` non-empty string |
| `test_frontmatter_has_methodology_status` | methodology-staleness disclosure (MAJOR-4) | YAML frontmatter | `methodology_status` is one of `{"current", "stale-as-of-publisher-cycle", "unknown"}`; for `asme-b31-3.md` MUST be `stale-as-of-publisher-cycle` |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (ASME-specific phrase set; see RAW_TELLTALE_PHRASES below — minimum 3 ASME-specific footer phrases required) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict ceiling tightened to ≤500 words (down from prior W1-A baseline) per MAJOR-3 ASME copyright posture | page body | `100 ≤ N ≤ 500` (inclusive ceiling; assertion fails the page if it exceeds 500) |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains ONLY the four allowed structural sections — explicitly rejects "Clauses" and "Formulas" sections (MAJOR-3) | page body | top-level `##` headings are an exact subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}`; presence of any heading containing the substrings "Clauses" or "Formulas" (case-insensitive) FAILS the test |
| `test_links_only_pointer_to_mnt_ace` | the page mentions the raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/ASME/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolution — both construction AND `validate_citation` (MINOR-2) | `Citation(code_id=<id>, publisher="ASME", revision=<rev>, section="placeholder", wiki_path=<path>)` followed by `validate_citation(c, repo_root=Path('.'))` | `CitationValidationError` not raised, `CitationResolutionError` not raised; `wiki_path` exists |
| `test_index_lists_all_ten` | wiki index updated | `index.md` contents | each of the 10 page links present in the "## Standards" section |
| `test_engineering_wiki_ffs1_remains_reachable` | positive discipline-boundary guard (replaces the prior hollow assert-no-link test per Adversarial pattern hunt) | for the existing `engineering/wiki/standards/api-579-ffs.md` page | the file still exists with its current frontmatter intact AND is reachable from at least one cross-reference within the engineering-wiki standards/ subtree (i.e. W2-B did not orphan or modify it) |

`RAW_TELLTALE_PHRASES` will be extracted by **sampling the cover/copyright pages of at least 3 of the 10 on-disk PDFs** (B31.3-2012, BPVC VIII-1-2010, B16.5-2013) and capturing the actual front-matter phrasing observed (per MINOR-4 — older PDFs may carry "Two Park Avenue" addresses while newer ones carry "150 W 47th St"). The list MUST include **at least 3 ASME-specific footer phrases** (e.g. "American Society of Mechanical Engineers", "Two Park Avenue", "New York, NY 10016", "150 W 47th St", "Reproduction or translation of any part of this work", "© 20XX by the American Society of Mechanical Engineers", "All rights reserved", "ASME is the registered trademark of"). The list will deliberately exclude the standard's title (which is allowed) and code identifier (which is required). Implementation-time check: the sampling step happens BEFORE the denylist is locked, and the per-PDF observed phrasing is recorded in a comment block above `RAW_TELLTALE_PHRASES` in the test file.

---

## Acceptance Criteria

- [ ] All ten new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_asme.py -v` passes (all parametrized cases green).
- [ ] No new test in `tests/knowledge/` regresses: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No raw-PDF clause text is committed: a `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/asme-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated, kebab-case `code_id` matches filename stem).
- [ ] Citation downstream-resolution check (per W1-A precedent — single canonical revision string per page; the page's frontmatter `revision` and the `Citation(...)` argument MUST match verbatim, since `validate_citation` does literal-equality on the revision string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - For each page where a real publisher revision is asserted in frontmatter, `python -c "from digitalmodel.citations.schema import Citation; Citation(code_id='<id>', publisher='ASME', revision='<frontmatter-revision-verbatim>', section='<placeholder>', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md')"` succeeds without error. Concrete example: `asme-b31-3.md` will use `revision: "2012"` in BOTH frontmatter AND the `Citation(...)` call.
  - **Per MINOR-2 — full resolution check, not just construction**: for the worked B31.3 example, also run `from digitalmodel.citations.schema import Citation, validate_citation; from pathlib import Path; validate_citation(Citation(code_id='asme-b31-3', publisher='ASME', revision='2012', section='placeholder', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/asme-b31-3.md'), repo_root=Path('.'))` and assert no `CitationResolutionError` (i.e. fail-closed at calc time per #2481 D2 actually fires green for this page).
  - Pages whose revision cannot be pinned to a verifiable publisher edition at write-time MUST set `revision: "public-metadata-required-before-citation-use"` in frontmatter AND be excluded from this resolution check.
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 10 new pages under a "## Standards" section (jointly populated with W1-A's 10 pages if W1-A lands first; this plan only commits to its 10 rows being present).
- [ ] **Per MINOR-3 — `page_count` merge-conflict mitigation**: implementation MUST follow one of: (a) serialize landing such that W1-A merges first and W2-B rebases on top (final state `page_count = 25` = 5 + 10 + 10), (b) treat the integer as a merge-conflict marker and document the resolution recipe in the PR description (whichever lands second resolves to the additive sum), or (c) replace the literal `page_count` integer with a sentinel (`page_count: auto`) in the same PR and let the wiki-ingest job recompute. The chosen approach MUST be stated in the implementation PR description.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan (the source-summary surface is reserved for raw-corpus pointers, not standards pages).
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified by this plan (the joint API 579-1 / ASME FFS-1 page stays untouched; FFS-1 is excluded from W2-B scope).
- [ ] **Per MINOR-5 — systemic canonicality follow-up**: a follow-up GitHub issue is filed (within the same PR or as a referenced issue in the PR description) titled approximately "decide canonical wiki for cross-publisher standards (engineering vs engineering-standards) — supersede or merge". Cite this issue in the FFS-1 Open Q below.
- [ ] **Per MINOR-1 — Div 2 frequency disaggregation**: before locking the 10-page list, run `grep -rohE "VIII[ _-]*DIV[ _-]*2|VIII[_]?2|Div\s*2" /mnt/local-analysis/workspace-hub/digitalmodel/src/ | wc -l`; if the disaggregated Div 2 count is <5, swap `asme-bpvc-viii-2` for `asme-b31-1` (power piping) or `asme-b16-20` (metallic gaskets) per the listed alternatives, and update the Open Q below accordingly.
- [ ] Plan review artifacts present at `scripts/review/results/2026-05-02-plan-2591-claude-internal.md` (r1 single-author Claude — Codex + Gemini unavailable; provenance recorded in Adversarial Review Summary).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 4 MAJOR (#2471 scope; ledger rhetoric; ASME copyright posture; M4) + 5 MINOR — all addressed inline |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (4 MAJOR + 5 MINOR applied 2026-05-02)

**Revisions made based on review:**
- MAJOR-1: re-anchored path-sanction citation away from #2471 (CSA-only) to engineering-standards `CLAUDE.md` directory schema + calc-citation-contract rule 2 + W1-A #2586 organizational precedent; explicitly noted #2471 is CSA-Z276-specific.
- MAJOR-2: rewrote ledger-empty claim to disclose `asme_jomae_omae` in `online-resource-registry.yaml` and connected line 27 to line 58 explicitly.
- MAJOR-3: tightened body word-count ceiling to ≤500, expanded ASME-specific denylist with ≥3 footer phrases (sampling step required), added positive-shape structural-section whitelist test that explicitly rejects "Clauses" and "Formulas" sections; replaced miscited Hydrolevel antitrust case with ASME's published copyright-policy URL; surfaced bounded-vs-stub trade-off explicitly.
- MAJOR-4: updated B31.3 publisher-current evidence to 2024/2026 cycle (14-year lag with SIF methodology rupture); added new `methodology_status` frontmatter field (required `stale-as-of-publisher-cycle` for B31.3); added a body-advisory requirement for B31.3.
- MINOR-1: added Div 2 frequency-disaggregation acceptance criterion with swap-decision rule (<5 hits → swap for B31.1 or B16.20).
- MINOR-2: added full `validate_citation(repo_root=Path('.'))` resolution check to acceptance criteria for the worked B31.3 example.
- MINOR-3: added explicit `page_count` merge-conflict mitigation acceptance criterion (3 options: serialize, document recipe, or sentinel).
- MINOR-4: required denylist phrases be extracted by sampling cover/copyright pages of ≥3 on-disk PDFs before locking; per-PDF observed phrasing recorded in test-file comment block.
- MINOR-5: added acceptance criterion to file follow-up issue on canonical wiki for cross-publisher standards (engineering vs engineering-standards).

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk:** Copyright leakage. ASME's published copyright policy explicitly prohibits reproduction without permission (per <https://www.asme.org/publications-submissions/publishing-information/legal-policies/copyright-terms-and-conditions> and <https://www.asme.org/codes-standards/find-codes-standards/use-of-asme-copyrighted-information>). This is treated as at least equal-tier to the W1-A API set; the bounded-summary mitigation is held to a tighter ceiling on first-principles grounds (no public DMCA-precedent miscitation — the prior draft cited *ASME v. Hydrolevel* incorrectly; that 1982 Supreme Court case is an antitrust matter about ASME interpretive-letter abuse, not a copyright-republishing precedent). **Mitigation (tightened per MAJOR-3):** word-count ceiling **≤500 words per page** (down from prior W1-A baseline; enforced by `test_body_word_count_bounded`) + positive-shape structural-section whitelist test that explicitly REJECTS any `## Clauses` or `## Formulas` section heading (`test_body_structure_is_whitelisted_only`) + denylist with ≥3 ASME-specific footer phrases sampled from on-disk PDF cover/copyright pages (per MINOR-4) + `extraction_policy: metadata-only` + `raw_copy_allowed: false` frontmatter + cross-review on every revision touching `wiki/standards/asme-*.md`. **Safe-by-default mode:** any page whose on-disk revision cannot be authoritatively pinned to a verifiable publisher edition MUST default to the api-17e stub pattern (`revision: "public-metadata-required-before-citation-use"`); the bounded-summary mode is opt-in for pages with a verifiable on-disk edition.
- **Risk:** BPVC cross-reference sprawl. BPVC sections II/V/VIII/IX cross-reference each other heavily (II-D supplies allowable stresses to VIII; VIII references V for NDE and IX for welding qualifications). The 10 priority pages WILL link to each other; care is needed not to import clause text along with the cross-link. **Mitigation:** the bounded skeleton ("Cross-references" section accepts only `[[wiki-id]]` link tokens, no quoted clause excerpts; this is enforced by the structural-section whitelist test).
- **Risk:** Revision lifecycle and methodology rupture. ASME BPVC revises **every 2 years** on ~July 1 (current active = 2023; 2025 publishes July 2025); B31-series codes revise every ~3 years; B16-series irregularly. The on-disk PDFs are older editions. **B31.3 specifically** has a 14-year on-disk-vs-publisher lag (2012 on-disk vs 2024/2026 cycle current) AND a methodology rupture across that lag (Stress Intensification Factor calculation moved from simplified Appendix D charts to mandatory ASME B31J method per the 2024/2026 cycle). **Mitigation (tightened per MAJOR-4):** wiki page `revision` field pins to the **on-disk** edition (the citable artifact); the `publisher_current_edition` frontmatter field surfaces the catalog-current edition for reviewer awareness; a new `methodology_status` frontmatter field (`current` / `stale-as-of-publisher-cycle` / `unknown`) discloses methodology staleness — `asme-b31-3.md` MUST set this to `stale-as-of-publisher-cycle` and the body MUST include a one-sentence advisory on the SIF method change (no quoting). Downstream calc callers can read this field and refuse to silently rely on a retired methodology. Stale-edition citation when methodology has not been retired is a known limitation, not a bug.
- **Risk:** Discipline-boundary collision with the existing `engineering/wiki/standards/api-579-ffs.md` joint API 579-1 / ASME FFS-1 page. **Mitigation:** FFS-1 is **excluded from the W2-B priority list** to avoid double-coverage. Per MINOR-5, this is a systemic issue (two wikis with overlapping `standards/` subtrees, no canonicality decision); a follow-up GitHub issue MUST be filed in the implementation PR titled approximately "decide canonical wiki for cross-publisher standards (engineering vs engineering-standards) — supersede or merge", and that issue's number cited in the FFS-1 Open Q below. The current PR landing 10 ASME pages in engineering-standards does not resolve the canonicality question — it just defers it explicitly with a tracking issue.
- **Risk:** ID-naming consistency. The W1-A plan uses `api-rp-2a-wsd`, `api-spec-17j` (publisher-prefix-included). This plan uses `asme-b31-3`, `asme-bpvc-viii-1`, `asme-pcc-1` — keeping `asme-` as the publisher prefix and the section/division as a kebab-case path component. **Mitigation:** the naming follows the `wiki/standards/<publisher>-<code-id>` shape sanctioned by the engineering-standards wiki's `CLAUDE.md` directory schema and the W1-A plan #2586 organizational precedent. Note: #2471's CSA-Z276 path-routing decision does NOT generalize to ASME (it is CSA-specific per memory `project_wiki_standards_path_decision.md`); the path sanction here rests on the local wiki schema, not #2471.
- **Open:** **Which 10?** This plan proposes the following ten priority codes, biased by (a) digitalmodel internal-reference frequency, (b) verifiable raw source under `/mnt/ace`, (c) E&P upstream/offshore relevance:
  1. ASME B31.3 (2012) — Process piping
  2. ASME B31.4 (2009) — Liquid hydrocarbon pipelines (17 internal hits)
  3. ASME B31.8 (2007) — Gas transmission piping (16 internal hits)
  4. ASME B31.G (2012) — Corroded-pipeline remaining strength
  5. ASME BPVC Section VIII Div 1 (2010) — Pressure-vessel construction (33 `ASME VIII` internal hits, shared with Div 2)
  6. ASME BPVC Section VIII Div 2 (2010) — Alternative-rules pressure vessels
  7. ASME BPVC Section II Part D (2010) — Allowable stresses (referenced by every B31.x and VIII calc)
  8. ASME BPVC Section IX (2010) — Welding/brazing qualifications
  9. ASME PCC-1 (2000) — Bolted flange-joint assembly guidelines
  10. ASME B16.5 (2013) — Pipe flanges and flanged fittings

  **User confirmation required during plan-review.** If different priorities are preferred (e.g. include B16.20 metallic gaskets, B16.34 valves, B16.47 large-diameter flanges, BPVC Section V NDE, B31.1 power piping, B36.10M wrought-steel pipe schedules), they can be substituted before approval.
- **Open:** **Granularity of BPVC Section VIII** — propose `asme-bpvc-viii-1` and `asme-bpvc-viii-2` as separate pages (consumes 2 of the 10 slots). Alternative: a single `asme-bpvc-viii` parent page with subsections, freeing one slot for (e.g.) ASME B16.20 or ASME B31.1. Flag for reviewer.
- **Open:** **FFS-1 unification** — the existing joint API 579-1 / ASME FFS-1 page lives in `engineering/wiki/standards/`, not the target `engineering-standards/wiki/standards/`. Should W2-B (a) leave it alone (current proposal), (b) retro-move it, or (c) create a thin pointer page in the target wiki linking to the existing one? Flag for reviewer; the current proposal is (a). **Per MINOR-5**: regardless of which option lands, the implementation PR MUST file a follow-up issue titled approximately "decide canonical wiki for cross-publisher standards (engineering vs engineering-standards) — supersede or merge" so the systemic split does not silently harden.
- **Open:** **Edition pinning** — every on-disk ASME PDF is an older edition than the publisher's currently-active edition. Should the W2-B pages additionally include a "currently-active edition" advisory line in the body (in addition to the `publisher_current_edition` frontmatter field), to discourage downstream calc callers from quoting an old revision as authoritative? Flag for reviewer. **Per MAJOR-4**: this is mandatory (not optional) for any page where `methodology_status == "stale-as-of-publisher-cycle"` (currently B31.3).
- **Open:** **W1-A pattern lock** — this plan inherits the W1-A skeleton heavily, but W1-A (#2586) is itself OPEN and not yet implemented. Inheritance from an unlanded sibling means W2-B may need to track W1-A's review revisions in lockstep. **Resolution rule**: W2-B implementation does NOT begin until W1-A is plan-approved OR explicit user approval is given to fork the patterns. Flag for reviewer.
- **Open:** **Cross-repo grep coverage** — the digitalmodel-only frequency analysis in Resource Intel does not cover assethold or dgs-engineering callers. If those repos cite ASME B16.20 / B16.34 / B16.47 / BPVC V (NDE), the top-10 picked here is locally optimal but may be globally short-sighted. **Resolution rule**: either run cross-repo grep before locking the 10-page list, OR explicitly state in the PR description that W2-B is digitalmodel-only and other-repo coverage is a separate follow-up. Flag for reviewer.

---

## Complexity: T2

**T2** — multi-file documentation work (10 new wiki pages + 1 test file + 1 index update + 1 docs/plans/README.md update = 13 files), no new code modules, but a real test contract (≥12 parametrized assertions × 10 pages ≈ 120 effective test cases). Implementation is templated repetition matching the W1-A shape; the design risk is concentrated in (a) the ASME-specific denylist phrasing, (b) the BPVC cross-reference handling, and (c) the FFS-1 boundary decision — not in algorithm correctness.
