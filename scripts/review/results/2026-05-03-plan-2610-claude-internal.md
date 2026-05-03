# Adversarial Review — Plan #2610 (W5-A NORSOK Bounded Summary Promotion)

- **Plan:** `docs/plans/2026-05-03-issue-2610-llm-wiki-W5A-engineering-standards-norsok.md`
- **Issue:** #2610 (not yet filed per plan; planning-only)
- **Date:** 2026-05-03
- **Reviewer:** Claude (single-author r1, internal)
- **Codex:** UNAVAILABLE — codex-cli 0.124.0 stdin-hang regression (#2479) per memory `feedback_codex_cli_0_124_upstream_regression.md`
- **Gemini:** UNAVAILABLE — sandbox `cwd=/tmp` blocks workspace-hub overlay reads per memory `feedback_gemini_sandbox_overlay_blindness.md`
- **Stance:** Adversarial; defects until proven otherwise; APPROVE only after affirmative verification.

## Verdict

**MAJOR** — 2 P1 defects, 5 P2/P3 minor findings.

The plan is well-scoped, internally honest about most known mismatches (M-506 absent, Z-008 absent, edition-vs-publisher-current gap, allowlist guardrail glob limitation), and inherits a mature shape from W4-A/W4-B precedents. However, two substantive accuracy defects MUST be corrected before plan-approved:

1. The D-SR-022 `superseded_by` migration target (plan claims "ISO 13533 (drill-through equipment — also on-disk per W4-B BSI plan)") is wrong on both counts — ISO 13533 covers drill-through equipment NOT BOP/diverter/riser, and it is not on /mnt/ace.
2. The `superseded_by` field-name choice contradicts the plan's own Risk #6 acknowledgement that NORSOK→ISO is parallel/mirror, not supersession; the field name perpetuates the imprecise framing the plan elsewhere disavows, and the ISO-mirror cases (N-001, N-004, M-001, M-501, M-710) will all carry a misleading-by-construction key.

---

## Verification Performed

| Check | Result |
|---|---|
| Allowlist guardrail (`uv run pytest tests/governance/test_2471_citation_scope.py`) | **PASS** — 6 passed in 0.28s. Plan's claim of `PLANS_GLOB = "docs/plans/2026-05-02-*.md"` (does NOT scan 2026-05-03) is correct: verified at `tests/governance/test_2471_citation_scope.py:23`. Plan's compliance is therefore prose-only for now; explicitly admitted at lines 11, 115, 334. |
| On-disk NORSOK PDF count (claimed 9) | **PASS** — `find /mnt/ace/O&G-Standards/Norsok -type f \( -iname "*.pdf" \)` returns exactly 9 files matching the plan's enumeration at lines 100-109. |
| 6 picks have on-disk PDFs (N-001, N-004, M-001, M-501, M-710, D-SR-022) | **PASS** — all six codes resolve to on-disk PDFs; multi-edition pairs for N-001 (2004+2010), N-004 (1998+2004), M-501 (1999+2004) all present. |
| Z-008 absent claim | **PASS** — `find ... -iname "*Z-008*"` returns empty. Plan correctly admits at lines 9, 45, 82. |
| M-506 absent claim | **PASS** — `find ... -iname "*M-506*"` returns empty. Plan correctly admits at lines 27, 83, 126. |
| Cited issues #2540, #2587, #2596, #2599 | **PASS** — `gh issue view`: #2540 CLOSED ("epic(llm-wiki): overnight Elements corpus planning wave"), #2587 OPEN (W1-B asset-management; body explicitly flags NORSOK Z-008), #2596 OPEN (W3-C #2471 erratum), #2599 OPEN (W4-A NACE), #2586 OPEN (W1-A API), #2590 OPEN (W2-A DNV), #2594 OPEN (W3-A ABS), #2471 CLOSED, #2482 CLOSED, #2481 CLOSED. All 10 issues cited with correct status. |
| `tests/governance/test_2471_citation_scope.py` exists | **PASS** — file exists; PLANS_GLOB confirmed `docs/plans/2026-05-02-*.md`. |
| Index `page_count: 5` drift claim | **PASS** — `cat knowledge/wikis/engineering-standards/wiki/index.md` shows `page_count: 5`; `find knowledge/wikis/engineering-standards/wiki -name "*.md" \| wc -l` returns 9. Drift is real; plan correctly flags reconciliation requirement at lines 50, 269, 347. |
| Existing NORSOK pages | **PASS** — `find knowledge/wikis -name "norsok-*.md"` empty; only `api-17e.md` under engineering-standards/wiki/standards/. |
| Ledger NORSOK rows | **PASS** — single prose mention inside an API RP 2FPS row's notes; zero NORSOK rows. |
| Cross-link relative path depth (`../../../../../.claude/rules/...`) | **PASS** — from `wiki/standards/<file>.md`: 5 ups (standards → wiki → engineering-standards → wikis → knowledge → repo-root), depth correct. |
| ISO supersession lineage (web search, 2 queries) | **MIXED** — see P1-1 below. ISO 19902 / NORSOK N-001 relationship is parallel/alternative, not supersession. ISO 21457 / NORSOK M-001 is "complementary, not superseded" per ResearchGate "A Review of Materials Application Limits in NORSOK M-001 and ISO 21457" — ISO 21457 was based on NORSOK M-001, both remain active. Plan Risk #6 (line 384) acknowledges this but the field name `superseded_by` and AC #345 ("whether content has migrated to ISO") still trade on the imprecise framing. |
| ISO 13533 = BOP equivalent? | **FAIL** — ISO 13533 is "Drill-through equipment" (rotary table to top of casing head wellhead). It is NOT the BOP/diverter/riser equivalent. Actual successors for BOP content: API Spec 16A (drill-through equipment) overlaps drill-through, but BOP control = API Spec 16D, drilling riser = API RP 16Q / ISO 13624-1, BOP equipment = API Spec 16A. Diverter is a separate equipment class. Plan's Risk #5 line 382 misroutes the supersession map. |
| ISO 13533 on /mnt/ace | **FAIL** — `find /mnt/ace -iname "*ISO*13533*"` returns empty. Plan claim "also on-disk per W4-B BSI plan" is unverified by file existence. (W4-B plan file does mention 13533 — but mention ≠ on-disk; need to verify the W4-B plan's claim, not propagate it.) |
| Past-tense drift | **PASS** — all proposed work uses future tense ("propose", "MUST", "will create", "this plan creates"). No past-tense artifact claims. |

---

## P1 Findings (MAJOR — must fix before plan-approved)

### P1-1: D-SR-022 superseded_by migration target is wrong (Risk #5, line 382)

**Quoted claim (line 382):**
> "the BOP-specific content is now covered by ISO 13533 (drill-through equipment — also on-disk per W4-B BSI plan). **Mitigation:** the page's `revision: "designation-withdrawn-1994"` and `superseded_by` array explicitly list D-001, D-002, D-010, ISO 13533."

**Two defects:**

1. **ISO 13533 is the wrong equivalent.** ISO 13533 is "Petroleum and natural gas industries — Drilling and production equipment — Drill-through equipment" — covers the equipment train BELOW the diverter/BOP stack (rotary-table to casing-head spool). NORSOK D-SR-022 covers the BOP stack ITSELF, the diverter, and the drilling riser. The actual supersession lineage for those scopes:
   - BOP stack design / pressure-control: API Spec 16A (well-control equipment), API Spec 16D (control systems for BOPs)
   - Drilling riser: API RP 16Q / ISO 13624-1
   - Diverter: API Spec 16C (choke/kill systems) and 16RCD (rotating control devices)
   - There is no clean ISO single-target for D-SR-022's combined BOP+diverter+riser scope; the lineage requires multiple targets.
2. **ISO 13533 is not on /mnt/ace.** `find /mnt/ace -iname "*ISO*13533*"` returns empty. The plan's "also on-disk per W4-B BSI plan" parenthetical was not verified against /mnt/ace; it propagates a claim from W4-B plan text without filesystem verification. (`API RP 16Q` IS on disk at `/mnt/ace/docs/engineering-refs/api/`.) If the implementer creates the page with a `superseded_by` entry pointing at "ISO 13533" they will (a) ship a substantively wrong supersession claim, (b) fail `test_superseded_by_pointer_resolves` (line 297) because no wiki-internal page exists and no `publisher_catalog_url` will resolve.

**Fix:** Replace the ISO 13533 entry in the D-SR-022 `superseded_by` example with a multi-entry array citing API Spec 16A, API Spec 16D, API RP 16Q (and ISO 13624-1 if a publisher-catalog pointer is acceptable). Drop the parenthetical "also on-disk per W4-B BSI plan" — verify each cited code's on-disk presence individually before listing.

### P1-2: superseded_by field name contradicts Risk #6 admission

**Quoted claim (line 384):**
> "Per Standards Norway (May 2026 web evidence), NORSOK standards are revised in parallel with ISO via mirror committees, NOT 'superseded by ISO'. The 'superseded by ISO' framing in some industry sources is imprecise."

**Defect:** The Pseudocode template (line 224), the Test contract (line 297), and the AC (lines 345, 351) all use the field name `superseded_by`. For 5 of 6 pages (N-001, N-004, M-001, M-501, M-710 — all parallel/mirror cases per web evidence), this field's name is misleading-by-construction. Web verification:
- ISO 19902 / NORSOK N-001: "intention to revise this NORSOK standard as soon as the International Standards adequately covering the scope of this NORSOK standard have been published" — parallel, not superseded (per N-001 itself, search result 1).
- ISO 21457 / NORSOK M-001: "ISO 21457 ... based on the same principles as NORSOK M-001 ... NORSOK M-001 has not been superseded by ISO 21457" — parallel/complementary (per ResearchGate review article cited in search result 2; NORSOK M-001 5th Ed 2014 explicitly cites materials limits in BOTH Table 10 AND ISO 21457 Tables 4-11).

The plan's mitigation ("the page body's 'Lifecycle status' section uses the more accurate phrasing 'content mirrored in ISO XXXXX'") only fixes the body prose — not the structurally-load-bearing field name read by `test_superseded_by_pointer_resolves`. The field name controls how downstream resolvers and reviewers interpret the data; calling a parallel-mirror relationship `superseded_by` is exactly the imprecise framing the plan disavows.

**Fix:** Either (a) rename to `iso_relationship` (or `external_lineage`) with the existing `relationship` enum widened to `{"full-replacement", "partial-overlap", "parallel-mirror", "withdrawn-no-replacement"}`, OR (b) keep `superseded_by` but ONLY populate it for D-SR-022 (the one true supersession case) and use a new field `iso_mirrors` for the parallel cases. The latter is cleaner because it preserves W4-B's `superseded_by` test inheritance (BS-EN-ISO IS true supersession) and adds a NORSOK-specific second key for the parallel-mirror reality. Update the AC at line 351 and the test name at line 297 accordingly.

---

## P2 Findings (MINOR — fix before plan-approved or document-as-deferred)

### P2-1: AC at line 353 prescribes adversarial review topics — but the umbrella-vs-per-edition decision lacks a fallback path

The AC reads "Adversarial review explicitly addresses: ... (e) the multi-edition umbrella-vs-per-edition-page decision." Risk #4 (line 381) defaults to umbrella with reviewer-may-challenge fallback. But neither the AC nor the Risks section specifies what happens IF the reviewer requires per-edition split: the page count would jump from 6 to 9 (3 codes split × 2 editions + 3 single-edition pages). 9 pages exceeds the requested "6-8 cap" referenced at line 43. The plan should explicitly state: if reviewer requires split, the M-501 1999 4th Ed page is dropped from W5-A and deferred to W5-B (single-edition lifecycle precedent applied), keeping count at 8. As written, the fallback path is undefined.

**Fix:** Add a sub-bullet to Risk #4 specifying the deferral order if split is required.

### P2-2: `test_frontmatter_has_revision` regex is unmaintainable in Markdown

**Quoted (line 285):**
> `revision` non-empty string; matches NORSOK regex `^(\d+(st\|nd\|rd\|th)-Ed-\d{4}\|\d{4}\|public-metadata-required-before-citation-use\|designation-withdrawn-\d{4})$`

The escaped pipes (`\|`) are Markdown-table-syntax artifacts — they will not parse as regex alternation in Python. The implementer must remember to substitute `\|` → `|` when transcribing. This is the same paper-cut hazard the W4-A plan ran into. The W4-B plan and W4-A plan likely have similar patterns.

**Fix:** Either (a) split the regex into a fenced code block adjacent to the table cell so the literal `|` is preserved, or (b) add an inline note "(escape-pipes are table-syntax artifacts; the implementer translates `\|` → `|` in the test file)".

### P2-3: `norsok_series` enum includes letters that don't exist on disk

The series enum (line 287) lists `{D, M, N, Z, S, U, R, L, H, I, J, P}` — but the on-disk corpus has only `D, M, N`. Including the unused letters in the test's allowed-set is fine for forward-compatibility, but the plan's prose at line 110 says "D, M, N, Z series — NOTE: no Z series on disk despite W1-B target" — a correct admission, but `Z` is in the enum, suggesting the enum was sourced from publisher knowledge rather than the on-disk corpus. Reviewer should confirm whether the enum should be tightened to `{D, M, N}` for W5-A and widened in W5-B when Z-008 / Z-013 / etc. land via publisher-portal pointers, OR left wide. Tightening provides an early-warning trip if the implementer accidentally types `Z-008` somewhere; wide is forward-flexible.

**Fix:** Pick a stance and document it in Risks. (Recommend tightening to `{D, M, N}` for W5-A; widening in W5-B.)

### P2-4: Issue title contains "(W5-A)" suffix but issue is "not yet filed"

Open Question line 390: "Proposed title: `feat(llm-wiki): bounded NORSOK Norwegian-sector standards summary promotion (W5-A)`". The plan filename uses `issue-2610` — implying the issue number 2610 is reserved/expected. If the actual `gh issue create` returns a different number, the plan filename and every internal cross-reference will need rewriting. This is a known bookkeeping hazard for the wave; W4-B does the same thing.

**Fix:** Acknowledge in the plan header that the `2610` in the filename is provisional and will be reconciled at issue-creation time. (Or rename to `2026-05-03-issue-TBD-...` and rename post-creation; W4-A/W4-B precedent should be cross-checked.)

### P2-5: Lifecycle status section appears in two precedent shapes simultaneously

The plan introduces a NEW "Lifecycle status" section (line 247) AND inherits the W4-B `superseded_by` frontmatter pattern. Both pieces of state will overlap (frontmatter says "ISO 19902 partial-overlap" and body Lifecycle prose will say "content mirrored in ISO 19902"). This is duplicative state that can drift. The W4-A precedent's per-page-body convention is to NOT have a Lifecycle section — to put the lifecycle data in frontmatter only.

**Fix:** Pick one source-of-truth surface (frontmatter) and have the body section render dynamically OR drop the Lifecycle body section in favor of frontmatter-only. Keeping both is a future-drift hazard that the test contract does not catch.

---

## P3 (Style / Defensible)

### P3-1: Header self-reference circularity

Line 17 references "single-author Claude r1 to be produced as part of plan-review per `feedback_permission_gate_blocks_cross_review.md`" — and the file you're reading IS that artifact. This is fine but worth noting: the AC at line 352 expects the file at the published path `scripts/review/results/2026-05-03-plan-W5A-claude-internal.md` — but the actual path requested in this review prompt is `scripts/review/results/2026-05-03-plan-2610-claude-internal.md`. Two different naming conventions in flight. Reconcile to one before plan-approved (recommend matching the precedent set by `2026-05-02-plan-2541-claude.md` etc.: `<date>-plan-<NNNN>-claude.md` with no `-internal` suffix unless that's the established W-series convention).

### P3-2: Distinct-source count comment

Line 163 hand-counts 10 distinct sources. Verifiable by inspection. PASS.

### P3-3: 14-grep total claim breakdown

Line 119-125: claim is "5 NORSOK M-506 + 1 NORSOK_M506 + 7 NORSOK N-004 + 1 NORSOK-N-004 = 14". Arithmetic checks. The "Critical mismatch" framing (most-cited code is absent) is an accurate and useful design signal.

---

## Adversarial-Pattern Hunt Results

| Pattern | Verdict |
|---|---|
| Past-tense artifact claims (`feedback_plan_past_tense_artifact_claims.md`) | CLEAN — all proposed work uses future tense. |
| Self-approval / pre-approval (`feedback_never_offer_to_self_label_plan_approved.md`) | CLEAN — Status: draft; explicit `# issue creation is downstream of plan-review` at line 6. |
| #2471 over-citation (`project_wiki_standards_path_decision.md` + #2596 erratum) | CLEAN — every #2471 mention adjacent to allowlist token (CSA-Z276 / historical-origin / code_id / publisher / revision / Erratum / CLAUDE.md). Plan explicitly disclaims #2471 as NOT a NORSOK path-sanction at lines 13, 51, 68. |
| Naive secret-scan FP (`feedback_naive_secret_scan_false_positive_cascade.md`) | CLEAN — denylist phrases are NORSOK-specific contiguous tokens with the `(NORSOK\|Standards Norway)[^.]{0,40}All rights reserved` proximity regex preventing bare-string false positives. |
| Permission-gate blocks cross-review (`feedback_permission_gate_blocks_cross_review.md`) | APPLIED CORRECTLY — single-author Claude r1; Codex/Gemini explicitly UNAVAILABLE with citation to the per-tool feedback files. |
| llm-wiki hyphen-path pattern (`feedback_llm_wiki_hyphen_module_path_pattern.md`) | NOT APPLICABLE — plan does not reference `scripts/data/llm-wiki/` dotted module paths. |

---

## Summary

| Severity | Count |
|---|---|
| MAJOR (P1) | 2 |
| MINOR (P2) | 5 |
| Style (P3) | 3 |

**Verdict: MAJOR.** Both P1 defects are substantive accuracy issues that will produce wrong wiki content if implemented as written. Both are fixable with targeted edits to Risk #5 (D-SR-022 successor mapping), the Pseudocode template (frontmatter field name), the test contract (test name), and the AC (lines 345, 351). After fixes, expect MINOR or APPROVE at r2.

Recommended r2 round: regenerate after fixing P1-1 (rewrite D-SR-022 successors as multi-entry array citing API Spec 16A / 16D / RP 16Q with explicit on-disk verification per entry) and P1-2 (rename `superseded_by` → `iso_relationship` OR introduce a parallel `iso_mirrors` field). Re-verify with the same allowlist test + on-disk searches.
