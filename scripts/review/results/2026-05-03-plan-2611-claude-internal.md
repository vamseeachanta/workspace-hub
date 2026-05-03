# Adversarial Review — W5-B Plan (#2611 AWS welding standards)

- **Plan:** `docs/plans/2026-05-03-issue-2611-llm-wiki-W5B-engineering-standards-aws.md`
- **Issue:** #2611 (OPEN) — `feat(llm-wiki): bounded AWS welding standards summary promotion (W5-B)`
- **Reviewer:** Claude (single-author r1; Codex/Gemini UNAVAILABLE per memory `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_sandbox_overlay_blindness.md`, `feedback_permission_gate_blocks_cross_review.md`)
- **Date:** 2026-05-03
- **Verdict:** **MAJOR**

---

## Summary

3 MAJOR, 5 MINOR. Plan inherits a strong shape from W4-A and the corpus inventory is faithful (15 PDFs, 4 D1.1 editions including the unique 15-year on-disk gap). However:
- The `status: draft` / "not yet filed" header is contradicted by live GitHub state — **#2611 is OPEN with the exact W5-B title and proposed labels already applied** (mirrors W4-A MAJOR-2 exactly; the same defect is recurring across the 2026-05-03 wave).
- The "inherited from W2-B" framing of the new `cross_references` frontmatter convention is **factually wrong** — W2-B contains no such convention. W5 is introducing the convention de novo and mislabels its own novelty.
- The A5.5 "edition uncertainty" risk dissolves on a 30-second cover-page read: the cover page reads `ANSI/AWS A5.5-96`. The placeholder-revision mitigation is valid as a safety hatch but should not be treated as the default given on-disk evidence is unambiguous.

The W3-C guardrail-glob hollowness defect (W4-A MAJOR-1) is **acknowledged** in this plan (line 355), so it is downgraded to MINOR here.

---

## MAJOR

### MAJOR-1: Plan header contradicts live GitHub state — issue #2611 is filed, OPEN, with proposed title and labels

**Plan claim** (line 6):
> **Issue:** _not yet filed — this plan is `status: draft` and does NOT pre-authorize an issue filing per memory `feedback_never_offer_to_self_label_plan_approved.md`. Proposed title and labels appear in the trailing return-format block; user-in-loop approval gates the filing._

**Verified live (`gh issue view 2611`):**
- State: **OPEN**
- Title: `feat(llm-wiki): bounded AWS welding standards summary promotion (W5-B)` (matches the W5-B plan filename slug exactly)
- Labels already applied: `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:standards` — these are the exact labels that any plan-review approval would assign

**Why this is MAJOR:** Identical defect to W4-A MAJOR-2 in `2026-05-03-plan-2599-claude-internal.md`. The plan describes the issue as future-pending when it is present-existing. Per memory `feedback_plan_past_tense_artifact_claims.md`, plans describing artifacts contrary to their actual state mislead reviewers. A reviewer who skips the live-state check approves a plan whose "downstream" actions have already happened. Per memory `feedback_never_offer_to_self_label_plan_approved.md`, this is exactly the user-in-loop bypass pattern that memory warns against. The recurrence across W4-A → W4-B → W5 in the same 2026-05-03 batch suggests an upstream automation is filing issues ahead of plan-review approval — that systemic issue exceeds this plan's scope but the plan must reflect actual state.

**Required fix:** Update the header to reference `#2611` with state OPEN, drop "_not yet filed_" prose, drop the "proposed title and labels" return-format block (or move to a "Confirmed" tracker noting issue was pre-filed), and add a short note acknowledging that filing happened before plan-review per the same systemic upstream automation that affected #2599 and #2600.

---

### MAJOR-2: `cross_references` convention is NEW and falsely framed as W2-B-inherited

**Plan claim** (line 9):
> **Sibling precedent (W2-B, ASME):** [#2591](...) — closest welding cousin (ASME BPVC IX qualifies welders/procedures that AWS D1.1 references); cross-reference frontmatter pattern is inherited here.

**Plan claim** (line 65):
> `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` — W2-B ASME plan; closest welding cousin ... Cross-reference frontmatter pattern (`cross_references` to ASME / API counterparts) inherited from this sibling.

**Verified live:**
```bash
$ grep -E "cross_references" docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md
(no output)

$ grep -rE "cross_references" knowledge/wikis/
knowledge/wikis/cross-links.md:total_cross_references: 16    # unrelated counter, not frontmatter
```

The `cross_references` frontmatter key does **not** appear in W2-B (or any other plan), nor in any existing wiki page across `knowledge/wikis/`. This plan introduces the convention de novo. The "inherited from this sibling" framing is wrong.

The plan's own line 88-89 ("W5 introduces the `cross_references` frontmatter convention ... the convention itself, not the cross-referenced pages, is the deliverable") **contradicts** the inheritance framing in line 9 / line 65. The plan is internally inconsistent on whether `cross_references` is novel or inherited.

**Why this is MAJOR:** A reviewer trusting the line-9 / line-65 framing would assume the convention has already been agreed and tested in W2-B and would not scrutinize the new shape. In fact this plan is the **first** appearance of the convention anywhere, and it is being forged inside a multi-page batch with no upstream consensus. The schema additions (`code_id`, `relation` enum {qualifies, companion, references, superseded-by, supersedes, equivalent}, `note`) deserve a separate convention-introduction issue (or at minimum a top-level acknowledgement in this plan) before proliferating across 5-6 new pages.

**Required fix:** (a) Drop the "inherited from W2-B" claim on lines 9 and 65; (b) reframe `cross_references` as a NEW W5 convention introduction with explicit reviewer call-out at the top of the plan (it currently appears as line-89 inline prose); (c) consider promoting the convention introduction to a separate Conventions-update follow-up that lands BEFORE the 5-6 wiki pages, so the schema lands in `knowledge/wikis/engineering-standards/CLAUDE.md` first and the wiki pages reference an already-sanctioned schema; OR (d) explicitly accept that this plan is doing both the convention introduction AND the first 5-6 uses in a single landing, with a follow-up issue to retroactively codify the schema in CLAUDE.md after this plan merges.

---

### MAJOR-3: Schema addition NOT codified in `engineering-standards/CLAUDE.md` — backward-compatibility unstated

**Plan claim** (line 12):
> **Path sanction (AWS):** Local sanctioning authority is `knowledge/wikis/engineering-standards/CLAUDE.md` directory schema (defines `wiki/standards/<code-id>.md` routing for the engineering-standards domain — see Evidence excerpt). Frontmatter contract per `.claude/rules/calc-citation-contract.md` rule 2 (`code_id`/`publisher`/`revision`).

**Verified live (`grep -rE "code_id|cross_references" knowledge/wikis/engineering-standards/CLAUDE.md`):**
- Line found: `code_id`, `publisher`, `revision` in the Standards-page extra-fields table (CLAUDE.md lines 36-43)
- **NOT found:** `cross_references` — the schema document does not yet describe this field

**Why this is MAJOR (compounded with MAJOR-2):** The plan emits 5-6 wiki pages that carry a `cross_references` frontmatter key not present in the wiki's own schema document. This is a **backward-incompatible schema addition** delivered without updating the schema document. Concretely:
- Wiki ingest tools (`llm-wiki` per the W5 sibling skills) MAY warn or silently drop unknown keys.
- The api-17e.md template exemplar does not carry the field, so future contributors editing AWS pages will see one shape and editing API pages another shape, creating drift.
- The test contract (`test_cross_references_shape_when_present`) validates the shape but does NOT validate that the schema document itself has been updated to declare the field as a known optional key. A future schema-validation script that enforces "frontmatter keys are subset-of CLAUDE.md table" will fail on every AWS page.

**Required fix:** Add to the Files to Change table: `Modify | knowledge/wikis/engineering-standards/CLAUDE.md | Add cross_references to the Standards page extra fields table as optional shape-validated key`. The schema update MUST land in the same commit as the first wiki page that uses the field, otherwise reviewers (and any future schema-conformance test) will see CLAUDE.md and the page diverge.

Additionally, the plan's `test_cross_references_dangling_allowed` (line 312) verifies the entry shape but explicitly does NOT validate target-page existence. This is acceptable per the plan's stated forward-pointing-link tolerance, but the test does not codify a sunset clause: when does dangling stop being acceptable? After W2-B + W1-A merge, all dangling links should resolve. The plan should add a follow-up issue to **promote the test from shape-only to dangling-resolution after W2-B and W1-A both merge**.

---

## MINOR

### MINOR-1: A5.5 cover-page edition is verifiable in 30 seconds — placeholder default is conservative-to-fault

**Plan claim** (line 38, 48, 396):
> AWS A5.5 — Specification for Low-Alloy Steel Electrodes for SMAW | gap (`AWS-A5-5.pdf` at AWS-folder root, 2001 PDF generation date — likely 1996 edition reissue; on-disk edition needs verification at implementation time)
>
> Risk (A5.5 on-disk edition uncertainty)... verification requires reading the cover page at implementation time.

**Verified by reviewer (PyMuPDF cover-page extraction):**
The PDF cover page (page 2) reads literally:
```
AWS A505 96
ANSI/AWS A5.5-96
An American National Standard
Approved by American National Standards Institute January 12, 1996
Specification for Low-Alloy Steel Electrodes for Shielded Metal Arc Welding
Supersedes AWS A5.5-81
... © 1996 by American Welding Society. All rights reserved
ISBN 0-87171-452-3
```

The on-disk edition is unambiguously **1996** (specifically: `ANSI/AWS A5.5-96`, with 2001 PDF reissue print). The plan correctly identifies "likely 1996" but defers verification — this is conservative-to-fault when the answer is a 30-second `pdftotext` away.

**Why this is MINOR (not MAJOR):** the placeholder mechanism (`revision: public-metadata-required-before-citation-use`) is a valid safety hatch and the plan's process (skip resolution check via `pytest.mark.skip`) is internally consistent. But the default proposal effectively ships a non-resolvable wiki page when the on-disk PDF resolves cleanly to 1996. Recommend: change the plan default to `revision: "1996"` (with provenance pointing to cover-page text inside `/mnt/ace/...`) and reserve the placeholder for the OPTIONAL filler-metal-overview only.

**Required fix:** Update line 48 to default `revision: "1996"`, update Risk-A5.5 (line 396) to "verified 1996 from cover page on 2026-05-03 (reviewer)", and update AC #4 (line 362) to require `revision: "1996"` literal-equality. Note: this also removes the `pytest.mark.skip` for A5.5 from the test contract — the page should participate in `test_citation_schema_resolvable`.

**Telltale phrase note:** the cover page contains `"550 N.W. LeJeune Road, Miami, FL"`, `"© 1996 by American Welding Society. All rights reserved"`, `"ISBN 0-87171-452-3"`, `"ANSI/AWS"`, and `"American National Standard"` adjacent to "AWS" — every one of these matches the plan's `RAW_TELLTALE_PHRASES` (lines 328-335). The denylist is well-calibrated for this PDF specifically; no adjustment needed.

---

### MINOR-2: AWS-A5.10 ledger row enrichment claim is verified, but ID format mismatch is unaddressed

**Plan claim** (line 38, 145-162):
> AWS A5.10 ... ledger row already exists (`id: AWS-A5.10`, `status: done`, `repo: acma-projects`)

**Verified live (`grep -i AWS data/document-index/standards-transfer-ledger.yaml`):**
- Single row matched: `id: AWS-A5.10` at line 4016 of the ledger
- `doc_path: ''` (empty, as plan claims)
- `repo: acma-projects` (matches plan)
- `status: done` (matches)

**The defect:** the plan introduces `ledger_id: AWS-D1.1`, `ledger_id: AWS-A5.5` etc. as new ledger rows. The ledger uses uppercase-with-dots; wiki uses lowercase-with-dashes. The plan's ID-form bridge (line 404, "ledger uses uppercase-with-dots; wiki uses lowercase-kebab-with-hyphens") is correct, but introduces a new ID-form discipline that future ledger-validation tools may not anticipate.

Specifically: the ledger's existing row has `id: AWS-A5.10` (with `.10` not `-10`). The plan's wiki page is `aws-a5-10.md` and `code_id: aws-a5-10` (kebab). The transformation `AWS-A5.10 → aws-a5-10` is a non-trivial mapping (uppercase→lowercase, dots→dashes). If a future migrator maps mechanically, `AWS-A5.10` could become `aws-a5.10` or `aws-a510`. The `ledger_id` frontmatter key is the bridge — but the plan does not document the canonical transformation rule.

**Required fix:** Add to the AC: "documented canonical transformation: ledger `AWS-X.Y` ↔ wiki `aws-x-y` (lowercase + dot-to-dash)". Better: codify the transformation in a small helper in `data/document-index/` or in the test contract's `test_ledger_alignment`.

---

### MINOR-3: D1.1 multi-edition umbrella is faithfully described but `revision: "2010"` is the wrong choice given the 2008 root-level PDF

**Plan claim** (line 35, 45, line 109-111):
> AWS D1.1/D1.1M (2010) Structural Welding Code — Steel | gap (4 PDFs across 2006/2009/2010 editions on disk; ledger has no row)
>
> AWS-D1-1-D1-1M-2008(1).pdf (root-level duplicate, 2008 edition) | gap — same code as priority #1 above; treat as additional `sources` entry on `aws-d1-1.md`

**Verified live (`ls /mnt/ace/O&G-Standards/AWS/AWS D1.1/`):**
```
AWS D1.1 (2006) - Structual Welding Code - Steel (Scanned).pdf      [2006]
AWS D1.1 (2006) - Structual Welding Code - Steel (Searchable).pdf   [2006, OCR variant]
AWS D1.1 (2009) - Structual Welding Code - Steel (Scanned).pdf      [2009]
AWS D1.1-D1.1M (2010) Structural Welding Code - Steel.pdf           [2010]
```
Plus the root-level `AWS-D1-1-D1-1M-2008(1).pdf` [2008].

**Multi-edition claim verified:** 4 distinct editions on disk (2006 with two scan variants, 2008, 2009, 2010). 15-year gap claim (2010 vs current 2025) is correct — widest gap in the W-series.

**Why this is MINOR:** The plan picks `revision: "2010"` as "newest on-disk" — correct. But the umbrella discipline is internally inconsistent:
- Plan line 286 says "Multi-edition umbrella covering 2006/2008/2009/2010 on-disk PDFs"
- Plan line 35 says "4 PDFs across 2006/2009/2010 editions" (drops 2008)
- Plan line 226-249 (pseudocode) lists `revision: "2010"` and `sources: [<one or more /mnt/ace paths>]` without specifying ALL 4 editions must be enumerated

The acceptance criterion (line 360) says `revision: "2010"` but does not require all 4 (or 5 with the 2006 OCR variant) source paths to be enumerated. A naïve implementer could ship a single-source wiki page that cites only the 2010 PDF and call it "multi-edition umbrella" because the prose says so.

**Required fix:** Add explicit AC: "the `sources:` frontmatter list of `aws-d1-1.md` MUST contain at least 4 entries corresponding to the 2006/2008/2009/2010 editions on disk (the 2006-Scanned and 2006-Searchable PDFs may be combined under one entry with parenthetical 'two-print variants')." Reconcile lines 35 vs 286 to consistently enumerate all 4 editions.

---

### MINOR-4: AC #4 (W3-C guardrail) — same hollowness as W4-A; plan does acknowledge but framing remains misleading

**Plan claim** (line 355):
> No regression: `uv run pytest tests/governance/test_2471_citation_scope.py -v` passes (the W3-C erratum's guardrail must remain green). **Note (inherited from W4-A MAJOR-1):** the guardrail's `PLANS_GLOB` is hard-pinned to `docs/plans/2026-05-02-*.md` and does NOT scan this 2026-05-03 plan.

**Verified live:**
```python
# tests/governance/test_2471_citation_scope.py:21
PLANS_GLOB = "docs/plans/2026-05-02-*.md"
```
6/6 tests pass against the current PLANS_GLOB. The plan correctly notes the hollowness.

**Why this is MINOR (not MAJOR):** the plan acknowledges the defect (unlike W4-A which initially claimed coverage). The framing is honest. The MINOR concern is that the AC remains in the list at all — passing the test does not constitute evidence that W5's #2471 framing is allowlist-compliant. The AC is a no-op.

**Required fix:** Either (a) remove the AC entirely and replace with prose-only verification ("Claude r1 confirms manually that all #2471 mentions in this plan appear within proximity of allowlist tokens"); or (b) generalize PLANS_GLOB to `2026-05-*.md` as a one-line follow-up issue and re-state the AC after that lands. Prefer (b) for the W-series collectively.

**Verified-Compliance manual sweep (this review performs it now):** Every #2471 mention in the W5 plan appears with allowlist tokens (`CSA-Z276`, `CSA-only`, `historical origin`, `frontmatter`) within 3 lines. Lines 12, 76, 100, 174 all clear. Compliance is established by this manual sweep.

---

### MINOR-5: A2.4 standards-vs-concepts routing is flagged but plan-default is clear

**Plan claim** (line 47, 405-409):
> AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and NDE | gap (reference document, NOT a code per se — see Open Questions)
>
> Open: A2.4 routing... Option 1 (recommended)... Option 2 (re-route to wiki/concepts/)... Option 3 (both)... **This plan proposes Option 1 (recommended). Reviewer MUST confirm.**

**Why this is MINOR:** The plan does have a clear default (Option 1: standards/) and explicitly calls out the open question. This is acceptable. The MINOR concern is that the plan's own logic ("A2.4 is a reference / symbology standard, not a code per se") undermines its own default — if A2.4 is not a code, why does it carry a `code_id` of `aws-a2-4`? The schema field name is `code_id`, and AWS A2.4 is documented by AWS as a "Standard" (not a "Code") — the naming is confusing but the publisher does treat A2.4 as a publishable standards document with a citation-able document number.

**Required fix:** Reviewer confirms Option 1 (proceed with `wiki/standards/aws-a2-4.md`). Add prose to the Open Question close-out: "A2.4 is published by AWS as a standards document (not a code per the AWS taxonomy distinction); `code_id` is overloaded to mean `standards-document-id`; future schema rename to `standards_id` is a separate convention-evolution issue." This converts the open question to a closed question and removes the "Reviewer MUST confirm" gate.

---

## Past-tense drift check

Searched the plan for past-tense artifact claims (per memory `feedback_plan_past_tense_artifact_claims.md`):

- Line 6: "_not yet filed_" — **FALSE** (#2611 is OPEN). This is the inverse of past-tense drift: the plan describes future-pending work that is actually present-existing. Captured under MAJOR-1.
- Line 9: "cross-reference frontmatter pattern is inherited here" — **FALSE** (no such inheritance). Captured under MAJOR-2.
- Lines 211-212: "Plan review — Codex | UNAVAILABLE" / "Plan review — Gemini | UNAVAILABLE" — verified consistent with memory `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_gemini_sandbox_overlay_blindness.md`. No defect.
- Lines 75: "this plan describes proposed work in **future tense**; no work has been performed." — verified accurate for the wiki pages, test file, ledger updates. The defect is exclusively in the issue-filing past-tense which is captured under MAJOR-1.
- Pseudocode block (lines 226-275) uses present-tense schema description (`---\ntitle: ...\n---`) — this is conventional and not a defect.

No additional past-tense drift beyond MAJOR-1.

---

## Verified-Compliance section

Manual prose-only sweep of #2471 mentions in this plan (since the W3-C guardrail does not scan it):

| Line | Mention context | Allowlist token within 3 lines | Pass/Fail |
|---|---|---|---|
| 12 | "[#2471](...) (CLOSED) codified the path-routing decision for CSA-Z276 specifically" | `CSA-Z276` (same line), `frontmatter` (same line), `historical origin` (same line) | **PASS** |
| 76 | "explicitly states **#2471 is CSA-Z276-only**" | `CSA-Z276-only` (same line), `CLAUDE.md` (next line), `path-routing principle` (same line) | **PASS** |
| 100 | "`#2471` — CLOSED — \"feat(knowledge): decide sanctioned CSA Z276 wiki routing...\"" | `CSA Z276` (same line), `feat(knowledge)` issue title (same line) | **PASS** |
| 173 | "**Issue #2471 body excerpt** (verifies CSA-Z276-only scope)" | `CSA-Z276-only` (same line), body excerpt scope text (next line) | **PASS** |

All #2471 mentions pass the manual allowlist sweep. The plan complies with the W3-C #2471 sanction-scope erratum framing.

---

## Cross-reference dangling-link analysis

Plan introduces `cross_references` seeds for D1.1 pointing to:
- `asme-bpvc-ix` — does NOT exist; per plan, scope of W2-B (#2591 OPEN, plan exists)
- `api-1104` — does NOT exist; per plan, scope of W1-A (#2586 OPEN, plan exists) or future W1-B

**Dangling-state defeat-of-test analysis:**
The plan states (line 89):
> the cross_references seeds are forward-pointing dangling links that the test contract permits AS DANGLING and explicitly does NOT validate as resolvable

`test_cross_references_dangling_allowed` (line 312) validates entry shape only. Does the dangling state defeat any "≥1 standards-body cross-reference" test? **There is no such test in the plan's TDD list.** The plan does not assert "every AWS page must cross-reference at least one ASME/API/BSI/etc. counterpart". The dangling state therefore does NOT defeat any AC; it is purely a soft-quality goal.

This is a **defensible omission** but worth noting for a future hardening pass: when W2-B and W1-A merge, the test should be promoted to verify cross_references targets resolve. The plan flags this as a follow-up (line 399, "A follow-up issue will tighten the test once those pages land") but does not file the issue. Recommend filing the follow-up at plan-merge time.

---

## What this review concludes

**MAJOR (3):**
1. Plan header contradicts live state — #2611 is OPEN (W4-A pattern recurrence).
2. `cross_references` convention is NEW but framed as W2-B-inherited.
3. Schema addition not codified in `engineering-standards/CLAUDE.md`.

**MINOR (5):**
1. A5.5 edition is verifiable on cover-page → plan should default `revision: "1996"`.
2. Ledger ID-form transformation rule is undocumented.
3. D1.1 umbrella `sources:` enumeration not AC-enforced.
4. AC #4 (W3-C guardrail) is acknowledged-hollow; remove or generalize PLANS_GLOB.
5. A2.4 routing open-question can be closed with documented `code_id` overload.

**Verified evidence:**
- Allowlist test passes 6/6 (but does not scan this plan)
- 15 PDFs in `/mnt/ace/O&G-Standards/AWS/` (matches plan)
- 4 D1.1 PDFs across 4 editions (2006, 2008, 2009, 2010) (matches plan)
- A5.5 cover page reads "ANSI/AWS A5.5-96" (1996 — DEFINITIVE)
- 1 AWS row in ledger (AWS-A5.10, doc_path empty, status done) (matches plan)
- 12 internal AWS references, all `AWS D1.1` (matches plan)
- `cross_references` does not exist in any wiki page or any plan (W5 is the originator)
- engineering-standards CLAUDE.md does NOT yet document `cross_references` field
- Issue #2611 is OPEN with the proposed title and labels already applied (defect)

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Codex/Gemini UNAVAILABLE per memories. Verifications run via Read/Bash on the live workspace at SHA `801de7c3a` + uncommitted plan file.

**Recommendation:** The user must first decide whether to accept the recurring "issue filed before plan-review" pattern (per MAJOR-1) as a process-level concession or push back on the upstream automation. The plan content itself is largely sound after the schema-codification fix (MAJOR-3) and the cross_references-novelty acknowledgement (MAJOR-2) land.
