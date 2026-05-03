# Plan for LLM-Wiki Completeness W4-A: Bounded NACE/AMPP Standards Summary Promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** _not yet filed — issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md`. Proposed title: `feat(llm-wiki): bounded NACE/AMPP standards summary promotion to engineering-standards wiki (W4-A)`._
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) (CLOSED) — overnight Elements corpus planning wave; this W4 packet is a continuation under the same bounded-summary contract.
> **Sibling precedent (W1-A, API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN) — original bounded-promotion pattern. NOTE: W1-A header still over-cites `#2471` as path-sanction at lines 9 and 225; the W3-C erratum [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN) tracks the forward-amendment. W4-A does NOT inherit that over-cite.
> **Sibling precedent (W2-A, DNV) and (W3-A, ABS):** [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (OPEN) and [#2594](https://github.com/vamseeachanta/workspace-hub/issues/2594) (OPEN) — adopt the corrected #2471 framing (local sanction = `engineering-standards/CLAUDE.md` directory schema; #2471 cited only as historical origin of the frontmatter triple). W4-A inherits this corrected framing verbatim.
> **Sibling precedent (W3-C erratum):** [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN) — retro-fixed the #2471 sanction-scope defect across W1-A/W1-B/W2-C/W3-D and added the allowlist-polarity guardrail at `tests/governance/test_2471_citation_scope.py`. W4-A is written so that guardrail passes against this plan.
> **Path sanction (NACE/AMPP):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for the engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). In-progress organizational precedent: W2-A plan [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (DNV, revised) and W3-A [#2594](https://github.com/vamseeachanta/workspace-hub/issues/2594) (ABS, revised). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision for CSA-Z276 specifically (verified per memory `project_wiki_standards_path_decision.md`); it is NOT a general-standards path sanction and is referenced here only as the historical origin of the frontmatter triple, not as NACE/AMPP path authority.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter.
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`).
> **Calc-citation pilot (epic-level):** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors pilot. W4-A does NOT extend the pilot to NACE/AMPP code; that is a downstream consumer concern.
> **Review artifact:** `scripts/review/results/2026-05-03-plan-W4A-claude-internal.md` (single-author Claude r1, to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini UNAVAILABLE per memory (codex-cli 0.124.0 stdin-hang #2479; Gemini sandbox cwd=/tmp blocks workspace-hub overlay reads).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). Downstream consumer that will resolve the wiki pages this plan creates. Schema fields: `code_id`/`publisher`/`revision`/`section`/`wiki_path` (verified at lines 42-50, 118).
- Found: NACE references in `digitalmodel/src/` are real and structured — `digitalmodel/src/digitalmodel/cathodic_protection/` carries six modules referencing NACE practice (`anode_depletion.py`, `cp_survey.py`, `corrosion_rate.py`, `iccp_design.py`, `cp_monitoring.py`, `coating.py`). NACE is the **primary cathodic-protection citation source** in the codebase — higher relative density than ABS's offshore-rule-book references.
- Internal-reference frequency: NACE appears in `digitalmodel/src/` as 26 structured short-string citations across **7 distinct codes** — `NACE SP0169` (14 hits, pipeline external corrosion control), `NACE SP0176` (3, offshore CP), `NACE SP0207` (1, in-line inspection), `NACE SP0490` (1), `NACE SP0502` (3, direct assessment), `NACE TM0497` (3, soil resistivity), `NACE MR0175` (1). **Critical mismatch:** the most-cited internal codes (`SP0169`, `SP0176`, `TM0497`) are **NOT** in the `/mnt/ace/O&G-Standards/NACE/` corpus on disk. The on-disk corpus has only `MR 0175` (4 PDFs across 1995 + 2009 Pt 1/2/3) and `TM 0177-96` plus 3 conference papers. See Risks for the corpus-vs-citation-frequency mismatch and the forward path.
- Gap: zero NACE/AMPP wiki pages exist anywhere — `ls knowledge/wikis/*/wiki/standards/` returns no `nace-*.md` or `ampp-*.md` file. The `engineering-standards/wiki/standards/` directory holds only `api-17e.md` today (1 file).

### Standards

The on-disk NACE corpus is small (8 documents, 5 of them standards). Conference papers are vendor-derivative per #2482 and EXCLUDED. The remaining 5 standards documents collapse to 4-5 priority wiki pages:

| Standard | Status | Source |
|---|---|---|
| NACE MR 0175 / ISO 15156 (2009 — current; multi-part: Pt 1, 2, 3) — Sour-service materials selection | gap (3 PDFs of the 2009 2nd Ed on disk; ledger has no row yet) | `/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 1 2nd Ed (2009) ...pdf` (+ Pt 2, Pt 3) |
| NACE MR 0175 (1995) — superseded historical edition retained for legacy traceability | gap | `/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 (1995) Sulfide Stress Cracking Resistant Metallic Materials for Oilfield Equipment.pdf` |
| NACE TM 0177-96 — Sulfide stress cracking laboratory test method | gap | `/mnt/ace/O&G-Standards/NACE/NACE TM0177-96/TM0177-96 (H2S Cracking Test Procedures).PDF` |
| NACE Paper 01469 (Splash Zone Protection) | EXCLUDED — conference paper, vendor-derivative per #2482 | n/a |
| NACE Paper 04022 (TSA Coating) | EXCLUDED — conference paper | n/a |
| NACE Paper 05153 (Riser Inspection West Africa) | EXCLUDED — conference paper | n/a |

This plan therefore proposes **4 priority wiki pages** (not 4-6 — the small on-disk corpus does not support more without inventing pointer-only stubs):

1. `nace-mr-0175.md` — multi-part umbrella page covering MR 0175 / ISO 15156 (current 2009 2nd Ed). Single page, multi-part document — `nace_part_section` frontmatter expresses the Pt 1 / Pt 2 / Pt 3 distinction within the umbrella, mirroring the W3-A `abs_part_section` pattern.
2. `nace-mr-0175-1995.md` — separate page for the superseded 1995 edition (historical traceability; `supersedes` lineage to MR 0175 (2009) 2nd Ed).
3. `nace-tm-0177.md` — sulfide stress cracking test method (1996 edition on disk; the test method has been revised multiple times since — frontmatter pins to the on-disk `1996` edition with a note that the calc-caller MUST verify against the publisher's current edition before use).
4. **OPTIONAL** `ampp-knowledge-hub.md` — pointer-only stub referencing the AMPP / NACE Knowledge Hub URL already in `online-resource-registry.yaml` (id: `ampp_knowledge_hub`). This is a publisher-level pointer, NOT a standard. Flagged in Open Questions; if rejected, scope drops to **3 pages**.

The most-internally-cited NACE codes (`SP0169`, `SP0176`, `TM0497`) are NOT promoted by W4-A — no raw on disk. They are deferred to a W4-B follow-up using publisher-portal pointers (mirrors the W3-A "MODU/FPI/Subsea/MOU" deferral pattern).

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards code page; metadata-stub frontmatter pattern this plan replicates. Confirms lowercase-kebab `code_id` convention (`code_id: api-17e`) and the `revision: public-metadata-required-before-citation-use` placeholder convention when the on-disk edition cannot be pinned to a publisher-verifiable revision.
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`. **Arithmetic AC** (per W2-A and W3-A pattern): `page_count` after this plan = (current `page_count` at implementation time) + 4 (or +3 if AMPP Knowledge Hub stub rejected). The plan does NOT pin a fixed final number, since W1-A/W2-A/W3-A may have landed by W4-A implementation time.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision`); the new pages will all comply. Schema example values use lowercase-kebab. **This is the path-sanction authority** for engineering-standards domain (NOT #2471).
- `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — Elements ingest catalog already references the broader DORIS standards corpus. The NACE subset of `/mnt/ace/O&G-Standards/NACE/` is a complementary path through that corpus.
- No pre-existing NACE or AMPP pages exist in any wiki (verified by `ls knowledge/wikis/*/wiki/standards/ | grep -iE "nace|ampp"` returning no matches).

### Documents consulted

- `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md` — direct shape precedent. **Inherited contracts:** bounded-preview frontmatter, no-raw-text test, citation-resolvability test, lowercase-kebab `code_id`, `<part>_part_section` frontmatter for multi-part rule books, ledger-form/wiki-form ID divergence pattern (`ledger_id` frontmatter key bridges the two).
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — revised W2-A. Adopts corrected #2471 framing.
- `docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md` — W3-C erratum. Defines the allowlist-polarity guardrail (`tests/governance/test_2471_citation_scope.py`) that W4-A must pass.
- `data/document-index/standards-transfer-ledger.yaml` — searched for `NACE` / `AMPP`: **zero rows**. All 4 priority NACE pages introduced by this plan require new ledger rows.
- `data/document-index/online-resource-registry.yaml` — entry `ampp_knowledge_hub` exists (URL `https://www.ampp.org/technical-research/impact/corrosion-basics`) with the note: "AMPP Knowledge Hub (2025) unifies NACE and AMPP content. Non-members access Corrosion Basics and some open articles. CORROSION journal has selective OA. Standards (SP0169 pipeline CP, SP0176 offshore CP) require purchase. Relevant to cathodic protection and corrosion modules." This is the load-bearing entry for both the NACE → AMPP rebrand evidence AND the Open-Question stub.
- `.claude/rules/calc-citation-contract.md` — citation contract this plan exists to satisfy.
- `.claude/rules/coding-style.md` and `.claude/rules/patterns.md` — universal rules.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in **future tense**; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). The path-routing principle generalizes only to {marine-engineering, engineering, naval-architecture}; for engineering-standards wiki, cite the LOCAL `engineering-standards/CLAUDE.md` directory schema. Load-bearing.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; this plan keeps phrase lists narrowly scoped to NACE/AMPP-specific copyright/cover-page strings (Houston TX HQ, "© NACE International", "All rights reserved").
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review acceptable when Codex/Gemini unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex CLI 0.124.0 stdin-hang regression #2479; Codex review unavailable.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini cwd=/tmp blocks workspace-hub overlay reads; Gemini review unavailable.
- `feedback_never_offer_to_self_label_plan_approved.md` — issue filing is downstream of plan-review approval; this plan is `status: draft` and does NOT pre-authorize a downstream issue.

### Gaps identified

- No engineering-standards wiki pages exist for any NACE or AMPP code (zero — `ls knowledge/wikis/*/wiki/standards/ | grep -iE "nace|ampp"` returns empty).
- The standards-transfer-ledger contains zero NACE/AMPP rows. 4 (or 3 if AMPP stub rejected) new ledger rows required.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any NACE page.
- The 7 most-internally-cited NACE codes (`SP0169`, `SP0176`, `SP0207`, `SP0490`, `SP0502`, `TM0497`, `MR0175`) appear in 26 source-file references but only ONE (`MR0175`) has a raw on-disk PDF. The 6 cathodic-protection-domain codes are cited but not promotable from `/mnt/ace` corpus alone — deferred to W4-B publisher-portal pointer follow-up.
- NACE → AMPP rebrand (2021): NACE merged with SSPC to form AMPP. The rebrand decision affects `publisher` frontmatter — pages MUST declare both `publisher: AMPP` (current) and `legacy_publisher: NACE International` (historical) to satisfy both old-citation backward-compat and new-citation forward-compat. The `code_id` convention chosen (see Open Questions) MUST also reflect this.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — body explicitly scopes to CSA-Z276 (CSA-only, per memory)
- `#2540` — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — W1-A engineering-standards API
- `#2594` — OPEN — W3-A engineering-standards ABS
- `#2596` — OPEN — W3-C #2471 sanction-scope erratum
- `#2482` — CLOSED — vendor-derivative deny-list governance
- `#2481` — CLOSED — calc-citation contract pilot

**File existence** (`ls -la /mnt/ace/O&G-Standards/NACE/` 2026-05-03):
```
drwxr-xr-x  NACE MR 0175           (4 PDFs: 1995, 2009 Pt 1, Pt 2, Pt 3)
drwxr-xr-x  NACE Paper No 01469    (1 PDF — EXCLUDED, conference paper)
drwxr-xr-x  NACE Paper No 04022    (1 PDF — EXCLUDED, conference paper)
drwxr-xr-x  NACE Paper No 05153    (1 PDF — EXCLUDED, conference paper)
drwxr-xr-x  NACE TM0177-96         (1 PDF — H2S Cracking Test Procedures)
```
Total: 8 documents, 5 standards (4 MR 0175 editions + 1 TM 0177-96), 3 papers (excluded).

- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (template exemplar)
- EXISTS: `knowledge/wikis/engineering-standards/CLAUDE.md` (path-sanction authority)
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (resolver target)
- EXISTS: `tests/governance/test_2471_citation_scope.py` (allowlist-polarity guardrail; this plan must pass it)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/nace-mr-0175.md`, `nace-mr-0175-1995.md`, `nace-tm-0177.md`, and OPTIONAL `ampp-knowledge-hub.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_nace.py`

**Internal-reference proof — NACE in digitalmodel** (`grep -rohE "NACE[ _-]?(MR|TM|RP|SP)[ _-]?[0-9]+" digitalmodel/src/ | sort | uniq -c`):
```
      1 NACE MR0175
     14 NACE SP0169
      3 NACE SP0176
      1 NACE SP0207
      1 NACE SP0490
      3 NACE SP0502
      3 NACE TM0497
```
Total: 26 hits across 7 codes. **Of these, only `MR0175` has raw on disk** — the SP-series and TM 0497 are deferred to W4-B.

**NACE source files in digitalmodel** (`grep -rli "NACE" digitalmodel/src/`):
```
digitalmodel/src/digitalmodel/cathodic_protection/anode_depletion.py
digitalmodel/src/digitalmodel/cathodic_protection/cp_survey.py
digitalmodel/src/digitalmodel/cathodic_protection/corrosion_rate.py
digitalmodel/src/digitalmodel/cathodic_protection/iccp_design.py
digitalmodel/src/digitalmodel/cathodic_protection/cp_monitoring.py
digitalmodel/src/digitalmodel/cathodic_protection/coating.py
digitalmodel/src/digitalmodel/marine_ops/installation/jumper_lift.py
digitalmodel/src/digitalmodel/structural/offshore_resilience/structural_health.py
```
Confirms NACE is THE primary citation source for `digitalmodel/cathodic_protection/`. The grep-frequency and the on-disk-corpus do NOT match — corpus priority is `MR0175` (the one on-disk + cited code) plus its test method `TM 0177`.

**NACE / AMPP ledger rows present** (`grep -i "NACE\|AMPP" data/document-index/standards-transfer-ledger.yaml`):
```
(empty)
```
Zero existing ledger rows. Plan adds 3 (or 4 with AMPP stub).

**Online-resource-registry AMPP entry** (`grep -A8 "ampp_knowledge_hub" data/document-index/online-resource-registry.yaml`):
```
- id: ampp_knowledge_hub
  url: https://www.ampp.org/technical-research/impact/corrosion-basics
  name: AMPP / NACE Knowledge Hub
  type: tool
  domain: materials
  notes: 'AMPP Knowledge Hub (2025) unifies NACE and AMPP content. Non-members access Corrosion Basics and some open articles.
    CORROSION journal has selective OA. Standards (SP0169 pipeline CP, SP0176 offshore CP) require purchase. Relevant to cathodic
    protection and corrosion modules.'
```
This is the documented evidence of the NACE → AMPP rebrand inside this repo. Plan's `legacy_publisher` frontmatter convention is grounded here.

**Engineering-standards CLAUDE.md path-sanction excerpt** (the load-bearing line that replaces any "#2471 path sanction" claim):
```
wiki/
  standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)
```
Plus the Standards page extra-fields table (`code_id`, `publisher`, `revision` all required at L0 prose; example values lowercase-kebab `csa-z276`, `api-17j`, `ocimf-meg4`).

**Issue #2471 body excerpt** (verifies CSA-Z276-only scope):
```
Decide and codify the sanctioned durable-wiki routing/schema for CSA Z276 pages
before CSA coverage is promoted from ACMA/standards metadata into LLM-wiki content.
```

**Public-revision evidence (web)**:
- AMPP standards portal: <https://store.ampp.org/> — current MR 0175 / ISO 15156 is jointly published with ISO; the joint document is currently at the **2020** edition (Parts 1, 2, 3), superseding the 2009 edition on disk. The `revision` frontmatter for `nace-mr-0175.md` will pin to the on-disk edition (`2009-2nd-Ed`) with explicit prose noting that calc-callers MUST verify against the publisher's current 2020 edition before use; downstream calc-callers SHOULD prefer citing the 2020 edition once the wiki page is updated against a verified source.
- NACE → AMPP rebrand: NACE International merged with SSPC (Society for Protective Coatings) on 2021-01-01 to form the **Association for Materials Protection and Performance (AMPP)**. The rebrand is documented in the AMPP knowledge-hub registry entry above (`AMPP Knowledge Hub (2025) unifies NACE and AMPP content`). This is well-established public information.
- TM 0177 current edition: per AMPP standards catalog, current TM 0177 is at the **2016** edition (with multiple solution-method revisions since 1996). On-disk is **1996** — `revision: "1996"` pinned with prose note that calc-callers MUST verify against current edition.

<!-- Distinct sources counted: existing repo code (1), standards ledger / online registry (2), engineering-standards CLAUDE.md schema (3), W3-A precedent plan (4), W2-A revised precedent plan (5), W3-C erratum + guardrail test (6), `/mnt/ace/.../NACE/` corpus contents (7), citation rule (8), project memory (9), web public catalogs (10). 10 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2599-llm-wiki-W4A-engineering-standards-nace.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/nace-mr-0175.md` (current, 2009 2nd Ed; multi-part umbrella for Pt 1 / Pt 2 / Pt 3) |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/nace-mr-0175-1995.md` (superseded historical edition) |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/nace-tm-0177.md` (sulfide stress cracking lab test method, 1996 edition on disk) |
| Wiki page (4 — OPTIONAL) | `knowledge/wikis/engineering-standards/wiki/standards/ampp-knowledge-hub.md` (publisher-level pointer; flagged as Open Question — see Risks/Open Questions) |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 3 or 4 new rows) |
| Test contract | `tests/knowledge/test_engineering_standards_nace.py` |
| Plans-index update | `docs/plans/README.md` |
| Plan review — Claude (r1, single-author) | `scripts/review/results/2026-05-03-plan-W4A-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |

---

## Deliverable

Three (or four if the AMPP Knowledge Hub stub is approved) new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/`, one per priority NACE code (or AMPP-publisher pointer), each carrying calc-citation-contract-compliant frontmatter (`code_id`, `publisher`, `revision`, plus `extraction_policy: metadata-only`, `raw_copy_allowed: false`, plus NACE/AMPP-specific `legacy_publisher: "NACE International"` to track the 2021 rebrand) and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/NACE/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream `digitalmodel/cathodic_protection/` calc modules CAN resolve a `Citation` instance for NACE MR 0175 (and the future NACE SP-series / TM-series codes once W4-B promotes them) without any verbatim source text entering git.

---

## Pseudocode

The work is templated 3-4x repetition. Each new wiki page follows this skeleton (identical to W3-A modulo `publisher: AMPP`/`legacy_publisher: NACE International` and NACE-specific fields):

```
---
title: "<Full NACE/AMPP document name> — bounded summary"
tags: ["nace", "ampp", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: nace-mr-0175                    # lowercase-kebab; matches engineering-standards CLAUDE.md, api-17e
                                         # Open Question: nace-* vs. ampp-* prefix — see Open Questions
publisher: AMPP                          # current publisher per 2021 rebrand
publisher_full: "Association for Materials Protection and Performance"
legacy_publisher: "NACE International"   # historical name; preserved for backward-compat citations
publisher_history:                       # optional; mirrors W2-A "DNV vs DNV GL" pattern
  - { name: "NACE International", from: "1943", to: "2020-12-31" }
  - { name: "AMPP", from: "2021-01-01", to: "present" }
revision: "2009-2nd-Ed"                  # on-disk edition; ISO 15156 jointly-published current is "2020"
revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"  # OPTIONAL — may be omitted
verified_on: 2026-05-03                  # OPTIONAL — may be omitted; if present use this exact key (not `verified_date`)
public_url: https://store.ampp.org/      # OPTIONAL — may be omitted when no canonical public URL
sources:
  - <one or more /mnt/ace/... paths — pointer only, never quoted>
extraction_policy: metadata-only
raw_copy_allowed: false
nace_doc_number: "MR 0175"               # NACE document-number convention
nace_part_section: "Pt.1 / Pt.2 / Pt.3"  # ONLY on the umbrella nace-mr-0175.md page; OMIT entirely on
                                         # nace-tm-0177.md and nace-mr-0175-1995.md (do NOT set to YAML null)
ledger_id: NACE-MR-0175-2009             # bridge to standards-transfer-ledger uppercase form
supersedes: ["nace-mr-0175-1995"]        # OPTIONAL on current page; required on the 1995 page IF current page exists
iso_equivalent: "ISO 15156"              # OPTIONAL; only on MR 0175 (jointly published with ISO since 2003)
cross_links:                             # cross-wiki references, currently empty for NACE
  - []
---

# <Full NACE/AMPP document name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.

## Where to find the full text
- Raw PDF: <absolute /mnt/ace/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://store.ampp.org/ (registration required for purchase/download)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code, or "no live caller; future-needed">

## Cross-references
- [[nace-tm-0177]] (test method companion to MR 0175 sulfide stress cracking acceptance)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file uses a parametrized fixture iterating over the 3-4 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/nace-mr-0175.md` | Bounded summary umbrella for NACE MR 0175 / ISO 15156 (2009 2nd Ed; multi-part Pt 1/2/3). Highest-relevance NACE code for sour-service materials selection across `digitalmodel/`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/nace-mr-0175-1995.md` | Bounded summary for the superseded 1995 edition. Required for legacy-citation backward-compat (one `digitalmodel/` source-file already cites `MR0175` without an edition tag — until that caller is migrated, both editions need resolver targets). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/nace-tm-0177.md` | Bounded summary for NACE TM 0177-96 — Sulfide Stress Cracking Laboratory Test Procedures. Companion test method for MR 0175 acceptance criteria. |
| Create (OPTIONAL) | `knowledge/wikis/engineering-standards/wiki/standards/ampp-knowledge-hub.md` | Publisher-level pointer (NOT a standard) summarizing the AMPP / NACE Knowledge Hub URL already in `online-resource-registry.yaml`. **Flagged in Open Questions** — drop if not approved. |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 3-4 new rows; bump `page_count` per the **arithmetic AC** (current count + 3 or +4), not a fixed value. |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 3 (or 4 with AMPP stub) new rows. New IDs: `NACE-MR-0175-2009`, `NACE-MR-0175-1995`, `NACE-TM-0177-1996`, optionally `AMPP-KH-POINTER`. |
| Create | `tests/knowledge/test_engineering_standards_nace.py` | Test contract: frontmatter, no-raw-text, citation resolvability, ledger alignment, code_id uniqueness across wikis, `nace_part_section`-only-on-umbrella discipline, `legacy_publisher` discipline. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_nace.py`. Each test parametrized over the 3 or 4 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 3-4 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, lowercase-kebab; filename stem equals `code_id` verbatim (e.g., `nace-mr-0175.md` ↔ `nace-mr-0175`) |
| `test_frontmatter_has_publisher_ampp` | publisher discipline (current rebrand) | YAML frontmatter | `publisher == "AMPP"`; if present, `publisher_full == "Association for Materials Protection and Performance"` |
| `test_frontmatter_has_legacy_publisher_nace` | rebrand backward-compat discipline | YAML frontmatter | `legacy_publisher == "NACE International"` on every NACE-prefixed page; OMITTED on the OPTIONAL `ampp-knowledge-hub.md` (which has no NACE legacy form) |
| `test_frontmatter_has_revision` | revision presence per calc-citation-contract rule 2 | YAML frontmatter | `revision` non-empty string; matches NACE/AMPP regex `^(\d{4}(-\d+(st\|nd\|rd\|th)?-Ed)?\|public-metadata-required-before-citation-use)$` |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_has_nace_doc_number` | NACE-specific traceability | YAML frontmatter | `nace_doc_number` non-empty (e.g. `"MR 0175"`, `"TM 0177"`) on the 3 NACE pages; OMITTED on the OPTIONAL `ampp-knowledge-hub.md` |
| `test_part_section_only_on_umbrella` | multi-part-document discipline | YAML frontmatter | only `nace-mr-0175.md` carries `nace_part_section`; the other pages do NOT (key omitted entirely; do NOT set to YAML `null`) |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow NACE/AMPP-specific phrase set) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict `<500` word ceiling matching W1-A/W2-A/W3-A | page body | `0 < word_count < 500` strict on both bounds; constant imported from W1-A's test file when present, else local `MAX_BODY_WORDS = 500` with `# TODO: migrate to shared constant` comment |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only allowed sections | page body | top-level `##` headings exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` |
| `test_links_only_pointer_to_mnt_ace` | mentions raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/NACE/` present in a "Where to find" section (NACE pages); the OPTIONAL `ampp-knowledge-hub.md` is exempt — it points to AMPP URL, no `/mnt/ace` source |
| `test_citation_schema_resolvable` | downstream resolver actually reads the wiki page | invoke resolver function from `digitalmodel/src/digitalmodel/citations/schema.py` for each NACE page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised |
| `test_ledger_alignment` | every page's `ledger_id` resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `ledger_id` | matching `id:` row found in ledger YAML |
| `test_code_id_unique_across_wiki_domains` | inherited from W2-A/W3-A AC | every `code_id` in `knowledge/wikis/*/wiki/standards/*.md` | no duplicates |
| `test_index_lists_all_pages` | wiki index updated | `index.md` contents | each new page link present in the "## Standards" section |
| `test_iso_equivalent_only_on_mr_0175` | ISO co-publication discipline | YAML frontmatter | only `nace-mr-0175.md` carries `iso_equivalent: "ISO 15156"`; the 1995 page may or may not (1995 pre-dates ISO joint publication; this assertion permits both) |

`RAW_TELLTALE_PHRASES` is a narrowly-scoped list (≤15 entries) drawn from NACE/AMPP publication front-matter conventions:
- "NACE International" (cover-page; legitimate as `legacy_publisher` value but FORBIDDEN in body prose)
- "Association for Materials Protection and Performance"
- "© NACE International"
- "© AMPP"
- "Houston, Texas"  (NACE/AMPP HQ city)
- "All rights reserved"
- "Reproduction, copy or transmission of this publication"
- "ISBN" + "1-57590"  (NACE ISBN prefix)
- "Catalog Number"
- "ANSI/NACE"  (American National Standard designator)
- "ISO 15156"  (cover-page joint-publication string — body text may legitimately mention ISO 15156, so this entry is contextual; mitigation: allow ISO 15156 in body but flag if it appears with > 3 surrounding words from a known cover-page template)
- "AMPP, Houston, TX"
- "First published"
- "Reaffirmed"

**Deliberately excluded from denylist (allowed in body):** `MR 0175`, `TM 0177` (document numbers), `sulfide stress cracking` / `SSC` (technical concept paraphrase), `sour service` (technical concept), `cathodic protection` (technical concept), `H2S` (chemical formula).

The denylist will NOT overlap with OCIMF, API, DNV, or ABS denylists. **Honesty caveat (inherited from W2-A P2-3 / W3-A risk):** denylist alone will NOT catch a 100-200-word verbatim clause copy; reviewers MUST manually inspect every revision. Shingle-match / cosine-similarity follow-up deferred to W4-B.

---

## Acceptance Criteria

- [ ] All 3 (or 4 if AMPP stub approved) new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_nace.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No regression: `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes (THIS plan is in scope of the allowlist-polarity guardrail; the W3-C erratum's guardrail must remain green).
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/nace-*.md knowledge/wikis/engineering-standards/wiki/standards/ampp-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated; `code_id` lowercase-kebab; filename stem equals `code_id` verbatim).
- [ ] **Rebrand discipline:** every NACE-prefixed page carries `legacy_publisher: "NACE International"`. The `publisher` field is `AMPP` (current). `publisher_history` MAY be present and MUST list both names with non-overlapping date ranges; the boundary is `2020-12-31` → `2021-01-01`.
- [ ] Citation downstream-resolution check (literal-equality on `revision` string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - `nace-mr-0175.md` page MUST use `revision: "2009-2nd-Ed"` in BOTH frontmatter AND any test `Citation(...)` call.
  - `nace-mr-0175-1995.md` page MUST use `revision: "1995"`.
  - `nace-tm-0177.md` page MUST use `revision: "1996"` (the on-disk edition; current TM 0177 is 2016 — calc-callers needing the 2016 edition must wait for the page to be updated).
  - The OPTIONAL `ampp-knowledge-hub.md` (if approved) MUST use `revision: "public-metadata-required-before-citation-use"` and be excluded from this resolution check (`pytest.mark.skip`).
- [ ] **`code_id` prefix discipline (Open Question resolution must be embedded as a comment in each page):** the chosen prefix (`nace-` for documents bearing the NACE imprint at publication time, `ampp-` for documents published post-2021 under AMPP imprint, `ampp-` for the publisher-level Knowledge Hub stub) is applied consistently across all pages. The resolution decision is documented in a `# code_id_prefix_rationale: ...` frontmatter comment OR in the page body's "Why this page exists" section.
- [ ] Ledger alignment: every page's `ledger_id` (frontmatter key) resolves to a row `id:` in `data/document-index/standards-transfer-ledger.yaml` (3 or 4 new rows added by this plan).
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 3-4 new pages under a "## Standards" section. **Arithmetic AC:** `page_count` after this plan = (current `page_count` at implementation time) + 3 (or +4 if AMPP stub approved).
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan.
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified — verified there are NO pre-existing NACE/AMPP pages anywhere (cross-checked by `ls knowledge/wikis/*/wiki/standards/ | grep -iE "nace|ampp"` returning empty).
- [ ] **`code_id` uniqueness across wiki domains:** test asserts no `code_id` duplicated across `knowledge/wikis/*/wiki/standards/*.md`. Vacuous for NACE/AMPP today (no other pages exist) but guards future drift.
- [ ] Plan review artifact present at `scripts/review/results/2026-05-03-plan-W4A-claude-internal.md` (single-author Claude review). Codex/Gemini UNAVAILABLE per memory.
- [ ] Adversarial review explicitly addresses: (a) the corpus-vs-citation-frequency mismatch (most-cited NACE codes have no raw on disk), (b) the NACE → AMPP rebrand `publisher`/`legacy_publisher` discipline, (c) the on-disk editions (1995, 2009 2nd Ed, 1996) all being older than the publisher-current editions (current MR 0175 is jointly-ISO 15156 2020; current TM 0177 is 2016), (d) the `code_id` prefix decision.

---

## Adversarial Review Summary

<!-- To be filled after Step 4 (adversarial review). Plan currently `status: draft`. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | TBD | _pending_ |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** _pending r1 internal Claude review_

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`.

---

## Risks and Open Questions

- **Risk (NEW — corpus-vs-citation-frequency mismatch):** The 7 NACE codes most-cited in `digitalmodel/src/` (`SP0169` 14×, `SP0176` 3×, `SP0207` 1×, `SP0490` 1×, `SP0502` 3×, `TM0497` 3×, `MR0175` 1×) have raw on-disk PDFs for ONLY `MR0175`. W4-A is therefore corpus-bound, NOT citation-frequency-bound. **Mitigation:** explicit prose in each page's "Why this page exists" section noting that downstream calc-callers needing SP-series codes (e.g., `cathodic_protection/iccp_design.py` cites `SP0169`) must wait for W4-B publisher-portal-pointer pages. Disambiguation rule: every priority page's `sources` frontmatter MUST list at least one verifiable `/mnt/ace/...` path; pages that cannot list one (the OPTIONAL `ampp-knowledge-hub.md`) are flagged stub and excluded from resolver tests via `pytest.mark.skip`.
- **Risk:** Copyright leakage. NACE/AMPP publishes from Houston TX (HQ) with cover-page strings "NACE International", "Association for Materials Protection and Performance", "© NACE International", "© AMPP". **Mitigation (inherited from W1-A/W2-A/W3-A):** word-count ceiling `<500` strict + positive-shape structural test + `extraction_policy: metadata-only` + `raw_copy_allowed: false` + cross-review on every revision touching `wiki/standards/nace-*.md` / `ampp-*.md`. **Honesty caveat:** denylist alone is necessary-but-not-sufficient.
- **Risk (NEW — multi-part umbrella discipline for MR 0175):** NACE MR 0175 (2009 2nd Ed) is published as 3 separate parts (Pt 1 General principles, Pt 2 Carbon/low-alloy steels, Pt 3 Corrosion-resistant alloys). The W3-A `<part>_part_section` pattern handled multi-part rule books with one wiki page per Part. W4-A proposes a SINGLE umbrella page for MR 0175 (all 3 Parts) because the Parts share a common scope and are typically cited as the single document `MR 0175`. **Mitigation:** the umbrella page carries `nace_part_section: "Pt.1 / Pt.2 / Pt.3"` enumerating which parts are covered; the `sources` frontmatter lists all 3 Part PDFs as separate `/mnt/ace` paths. Calc-callers needing per-Part citation set `Citation.section` to e.g., `"Pt.2 §6.2"`. **Alternative considered and rejected:** 3 separate pages (`nace-mr-0175-pt1.md`, `nace-mr-0175-pt2.md`, `nace-mr-0175-pt3.md`) would mirror W3-A's per-Part discipline more strictly, but inflates page count to 5+ for a small corpus and violates the "small corpus" mission constraint. Reviewer SHOULD challenge this if per-Part granularity is required by an actual `digitalmodel/` consumer.
- **Risk (NEW — pre-internet 1995 edition):** The 1995 MR 0175 PDF predates the joint NACE/ISO publication and the multi-part split. It is materially different from the 2009 2nd Ed (single document, no Parts). **Mitigation:** `nace-mr-0175-1995.md` is a separate page with `supersedes: []` (it is itself superseded), `iso_equivalent` field OMITTED, and `nace_part_section` field OMITTED (single-document edition). Cross-link from current page: `supersedes: ["nace-mr-0175-1995"]`.
- **Risk (NEW — on-disk edition vs. publisher-current edition gap):** All 5 on-disk standards documents are OLDER than the publisher-current editions (MR 0175 on disk is 2009; current is jointly-ISO 15156 2020. TM 0177 on disk is 1996; current is 2016). Calc-callers using the wiki pages will get `revision` strings that DO NOT match the latest publisher-released edition. **Mitigation:** every page body MUST include a "Where to find the full text" section pointing to `https://store.ampp.org/` with explicit prose: "On-disk edition is `<year>`. Publisher-current edition is `<year>`. Calc-callers MUST verify against the publisher-current edition before use; this wiki page reflects the on-disk corpus only." **AC** records this as the "edition gap discipline" — every NACE page must acknowledge the gap.
- **Risk (NEW — NACE → AMPP rebrand citation continuity):** A `digitalmodel/` source written before 2021-01-01 may cite `Citation(publisher="NACE International", ...)`. Post-rebrand pages with `publisher: AMPP` will fail literal-equality validation. **Mitigation:** the wiki page's `publisher` is `AMPP` (current canonical); calc-callers MUST migrate citations to `publisher="AMPP"`. The `legacy_publisher` frontmatter is documentation-only — the citation resolver does NOT match against it. A follow-up issue against `digitalmodel/src/digitalmodel/citations/schema.py` MAY add publisher-alias support; OUT OF SCOPE for W4-A. The grep above shows zero existing structured `Citation(...)` calls for NACE in `digitalmodel/src/`, so this is a forward-discipline rule, not a migration risk.
- **Risk (inherited from W2-A / W3-A):** Hidden assumption — `digitalmodel` grep-frequency is NOT the priority-selection criterion for W4-A (only `MR0175` is on disk + cited; other cited codes await W4-B). Cross-repo consumer audit follow-up was already filed under W2-A P2-2 covering all standards-publisher consumers; that audit covers NACE/AMPP too — no new follow-up needed.
- **Risk:** Ledger-form / wiki-form ID divergence. Ledger uses uppercase-with-hyphens (`NACE-MR-0175-2009`); wiki uses lowercase-kebab (`nace-mr-0175`). **Mitigation:** add a `ledger_id` frontmatter key on each wiki page; `test_ledger_alignment` checks `frontmatter['ledger_id']` exists in the ledger, NOT `code_id`. Same pattern as W3-A.
- **Risk (NEW — conference-paper exclusion):** The 3 NACE Papers (01469, 04022, 05153) on disk are vendor-derivative per #2482 and are EXCLUDED from W4-A. A future contributor may try to add wiki pages for them. **Mitigation:** the test suite asserts `nace-paper-*.md` and `ampp-paper-*.md` patterns DO NOT exist in `wiki/standards/`. If a contributor argues a paper should be promoted, they MUST file a separate issue against the #2482 vendor-derivative deny-list governance, not extend W4-A.
- **Open:** **`code_id` prefix decision (REQUIRES USER CONFIRMATION DURING PLAN-REVIEW).** Three options:
  1. **`nace-*` for all NACE-imprint pages** (publication-time imprint) → `nace-mr-0175.md`, `nace-mr-0175-1995.md`, `nace-tm-0177.md`. AMPP-imprint future page (e.g., a 2023+ AMPP standard) would use `ampp-*`. The OPTIONAL knowledge-hub stub uses `ampp-knowledge-hub.md` because the URL is post-rebrand. **Recommended.** Matches the publication-time-imprint convention also used by API/DNV/ABS pages.
  2. **`ampp-*` for all** (force current-publisher imprint) → `ampp-mr-0175.md`, etc. Reflects the current publisher but makes the existing `digitalmodel/` `NACE MR0175` references resolver-invisible until calc-callers migrate the citation strings.
  3. **Hybrid:** legacy NACE-imprint docs use `nace-*`, AMPP-imprint future docs use `ampp-*`, the publisher pointer uses `ampp-*`. Same as option 1.
  This plan proposes **Option 1** (recommended). Reviewer MUST confirm.
- **Open:** **Should the OPTIONAL `ampp-knowledge-hub.md` stub be created?** It is a publisher-level pointer (URL) NOT a standard, so it occupies an unusual slot in `wiki/standards/`. Pros: gives W4-B a forward home for the publisher-portal pointers (SP0169, SP0176, etc.) without inventing a new directory. Cons: violates the "standards page = a standard" mental model; could mislead the citation resolver. **Plan default:** include it, flagged stub-only, excluded from resolver tests via `pytest.mark.skip`. Reviewer MAY drop it; scope falls to 3 pages.
- **Open:** Should `nace-mr-0175.md` be ONE umbrella page (current proposal) or 3 per-Part pages (`-pt1.md`/`-pt2.md`/`-pt3.md`)? See multi-part umbrella Risk above. Plan default: ONE umbrella. Reviewer MAY require split.
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_nace.py` (one file, parametrized) matching W3-A, or be split per-page? Plan proposes single file (matches W3-A).
- **Open:** Issue title and labels. Proposed title: `feat(llm-wiki): bounded NACE/AMPP standards summary promotion to engineering-standards wiki (W4-A)`. Proposed labels: `priority:medium,cat:documentation,domain:knowledge-management,domain:standards`. Issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md` and is NOT performed by this plan.

---

## Complexity: T2

**T2** — multi-file documentation work (3 or 4 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 7 or 8 files), no new code modules, but a real test contract (≥17 parametrized assertions × 3-4 pages = ~55-70 effective test cases). Implementation is templated repetition. Design risk is concentrated in (a) NACE → AMPP rebrand `publisher`/`legacy_publisher` discipline (NEW for W4-A), (b) the multi-part umbrella vs. per-Part decision for MR 0175, (c) the on-disk-edition vs. publisher-current-edition gap discipline, (d) the `code_id` prefix decision. Slightly LIGHTER than W1-A/W2-A/W3-A (3-4 pages instead of 10) reflecting the small on-disk corpus, but the rebrand-and-edition-gap design surface keeps it firmly in T2 territory rather than T1.
