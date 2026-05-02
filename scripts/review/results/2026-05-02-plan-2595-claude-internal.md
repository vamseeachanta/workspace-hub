# Adversarial Review — Plan #2595 (W3-B ISO 19900-series)

- **Plan:** `docs/plans/2026-05-02-issue-2595-llm-wiki-W3B-engineering-standards-iso-19900.md`
- **Issue:** [#2595](https://github.com/vamseeachanta/workspace-hub/issues/2595) — OPEN (verified `gh issue view 2595` 2026-05-02)
- **Reviewer:** Claude (single-author, internal). Codex unavailable per `feedback_codex_cli_0_124_upstream_regression.md`; Gemini unavailable per `feedback_gemini_sandbox_overlay_blindness.md`.
- **Stance:** 7-clause adversarial. Charitable reading is malpractice; assume defects exist until proven absent.
- **Round:** r1

---

## Verdict: MINOR

- **MAJOR:** 0
- **MINOR:** 5

The plan is well-grounded: cited-issue states verify, the on-disk-all-drafts critical caveat verifies, the W1-C taxonomy cross-link verifies (W1-C plan lines 40/170/235 explicitly adopt the ISO 19900-series taxonomy as the audit's verifiable anchor — the plan is not over-claiming the dependency), the #2471-NOT-cited boundary holds, and the past-tense drift hunt comes up clean. The defects below are real but are scoped to (a) arithmetic that is wrong but self-mitigated by the "recompute live" AC, (b) a contract field that exists only as de-facto convention, (c) a Risks-section claim that the test contract does not actually enforce, (d) a partial deny-list, and (e) an under-spec ledger ID-casing convention. None of these warrant blocking.

---

## Verification ledger (required checks)

### 1. Full plan read — DONE

### 2. Critical caveat: "every on-disk 19900-series PDF is a draft" — VERIFIED ✅

`find /mnt/ace/O\&G-Standards/ISO -iname "*1990*"` returns 22 files (plan claims 24; the discrepancy is the plan inadvertently included a glob-mistake match `JH22419905K0.pdf` and `N328A_Terminology_for_19900_series.pdf` in its inventory — see MINOR-5). All matched files carry `DIS`, `FDIS`, `CD`, `markup`, `TR`, `Pre_Publication_Comments`, `Submitted`, `Future`, `Terminology`, or comparison-doc markers. **No file is a published edition.** The plan's critical observation at lines 127-128 is confirmed verbatim. The `revision_source` MUST-cite-portal contract (test `test_frontmatter_distinguishes_draft_vs_published_revision`) is the correct mitigation.

### 3. #2471 NOT-cited check — PASS ✅

Plan line 12 explicitly carves out: "**#2471 (CLOSED) codified the path-routing decision for CSA-Z276 specifically** ... it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple, not as ISO path authority." This matches memory `project_wiki_standards_path_decision.md` ("**#2471 is CSA-Z276-only** (verified 2026-04-25)"). The plan does not improperly invoke #2471 as ISO authority.

### 4. W1-C cross-link claim — VERIFIED ✅

Plan claim: "W1-C r1 review's MAJOR-3 fix replaced an unverifiable 'SUT taxonomy' with the **ISO 19900-series taxonomy** as the audit's verifiable priority anchor."

Verified in `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md`:
- Line 235: `MAJOR-3: replaced unverifiable SUT taxonomy with ISO 19900-series (19900/19901/19902/19903/19904/19905-1) as the verifiable external anchor.`
- Line 170: rationale-anchor list includes `ISO 19900-series part number (regex: '19900|19901|19902|19903|19904|19905-1')`
- Line 202: `test_audit_rationales_cite_required_anchors` enforces it
- Line 40: ISO 19900-series taxonomy named explicitly as "the verifiable external taxonomy anchor for priority rationale"

The W3-B plan's bidirectional dependency claim — that the wiki pages this plan creates are the resolution targets for the part numbers W1-C's audit will cite — is real and material.

**Note:** GitHub issue #2588's body still mentions the older "SUT taxonomy" basis (the issue body was not refreshed when the plan was revised). Not a defect of *this* plan, but worth flagging as upstream staleness if anyone reads the issue without the plan file.

### 5. Cited issues verified ✅

| Issue | Claimed state | Actual state |
|---|---|---|
| [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) | OPEN | OPEN ✅ |
| [#2586](https://github.com/vamseeachanta/workspace-hub/issues/2586) | OPEN | OPEN ✅ |
| [#2588](https://github.com/vamseeachanta/workspace-hub/issues/2588) | OPEN | OPEN ✅ |
| [#2590](https://github.com/vamseeachanta/workspace-hub/issues/2590) | OPEN | OPEN ✅ |
| [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) | CLOSED | CLOSED ✅ |
| [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) | CLOSED | (not re-verified; previously in scope of bounded preview pattern) |

All hyperlinks render correctly per memory `feedback_inline_gh_issue_url.md`.

### 6. `revision_source` field — REAL AS DE-FACTO CONVENTION, NOT FORMAL SCHEMA — see MINOR-2

`knowledge/wikis/engineering-standards/CLAUDE.md` schema "Standards page extra fields" table lists `code_id`, `publisher`, `revision`, `jurisdiction`, `supersedes` — **`revision_source` is NOT in the schema.** It exists in `api-17e.md` (the lone pre-existing standards page) as `revision_source: public publisher metadata not bundled with Elements corpus`, so the field is a de-facto convention but not formally schemaed. The plan introduces a new contract on a field whose schema authority is one previous file. See MINOR-2.

### 7. Series cross-reference budget "≤2 normative siblings per part page" — UNDER-ENFORCED — see MINOR-3

Plan Risks section line 324 commits: "each part page lists ONLY the umbrella + the ≤2 most directly normative siblings". The Test List enforces only the umbrella back-reference (`test_umbrella_cross_reference`) — there is **no test that the per-page cross-ref count is ≤3** (umbrella + ≤2). Reviewers manually inspect, per Risks. This makes the contract reviewer-discretional rather than test-enforced, while everything else in the plan is test-enforced. See MINOR-3.

### 8. page_count mismatch — VERIFIED, FIXABLE-AT-WRITE-TIME ✅

`grep page_count knowledge/wikis/engineering-standards/wiki/index.md` → `page_count: 5`.

Live `find` count → **9 markdown files**. The index is out of date by 4. Plan claim (line 51): "present-tense floor before this plan: 5 sources + 1 standards page (`api-17e`) = 6." Even the plan's *own* present-tense floor undercounts (actual is 9, not 6 — the plan miscounts because it conflates `source_count` with `page_count` and misses that 4 additional pages exist outside the `sources/` and `standards/` subdirs). The plan's mitigation is correct: AC line 293 mandates recompute against live state at write-time, so the implementation step will not propagate this miscount. See MINOR-1 (the inconsistency is real but the AC saves it).

### 9. Past-tense drift + adversarial hunt — PASS ✅

- "this plan WILL create" / "the implementation step MUST recompute" / "to be filled at plan-review handoff" — all future tense. No "has been added" / "the page now contains" violations per `feedback_plan_past_tense_artifact_claims.md`.
- Plan does NOT propose self-approval; explicitly cites `feedback_never_offer_to_self_label_plan_approved.md`.
- Plan does NOT pre-authorize downstream agents.
- Issue field at line 6 is honest: "_not yet filed — this plan file is the deliverable; issue creation is downstream of plan-review_".

---

## Findings

### MINOR-1: Page-count arithmetic in resource-intel section is wrong, but mitigated by recompute-AC

**Where:** plan line 51 (resource-intel "LLM Wiki pages consulted") states "present-tense floor before this plan: 5 sources + 1 standards page (`api-17e`) = 6".

**Defect:** the actual live count is 9 markdown files in `wiki/` (`index.md` + 5 sources + 1 standards + 2 others including `log.md`, `overview.md` or similar — confirmed via `find knowledge/wikis/engineering-standards/wiki -name "*.md" | wc -l` = 9). The frontmatter `page_count: 5` itself is stale — it's tracking source count, not page count. Plan's own recompute-AC on line 293 catches this at write-time, but the resource-intel arithmetic that downstream agents may quote is wrong.

**Why it matters:** if a parallel-session agent reads the plan and trusts the "= 6" floor for some other arithmetic, drift propagates. Memory `feedback_isolated_clone_dispatch_race.md` says cross-session reads of plan artifacts are real.

**Suggested fix:** in resource-intel, replace "present-tense floor before this plan: ... = 6" with "present-tense floor before this plan: 9 (live count via `find ... | wc -l`); the index.md `page_count: 5` field is itself stale and will be corrected by the implementation step's live recompute". Optional: add an AC explicitly fixing the stale `page_count: 5` value as part of this plan's index update.

### MINOR-2: `revision_source` field is convention-only, not formally schemaed

**Where:** plan lines 200-202 (pseudocode), AC line 296 (`test_frontmatter_distinguishes_draft_vs_published_revision`).

**Defect:** the W3-B contract enforces `revision_source` semantics (must be portal URL, not draft path) on a field that is **not** listed in `engineering-standards/CLAUDE.md` schema "Standards page extra fields". The only precedent is `api-17e.md`'s single occurrence. The plan proposes 9 new pages all using the field, but does not propose updating the schema table in `engineering-standards/CLAUDE.md` to formalize it. This creates a contract that is enforced by tests in this plan but invisible to a future schema reader.

**Why it matters:** the calc-citation-contract rule lives in `.claude/rules/`; the wiki schema lives in `engineering-standards/CLAUDE.md`. Splitting a frontmatter contract across them invites future drift (e.g., a later W4 plan dropping `revision_source` because the schema doesn't require it). When W1-A and W2-A also use this field (likely — they share the `api-17e` template), the field will become de-facto schemaed by usage but never formally promoted.

**Suggested fix:** add a small line item to "Files to Change" — `Modify | knowledge/wikis/engineering-standards/CLAUDE.md | Add 'revision_source' (required when revision != public-metadata-...) and 'verified_on' (required) to the Standards page extra fields table`. Alternatively, defer to a W4 follow-up but cite the deferral explicitly as an Open Question.

### MINOR-3: ≤2-cross-reference-budget is reviewer-only, not test-enforced

**Where:** Risks line 324 commits to "umbrella + ≤2 most directly normative siblings"; TDD test list lines 263-276 enforce only the umbrella back-reference.

**Defect:** the cross-reference budget cap is the largest claimed risk-mitigation in the plan ("If each part page lists every cross-reference, the body word count budget (≤500) blows. Mitigation: ..."). The mitigation is reviewer-discretional. Every other contract in the plan has a test (denylist, word-count, frontmatter, ledger, cross-wiki uniqueness, umbrella-ref). This one is the orphan.

**Why it matters:** asymmetric enforcement — plans that claim test-enforcement-by-default invite weakening. Once one contract is reviewer-only and stays green for a while, the next will be too. Memory `feedback_naive_secret_scan_false_positive_cascade.md` is a sibling pattern (test-enforcement gap leading to defect cascade).

**Suggested fix:** add a parametrized test `test_cross_reference_budget_bounded` — count `[[iso-...]]` wiki-link occurrences in body (excluding the page's own `code_id`); assert `count <= 3` (umbrella + ≤2). The umbrella page itself is exempted (it lists every part). Implementation is one regex + a counter in the existing test fixture.

### MINOR-4: `RAW_TELLTALE_PHRASES` denylist is incomplete for the 19905-1 .doc/.docx draft set

**Where:** TDD list lines 278 (denylist phrase enumeration).

**Defect:** the phrase list is drawn from "ISO publication front-matter conventions" (`"© ISO 20"`, `"All rights reserved"`, `"Case postale 56"`, `"INTERNATIONAL STANDARD ISO"`, etc.). However, the on-disk corpus for 19905-1 includes `.doc`/`.docx` working drafts (`19905-1_(E)_CD_G-2007-03-20.doc`, `Pre_Publication_Comments_on_ISO_FDIS_19905-1-at-2011-04-29.doc`, `ISO_19905-1_2012_vs_FDIS_2015.docx`). Working drafts often carry **track-changes annotations**, **ballot comments**, and **FDIS submission cover sheets** that have different telltale strings (e.g., `"FDIS ballot"`, `"Comment number"`, `"Editing committee"`, `"ISO/TC 67/SC 7"`). A drafter copy-pasting from a `.doc` working draft would not trigger the cover-page denylist.

**Why it matters:** the no-raw-text contract is the load-bearing safeguard for vendor-derivative deny-list compliance per #2482. A partial denylist that only catches published-cover patterns leaves working-draft leakage uncaught.

**Suggested fix:** extend `RAW_TELLTALE_PHRASES` with a working-draft sub-section: `"FDIS ballot"`, `"DIS comment"`, `"ISO/TC 67/SC 7"`, `"Editing committee"`, `"track changes"` (or move detection to a higher signal-to-noise heuristic — see Risks acknowledgement of shingle-match as W2-B follow-up). Minimum viable: add the TC/SC code `"ISO/TC 67"` and `"FDIS ballot"`; both are stable across decades.

### MINOR-5: Ledger ID casing convention is under-specified

**Where:** plan line 250 (Files to Change ledger row), AC line 292.

**Defect:** plan ledger row IDs are written `ISO-19900`, `ISO-19901-1`, `ISO-19902`, etc. (uppercase ISO prefix), but `code_id` frontmatter is lowercase-kebab `iso-19900`, `iso-19901-1`, `iso-19902`. The `test_ledger_alignment` test at line 273 says "every page's `code_id` resolves to a row in `data/document-index/standards-transfer-ledger.yaml`". If the ledger row's `id:` field is `ISO-19900` and the wiki `code_id` is `iso-19900`, the test must do case-insensitive comparison or one side must change. Plan does not specify which.

**Why it matters:** memory `feedback_llm_wiki_hyphen_module_path_pattern.md` documents recurrent hyphen/case casing collisions that bit three 2026-04-24 plans. Same risk class. Without a casing-rule clarification, the test will either be over-permissive (case-insensitive, hides drift) or fail at implementation time.

**Suggested fix:** add a one-line normalization rule to the resource-intel section or AC: "ledger `id:` values match wiki `code_id` byte-for-byte (lowercase-kebab; e.g., `iso-19901-7`, not `ISO-19901-7`)." Update the Files to Change table row to render the IDs in lowercase. Verify W2-A's existing ledger pattern (DNV) for parity — if W2-A uses uppercase, propose a unifying decision; if lowercase, this plan must match.

---

## What I checked and did NOT find

- No past-tense drift (memory `feedback_plan_past_tense_artifact_claims.md`).
- No self-approval language; no pre-authorization of downstream agents (memory `feedback_never_offer_to_self_label_plan_approved.md`).
- No Iron-Law violations (no `--no-verify`, no `git reset --hard` in pseudocode).
- No invalid `gh issue` URL formatting; all `#NNNN` references render as Markdown links.
- No claim of work performed; the issue field correctly states "_not yet filed_".
- No worktree-pollution risk (no `.claude/worktrees/` references).
- No path-pattern collision (`iso-19900-series`, `iso-19901-7` are clean lowercase-kebab; no `iso_19901-7` or `iso19901_7` anywhere).
- No phantom-source citations; all 11 sources in the source-counter line 152 verify.

---

## Recommended disposition

**MINOR — proceed to user-approval gate after addressing the 5 minor findings.**

The five MINORs cluster as: arithmetic correction (MINOR-1), one schema-update line item (MINOR-2), one extra test (MINOR-3), denylist extension (MINOR-4), one-line casing rule (MINOR-5). All addressable in a single revision pass without restructuring. None blocks the plan's central contract or the bidirectional W1-C dependency.

**Provenance:** Single-author Claude r1 review per memory `feedback_permission_gate_blocks_cross_review.md`. Codex v0.124.0 stdin-hang #2479 blocks Codex; Gemini sandbox cwd=/tmp blocks Gemini. Cross-provider review is not a hard gate; if codex-cli 0.123.0 downgrade lands before implementation, an r2 cross-review SHOULD be dispatched.
