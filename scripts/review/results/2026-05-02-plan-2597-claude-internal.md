# Adversarial Review — Plan #2597 W3-D Engineering Wiki Riser Expansion (Claude internal)

**Reviewer:** Claude (Opus 4.7, 1M context)
**Plan:** `docs/plans/2026-05-02-issue-2597-llm-wiki-W3D-engineering-riser-expansion.md`
**Issue:** #2597 (OPEN, verified)
**Date:** 2026-05-02
**Stance:** standard 7-clause adversarial; defect-hunt, not charitable read.

## Verdict: MAJOR

**MAJOR_COUNT: 2**
**MINOR_COUNT: 5**

The plan is well-grounded in resource intelligence and reproduces W1-D's shape faithfully, but two structural defects make it not-yet-approvable: (1) the boundary-discipline regex test as written cannot distinguish dominant-topic violations from legitimate adjacency mentions and is calibrated to a threshold that is both too tight and too loose simultaneously, and (2) the "forward-reference comments" pattern for ISO 19901-7 / DNV-OS-F201 is a known source-of-truth footgun across W3-D × W3-B sibling-plan boundary that the plan does not concretize into a falsifiable test or a deletion checklist.

---

## P1 (MAJOR) — must fix before approval

### P1-1. Scope-creep regex (`test_no_scope_creep_into_pipeline_mooring_umbilical`) is mis-calibrated for both directions

**Where:** TDD Test List row 7, Risk section "scope creep into pipeline / mooring / umbilical", Acceptance Criteria bullet "no new page will broaden scope into pipelines, mooring, or umbilicals".

**The plan asserts** that limiting `pipeline | mooring | umbilical` to ≤3 occurrences per page, plus banning H2/H3 sections titled with those words, suffices to enforce the boundary. **This is wrong on both ends:**

- **Too tight (false-positive risk).** Riser-engineering pages legitimately discuss **riser-flowline-jumper interface**, **SCR-pipeline tie-in**, **riser-mooring shared-pollution scenarios** (cf. `mooring-line-failure-physics.md` already on disk), **umbilical-attached-to-riser bundle** configurations (`hybrid-riser-tower.md` SLOR includes a power/control umbilical), and **flexible-riser-end-connector to PLET/PLEM pipeline manifold**. Of the 8 proposed pages, at least three (`riser-configurations.md`, `flexible-riser-design.md`, `hybrid-riser-tower.md`) cannot honestly describe their topology without 4+ occurrences of either `pipeline` or `umbilical`. The plan's own Resource Intelligence cites `2H/2006-08-07 Guidelines for Integrity Monitoring of Unbonded Flexible Pipe` and `client_projects/energy_drilling_riser/{Diverter and riser man.pdf}` — material that explicitly couples flexible-pipe and riser. A ≤3-cap forces authors to either (a) write evasive prose that obscures real engineering, or (b) silently cheat by using synonyms (`hose`, `subsea cable`, `flowline transition`) that defeat the test.

- **Too loose (false-negative risk).** Conversely, a page can sit at 0 occurrences of those three nouns and still be a scope violation by re-covering, e.g., **mooring fatigue** under the synonym "tendon fatigue" or **pipeline free-span VIV** under the synonym "spanned-section VIV", or by re-covering the existing `viv-riser-fatigue.md` (same-domain, not cross-domain). The plan separately introduces `test_no_redundant_viv_content_in_new_pages` for the second case, but the cross-domain synonym attack is unguarded.

**Suggested fix.** Replace the count-threshold heuristic with a **section-dominance test**:
1. Tokenise the page into top-level sections. For each section, compute the riser-vs-non-riser keyword ratio. **If any section's `pipeline|mooring|umbilical` keyword count exceeds the riser keyword count, fail.**
2. Whitelist explicit boundary callouts: a `## Scope` or `## Out of Scope` section with `pipeline|mooring|umbilical` is allowed to exceed the cap.
3. Drop the per-page total-count cap entirely — it punishes legitimate adjacency.
4. Add a positive-presence test: every page must contain ≥3 occurrences of `riser` (or a riser-typology subterm: `SCR`, `TTR`, `flexible riser`, `hybrid tower`, `drilling riser`) to prove riser is the dominant topic.

This shift turns the test from a fragile word-counter into a topical-dominance check, which is what the prompt actually demands.

### P1-2. "Forward-reference comments" to W3-B sibling is an unbounded-debt footgun without a deletion checklist

**Where:** Standards table row "DNV-OS-F201", Risk section "ISO 19901-7 W3-B sibling not yet a standards page", and the Pseudocode section "MUST NOT enumerate specific thresholds, formulas, or code clauses".

**The plan asserts** that 8 new concept pages will cite ISO 19901-7 and DNV-OS-F201 by title+URL with "forward-reference comments" pointing at the W3-B sibling plan, then "if/when W3-B promotes that standards page, a follow-up edit will rewrite the references to relative `../standards/` links." **This pattern has three latent defects:**

1. **The forward-reference comment surface is undefined.** Nothing in Pseudocode, Files-to-Change, or TDD specifies *what* the comment looks like, *where* in the page it lives (frontmatter? body? HTML comment?), or *what* string a future cleanup script greps for. Without a canonical marker, the "follow-up edit" step at W3-B promotion is a free-text search-and-replace, which is exactly the class of debt the LLM-wiki document-intelligence governance memo (#2205) was designed to prevent.

2. **W3-B is a sibling plan, not a sibling implementation.** The plan's prose says "W3-B sibling per prompt — currently planned, not yet codified at the time of writing". As I verified, **`knowledge/wikis/engineering/wiki/standards/iso-19901-7.md` and `dnv-os-f201.md` do not exist** (plain `ls` errors). If W3-B never lands — which is plausible: the parent #2540 wave epic has 0 children that have been approved at the time of writing — these forward-references become permanent dangling pointers. Tier-1 link-resolution gates won't catch them because they're prose-citations, not markdown links.

3. **Inconsistency with calc-citation contract.** `.claude/rules/calc-citation-contract.md` says concept pages "name standards bodies and titles by reference" — fine — but mandates that **calc-side citations be fail-closed at calc time** when wiki pages are missing. A forward-reference comment in a concept page is not a calc-side citation; it's a *promise* of one. Future calc modules trying to cite via the new concept pages will run into a missing-standards-page resolution error if they expect transitive resolution. The plan does not state explicitly that calc-side citations remain blocked until W3-B lands.

**Suggested fix.** Make forward-references concrete and falsifiable:
1. Define a single canonical marker — e.g., HTML comment `<!-- TODO(W3-B): replace with [[../standards/iso-19901-7]] when standards page lands -->` — and add a TDD test that every external standards-URL in a new page is paired with such a marker (or, for already-codified standards like DNV-RP-C203, with a `[[../standards/dnv-rp-c203]]` wikilink instead).
2. Add a corresponding lint script (or extend `tests/knowledge/test_engineering_riser_expansion.py`) that emits a count of pending forward-references — so a future plan reviewing W3-B's promotion can run the script, get the list of files needing update, and discharge them deterministically.
3. Add an explicit Acceptance-Criteria bullet: "no calc-module is expected to cite these new concept pages as standards-resolution targets until W3-B lands codified standards pages — calc-citation-contract continues to require direct standards-page resolution."

Without these, the cleanup work is ambiguous and the plan creates technical debt scaled by 8 pages × 2-3 standards each.

---

## P2 (MINOR) — fix opportunistically

### P2-1. `viv-riser-fatigue.md` already cross-mentions pipeline — the boundary may already be muddied

**Where:** Pseudocode "boundary discipline: SCR page must NOT re-cover VIV fatigue mechanics".

I verified `grep -ic "pipeline\|flowline" knowledge/wikis/engineering/wiki/concepts/viv-riser-fatigue.md` = **2 hits**. So the existing canonical riser page itself violates the boundary the new pages are supposed to enforce. The plan should add a one-line maintenance note: "if reviewer of new pages identifies the existing 2 pipeline/flowline mentions in `viv-riser-fatigue.md` as material, those should be removed in the same PR."

### P2-2. Plan-tense drift inside the plan itself (recursive class)

**Where:** TDD test names and Acceptance Criteria.

The plan correctly uses **future tense in Acceptance Criteria** ("will exist", "will pass") per `feedback_plan_past_tense_artifact_claims.md`. **However**, the Resource Intelligence section uses present-tense verbs that could read as completed claims to a casual reviewer: "This plan creates **concept pages**" (line 39), "This plan **does NOT extract** from these PDFs" (line 76), "Adding these concept pages **does not** by itself create a cross-ref" (line 173). These are factually fine — they describe the plan's design decisions — but the same memo notes that adversarial reviewers calibrate on past/present tense. Recommend: switch all such phrasings to "this plan will create" / "this plan will not extract" / "adding these concept pages will not …" for tense-discipline consistency with the rest of the document. (Minor, prose-quality only.)

### P2-3. `test_no_redundant_viv_content_in_new_pages` is keyword-list, not semantic

**Where:** TDD Test List row 15.

The test's regex match for "S-N curve tables, DFF tables, wake-interference S/D tables, rainflow-counting prose" is keyword-fragile. A page can re-introduce VIV content by writing "Strouhal-frequency-based fatigue damage accumulation" without using the word "S-N", "DFF", or "rainflow", and pass the test. Suggest extending the keyword list to include `Strouhal`, `lock-in`, `mode-shape participation`, `Iwan-Blevins`, or — more robustly — capping the per-page count of the noun **fatigue** to ≤5 occurrences (since `viv-riser-fatigue.md` is the canonical fatigue page, new design-state pages should reference fatigue in passing only).

### P2-4. ISO 19901-7 mis-attribution

**Where:** Standards table row "ISO 19901-7 (Stationkeeping — also covers riser-vessel interface in revised editions)".

ISO 19901-7 is **stationkeeping for offshore structures** (mooring + DP), not riser. The "also covers riser-vessel interface in revised editions" qualifier is non-canonical — Part 7 covers stationkeeping; **ISO 13624 is the marine drilling-riser part** in the 13624 family, **ISO 13628 is the production-riser family**. Plan claims a cross-link to W3-B for ISO 19901-7 specifically, but if W3-B is the riser-standards plan it should be carrying ISO 13624 / 13628 references, not 19901-7. Suggest re-checking the prompt's claim that "W3-B handles ISO 19901-7 family" — this may be a wave-epic oversight, not a plan defect, but the plan should not propagate the mis-attribution into 8 pages.

### P2-5. Page-count delta arithmetic in Pseudocode is internally inconsistent

**Where:** Resource Intelligence ("82 → 90 (+8)") and Pseudocode ("Concepts (32 pages) → (40 pages)").

The arithmetic is fine — 8 new concept pages, all into Concepts table, so 32 → 40 and 82 → 90 are correct **only if** no pages move between tables and no orphaned pages get reclassified. But the Resource Intelligence also notes `ocimf-tandem-mooring.md` "exists on disk but is not yet in `index.md` standards table". If a parallel-running plan promotes `ocimf-tandem-mooring.md` into the standards table during this work (it's currently mid-flight per recent commits — `33214dae8 docs(plans): draft #2559 OCIMF tandem wiki promotion plan`), the arithmetic shifts. Plan should add a defensive note: "if `index.md` is bumped by another plan during W3-D execution, re-derive the counts at execution time rather than committing to 90 / (40 pages) literally."

---

## What the plan got right (calibration)

- **Resource Intelligence is dense and verifiable.** I sampled 7 of 11 cited sources (file paths under `knowledge/wikis/engineering/wiki/`, `/mnt/ace/2H/`, `/mnt/ace/digitalmodel/docs/risers/literature/`, `/mnt/ace/frontierdeepwater/Engineering/risers/Airgap/`, the four GitHub issues #2540/#2588/#2589/#2592, and the digitalmodel `drilling_riser/` package). All 7 verified. The "57 VIV hits, 2 SCR, 0 TTR, 0 hybrid riser, 0 J-tube, 0 wave-induced" terminology baseline reproduced **exactly** under my own grep — strong gap signal grounding.
- **One existing riser page count claim is correct.** `find knowledge/wikis/engineering/wiki -iname "*riser*" -type f` returns exactly `concepts/viv-riser-fatigue.md` — matches the plan's "1 existing riser page" claim.
- **2H Offshore corpus claim is verified.** `ls /mnt/ace/2H/` returns 32 entries; the plan's enumeration of 10 specific subdirectories cross-checks against the actual listing without invention. (Minor: `/mnt/ace/2H/0011 Joint Database`, `31103 Moho Nord`, `31486 Mode Normalization` are not riser-specific and were correctly excluded; `31404 FMOG King SCR Detailed Design` exists and is riser-specific but was *omitted* from the plan's enumeration — a missed opportunity but not a defect, since the plan's claim is "32 directories under `/mnt/ace/2H/` including" rather than exhaustive.)
- **#2471 is correctly cited as routing-principle, not as path-sanction.** Plan says "the #2471-sanctioned `wiki/standards/<code-id>.md` routing principle" and explicitly defers standards-page production to a future plan. This matches `project_wiki_standards_path_decision.md` memory: "**#2471 is CSA-Z276-only** (verified 2026-04-25) … general offshore/marine substrate now scoped to aceengineer-strategy aces-#4". Plan does NOT misuse #2471 as general-path sanction.
- **VIV collision handling is adequate.** 57 VIV hits in `viv-riser-fatigue.md`, plan adds explicit boundary callouts in 4 of the 8 new pages (`steel-catenary-riser-design`, `top-tensioned-riser-design`, `riser-soil-interaction`, `riser-global-analysis-load-cases`) plus the "Related design pages" reverse pointer block on the existing page. The collision is handled, modulo the keyword-fragility concern in P2-3.
- **Future-tense discipline holds in Acceptance Criteria.** No "we have created" / "the new page exists" past-tense drift in Acceptance Criteria. (Minor present-tense items captured in P2-2.)
- **Hidden-assumption check.** I scanned for hidden assumptions: (a) plan does not assume W3-B will land — it explicitly handles W3-B-absent case; (b) plan does not assume engineering-wiki seed file exists — it explicitly notes "no formal seed YAML"; (c) plan does not assume the digitalmodel calc-side will cite the new pages — explicitly defers to follow-up; (d) plan does not assume `index.md` page_count of 82 is correct — provides arithmetic derivation. All major hidden assumptions are surfaced. The only one missing is the parallel-plan-arithmetic interaction noted in P2-5.
- **Issue verification clean.** All 5 cited GitHub issues (#2540, #2588, #2589, #2592, #2597) verify as OPEN with the titles claimed.

---

## Summary of required fixes for APPROVE

1. (**P1-1**) Replace per-page word-count cap on `pipeline|mooring|umbilical` with a section-dominance keyword-ratio test plus a positive `riser`-presence assertion.
2. (**P1-2**) Define a canonical forward-reference marker (HTML comment with `TODO(W3-B):` token) and add a TDD test plus a calc-citation deferral acceptance bullet.
3. (Optional, P2 cluster) Tighten the VIV-redundancy keyword list, fix ISO 19901-7 attribution if the prompt's W3-B framing is wrong, switch present-tense Resource-Intelligence verbs to future tense, and add a defensive arithmetic note for parallel-plan interaction.

With P1-1 and P1-2 addressed, the plan moves to APPROVE. P2 items can be folded into implementation without re-review.
