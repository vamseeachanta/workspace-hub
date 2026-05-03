# Adversarial Review — W4-A Plan (#2599 NACE/AMPP)

- **Plan:** `docs/plans/2026-05-03-issue-2599-llm-wiki-W4A-engineering-standards-nace.md`
- **Reviewer:** Claude (single-author r1; Codex/Gemini UNAVAILABLE per memory `feedback_permission_gate_blocks_cross_review.md`, `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_sandbox_overlay_blindness.md`)
- **Date:** 2026-05-03
- **Verdict:** **MAJOR**

---

## Summary

3 MAJOR, 4 MINOR. The plan is otherwise technically sound and inherits a good pattern from W3-A — but it carries one defect that invalidates a load-bearing acceptance criterion (the W3-C guardrail does NOT scan W4-A), one factual contradiction with live state (issue #2599 is already filed and OPEN, contrary to the plan header), and one specification self-contradiction in the no-raw-text test that risks blocking legitimate body prose. These must be resolved before approval.

---

## MAJOR

### MAJOR-1: AC #4 is hollow — W3-C guardrail does NOT cover W4-A

**Plan claim** (line 10): "W4-A is written so that guardrail passes against this plan."

**Plan claim** (Acceptance Criteria, line 331): "No regression: `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes (THIS plan is in scope of the allowlist-polarity guardrail; the W3-C erratum's guardrail must remain green)."

**Verified live (`tests/governance/test_2471_citation_scope.py:21`):**
```
PLANS_GLOB = "docs/plans/2026-05-02-*.md"
```

The glob is hard-pinned to `2026-05-02-*.md`. The W4-A plan filename is `2026-05-03-issue-2599-...md`. The guardrail will pass with 6/6 (verified via `uv run pytest tests/governance/test_2471_citation_scope.py 2>&1 | tail -3`) **regardless of what W4-A contains**, because W4-A is not scanned. The AC is therefore hollow — passing the test does not constitute evidence that W4-A's #2471 framing is allowlist-compliant.

**Why this is MAJOR:** The plan markets the guardrail as enforcement of the corrected sanction-scope framing for W4-A. It does no such thing. Any future plan dated 2026-05-03+ silently bypasses the guardrail. The W3-C erratum's intent is undermined; this is exactly the class of defect #2596 was meant to prevent.

**Required fix:** Either (a) generalize the guardrail glob to `docs/plans/2026-05-*.md` or `2026-*.md` and ship that change as a one-line precondition for W4-A merge (filed against W3-C #2596 or as a new follow-up), and re-state the AC as "after glob extension, this plan passes"; or (b) remove the AC and the line-10 claim entirely and replace with prose-only verification (manual reviewer sweep confirms #2471 is cited only as historical-origin, with allowlist tokens within proximity — Claude r1 confirms this prose check passes for every #2471 mention in the W4-A plan, see Verified-Compliance section below).

---

### MAJOR-2: Plan header contradicts live GitHub state — issue #2599 is filed, OPEN, with proposed title

**Plan claim** (line 6):
> **Issue:** _not yet filed — issue creation is downstream of plan-review per `feedback_never_offer_to_self_label_plan_approved.md`. Proposed title: `feat(llm-wiki): bounded NACE/AMPP standards summary promotion to engineering-standards wiki (W4-A)`._

**Verified live (`gh issue view 2599`):**
- State: **OPEN**
- Title: `feat(llm-wiki): bounded NACE/AMPP standards summary promotion to engineering-standards wiki (W4-A)` (exact match to "proposed title")
- Body references "Wave 4-A, 2026-05-03" and the same plan content
- Labels already applied: `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:standards` (exact match to Open Question's "Proposed labels" line 386)

**Why this is MAJOR:** The plan describes the issue as not-yet-filed and the labels as proposed. The live state shows both are already done. This is a past-tense / present-tense drift — but inverted: the plan describes something as future-pending when it is actually present-existing. Per memory `feedback_plan_past_tense_artifact_claims.md`, plans describing artifacts contrary to their actual state mislead reviewers and approvers. A reviewer who skips the live-state check will approve a plan whose "downstream" actions have already happened.

The Open Question on line 386 ("Issue title and labels...issue creation is downstream of plan-review") is therefore moot — the user (or another agent) has already decided this question off-plan. The plan must either (a) be reframed as documenting an already-existing issue or (b) acknowledge that #2599 was filed pre-plan-review and explain why; the open question must be closed.

**Possible benign explanation** that does NOT excuse the defect: an upstream batch/automation ran ahead of plan-review. Memory `feedback_never_offer_to_self_label_plan_approved.md` warns precisely against pre-authorization of downstream actions. The plan must reflect what actually happened, not what its workflow says SHOULD happen.

**Required fix:** Update header to reference `#2599` directly with state OPEN, drop "_not yet filed_" prose, drop the "proposed labels" line in Open Questions or move it to a "Confirmed" tracker.

---

### MAJOR-3: `test_no_raw_pdf_text_bleed_through` denylist self-contradiction risks blocking legitimate prose

**Plan claim** (lines 304-309, denylist):
> - "NACE International" (cover-page; legitimate as `legacy_publisher` value but FORBIDDEN in body prose)
> - "Association for Materials Protection and Performance"
> - "Houston, Texas"  (NACE/AMPP HQ city)
> - "ISO 15156"  (cover-page joint-publication string — body text may legitimately mention ISO 15156, so this entry is contextual; mitigation: allow ISO 15156 in body but flag if it appears with > 3 surrounding words from a known cover-page template)

**Defects:**

1. **"NACE International" forbidden in body prose contradicts the page's own purpose.** Every NACE page must explain that the document was published by NACE International (now AMPP). A natural body sentence like "The 1995 edition was published by NACE International in Houston, Texas" would fail two denylist entries simultaneously, despite being entirely metadata-paraphrased and copyright-safe. The plan's own sample body skeleton (line 244, "## Scope (one paragraph, ≤80 words, paraphrased)") cannot describe MR 0175's publisher without tripping the denylist.

2. **"ISO 15156" mitigation is hand-wavy and untestable as specified.** "Allow if NOT within 3 surrounding words of a cover-page template" is not a test — it is a heuristic. The plan does not specify (a) the cover-page template list, (b) the 3-word window's tokenization rule, (c) what "from a known cover-page template" means computationally. A test must be deterministic; this one is not. The W3-A test (`tests/knowledge/test_engineering_standards_abs.py`, presumably) likely solved this differently — the plan should reference that solution rather than handwave a new one.

3. **"Association for Materials Protection and Performance" cannot be in body OR frontmatter except as the `publisher_full` value.** The denylist scans body only, so frontmatter is safe — but the plan's own skeleton (line 219) places this string in `publisher_full`. The denylist test must explicitly carve out frontmatter from its scan, which the plan's test specification does not state. (W3-A precedent presumably handles this; the plan must inherit, not silently assume.)

**Why this is MAJOR:** A test that the plan claims will catch raw-bleed will instead block the plan's own conformant pages, OR will be silently weakened during implementation (the implementer will discover the contradiction and quietly drop entries from the denylist), defeating the test's purpose. Either outcome is a defect.

**Required fix:** Specify the body-vs-frontmatter scope of the scan; replace the "ISO 15156 contextual heuristic" with either a hard rule (always-allow) or a deterministic regex; rewrite "NACE International" entry to allow paraphrased body prose like "published by NACE International" and only flag specific cover-page templates (e.g., "© NACE International. All rights reserved." as a single contiguous token).

---

## MINOR

### MINOR-1: TM 0177 page is not justified by current internal-citation evidence

**Plan claim** (line 137): "Confirms NACE is THE primary citation source for `digitalmodel/cathodic_protection/`. The grep-frequency and the on-disk-corpus do NOT match — corpus priority is `MR0175` (the one on-disk + cited code) plus its test method `TM 0177`."

**Verified live:** `grep -ri "tm[ _-]?0177" digitalmodel/src/` returns zero matches. `TM 0497` is cited 3× (and is NOT on disk). `TM 0177` is NOT cited and IS on disk.

**Why this matters:** The plan's stated priority criterion is "on-disk corpus AND cited" — but TM 0177 only satisfies the first half. The "TM 0177 is the test method companion to MR 0175" justification is reasonable on subject-matter grounds, but the plan should state the criterion explicitly: "TM 0177 promoted because (a) on disk and (b) referenced by MR 0175 acceptance criteria, NOT because cited in `digitalmodel/`." Otherwise the plan reads as if TM 0177 has internal callers, which it doesn't.

**Recommendation:** Add a one-line clarification in the Risks section ("TM 0177 has zero current internal callers; promoted on subject-matter-companion grounds only").

---

### MINOR-2: Issue body uses `legacy_code_id`; plan uses `legacy_publisher` — terminology mismatch

**Issue body** (`#2599`): "NACE → AMPP rebrand (2021) requires `legacy_code_id` bridge"

**Plan body** (everywhere): `legacy_publisher`, no `legacy_code_id`

These are different fields with different semantics. `legacy_code_id` would be for codes whose IDs changed (`NACE-MR-0175` → `AMPP-MR-0175`?); `legacy_publisher` is for the publishing org's name. The plan uses the latter consistently and never defines `legacy_code_id`. Either the issue body is wrong or the plan is wrong, but they disagree.

**Recommendation:** Reconcile. If the plan is authoritative, edit the issue body. If `legacy_code_id` is needed (e.g., for the `code_id` prefix Open Question's option-2 case), specify it in the plan's frontmatter schema.

---

### MINOR-3: Open Questions hide a design decision

The plan has 5 Open Questions (lines 378-386). Three are user-decidable:
- (Q1) `code_id` prefix decision (`nace-` vs `ampp-` vs hybrid) — user-decidable
- (Q3) one umbrella vs three per-Part pages for MR 0175 — user-decidable
- (Q5) issue title/labels — already resolved (see MAJOR-2)

But two are **design defects masquerading as questions**:
- (Q2) "Should the OPTIONAL `ampp-knowledge-hub.md` stub be created?" — The plan default is "include it, flagged stub-only, excluded from resolver tests via `pytest.mark.skip`." This is asking the user to bless an exception (a non-standard in `wiki/standards/`). The honest framing is: "We need a place for publisher-level pointers; `wiki/standards/` is the wrong directory because the schema requires `code_id` to be a code, not a publisher. Decide on a new directory (`wiki/publishers/`?) or keep this as a future-W4-B problem and DROP it from W4-A." Punting to the user with `pytest.mark.skip` is design-debt accumulation.
- (Q4) test file location — vacuous; W3-A precedent is settled. Should not be an Open Question.

**Recommendation:** Resolve Q2 directly (drop the AMPP stub from W4-A; defer to a separate issue that decides where publisher-pointers live). Drop Q4. Leave Q1 and Q3 open.

---

### MINOR-4: Wiki `index.md` `page_count: 5` is already inconsistent with on-disk count

**Verified live:** `find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` returns 9. The index claims `page_count: 5`. The plan's "arithmetic AC" works around this by saying "current count + 3 (or +4)" — but the plan doesn't acknowledge that the current count is already wrong.

**Why this matters:** A future implementer following the AC literally ("page_count = current + 3") would land `page_count: 8` (5+3) when the actual on-disk count would be 12 (9+3). The drift compounds.

**Recommendation:** Add a sub-task to the implementation: "First, reconcile `index.md` `page_count` against `find ... | wc -l`; THEN apply the +3/+4 increment." Or assert the precondition test as an additional AC.

---

## Past-Tense Drift Hunt

- Plan describes itself in future tense throughout — clean on this dimension.
- HOWEVER the issue header is the inversion (described as future, exists in present) — see MAJOR-2.

## Hidden Assumption Hunt

- **HA-1 (cited but verified OK):** Plan assumes the W3-A test file format will be extensible to NACE-specific frontmatter keys. Verified — W3-A precedent at `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md` is structured for parametrization.
- **HA-2 (defect — see MAJOR-3):** Plan assumes a denylist-only test catches raw-bleed without listing specific allow-rules for the page's own metadata-prose needs.
- **HA-3:** Plan assumes `validate_citation()` from `digitalmodel/src/digitalmodel/citations/schema.py` is the resolver — verified, function exists at line 102.
- **HA-4:** Plan assumes 26 grep hits across 7 codes is the complete picture of NACE references in `digitalmodel/`. Verified — `grep -rohE "NACE[ _-]?(MR|TM|RP|SP)[ _-]?[0-9]+" digitalmodel/src/ | sort | uniq -c` matches the plan's table exactly.

## Scope Creep Hunt

- The plan stays within bounded-summary scope; no leakage into raw-text promotion or new directory creation.
- Counter-example: the AMPP Knowledge Hub stub (Q2) IS scope creep — it puts a publisher-level pointer in a `wiki/standards/` directory whose schema requires a `code_id`. See MINOR-3.

## Verified-Compliance Section (#2471 framing)

I checked every `#2471` mention in the W4-A plan against the W3-C allowlist tokens. Within the proximity window of every mention, at least one allowlist token is present (`CSA-Z276`, `CSA-only`, `historical origin`, `frontmatter`, `code_id`, `over-citation`, `Erratum`, `CLAUDE.md`, etc.). The plan would pass the W3-C guardrail if the guardrail's glob were extended to scan it. This Verified-Compliance check is the prose-only fallback referenced in MAJOR-1's recommended fix (b).

## Verified Inventories

- **Allowlist test status:** 6/6 pass (`tests/governance/test_2471_citation_scope.py` — `uv run pytest` green; W4-A out of glob scope, see MAJOR-1).
- **NACE corpus inventory** (`/mnt/ace/O&G-Standards/NACE/`): 8 PDFs across 5 directories. MR 0175 (4 PDFs: 1995, 2009 Pt 1, Pt 2, Pt 3); TM 0177-96 (1 PDF); 3 conference papers. Plan claim verified.
- **Corpus mismatch (most-cited has no raw):** Verified. `find /mnt/ace/O&G-Standards/NACE -iname "*SP*0169*" -o -iname "*SP*0176*" -o -iname "*TM*0497*"` returns zero. The plan's central premise is true.
- **NACE→AMPP 2021 rebrand:** Verified via repo-internal evidence at `data/document-index/online-resource-registry.yaml` (entry `ampp_knowledge_hub`: "AMPP Knowledge Hub (2025) unifies NACE and AMPP content"). NACE/SSPC merged 2021-01-01 into AMPP — this is well-established public information consistent with the AMPP knowledge-hub registry note.
- **Cited issues:** #2540 CLOSED (epic), #2586 OPEN (W1-A), #2594 OPEN (W3-A), #2596 OPEN (W3-C erratum), #2471 CLOSED (CSA-Z276 only), #2599 OPEN (this plan's issue — see MAJOR-2).
- **W3-A precedent:** Header structure matches the inheriting pattern; plan correctly inherits the corrected #2471 framing.
- **`api-17e.md` exemplar:** Verified at `knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` — the `code_id`/`publisher`/`revision`/`extraction_policy`/`raw_copy_allowed` pattern matches what W4-A proposes to inherit.
- **Engineering-standards CLAUDE.md path-sanction:** Verified at `knowledge/wikis/engineering-standards/CLAUDE.md` — the directory schema declares `wiki/standards/` for "publisher-agnostic; code_id, publisher, revision required" pages.
- **Standards-transfer-ledger NACE rows:** Zero pre-existing rows verified (`grep -i "NACE\|AMPP" data/document-index/standards-transfer-ledger.yaml` returns nothing).

---

## Verdict Rationale

**MAJOR (3):** AC#4 hollow due to glob scope (MAJOR-1); plan-vs-live state contradiction on #2599 issue existence (MAJOR-2); `test_no_raw_pdf_text_bleed_through` self-contradicts and is partially non-deterministic (MAJOR-3).

**MINOR (4):** TM 0177 promotion criterion not aligned with stated priority rule; `legacy_publisher` vs `legacy_code_id` issue/plan terminology mismatch; design defects packaged as Open Questions; index.md `page_count: 5` already drifted from on-disk count of 9.

The plan is good engineering work — bounded scope, clear inheritance from W3-A, honest acknowledgement of the corpus-vs-citation-frequency mismatch, defensible Q&A in Open Questions modulo MINOR-3. But the three MAJOR defects each block approval independently. Once those three are fixed, the plan is approvable.

**Provenance:** Single-author Claude review. Codex/Gemini UNAVAILABLE per the cited memory entries. Acceptable per `feedback_permission_gate_blocks_cross_review.md` for planning-only sessions.
