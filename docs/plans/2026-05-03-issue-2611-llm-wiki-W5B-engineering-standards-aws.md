# Plan for LLM-Wiki Completeness W5: Bounded AWS Welding Standards Summary Promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** _not yet filed — this plan is `status: draft` and does NOT pre-authorize an issue filing per memory `feedback_never_offer_to_self_label_plan_approved.md`. Proposed title and labels appear in the trailing return-format block; user-in-loop approval gates the filing._
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) (CLOSED) — overnight Elements corpus planning wave; this W5 packet is a continuation under the same bounded-summary contract.
> **Sibling precedent (W1-A, API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN) — original bounded-promotion pattern. The W3-C erratum [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN) tracks #2471 over-citation cleanup; W5 does NOT inherit that defect.
> **Sibling precedent (W2-B, ASME):** [#2591](https://github.com/vamseeachanta/workspace-hub/issues/2591) (OPEN) — closest welding cousin (ASME BPVC IX qualifies welders/procedures that AWS D1.1 references); cross-reference frontmatter pattern is inherited here.
> **Sibling precedent (W4-A, NACE):** [#2599](https://github.com/vamseeachanta/workspace-hub/issues/2599) (OPEN) — direct shape precedent; revised-after-r1 framing of #2471 sanction-scope is adopted verbatim.
> **Sibling precedent (W4-B, BSI):** [#2600](https://github.com/vamseeachanta/workspace-hub/issues/2600) (OPEN) — sibling 2026-05-03 batch plan, shape parity expected.
> **Path sanction (AWS):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for the engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision for CSA-Z276 specifically (verified per memory `project_wiki_standards_path_decision.md`); it is NOT a general-standards path sanction and is referenced here only as the historical origin of the frontmatter triple, not as AWS path authority.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter.
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`).
> **Calc-citation pilot (epic-level):** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors pilot. W5 does NOT extend the pilot; downstream wiring is a calc-module concern.
> **Review artifacts:** `scripts/review/results/2026-05-03-plan-W5-claude-internal.md` (single-author Claude r1, to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini UNAVAILABLE per memory (codex-cli 0.124.0 stdin-hang #2479; Gemini sandbox cwd=/tmp blocks workspace-hub overlay reads).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). Downstream consumer that will resolve the wiki pages this plan creates.
- Found: AWS D1.1 is structurally referenced in `digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py` — the module exposes an `AWS_CURVES` dict (S-N fatigue curves per AWS D1.1) and lists `AWS D1.1 (Structural welding)` alongside `BS 7608` and `IIW` as a recognized reference standard. `digitalmodel/src/digitalmodel/structural/fatigue/__init__.py`, `digitalmodel/src/digitalmodel/fatigue/sn_library.py`, and `digitalmodel/src/digitalmodel/fatigue/weld_classification.py` also reference AWS D1.1. **AWS D1.1 is the headline citation target** for the structural-fatigue/welding modules.
- Internal-reference frequency: AWS appears in `digitalmodel/src/` as 12 hits across **1 distinct code** — `AWS D1.1` (12 hits across 4 source files; 11 of `AWS D1.1` form + 1 of `AWS-D1.1` form). NO internal references to AWS A5-series, A2.4, or D1.2 yet.
- Gap: zero AWS wiki pages exist anywhere — `ls knowledge/wikis/*/wiki/standards/ | grep -iE "^aws-"` returns no matches. The `engineering-standards/wiki/standards/` directory holds only `api-17e.md` today (1 file).

### Standards

The on-disk AWS corpus is 15 PDFs total. Several are derivative training/guide materials (vendor-derivative per #2482) and EXCLUDED from W5. Standards documents collapse to 6 priority wiki pages.

| Standard | Status | Source |
|---|---|---|
| AWS D1.1/D1.1M (2010) Structural Welding Code — Steel | gap (4 PDFs across 2006/2009/2010 editions on disk; ledger has no row) | `/mnt/ace/O&G-Standards/AWS/AWS D1.1/AWS D1.1-D1.1M (2010) Structural Welding Code - Steel.pdf` |
| AWS D1.2 (2003) Structural Welding Code — Aluminum | gap | `/mnt/ace/O&G-Standards/AWS/AWS D1.2/AWS D1.2 (2003) Structural Welding Code Aluminum.pdf` |
| AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and NDE | gap (reference document, NOT a code per se — see Open Questions) | `/mnt/ace/O&G-Standards/AWS/AWS A2.4/AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and Nondestructive Examination.pdf` |
| AWS A5.5 — Specification for Low-Alloy Steel Electrodes for SMAW | gap (`AWS-A5-5.pdf` at AWS-folder root, 2001 PDF generation date — likely 1996 edition reissue; on-disk edition needs verification at implementation time, see Risks) | `/mnt/ace/O&G-Standards/AWS/AWS-A5-5.pdf` |
| AWS A5.10 (1999) Specification for Bare Aluminum and Aluminum-Alloy Welding Electrodes and Rods | gap on wiki side, but **ledger row already exists** (`id: AWS-A5.10`, `status: done`, `repo: acma-projects`) — wiki page is the missing piece | `/mnt/ace/O&G-Standards/AWS/AWS A5.10/AWS A5.10 (1999)Spec for Bare Alum & Alum Alloy Welding Electrodes & Rods.pdf` |
| AWS-D1-1-D1-1M-2008(1).pdf (root-level duplicate, 2008 edition) | gap — same code as priority #1 above; treat as additional `sources` entry on `aws-d1-1.md` (NOT a separate page) | `/mnt/ace/O&G-Standards/AWS/AWS-D1-1-D1-1M-2008(1).pdf` |
| Guide to Filler Metal.pdf, WELDING GUIDE.pdf, AWS Q & A Chapter 1-6.pdf, Fundamental examination.pdf, Guidance_on_the_Welding_of_Weathering_Steels.pdf, SURFACE TENSION.pdf | EXCLUDED — guide / training / vendor-derivative per #2482 | n/a |

This plan therefore proposes **6 priority wiki pages** (within the 6-8 ceiling):

1. `aws-d1-1.md` — **HEADLINE**. Structural Welding Code — Steel. Multi-edition umbrella covering 2006/2009/2010 on-disk PDFs; canonical `revision` pinned to on-disk **2010** with explicit prose noting current publisher edition is **2025** (web-verified — see Evidence). Cross-referenced by `digitalmodel/structural/fatigue/sn_curves.py`.
2. `aws-d1-2.md` — Structural Welding Code — Aluminum. Companion to D1.1 covering aluminum structures.
3. `aws-a2-4.md` — Standard Symbols for Welding, Brazing, and NDE. **Open Question:** A2.4 is a reference / symbology standard, not a code per se. Promote here as a `wiki/standards/` page (proposed default) OR re-route to `wiki/concepts/` (alternative). See Open Questions.
4. `aws-a5-5.md` — Specification for Low-Alloy Steel Electrodes for SMAW. On-disk edition needs verification (see Risks); `revision: "public-metadata-required-before-citation-use"` placeholder used until edition is confirmed.
5. `aws-a5-10.md` — Specification for Bare Aluminum and Aluminum-Alloy Welding Electrodes and Rods. On-disk edition is **1999**.
6. `aws-filler-metal-overview.md` — concept-style overview of the AWS A5-series filler-metal classification family. **Open Question:** the schema slot is `wiki/standards/` not `wiki/concepts/` — this page is a series-overview and may be better routed to `wiki/concepts/`. See Open Questions; if rejected as out-of-place, scope drops to **5 pages**.

The promoted set is corpus-bound (everything has a raw on-disk PDF) AND citation-aware (D1.1 leads because it's the only AWS code internally cited in `digitalmodel/`). Other A5-series codes commonly cited in O&G welding workflows (A5.18 GMAW, A5.20 FCAW, A5.28 low-alloy GMAW, A5.29 low-alloy FCAW, A5.36 fluxes) are NOT on disk and are deferred to a future W5-B publisher-portal-pointer pass.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards code page; metadata-stub frontmatter pattern this plan replicates. Confirms lowercase-kebab `code_id` convention and the `revision: public-metadata-required-before-citation-use` placeholder convention for cases where the on-disk edition cannot be pinned.
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`. Reality on disk: `find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` returns **9** — pre-existing drift (same drift documented in W4-A MINOR-4). **Arithmetic AC:** the implementation MUST first reconcile current `page_count` against on-disk count, then apply `+6` (or `+5` if the filler-metal-overview is rejected per Open Questions).
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision`); the new pages will all comply. Schema example values use lowercase-kebab. **This is the path-sanction authority** for engineering-standards domain (NOT #2471).
- `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` — recently-landed engineering-wiki standards page (untracked at session start, per `git status`); not directly in scope, but confirms the engineering-domain wiki is also receiving fresh standards pages alongside engineering-standards.
- No pre-existing AWS pages exist in any wiki (verified by `ls knowledge/wikis/*/wiki/standards/ | grep -iE "^aws-"` returning empty).

### Documents consulted

- `docs/plans/2026-05-03-issue-2599-llm-wiki-W4A-engineering-standards-nace.md` — direct shape precedent. **Inherited contracts:** bounded-preview frontmatter, no-raw-text test, citation-resolvability test, lowercase-kebab `code_id`, multi-edition / multi-document handling pattern, ledger-form/wiki-form ID divergence (`ledger_id` frontmatter key), revised-after-r1 framing of #2471 sanction-scope.
- `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` — W2-B ASME plan; closest welding cousin (ASME BPVC IX qualifies welders that AWS D1.1 references). Cross-reference frontmatter pattern (`cross_references` to ASME / API counterparts) inherited from this sibling.
- `docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md` — sibling 2026-05-03 plan; shape parity check.
- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — original W1-A pattern (API standards); confirms cross-reference framing for API 1104 / API 650 ↔ AWS D1.1 welding-procedure overlap.
- `data/document-index/standards-transfer-ledger.yaml` — searched for AWS: **1 row exists** (`id: AWS-A5.10`, `status: done`, `repo: acma-projects`, no `doc_path` populated). All other 5 (or 4) priority pages require new ledger rows. The existing AWS-A5.10 row will be ENRICHED (`doc_path` populated) NOT duplicated.
- `data/document-index/online-resource-registry.yaml` — searched for AWS publisher portal: no `aws_pubs` or `aws_store` entry currently. Public URL `https://pubs.aws.org/` will be referenced in page bodies; registry follow-up is OUT OF SCOPE for W5 (separate registry-grooming issue).
- `.claude/rules/calc-citation-contract.md` — citation contract this plan exists to satisfy.
- `.claude/rules/coding-style.md` and `.claude/rules/patterns.md` — universal rules.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in **future tense**; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). The path-routing principle generalizes only to {marine-engineering, engineering, naval-architecture}; for engineering-standards wiki, cite the LOCAL `engineering-standards/CLAUDE.md` directory schema. Load-bearing.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; phrase lists are narrowly scoped to AWS-specific copyright/cover-page strings (Miami FL HQ, "© American Welding Society", "All rights reserved").
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review acceptable when Codex/Gemini unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex CLI 0.124.0 stdin-hang regression #2479; Codex review unavailable.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini cwd=/tmp blocks workspace-hub overlay reads; Gemini review unavailable.
- `feedback_never_offer_to_self_label_plan_approved.md` — issue filing is downstream of plan-review approval; this plan is `status: draft` and does NOT pre-authorize a downstream issue.

### Gaps identified

- No engineering-standards wiki pages exist for any AWS code (zero — `ls knowledge/wikis/*/wiki/standards/ | grep -iE "^aws-"` returns empty).
- The standards-transfer-ledger contains 1 AWS row (`AWS-A5.10`, `status: done` but `doc_path` empty); 5 (or 4 if filler-metal-overview rejected) new ledger rows required, plus `doc_path` enrichment of the existing AWS-A5.10 row.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any AWS page.
- `digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py` references `AWS D1.1` but no `Citation` instance is wired (forward-discipline; W5 unblocks the wiring but does NOT perform it — that is a downstream calc-module follow-up).
- Cross-references are NOT yet expressed in any existing `knowledge/wikis/engineering-standards/wiki/standards/*.md` page. W5 introduces the `cross_references` frontmatter convention (with seeds pointing to ASME BPVC IX and API 1104) — the convention itself, not the cross-referenced pages, is the deliverable. **Important caveat:** the target pages (`asme-bpvc-ix.md`, `api-1104.md`) do NOT yet exist; this plan's cross_references seeds are forward-pointing dangling links that the test contract permits AS DANGLING and explicitly does NOT validate as resolvable. The ASME companion page is in W2-B scope; the API 1104 page is in W1-A scope or a future W1-B scope.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):
- `#2540` — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — W1-A engineering-standards API
- `#2591` — OPEN — W2-B engineering-standards ASME
- `#2596` — OPEN — W3-C #2471 sanction-scope erratum
- `#2599` — OPEN — W4-A engineering-standards NACE/AMPP
- `#2600` — OPEN — W4-B engineering-standards BSI
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — body explicitly scopes to CSA-Z276
- `#2482` — CLOSED — vendor-derivative deny-list governance
- `#2481` — CLOSED — calc-citation contract pilot

**File existence** (`ls -la /mnt/ace/O&G-Standards/AWS/` 2026-05-03):
```
drwxr-xr-x  AWS A2.4               (1 PDF — A2.4 (2007) Symbols)
drwxr-xr-x  AWS A5.10              (1 PDF — A5.10 (1999) Aluminum electrodes)
-rwxr-xr-x  AWS-A5-5.pdf           (root-level; A5.5 Low-Alloy SMAW; PDF created 2001)
drwxr-xr-x  AWS D1.1               (4 PDFs: 2006 scanned, 2006 searchable, 2009 scanned, 2010 D1.1/D1.1M)
drwxr-xr-x  AWS D1.2               (1 PDF — D1.2 (2003) Aluminum structural)
-rwxr-xr-x  AWS-D1-1-D1-1M-2008(1).pdf  (root-level duplicate-edition of D1.1; 2008 reissue)
-rwxr-xr-x  AWS Q & A Chapter 1-6.pdf       (EXCLUDED — Q&A guide; vendor-derivative)
-rwxr-xr-x  Fundamental examination.pdf      (EXCLUDED — exam prep)
-rwxr-xr-x  Guidance_on_the_Welding_of_Weathering_Steels.pdf  (EXCLUDED — guidance doc)
-rwxr-xr-x  Guide to Filler Metal.pdf        (EXCLUDED — guide)
-rwxr-xr-x  SURFACE TENSION.pdf              (EXCLUDED — single-topic article)
-rwxr-xr-x  WELDING GUIDE.pdf                (EXCLUDED — guide)
```
Total: 15 documents (8 PDFs in subdirs, 7 at root); 7 standards (counting D1.1 family as 5 PDFs across 4 editions of 1 code = umbrella) + 8 excluded guides/papers.

- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (template exemplar)
- EXISTS: `knowledge/wikis/engineering-standards/CLAUDE.md` (path-sanction authority)
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (resolver target)
- EXISTS: `digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py` (downstream consumer of `aws-d1-1.md`)
- EXISTS: `tests/governance/test_2471_citation_scope.py` (allowlist-polarity guardrail; this plan must not regress it — note: PLANS_GLOB is hard-pinned to `2026-05-02-*.md` and does NOT scan this 2026-05-03 plan, same situation as W4-A; compliance is by manual reviewer sweep)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/aws-d1-1.md`, `aws-d1-2.md`, `aws-a2-4.md`, `aws-a5-5.md`, `aws-a5-10.md`, and OPTIONAL `aws-filler-metal-overview.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_aws.py`

**Internal-reference proof — AWS in workspace digitalmodel** (`grep -rohE "AWS[ _-]?(A|D)[0-9.]+" digitalmodel/src/ | sort | uniq -c`):
```
     11 AWS D1.1
      1 AWS-D1.1
```
Total: 12 hits across 1 code. **Of the 6 priority pages, only `D1.1` is currently cited internally** — the A2.4 / D1.2 / A5.5 / A5.10 pages are corpus-driven (on disk + within stated mission scope), not citation-frequency-driven. Selection criterion is: "on-disk AND (cited internally OR within the welding-workflow standards set explicitly named in the W5 mission brief)".

**AWS source files in digitalmodel** (`grep -rli "AWS D1\|AWS A5\|AWS A2.4" digitalmodel/src/`):
```
digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py
digitalmodel/src/digitalmodel/structural/fatigue/__init__.py
digitalmodel/src/digitalmodel/fatigue/sn_library.py
digitalmodel/src/digitalmodel/fatigue/weld_classification.py
```
All 4 files cite `AWS D1.1` only. None cite A5/A2 codes.

**Existing AWS ledger rows** (`grep -B1 -A14 "id: AWS-" data/document-index/standards-transfer-ledger.yaml`):
```
- id: AWS-A5.10
  title: AWS A5.10 Specification for Bare Aluminum and Aluminum-Alloy Welding Electrodes
    and Rods
  org: ''
  domain: materials
  doc_path: ''
  doc_paths: []
  status: done
  wrk_id: null
  repo: acma-projects
  modules: []
  implemented_at: '2026-04-06T02:51:10'
  notes: This specification establishes requirements for the classification of bare
    aluminum and aluminum-alloy welding electrode
  exhausted: false
```
Pre-existing row for AWS-A5.10 with empty `doc_path` — W5 enriches `doc_path` with the verified `/mnt/ace/...` path; the row is NOT recreated.

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

**Page-count drift** (`find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` 2026-05-03):
```
9
```
Index claims `page_count: 5`. Pre-existing drift; same situation documented in W4-A MINOR-4 fix.

**Public-revision evidence (web)**:
- AWS standards portal: <https://pubs.aws.org/> — current AWS D1.1/D1.1M is at the **2025** edition (publisher-confirmed via `pubs.aws.org/p/2264/d11d11m2025-structural-welding-code-steel`). On-disk newest is **2010** (with 2008 root-level duplicate). The `revision` frontmatter for `aws-d1-1.md` will pin to `"2010"` with explicit prose noting publisher-current is `2025`; calc-callers MUST verify against the current edition before use.
- AWS A5-series 2025 cycle: A5.1/A5.1M:2025 (carbon steel SMAW), A5.18/A5.18M:2025 (carbon steel GMAW), A5.02/A5.02M:2025 — all reissued 2025. **A5.5 specifically:** no confirmed 2025 reissue surfaced via the search; latest publisher edition appears to be A5.5/A5.5M:2014 (subject to verification at implementation time). The on-disk PDF (created 2001) is most likely the **1996** edition with a 2001 reissue print — needs verification by reading the cover page at implementation time. Plan's default `revision` for A5.5 is `"public-metadata-required-before-citation-use"` until cover-page verification is performed.
- AWS A5.10 on-disk edition is **1999** (per filename and ledger note already filed).
- AWS A2.4 on-disk edition is **2007** (per filename); current publisher edition is **A2.4:2020** (subject to verification).
- AWS D1.2 on-disk edition is **2003**; current publisher edition is **D1.2/D1.2M:2014** (subject to verification).

<!-- Distinct sources counted: existing repo code + sn_curves.py (1), standards ledger (2), engineering-standards CLAUDE.md schema (3), W4-A precedent plan (4), W2-B ASME precedent plan (5), W4-B BSI sibling plan (6), `/mnt/ace/.../AWS/` corpus contents (7), citation rule (8), project memory (9), web public catalogs / pubs.aws.org (10). 10 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2611-llm-wiki-W5B-engineering-standards-aws.md` |
| Wiki page (1 — headline) | `knowledge/wikis/engineering-standards/wiki/standards/aws-d1-1.md` (Structural Welding Code — Steel; multi-edition umbrella 2006/2009/2010 + root-level 2008 PDF) |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/aws-d1-2.md` (Structural Welding Code — Aluminum, 2003) |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/aws-a2-4.md` (Welding Symbols, 2007) — see Open Questions on standards-vs-concepts routing |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/aws-a5-5.md` (Low-Alloy SMAW Electrodes; on-disk edition TBD) |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/aws-a5-10.md` (Bare Aluminum Electrodes & Rods, 1999) |
| Wiki page (6 — OPTIONAL) | `knowledge/wikis/engineering-standards/wiki/standards/aws-filler-metal-overview.md` (A5-series family overview; flagged in Open Questions) |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (5 new rows + 1 enrichment) |
| Test contract | `tests/knowledge/test_engineering_standards_aws.py` |
| Plans-index update | `docs/plans/README.md` |
| Plan review — Claude (r1, single-author) | `scripts/review/results/2026-05-03-plan-W5-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |

---

## Deliverable

Five (or six if the OPTIONAL filler-metal-overview is approved) new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/`, one per priority AWS code, each carrying calc-citation-contract-compliant frontmatter (`code_id`, `publisher`, `revision`, `extraction_policy: metadata-only`, `raw_copy_allowed: false`, plus AWS-specific `aws_doc_number` and the new W5 `cross_references` frontmatter convention seeded with pointers to ASME BPVC IX and API 1104 counterparts) and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/AWS/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream `digitalmodel/structural/fatigue/sn_curves.py` (and other welding-fatigue calc modules) CAN resolve a `Citation` instance for AWS D1.1 without any verbatim source text entering git.

---

## Pseudocode

The work is templated 5-6x repetition. Each new wiki page follows this skeleton (modulo `revision` and `aws_doc_number`):

```
---
title: "<Full AWS document name> — bounded summary"
tags: ["aws", "standards", "welding", "<discipline-tag>", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: aws-d1-1                        # lowercase-kebab; matches engineering-standards CLAUDE.md, api-17e
publisher: AWS                           # American Welding Society
publisher_full: "American Welding Society"
revision: "2010"                         # on-disk edition; publisher-current is 2025 — see Risks
revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"  # OPTIONAL
verified_on: 2026-05-03                  # OPTIONAL
public_url: https://pubs.aws.org/p/2264/d11d11m2025-structural-welding-code-steel  # OPTIONAL — current-edition link
sources:
  - <one or more /mnt/ace/... paths — pointer only, never quoted>
extraction_policy: metadata-only
raw_copy_allowed: false
aws_doc_number: "D1.1/D1.1M"             # AWS document-number convention (slash form for dual unit)
ledger_id: AWS-D1.1                      # bridge to standards-transfer-ledger uppercase form
cross_references:                        # NEW W5 frontmatter convention; forward-pointing dangling links allowed
  - { code_id: "asme-bpvc-ix", relation: "qualifies", note: "ASME BPVC Section IX qualifies welders/procedures referenced by D1.1 contract documents" }
  - { code_id: "api-1104", relation: "companion", note: "API 1104 is the pipeline-welding companion code (D1.1 covers structural; 1104 covers transmission pipelines)" }
cross_links:
  - []
---

# <Full AWS document name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.

## Where to find the full text
- Raw PDF: <absolute /mnt/ace/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://pubs.aws.org/ (registration required for purchase/download)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code, or "no live caller; future-needed">

## Edition gap discipline
On-disk edition is `<year>`. Publisher-current edition is `<year>`. Calc-callers
MUST verify against the publisher-current edition before use; this wiki page
reflects the on-disk corpus only.

## Cross-references
- [[asme-bpvc-ix]] (ASME BPVC IX qualifies welders/procedures — page does NOT yet exist; W2-B will create)
- [[api-1104]] (companion pipeline-welding code — page does NOT yet exist; W1-A or follow-up)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file uses a parametrized fixture iterating over the 5-6 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/aws-d1-1.md` | HEADLINE bounded summary for AWS D1.1/D1.1M (Structural Welding Code — Steel). Multi-edition umbrella covering 2006/2008/2009/2010 on-disk PDFs. Highest-relevance AWS code; cited 11+ times across `digitalmodel/structural/fatigue/`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/aws-d1-2.md` | Bounded summary for AWS D1.2 (Structural Welding Code — Aluminum, 2003). Companion to D1.1 covering aluminum structures. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/aws-a2-4.md` | Bounded summary for AWS A2.4 (Standard Symbols for Welding, Brazing, and NDE, 2007). Reference symbology — see Open Questions on standards-vs-concepts routing. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/aws-a5-5.md` | Bounded summary for AWS A5.5 (Low-Alloy Steel Electrodes for SMAW). On-disk edition TBD; placeholder `revision: public-metadata-required-before-citation-use` until cover-page verification. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/aws-a5-10.md` | Bounded summary for AWS A5.10 (Bare Aluminum and Aluminum-Alloy Welding Electrodes and Rods, 1999). Existing ledger row; wiki page is the missing piece. |
| Create (OPTIONAL) | `knowledge/wikis/engineering-standards/wiki/standards/aws-filler-metal-overview.md` | A5-series family overview. **Flagged in Open Questions** — drop if not approved. |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 5-6 new rows; bump `page_count` per the **arithmetic AC** (reconcile-then-add: current on-disk count + 5 or +6), not a fixed value. |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 5 new rows: `AWS-D1.1`, `AWS-D1.2`, `AWS-A2.4`, `AWS-A5.5`, optionally `AWS-FILLER-METAL-OVERVIEW`. Enrich existing `AWS-A5.10` row with `doc_path`. |
| Create | `tests/knowledge/test_engineering_standards_aws.py` | Test contract: frontmatter, no-raw-text, citation resolvability, ledger alignment, code_id uniqueness across wikis, `cross_references` shape (NEW W5 convention test), edition-gap discipline. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_aws.py`. Each test parametrized over the 5 or 6 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 5-6 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, lowercase-kebab; filename stem equals `code_id` verbatim (e.g., `aws-d1-1.md` ↔ `aws-d1-1`) |
| `test_frontmatter_has_publisher_aws` | publisher discipline | YAML frontmatter | `publisher == "AWS"`; if present, `publisher_full == "American Welding Society"` |
| `test_frontmatter_has_revision` | revision presence per calc-citation-contract rule 2 | YAML frontmatter | `revision` non-empty string; matches AWS regex `^(\d{4}\|public-metadata-required-before-citation-use)$` |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_has_aws_doc_number` | AWS-specific traceability | YAML frontmatter | `aws_doc_number` non-empty (e.g. `"D1.1/D1.1M"`, `"A5.5"`, `"A2.4"`) on every page (including OPTIONAL filler-metal-overview which uses `"A5-series"`) |
| `test_cross_references_shape_when_present` | NEW W5 convention discipline | YAML frontmatter `cross_references` (when present) | each entry is a dict with keys `{code_id, relation, note}`; `code_id` lowercase-kebab; `relation` in `{qualifies, companion, references, superseded-by, supersedes, equivalent}` |
| `test_cross_references_dangling_allowed` | forward-pointing dangling links permitted | `cross_references[*].code_id` | test does NOT fail if target page absent; only validates entry shape |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow AWS-specific phrase set, body-only scan per W4-A MAJOR-3) | page body (post-frontmatter only) | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict `<500` word ceiling matching W1-A/W2-A/W3-A/W4-A | page body | `0 < word_count < 500` strict on both bounds |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only allowed sections | page body | top-level `##` headings exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Edition gap discipline", "Cross-references"}` |
| `test_links_only_pointer_to_mnt_ace` | mentions raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/AWS/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolver actually reads the wiki page | invoke resolver function from `digitalmodel/src/digitalmodel/citations/schema.py` for each AWS page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised; pages with `revision: public-metadata-required-before-citation-use` are excluded via `pytest.mark.skip` |
| `test_ledger_alignment` | every page's `ledger_id` resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `ledger_id` | matching `id:` row found in ledger YAML |
| `test_code_id_unique_across_wiki_domains` | inherited from W2-A/W3-A/W4-A AC | every `code_id` in `knowledge/wikis/*/wiki/standards/*.md` | no duplicates |
| `test_index_lists_all_pages` | wiki index updated | `index.md` contents | each new page link present in the "## Standards" section |
| `test_edition_gap_section_present` | edition-gap discipline (NEW W5) | page body | every page (including the OPTIONAL overview) carries an `## Edition gap discipline` H2 with prose acknowledging on-disk vs. publisher-current; pages where on-disk == publisher-current may state "On-disk edition is current as of <date>" |

**Scope rule (inherited from W4-A MAJOR-3):** the no-raw-text test scans **page body only** (Markdown content after the closing `---` frontmatter delimiter). Frontmatter is explicitly EXCLUDED from the scan, so values like `publisher_full: "American Welding Society"` cannot trigger denylist hits. Test implementation MUST split the file at the second `---` line and scan only the post-frontmatter portion.

`RAW_TELLTALE_PHRASES` is a narrowly-scoped list (≤12 entries) drawn from AWS publication front-matter conventions. **Each entry is a contiguous cover-page template token, NOT a paraphrasable name** — paraphrased prose like "published by the American Welding Society" or "AWS standards are issued from Miami, Florida" is allowed in body, while specific cover-page boilerplate strings are forbidden:

- "© American Welding Society. All rights reserved."  (single contiguous cover-page boilerplate)
- "© AWS. All rights reserved."  (single contiguous cover-page boilerplate)
- "ANSI/AWS"  (American National Standard cover-page designator with publisher prefix)
- "Reproduction, copy or transmission of this publication"  (cover-page legal-notice template)
- "ISBN 978-0-87171"  (AWS ISBN prefix as contiguous string)
- "550 N.W. LeJeune Road, Miami, FL"  (specific contiguous cover-page imprint string)
- "First published"  (cover-page publication-history boilerplate)
- "Reaffirmed"  (cover-page revision-history boilerplate)
- "An American National Standard" — flagged ONLY when within 5 tokens of "AWS" (regex: `(AWS|American Welding Society)[^.]{0,40}American National Standard` and reverse). Bare "American National Standard" is allowed because the phrase is generic.

**Deliberately allowed in body (paraphrased prose):**
- "American Welding Society" used as paraphrased publisher reference
- "Miami, Florida" used in paraphrased prose about HQ location
- `D1.1`, `D1.2`, `A2.4`, `A5.5`, `A5.10` (document numbers)
- `structural welding`, `filler metal`, `welding symbols`, `SMAW`, `GMAW`, `FCAW` (technical concept paraphrase)
- `ASME BPVC IX`, `API 1104`, `BS 7608`, `IIW` (cross-references to other codes)

**Test determinism rule (inherited from W4-A MAJOR-3):** every `RAW_TELLTALE_PHRASES` entry is a deterministic literal substring or a fully-specified regex. No "within N words of a template" handwaving except the explicit `(AWS|American Welding Society)[^.]{0,40}American National Standard` regex above.

The denylist will NOT overlap with OCIMF, API, DNV, ABS, NACE, or BSI denylists (different publisher conventions). **Honesty caveat (inherited):** denylist alone will NOT catch a 100-200-word verbatim clause copy; reviewers MUST manually inspect every revision.

---

## Acceptance Criteria

- [ ] All 5 (or 6 if OPTIONAL overview approved) new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_aws.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No regression: `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes (the W3-C erratum's guardrail must remain green). **Note (inherited from W4-A MAJOR-1):** the guardrail's `PLANS_GLOB` is hard-pinned to `docs/plans/2026-05-02-*.md` and does NOT scan this 2026-05-03 plan. The AC therefore guarantees that no in-scope plans regress; it does NOT certify W5's #2471 framing. Compliance for THIS plan is established by the prose-only manual reviewer sweep documented in the r1 review's Verified-Compliance section.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/aws-*.md` contains zero matches for `RAW_TELLTALE_PHRASES`.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated; `code_id` lowercase-kebab; filename stem equals `code_id` verbatim).
- [ ] Citation downstream-resolution check (literal-equality on `revision` string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - `aws-d1-1.md` page MUST use `revision: "2010"` (newest on-disk edition; current publisher-edition is 2025).
  - `aws-d1-2.md` page MUST use `revision: "2003"`.
  - `aws-a2-4.md` page MUST use `revision: "2007"`.
  - `aws-a5-5.md` page MUST use `revision: "public-metadata-required-before-citation-use"` UNLESS cover-page verification at implementation time pins a specific year, in which case it MUST be the verified year.
  - `aws-a5-10.md` page MUST use `revision: "1999"`.
  - The OPTIONAL `aws-filler-metal-overview.md` (if approved) MUST use `revision: "public-metadata-required-before-citation-use"` and be excluded from this resolution check (`pytest.mark.skip`).
- [ ] **Cross-references discipline (NEW W5):** every page that introduces a `cross_references` frontmatter list MUST shape each entry as `{code_id, relation, note}`; `code_id` lowercase-kebab; `relation` from the closed enum `{qualifies, companion, references, superseded-by, supersedes, equivalent}`. Forward-pointing dangling targets (e.g., `asme-bpvc-ix`, `api-1104`) are PERMITTED and the test contract explicitly does NOT validate target-page existence.
- [ ] **Edition-gap discipline (NEW W5):** every page body carries an `## Edition gap discipline` H2 section with prose comparing on-disk and publisher-current editions. Pages where on-disk == publisher-current state "On-disk edition is current as of <verification-date>".
- [ ] **`code_id` uniqueness across wiki domains:** test asserts no `code_id` duplicated across `knowledge/wikis/*/wiki/standards/*.md`. Vacuous for AWS today (no other AWS pages exist) but guards future drift.
- [ ] Ledger alignment: every page's `ledger_id` (frontmatter key) resolves to a row `id:` in `data/document-index/standards-transfer-ledger.yaml`. The pre-existing `AWS-A5.10` row is ENRICHED (`doc_path` populated with `/mnt/ace/O&G-Standards/AWS/AWS A5.10/AWS A5.10 (1999)Spec for Bare Alum & Alum Alloy Welding Electrodes & Rods.pdf`); 4 (or 5 with overview) NEW rows added.
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 5 (or 6) new pages under a "## Standards" section. **Arithmetic AC (inherited from W4-A MINOR-4):** the implementation MUST first reconcile the current `page_count` against the actual on-disk count (`find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` returns 9; index claims 5 — drift). After reconciliation, apply `+5` (or `+6` if overview approved). Final `page_count = (reconciled-current) + 5 (or +6)`.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan.
- [ ] Plan review artifact present at `scripts/review/results/2026-05-03-plan-W5-claude-internal.md` (single-author Claude review). Codex/Gemini UNAVAILABLE per memory.
- [ ] Adversarial review explicitly addresses: (a) the multi-edition umbrella discipline for D1.1 (4 PDFs across 4 editions, single page), (b) the A5.5 on-disk edition uncertainty and the placeholder revision convention, (c) the A2.4 standards-vs-concepts routing decision (Open Question), (d) the NEW `cross_references` frontmatter convention shape and the dangling-link tolerance, (e) the on-disk-edition vs. publisher-current-edition gap (every code on disk is older than current — D1.1 on-disk 2010 vs. current 2025 is the widest gap).

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | _pending_ | _to be filed at `scripts/review/results/2026-05-03-plan-W5-claude-internal.md`_ |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | sandbox cwd=/tmp blocks workspace-hub overlay reads |

**Overall result:** _pending r1 review_

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1 to follow.

---

## Risks and Open Questions

- **Risk (corpus-vs-citation-frequency mismatch):** Of the 6 priority codes, only `D1.1` is internally cited in `digitalmodel/`. `D1.2`, `A2.4`, `A5.5`, `A5.10`, and the OPTIONAL filler-metal-overview are corpus-driven (on-disk + within W5 mission scope), NOT citation-frequency-driven. **Mitigation:** explicit prose in each page's "Why this page exists" section noting "no live caller; future-needed". Selection criterion: "on-disk AND (cited internally OR within the welding-workflow standards set explicitly named in the W5 mission brief)".
- **Risk (multi-edition umbrella for D1.1):** D1.1 has 4 PDFs across 2006/2008/2009/2010 editions on disk. W5 proposes a SINGLE umbrella page with `revision: "2010"` (newest on-disk) and lists all 4 PDFs in `sources` frontmatter. **Alternative considered and rejected:** 4 separate pages (`aws-d1-1-2006.md` etc.) would inflate page count and provide no resolver value (no calc-caller pins to a specific edition). **Honesty caveat:** if a future caller needs the 2009 edition specifically, the multi-edition umbrella does not distinguish; the caller MUST request a per-edition split as a follow-up.
- **Risk (A5.5 on-disk edition uncertainty):** The `AWS-A5-5.pdf` at the AWS-folder root has a 2001 PDF creation date but no clear edition stamp in the filename. Most likely the 1996 edition with a 2001 reissue print, but verification requires reading the cover page at implementation time. **Mitigation:** default `revision: "public-metadata-required-before-citation-use"` placeholder; resolution check skipped via `pytest.mark.skip`. AC requires implementer to verify cover-page edition before commit; if verified, `revision` is updated to the verified year and the page is included in the resolution check.
- **Risk (A2.4 standards-vs-concepts routing — see Open Questions):** AWS A2.4 is a symbology / reference standard, not a code per se. Placing it in `wiki/standards/` (the proposed default) follows the engineering-standards CLAUDE.md schema but treats a reference document as a code. **Mitigation:** flagged as Open Question; reviewer MAY require re-routing to `wiki/concepts/aws-welding-symbols.md`.
- **Risk (on-disk edition vs. publisher-current edition gap):** All 5 priority on-disk standards are OLDER than publisher-current — D1.1 on-disk is 2010 (current 2025; 15-year gap, the widest in the W-series); D1.2 on-disk is 2003 (current 2014); A2.4 on-disk is 2007 (current 2020); A5.10 on-disk is 1999 (multiple revisions since). Calc-callers using the wiki pages will get `revision` strings that DO NOT match latest publisher-released editions. **Mitigation:** every page body carries a dedicated `## Edition gap discipline` H2 section (NEW W5 contract) with explicit prose acknowledging the gap and pointing calc-callers to `https://pubs.aws.org/` for the current edition before any compliance use.
- **Risk (cross_references convention is NEW):** The `cross_references` frontmatter convention is introduced by W5; no other engineering-standards page currently carries it. **Mitigation:** the test contract validates SHAPE (each entry has `{code_id, relation, note}`, `relation` from closed enum) but explicitly does NOT validate target existence — forward-pointing dangling links are permitted because `asme-bpvc-ix` and `api-1104` pages do not yet exist (W2-B and W1-A scope respectively). A follow-up issue will tighten the test once those pages land.
- **Risk (vendor-derivative exclusion challenged):** The 6 EXCLUDED non-standards documents on disk (Q&A, exam prep, weathering-steel guidance, filler-metal guide, surface-tension article, welding guide) are excluded per #2482 deny-list governance. A future contributor may try to add wiki pages for them. **Mitigation:** the test suite asserts `aws-q-and-a*.md`, `aws-welding-guide*.md`, `aws-fundamental*.md` patterns DO NOT exist in `wiki/standards/`. If a contributor argues a guide should be promoted, they MUST file a separate issue against #2482, not extend W5.
- **Risk (ledger row drift on existing AWS-A5.10):** The pre-existing `AWS-A5.10` ledger row claims `status: done` and `repo: acma-projects` but `doc_path: ''` is empty. W5 enriches the row with `doc_path`. **Mitigation:** test asserts `doc_path` is non-empty for every AWS row after this plan lands. The `acma-projects` repo claim is preserved unchanged (W5 does not contest the implementing-repo attribution).
- **Risk (paraphrase-leakage in welding-symbol descriptions):** A2.4 page describing welding symbols may inadvertently reproduce the standard's symbol-table format. **Mitigation:** the page MUST describe symbols only at the conceptual level ("the standard defines a left-side / right-side convention for fillet welds") and link to the publisher catalog for the actual symbol library; the test contract's `RAW_TELLTALE_PHRASES` includes explicit symbol-table boilerplate strings.
- **Risk (cross-repo consumer audit):** Inherited from W2-A P2-2 (covers all standards-publisher consumers). No new follow-up needed for AWS specifically.
- **Risk (ledger-form / wiki-form ID divergence):** Ledger uses uppercase-with-dots (`AWS-D1.1`); wiki uses lowercase-kebab-with-hyphens (`aws-d1-1`). **Mitigation:** add `ledger_id` frontmatter key on each wiki page; `test_ledger_alignment` checks `frontmatter['ledger_id']` exists in ledger, NOT `code_id`. Same pattern as W3-A/W4-A.
- **Open: A2.4 routing.** AWS A2.4 (welding symbols) is a reference / symbology standard, not a code per se. Three options:
  1. **Promote to `wiki/standards/aws-a2-4.md`** (proposed default) — follows the engineering-standards CLAUDE.md schema and treats A2.4 as a publisher-issued standards document. Calc-callers can resolve a `Citation`. Recommended.
  2. **Re-route to `wiki/concepts/aws-welding-symbols.md`** — treats A2.4 as a concept page (symbology vocabulary). Loses calc-citation resolvability.
  3. **Both** — `wiki/standards/aws-a2-4.md` for citation + `wiki/concepts/aws-welding-symbols.md` for vocabulary. Doubles work; defer the concepts page to a future pass.
  This plan proposes **Option 1** (recommended). Reviewer MUST confirm.
- **Open: filler-metal-overview promotion.** Should the OPTIONAL `aws-filler-metal-overview.md` be created in `wiki/standards/` (as a series-overview page rather than a single code), routed to `wiki/concepts/aws-filler-metal-classification.md` instead, or DROPPED entirely? This plan proposes the OPTIONAL slot in `wiki/standards/` with a `revision: public-metadata-required-before-citation-use` placeholder, but the placement is debatable per the W4-A MINOR-3 precedent (a publisher-level pointer in `wiki/standards/` violates the schema). **Plan default:** approved — keep it in `wiki/standards/`. **Reviewer MAY drop or re-route**, dropping the page count to 5.
- **Open: D1.1 multi-edition split.** Should `aws-d1-1.md` be ONE umbrella page (current proposal, `revision: "2010"`) or 4 per-edition pages (`-2006`/`-2008`/`-2009`/`-2010`)? Current proposal: ONE umbrella. Reviewer MAY require split per the W3-A per-Part precedent.
- **Open: A5.5 cover-page verification timing.** The implementer MUST read the A5.5 PDF cover page to verify the edition before committing. Should this be (a) implementer's responsibility at implementation time (current proposal), or (b) a separate pre-implementation spike? Plan default: (a). Reviewer MAY require (b) if the corpus is suspected to be ambiguous.

---

## Complexity: T2

**T2** — multi-file documentation work (5 or 6 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 9 or 10 files), no new code modules, but a real test contract (≥17 parametrized assertions × 5-6 pages = ~85-100 effective test cases). Implementation is templated repetition. Design risk is concentrated in (a) the NEW `cross_references` frontmatter convention and its dangling-link tolerance, (b) the multi-edition umbrella discipline for D1.1 (widest edition gap in the W-series at 15 years), (c) the A2.4 standards-vs-concepts routing decision, (d) the A5.5 cover-page-edition verification dependency, (e) the on-disk-edition vs. publisher-current-edition gap discipline (NEW H2 section requirement). Larger surface than W4-A (3 pages) but smaller than W1-A (10 pages); firmly T2 territory because of the new convention introductions (cross_references, edition-gap section).
