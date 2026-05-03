# Plan for LLM-Wiki Completeness W4-B: Bounded BSI Offshore-Petroleum Subset Summary Promotion

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-03
> **Issue:** _not yet filed_ (issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md`; expected title and labels in Open Questions)
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) (CLOSED) — overnight Elements corpus planning wave (parent of the W1/W2/W3 completeness chain)
> **Sibling precedent (W1-A, API):** [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) (OPEN) — bounded-promotion pattern. W1-A originally over-cited #2471 as path-sanction; corrected via [W3-C erratum](https://github.com/vamseeachanta/workspace-hub/issues/2596) (OPEN). W4-B inherits the post-erratum framing only.
> **Sibling precedent (W2-A, DNV):** [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) (OPEN) — adopts the corrected #2471 framing (engineering-standards/CLAUDE.md schema as path-sanction; #2471 is the historical origin of the frontmatter triple, not generalized standards-routing authority).
> **Sibling precedent (W3-A, ABS):** [#2594](https://github.com/vamseeachanta/workspace-hub/issues/2594) (OPEN) — direct W3-A precedent on the engineering-standards wiki for a single-publisher bounded subset; W4-B inherits the test contract verbatim and adds a new `superseded_by` regression test specific to BSI's BS-EN-ISO adoption pattern.
> **Sibling precedent (W3-B, ISO 19900-series):** [#2595](https://github.com/vamseeachanta/workspace-hub/issues/2595) (OPEN) — ISO offshore-engineering subset; W4-B's `superseded_by` pointers will frequently target ISO codes whose wiki pages do not yet exist (W3-B may close that gap; if not, W4-B's test must accept "publisher catalog pointer" form).
> **Path sanction (BSI):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`). [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) is **CSA-Z276-only** per memory `project_wiki_standards_path_decision.md` (verified 2026-04-25); it is NOT generalized standards-path sanction. The W3-C erratum allowlist test at `tests/governance/test_2471_citation_scope.py` will catch any over-citation; W4-B's prose deliberately keeps every #2471 mention adjacent to a CSA-Z276 / over-citation / W3-C erratum / scope token to satisfy the allowlist.
> **Citation contract:** `.claude/rules/calc-citation-contract.md` rule 2 — every standards-derived constant in a calc module must resolve to a wiki page with `code_id`/`publisher`/`revision` frontmatter.
> **Governance reference:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) (CLOSED) — vendor-derivative deny-list (raw text MUST stay in `/mnt/ace`). [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — bulk-extraction prohibition.
> **Calc-citation pilot (epic-level):** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED) — DNV-OS-E301 mooring safety factors prose-level pilot (W4-B does NOT extend the pilot to BS code; that is a downstream consumer concern).
> **Review artifact (planned):** `scripts/review/results/2026-05-03-plan-W4B-claude-internal.md` (single-author Claude r1 to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini UNAVAILABLE per memory (codex-cli 0.124.0 stdin-hang #2479; Gemini sandbox cwd=/tmp).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` dataclass with fail-closed `CitationResolutionError` (per #2481 D2). Downstream consumer that will resolve the wiki pages this plan creates.
- Found: `digitalmodel/src/digitalmodel/citations/registry.py` — companion resolver. Single live `Citation(...)` constructor on disk lives at line 52 (DNV-OS-E301 pilot only; no live BS `Citation(...)` exists today).
- Internal-reference frequency: BS / BSI / BS EN ISO appears in `digitalmodel/src/` only as occasional prose comments (`grep` returns zero structured citations). BSI is therefore a **lower-frequency consumer** than DNV / API / ABS today; priority for W4-B derives from corpus coverage of the BS 13xxx offshore-petroleum subset (the same numeric range as ISO 13xxx, intentionally) rather than grep-frequency.
- Gap: zero summary-promotion artifact exists for the `/mnt/ace/O&G-Standards/BSI/` corpus in any wiki domain. The standards ledger contains exactly **one** BS row (`BS-7608`, structural fatigue) — none for the 13xxx offshore-petroleum subset. The 11 priority documents below all require new ledger rows.

### Standards

The **8** priority BS documents biased toward subsea production / drill-through equipment / marine drilling risers / offshore platform piping (8 chosen to match W3-A's T2 sizing precedent and to keep the new-page count manageable given the `superseded_by` complexity):

| Standard | Status | Source |
|---|---|---|
| BS EN ISO 13628-2 (2001, with Corrigendum 1) — Flexible pipe systems for subsea (unbonded) | gap | `/mnt/ace/O&G-Standards/BSI/BS_13628_Pt_2_with_Corrigendum1_(2001)_Flexible_pipe_systems_for_subsea.pdf` |
| BS EN ISO 13628-3 (2001, with Corrigenda 1+2) — Through-Flowline (TFL) Systems | gap | `/mnt/ace/O&G-Standards/BSI/BS_13628_Pt_3_with_Corrigenda_1_+_2_(2001)_Through_Flowline_(TFL)_Systems.pdf` |
| BS EN ISO 13628-5 (2002) — Subsea umbilicals | gap | `/mnt/ace/O&G-Standards/BSI/BS_13628_Pt_5_(2002)_Subsea_umbilicals.pdf` |
| BS EN ISO 13628-8 (2002) — Remotely Operated Vehicle (ROV) interfaces | gap | `/mnt/ace/O&G-Standards/BSI/BS_13628_Pt_8_(2002)_Remotely_Operated_Vehicle.pdf` |
| BS EN ISO 13533 (2002) — Drill-through equipment (BOPs) | gap | `/mnt/ace/O&G-Standards/BSI/BS_13533_(2002)_Drill_through_equipment.pdf` |
| BS EN ISO 13625 (2002) — Marine drilling riser couplings | gap | `/mnt/ace/O&G-Standards/BSI/BS_13625_(2002)_Marine_drilling_riser_couplings.pdf` |
| BS EN ISO 13703 (2001) — Design & installation of piping systems on offshore production platforms | gap | `/mnt/ace/O&G-Standards/BSI/BS_13703_(2001)_Design_&_installation_of_piping_systems_on_offshore_production_platforms.pdf` |
| BS EN ISO 13626 (2004) — Drilling and well-servicing structures | gap | `/mnt/ace/O&G-Standards/BSI/BS_13626_(2004)_Drilling_and_production_equipment_-_drilling_and_well_servicing_structures.pdf` |

This is **8** entries — all have a verifiable raw source under `/mnt/ace/O&G-Standards/BSI/`. **BS 13628 Pt 1, 4, 6, 7, 9, 10, 11, 15** (other parts of the subsea-production-systems family) are NOT among the 11 BS 13xxx PDFs on disk; deferred to a W4-B follow-up using publisher-portal pointers from BSI Knowledge. BS 13678 / BS 14310 / BS 14693 / BS 15136 etc. are out of the BS 13xxx scope and out of W4-B scope.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — the ONLY existing engineering-standards code page (lowercase-kebab `code_id` convention).
- `knowledge/wikis/engineering-standards/wiki/index.md` — currently `page_count: 5`, `source_count: 5`. Per W3-A AC inheritance, W4-B's index update uses **arithmetic**: `page_count` after W4-B = (current `page_count` at implementation time) + 8. If W1-A/W2-A/W3-A/W3-B all land before W4-B, the count math compounds; the AC is pinned to delta, not absolute.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — defines the standards-page extra fields (`code_id`, `publisher`, `revision` required at L0 prose); the new pages will all comply. **This is the path-sanction authority** for engineering-standards domain (NOT #2471).
- No pre-existing BS pages exist anywhere in `knowledge/wikis/*/wiki/standards/` (cross-checked via `find … -name "bs-*.md" -o -name "bsi-*.md"`); contrast W2-A's 5x DNV cross-wiki collision and W3-A's zero-collision baseline.

### Documents consulted

- `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md` — **direct precedent**. W4-B inherits verbatim: bounded-preview frontmatter, no-raw-text test, citation-resolvability test, lowercase-kebab `code_id`, ledger-alignment test, cross-wiki uniqueness test, `<500` strict word-count, positive-shape structural test. **Inherited fix lineage:** the W1-A inheritance-blocker (`#2471` over-cite at lines 9 and 225) was corrected in W3-A; W4-B carries the corrected framing.
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — revised W2-A plan (post-erratum framing).
- `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — bounded preview pattern.
- `data/document-index/standards-transfer-ledger.yaml` — contains exactly 1 BS row (`BS-7608`, structural fatigue, unrelated to the 13xxx offshore subset). All 8 priority BS documents introduced by this plan require new ledger rows.
- `.claude/rules/calc-citation-contract.md` — citation contract this plan exists to satisfy.
- `tests/governance/test_2471_citation_scope.py` — W3-C erratum allowlist regression test; W4-B's prose stays within the allowlist.

### Project memory consulted

- `feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed.
- `project_wiki_standards_path_decision.md` — explicitly states **#2471 is CSA-Z276-only** (verified 2026-04-25). The W3-C erratum forward-amended W1-A and W1-B; W4-B is drafted post-erratum.
- `feedback_naive_secret_scan_false_positive_cascade.md` — relevant because the test suite uses regex denylists; W4-B's phrase list is narrowly scoped to BSI-specific copyright/cover-page strings ("389 Chiswick High Road, London W4 4AL", "© BSI", "British Standards Institution") and will NOT overlap with API / DNV / ABS / OCIMF denylists.
- `feedback_permission_gate_blocks_cross_review.md` — single-author Claude review acceptable when Codex/Gemini are unavailable.
- `feedback_codex_cli_0_124_upstream_regression.md` — Codex review unavailable.
- `feedback_gemini_sandbox_overlay_blindness.md` — Gemini review unavailable.
- `feedback_never_offer_to_self_label_plan_approved.md` — issue filing is downstream of plan-review approval; this plan is `status: draft`.

### Gaps identified

- No engineering-standards wiki pages exist for any BS / BSI / BS EN ISO code (zero, anywhere in `knowledge/wikis/*/wiki/standards/`).
- The standards-transfer-ledger contains 1 BS row (`BS-7608`); 8 new ledger rows required for the 8 priority BS 13xxx documents.
- No regression test asserts "wiki page does not contain raw PDF text bleed-through" for any BS page.
- **No test asserts that a `superseded_by` frontmatter pointer actually resolves to a real ISO/EN code form** — this is a NEW W4-B-specific test, since the BSI-vs-ISO supersession pattern is the load-bearing value of every BS wiki page in this batch.
- ISO counterpart wiki pages (`iso-13628-2.md`, `iso-13533.md`, `iso-13625.md`, `iso-13703.md`, `iso-13626.md`) DO NOT exist in any wiki domain — confirmed via `find ... -name "iso-1362*.md"` returning zero matches in `wiki/standards/`. W4-B's `superseded_by` test therefore accepts EITHER a wiki-internal link to an ISO page (when present) OR a `publisher_catalog_url` pointer to the ISO catalog (when the wiki page does not yet exist). W3-B may close some of this gap; W4-B does not block on W3-B.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" (CSA-Z276-only — referenced here only in the W3-C erratum scope-discussion context, per the `tests/governance/test_2471_citation_scope.py` allowlist)
- `#2540` — CLOSED — parent epic
- `#2586` — OPEN — W1-A precedent (post-erratum)
- `#2590` — OPEN — W2-A precedent (post-erratum)
- `#2594` — OPEN — W3-A precedent (direct)
- `#2595` — OPEN — W3-B (ISO 19900-series) sibling
- `#2596` — OPEN — W3-C erratum
- `#2482` — CLOSED — vendor-derivative deny-list
- `#2481` — CLOSED — calc-citation pilot

**File existence** (`ls` 2026-05-02):
- EXISTS: `/mnt/ace/O&G-Standards/BSI/` — 76 entries (75 PDFs + 1 .doc), of which **11 BS_13xxx PDFs** match the offshore-petroleum subset. The remaining 64 cover BS 7608 fatigue, BS 4360 sections, BS 5400 bridges, BS 7448 fracture mechanics, BS 14xxx / 15xxx / 16xxx / 17xxx (downhole / artificial lift / HVAC / sour-service / emergency-response / heat exchangers / life cycle / lock mandrels / side-pocket mandrels) — out of W4-B scope.
- EXISTS: `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` (only existing engineering-standards code page).
- EXISTS: `knowledge/wikis/engineering-standards/CLAUDE.md` (path-sanction authority).
- EXISTS: `tests/governance/test_2471_citation_scope.py` (W3-C allowlist test).
- MISSING (this plan creates): 8 wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/bs-*.md` plus `tests/knowledge/test_engineering_standards_bsi.py`.

**BS 13xxx PDF inventory** (`find /mnt/ace/O&G-Standards/BSI -name "BS_13*" -type f` 2026-05-02):
```
BS_13533_(2002)_Drill_through_equipment.pdf
BS_13535_(2001)_Hoisting_equipment.pdf                        # NOT in priority 8 (covered by ISO 13535; deferred)
BS_13625_(2002)_Marine_drilling_riser_couplings.pdf
BS_13626_(2004)_Drilling_and_production_equipment_-_drilling_and_well_servicing_structures.pdf
BS_13628_Pt_2_with_Corrigendum1_(2001)_Flexible_pipe_systems_for_subsea.pdf
BS_13628_Pt_3_with_Corrigenda_1_+_2_(2001)_Through_Flowline_(TFL)_Systems.pdf
BS_13628_Pt_3_with_Corrigendum_1_(2001)_Through_Flowline_(TFL)_Systems.pdf   # duplicate (older corrigendum); both .pdfs collapse into one wiki page
BS_13628_Pt_5_(2002)_Subsea_umbilicals.pdf
BS_13628_Pt_8_(2002)_Remotely_Operated_Vehicle.pdf
BS_13678_(2000)_Evaluation_&_testing_of_threat_compounds_for_use_with_casing_tubing_&_line_pipe.PDF   # NOT 13xxx-offshore subset; BS 13678 is downhole compounds
BS_13703_(2001)_Design_&_installation_of_piping_systems_on_offshore_production_platforms.pdf
```
11 total. The 8 priority pages cover 9 of the 11 (the duplicate BS 13628 Pt 3 corrigendum file collapses into one wiki page; BS 13535 and BS 13678 are deferred). Total counts (case-sensitive `BS_*` matching): `find /mnt/ace/O&G-Standards/BSI -name "BS_13*" -type f | wc -l` = **11**; `find /mnt/ace/O&G-Standards/BSI -name "BS_*" -type f | wc -l` = **49**. The full directory listing returns **76** entries (75 PDFs + 1 .doc); the gap between 49 and 76 is files whose names lack the case-sensitive `BS_` prefix (e.g. `bs4360.doc`) or use different separators — these are NOT in W4-B priority scope. The two `find` runs above answer different questions (case-sensitive prefix glob vs full directory enumeration) and the 76-vs-49 reconciliation is naming-convention only, not a missing-file gap.

**BSI ledger rows present** (`grep -B0 -A6 "BSI\|^- id: BS" data/document-index/standards-transfer-ledger.yaml`):
```
- id: BS-7608
  title: Guide to fatigue design and assessment of steel products
  org: BS
  domain: structural
  doc_path: ''
  doc_paths: []
  status: done
```
Only 1 BS row (BS-7608, fatigue, unrelated to the offshore-petroleum subset). Plan adds 8.

**Engineering-standards CLAUDE.md path-sanction excerpt** (the load-bearing line replacing the W1-A "#2471 path sanction" claim — same as W3-A):
```
wiki/
  standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)
```
Plus the Standards-page extra-fields table (`code_id`, `publisher`, `revision` all required at L0 prose).

**BS-EN-ISO supersession pattern (web evidence — load-bearing for `superseded_by`):**
- BSI's `BS EN ISO 13628-2:2001` is the British-published adoption of ISO 13628-2 (CEN ratified, BSI re-published with `BS EN ISO` prefix). Per BSI Knowledge product page <https://knowledge.bsigroup.com/products/petroleum-and-natural-gas-industries-design-and-operation-of-subsea-production-systems-flexible-pipe-systems-for-subsea-and-marine-applications-1>, the standard is identical to ISO 13628-2 in technical content and identical with the English version of API 17J. **Implication:** the BS form is NOT a "superseded" standard in the obsolete sense — it is the BSI-published form of the ISO standard. The wiki page's value-add is therefore: (a) historical filename / disk-path provenance (the `/mnt/ace/O&G-Standards/BSI/BS_13628_Pt_2_*.pdf` label), (b) UK-jurisdiction adoption notes (e.g., `jurisdiction: UK` frontmatter), (c) corrigendum tracking (Corrigendum 1 for Pt 2; Corrigenda 1+2 for Pt 3) which is BSI-publication-specific.
- BS EN ISO 13703 (offshore platform piping) — confirmed superseded by BS EN ISO 13703-3:2023 (Oil and gas industries, lower carbon energy — piping). Per ISO catalog <https://www.iso.org/standard/79569.html>. The 2001 BS form on disk is therefore a historical edition.
- BS EN ISO 13533 (drill-through equipment) — present in ISO catalog. Status reported as historic by BSI in some jurisdictions; current ISO equivalent retained.
- **`superseded_by` semantic:** for W4-B, the field expresses "the canonical current ISO / EN ISO code that supersedes the BS-prefixed historical form". Where the BS form IS the EN ISO adoption (e.g., BS 13628-2 ⇒ BS EN ISO 13628-2), the `superseded_by` value should be `iso-13628-2` (the unprefixed ISO code-id) and a free-text note clarifies "BSI-published form of the ISO standard, not technically superseded — the BS prefix is jurisdictional re-publication".

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md` |
| Wiki page (1) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-2-flexible-pipe-subsea.md` |
| Wiki page (2) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-3-tfl-systems.md` |
| Wiki page (3) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-5-subsea-umbilicals.md` |
| Wiki page (4) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-8-rov-interfaces.md` |
| Wiki page (5) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13533-drill-through-equipment.md` |
| Wiki page (6) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13625-marine-drilling-riser-couplings.md` |
| Wiki page (7) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13703-offshore-platform-piping.md` |
| Wiki page (8) | `knowledge/wikis/engineering-standards/wiki/standards/bs-13626-drilling-well-servicing-structures.md` |
| Wiki index update | `knowledge/wikis/engineering-standards/wiki/index.md` (append "## Standards" entries; arithmetic `page_count += 8`) |
| Standards-ledger update | `data/document-index/standards-transfer-ledger.yaml` (add 8 new rows) |
| Test contract | `tests/knowledge/test_engineering_standards_bsi.py` |
| Plan review — Claude (r1, single-author) | `scripts/review/results/2026-05-03-plan-W4B-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) |
| Plan review — Gemini | UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads) |
| docs/plans/README.md | append W4-B row to plan index |

---

## Deliverable

Eight new bounded-summary wiki pages under `knowledge/wikis/engineering-standards/wiki/standards/` (one per priority BS 13xxx code), each carrying calc-citation-contract-compliant frontmatter (`code_id`, `publisher: BSI`, `revision`, plus `extraction_policy: metadata-only`, `raw_copy_allowed: false`, `superseded_by: <iso-code-id>`, `jurisdiction: UK`), a links-only pointer to the raw source under `/mnt/ace/O&G-Standards/BSI/`, and a single test file enforcing the no-raw-text-bleed, frontmatter-validity, citation-resolvability, ledger-alignment, code-id-uniqueness, AND a NEW `superseded_by`-pointer-resolves contract — so downstream calc modules CAN resolve `Citation` instances for the BS-published form of these eight ISO offshore-petroleum codes (subsea production systems Pt 2/3/5/8, drill-through equipment, marine drilling riser couplings, offshore-platform piping, drilling/well-servicing structures) without any verbatim source text entering git, AND so the historical-context value-add of each BS page (UK jurisdiction, corrigendum tracking, BSI-publication metadata) is preserved alongside the ISO supersession pointer.

---

## Pseudocode

The work is templated 8x repetition. Each new wiki page will follow the W3-A skeleton plus the W4-B-specific `superseded_by` and `jurisdiction` fields:

```yaml
---
title: "<Full BS document name> — bounded summary"
tags: ["bsi", "standards", "<discipline-tag>", "metadata-only"]   # single-publisher-token convention per W3-A — m3 fix from r1 review
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: bs-<doc-number-or-slug>          # lowercase-kebab; matches engineering-standards CLAUDE.md, api-17e, W1-A, W2-A, W3-A
publisher: BSI                              # canonical short name; full form "British Standards Institution" tracked in publisher_full
publisher_full: "British Standards Institution"
revision: "<YYYY>"                          # 4-digit base year per W3-A revision-discipline rule
revision_amendments_note: "<corrigendum and amendment list — text only, NOT part of revision string>"
jurisdiction: UK                            # NEW for W4-B — every BS page is UK-published
superseded_by: iso-<corresponding-iso-code>    # NEW for W4-B — REQUIRED on every BS page; value is the lowercase-kebab ISO code-id
superseded_by_note: "BSI-published form of ISO standard; not technically superseded — UK jurisdictional re-publication"  # OPTIONAL clarifier on BS-EN-ISO adoption pages
publisher_catalog_url: <https://knowledge.bsigroup.com/...>   # OPTIONAL — BSI Knowledge product page
sources:
  - <one or more /mnt/ace/O&G-Standards/BSI/... paths — pointer only, never quoted>
extraction_policy: metadata-only
raw_copy_allowed: false
bs_doc_number: <"BS EN ISO 13628-2" | "BS EN ISO 13533" | ...>
ledger_id: <"BS-EN-ISO-13628-2" | "BS-EN-ISO-13533" | ...>
---

# <Full BS document name>

## Scope (one paragraph, ≤80 words, paraphrased — never quoted)
<one-sentence scope summary>

## Why this page exists
Resolver target for digitalmodel `Citation` instances per
.claude/rules/calc-citation-contract.md. Contains no clause text.
The BS form is the BSI-published adoption of the ISO standard; cite
the ISO `code_id` for technical equivalence, this BS page for UK
jurisdictional / corrigendum traceability.

## Where to find the full text
- Raw PDF: <absolute /mnt/ace/O&G-Standards/BSI/... path> (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: <BSI Knowledge URL>
- ISO equivalent: <link to iso-... wiki page IF present, else ISO catalog URL>
- Internal callers: <relative path(s) under digitalmodel/src/, or "no live caller; future-needed">

## Cross-references
- [[<iso-counterpart-page>]] (when the ISO wiki page lands via W3-B)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
```

The test file will use a parametrized fixture iterating over the 8 page paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-2-flexible-pipe-subsea.md` | BSI-published form of ISO 13628-2 (unbonded flexible pipe). `superseded_by: iso-13628-2`. Corrigendum 1 (2001) tracked in `revision_amendments_note`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-3-tfl-systems.md` | BSI-published form of ISO 13628-3 (Through-Flowline systems). `superseded_by: iso-13628-3`. Two on-disk PDFs collapse into one wiki page (Corrigendum 1 only vs Corrigenda 1+2 are revisions of the same standard). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-5-subsea-umbilicals.md` | BSI-published form of ISO 13628-5 (subsea umbilicals). `superseded_by: iso-13628-5`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13628-8-rov-interfaces.md` | BSI-published form of ISO 13628-8 (ROV interfaces on subsea production systems). `superseded_by: iso-13628-8`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13533-drill-through-equipment.md` | BSI-published form of ISO 13533 (drill-through equipment / BOPs). `superseded_by: iso-13533`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13625-marine-drilling-riser-couplings.md` | BSI-published form of ISO 13625 (marine drilling riser couplings). `superseded_by: iso-13625`. |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13703-offshore-platform-piping.md` | BSI-published form of ISO 13703 (offshore-platform piping design & installation). `superseded_by: iso-13703-3` (the 2023 multi-part revision is the current ISO form; the 2001 BS form on disk is an older edition). |
| Create | `knowledge/wikis/engineering-standards/wiki/standards/bs-13626-drilling-well-servicing-structures.md` | BSI-published form of ISO 13626 (drilling and well-servicing structures). `superseded_by: iso-13626`. |
| Modify | `knowledge/wikis/engineering-standards/CLAUDE.md` | **NEW from r1 review M2** — extend the Standards-page extra-fields table to document the W4-B-introduced fields (`superseded_by`, `superseded_by_note`, `bs_doc_number`, `revision_amendments_note`, `publisher_full`, `ledger_id`, `publisher_catalog_url`). Without this the new fields are an undocumented schema fork; the documented `supersedes` field expresses the inverse direction (what this page replaces) — `superseded_by` is the opposite-polarity field needed for the BSI-jurisdictional-re-publication case. |
| Modify | `knowledge/wikis/engineering-standards/wiki/index.md` | Append "## Standards" rows for all 8; bump `page_count` per arithmetic AC (current + 8). |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 8 new rows with `id: BS-EN-ISO-13628-2` etc. (uppercase ledger form vs lowercase wiki form bridged via `ledger_id` frontmatter key, per W3-A pattern). |
| Create | `tests/knowledge/test_engineering_standards_bsi.py` | Test contract — inherits W3-A's 14 tests verbatim plus NEW `test_superseded_by_pointer_resolves`. |
| Update | `docs/plans/README.md` | Add W4-B row. |

---

## TDD Test List

All tests in a single file `tests/knowledge/test_engineering_standards_bsi.py`. Each test parametrized over the 8 page filenames.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_page_exists` | each of the 8 standards files is present | filename in `EXPECTED_PAGES` | file resolves under `wiki/standards/` |
| `test_frontmatter_has_code_id` | required key per `.claude/rules/calc-citation-contract.md` rule 2 | YAML frontmatter | `code_id` non-empty, lowercase-kebab; filename stem equals `code_id` verbatim |
| `test_frontmatter_has_publisher_bsi` | publisher discipline | YAML frontmatter | `publisher == "BSI"`; if present, `publisher_full == "British Standards Institution"` |
| `test_frontmatter_has_revision` | revision presence | YAML frontmatter | `revision` non-empty 4-digit-year string per W3-A revision-discipline (corrigenda enumerated separately in `revision_amendments_note`, NOT appended to `revision`) |
| `test_frontmatter_has_extraction_policy_metadata_only` | bounds enforcement | YAML frontmatter | `extraction_policy == "metadata-only"` and `raw_copy_allowed is False` |
| `test_frontmatter_has_jurisdiction_uk` | NEW for W4-B — every BS page is UK-published | YAML frontmatter | `jurisdiction == "UK"` |
| `test_frontmatter_has_bs_doc_number` | BSI-specific traceability | YAML frontmatter | `bs_doc_number` non-empty, starts with `"BS "` (e.g., `"BS EN ISO 13628-2"`, `"BS EN ISO 13533"`) |
| **`test_superseded_by_pointer_resolves`** | **NEW for W4-B — every BS page's `superseded_by` must point to a valid ISO/EN code-id** | YAML frontmatter | `superseded_by` non-empty, lowercase-kebab, starts with `"iso-"` OR `"en-iso-"`; AND value satisfies one of: (a) wiki page at `knowledge/wikis/*/wiki/standards/<superseded_by>.md` exists, OR (b) **(STRENGTHENED per r1 review M3)** `publisher_catalog_url` frontmatter key is present, the URL host is `bsigroup.com` OR `iso.org` OR `knowledge.bsigroup.com`, AND the URL contains the numeric code extracted from the `superseded_by` value (e.g., `superseded_by: iso-13628-2` → URL must contain the substring `13628`). Plain "non-empty URL" is NOT sufficient. The OR is necessary because ISO counterpart wiki pages may not yet exist (W3-B may close that gap). If neither (a) nor the strengthened (b) is achievable for a given page, the test marks that page parametrization `xfail` with `reason="W3-B ISO 13xxx pages not yet present; pointer resolution structural-only"` so the weakness is explicit, not silent. |
| **`test_frontmatter_has_superseded_by_note_when_bs_en_iso`** | **NEW for W4-B per r1 review M4 — machine-enforce the BS-EN-ISO classification distinction** | YAML frontmatter | if `bs_doc_number` starts with `"BS EN ISO"`, then `superseded_by_note` is present AND its value contains either the substring `"jurisdictional re-publication"` OR `"not technically superseded"`. This is the load-bearing field distinguishing "BSI-published form of the ISO standard" from "obsolete prior edition" — must not be human-review-only. |
| `test_no_raw_pdf_text_bleed_through` | denylist guard (BSI-specific phrase set) | page body | none of `RAW_TELLTALE_PHRASES` present |
| `test_body_word_count_bounded` | strict `<500` ceiling matching W1-A / W2-A / W3-A | page body | `0 < word_count < 500` strict on both bounds; constant imported from W3-A's test file when present, else `MAX_BODY_WORDS = 500` locally |
| `test_body_structure_is_whitelisted_only` | positive-shape | page body | top-level `##` headings ⊆ `{"Scope", "Why this page exists", "Where to find the full text", "Cross-references"}` |
| `test_links_only_pointer_to_mnt_ace` | the page mentions the raw path but does not embed clause text | page body | regex `/mnt/ace/O&G-Standards/BSI/` present in a "Where to find" section |
| `test_citation_schema_resolvable` | downstream resolver — actually reads the wiki page | invoke resolver for each new page | resolver returns matching `code_id`/`publisher`/`revision`; `CitationResolutionError` not raised |
| `test_ledger_alignment` | every page's `ledger_id` frontmatter resolves to a row in `standards-transfer-ledger.yaml` | wiki frontmatter `ledger_id` | matching `id:` row found in ledger YAML |
| `test_code_id_unique_across_wiki_domains` | inherited from W2-A AC | every `code_id` in `knowledge/wikis/*/wiki/standards/*.md` | no duplicates |
| `test_index_lists_all_eight` | wiki index updated | `index.md` contents | each of the 8 page links present in the "## Standards" section |

`RAW_TELLTALE_PHRASES` will be a small, narrowly-scoped list (≤15 entries) drawn from BSI publication conventions — e.g. `"389 Chiswick High Road, London W4 4AL"`, `"© BSI"`, `"© British Standards Institution"`, `"BSI is incorporated by Royal Charter"`, `"Reproduction except as permitted by the Copyright"`, `"BSI is the national body responsible"`, `"This British Standard, having been prepared under the direction"`, `"Permission to reproduce extracts"`, `"BSI 389 Chiswick"`, `"shop.bsigroup.com"` (cover-page link only — context-aware exclusion when reference is to publisher-catalog URL). The list will deliberately exclude BS document numbers (`BS 13628`, `BS EN ISO 13628-2` — required) and the document title (paraphrase allowed). The BSI-specific list will NOT overlap with the API / DNV / ABS / OCIMF denylists. **Honesty caveat (inherited from W3-A):** the denylist alone will NOT catch a 100-200-word verbatim clause copy; reviewers MUST manually inspect every revision. Shingle-match / cosine-similarity follow-up deferred.

---

## Acceptance Criteria

- [ ] All 8 new wiki pages exist at the prescribed paths.
- [ ] `uv run pytest tests/knowledge/test_engineering_standards_bsi.py -v` passes (all parametrized cases green).
- [ ] No regression: `uv run pytest tests/knowledge/ -v` passes.
- [ ] `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes — the W4-B plan stays within the W3-C erratum allowlist (every #2471 mention is adjacent to a CSA-Z276 / W3-C erratum / over-citation / scope token).
- [ ] **PLANS_GLOB regression-coverage AC (NEW from r1 review M1):** before W4-B implementation lands, `tests/governance/test_2471_citation_scope.py` MUST be updated so the regression net actually scans 2026-05-03 plans. Resolution options (any one): (a) generalize `PLANS_GLOB` to `docs/plans/2026-05-0[2-9]-*.md` (or `docs/plans/2026-05-*.md`), OR (b) add an explicit per-plan test (`test_w4b_scope_compliance` matching the existing `test_w1a_amendment_landed` / `test_w1b_amendment_landed` / `test_w2c_amendment_landed` precedents) pinning this plan path. Without this update the W4-B `#2471`-discipline AC above is vacuous because the test glob is hard-coded to `2026-05-02-*.md`.
- [ ] No raw-PDF clause text is committed: `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/bs-*.md` contains zero matches for `RAW_TELLTALE_PHRASES`.
- [ ] Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema (`code_id`, `publisher`, `revision` populated; `code_id` lowercase-kebab; filename stem equals `code_id` verbatim).
- [ ] Frontmatter for every new page carries `jurisdiction: UK`, `superseded_by: <iso-code-id>`, and `bs_doc_number` (W4-B-specific contract).
- [ ] **`superseded_by_note` AC (NEW from r1 review M4):** for every page where `bs_doc_number` starts with `"BS EN ISO"`, the `superseded_by_note` frontmatter field is present and contains either the substring `"jurisdictional re-publication"` OR `"not technically superseded"`. Enforced by `test_frontmatter_has_superseded_by_note_when_bs_en_iso` — NOT delegated to human review.
- [ ] **`superseded_by` pointer-resolution AC (NEW for W4-B, STRENGTHENED per r1 review M3):** for each of the 8 pages, EITHER (a) the target ISO wiki page exists at `knowledge/wikis/*/wiki/standards/<superseded_by>.md` OR (b) the page carries a `publisher_catalog_url` frontmatter key whose URL host is `bsigroup.com` / `knowledge.bsigroup.com` / `iso.org` AND whose URL string contains the numeric code from the `superseded_by` value. Plain "non-empty URL" is NOT sufficient. The test enforces the strengthened OR; AC enforces the presence of at least one of the two anchors.
- [ ] Citation downstream-resolution check (per W3-A AC inheritance — literal-equality on the revision string): for each page where a real publisher revision is asserted, `Citation(code_id=..., publisher='BSI', revision=<frontmatter-revision-verbatim>, ...)` succeeds without `CitationResolutionError`. Pages whose ISO supersession is unverifiable at write-time MUST set `revision: "public-metadata-required-before-citation-use"` and be excluded from this check via `pytest.mark.skip`. **m4 from r1 review:** in practice, all 8 W4-B priority pages have on-disk-confirmed revision years (2001 / 2002 / 2004) drawn from the BSI PDF filenames, so this placeholder fallback is defensive-only and SHOULD NOT trigger for any page in this batch. The clause is retained as a safety net for downstream W4-x batches where on-disk evidence may be weaker.
- [ ] **Revision-discipline-for-BS-EN-ISO pages (W3-A inheritance):** `revision` is a 4-digit base year string with NO corrigendum/amendment suffix. Corrigenda enumerated via `revision_amendments_note` (free text) and via the `sources` frontmatter list (one path per corrigendum PDF on disk). Example: `bs-13628-3-tfl-systems.md` uses `revision: "2001"` and `revision_amendments_note: "Corrigendum 1 (2001); Corrigenda 1+2 (later)"` plus two `sources` entries.
- [ ] Ledger alignment: every page's `ledger_id` frontmatter resolves to a row in `data/document-index/standards-transfer-ledger.yaml` (8 new rows added by this plan; existing `BS-7608` row is unaffected). Ledger-form / wiki-form ID divergence bridged via `ledger_id` per W3-A pattern.
- [ ] `knowledge/wikis/engineering-standards/wiki/index.md` lists all 8 new pages under "## Standards". **Arithmetic AC:** `page_count` after this plan = (current `page_count` at implementation time) + 8. **Implementer note (m1 from r1 review):** the current value is 5 at plan-time (2026-05-02), but W4-A/W4-C/W4-D and W3-A may land before W4-B; the implementer MUST read the live `page_count` at write-time and add 8 — do NOT assume `5 + 8 = 13`.
- [ ] No file under `knowledge/wikis/engineering-standards/wiki/sources/` is modified.
- [ ] No file under `knowledge/wikis/engineering/wiki/standards/` is modified — verified there are NO pre-existing BS pages anywhere; if a future contributor preempts W4-B, this plan MUST be re-scoped before merge.
- [ ] `code_id` uniqueness across wiki domains: the test asserts no duplicates across `knowledge/wikis/*/wiki/standards/*.md` (vacuous-but-protective for BS today).
- [ ] Plan review artifact present at `scripts/review/results/2026-05-03-plan-W4B-claude-internal.md` (single-author Claude review acceptable per memory `feedback_permission_gate_blocks_cross_review.md`). Codex/Gemini unavailable. If Codex 0.123.0 downgrade lands before implementation, a v2 review SHOULD be dispatched as non-blocking.
- [ ] Adversarial review explicitly addresses (a) the BS-EN-ISO-vs-superseded distinction (every page must be classified correctly: jurisdictional re-publication vs technically superseded older edition), (b) the duplicate BS 13628 Pt 3 PDFs collapsing into one wiki page, and (c) confirmation that all #2471 mentions stay within the W3-C allowlist proximity.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR -> revised | 4 MAJOR + 6 MINOR — all addressed inline |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (4 MAJOR + 6 MINOR fixes applied 2026-05-03)

**Revisions made based on review:**
- M1 — added explicit AC requiring `tests/governance/test_2471_citation_scope.py` `PLANS_GLOB` generalization (or per-plan W4-B test) so the regression net actually scans 2026-05-03 plans; without this the #2471-discipline AC was vacuous.
- M2 — added Files-to-Change row for `knowledge/wikis/engineering-standards/CLAUDE.md` to document the W4-B-introduced frontmatter fields (`superseded_by`, `superseded_by_note`, `bs_doc_number`, `revision_amendments_note`, `publisher_full`, `ledger_id`, `publisher_catalog_url`) — closes the schema-fork against the existing inverse-direction `supersedes` field.
- M3 — strengthened `test_superseded_by_pointer_resolves` clause (b) from "non-empty URL" to "URL host is `bsigroup.com` / `knowledge.bsigroup.com` / `iso.org` AND URL contains numeric code from `superseded_by`"; added documented `xfail` fallback when neither (a) nor (b) is achievable.
- M4 — promoted `superseded_by_note` from human-review-only to a machine-enforced contract via new `test_frontmatter_has_superseded_by_note_when_bs_en_iso` test plus matching AC; the BS-EN-ISO-vs-superseded distinction is no longer hidden behind reviewer attention.
- m1 — left arithmetic AC unchanged but added explicit reminder that implementer reads current `page_count` at write-time (not assume `5+8`).
- m2 — clarified the 76-vs-49 file-count reconciliation prose (case-sensitive `BS_*` glob vs full directory listing).
- m3 — collapsed `tags` to single-publisher token: `["bsi", "standards", ...]` (drop `"british-standards"` to match W3-A precedent).
- m4 — annotated the `revision: "public-metadata-required-before-citation-use"` placeholder as defensive-only paste-through; in practice all 8 W4-B pages have on-disk-confirmed revision years.
- m5 — removed the meta-prose `<!-- Distinct sources counted: ... -->` HTML comment.
- m6 — corrected the T2-justification phrasing from "≥16 parametrized assertions × 8 pages ≈ 128 effective test cases" to "16 distinct test functions × 8 page params = 128 pytest invocations".

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk (load-bearing for W4-B):** BS-EN-ISO-vs-superseded conflation. The 8 BS PDFs on disk were filed under `BSI/` with `BS_xxxx_*` filenames, but their published form is `BS EN ISO xxxx` (BSI-published adoption of ISO standards via CEN ratification). Cataloguing these as "superseded by" their ISO counterpart is **technically misleading** — the BS form is the same standard, jurisdictionally re-published. **Mitigation:** every BS page MUST carry `superseded_by_note: "BSI-published form of ISO standard; not technically superseded — UK jurisdictional re-publication"` for the BS-EN-ISO adoption case; `superseded_by_note` is OMITTED (or set to a different free-text string) only for the rare BS-without-ISO-equivalent case (none in the W4-B priority 8). Reviewer must verify the note text is present on every page during plan-review.
- **Risk (NEW for W4-B):** ISO counterpart wiki pages do not yet exist. `find ... -name "iso-1362*.md"` returns zero matches in `wiki/standards/`. **Mitigation:** `test_superseded_by_pointer_resolves` accepts EITHER a wiki-internal link OR a `publisher_catalog_url` pointer to BSI Knowledge / ISO catalog. W3-B (#2595) may land ISO 19900-series pages but will NOT cover the 13xxx family at the same rate; W4-B does NOT block on W3-B.
- **Risk:** Multiple BS 13628 parts share a code-id stem. Pt 2 / Pt 3 / Pt 5 / Pt 8 are distinct standards under the same code base. **Mitigation:** the lowercase-kebab `code_id` form encodes the part: `bs-13628-2`, `bs-13628-3`, `bs-13628-5`, `bs-13628-8`. The `bs_doc_number` frontmatter carries the published form (`"BS EN ISO 13628-2"`). The `superseded_by` mirrors: `iso-13628-2`, `iso-13628-3`, `iso-13628-5`, `iso-13628-8`. No collision.
- **Risk:** Duplicate on-disk PDFs. Two BS 13628 Pt 3 PDFs exist (Corrigendum 1 only and Corrigenda 1+2). **Mitigation:** both PDFs collapse into ONE wiki page (`bs-13628-3-tfl-systems.md`); both `/mnt/ace` paths listed in the `sources` frontmatter; the test asserts `len(sources) >= 1`, NOT exactly 1. The `revision_amendments_note` lists both corrigenda explicitly.
- **Risk:** BS revision lifecycle. BS standards receive amendments and corrigenda that the ISO form may not (and vice versa). The 2001 BS 13703 form on disk is older than the current ISO 13703-3:2023 multi-part split. **Mitigation:** `revision: "2001"` pins the BS edition on disk; `superseded_by: iso-13703-3` points to the current ISO form; `superseded_by_note` clarifies the ISO has split into Pt 1/2/3 since 2001. Calc-callers using BS 13703 should be aware they are citing a historical edition.
- **Risk:** BS EN aliases. Some BS standards are re-published as `BS EN ISO` (CEN-ratified) AND as standalone `BS ISO` (BSI-only adoption). The on-disk filenames use the short `BS_<num>` form which is ambiguous. **Mitigation:** `bs_doc_number` frontmatter carries the verified published form (`"BS EN ISO 13628-2"`), confirmed via BSI Knowledge product page during write-time. If BSI Knowledge is unreachable for a given page, the page MUST set `revision: "public-metadata-required-before-citation-use"` and skip the citation-resolvability test.
- **Risk:** Copyright leakage. BSI publishes from London (389 Chiswick High Road, London W4 4AL) with cover-page strings "© BSI" / "© British Standards Institution" / "BSI is incorporated by Royal Charter". **Mitigation (inherited from W3-A):** word-count ceiling `<500` strict + positive-shape structural test + `extraction_policy: metadata-only` + `raw_copy_allowed: false` + cross-review on every revision. **Honesty caveat:** denylist alone is necessary-but-not-sufficient.
- **Risk:** Cross-wiki duplication. ZERO pre-existing BS pages exist anywhere in `knowledge/wikis/*/wiki/standards/` (verified via `find`). The 5x-collision risk does NOT apply.
- **Risk:** Test-suite drift between W3-A and W4-B. W4-B inherits 14 tests from W3-A and adds 1 new test (`test_superseded_by_pointer_resolves`) plus 1 modified test (`test_frontmatter_has_publisher_bsi` instead of `test_frontmatter_has_publisher_abs`). **Mitigation:** the W4-B test file imports `MAX_BODY_WORDS` from W3-A's test file when present (single source of truth); if W3-A has not yet landed at implementation time, define locally with a `# TODO: migrate to shared constant once W3-A lands` comment. The pattern is W3-A → W4-B inheritance, not W4-B forking the W3-A contract.
- **Open:** **Should superseded BS standards be promoted at all if the ISO counterpart exists?** The W4-B answer is YES, on the historical-context-and-corrigendum-tracking value-add (UK jurisdiction notes, BSI corrigenda not always carried into ISO, on-disk file traceability for audit purposes). However, if user prefers ISO-only promotion via W3-B (#2595) and BS pages reduced to single-line redirects, W4-B should be re-scoped or cancelled in favor of expanded W3-B coverage. **User decision required during plan-review.**
- **Open:** Should W4-B include BS 13535 (hoisting equipment) and BS 13678 (downhole compounds)? Both are on disk under BS 13xxx but cover lifting/material-test scope rather than the "subsea/drilling/platform-piping" subset proposed for W4-B. Defer to W4-C follow-up unless user expands scope.
- **Open:** Issue title and labels. Proposed title: `feat(llm-wiki): bounded BSI offshore-petroleum subset summary promotion (W4-B)`. Proposed labels: `priority:medium,cat:documentation,domain:knowledge-management,domain:standards`. Issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md` and is NOT performed by this plan.
- **Open:** Should the test file live at `tests/knowledge/test_engineering_standards_bsi.py` (one file, parametrized) or be split per-page? The single-file form is proposed for tractability and matches W3-A.

---

## Complexity: T2

**T2** — multi-file documentation work (8 new wiki pages + 1 test file + 1 index update + 1 ledger update + 1 engineering-standards/CLAUDE.md schema-extension update + 1 docs/plans/README.md update = 13 files), no new code modules, but a real test contract (16 distinct parametrized test functions × 8 page parameters = 128 pytest invocations — m6 phrasing fix from r1 review). Implementation is templated repetition; design risk is concentrated in (a) the BS-EN-ISO-vs-superseded distinction (every page classified correctly), (b) the new `superseded_by` resolution test (must accept either wiki-internal link or publisher-catalog URL), (c) duplicate-PDF collapse for BS 13628 Pt 3, and (d) staying within the W3-C erratum #2471 allowlist proximity. Matches W3-A T2 sizing (8 pages vs W3-A's 10 pages — slight reduction to absorb the `superseded_by` complexity without spilling into T3).
