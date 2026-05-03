# Adversarial Review — Plan #2600 (W4-B BSI Bounded Subset Promotion)

- **Plan:** `docs/plans/2026-05-03-issue-2600-llm-wiki-W4B-engineering-standards-bsi.md`
- **Issue:** #2600 (OPEN — `feat(llm-wiki): bounded BSI offshore-petroleum subset summary promotion (W4-B)`)
- **Reviewer:** Claude (single-author, internal r1)
- **Date:** 2026-05-03
- **Provenance:** Codex/Gemini UNAVAILABLE per memory (`feedback_codex_cli_0_124_upstream_regression.md`, `feedback_gemini_sandbox_overlay_blindness.md`); single-author review path per `feedback_permission_gate_blocks_cross_review.md`.

## Stance contract

Adversarial — defects only. Charitable reading is forbidden. Verdict scale: APPROVE (zero issues), MINOR (only stylistic / non-blocking), MAJOR (any blocker or hidden assumption that would invalidate AC).

---

## Verification log

| Check | Result | Evidence |
|---|---|---|
| Allowlist test runs clean | PASS | `uv run pytest tests/governance/test_2471_citation_scope.py` → 6 passed in 3.39s |
| BSI inventory (`BS_13*`) count | PASS | `find /mnt/ace/O&G-Standards/BSI -name "BS_13*" -type f \| wc -l` = **11** (matches plan) |
| BSI total file count | PASS | 76 entries (75 PDFs + 1 .doc), matches plan |
| BS 13628 / 13533 / 13703 on disk | PASS | 5 PDFs match `*13628*` (4 distinct parts incl. duplicate Pt 3); 1 each for 13533 and 13703 |
| Issue states (#2540, #2594, #2596, #2600) | PASS | #2540 CLOSED, #2594 OPEN, #2596 OPEN, #2600 OPEN |
| WebSearch (BS-EN-ISO adoption pattern) | PASS | Confirmed: `BS EN ISO 13628-x` is BSI re-publication of ISO via CEN; "not technically superseded" is the correct framing for that case |
| `validate_citation` semantics | PASS | `digitalmodel/src/digitalmodel/citations/schema.py:102` does literal-equality on `code_id`/`publisher`/`revision`; matches plan claim |
| Engineering-standards CLAUDE.md schema fields | **PARTIAL** | Schema lists `supersedes` (optional), NOT `superseded_by`. Plan introduces a new field name. See M1. |
| `tests/knowledge/test_engineering_standards_abs.py` exists | NEGATIVE | Does not exist on disk; W3-A has not yet landed. Plan acknowledges this (TODO fallback). |
| Past-tense drift | NEGATIVE | `grep -nE "have been\|was created\|landed\|completed\|implemented"` returns no past-tense claims about W4-B work itself; only inherited "fix lineage" prose for W1-A/W3-A which IS past-tense reality. Acceptable. |

---

## MAJOR findings

### M1. The W3-C allowlist test does NOT scan 2026-05-03 plans — every #2471 mention in this plan escapes regression coverage

The plan's path-sanction risk control says: *"The W3-C erratum allowlist test at `tests/governance/test_2471_citation_scope.py` will catch any over-citation; W4-B's prose deliberately keeps every #2471 mention adjacent to a CSA-Z276 / over-citation / W3-C erratum / scope token to satisfy the allowlist."*

**Defect:** the allowlist test glob is hard-coded:

```python
PLANS_GLOB = "docs/plans/2026-05-02-*.md"
```

(`tests/governance/test_2471_citation_scope.py:21`)

The W4-B plan filename is `docs/plans/2026-05-03-issue-2600-...md`. **It is not scanned.** The same applies to its sibling W4-A/W4-C/W4-D plans (#2599/#2601/#2602). Eight `#2471` mentions in this plan are therefore outside the regression net.

I ran an ad-hoc proximity check and the eight mentions in this plan all DO appear adjacent to allowlist tokens (the prose is well-disciplined). But the AC at line 280 — *"`uv run pytest tests/governance/test_2471_citation_scope.py -v` passes — the W4-B plan stays within the W3-C erratum allowlist"* — is **vacuous**: the test passes today even with zero scope discipline in this plan, because the test isn't looking at this file.

**Fix options (any one resolves M1):**
1. Generalize the glob to `docs/plans/2026-05-0[2-9]-*.md` or `docs/plans/2026-05-*.md` and re-run.
2. Add an explicit `test_w4b_scope_compliance` test pinning this plan path (matching the existing `test_w1a_amendment_landed` / `test_w1b_amendment_landed` / `test_w2c_amendment_landed` precedents).
3. Add a clause to the AC that the implementer MUST update `PLANS_GLOB` (or add an explicit test) before landing the implementation.

Without any of these, the plan's #2471-discipline AC is a dead letter.

### M2. `superseded_by` is a brand-new field invented by this plan; the engineering-standards CLAUDE.md schema defines `supersedes` (the inverse direction) and the plan does not declare `superseded_by` as a schema extension

`knowledge/wikis/engineering-standards/CLAUDE.md` Standards-page extra-fields table (verified 2026-05-02):

| Field | Required |
|---|---|
| `code_id` | required |
| `publisher` | required |
| `revision` | required |
| `jurisdiction` | optional |
| `supersedes` | optional |

The plan's frontmatter introduces:
- `superseded_by` (NEW — opposite direction from schema's `supersedes`)
- `superseded_by_note` (NEW)
- `bs_doc_number` (NEW)
- `revision_amendments_note` (NEW)
- `publisher_full` (NEW)
- `ledger_id` (NEW)
- `publisher_catalog_url` (NEW)

AC line 282 claims: *"Frontmatter for every new page validates against the engineering-standards `CLAUDE.md` schema"*. This is technically true (the schema only **requires** `code_id`/`publisher`/`revision`, and additional fields are not forbidden), but the plan never explicitly amends the schema or files a follow-up to land these new fields in `CLAUDE.md`. Two specific concerns:

1. **`superseded_by` vs `supersedes` direction is load-bearing.** The semantic of "this BS page is superseded by ISO X" is the inverse of `supersedes`, which lists "what this page replaces". The plan's `superseded_by` field is correct for the BSI case (the BS page is the older/national form, ISO is the canonical form). But by introducing a new field name instead of using the documented `supersedes` field with inverted directionality, the plan creates a schema fork. CSA-Z276 and any future code might use either `supersedes` or `superseded_by` based on which plan author wrote first; consumers (e.g., `digitalmodel.citations`) get a fork.
2. **`test_superseded_by_pointer_resolves` is the load-bearing W4-B-specific test.** If the field name itself is debatable, the test's contract is debatable.

**Fix:** either (a) add a documented schema-extension step to `engineering-standards/CLAUDE.md` as part of W4-B (one-line entry in the Standards-page extra-fields table), OR (b) re-use the existing `supersedes` field with semantics adjusted (BS page lists `supersedes: [iso-13628-2]` would be wrong; this would require introducing an inverse field anyway, so option (a) is cleaner). Either way, the schema decision must be made before implementation, not deferred to a downstream consumer.

### M3. `test_superseded_by_pointer_resolves` is a tautology in the W3-B-not-landed world

The test contract (line 261):
> `superseded_by` non-empty, lowercase-kebab, starts with `"iso-"` OR `"en-iso-"`; AND value satisfies one of: (a) wiki page at `knowledge/wikis/*/wiki/standards/<superseded_by>.md` exists, OR (b) `publisher_catalog_url` frontmatter key is present and is a non-empty URL string.

I verified (`find knowledge/wikis -name "iso-1362*.md"`) — **zero** ISO 13xxx wiki pages exist. The plan acknowledges this. So clause (a) is unreachable for all 8 pages at write-time; every page MUST satisfy clause (b) by carrying `publisher_catalog_url`.

This collapses the test to: *"every page has a `publisher_catalog_url` frontmatter key whose value is a non-empty URL string."* That is identical to a `test_frontmatter_has_publisher_catalog_url` test. It does NOT verify that the URL resolves, that the URL points to the correct standard, or even that the URL is well-formed (the test only checks "non-empty URL string" — `"http://x"` passes).

The plan's value claim — *"every BS page's `superseded_by` must point to a valid ISO/EN code-id"* (line 261) — is not what the test enforces in the W3-B-not-landed world. The test enforces "has a URL", which is far weaker.

**Fix:** strengthen clause (b) to one of:
1. HTTP HEAD check on the URL (network-dependent — risky for CI; defer).
2. Regex enforcing the URL host is `bsigroup.com` or `iso.org` AND the URL contains the ISO code number from the `superseded_by` value (e.g., `superseded_by: iso-13628-2` → URL must contain `13628`). This is testable offline and far more meaningful.
3. Mark the test `xfail` with a `reason="W3-B ISO 13xxx pages not yet present; pointer resolution is structural-only"`, so the weakness is documented rather than masquerading as semantic verification.

### M4. `superseded_by_note` is body-prose-only in pseudocode; the plan never declares it as a frontmatter field but treats it as if it were testable

Line 192 of the pseudocode block lists `superseded_by_note: "BSI-published form of ISO standard..."` inside the YAML frontmatter. But:

- The risk-mitigation prose at line 316 says: *"every BS page MUST carry `superseded_by_note: '...' for the BS-EN-ISO adoption case... Reviewer must verify the note text is present on every page during plan-review."*
- There is **no test** in the TDD list (lines 252-272) that asserts `superseded_by_note` presence or content.
- AC line 283 lists *"`jurisdiction: UK`, `superseded_by: <iso-code-id>`, and `bs_doc_number`"* as W4-B-specific contracts — `superseded_by_note` is omitted from the AC.

So the plan declares `superseded_by_note` as load-bearing for the BS-EN-ISO classification (Risks line 316: *"Reviewer must verify the note text is present"*), assigns its enforcement to a human reviewer, and provides no test contract for it. This is exactly the "hidden assumption / hollow test" pattern: the most engineering-meaningful field on each page (the one that distinguishes "jurisdictional re-publication" from "obsolete prior edition") has no machine enforcement.

**Fix:** add `test_frontmatter_has_superseded_by_note_when_bs_en_iso` to the TDD list with logic: *"if `bs_doc_number` starts with `BS EN ISO`, then `superseded_by_note` is present and contains the substring 'jurisdictional re-publication' or 'not technically superseded'"*. Then add a corresponding AC.

---

## MINOR findings

### m1. AC arithmetic for `page_count` is brittle — actual current `page_count` is 5, but if W3-A also runs to 10 first, plan's "+8" gives `page_count = 23`, an unverified claim

`knowledge/wikis/engineering-standards/wiki/index.md:5` shows `page_count: 5`. The plan's AC (line 288) is "current + 8" arithmetic. This is fine for W4-B in isolation but, combined with the parallel-plan reality (W4-A/W4-C/W4-D filed for the same date and same wiki domain), creates merge-order coupling. AC is correct as drafted; just flagging that the implementer must read the current value at write-time, NOT assume `5 + 8 = 13`.

### m2. The "76 entries (75 PDFs + 1 .doc)" prose is verified but the line saying *"76 entries because some filenames lack the `BS_` prefix or are non-PDF — e.g. `bs4360.doc`"* is slightly self-contradictory

Line 114: *"the directory listing shows 76 entries because some filenames lack the `BS_` prefix or are non-PDF"* — implies the 76 number is "above 49". The earlier `find -name "BS_*"` count of 49 actually comes from case-sensitive `BS_` matching; the directory has more `BS *` files with different naming. The numbers reconcile but the prose conflates two different `find` runs. Cosmetic.

### m3. Pseudocode `tags` list mixes `"british-standards"` and `"bsi"` — likely tag-discipline drift

Line 181: `tags: ["bsi", "british-standards", "standards", "<discipline-tag>", "metadata-only"]`. W3-A precedent uses single-publisher-token tags (`["abs", "standards", ...]`). Doubling up `"bsi"` AND `"british-standards"` invites tag-cardinality drift. Pick one. Recommend `"bsi"` for consistency with the `code_id` lowercase-kebab convention.

### m4. AC line 286 `revision: "public-metadata-required-before-citation-use"` placeholder — copy-pasted from W3-A; plan does not explicitly identify which (if any) of the 8 BS pages need this fallback

Plan's Evidence section pins all 8 pages to specific revision years (2001, 2002, 2004) confirmed via on-disk filenames. So in practice the placeholder is a paste-through from W3-A and likely never triggers for W4-B. Either prove it never triggers (drop the AC clause) or identify which page might trigger it. As written, it's defensive-but-unused.

### m5. "12 ≥ 3" source-count comment (line 141) is meta-prose left in the rendered plan

Cosmetic — the HTML comment counting distinct sources is plan-author plumbing that survived to the committed version. Either remove or clarify the convention. Not load-bearing.

### m6. The TDD list claims "≥16 parametrized assertions × 8 pages ≈ 128 effective test cases" (line 334), but the actual test count is 16 distinct test functions, not 16 assertions per page

Cosmetic but the math is sloppy. 16 tests × 8 page params = 128 test invocations, which IS what pytest reports. The "≥16 parametrized assertions" phrasing conflates tests with assertions. Fine for a T-shirt-size justification; not a blocker.

---

## Past-tense drift hunt

`grep -nE "have been|was created|was built|landed|completed|implemented|added rows|created pages"` against the plan returned ONE match:

> Line 324: *"the W4-B test file imports `MAX_BODY_WORDS` from W3-A's test file when present (single source of truth); if W3-A has not yet landed at implementation time..."*

This is correct conditional prose ("when present", "if not yet landed") — describes a runtime fork, not a past-tense claim. **No past-tense drift.**

The plan is consistently future-tense about its own work. The "post-erratum framing" prose for inherited W1-A/W3-A defects is past-tense reality (those WERE corrected) — also correct.

---

## Hidden-assumption / scope-creep hunt

1. **Cross-wiki collision check at line 51 says "ZERO pre-existing BS pages exist anywhere in `knowledge/wikis/*/wiki/standards/`."** I verified: `find knowledge/wikis -name "bs-*.md"` returns zero matches. PASS.
2. **Plan claims "BS 13628 Pt 1, 4, 6, 7, 9, 10, 11, 15... are NOT among the 11 BS 13xxx PDFs on disk"** — verified via `find /mnt/ace/O&G-Standards/BSI -iname "*13628_Pt_1*" -o -iname "*13628_Pt_6*"` returns empty. PASS.
3. **Duplicate BS 13628 Pt 3 collapse semantics:** plan says both PDFs collapse into one wiki page with both paths in `sources` frontmatter. Risk acknowledged at line 319; test contract at line 265 only asserts `/mnt/ace/...` is mentioned in body, NOT that both source paths appear. **Hidden assumption:** plan never enforces that both Pt 3 PDFs are listed in `sources` — only the Risks prose says so. If one path is dropped at implementation, no test catches it. Promote to `test_pt3_dual_sources_listed` or accept the m-level gap. Borderline minor.
4. **Cross-reference `[[<iso-counterpart-page>]] (when the ISO wiki page lands via W3-B)`** in pseudocode line 220 — this is a wiki-link to a non-existent page. Wiki-internal-link rendering may or may not warn; the plan never specifies behavior when the link resolves to nothing. Cosmetic.
5. **No mention of digitalmodel sparse-checkout overlay status.** Per memory `feedback_sparse_checkout_add_not_disable.md`, `digitalmodel/` is in the workspace-hub overlay; the plan invokes `validate_citation` from `digitalmodel/src/...` and assumes the file is materialized. For workspace-hub, `digitalmodel/` is materialized today (verified via existing read of `schema.py`). Not a defect for this run; flagging as a latent risk.

---

## Overall verdict

**MAJOR — 4 MAJOR findings, 6 MINOR findings.**

The plan is well-disciplined on inherited W3-A test contract, BS-EN-ISO classification framing, and on-disk evidence verification. But four blockers are non-trivial:

- **M1** — the regression test backstop the plan leans on does not even scan this plan's filename.
- **M2** — `superseded_by` field is a schema fork the plan does not own.
- **M3** — the new W4-B-specific test reduces to a tautology in the only world that exists today.
- **M4** — the most engineering-meaningful field (`superseded_by_note`) is delegated to human review with no test.

Each is independently fixable in plan-revision (a few lines of edits). The inheritance lineage is sound and the on-disk corpus checks out. **Do not approve until M1-M4 are addressed.**

Recommended revisions:
1. Generalize `PLANS_GLOB` in `tests/governance/test_2471_citation_scope.py` to cover 2026-05-03 plans (or add explicit per-plan tests). Hold this as an AC for W4-B, OR file as a small companion fix.
2. Document `superseded_by` (and `jurisdiction`-extension semantics) in `engineering-standards/CLAUDE.md` Standards-page extra-fields table as part of W4-B's deliverables.
3. Strengthen `test_superseded_by_pointer_resolves` clause (b) to require the URL host be `bsigroup.com` or `iso.org` AND contain the numeric code (`13628`, `13533`, etc.). OR mark `xfail` with documented reason.
4. Add `test_frontmatter_has_superseded_by_note_when_bs_en_iso` to TDD list and AC.
