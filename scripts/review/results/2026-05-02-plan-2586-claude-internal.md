# Adversarial Review of Plan #2586 — Claude (internal subagent)

**Reviewer:** Claude internal subagent
**Provenance:** Cross-review tooling unavailable on 2026-05-02 — Codex CLI 0.124 stdin-hang regression (#2479) + Gemini CLI sandbox path-resolution failure on cwd=/tmp workaround. Single-author review per fallback in memory `feedback_permission_gate_blocks_cross_review.md`.
**Verdict:** MINOR
**Date:** 2026-05-02

## Affirmatively verified

- `gh issue view 2586 --json state,title` → `{"state":"OPEN","title":"feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"}` — title matches plan.
- `gh issue view 2471` → CLOSED, "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — matches plan claim.
- `gh issue view 2540` → OPEN, epic — matches.
- `gh issue view 2559` → OPEN — matches.
- `gh issue view 2373` → OPEN — matches (referenced obliquely).
- `gh issue view 2482` → CLOSED — matches.
- `gh issue view 2481` → CLOSED — matches (cited via calc-citation contract).
- `ls -la /mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/standards/` → only `api-17e.md` exists. Confirms gap claim.
- `ls -la /mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/wiki/index.md` → exists.
- `ls -la /mnt/local-analysis/workspace-hub/knowledge/wikis/engineering-standards/CLAUDE.md` → exists; verified frontmatter contract requires `code_id`, `publisher`, `revision` for `wiki/standards/*.md` (lines 42-50).
- `ls -la "/mnt/ace/O&G-Standards/API/"` → exists, populated with hundreds of PDFs.
- `find "/mnt/ace/O&G-Standards/API/Recommended-Practice/" -iname "*2A_WSD_22nd*"` → `API_RP_2A-WSD_22nd_Edition_Nov_2014.pdf` exists.
- `find "/mnt/ace/O&G-Standards/API/Recommended-Practice/" -iname "*2GEO*"` → `API_RP_2GEO_1st_Edition_Addendum_1,_Oct_2014.pdf` and `API_RP_2GEO_1st_Ed_(2011)...` exist.
- `find "/mnt/ace/O&G-Standards/API/Recommended-Practice/" -iname "*17B*"` → `API_RP_17B_5th_Ed_(2014)_Flexible_Pipe.pdf` exists.
- `find "/mnt/ace/O&G-Standards/API/Specifications/" -iname "*17J*"` → `API_SPEC_17J_4rd_Ed_(2014)_Unbonded_Flexible_Pipe.pdf` exists (note: filename uses "4rd" typo).
- `find "/mnt/ace/O&G-Standards/API/Standards/" -iname "*2RD*"` → only `API_STD_2RD_2nd_Ed_(2013)...` exists; **no 3rd-Ed-2025 PDF on /mnt/ace** (plan acknowledges this in the ledger row).
- `find "/mnt/ace/O&G-Standards/API/Recommended-Practice/" -iname "*2SK*"` → 6 files including 3rd Ed 2005; plan claims 4th Ed 2005 R2018 — **edition number disagreement** (see Findings).
- `grep -rohE "API[ _-]?(RP|Spec|Std|TR|BUL)[ _-]?[0-9A-Za-z]+" digitalmodel/src/ | sort | uniq -c | sort -rn | head -10` reproduces the plan's table exactly (RP 1111: 100, RP 2A: 68, RP 2SK: 66, RP_1111: 47, RP 2RD: 32, RP 2GEO: 23, RP 16Q: 17, TR 5C3: 15, RP_2RD: 12, RP 1632: 10) — frequency table is faithful.
- `cat .claude/rules/calc-citation-contract.md` → confirms #2471 frontmatter contract (`code_id`, `publisher`, `revision`); confirms `Pilot reference` is **`mooring_design.py` for DNV-OS-E301**, NOT API RP 2SK.
- `grep "Citation(" digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` → **zero matches**. The only `Citation(` constructor in `digitalmodel/src/` is `digitalmodel/src/digitalmodel/citations/registry.py:52`. Plan line 21's "emits `Citation` instances against API RP 2SK" is **doubly wrong**: wrong standard (DNV-OS-E301), wrong artifact (no Citation constructor in that file).
- `cat tests/knowledge/test_ocimf_tandem_no_raw_pdf_text.py` → confirms `RAW_OCR_DENYLIST` pattern with concrete OCR-page phrases. Plan correctly identifies this as the inheritance template.
- `cat knowledge/wikis/engineering-standards/wiki/standards/api-17e.md` → frontmatter has `code_id: api-17e` (no `spec` infix). Plan accurately captures the id-collision risk in its Risks section.
- `grep "API-RP-2A-WSD\|API-STD-2RD\|..." data/document-index/standards-transfer-ledger.yaml` → all 10 priority codes (or close variants) found, **except** the plan-claimed exact string `API-SPEC-17J-4RD-ED` is at line 326 (matches), but the more general `API-RP-1111` ID in ledger is `API-RP-1111-3RD-ED` (3rd Ed) — the plan proposes wiki page for 4th Ed (2009). Edition mismatch — see Findings.

## Findings — MAJOR

**none.** The plan's substantive scope (10 bounded standards pages with #2471 frontmatter, single test file, no raw text, links-only pointer to `/mnt/ace`) is sound and consistent with the cited contracts (#2471, #2482, calc-citation-contract.md). The defects below are correctness-of-claim and accuracy-of-acceptance-criteria issues, not scope/architecture defects, hence MINOR.

## Findings — MINOR

1. **Plan line 21 misattributes the calc-citation pilot.** Quote: "Found: `…/orcaflex/mooring_design.py` — pilot reference cited by `.claude/rules/calc-citation-contract.md`; emits `Citation` instances against API RP 2SK." The rule file (line 19) says the pilot demonstrates "DNV-OS-E301 mooring safety factors", and `grep "Citation(" mooring_design.py` returns **zero matches** — no Citation instance is emitted there. The actual sole `Citation(` constructor in `digitalmodel/src/` is `citations/registry.py:52`. **Remediation:** rewrite line 21 to either (a) cite `registry.py:52` as the construction site, or (b) state truthfully that the pilot is a *prose* reference (the rule's `Pilot reference:` line) and the Citation constructor has not yet been wired into `mooring_design.py` — which would clarify why the api-rp-2sk wiki page is *future-needed* even if no live caller exists today. The current language overstates downstream readiness and could trick a reviewer into approving on the assumption that a live caller already depends on the new page.

2. **Plan line 32 / Risks section claim "API RP 2SK (4th Ed, 2005, R2018)" — edition number is wrong.** The PDFs on `/mnt/ace/O&G-Standards/API/Recommended-Practice/` are clearly labeled `API_RP_2SK_3rd_Ed_(2005)_Design_and_Analysis_of_Stationkeeping…pdf` and `API_RP_2SK_3rd_Ed_Addendum_1_(2007)…pdf`. Public publisher metadata (api.org) shows 3rd Edition 2005, with "reaffirmed 2008" addendum and a separate 4th Edition initiative. Plan's "4th Ed, 2005" pairs an edition number with a year that don't co-occur in any verifiable source. **Remediation:** change to "3rd Ed, 2005 (R2008 addendum)" matching the on-disk filename, OR provide a publisher-catalog URL pinning a 4th-Ed-2005 release before approval. The error is load-bearing because `revision_source` and `Citation.revision` will downstream-attest this string.

3. **Plan line 39 / Risks #10 says "API RP 1111 (4th Ed, 2009; offshore hydrocarbon pipelines, LSD)" but ledger ID is `API-RP-1111-3RD-ED`.** Verified by `grep API-RP-1111 standards-transfer-ledger.yaml` → only `API-RP-1111-3RD-ED` is ledgered (line 128). The on-disk PDF `API_RP_1111_4th_Ed_(2009)…pdf` does exist, so the underlying *source* is real, but the **ledger ID does not match the proposed wiki edition** — meaning the plan implicitly proposes either (a) creating a new ledger row, or (b) using the ledger's 3rd-Ed ID for a 4th-Ed wiki page. Neither is stated. **Remediation:** state explicitly which ledger ID the new `api-rp-1111.md` page maps to, and if a new row is required, add it to "Files to Change". The acceptance criterion "frontmatter validates against engineering-standards CLAUDE.md schema" does **not** catch this mismatch because the schema doesn't cross-validate against the ledger.

4. **The "Open Questions" `revision: "public-metadata-required-before-citation-use"` fallback hidden in the pseudocode skeleton (line 164) silently lets pages ship with non-resolvable revisions.** Setting that string satisfies the `test_frontmatter_has_revision` assertion (it's a non-empty string) and the schema check in `validate_citation` (the citation's revision string would just need to *match* — the validator does no semantic check on whether the revision is real). **The acceptance criterion `Citation(... revision='4e-2005' ...)` would actually FAIL** against a page whose frontmatter says `revision: public-metadata-required-before-citation-use`, because `validate_citation` requires the citation's revision to equal the frontmatter's revision string verbatim (`schema.py:127-132`). So the acceptance criterion as written can pass for `api-rp-2sk.md` only if that page's revision frontmatter is *literally* `4e-2005` — which contradicts plan line 32's "4th Ed, 2005, R2018" *AND* the ledger's 3rd-Ed reality. **Remediation:** (a) commit to a single revision string per page and use it both in frontmatter and the acceptance-criterion `Citation(...)`, or (b) explicitly mark some of the 10 pages as "stub-only, revision pending" and exclude them from the resolution check.

5. **Acceptance criterion `git diff origin/main...HEAD -- knowledge/wikis/engineering-standards/wiki/standards/api-*.md` matches zero raw-text phrases (line 243) tests only a denylist that is itself only sketched (line 234)**. The plan promises "≤15 entries" drawn from "API publication front-matter conventions" and offers four examples ("American Petroleum Institute", "1220 L Street, NW", "Washington, DC 20005", "Reproduction or translation of any part of this work"). This is a *content-bleed proxy*, not a content-bleed test: the OCIMF precedent uses 8 phrases all drawn from a *specific* OCR'd cover page; the API list as drafted would catch a verbatim copyright page but **not** a verbatim clause excerpt (e.g., a dimensional formula with a citation footer). Given the plan's word-budget ceiling of 1500 words, a determined contributor could paste a substantial clause excerpt and pass every test. **Remediation:** either (a) tighten the budget ceiling to ~500 words for the bounded preview, or (b) add a positive-shape test that the body contains only structural sections (Scope, Why-this-page-exists, Where-to-find, Cross-references) and not a "Clauses" or "Formulas" section. Currently the test contract is structural-existence-leaning, which the rubric flags as a hollow test list.

6. **Past-tense drift detected.** Plan line 24's parenthetical "(the only existing API standards page is `wiki/standards/api-17e.md`, a metadata stub)" is fine; but line 24 also says **"no wiki page yet exists for any of the 10 priority codes proposed below"** — verified true. However, plan line 60 in "Project memory consulted" says: *"`feedback_plan_past_tense_artifact_claims.md` — this plan describes proposed work in future tense; no work has been performed."* That's a self-attestation, which is fine, but the **Acceptance Criterion line 245** uses imperative present-tense `Citation(...) succeeds without error` referencing a wiki page (`api-rp-2sk.md`) that **does not exist yet**. The acceptance criterion is a checkable post-condition, but a plan reviewer skimming the criteria might interpret "verified to exist at `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py`" (the parenthetical) as an attestation that the *wiki page* path also already resolves. **Remediation:** rephrase the parenthetical to attest only the resolver module's existence, not the wiki page's.

## Notes

- Plan does NOT propose copying raw text. The pseudocode skeleton (lines 156-191) explicitly forbids quoting and mandates `extraction_policy: metadata-only` + `raw_copy_allowed: false`. #2482 vendor-derivative deny-list is honored.
- The id-collision risk discussion (Risks line 269) is accurately characterized: existing `api-17e.md` uses bare `api-17e`, new pages use `api-rp-`/`api-spec-`/`api-std-` prefixes. Plan correctly defers retro-rename to follow-up. The asymmetry will cause some reviewer head-scratching but is not a defect.
- The "Open: Which 10?" subsection at line 270 explicitly invites user substitution before approval — appropriate user-in-loop gating.
- Plan correctly avoids modifying `wiki/sources/` (acceptance-criterion bullet line 247 makes this explicit, consistent with calc-citation-contract.md rule 7).
- The TDD list contains 10 tests; ~6 are pure structural-existence (`test_page_exists`, `test_frontmatter_has_*`, `test_index_lists_all_ten`) and 4 attempt contract behavior (`test_no_raw_pdf_text_bleed_through`, `test_body_word_count_bounded`, `test_links_only_pointer_to_mnt_ace`, `test_citation_schema_resolvable`). The contract tests are stronger than typical "hollow" lists, but Finding #5 above tightens the bleed-through test specifically.
- 7 distinct sources counted (line 118) — meets ≥3 floor.
- Plan correctly cites `feedback_naive_secret_scan_false_positive_cascade.md` and explicitly scopes the denylist narrowly (line 234) to avoid the false-positive trap. Good.
- Stub-vs-full naming asymmetry (`api-17e` vs `api-spec-17e`) is flagged as Open Question; reasonable to defer.

## Reviewer's checklist
- [x] Verified ≥3 cited sources via direct file/issue read (verified 8: 6 issue states + multiple file paths + grep proof + frontmatter contract + on-disk PDFs)
- [x] Read the FULL plan (all 290 lines)
- [x] Hunted for past-tense drift (Finding #6)
- [x] Hunted for hidden assumptions (Finding #1: assumes Citation already wired; Finding #4: assumes revision-string consistency; Finding #5: denylist as proxy for content bleed)
- [x] Did NOT praise the plan
- [x] Did NOT restate the plan body
- [x] Embedded evidence inline for each finding
