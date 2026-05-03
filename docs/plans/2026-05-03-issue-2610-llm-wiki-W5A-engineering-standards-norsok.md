# Plan for LLM-Wiki Completeness W5-A: Bounded NORSOK Norwegian-Sector Standards Summary Promotion

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** _not yet filed_ (issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md`; expected title and labels in Open Questions). **Filename `issue-2610` is provisional** — the actual GitHub issue number is reconciled at `gh issue create` time; if it differs, this filename and all internal cross-refs will be renamed at that point. Same convention as W4-A/W4-B.
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) (CLOSED) — overnight Elements corpus planning wave; this W5 packet is a continuation under the same bounded-summary contract.
> **Sibling precedent (W1-A, API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN) — original bounded-promotion pattern. NOTE: W1-A header originally over-cited `#2471` as path-sanction; the W3-C erratum [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN) tracks the forward-amendment. W5-A does NOT inherit that over-cite.
> **Sibling precedent (W1-B, asset management):** [#2587](https://github.com/vamseeachanta/workspace-hub/issues/2587) (OPEN) — flagged NORSOK Z-008 (risk-based maintenance) as a target. **W5-A delivers the on-disk member of that target list** but the on-disk corpus does NOT contain Z-008 itself; see Risks for the corpus-vs-W1B-target-list mismatch.
> **Sibling precedent (W2-A, DNV) and (W3-A, ABS):** [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (OPEN) and [#2594](https://github.com/vamseeachanta/workspace-hub/issues/2594) (OPEN) — adopt the corrected #2471 framing.
> **Sibling precedent (W3-C erratum):** [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN) — retro-fixed the #2471 sanction-scope defect across W1-A/W1-B/W2-C/W3-D and added the allowlist-polarity guardrail at `tests/governance/test_2471_citation_scope.py`. **Glob-scope caveat:** the guardrail's `PLANS_GLOB` is hard-pinned to `docs/plans/2026-05-02-*.md` and therefore does NOT scan this 2026-05-03 plan. As prose-only verification meanwhile: this plan deliberately keeps every `#2471` mention adjacent to a CSA-Z276 / historical-origin / `code_id` / `CLAUDE.md` / sanction-scope / Erratum allowlist token. A glob-extension follow-up is filed against #2596 and is NOT a W5-A blocker.
> **Sibling precedent (W4-A, NACE) and (W4-B, BSI):** [#2599](https://github.com/vamseeachanta/workspace-hub/issues/2599) (OPEN) and W4-B (issue not yet filed; plan at `docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md`) — most-recent revised same-shape precedents. W5-A inherits verbatim the post-erratum framing, the body-only no-raw-text scan rule, the deterministic-regex denylist rule, the `<500` strict word-count, the positive-shape structural test, and the `superseded_by` frontmatter pattern (introduced in W4-B for BS-EN-ISO adoptions; W5-A applies it to the ISO-supersession status of most NORSOK standards).
> **Path sanction (NORSOK):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for the engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). **Note:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) codified the path-routing decision for CSA-Z276 specifically (verified per memory `project_wiki_standards_path_decision.md`); it is NOT a general-standards path sanction and is referenced here only as the historical origin of the frontmatter triple, not as NORSOK path authority.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter.
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) (CLOSED) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`). [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — bulk-extraction prohibition.
> **Calc-citation pilot (epic-level):** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors pilot. W5-A does NOT extend the pilot to NORSOK code; that is a downstream consumer concern.
> **Review artifact (planned):** `scripts/review/results/2026-05-03-plan-2610-claude-internal.md` (single-author Claude r1 to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini UNAVAILABLE per memory (codex-cli 0.124.0 stdin-hang #2479; Gemini sandbox cwd=/tmp blocks workspace-hub overlay reads).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). Downstream consumer that will resolve the wiki pages this plan creates.
- Found: NORSOK references in `digitalmodel/src/` cluster around two domains — (a) **fatigue / SN-curve work** in `digitalmodel/fatigue/` (citing NORSOK N-004, 7 grep hits) and (b) **CO2 corrosion modelling** in `digitalmodel/cathodic_protection/corrosion_rate.py` (citing NORSOK M-506, 5 grep hits). Internal citation density: **NORSOK N-004** (7×) and **NORSOK M-506** (5× plus one underscore-form `NORSOK_M506` and one hyphen-form `NORSOK-N-004`). The `__init__.py` exports include `norsok_m506_co2`, indicating live calc-caller dependency on M-506.
- Internal-reference frequency total: 14 grep hits across 2 codes (N-004 and M-506). **Critical mismatch:** the most-cited internal code is **NORSOK M-506** but it is **NOT** in the on-disk `/mnt/ace/O&G-Standards/Norsok/` corpus. The on-disk corpus contains N-001, N-004, M-001, M-501, M-710, and D-SR-022. See Risks for the corpus-vs-citation-frequency mismatch and the forward path.
- Gap: zero NORSOK wiki pages exist anywhere — `find knowledge/wikis -name "norsok-*.md"` returns no matches. The `engineering-standards/wiki/standards/` directory holds only `api-17e.md` today (1 file).

### Standards

The on-disk NORSOK corpus is exactly **9 documents** (verified by `find` — see Evidence). After collapsing multi-edition duplicates into single umbrella pages with both editions referenced in `sources` frontmatter, the corpus collapses to **6 priority wiki pages**:

| Standard | Status | Source |
|---|---|---|
| NORSOK N-001 (Structural design) — 7th Ed (2010) current on-disk; 4th Ed (2004) superseded | gap | `Norsok_Standard_N-001_7th_Ed_(2010)_Structural_design.pdf` + `Norsok_Standard_N-001_4th_Ed_(2004)_Structural_design.pdf` |
| NORSOK N-004 (Design of steel structures) — 2nd Ed (2004) current on-disk; 1st Ed (1998) superseded | gap (cited 7× in `digitalmodel/fatigue/`) | `Norsok_Standard_N-004_2nd_Ed_(2004)_Design_of_Steel_Structures.pdf` + `Norsok_Standard_N-004_1st_Ed_(1998)_Design_of_Steel_Structures.pdf` |
| NORSOK M-001 (Materials selection) — 4th Ed (2004) | gap | `Norsok_Standard_M-001_4th_Ed_(2004)_Materials_selection.pdf` |
| NORSOK M-501 (Surface preparation and protective coating) — 5th Ed (2004) current on-disk; 4th Ed (1999) superseded | gap | `Norsok_Standard_M-501_5th_Ed_(2004)_...pdf` + `Norsok_Standard_M-501_4th_Ed_(1999)_...pdf` |
| NORSOK M-710 (Qualification of non-metallic sealing materials and manufacturers) — 2013 (only edition on disk) | gap | `M-710_Qualification_of_non-metallic_sealing_materials_and_manufacturers.pdf` |
| NORSOK D-SR-022 (BOP, Diverter and Drilling Riser System) — 1994 | gap | `NORSOK_D-SR-022_(1994)_BOP,_Diverter_and_Drilling_Riser_System.pdf` |

This plan therefore proposes **6 priority wiki pages** (within the requested 6-8 cap; stays at 6 because the 9 on-disk PDFs collapse to 6 unique standards once duplicate-edition pages share an umbrella page).

The most-internally-cited NORSOK code (`M-506`, 5×) is NOT promoted by W5-A — no raw on disk. It is deferred to a W5-B follow-up using publisher-portal pointers (Standards Norway sells M-506 via standard.no). **NORSOK Z-008** (risk-based maintenance — flagged in W1-B asset-management plan #2587) is NOT on disk either; deferred to W5-B with the same publisher-portal-pointer pattern. This is the corpus-vs-W1B-target-list mismatch.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — only existing engineering-standards code page; metadata-stub frontmatter pattern this plan replicates. Confirms lowercase-kebab `code_id` convention (`code_id: api-17e`).
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`. **Arithmetic AC** (per W2-A/W3-A/W4-A pattern): `page_count` after this plan = (current `page_count` at implementation time) + 6. Index also drifts (claims 5 but actual on-disk Markdown count is 9) — the implementation step MUST first reconcile the drift before applying the +6 increment.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision`); the new pages will all comply. **This is the path-sanction authority** for engineering-standards domain (NOT #2471).
- No pre-existing NORSOK pages exist anywhere — `find knowledge/wikis -name "norsok-*.md" -o -name "*-norsok-*.md"` returns empty.

### Documents consulted

- `docs/plans/2026-05-03-issue-2599-llm-wiki-W4A-engineering-standards-nace.md` — direct shape precedent. **Inherited contracts:** body-only no-raw-text scan, deterministic-regex denylist rule, multi-edition umbrella pattern (W4-A's `nace-mr-0175.md` covered the 2009 2nd Ed Pt 1/2/3), `legacy_publisher` pattern for org name changes (W5-A re-uses for the historical "Norwegian Petroleum Directorate" / "Statoil" / "Standards Norway" co-publisher chain on D-SR-022).
- `docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md` — direct shape precedent for the **`superseded_by` frontmatter pattern** that W5-A re-uses for NORSOK→ISO supersession lineage.
- `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md` — direct shape precedent for multi-part document handling; W5-A uses single-umbrella-per-code (different from W3-A's per-Part split because NORSOK editions are sequential not parallel-Part).
- `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` — W1-B target list (flagged NORSOK Z-008). W5-A delivers neighboring on-disk codes; Z-008 itself deferred to W5-B.
- `data/document-index/standards-transfer-ledger.yaml` — searched for `NORSOK` / `NS`: **zero rows** for NORSOK. One prose mention of NORSOK in an API RP 2FPS row (comparative appraisal note, not a NORSOK row). All 6 priority NORSOK pages introduced by this plan require new ledger rows.
- `data/document-index/online-resource-registry.yaml` — searched for `NORSOK`: zero entries. The Standards Norway publisher portal `https://standard.no/en/sectors/petroleum/norsok-standards/` is the canonical pointer.
- `.claude/rules/calc-citation-contract.md` — citation contract this plan exists to satisfy.
- `.claude/rules/coding-style.md` and `.claude/rules/patterns.md` — universal rules.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in **future tense**; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). Load-bearing.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite uses regex denylists; this plan keeps phrase lists narrowly scoped to NORSOK-specific copyright/cover-page strings.
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review acceptable when Codex/Gemini unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex CLI 0.124.0 stdin-hang regression #2479; Codex review unavailable.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini cwd=/tmp blocks workspace-hub overlay reads; Gemini review unavailable.
- `feedback_never_offer_to_self_label_plan_approved.md` — issue filing is downstream of plan-review approval; this plan is `status: draft`.

### Gaps identified

- No engineering-standards wiki pages exist for any NORSOK code (zero — `find knowledge/wikis -name "norsok-*.md"` returns empty).
- The standards-transfer-ledger contains zero NORSOK rows. 6 new ledger rows required.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any NORSOK page.
- The `online-resource-registry.yaml` lacks any NORSOK / Standards Norway entry. W5-A optionally adds one (deferred to W5-B if not approved).
- **NORSOK lifecycle gap:** most NORSOK standards have been superseded or cancelled, with content migrated to ISO. None of the 6 W5-A priority pages have a verified ISO-equivalent table maintained in the repo today. The `superseded_by` frontmatter pattern (introduced by W4-B) is load-bearing; W5-A's `superseded_by` test must accept either a wiki-internal link to an ISO page OR a `publisher_catalog_url` pointer when the wiki page does not yet exist.
- **Corpus-vs-W1B-target mismatch:** W1-B (#2587) flagged NORSOK Z-008 as a target. Z-008 is NOT on disk; W5-A explicitly does NOT promote it. Z-008 is deferred to W5-B (publisher-portal pointer).
- **Corpus-vs-citation-frequency mismatch:** the most-cited NORSOK code in `digitalmodel/` is M-506 (5×), which is also NOT on disk. M-506 deferred to W5-B.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — body explicitly scopes to CSA-Z276 (CSA-only, per memory)
- `#2540` — CLOSED — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — W1-A engineering-standards API
- `#2587` — OPEN — W1-B asset-management audit (flags NORSOK Z-008 as target)
- `#2594` — OPEN — W3-A engineering-standards ABS
- `#2596` — OPEN — W3-C #2471 sanction-scope erratum
- `#2599` — OPEN — W4-A engineering-standards NACE/AMPP
- `#2482` — CLOSED — vendor-derivative deny-list governance
- `#2481` — CLOSED — calc-citation contract pilot

**File existence** (`ls -la /mnt/ace/O&G-Standards/Norsok/` 2026-05-03):
```
M-710_Qualification_of_non-metallic_sealing_materials_and_manufacturers.pdf       (468740 bytes; 2013)
NORSOK_D-SR-022_(1994)_BOP,_Diverter_and_Drilling_Riser_System.pdf                (252172; 1994)
Norsok_Standard_M-001_4th_Ed_(2004)_Materials_selection.pdf                       (510988; 2004)
Norsok_Standard_M-501_4th_Ed_(1999)_Surface_Preparation_and_Protective_Coating.pdf (167682; 1999)
Norsok_Standard_M-501_5th_Ed_(2004)_Surface_Preparation_and_Protective_Coating.pdf (165245; 2004)
Norsok_Standard_N-001_4th_Ed_(2004)_Structural_design.pdf                         (175676; 2004)
Norsok_Standard_N-001_7th_Ed_(2010)_Structural_design.pdf                         (196309; 2010)
Norsok_Standard_N-004_1st_Ed_(1998)_Design_of_Steel_Structures.pdf                (7765534; 1998)
Norsok_Standard_N-004_2nd_Ed_(2004)_Design_of_Steel_Structures.pdf                (4906129; 2004)
```
Total: **9 PDFs** across 6 unique standards (D, M, N, Z series — NOTE: no Z series on disk despite W1-B target). Two M-501 editions, two N-001 editions, two N-004 editions collapse into 3 umbrella pages; M-001, M-710, D-SR-022 are single-edition pages.

- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (template exemplar)
- EXISTS: `knowledge/wikis/engineering-standards/CLAUDE.md` (path-sanction authority — see excerpt below)
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (resolver target)
- EXISTS: `tests/governance/test_2471_citation_scope.py` (allowlist-polarity guardrail; this plan must pass it — body-prose-only verification meanwhile, since `PLANS_GLOB` is `2026-05-02-*.md`)
- MISSING (this plan creates): `knowledge/wikis/engineering-standards/wiki/standards/norsok-n-001.md`, `norsok-n-004.md`, `norsok-m-001.md`, `norsok-m-501.md`, `norsok-m-710.md`, `norsok-d-sr-022.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_standards_norsok.py`

**Internal-reference proof — NORSOK in digitalmodel** (`grep -rohE "NORSOK[ _-]?(Z|M|N|D|S|U|R|L|H|I|J|P)[ _-]?[0-9]+" digitalmodel/src/ | sort | uniq -c`):
```
      5 NORSOK M-506
      1 NORSOK_M506
      7 NORSOK N-004
      1 NORSOK-N-004
```
Total: 14 hits across 2 codes (M-506 and N-004). **Of these, only `N-004` has raw on disk** — `M-506` is cited but not in `/mnt/ace/O&G-Standards/Norsok/`. M-506 deferred to W5-B.

**NORSOK source files in digitalmodel** (`grep -rli "NORSOK" digitalmodel/src/`):
```
digitalmodel/src/digitalmodel/cathodic_protection/corrosion_rate.py     # cites M-506
digitalmodel/src/digitalmodel/cathodic_protection/__init__.py            # exports norsok_m506_co2
digitalmodel/src/digitalmodel/fatigue/sn_library.py                      # cites N-004 Annex C
digitalmodel/src/digitalmodel/fatigue/fatigue_reporting.py               # cites N-004 Annex C
digitalmodel/src/digitalmodel/fatigue/environmental_correction.py        # cites N-004 Annex C.2.6
```

**NORSOK ledger rows present** (`grep -i "Norsok\|NORSOK" data/document-index/standards-transfer-ledger.yaml`):
```
notes: A comparative appraisal of the API RP 2FPS code against ISO, NORSOK, and ...
```
Single prose mention inside an API RP 2FPS row's notes field. **Zero NORSOK rows.** Plan adds 6.

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

**Public-revision evidence (web — Standards Norway / standard.no)**:
- NORSOK lifecycle status (May 2026): per Standards Norway, NORSOK standards are normally based on recognized international standards and remain in force on the Norwegian continental shelf alongside ISO. Recent revisions: NORSOK R-005 updated 2024 (replacing 2008); industrial-automation NORSOK revision under public consultation through 2025-01-10. The "supersession by ISO" framing in some industry sources is **not strictly correct** — NORSOK standards are revised in parallel with ISO, with mirror committees feeding both surfaces.
- M-501 (the on-disk 1999 4th Ed and 2004 5th Ed) has been further revised at least twice publicly since 2004; the on-disk 2004 5th Ed is NOT publisher-current. Calc-callers MUST verify against the publisher-current edition.
- M-710 has been further revised since 2013 (2014 4th Ed in publisher catalog).
- N-001 7th Ed (2010) and N-004 2nd Ed (2004) on-disk are both older than publisher-current revisions.
- D-SR-022 (1994) is a legacy "draft for revision" series — these were converted to NORSOK D-001 / D-002 / D-010 etc. and the SR-022 designation was withdrawn. The on-disk PDF retains historical traceability value only; the `superseded_by` frontmatter MUST point to the migration target.

<!-- Distinct sources counted: existing repo code (1), engineering-standards CLAUDE.md schema (2), W4-A precedent plan (3), W4-B precedent plan (4), W3-A precedent plan (5), W1-B target-list precedent plan (6), `/mnt/ace/.../Norsok/` corpus contents (7), citation rule + governance memory (8), web publisher-catalog (9), standards-transfer-ledger search result (10). 10 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2610-llm-wiki-W5A-engineering-standards-norsok.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-n-001.md` (Structural design; umbrella for 7th Ed 2010 + 4th Ed 2004) |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-n-004.md` (Design of steel structures; umbrella for 2nd Ed 2004 + 1st Ed 1998; cited 7× in `digitalmodel/fatigue/`) |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-001.md` (Materials selection; 4th Ed 2004) |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-501.md` (Surface preparation and protective coating; umbrella for 5th Ed 2004 + 4th Ed 1999) |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-710.md` (Qualification of non-metallic sealing materials and manufacturers; 2013) |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/norsok-d-sr-022.md` (BOP, Diverter and Drilling Riser System; 1994 — historical, designation withdrawn) |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 6 new rows) |
| Test contract | `tests/knowledge/test_engineering_standards_norsok.py` |
| Plans-index update | `docs/plans/README.md` |
| Plan review — Claude (r1, single-author) | `scripts/review/results/2026-05-03-plan-2610-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |

---

## Deliverable

Six new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/`, one per priority NORSOK code, each carrying calc-citation-contract-compliant frontmatter (`code_id`, `publisher`, `revision`, plus `extraction_policy: metadata-only`, `raw_copy_allowed: false`, plus NORSOK-specific `superseded_by` and `iso_equivalent` keys to track ISO migration lineage) and a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/Norsok/`, plus a single test file enforcing the no-raw-text-bleed and frontmatter-validity contracts — so downstream `digitalmodel/fatigue/` and `digitalmodel/cathodic_protection/` calc modules CAN resolve a `Citation` instance for NORSOK N-004 (immediately) and for the future M-506 / Z-008 codes (after W5-B lands publisher-portal pointers) without any verbatim source text entering git.

---

## Pseudocode

The work is templated 6x repetition. Each new wiki page follows this skeleton (identical to W4-A/W4-B modulo `publisher: Standards Norway` / `legacy_publisher: NORSOK Steering Committee` and NORSOK-specific fields):

```
---
title: "<Full NORSOK document name> — bounded summary"
tags: ["norsok", "standards", "<discipline-tag>", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: norsok-n-004                      # lowercase-kebab; matches engineering-standards CLAUDE.md, api-17e
publisher: "Standards Norway"              # current canonical publisher (standard.no)
publisher_full: "Standards Norway (NORSOK)"
legacy_publisher: "NORSOK Steering Committee"  # historical pre-2002 stewardship; preserved for traceability
revision: "2nd-Ed-2004"                    # on-disk edition; publisher-current may be later
publisher_current_revision: "2nd-Ed-2004"  # NEW per r1 P2-5; publisher-current as of verified_on; pin or "designation-withdrawn"
lifecycle_status: "in-force-mirror"         # NEW per r1 P2-5; one of {"in-force-mirror", "in-force-shelf-specific", "designation-withdrawn", "superseded-by-edition"}
revision_source: "<URL or '/mnt/ace path'>"  # OPTIONAL
verified_on: 2026-05-03                     # OPTIONAL
public_url: https://standard.no/en/sectors/petroleum/norsok-standards/
sources:
  - "/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_N-004_2nd_Ed_(2004)_Design_of_Steel_Structures.pdf"
  - "/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_N-004_1st_Ed_(1998)_Design_of_Steel_Structures.pdf"   # superseded; included for traceability
extraction_policy: metadata-only
raw_copy_allowed: false
norsok_series: N                           # NORSOK series letter (D, M, N, Z, etc.)
norsok_doc_number: "N-004"                  # full code form
ledger_id: NORSOK-N-004-2004                # bridge to standards-transfer-ledger uppercase form
supersedes: ["norsok-n-004-1998-internal"]  # OPTIONAL — the on-disk 1st Ed 1998 is bundled into this umbrella
                                            # rather than getting its own page; this key documents the lineage
                                            # WITHIN the umbrella
iso_relationship:                           # RENAMED from `superseded_by` per r1 review P1-2: NORSOK→ISO is
                                            # mostly parallel/mirror, NOT supersession. The rename ends the
                                            # misleading-by-construction key name. `relationship` enum widened
                                            # to {"full-replacement", "partial-overlap", "parallel-mirror",
                                            # "withdrawn-no-replacement"}. Empty array if no ISO counterpart.
                                            # For true supersession (only D-SR-022 designation-withdrawn case),
                                            # the entries describe the migration targets.
  - { code: "ISO 19902", relationship: "parallel-mirror", note: "ISO 19902 covers fixed steel offshore structures; mirror committee with NORSOK N-004; both remain in force on Norwegian shelf — NORSOK retains shelf-specific provisions" }
iso_equivalent: "ISO 19902"                # OPTIONAL; only when joint or mirror committee exists
cross_links:
  - []
---

# <Full NORSOK document name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.

## Where to find the full text
- Raw PDF: <absolute /mnt/ace/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://standard.no/en/sectors/petroleum/norsok-standards/ (most NORSOK standards are free-to-download from Standards Norway since 2002)
- Internal callers: <relative path(s) under digitalmodel/src/ that cite this code, or "no live caller; future-needed">
- Lifecycle: see frontmatter `revision`, `publisher_current_revision`, `lifecycle_status`, `iso_relationship` (single source-of-truth surface per r1 P2-5; calc-callers MUST verify against publisher-current edition before use)

## Cross-references
- [[norsok-m-001]] (materials selection companion)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file uses a parametrized fixture iterating over the 6 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-n-001.md` | Bounded summary umbrella for NORSOK N-001 (Structural design; 7th Ed 2010 current on-disk + 4th Ed 2004 superseded). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-n-004.md` | Bounded summary umbrella for NORSOK N-004 (Design of steel structures; 2nd Ed 2004 current on-disk + 1st Ed 1998 superseded). **Highest-priority NORSOK page** because it is cited 7× in `digitalmodel/fatigue/`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-001.md` | Bounded summary for NORSOK M-001 (Materials selection; 4th Ed 2004). Companion to M-710 / M-501 in the materials series. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-501.md` | Bounded summary umbrella for NORSOK M-501 (Surface preparation and protective coating; 5th Ed 2004 current on-disk + 4th Ed 1999 superseded). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-m-710.md` | Bounded summary for NORSOK M-710 (Qualification of non-metallic sealing materials and manufacturers; 2013). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/norsok-d-sr-022.md` | Bounded summary for NORSOK D-SR-022 (BOP, Diverter and Drilling Riser System; 1994). **Designation withdrawn** — `superseded_by` frontmatter points to NORSOK D-001/D-002/D-010 series migration target. |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | First reconcile drift (claims `page_count: 5`, on-disk is 9), then append "## Standards" section + 6 new rows; bump `page_count` per the **arithmetic AC** (reconciled-current + 6). |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 6 new rows. New IDs: `NORSOK-N-001-2010`, `NORSOK-N-004-2004`, `NORSOK-M-001-2004`, `NORSOK-M-501-2004`, `NORSOK-M-710-2013`, `NORSOK-D-SR-022-1994`. |
| Create | `tests/knowledge/test_engineering_standards_norsok.py` | Test contract: frontmatter, no-raw-text body-only scan, citation resolvability, ledger alignment, code_id uniqueness across wikis, `superseded_by` resolvability test (NEW — inherited from W4-B), `norsok_series` letter discipline. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_norsok.py`. Each test parametrized over the 6 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 6 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, lowercase-kebab; filename stem equals `code_id` verbatim (e.g., `norsok-n-004.md` ↔ `norsok-n-004`) |
| `test_frontmatter_has_publisher_standards_norway` | publisher discipline | YAML frontmatter | `publisher == "Standards Norway"`; if present, `publisher_full == "Standards Norway (NORSOK)"` |
| `test_frontmatter_has_revision` | revision presence per calc-citation-contract rule 2 | YAML frontmatter | `revision` non-empty string; matches NORSOK regex (see fenced-block below the table — pipes are pipe-alternation, not table syntax) |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_has_norsok_series_letter` | NORSOK-specific traceability | YAML frontmatter | `norsok_series` ∈ {`D`, `M`, `N`} for W5-A (tightened per r1 P2-3 to match the on-disk corpus letters; W5-B will widen to add `Z` for Z-008 and any other publisher-portal-pointer-only codes); matches first letter of `norsok_doc_number` |
| `test_frontmatter_has_norsok_doc_number` | NORSOK-specific traceability | YAML frontmatter | `norsok_doc_number` non-empty (e.g. `"N-004"`, `"D-SR-022"`) |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (narrow NORSOK-specific phrase set; **body-only scan** — frontmatter excluded) | page body after second `---` | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict `<500` word ceiling matching W1-A/W2-A/W3-A/W4-A/W4-B | page body | `0 < word_count < 500` strict on both bounds |
| `test_body_structure_is_whitelisted_only` | positive-shape: body contains only allowed sections | page body | top-level `##` headings exactly a subset of `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` (matches W4-A precedent shape; the per-r1-P2-5 decision moves lifecycle data into frontmatter only — no body "Lifecycle status" section to avoid frontmatter↔body drift) |
| `test_links_only_pointer_to_mnt_ace` | mentions raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/Norsok/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolver actually reads the wiki page | invoke resolver function from `digitalmodel/src/digitalmodel/citations/schema.py` for each NORSOK page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised |
| `test_ledger_alignment` | every page's `ledger_id` resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `ledger_id` | matching `id:` row found in ledger YAML |
| `test_code_id_unique_across_wiki_domains` | inherited from W2-A/W3-A/W4-A/W4-B AC | every `code_id` in `knowledge/wikis/*/wiki/standards/*.md` | no duplicates |
| `test_index_lists_all_pages` | wiki index updated | `index.md` contents | each new page link present in the "## Standards" section |
| `test_iso_relationship_pointer_resolves` | NEW W5-A test (renamed from `test_superseded_by_pointer_resolves` per r1 P1-2; W4-B's `superseded_by` test inheritance lives in W4-B's plan, not here); only on pages where `iso_relationship` is non-empty | YAML frontmatter | each `iso_relationship` entry's `code` field resolves to either (a) a wiki-internal page under `knowledge/wikis/*/wiki/standards/<code>.md` OR (b) a `publisher_catalog_url` field on the parent page pointing to a public catalog. The test accepts either fallback. `relationship` field MUST be one of `{"full-replacement", "partial-overlap", "parallel-mirror", "withdrawn-no-replacement"}` |
| `test_iso_equivalent_optional_field_well_formed` | ISO joint-committee discipline | YAML frontmatter | when `iso_equivalent` present, value matches `^ISO \d{4,5}(-\d+)?$` regex |

**Revision regex (literal, per r1 P2-2 — pipes are pipe-alternation, NOT Markdown-table syntax):**

```python
REVISION_PATTERN = r"^(\d+(st|nd|rd|th)-Ed-\d{4}|\d{4}|public-metadata-required-before-citation-use|designation-withdrawn-\d{4})$"
```

The implementer MUST transcribe this fenced-code regex verbatim into the test file (no `\|` escapes — those would only appear if the regex were embedded in a Markdown table cell, which it is not here).

**Scope rule (inherited from W4-A MAJOR-3):** the no-raw-text test scans **page body only** (Markdown content after the closing `---` frontmatter delimiter). Frontmatter is explicitly EXCLUDED from the scan. Test implementation MUST split the file at the second `---` line and scan only the post-frontmatter portion.

`RAW_TELLTALE_PHRASES` is a narrowly-scoped list (≤12 entries) drawn from NORSOK / Standards Norway publication front-matter conventions. **Each entry is a contiguous cover-page template token, NOT a paraphrasable name** — paraphrased prose like "published by Standards Norway in Lysaker" is allowed in body, while specific cover-page boilerplate strings are forbidden:

- "© NORSOK Standard"  (single contiguous cover-page boilerplate)
- "© Standards Norway"  (single contiguous cover-page boilerplate)
- "Strandveien 18"  (Standards Norway HQ street address — specific contiguous string)
- "Postboks 242"  (NORSOK postal-box boilerplate)
- "N-1326 Lysaker"  (Lysaker postal code — specific cover-page imprint)
- "All rights reserved" — flagged ONLY when within 5 tokens of "NORSOK" or "Standards Norway" (regex: `(NORSOK|Standards Norway)[^.]{0,40}All rights reserved` and reverse). Bare "All rights reserved" is allowed because the phrase is generic.
- "petroleum.standard.no"  (NORSOK platform domain — specific contiguous string)
- "Norwegian Petroleum Directorate"  (legacy publisher cover-page imprint pre-2002)
- "Statoil and Norsk Hydro" — flagged when adjacent to NORSOK boilerplate (joint-publisher cover-page reference)

**Deliberately allowed in body (paraphrased prose):**
- "Standards Norway" used as paraphrased publisher reference
- "NORSOK" used as paraphrased reference to the standards series
- "Lysaker, Norway" used in paraphrased prose about HQ location
- "Norwegian continental shelf" (technical scope phrase)
- `N-004`, `M-501`, `D-SR-022` (document numbers)
- `sour service`, `cathodic protection`, `fatigue` (technical concepts)
- `ISO 19902`, `ISO 13628-1`, `ISO 21457` (ISO-equivalent references — always allowed in body; same hard always-allow rule as W4-A's ISO 15156)

**Test determinism rule (inherited from W4-A MAJOR-3):** every `RAW_TELLTALE_PHRASES` entry is a deterministic literal substring or a fully-specified regex. Only the explicit `(NORSOK|Standards Norway)[^.]{0,40}All rights reserved` regex carries proximity logic.

The denylist will NOT overlap with OCIMF, API, DNV, ABS, NACE, or BSI denylists (verified: NORSOK-specific tokens — Lysaker postal code, Standards Norway street address, petroleum.standard.no domain — are unique to this publisher). **Honesty caveat (inherited from W2-A P2-3 / W3-A risk):** denylist alone will NOT catch a 100-200-word verbatim clause copy; reviewers MUST manually inspect every revision.

---

## Acceptance Criteria

- [ ] All 6 new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_norsok.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] No regression: `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes (the W3-C erratum's guardrail must remain green). **Note:** the guardrail's `PLANS_GLOB` is hard-pinned to `docs/plans/2026-05-02-*.md` and does NOT scan this 2026-05-03 plan. The AC therefore guarantees that no in-scope plans regress; it does NOT certify W5-A's #2471 framing. Compliance for THIS plan is established by the prose-only manual reviewer sweep documented in the r1 review's Verified-Compliance section. A one-line follow-up to extend `PLANS_GLOB` to `docs/plans/2026-*.md` is filed against #2596 and is NOT a W5-A blocker.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/norsok-*.md` contains zero matches for the `RAW_TELLTALE_PHRASES` denylist.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` all populated; `code_id` lowercase-kebab; filename stem equals `code_id` verbatim).
- [ ] **Publisher discipline:** every NORSOK page carries `publisher: "Standards Norway"`. The `legacy_publisher` field is OPTIONAL and used only on D-SR-022 (which predates the 2002 stewardship transfer).
- [ ] Citation downstream-resolution check (literal-equality on `revision` string per `digitalmodel/src/digitalmodel/citations/schema.py`):
  - `norsok-n-001.md` page MUST use `revision: "7th-Ed-2010"` in BOTH frontmatter AND any test `Citation(...)` call.
  - `norsok-n-004.md` page MUST use `revision: "2nd-Ed-2004"`.
  - `norsok-m-001.md` page MUST use `revision: "4th-Ed-2004"`.
  - `norsok-m-501.md` page MUST use `revision: "5th-Ed-2004"`.
  - `norsok-m-710.md` page MUST use `revision: "2013"`.
  - `norsok-d-sr-022.md` page MUST use `revision: "designation-withdrawn-1994"` (the 1994 PDF is the only edition; the SR-prefixed designation was withdrawn when content migrated to NORSOK D-001/D-002/D-010 series).
- [ ] **Lifecycle discipline (NEW for W5-A):** every NORSOK page carries the lifecycle data in **frontmatter only** (per r1 P2-5: pick one source-of-truth surface to avoid frontmatter↔body drift). Frontmatter `iso_relationship` array + a new `lifecycle_status` scalar key (values: `"in-force-mirror"`, `"in-force-shelf-specific"`, `"designation-withdrawn"`, `"superseded-by-edition"`) capture (a) the on-disk edition year (already in `revision`), (b) the publisher-current edition year (in a new `publisher_current_revision` key), (c) the ISO relationship (already in `iso_relationship`). The body section is renamed to "## Where to find the full text" with a single bullet linking to the frontmatter; the standalone "## Lifecycle status" body section is REMOVED to keep `test_body_structure_is_whitelisted_only` aligned with the W4-A precedent shape.
- [ ] Ledger alignment: every page's `ledger_id` (frontmatter key) resolves to a row `id:` in `data/document-index/standards-transfer-ledger.yaml` (6 new rows added by this plan).
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 6 new pages under a "## Standards" section. **Arithmetic AC:** the implementation MUST first reconcile the current `page_count` against the actual on-disk count (`find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` returns 9; the index claims 5 — a pre-existing drift). After reconciliation, apply `+6`. Final `page_count = (reconciled-current) + 6`.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified by this plan.
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified — verified there are NO pre-existing NORSOK pages anywhere (cross-checked by `find knowledge/wikis -name "norsok-*.md"` returning empty).
- [ ] **`code_id` uniqueness across wiki domains:** test asserts no `code_id` duplicated across `knowledge/wikis/*/wiki/standards/*.md`. Vacuous for NORSOK today (no other pages exist) but guards future drift.
- [ ] **`iso_relationship` resolvability (NEW W5-A AC; renamed from `superseded_by` per r1 P1-2):** for every page with non-empty `iso_relationship` array, every entry's `code` field must resolve via either (a) a wiki-internal page (preferred when ISO equivalent has its own wiki page) OR (b) a `publisher_catalog_url` pointer to an ISO/Standards Norway catalog page. The test accepts either fallback. The `relationship` field on each entry must be one of `{"full-replacement", "partial-overlap", "parallel-mirror", "withdrawn-no-replacement"}`.
- [ ] Plan review artifact present at `scripts/review/results/2026-05-03-plan-2610-claude-internal.md` (single-author Claude review). Codex/Gemini UNAVAILABLE per memory.
- [ ] Adversarial review explicitly addresses: (a) the corpus-vs-citation-frequency mismatch (M-506 cited 5× but NOT on disk; deferred to W5-B), (b) the corpus-vs-W1B-target mismatch (Z-008 flagged in #2587 but NOT on disk; deferred to W5-B), (c) the on-disk editions all being older than publisher-current editions, (d) the D-SR-022 designation-withdrawn status and `superseded_by` migration target accuracy, (e) the multi-edition umbrella-vs-per-edition-page decision.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 2 MAJOR + 5 MINOR — all addressed inline; allowlist test PASS |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (2 MAJOR + 5 MINOR fixes applied 2026-05-03)

**Revisions made based on review:**
- P1-1 (D-SR-022 successor mapping): replaced wrong "ISO 13533" successor claim with multi-entry mapping (NORSOK D-001/D-002/D-010 + API Spec 16A/16D/RP 16Q + ISO 13624-1 publisher-catalog fallback); each successor flagged for individual on-disk verification at implementation time.
- P1-2 (`superseded_by` field rename): renamed to `iso_relationship` across Pseudocode + test contract + AC; widened `relationship` enum to include `parallel-mirror`; preserves W4-B's `superseded_by` test inheritance because that lives in W4-B's plan/test, not here.
- P2-1 (umbrella-vs-per-edition fallback): added explicit deferral order to Risk #4 (split N-004 first, then drop M-501 4th Ed, then N-001 4th Ed) so the 6-8 page cap stays satisfied.
- P2-2 (regex pipe escaping): moved `REVISION_PATTERN` regex into a fenced Python code block so the pipe-alternation transcribes verbatim into the test file.
- P2-3 (`norsok_series` enum tightening): tightened to `{D, M, N}` for W5-A; widening to add `Z` etc. is documented as a W5-B follow-up.
- P2-4 (provisional issue number): plan header explicitly notes `2610` is provisional and will be reconciled at `gh issue create` time.
- P2-5 (Lifecycle frontmatter↔body drift): removed standalone "## Lifecycle status" body section; lifecycle data lives in frontmatter only (`revision`, `publisher_current_revision`, `lifecycle_status`, `iso_relationship`); body "Where to find" section gains a single bullet pointing to the frontmatter as the source-of-truth surface.
- P3-1 (review file naming): reconciled all internal references to use `scripts/review/results/2026-05-03-plan-2610-claude-internal.md` (matches the precedent set by `2026-05-02-plan-2541-claude.md` and the review-prompt path).

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk (corpus-vs-citation-frequency mismatch):** The most-cited NORSOK code in `digitalmodel/src/` is **M-506** (5 grep hits + an exported `norsok_m506_co2` symbol in `cathodic_protection/__init__.py`). M-506 is NOT in the on-disk `/mnt/ace/O&G-Standards/Norsok/` corpus. W5-A is therefore corpus-bound, NOT citation-frequency-bound for the materials-corrosion domain. **Mitigation:** explicit prose in M-001 / M-501 / M-710 page bodies notes that downstream calc-callers needing M-506 must wait for W5-B publisher-portal-pointer page. Cross-reference comment in `corrosion_rate.py` flagged as a follow-up note (out of scope for W5-A).
- **Risk (corpus-vs-W1B-target mismatch):** W1-B (#2587) flagged NORSOK Z-008 as a target for asset-management. Z-008 is NOT on disk. W5-A explicitly does NOT promote Z-008. **Mitigation:** Z-008 is deferred to W5-B (publisher-portal pointer); the W5-A plan body explicitly documents this scope decision so a downstream W1-B implementer cannot assume Z-008 is now resolvable.
- **Risk:** Copyright leakage. NORSOK publishes via Standards Norway from Lysaker, Norway with cover-page strings "Standards Norway", "NORSOK Standard", "© Standards Norway", "Strandveien 18", "Postboks 242", "N-1326 Lysaker". **Mitigation (inherited from W4-A/W4-B):** word-count ceiling `<500` strict + positive-shape structural test + `extraction_policy: metadata-only` + `raw_copy_allowed: false` + cross-review on every revision touching `wiki/standards/norsok-*.md`. **Honesty caveat:** denylist alone is necessary-but-not-sufficient.
- **Risk (multi-edition umbrella discipline):** N-001 (4th + 7th editions on disk), N-004 (1st + 2nd editions on disk), and M-501 (4th + 5th editions on disk) each have two on-disk editions. W5-A proposes a SINGLE umbrella page per code (with the `revision` frontmatter pinned to the current edition and the superseded edition listed in `sources` for traceability). **Alternative considered and rejected:** 6 separate pages (one per edition × 3 codes = 6, plus 3 single-edition pages = 9 total) would bloat scope and inflate page count beyond the 6-8 cap. Reviewer SHOULD challenge this if per-edition-citation granularity is required by an actual `digitalmodel/` consumer (none exist today — verified by grep).
  - **Fallback path if reviewer requires per-edition split (NEW per r1 P2-1):** if the reviewer mandates per-edition pages for the multi-edition codes, the page count would jump to 9 (3 codes × 2 editions = 6 + 3 single-edition pages = 9), which exceeds the 6-8 cap. Resolution order: (a) split N-004 first (cited 7× in `digitalmodel/fatigue/`, so per-edition citation granularity has the strongest live-caller justification), giving 7 pages — within cap; (b) if N-001 also requires split, drop the M-501 1999 4th Ed superseded edition from W5-A scope and defer it to W5-B (single-edition lifecycle precedent applied), giving 8 pages — at cap; (c) if all three codes require split, defer the entire W5-A and re-scope as W5-A1/W5-A2 in a follow-up plan. The defer order is N-001 4th Ed → M-501 4th Ed → N-004 1st Ed (drop oldest superseded editions first, preserve current editions and high-citation codes).
- **Risk (NORSOK D-SR-022 designation withdrawn):** D-SR-022 (1994) is a pre-2002 "draft for revision" series document. The SR-prefixed designation was withdrawn when content migrated to NORSOK D-001 (well design and well-control), D-002 (system requirements drilling/well facilities), D-010 (well integrity in drilling and well operations). The BOP/diverter/riser scope does NOT have a single clean ISO successor — the lineage requires multiple targets across distinct equipment classes: BOP stack design / pressure-control = API Spec 16A (well-control equipment) and API Spec 16D (BOP control systems); drilling riser = API RP 16Q / ISO 13624-1; diverter / rotating control devices = API Spec 16C and API Spec 16RCD. (NOTE: ISO 13533 — "Drill-through equipment" — was originally proposed as the equivalent in W5-A r1 draft but is the WRONG equivalent: 13533 covers the equipment train BELOW the diverter/BOP stack, NOT BOP/diverter/riser; r1 review caught this and corrected.) **Mitigation:** the page's `revision: "designation-withdrawn-1994"` and `iso_relationship` (formerly `superseded_by`; see Risk #6 rename) array explicitly list D-001, D-002, D-010 as the NORSOK-internal successors and API Spec 16A / API Spec 16D / API RP 16Q (with ISO 13624-1 as `publisher_catalog_url` fallback) as the international-standard successors. **Each cited successor's on-disk presence MUST be verified individually at implementation time** — do NOT propagate W4-B plan claims without `find /mnt/ace -iname "*<code>*"` confirmation. Page is promoted for historical-traceability value only — calc-callers MUST NOT cite D-SR-022 for new work.
- **Risk (ISO-supersession lineage accuracy):** The `superseded_by` claims for each page are based on industry knowledge and the Standards Norway publisher portal, not on a verified per-clause supersession map. Several NORSOK standards retain Norwegian-shelf-specific provisions that are NOT in the ISO-equivalent. **Mitigation:** every `superseded_by` entry carries a `relationship` field with values `{"full-replacement", "partial-overlap", "withdrawn-no-replacement"}` and a free-text `note` field explaining the relationship. Reviewers SHOULD spot-check at least 2 of the 6 pages against the publisher catalog before approval.
- **Risk (NORSOK lifecycle is not "supersession by ISO"):** Per Standards Norway (May 2026 web evidence), NORSOK standards are revised in parallel with ISO via mirror committees, NOT "superseded by ISO". The "superseded by ISO" framing in some industry sources is imprecise. **Mitigation (structural — addresses r1 P1-2):** the frontmatter field is named `iso_relationship` (NOT `superseded_by`) so the structurally-load-bearing key matches the parallel-mirror reality. The `relationship` enum is widened to `{"full-replacement", "partial-overlap", "parallel-mirror", "withdrawn-no-replacement"}`. Only D-SR-022 (designation-withdrawn) carries `relationship: "withdrawn-no-replacement"` against its NORSOK-internal D-001/D-002/D-010 successors and `parallel-mirror`/`partial-overlap` against the API Spec 16A/16D/RP 16Q targets. The W4-B `superseded_by` test inheritance is preserved by name in the test file (`test_superseded_by_pointer_resolves` is renamed to `test_iso_relationship_pointer_resolves`); the BS-EN-ISO genuine-supersession case in W4-B remains undisturbed because that pattern lives in W4-B's plan and test file, not W5-A's. **Mitigation (prose):** the page body's "Lifecycle status" section also uses the accurate phrasing "content mirrored in ISO XXXXX" or "ISO XXXXX is the international counterpart"; only D-SR-022 (designation withdrawn) and edition-replacements (e.g. N-004 1998 → 2004) use literal "superseded" language.
- **Risk (on-disk edition vs. publisher-current edition gap):** All 6 promoted standards have on-disk editions OLDER than the publisher-current revisions (e.g., M-501 5th Ed 2004 on disk; publisher-current is later). **Mitigation:** every page body MUST include a "Lifecycle status" section pointing to `https://standard.no/` with explicit prose. **AC** records this as the "edition gap discipline" — every NORSOK page must acknowledge the gap.
- **Risk:** Ledger-form / wiki-form ID divergence. Ledger uses uppercase-with-hyphens (`NORSOK-N-004-2004`); wiki uses lowercase-kebab (`norsok-n-004`). **Mitigation:** add a `ledger_id` frontmatter key on each wiki page; `test_ledger_alignment` checks `frontmatter['ledger_id']` exists in the ledger, NOT `code_id`. Same pattern as W3-A/W4-A/W4-B.
- **Risk (cross-author confusion — `iso_relationship` cardinality):** A NORSOK standard MAY have multiple ISO equivalents covering different parts (e.g., N-004 maps to ISO 19902 for jacket structures and ISO 19904-1 for floating structures). The `iso_relationship` array supports multiple entries, but the reviewer MAY argue for a single entry per page to keep test logic simple. **Decision:** array-of-entries with `relationship` field per entry is the chosen design; matches W4-B's BS-EN-ISO multi-target pattern (the W4-B field is `superseded_by` because BS-EN-ISO IS true supersession; W5-A renames to `iso_relationship` per r1 P1-2 because NORSOK→ISO is parallel-mirror).
- **Risk (`norsok_series` enum scope — addresses r1 P2-3):** the on-disk W5-A corpus uses series letters `D, M, N` only. W5-A tightens `test_frontmatter_has_norsok_series_letter` to that exact set so an accidental typo (e.g., `Z-008` slipped into a W5-A page) trips the test as an early-warning. **Decision:** `{D, M, N}` for W5-A; widen to add `Z` (Z-008, Z-013) and any other publisher-portal letters in W5-B when those land. The forward-flexible widening is a one-line test edit — cost of tightening now is zero, benefit is early-warning on scope creep.

- **Open:** **Should cancelled-and-not-superseded NORSOK standards be promoted at all?** The 1994 D-SR-022 is the only on-disk member of this category (designation withdrawn; partial migration to D-001/D-002/D-010 + ISO 13533 but no clean 1:1 successor). **W5-A default:** YES — promote with `revision: "designation-withdrawn-1994"` and prominent `superseded_by` array, because (a) historical-traceability value (legacy citations in older `digitalmodel/` work might exist; verified zero structured calls today but prose comments may exist), (b) the on-disk PDF will not vanish from `/mnt/ace`, so a resolver target should exist if a calc-caller surfaces it, (c) excluding D-SR-022 reduces the page count to 5 which is still within the 6-8 cap but loses the lifecycle-discipline test case. **Reviewer MUST confirm.** If rejected, scope drops to 5 pages.
- **Open:** Issue title and labels. Proposed title: `feat(llm-wiki): bounded NORSOK Norwegian-sector standards summary promotion (W5-A)`. Proposed labels: `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:standards`. Issue filing is downstream of plan-review approval per `feedback_never_offer_to_self_label_plan_approved.md`.
- **Open:** Should `online-resource-registry.yaml` gain a `standards_norway_norsok` entry pointing to `https://standard.no/en/sectors/petroleum/norsok-standards/`? **W5-A default:** YES (one-line addition; mirrors the AMPP knowledge-hub entry in W4-A's evidence). If reviewer prefers to defer to W5-B, drop from this plan.
- **Open:** Should the multi-edition umbrellas (N-001, N-004, M-501) split into per-edition pages instead? Default: NO (umbrella with `sources` array listing both editions). Reviewer MAY require split if per-edition citation granularity is needed.

---

## Complexity: T2

**T2** — multi-file documentation work (6 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 docs/plans/README.md update = 10 files), no new code modules, but a real test contract (≥17 parametrized assertions × 6 pages = ~100 effective test cases). Implementation is templated repetition. Design risk is concentrated in (a) the corpus-vs-citation-frequency mismatch (M-506 cited but absent), (b) the corpus-vs-W1B-target mismatch (Z-008 flagged but absent), (c) the multi-edition umbrella decision for N-001/N-004/M-501, (d) the D-SR-022 designation-withdrawn `superseded_by` migration target accuracy, (e) the NEW NORSOK-specific "Lifecycle status" body section and the corresponding positive-shape test extension. Complexity sits firmly in T2 — heavier than W4-A (3 pages) but lighter than W4-B (8 pages), and the `superseded_by` test is inherited from W4-B rather than newly designed.
