# Adversarial Review — Plan #2594 W3-A (ABS bounded promotion)

> **Plan:** `docs/plans/2026-05-02-issue-2594-llm-wiki-W3A-engineering-standards-abs.md`
> **Issue:** #2594 (OPEN — verified `gh issue view 2594` 2026-05-02)
> **Reviewer:** Claude (single-author r1)
> **Date:** 2026-05-02
> **Provider availability:** Codex UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479); Gemini UNAVAILABLE (sandbox cwd=/tmp blocks workspace-hub overlay reads). Single-author Claude review acceptable per memory `feedback_permission_gate_blocks_cross_review.md`.
> **Stance:** defects-until-proven-otherwise. APPROVE only after affirmative verification.

---

## Verification log (affirmative)

| # | Check | Method | Result |
|---|---|---|---|
| V1 | #2471 framing — plan does NOT use it as generalized standards path-sanction | grep + read lines 8, 11, 52, 86, 162-166 | **PASS.** Line 11 explicitly states "[#2471] codified the path-routing decision **for CSA-Z276 specifically**... it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple." Line 52 names `engineering-standards/CLAUDE.md` as path-sanction authority. Line 12 cites `.claude/rules/calc-citation-contract.md` rule 2 as frontmatter contract. Plan is correctly framed per memory `project_wiki_standards_path_decision.md`. |
| V2 | ABS PDF inventory = 29; subdir splits 17 GN / 5 Notices / 7 Rules | `find /mnt/ace/O&G-Standards/ABS -maxdepth 4 -type f -iname "*.pdf"` and per-subdir | **PASS.** Total 29; Guidance-Notes=17, Notices=5, Rules=7. Matches plan line 108 verbatim. |
| V3 | 3 picked codes have on-disk presence | `find /mnt/ace/O&G-Standards/ABS -iname "*GUI-115*"` etc. | **PASS.** GUI-115 → 4 hits including 2014 edition (the one the plan pins). GN-Cathodic-Offshore-2018 → 1 hit. Steel-Vessels-Part3-2016 → 1 hit. Conditions-Classification-Part1-Offshore-2014 → present in `Rules/`. Rules-Part1-Offshore-2014 → present. All 5 spot-checked codes verified. |
| V4 | Cited issue states | `gh issue view 2540/2586/2590/2471/2594/2227/2482/2481` | **PASS.** #2540 OPEN ("epic(llm-wiki): overnight Elements corpus planning wave"), #2586 OPEN (W1-A API), #2590 OPEN (W2-A DNV), #2471 CLOSED ("CSA Z276 wiki routing"), #2594 OPEN (this plan's issue, contradicting plan line 6 "_not yet filed_" — see F1), #2227 CLOSED, #2482 CLOSED, #2481 CLOSED. All states match plan claims except #2594 itself. |
| V5 | Internal-reference grep claim "17 short-string ABS hits" | `grep -rohE "ABS[ _-]?(GUI\|GN\|MODU\|FPI\|FPSO\|MPS\|FAS\|LRFD\|SVR\|MOU\|BOI\|Rules\|Notice\|Steel\|Ship\|Drilling\|Riser\|Cathodic\|Fatigue)[ _-]?[A-Za-z0-9_-]*" digitalmodel/src/ \| sort \| uniq -c \| sort -rn` | **PASS.** Reproduced verbatim: `6 ABS Steel Vessel`, `6 ABS GN Offshore`, `1 ABS-SVR`, `1 ABS SVR`, `1 ABS Steel`, `1 ABS Rules for`, `1 ABS Rules call`, `1 ABS GN Ships`. Sum = 17 hits, 8 unique strings. Matches plan line 124-135 exactly. |
| V6 | `_read_frontmatter` exists in schema.py | `grep` schema.py | **PASS.** `digitalmodel/src/digitalmodel/citations/schema.py:82: def _read_frontmatter(path: Path) -> Mapping[str, Any]`. `validate_citation` at line 102 uses it at line 117. The `test_citation_schema_resolvable` invocation target (line 294) is real. |
| V7 | Engineering-standards CLAUDE.md path-sanction excerpt | Read CLAUDE.md lines 23, 42-49 | **PASS.** "wiki/standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)" present at line 23. The frontmatter triple table at lines 44-48 matches plan's quoted excerpt at lines 156-160. Plan accurately quotes the schema. |
| V8 | ABS ledger rows | `grep ^- id: ABS data/document-index/standards-transfer-ledger.yaml` | **PASS.** Two rows: `ABS-GUI-00` (Thrusters/DP 1994) and `ABS-GUI-002` (FPSO 1994). Matches plan lines 138-147. |
| V9 | No pre-existing ABS pages anywhere in `knowledge/wikis/*/wiki/standards/` | `ls knowledge/wikis/*/wiki/standards/abs-*` | **PASS.** Empty result — no ABS pages exist in any wiki domain. Confirms plan's "ZERO pre-existing ABS pages" claim (line 27, 78, 343). |
| V10 | Past-tense drift | `grep -nE "^\s*(was\|were\|landed\|completed\|done\|created\|added\|implemented\|wrote\|fixed\|merged) "` | **PASS.** No past-tense artifact claims. Plan describes work as future tense ("will create", "this plan creates", "to be produced"). Compliant with `feedback_plan_past_tense_artifact_claims.md`. |

---

## Findings

### F1 — MINOR — Plan header says "_not yet filed_" but issue #2594 is OPEN

**Location:** Plan line 6:
> `> **Issue:** _not yet filed — this plan is the deliverable; issue creation is downstream of plan-review per feedback_never_offer_to_self_label_plan_approved.md_`

**Evidence:** `gh issue view 2594` returns `{"number":2594,"state":"OPEN","title":"feat(llm-wiki): bounded ABS standards summary promotion to engineering-standards wiki (W3-A)"}`. Issue is filed and live; the plan filename also embeds `2594`. The plan's own filename indicates that #2594 already exists.

**Impact:** Header is factually stale. Reviewer scanning the plan may believe issue is unfiled and incorrectly proceed to file a duplicate. The "issue creation is downstream of plan-review" memory hook is still respected (the plan didn't *self-file*), but the prose is now wrong.

**Fix:** Replace line 6 with `> **Issue:** [#2594](https://github.com/vamseeachanta/workspace-hub/issues/2594) (OPEN)`.

---

### F2 — MINOR — Word-count constant import creates implicit W1-A→W3-A ordering coupling

**Location:** Plan line 291 (TDD Test List, `test_body_word_count_bounded`):
> "`word-count constant imported from W1-A's test file (tests/knowledge/test_engineering_standards_api_pages.py) at implementation time, NOT redefined`"

**Evidence:** `ls tests/knowledge/test_engineering_standards_api_pages.py` returns no match. W1-A is `status: OPEN` (#2586) and unimplemented; only `test_ocimf_tandem_*.py`, `test_batch_pack_2.py`, `test_embeddings_spike.py`, `test_inventory_readiness.py` exist in `tests/knowledge/`.

**Impact:** If W3-A is implemented before W1-A lands (perfectly possible given both are OPEN siblings being executed in parallel), the import will fail at collection time with `ModuleNotFoundError`. The AC for W3-A would be uncompletable through no fault of the W3-A implementer. The plan does not specify a fallback (e.g., "if W1-A test file is absent, define the constant locally and add a TODO to migrate-on-W1-A-landing").

**Fix:** Amend line 291 to: "`word-count constant imported from W1-A's test file when present; if W1-A not yet landed, define `MAX_BODY_WORDS = 500` locally with a `# TODO: migrate to shared constant once W1-A lands` comment.`" Or make W1-A a hard dependency in the AC, but that re-introduces ordering risk.

---

### F3 — MINOR — Body header says "8-10 priority documents" but every downstream artifact is 10

**Location:** Plan line 31:
> "The 8-10 priority ABS documents biased toward floating production, offshore standards, subsea, materials/welding, and survey:"

**Evidence:** The Standards table at lines 33-44 has exactly **10** rows. The Artifact Map (lines 182-191) lists 10 wiki pages. Files-to-Change creates 10 wiki pages. TDD parametrization is 10. AC says "All ten new wiki pages exist". Risks "Open: Which 10?" enumerates 10. The "8-10" in the section header is the only mention of a range; everything else is fixed at 10.

The user prompt for this review actually says "~8 picks; 29 raw PDFs" — confirming there's a planning-vs-prompt drift on the count too. The plan settles on 10; the user prompt expected ~8.

**Impact:** Soft inconsistency. Reviewer skimming the resource-intelligence section sees "8-10" and may assume the count is undecided; downstream sections then commit to 10 without explicitly resolving the upper bound. Materially the work is 10 pages (matches W1-A and W2-A at 10 each), so the choice is defensible — the issue is the prose drift.

**Fix:** Line 31 should read "The **10** priority ABS documents..." Add a one-sentence rationale: "10 chosen to match W1-A/W2-A T2 sizing precedent."

---

### F4 — MINOR — `abs_part_section` is documented as a "frontmatter field" but its testability rests on a weak `null`-vs-absent distinction

**Location:** Plan line 230 (pseudocode), line 289 (TDD `test_part_section_only_on_multipart_rules`), line 340 (Risks).

**Evidence:** Pseudocode line 230 declares the field as `abs_part_section: <"Part 3" | "Pt. 3 / Sec. 4" | null>`. Test description at line 289 says "only the three `abs-rules-*.md` pages carry `abs_part_section`; the seven Guide / GN pages do NOT". Risks line 340 frames it as a frontmatter field on three pages, null on seven.

**Issue:** YAML frontmatter parsers treat `key: null` as the key being **present** with value `None`. The pseudocode shows `null` as a valid value, but the test asserts the seven Guide/GN pages "do NOT" carry the field. A page with `abs_part_section: null` would FAIL the test as currently described, but the pseudocode tells the implementer to write `null`. This is a contradictory contract.

**Impact:** A literal implementer following the pseudocode will set `abs_part_section: null` on seven pages; the test will then fail because `'abs_part_section' in frontmatter` is True. The "field" is testable, but the test definition disagrees with the pseudocode.

**Fix:** Resolve to one of: (a) require absence on Guide/GN pages (drop `null` from the pseudocode allowed-values list — Rules pages have a string, Guide/GN omit the key entirely); or (b) require the key on all 10 pages, with `null` on Guide/GN, and rewrite the test to assert "the three abs-rules pages have a non-null string; the seven non-rules pages have the key set to null". Option (a) is simpler and matches the test assertion as written.

---

### F5 — MINOR — `test_citation_schema_resolvable` revision-equality contract is brittle for the Rules pages

**Location:** Plan AC line 310-312 (Citation downstream-resolution check) and TDD line 294 (`test_citation_schema_resolvable`).

**Evidence:** Plan correctly notes (line 310) that `validate_citation` does literal-equality on the revision string. The Rules pages are pinned to year `"2014"` (Offshore + CoC) and `"2016"` (Steel Vessels). However, ABS Rules books receive **annual notice updates** — the corpus already contains 5 corrigenda/notice PDFs in `Notices/` that amend the 2014 base text within the 2014 publication year. `INDEX.md` distinguishes "2014 base" from "2014 + Notice 1". A future calc-caller that constructs `Citation(code_id="abs-rules-offshore-installations", revision="2014 + Notice 1")` against a frontmatter `revision: "2014"` will fail validation despite citing the same logical document.

**Impact:** Forces calc-callers into either (a) lossy revision strings that drop notice information, or (b) literal-match strings that don't survive a notice-revision update. The Risks section (line 347) acknowledges that corrigenda are added to `sources` but doesn't address how `revision` reconciles. The W3-A scope decides "frontmatter pins to 2014; corrigenda enumerated in `sources`" but the Citation contract has only one `revision` field.

**Fix:** Either (a) add an explicit "revision-discipline-for-Rules" sub-section noting that calc-callers MUST cite the unamended base year (`"2014"`) and rely on `sources` for notice traceability, OR (b) flag this as a known schema limitation and file a follow-up against `digitalmodel/src/digitalmodel/citations/schema.py` for an optional `revision_amendments: list[str]` field. Either keeps the test passing; today's plan leaves the pattern undefined.

---

### F6 — MINOR — `revision_source` and `public_url` fields are introduced in pseudocode but not in the engineering-standards CLAUDE.md schema or any test

**Location:** Plan line 222-224 (pseudocode):
> ```
> revision_source: "<URL or '/mnt/ace path' or 'publisher catalog pointer'>"
> verified_on: 2026-05-02
> public_url: <eagle.org canonical URL when known>
> ```

**Evidence:** `knowledge/wikis/engineering-standards/CLAUDE.md` defines: `code_id`, `publisher`, `revision`, `jurisdiction`, `supersedes`. The plan introduces three additional non-standard fields (`revision_source`, `verified_on`, `public_url`) — none are in the schema, none are in any AC, none are tested. They're "nice-to-have" but the implementer has no contract that says they must be present, must be of any particular type, or must validate.

**Impact:** Zero failure mode (these are accretive), but the plan creates frontmatter inconsistency that may drift across 10 pages: page 1 may have `verified_on: 2026-05-02`, page 2 may have `verified_date: 2026-05-02` or omit it. The W2-A precedent likely faces the same issue (the plan claims to inherit W2-A pseudocode "verbatim"); reviewer should check whether W2-A added schema-level enforcement.

**Fix:** Either (a) add `test_optional_field_consistency` that asserts these fields are present on all 10 pages with consistent shape, OR (b) demote them to "may be omitted" in the pseudocode comment so the implementer can skip them when source isn't verifiable. Option (a) makes the page set self-documenting and survives audit drift; option (b) is faster.

---

## Adversarial pattern hunt

| Pattern | Result |
|---|---|
| Past-tense drift | None (V10) |
| `#2471` over-cite as generalized path-sanction | None — plan correctly scopes to CSA-Z276-only |
| `llm-wiki.<dotted>` poison path (per memory) | None — `llm-wiki` appears as repo-name only, no dotted-path imports |
| `--no-verify` / sandbox bypass language | None |
| Self-approve markers (`status:plan-approved` set in plan) | None — plan is `status: draft` |
| Plan claims gates/tests passed | None — all AC are forward-looking |
| Inheritance of W1-A's #2471 over-cite | **Correctly NOT inherited** — plan flags W1-A's defect at lines 8 and 58 as a follow-up correction, does not propagate it |
| Wrong wiki domain (`engineering/wiki/standards/`) | None — all 10 pages route to `engineering-standards/wiki/standards/` per CLAUDE.md schema |
| Disk path mismatches | None — all 10 picks resolved to on-disk files (V3) |
| Ledger-form vs wiki-form ID divergence ignored | **Pre-empted at line 313, 346** — `ledger_id` frontmatter key bridges the two; explicit risk-and-mitigation |
| Cross-wiki collision risk silently inherited from W2-A | None — plan explicitly notes "INVERSE of W2-A" (line 343, ZERO pre-existing ABS pages) and `test_code_id_unique_across_wiki_domains` is asserted as vacuous-but-guarded |

---

## Verdict

**MINOR — 6 findings.** All are correctable in a v2 revision; none block plan-approval in principle.

Plan is technically sound, framing-compliant (CLAUDE.md schema as path-sanction; #2471 correctly scoped to CSA-only historical origin), and evidence is reproducibly verified. The four MINOR findings (F2, F3, F4, F5, F6) are tightenings; F1 is a stale-prose fix. The plan correctly differentiates itself from W1-A's #2471 over-cite (the W1-A plan still has the defect at its line 9 — that is W1-A's problem, not W3-A's).

The novel-for-W3-A risks (multi-part rule-book numbering, multi-edition revision selection, corpus-vs-recognized-canon scope-down) are explicitly enumerated in the Risks section and have stated mitigations — although F4 surfaces a contradiction in the `abs_part_section` testability and F5 surfaces a brittle revision-equality contract for Rules pages.

The user prompt asked whether `abs_part_section` is "actually a frontmatter contract addition or just a string field". Answer: **it's a string field documented in pseudocode and asserted by `test_part_section_only_on_multipart_rules`, but the plan's pseudocode allows `null` as a value while the test asserts absence — these disagree (F4).** The field is testable in principle, but the contract as written is internally inconsistent.

---

## Verdict line

**VERDICT: MINOR**
**MAJOR_COUNT: 0**
**MINOR_COUNT: 6**
