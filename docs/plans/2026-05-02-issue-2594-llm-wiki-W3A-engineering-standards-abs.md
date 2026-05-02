# Plan for LLM-Wiki Completeness W3-A: Bounded ABS Code Body Summary Promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** _not yet filed — this plan is the deliverable; issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md`_
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Sibling precedent (W1-A, API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN) — the bounded-promotion pattern this plan inherits. **INHERITANCE BLOCKER (flagged here, not silently inherited):** the W1-A plan header still reads `Path sanction: #2471 — wiki/standards/<code-id>.md routing` and the W1-A test list cites `#2471` as the source of `code_id` (lines 9 and 225 in `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md`). Per memory `project_wiki_standards_path_decision.md`, [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) is **CSA-Z276-only** (verified 2026-04-25 from the issue body — see Evidence). The W1-A over-cite is preserved here as a defect to flag in W3-A's adversarial review and to track via a follow-up correction issue against W1-A; this W3-A plan does NOT inherit the over-cite.
> **Sibling precedent (W2-A, DNV):** [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (OPEN) — the **revised** W2-A plan adopts the corrected #2471 framing (local sanction = `engineering-standards/CLAUDE.md` directory schema; #2471 cited only as historical origin of the frontmatter triple). This W3-A plan adopts the W2-A revised framing verbatim.
> **Sibling precedent (OCIMF Tandem):** [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) (CLOSED) — bounded preview test pattern (`tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py`) which both W1-A and this plan extend.
> **Path sanction (ABS):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). In-progress organizational precedent: W2-A plan [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (DNV, revised). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision **for CSA-Z276 specifically** (verified per memory `project_wiki_standards_path_decision.md` and from the issue body itself); it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple, not as ABS path authority.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`)
> **Calc-citation pilot (epic-level):** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors prose-level pilot (this plan does NOT extend the pilot to ABS code; that is a downstream consumer concern)
> **Review artifact:** `scripts/review/results/2026-05-02-plan-W3A-claude-internal.md` (single-author Claude r1, to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini UNAVAILABLE per memory (codex-cli 0.124.0 stdin-hang #2479; Gemini sandbox cwd=/tmp). Single-author acceptable per same memory.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). Downstream consumer that will resolve the wiki pages this plan creates.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/registry.py` — companion resolver. Single live `Citation(...)` constructor on disk lives at line 52.
- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — prose-level pilot reference for DNV-OS-E301 (NOT an ABS code). No live ABS `Citation(...)` exists today; ABS pages will satisfy *future* citation wiring as `Citation(code_id="abs-...", publisher="ABS", ...)`.
- Internal-reference frequency: ABS appears in `digitalmodel/src/` only as **prose comments and config-key strings** (`"ABS Steel Vessel"`, `"ABS GN Offshore"`, `"ABS SVR"`), NOT as structured citation calls. Total of 17 unique short-string references across the source tree. ABS is therefore a **lower-frequency consumer** than DNV (~530 hits) or API (~285 hits) — bias toward `INDEX.md`-listed publisher coverage rather than grep-frequency.
- Gap: zero summary-promotion artifact exists for the `/mnt/ace/O&G-Standards/ABS/` corpus in any wiki domain (verified: `ls knowledge/wikis/*/wiki/standards/` reports no `abs-*.md` file in any wiki). Unlike the DNV W2-A 5x cross-wiki collision, there are **no pre-existing ABS pages** to reconcile.

### Standards

The 8-10 priority ABS documents biased toward floating production, offshore standards, subsea, materials/welding, and survey:

| Standard | Status | Source |
|---|---|---|
| ABS Rules for Building and Classing Offshore Installations (Part 1, Offshore) | gap (raw 2014 edition present; current at eagle.org) | `data/document-index/standards-transfer-ledger.yaml` (no row yet); `/mnt/ace/O&G-Standards/ABS/Rules/ABS-Rules-Part1-Offshore-2014.pdf` |
| ABS Rules for Conditions of Classification — Part 1 (Offshore) | gap | `/mnt/ace/O&G-Standards/ABS/Rules/ABS-Rules-Conditions-Classification-Part1-Offshore-2014.pdf` |
| ABS Rules for Building and Classing Steel Vessels (Part 3, hull) | gap | `/mnt/ace/O&G-Standards/ABS/Rules/ABS-Rules-Steel-Vessels-Part3-2016.pdf` |
| ABS GUI-002 Guide for Building and Classing Floating Production Storage Systems (FPSO) | partial — ledger row `id: ABS-GUI-002` exists, no wiki page | ledger; `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-002-Guide-for-Building-and-Classing-FPSO-1994.pdf` |
| ABS GUI-101 FPSO Dynamic Loading Approach (DLA) Guide | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-101-FPSO-Dynamic-Loading-Approach-Guide.pdf` |
| ABS GUI-115 Guide for Fatigue Assessment of Offshore Structures (2014) | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-115-Fatigue-Assessment-Offshore-Structures-2014.pdf` |
| ABS GUI-104 Offshore Spectral Fatigue Analysis Guide | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-104-Offshore-Spectral-Fatigue-Analysis-Guide.pdf` |
| ABS GUI-123 Guide for Offshore Risers (2008) | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-123-Guide-for-Offshore-Risers-2008.pdf` |
| ABS GN-239 Guidance Notes on Cathodic Protection of Offshore Structures (2018) | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GN-Cathodic-Protection-Offshore-Structures-2018.pdf` |
| ABS GUI-057 Guide for Drilling Systems (2014) | gap | `/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-057-Guide-for-Drilling-Systems-2014.pdf` |

This is **10** entries — all have a verifiable raw source under `/mnt/ace/O&G-Standards/ABS/`. **MODU Rules (Mobile Offshore Drilling Units), FPI Guide, MOU/BOI** are recognized canonical ABS offshore documents but are NOT among the 29 raw PDFs on disk; deferred to a W3-B follow-up using publisher-portal pointers. See Risks for the corpus-vs-recognized-canon mismatch.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards code page (1 file in `wiki/standards/`); metadata-stub frontmatter style this plan replicates ten times. Confirms the lowercase-kebab `code_id` convention (`code_id: api-17e`).
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`. Per W2-A precedent, the count math: 5 sources + 1 existing standards page (`api-17e`) + 10 new ABS pages = **16**. **However**, if W1-A and W2-A land before W3-A, this count must be re-derived at implementation time — e.g., 5 sources + 1 existing api-17e + 10 W1-A + 10 W2-A + 10 W3-A = 36. The plan AC pins `page_count` arithmetic to "current state at implementation time + 10 ABS pages", not a fixed value — see AC.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply. Schema example values use lowercase-kebab (`csa-z276`, `api-17j`, `ocimf-meg4`). **This is the path-sanction authority** for engineering-standards domain (NOT #2471).
- `knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md` — Elements ingest catalog already references the broader DORIS standards corpus; the ABS subset of `/mnt/ace/O&G-Standards/ABS/` (29 PDFs) is a complementary path through the same corpus.
- No pre-existing ABS pages exist in `engineering/wiki/standards/` (cross-checked via `ls`); contrast with W2-A's 5x DNV collision.

### Documents consulted

- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — direct precedent. **Inherited contracts:** bounded-preview frontmatter, no-raw-text test, citation-resolvability test, lowercase-kebab `code_id`. **Inheritance defect flagged (NOT propagated):** W1-A header line 9 cites `#2471` as path-sanction; W1-A line 225 cites `#2471` as `code_id` source. Both are over-cites per memory; this plan adopts W2-A's revised framing instead.
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — **revised** W2-A plan. Adopts corrected #2471 framing (local CLAUDE.md schema as path-sanction; #2471 as historical origin only). This W3-A plan inherits W2-A's revised framing verbatim, including the cross-wiki uniqueness AC, the publisher-history optional field, the strict `<500` word-count, and the ledger-alignment test.
- `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — bounded preview pattern (#2227 closure).
- `data/document-index/standards-transfer-ledger.yaml` — contains 2 ABS rows: `ABS-GUI-00` (Thrusters/DP, 1994) and `ABS-GUI-002` (FPSO building/classing, 1994). The other 8 priority ABS documents introduced by this plan require new ledger rows.
- `/mnt/ace/O&G-Standards/ABS/INDEX.md` — internal corpus catalog; identifies document numbers (GUI-115, GN-239, etc.), edition years, and source provenance ("eagle.org downloaded 2026-02-20" for the cathodic-protection items, "Migrated from raw archive" for the rest). This INDEX.md is the canonical mapping from ABS document-number to raw filename for this plan.
- `.claude/rules/calc-citation-contract.md` — the citation contract this plan exists to satisfy.
- `.claude/rules/coding-style.md` and `.claude/rules/patterns.md` — universal rules; no specific ABS implication, but the test file lives at the workspace-hub repo root (not inside `digitalmodel/`) so universal coding-style rules apply.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). The path-routing principle generalizes only to {marine-engineering, engineering, naval-architecture}; for engineering-standards wiki, cite the LOCAL `engineering-standards/CLAUDE.md` directory schema. This memory is the load-bearing input that distinguishes W3-A's framing from W1-A's.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite below uses regex denylists; this plan keeps phrase lists narrowly scoped to ABS-specific copyright/cover-page strings. ABS publishes from Spring TX (HQ) and Houston, so the denylist will draw from those + "American Bureau of Shipping" / "© ABS" cover-page conventions.
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review acceptable when Codex/Gemini are unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex CLI 0.124.0 stdin-hang regression #2479; Codex review unavailable.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini cwd=/tmp blocks workspace-hub overlay reads; Gemini review unavailable.
- `feedback_never_offer_to_self_label_plan_approved.md` — issue filing is downstream of plan-review approval; this plan is `status: draft` and does NOT pre-authorize a downstream issue.

### Gaps identified

- No engineering-standards wiki pages exist for any ABS code (zero; contrast W2-A's 5x DNV collision).
- The standards-transfer-ledger contains rows for only 2 of the 10 priority ABS documents (`ABS-GUI-00`, `ABS-GUI-002`). Eight new ledger rows required for traceability per the W1-A/W2-A precedent.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any ABS page.
- ABS uses `Pt.X / Sec.Y / §Z` clause-numbering inside its Rules books (multi-part rule sets, not single documents) — the existing `code_id` schema is single-document-per-code and does not natively express "Part 3 of Steel Vessels Rules". See Risks.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — body explicitly states "Decide and codify the sanctioned durable-wiki routing/schema **for CSA Z276 pages**" (CSA-only, verifying the memory)
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"
- `#2590` — OPEN — "feat(llm-wiki): bounded DNV standards summary promotion to engineering-standards wiki (W2-A)"
- `#2227` — CLOSED — "feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis"
- `#2482` — CLOSED — vendor-derivative deny-list governance
- `#2481` — CLOSED — calc-citation contract pilot

**File existence** (`ls` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/ABS/` — 3 subdirs (`Guidance-Notes/`, `Notices/`, `Rules/`) + `INDEX.md`. Contents fully enumerated above.
- EXISTS: `/mnt/ace/O&G-Standards/ABS/INDEX.md` — internal corpus catalog (sourced from eagle.org and "Relocated from BSI/ (mis-filed)")
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing engineering-standards code page — 1 file in `wiki/standards/`)
- EXISTS: `knowledge/wikis/engineering-standards/CLAUDE.md` (path-sanction authority; schema excerpt below)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-offshore-installations.md`, `abs-rules-coc-part1-offshore.md`, `abs-rules-steel-vessels-part3.md`, `abs-gui-002-fpso.md`, `abs-gui-101-fpso-dla.md`, `abs-gui-115-fatigue-offshore.md`, `abs-gui-104-spectral-fatigue.md`, `abs-gui-123-offshore-risers.md`, `abs-gn-239-cathodic-protection-offshore.md`, `abs-gui-057-drilling-systems.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_abs.py`
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (the resolver target)
- EXISTS: `digitalmodel/src/digitalmodel/citations/registry.py` (the live `Citation(...)` constructor at line 52)

**ABS PDF count** (`find /mnt/ace/O&G-Standards/ABS -maxdepth 4 -type f -iname "*.pdf" | wc -l` 2026-05-02):
```
29
```
Distribution: 17 in `Guidance-Notes/`, 5 in `Notices/`, 7 in `Rules/`. The 10 priority documents are drawn entirely from `Guidance-Notes/` (7) and `Rules/` (3); `Notices/` content is corrigenda/notices and is excluded from W3-A.

**Sample ABS PDFs on disk** (`find /mnt/ace/O&G-Standards/ABS -maxdepth 4 -type f -iname "*.pdf" | head -10` 2026-05-02):
```
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GN-Cathodic-Protection-Offshore-Structures-2018.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GN-Cathodic-Protection-Ships-2017.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GN-Drilling-Riser-Analysis-2014.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GN-Drilling-Riser-Analysis-2017.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-000-Guide-for-Thrusters-and-Dynamic-Positioning-Systems-1994.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-002-Guide-for-Building-and-Classing-FPSO-1994.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-057-Guide-for-Drilling-Systems-2014.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-101-FPSO-Dynamic-Loading-Approach-Guide.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-104-Offshore-Spectral-Fatigue-Analysis-Guide.pdf
/mnt/ace/O&G-Standards/ABS/Guidance-Notes/ABS-GUI-115-Fatigue-Assessment-Commentary.pdf
```

**Internal-reference proof — ABS in digitalmodel** (`grep -rohE "ABS[ _-]?(GUI|GN|MODU|FPI|FPSO|MPS|FAS|LRFD|SVR|MOU|BOI|Rules|Notice|Steel|Ship|Drilling|Riser|Cathodic|Fatigue)[ _-]?[A-Za-z0-9_-]*" digitalmodel/src/ | sort | uniq -c | sort -rn`):
```
      6 ABS Steel Vessel
      6 ABS GN Offshore
      1 ABS-SVR
      1 ABS SVR
      1 ABS Steel
      1 ABS Rules for
      1 ABS Rules call
      1 ABS GN Ships
```
Total of 17 short-string references across `digitalmodel/src/`. Most are config keys / prose comments, NOT structured `Citation(...)` calls — confirming ABS is a low-frequency citation consumer today and grep-frequency is NOT the priority-selection criterion for W3-A. Priority instead derives from `INDEX.md` corpus coverage (offshore-installation rule sets + FPSO/fatigue/riser/cathodic-protection guidance — ABS's well-known offshore-engineering publication set).

**ABS ledger rows present** (`grep -B0 -A4 "^- id: ABS" data/document-index/standards-transfer-ledger.yaml`):
```
- id: ABS-GUI-00
  title: ABS_GUI_00_(1994)_Guide_for_Thrusters_and_Dynamic_Positioning_Systems
  org: ABS
  domain: marine
- id: ABS-GUI-002
  title: ABS_GUI_002_(1994)_Guide_for_Building_and_Classing_Floating_Production_Storage_Systems
  org: ABS
  domain: marine
```
Only 2 ABS rows currently. Plan adds 8.

**Engineering-standards CLAUDE.md path-sanction excerpt** (the load-bearing line that replaces the W1-A "#2471 path sanction" claim):
```
wiki/
  standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)
```
Plus the Standards page extra-fields table:
```
| `code_id` | required (L0 prose) | Canonical code identifier, e.g. `csa-z276`, `api-17j`, `ocimf-meg4` |
| `publisher` | required (L0 prose) | Publishing body, e.g. `CSA Group`, `API`, `OCIMF` |
| `revision` | required (L0 prose) | Revision/edition/year, e.g. `2023`, `4e` |
```

**Issue #2471 body excerpt** (verifies CSA-Z276-only scope, NOT generalized standards-path sanction):
```
Decide and codify the sanctioned durable-wiki routing/schema for CSA Z276 pages
before CSA coverage is promoted from ACMA/standards metadata into LLM-wiki content.
```

**Public-revision evidence (web)**:
- ABS publisher portal: <https://www.eagle.org/> — free anonymous browse; downloads gated by registration. Per `INDEX.md`, two of the priority documents (cathodic-protection 2017/2018) were "downloaded 2026-02-20 from eagle.org".
- ABS Rules and Guides catalog: <https://ww2.eagle.org/en/rules-and-resources/rules-and-guides.html> — canonical revision dates per code published here.
- Recognized canonical ABS offshore set (per ABS public catalog): MODU Rules (Mobile Offshore Drilling Units), FPI Guide (Floating Production Installations), Building & Classing Offshore Installations, MOU (Mobile Offshore Units), Subsea Production Systems Guide, SVR (Survey After Construction). Of these, only **Building & Classing Offshore Installations** (`Rules/ABS-Rules-Part1-Offshore-2014.pdf`) and **SVR** (covered by `Rules/ABS-Rules-Dry-Dock-2014.pdf` + `Rules/ABS-Rules-Conditions-Classification-Part1-Offshore-2014.pdf`) have raw PDFs on disk; MODU Rules / FPI Guide / Subsea Production / MOU are NOT in the 29-PDF corpus.

<!-- Distinct sources counted: existing repo code (1), standards ledger (2), engineering-standards CLAUDE.md schema (3), W1-A precedent plan (4), W2-A revised precedent plan (5), OCIMF precedent (6), `/mnt/ace/.../ABS/INDEX.md` (7), citation rule (8), project memory (9), web (10). 10 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-offshore-installations.md` (Rules — Part 1, Offshore — Building & Classing) |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-coc-part1-offshore.md` (Conditions of Classification — Part 1, Offshore) |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-steel-vessels-part3.md` (Steel Vessels — Part 3, hull) |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-002-fpso.md` (FPSO Building & Classing Guide, 1994) |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-101-fpso-dla.md` (FPSO Dynamic Loading Approach Guide) |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-115-fatigue-offshore.md` (Fatigue Assessment of Offshore Structures, 2014) |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-104-spectral-fatigue.md` (Offshore Spectral Fatigue Analysis Guide) |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-123-offshore-risers.md` (Offshore Risers Guide, 2008) |
| Wiki page (9) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gn-239-cathodic-protection-offshore.md` (Cathodic Protection of Offshore Structures, 2018) |
| Wiki page (10) | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-057-drilling-systems.md` (Guide for Drilling Systems, 2014) |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 8 new rows; 2 already exist for `ABS-GUI-00` and `ABS-GUI-002`) |
| Test contract | `tests/knowledge/test_engineering_standards_abs.py` |
| Plan review — Claude (r1, single-author) | `scripts/review/results/2026-05-02-plan-W3A-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |

---

## Deliverable

Ten new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority ABS code), each carrying calc-citation-contract-compliant frontmatter (`code_id`, `publisher`, `revision`, plus `extraction_policy: metadata-only`, `raw_copy_allowed: false`) and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/ABS/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream calc modules CAN resolve `Citation` instances for the ten ABS offshore-engineering canonical documents (FPSO building/DLA, fatigue assessment, offshore risers, cathodic protection, drilling systems, plus the three foundational rule books) without any verbatim source text entering git.

---

## Pseudocode

The work is templated 10x repetition. Each new wiki page will follow the same skeleton (identical to W2-A modulo `publisher: ABS` and ABS-specific `revision` strings):

```
---
title: "<Full ABS document name> — bounded summary"
tags: ["abs", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: abs-<doc-number-or-slug>      # lowercase-kebab; matches engineering-standards CLAUDE.md, api-17e, W1-A, W2-A
publisher: ABS                          # canonical short name; full form "American Bureau of Shipping" tracked in publisher_full
publisher_full: "American Bureau of Shipping"
revision: "<YYYY>"                      # ABS revision convention is year-based (e.g., "2014", "2018")
revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"
verified_on: 2026-05-02
public_url: <eagle.org canonical URL when known>
sources:
  - <one or more /mnt/ace/... paths — pointer only, never quoted>
extraction_policy: metadata-only
raw_copy_allowed: false
abs_doc_number: <"GUI-115" | "GN-239" | "Rules Part 1 Offshore" | ...>
abs_part_section: <"Part 3" | "Pt. 3 / Sec. 4" | null>     # for multi-part rule books only; see Risks
---

# <Full ABS document name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.

## Where to find the full text
- Raw PDF: <absolute /mnt/ace/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: <eagle.org URL> (anonymous browse; download requires registration)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code, or "no live caller; future-needed">

## Cross-references
- [[abs-gui-115-fatigue-offshore]] (when applicable for fatigue cross-cite)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file will use a parametrized fixture iterating over the 10 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-offshore-installations.md` | Bounded summary for ABS Rules Part 1 (Offshore) — Building & Classing Offshore Installations. Foundational rule book covering MODU/FPI scope adjacent to internal `digitalmodel` `"ABS GN Offshore"` references (6 hits). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-coc-part1-offshore.md` | Bounded summary for ABS Rules — Conditions of Classification, Part 1 Offshore (2014). Companion to the offshore-installations rule book; gates classification status. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-rules-steel-vessels-part3.md` | Bounded summary for ABS Rules — Steel Vessels Part 3 (2016). Hull construction; cited 6 times in `digitalmodel/src/` as `"ABS Steel Vessel"`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-002-fpso.md` | Bounded summary for ABS GUI-002 (1994) — Building & Classing FPSO. Companion to GUI-101 DLA. Existing ledger row `ABS-GUI-002`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-101-fpso-dla.md` | Bounded summary for ABS GUI-101 — FPSO Dynamic Loading Approach Guide. Highest-relevance ABS document for `digitalmodel/marine_ops/marine_engineering/`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-115-fatigue-offshore.md` | Bounded summary for ABS GUI-115 (2014) — Fatigue Assessment of Offshore Structures. Most-revised document in the ABS corpus on disk (2003/2010/2014 + Commentary). Frontmatter pins to **2014**; Commentary and prior editions noted in `supersedes` and prose only. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-104-spectral-fatigue.md` | Bounded summary for ABS GUI-104 — Offshore Spectral Fatigue Analysis Guide. Methodology adjunct to GUI-115. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-123-offshore-risers.md` | Bounded summary for ABS GUI-123 (2008) — Offshore Risers. Riser-design guidance complementary to API STD 2RD / DNV-OS-F201. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gn-239-cathodic-protection-offshore.md` | Bounded summary for ABS GN-239 (2018) — Cathodic Protection of Offshore Structures. Cited 6 times in `digitalmodel/src/` as `"ABS GN Offshore"`. eagle.org-sourced (per `INDEX.md`). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/abs-gui-057-drilling-systems.md` | Bounded summary for ABS GUI-057 (2014) — Guide for Drilling Systems. Drilling-rig classification reference. |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" section + 10 new rows; bump `page_count` per the **arithmetic AC** (current count + 10), not a fixed value (W1-A and W2-A may have already bumped the count by the time W3-A lands) |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 8 new ABS rows (existing 2: `ABS-GUI-00`, `ABS-GUI-002`). New IDs: `ABS-RULES-PT1-OFFSHORE-2014`, `ABS-RULES-COC-PT1-OFFSHORE-2014`, `ABS-RULES-STEEL-VESSELS-PT3-2016`, `ABS-GUI-101`, `ABS-GUI-115-2014`, `ABS-GUI-104`, `ABS-GUI-123-2008`, `ABS-GN-239-2018`, `ABS-GUI-057-2014`. (Note: 9 IDs — `ABS-GUI-002` already exists.) |
| Create | `tests/knowledge/test_engineering_standards_abs.py` | Test contract: frontmatter, no-raw-text, citation resolvability, ledger alignment, code_id uniqueness across wikis (per W2-A AC inheritance) |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_abs.py`. Each test parametrized over the 10 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 10 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, **lowercase-kebab** (matches engineering-standards CLAUDE.md schema, `api-17e.md`, W1-A, W2-A); filename stem equals `code_id` verbatim (e.g., `abs-gui-115-fatigue-offshore.md` ↔ `abs-gui-115-fatigue-offshore`) |
| `test_frontmatter_has_publisher_abs` | publisher discipline | YAML frontmatter | `publisher == "ABS"`; if present, `publisher_full == "American Bureau of Shipping"` |
| `test_frontmatter_has_revision` | revision presence per calc-citation-contract rule 2 | YAML frontmatter | `revision` non-empty string; matches ABS regex `^(\d{4}\|public-metadata-required-before-citation-use)$` (year-based; ABS does not use month suffixes like DNV) |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_has_abs_doc_number` | ABS-specific traceability | YAML frontmatter | `abs_doc_number` non-empty (e.g. `"GUI-115"`, `"GN-239"`, `"Rules Part 1 Offshore"`) |
| `test_part_section_only_on_multipart_rules` | multi-part rule-book bridge | YAML frontmatter | only the three `abs-rules-*.md` pages carry `abs_part_section`; the seven Guide / GN pages do NOT (Guide pages are single-document, Part-numbering is a Rules-only artifact) |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow ABS-specific phrase set; see Risks) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict `<500` word ceiling matching W1-A and W2-A (per W2-A P3-4 fix) | page body | `0 < word_count < 500` strict on both bounds; word-count constant imported from W1-A's test file (`tests/knowledge/test_engineering_standards_api_pages.py`) at implementation time, NOT redefined |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only the four allowed sections | page body | top-level `##` headings exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` |
| `test_links_only_pointer_to_mnt_ace` | the page mentions the raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/ABS/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolver — actually reads the wiki page (per W2-A P2-5 fix) | invoke the resolver function (`_read_frontmatter` from `digitalmodel/src/digitalmodel/citations/schema.py` or registry-level resolution) for each new page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised; constructor-only validation alone is hollow and is replaced by file-reading assertion |
| `test_ledger_alignment` | every page's `code_id` resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `code_id` | matching `id:` row found in ledger YAML (case-insensitive comparison since ledger uses `ABS-GUI-115-2014` uppercase; wiki uses `abs-gui-115-fatigue-offshore` lowercase-kebab — see Risks for mapping) |
| `test_code_id_unique_across_wiki_domains` | inherited from W2-A AC | every `code_id` in `knowledge/wikis/*/wiki/standards/*.md` | no duplicates; if a duplicate exists, the engineering-standards page MUST carry `extraction_policy: metadata-only` and the legacy-domain peer MUST carry a `cross_links` pointer back |
| `test_index_lists_all_ten` | wiki index updated | `index.md` contents | each of the 10 page links present in the "## Standards" section |

`RAW_TELLTALE_PHRASES` will be a small, narrowly-scoped list (≤15 entries) drawn from ABS publication front-matter conventions — e.g. "American Bureau of Shipping", "ABS Plaza", "1701 City Plaza Drive, Spring TX", "Houston, Texas, USA", "© American Bureau of Shipping", "All rights reserved", "Reproduction, copy or transmission of this publication", "ABS Rules and Guides are reviewed", "eagle.org" (cover-page link only — the page may legitimately reference eagle.org URLs, so this entry is contextual). The list will deliberately exclude ABS document numbers (GUI-115, GN-239 — required) and the document title (allowed paraphrase). The ABS-specific list will NOT overlap with the OCIMF, API, or DNV denylists. **Honesty caveat (inherited from W2-A P2-3 risk):** the denylist alone will NOT catch a 100-200-word verbatim clause copy; reviewers MUST manually inspect every revision. Shingle-match / cosine-similarity follow-up deferred to W3-B.

---

## Acceptance Criteria

- [ ] All ten new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_abs.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/abs-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated; `code_id` lowercase-kebab; filename stem equals `code_id` verbatim).
- [ ] Citation downstream-resolution check (single canonical revision string per page; the page's frontmatter `revision` and the `Citation(...)` argument MUST match verbatim, since `validate_citation` does literal-equality on the revision string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - For each page where a real publisher revision is asserted in frontmatter, `python -c "from digitalmodel.citations.schema import Citation; Citation(code_id='<id>', publisher='ABS', revision='<frontmatter-revision-verbatim>', section='<placeholder>', wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md')"` succeeds without error. Concrete example: `abs-gui-115-fatigue-offshore.md` will use `revision: "2014"` in BOTH frontmatter AND the `Citation(...)` call.
  - Pages whose revision cannot be pinned to a verifiable publisher edition at write-time MUST set `revision: "public-metadata-required-before-citation-use"` in frontmatter AND be excluded from this resolution check (`pytest.mark.skip(reason="stub-only, revision pending")`). The `abs-gui-002-fpso.md` (1994 — pre-internet edition; revision date confirmed via `INDEX.md`) IS pinned to `revision: "1994"`; the `abs-rules-coc-part1-offshore.md` and `abs-rules-offshore-installations.md` are pinned to `"2014"`.
- [ ] Ledger alignment: every page's `code_id` resolves to a row in `data/document-index/standards-transfer-ledger.yaml` (8 new rows added by this plan; 2 already exist as `ABS-GUI-00` / `ABS-GUI-002`). The ID-form mapping rule: ledger uses uppercase-with-hyphens (`ABS-GUI-115-2014`), wiki uses lowercase-kebab title-form (`abs-gui-115-fatigue-offshore`). The test resolves via a per-page `ledger_id` frontmatter key on each wiki page, asserted to exist as a row `id:` in the ledger.
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 10 new pages under a "## Standards" section. **Arithmetic AC:** `page_count` after this plan = (current `page_count` at implementation time) + 10. The test reads the prior value from git history (parent commit) and asserts the new value equals `prior + 10`.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan.
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified — verified there are NO pre-existing ABS pages in `engineering/wiki/standards/` (cross-checked by `ls`); contrast W2-A's 5x DNV collision. If a future contributor creates an `engineering/wiki/standards/abs-*.md` page before W3-A lands, this plan MUST be re-scoped before merge.
- [ ] **`code_id` uniqueness across wiki domains:** the test suite asserts no `code_id` value is duplicated across `knowledge/wikis/*/wiki/standards/*.md`. (Inherited from W2-A AC; for ABS this is currently vacuous since no ABS pages exist elsewhere, but the assertion guards against future drift.)
- [ ] Plan review artifact present at `scripts/review/results/2026-05-02-plan-W3A-claude-internal.md` (single-author Claude review acceptable per memory `feedback_permission_gate_blocks_cross_review.md` when Codex/Gemini are unavailable). Codex unavailable per `feedback_codex_cli_0_124_upstream_regression.md`; Gemini unavailable per `feedback_gemini_sandbox_overlay_blindness.md`. If Codex 0.123.0 downgrade lands before implementation begins, a v2 review SHOULD be dispatched and added as a non-blocking artifact.
- [ ] Adversarial review explicitly addresses the W1-A inheritance-blocker (the W1-A plan still over-cites `#2471` as path-sanction at lines 9 and 225); reviewer either confirms W3-A's revised framing OR flags additional W1-A drift for a follow-up correction issue.

---

## Adversarial Review Summary

<!-- To be populated during plan-review per `.claude/skills/coordination/issue-planning-mode/SKILL.md`. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | _pending_ | _to be produced by main session_ |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini CLI cwd=/tmp sandbox cannot resolve repo paths |

**Overall result:** _pending r1 single-author review_

---

## Risks and Open Questions

- **Risk:** Copyright leakage. ABS publishes from Spring TX HQ (1701 City Plaza Drive) and Houston, with cover-page strings "American Bureau of Shipping" and "© ABS". If a future contributor pastes scope text from the PDF, the denylist may miss novel phrases. **Mitigation (inherited from W1-A/W2-A):** word-count ceiling `<500` (strict, matches W1-A) + positive-shape structural test + `extraction_policy: metadata-only` frontmatter + `raw_copy_allowed: false` + cross-review on every revision touching `wiki/standards/abs-*.md`. Reviewers should specifically watch for "American Bureau of Shipping" and "© ABS" cover-page phrases as the highest-leak-risk strings. **Honesty caveat:** denylist alone is necessary-but-not-sufficient; manual inspection required.
- **Risk (NEW for ABS — multi-part rule-book numbering mismatch):** ABS uses `Pt.X / Sec.Y / §Z` clause-numbering inside its Rules books (e.g., "Steel Vessels Rules Part 3, Chapter 2, Section 4"). The `Citation` schema is single-document-per-`code_id` and does not natively express "Part 3 of Steel Vessels Rules". **Mitigation:** introduce a frontmatter `abs_part_section` field on the three `abs-rules-*.md` pages (covers Part 1 Offshore, Part 1 Conditions of Classification, Part 3 Steel Vessels). The field is null on the seven Guide / GN pages. Calc citations using ABS rule books MUST set `Citation.section` to a string like `"Pt.3 Ch.2 Sec.4"`; this is a `Citation.section`-string convention, NOT a schema change. Tracked here for W3-A; if calc-callers ever need richer rule-book navigation (e.g. `Citation` with `part`, `chapter`, `section` as separate fields), file a follow-up against `digitalmodel/src/digitalmodel/citations/schema.py`.
- **Risk:** Corpus-vs-recognized-canon mismatch. The 29 PDFs on disk under `/mnt/ace/O&G-Standards/ABS/` cover 17 Guidance Notes / 5 Notices / 7 Rules — but DO NOT include several recognized-canonical ABS offshore documents (MODU Rules, FPI Guide, Subsea Production Systems Guide, MOU). The W3-A scope is **bounded to documents on disk**, NOT the recognized canon. **Mitigation:** the priority 10 are explicitly drawn from the 29-document on-disk corpus. MODU/FPI/Subsea/MOU are deferred to a W3-B follow-up that uses publisher-portal pointers from eagle.org without a `/mnt/ace` source. The plan does NOT silently substitute a recognized-canonical name onto a different on-disk PDF. Disambiguation rule: every priority page's `sources` frontmatter MUST list at least one verifiable `/mnt/ace/...` path, asserted by `test_links_only_pointer_to_mnt_ace`.
- **Risk (NEW for ABS — multi-edition revision selection):** GUI-115 has FOUR editions on disk (2003, 2010, 2014) plus a Commentary. Choosing the "current" revision is ambiguous without eagle.org verification. **Mitigation:** W3-A frontmatter pins to **2014** (the latest on-disk edition); `supersedes: ["GUI-115-2003", "GUI-115-2010"]` documents the lineage; the Commentary is referenced in prose only (NOT promoted as a separate page — Commentaries are not standards). Contributor verifying against eagle.org may bump to a newer edition during implementation; the test suite asserts `revision` is non-empty and matches the year regex, NOT a specific year.
- **Risk:** Cross-wiki duplication — INVERSE of W2-A. Where W2-A faced 5x pre-existing engineering-domain DNV pages, W3-A faces ZERO pre-existing ABS pages anywhere (`ls knowledge/wikis/*/wiki/standards/abs-*` returns no matches). The 5x-collision risk does NOT apply to W3-A. **Mitigation:** AC explicitly asserts "no `engineering/wiki/standards/abs-*.md` exists at implementation time" — re-scope the plan if a future contributor preempts this by creating one; the `test_code_id_unique_across_wiki_domains` test guards against silent drift.
- **Risk:** Publisher-history drift. ABS has been continuously named "American Bureau of Shipping" since 1862 — NO rebranding history (contrast DNV's 2013–2021 "DNV GL" interregnum). The optional `publisher_history` field from W2-A is therefore not needed for any ABS page. Confirmed.
- **Risk (inherited from W2-A P2-2):** Hidden assumption — `digitalmodel` grep-frequency would normally be the priority-selection criterion, but for ABS the grep yields only 17 short-string hits with no structured citations (`"ABS Steel Vessel"`, `"ABS GN Offshore"`). Priority for W3-A is therefore based on **`INDEX.md` corpus coverage + ABS's recognized offshore-engineering canon** (FPSO building/DLA, fatigue, risers, cathodic protection, drilling, plus the foundational rule books). If a sibling repo (`assethold`, `worldenergydata`, `acma-projects`) cites a different ABS distribution, the priority ranking is wrong. Cross-repo consumer audit follow-up was already filed under W2-A P2-2; that audit covers ABS too — no new follow-up needed.
- **Risk:** Ledger-form / wiki-form ID divergence. The ledger uses uppercase-with-hyphens (`ABS-GUI-115-2014`); the wiki filename uses lowercase-kebab title-form (`abs-gui-115-fatigue-offshore`). A naive `code_id == ledger_id` test would fail. **Mitigation:** add a `ledger_id` frontmatter key on each wiki page that names the corresponding ledger row; `test_ledger_alignment` checks `frontmatter['ledger_id']` exists in the ledger, NOT `code_id`. This is a documentation pattern the W2-A plan implicitly handled via case-insensitive comparison; W3-A makes the bridge explicit.
- **Risk:** Corrigenda/Notices documents. The `Notices/` subdir contains 5 PDFs that are corrigenda + amendment notices to the 2014 Rules. These are NOT promoted as standalone wiki pages (they amend documents already covered). **Mitigation:** the three `abs-rules-*.md` wiki pages MUST list the corresponding corrigendum/notice in their `sources` frontmatter (as additional `/mnt/ace` paths), and the test asserts `sources` length `>= 1`. The corrigenda are a `sources` enumeration, NOT a separate `code_id`.
- **Open:** **Which 10?** This plan proposes ten priority ABS documents biased by (a) `INDEX.md` corpus catalog coverage, (b) ABS's recognized offshore-engineering canon, (c) verifiable raw source under `/mnt/ace/O&G-Standards/ABS/`:
  1. ABS Rules — Building & Classing Offshore Installations, Part 1 (2014) — foundational rule book
  2. ABS Rules — Conditions of Classification, Part 1 Offshore (2014) — companion classification gate
  3. ABS Rules — Steel Vessels, Part 3 (2016) — hull construction; 6 internal hits
  4. ABS GUI-002 (1994) — FPSO Building & Classing Guide
  5. ABS GUI-101 — FPSO Dynamic Loading Approach Guide
  6. ABS GUI-115 (2014) — Fatigue Assessment of Offshore Structures
  7. ABS GUI-104 — Offshore Spectral Fatigue Analysis Guide
  8. ABS GUI-123 (2008) — Offshore Risers Guide
  9. ABS GN-239 (2018) — Cathodic Protection of Offshore Structures; 6 internal hits; eagle.org-sourced
  10. ABS GUI-057 (2014) — Guide for Drilling Systems

  **User confirmation required during plan-review.** Alternative substitutions to consider: GUI-116 (Novel Concepts, 2016) for GUI-057 (less code-cited); GUI-CDS (Cathodic Design of Ships, 2017) for one of the offshore-only entries; GUI-Drillships (2012) for GUI-057. The MODU Rules / FPI Guide / Subsea Production / MOU recognized-canonical set is explicitly NOT among the 10 (no raw on disk; deferred to W3-B).
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_abs.py` (one file, parametrized) or be split per-page? The single-file form is proposed for tractability and matches W2-A.
- **Open:** Issue title and labels. Proposed title: `feat(llm-wiki): bounded ABS standards summary promotion to engineering-standards wiki (W3-A)`. Proposed labels: `priority:medium,cat:documentation,domain:knowledge-management,domain:standards`. Issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md` and is NOT performed by this plan.

---

## Complexity: T2

**T2** — multi-file documentation work (10 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 14 files), no new code modules, but a real test contract (≥15 parametrized assertions × 10 pages = ~150 effective test cases). Implementation is templated repetition; design risk is concentrated in (a) ABS-specific multi-part rule-book numbering (`abs_part_section` frontmatter field is new for W3-A), (b) the multi-edition revision selection (GUI-115 has 3 on-disk editions), and (c) the corpus-vs-recognized-canon scope-down (MODU/FPI/Subsea/MOU deferred). Matches W1-A and W2-A T2 sizing.
