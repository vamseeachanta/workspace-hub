# Adversarial Review — Plan #2587 (Asset-Management LLM-Wiki W1-B)

**Reviewer:** Claude (single-author internal)
**Provenance:** Codex unavailable (codex-cli 0.124.0 stdin-hang regression — `feedback_codex_cli_0_124_upstream_regression.md`); Gemini sandbox failure (sparse-overlay blindness — `feedback_gemini_sandbox_overlay_blindness.md`); single-author Claude per `feedback_permission_gate_blocks_cross_review.md`.
**Date:** 2026-05-02
**Plan:** `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md`
**Issue:** #2587
**Verdict:** MAJOR

---

## Affirmatively verified

- **Plan read in full** (lines 1–287). All sections present: Resource Intel, Artifact Map, Deliverable, Pseudocode, Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review Summary (placeholder), Risks, Complexity.
- **Issue states verified** via `gh issue view`:
  - `#2540` OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" (matches plan claim)
  - `#2471` CLOSED — CSA Z276 routing decision (matches plan claim)
  - `#2482` CLOSED — vendor-derivative deny-list (matches plan claim)
  - `#2541` OPEN, `#2542` CLOSED, `#2543` CLOSED, `#2544` CLOSED, `#2559` OPEN, `#2587` OPEN
- **File existence verified** via `ls`:
  - `knowledge/wikis/asset-management/CLAUDE.md` EXISTS (read in full — 119 lines; schema matches plan claims about frontmatter + standards-page extras)
  - `knowledge/wikis/asset-management/wiki/index.md`, `log.md`, `overview.md` all EXIST
  - `knowledge/wikis/asset-management/wiki/sources/elements-assethold-casa-grande-77017.md` EXISTS (verified frontmatter; tagged `casa-grande`, source = `/mnt/ace/assethold/casa-grande-77017`)
  - All five empty subdirs (`concepts/`, `entities/`, `standards/`, `comparisons/`, `visualizations/`) EXIST and are empty — plan's "blank slate" claim is accurate
  - `knowledge/wikis/cross-links.md` EXISTS; `grep -i asset` returns header rows referencing engineering+marine-engineering pairs but NO row sourced from or targeting asset-management wiki (plan claim is accurate)
  - `.claude/rules/calc-citation-contract.md` EXISTS
  - `docs/plans/_template-issue-plan.md`, `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`, `docs/plans/2026-04-19-claude-llm-wiki-roadmap-review-prompt.md`, `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` all EXIST
  - `knowledge/wikis/engineering/wiki/standards/` peer pattern verified: 8 standards files including `ocimf-tandem-mooring.md`
- **Scope-boundary claim verified**: `ls /mnt/ace/assethold/` returns `casa-grande-77017` and `data`. Inspection of `casa-grande-77017/` shows: `Offering MemorandumCasa Grande OM 3.pdf`, `Operating and FinancialsCasa Grande Rent Roll.xlsx`, `Operating and FinancialsNov 2025 Trailing 12.xlsx`, `_from_elements/`. `data/` contains `sandsig-cre-listings`. This is unambiguously commercial-real-estate / financial-portfolio scope — plan's scope-boundary thesis is well-grounded. Note: there is no README at the assethold root or property-dir level, so the plan's framing rests on the artefact filenames alone (offering memorandum, rent roll, T12) — this is sufficient.
- **Past-tense drift scan** (`grep -nE "(was|were|added|created|completed|implemented) "`) — only one row, line 25, "Will be added under" (future tense). No drift.
- **Future-tense compliance**: `grep -c "will"` returns 9 occurrences; tone is consistent future-tense throughout.

---

## Findings — MAJOR

### M1. IAM Competency Framework misclassified as "publisher-issued reference doc" — abuses `wiki/standards/` slot

Plan line 32 and Files-to-Change row at line ~ Standards table (`wiki/standards/iam-competency-framework.md`) treat IAM CF as if it slots cleanly into the #2471-sanctioned `wiki/standards/<code-id>.md` route. **It does not.** #2471 routing requires `code_id`, `publisher`, **`revision`** frontmatter for "code-identified pages"; the contract was written for codes (CSA Z276, API 17J, OCIMF MEG4 etc.) with discrete revisions and an issuing standards body. The IAM Competency Framework v3.0 is a competency curriculum / training-design reference, not a code or specification. There is no "violation of IAM CF" that an engineer can be cited for.

The plan acknowledges the strain by parenthetically writing "treating IAM CF as a publisher-issued reference doc" — that aside is a tell. If the reviewer needs to defend the routing in prose, the routing is wrong.

**Concrete defects this creates:**
- `test_every_standards_page_has_code_id_publisher_revision` will demand a `code_id` + `revision` for IAM CF; the plan offers no canonical `code_id` for a curriculum (`iam-cf-v3` is invented, not publisher-assigned).
- A future agent linting `wiki/standards/` will treat IAM CF as audit-grade source and may cite it for compliance claims.

**Recommended fix:** route IAM CF as a **concept page** (`wiki/concepts/iam-competency-model.md` — already in the concepts list at line 204, so this is already ambivalent in the plan!) and **drop `wiki/standards/iam-competency-framework.md`**. The Standards table on lines 23–32 should be reduced to 7 rows (ISO 55000/55001/55002, API RP 580/581, API 579-1, DNV-RP-G101, NORSOK Z-008, HSE SCR15 — 8 once HSE SCR15 is included; see M2). This fixes the abuse and removes a duplicated topic.

### M2. Standards-table count mismatch with Files-to-Change list — HSE SCR15 silently dropped

Plan Standards ledger (lines 23–32) lists **8 standards** including `hse-scr-2015.md` at line 31. But the Files-to-Change table (lines 211–218) lists only **8 standards files** of which **HSE SCR15 is missing**: ISO 55000/55001/55002, API RP 580/581, DNV-RP-G101, NORSOK Z-008, API 579-1 = 8. HSE SCR15 dropped; IAM CF dropped (the latter is correct per M1, but unstated).

Acceptance criterion at line 251 says "All 8 standards pages carry `code_id`, `publisher`, `revision`" — but the standards ledger advertises 8 distinct codes (excluding IAM CF) **including** HSE SCR15. So the plan is internally inconsistent on which 8 are scaffolded.

**Concrete defect:** if the implementer follows the Files-to-Change list, `hse-scr-2015.md` will not be created, but the Risk register line 276 explicitly lists "HSE" in the topic mix, and `concepts/safety-critical-element-classification.md` (line 202) per its theme MUST link to SCR15 — `test_concept_pages_link_to_standards_pages` will then fail because the SCE classification page can't link to a non-existent standards page.

**Recommended fix:** add `Create | knowledge/wikis/asset-management/wiki/standards/hse-scr-2015.md | #2471-routed standards page` row to Files-to-Change, and explicitly state that IAM CF is intentionally NOT in standards/ (per M1).

### M3. Missing canonical references — ISO 31000, PAS 55, BS EN 16646 — Western-bias risk register entry is itself biased

Plan line 276 acknowledges Western-standards bias (Brazil ANP / Australia NOPSEMA / West Africa) and defers to follow-up. **But the plan also omits canonical Western references that should be in W1-B by name:**

- **ISO 31000:2018 (Risk management — Guidelines)** — this is the parent risk-management methodology that ISO 55001 §6 cross-references; without it, the RBI / ALARP / SCE-classification concept pages cannot ground their risk vocabulary in a single canonical source. ISO/IEC 31010 (risk-assessment techniques) is the methodology companion. **Verified absent**: `grep -rn "ISO 31000" knowledge/wikis/` returns zero results.
- **PAS 55-1/-2:2008 (BSI)** — superseded by ISO 55001 but still operationally cited in pre-2014 contracts and audit reports; concept pages on asset-register / asset-lifecycle should at minimum mention PAS 55 as the precursor and reference the ISO-55000-supersession. Verified absent.
- **BS EN 16646:2014 (Maintenance — Maintenance within physical asset management)** — CEN-published bridge between EN-13306 maintenance vocabulary and ISO 55000; without it, the integrity-management-cycle concept lacks a maintenance-side anchor. Verified absent.

Risk-register language on line 276 frames this as Brazil/Australia/West-Africa — those are real gaps but **the plan's own Western-canon list is incomplete first**. A reviewer reading only the risk register would be misled into thinking the Western coverage is exhaustive.

**Concrete defect:** ISO 31000 is missing not as a deferred follow-up but as a **first-class W1-B page** because three of the listed concept topics (ALARP, RBI, SCE classification) inherit terminology directly from ISO 31000.

**Recommended fix:** add at minimum `wiki/standards/iso-31000.md` to the standards backbone for W1-B; add PAS 55 + BS EN 16646 either to W1-B or to an explicit "deferred to W1-C" sub-list with a named follow-up issue number. Update the risk-register line to acknowledge "Western canon is also incomplete in W1-B (PAS 55, BS EN 16646)."

---

## Findings — MINOR

### m1. Review-artifact naming mismatch

Plan line 8 advertises "Review artifacts: scripts/review/results/2026-05-02-plan-W1-asset-management-claude.md | ...-codex.md | ...-gemini.md" and Artifact Map rows at lines 123–125 repeat that path. **But this review file is being written to** `2026-05-02-plan-2587-claude-internal.md` per the prompt contract. The plan should match the actually-emitted filename or vice versa. The Codex/Gemini rows are stale because (a) Codex cannot run (CLI regression), (b) Gemini sandbox blind to overlay — neither artifact will ever exist. Plan should be updated to mark Codex/Gemini rows as "unavailable" with the memory-feedback citations, not as TBD.

### m2. Concept-list overlap with engineering wiki — fragmentation risk under-stated

Plan line 277 raises "term overlap with reliability engineering" as a Risk and proposes cross-links as mitigation. But concept pages **already exist in the engineering wiki** for several of the proposed asset-management concepts (e.g., engineering wiki has `pipeline-integrity-assessment`, `cathodic-protection-design`, `viv-riser-fatigue` among standards-cross-linked concepts per `cross-links.md`). The plan does not enumerate which engineering-wiki concept pages will need bidirectional cross-links to the new asset-management pages. Without that enumeration, the `test_concept_pages_link_to_standards_pages` (asset-mgmt-internal links) will pass while `cross-links.md` (cross-wiki) will remain empty for asset-management.

**Recommended fix:** add a TDD test `test_asset_management_appears_in_cross_links_md` that asserts ≥1 row in `knowledge/wikis/cross-links.md` sourced from or targeting `knowledge/wikis/asset-management/`. Without this test, the "Risk — term overlap" mitigation is not load-bearing.

### m3. Test-theater risk: TDD contract is shape-only, not content-aware

The TDD list (lines 228–242) checks structural shape — frontmatter present, `## Scope` heading present, ≥1 cross-link present, scope-boundary literal-phrase match. **A malformed but well-shaped page passes every test:**

- `test_every_concept_page_has_yaml_frontmatter` accepts a page where `tags: ["asset-management", "engineering-scope"]` is present but the body is one sentence of nonsense.
- `test_every_new_page_has_at_least_one_cross_link` is satisfied by a single self-loop `[Scope](#scope)` markdown anchor (which is also a markdown link).
- `test_concept_pages_link_to_standards_pages` requires ≥8 of 12 concept pages link to a `wiki/standards/<code-id>.md` page — but doesn't verify the *target* page exists. A broken link `[ISO 55000](../standards/iso-55000.md)` on a concept page passes whether or not `iso-55000.md` exists.

**Recommended fix (incremental, not blocking):** add `test_all_internal_links_resolve` that walks every concept-page link to a `wiki/standards/...md` target and asserts the target file exists. This converts "link present" from shape-test to content-test.

### m4. Page-count: 12 concepts is plausible but lifecycle concept overlaps with ISO-55000-family

`asset-lifecycle.md` (line 200) and `iso-55000-family-overview.md` (line 203) will both cover the asset-lifecycle topic — ISO 55000 §3.1 defines it as a foundational term. Risk of duplication / contradiction between two pages without one being labeled the canonical authority. Marginal — not blocking.

### m5. Casa Grande source-page coupling implicitly hidden

Plan claims (line 18, 49) that this scaffold "deliberately does NOT consume" the Casa Grande corpus. **But** `wiki/index.md` `source_count: 1` (verified) and the existing source page is Casa Grande. The new scope-boundary disclaimer must explicitly state that the existing source page **does not** authorize concept-page material — i.e., the scaffold pages emerge from external publisher sources only, not from the Casa Grande corpus. The plan's pseudocode (lines 152, 170) does state `# publisher pages, not vendor copy` as a comment but does not lift that into the test contract. A future ingest agent reading only the test list and ignoring the comments could write a concept page citing Casa Grande and pass `test_no_vendor_derivative_citation_in_concept_pages` (the test scopes `wiki/sources/` paths, not the underlying corpus).

**Recommended fix:** strengthen `test_no_vendor_derivative_citation_in_concept_pages` to deny any reference to `casa-grande` or `assethold` slug-tokens in concept-page bodies, not just `wiki/sources/` path-references.

### m6. Two open questions deferred to user-approval gate but not scoped to a follow-up issue

Lines 280–281: "Flag for user during plan approval." Both items (performance-management page placement and ISO 55000 family granularity) are legitimate questions. But they are not tracked to a GitHub follow-up issue if user approves the plan as-is. Without a follow-up issue, the deferred decisions evaporate at merge time.

**Recommended fix:** if user approves the proposed defaults, file a single follow-up issue capturing the two deferred decisions and their resolution.

---

## Notes

- **Plan uses correct future-tense throughout** — no past-tense artefact-claim drift.
- **#2471 routing is correctly applied** for ISO/API/DNV/NORSOK/API-579 entries. Only IAM CF is mis-routed (M1).
- **Source-count integrity**: plan claims ≥3 distinct external sources at line 109 ("≥ 3 minimum"); the External-sources block lists 6+ distinct standards/frameworks. Compliant.
- **Manual-review checkbox pattern** (lines 224, 252–253) is sound — converts topical-curation risk into an explicit gate. Good pattern.
- **Pseudocode** (lines 137–191) mostly matches Files-to-Change list and TDD list, but the standards-loop pseudocode at line 158 says "for code in STANDARDS_BACKBONE" without enumerating the size of `STANDARDS_BACKBONE`; if M2 is fixed (HSE SCR15 added), this loop runs 9 times not 8.
- **#2482 deny-list correctly cited** — `wiki/sources/` not citable from concept/standards pages.
- **CLAUDE.md schema verified** matches the plan's frontmatter contract (title/tags/added/last_updated required; standards extras `code_id`/`publisher`/`revision` required at L0 prose). Plan accurately reflects schema.

---

## Reviewer's checklist

- [x] ≥3 sources verified (issues `#2540`, `#2471`, `#2482`, `#2541-2544`, `#2559`, `#2587`; files `CLAUDE.md`, `index.md`, `cross-links.md`, `calc-citation-contract.md`, peer engineering-wiki standards/ dir; `/mnt/ace/assethold/` directory listing)
- [x] Full plan read (287 lines)
- [x] Past-tense drift hunted (one false-positive at line 25 "will be added")
- [x] Hidden assumptions hunted (IAM CF routing, HSE SCR15 silent drop, ISO 31000 omission, Casa Grande corpus coupling)
- [x] No praise; no restatement
- [x] Evidence inline (commands and observations cited per-finding)

---

**Verdict: MAJOR** — 3 MAJOR (IAM CF mis-routing as standards page; HSE SCR15 silently dropped from Files-to-Change creating internal inconsistency; ISO 31000 / PAS 55 / BS EN 16646 missing from Western-canon). Plan is structurally strong, scope-boundary thesis is well-evidenced, and TDD shape is reasonable; but Standards table internal inconsistency and IAM-CF routing abuse must be resolved before plan-approval.
