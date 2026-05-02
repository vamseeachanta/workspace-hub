# Adversarial review — plan #2589 (naval-architecture wiki W1-D, 10 concept pages)

> **Reviewer:** Claude (internal, single-author fallback per memory `feedback_permission_gate_blocks_cross_review.md`)
> **Plan path:** `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md`
> **Plan SHA / status:** untracked working-tree draft on `main`, status `draft` (line 4)
> **Issue:** #2589 — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)"
> **Review date:** 2026-05-02
> **Stance:** adversarial — defects-until-disproven, no praise, every finding cites a quoted claim

---

## Affirmatively verified

The following claims were checked against ground truth and found to hold:

- **#2566 / #2568 issue states.** Both OPEN as of 2026-05-02 (`gh issue view`). Body excerpts in the plan (lines 113, 142–144) match the live issue bodies verbatim. Plan correctly identifies #2566 as a CI/test-validation gate (no wiki content overlap) and #2568 as reserving "advance, tactical diameter, turning diameter, and turn-rate response" terminology.
- **Existing concepts directory.** `find … concepts -name "*.md" | wc -l` → 13. Plan claims (line 119) 13 concept pages exist; matches.
- **Empty entities directory.** `ls knowledge/wikis/naval-architecture/wiki/entities/ 2>&1` → empty. Plan's claim (line 139) and `index.md:73` "No entity pages yet" match.
- **Standards page count.** `standards/` contains exactly one file (`steering-gear-rudder-stock-rule-crosswalk.md`), matching plan claim (line 26).
- **CLAUDE.md frontmatter schema.** Mandatory fields are `title`, `tags`, `added`, `last_updated`. The plan's TDD test list (line 240) matches the schema verbatim.
- **#2471 path-routing principle.** Plan correctly stays in `wiki/concepts/` and `wiki/entities/` and does NOT promote to `wiki/standards/`, consistent with memory `project_wiki_standards_path_decision.md`.
- **Future-tense discipline.** Spot-checked Acceptance Criteria (lines 254–265) — "will exist", "will cite", "will list" — passes the past-tense-drift test. Memory `feedback_plan_past_tense_artifact_claims.md` does not fire here.
- **Source URLs (partial).** `https://sname.org/principles-naval-architecture` — WebFetch confirmed real, three-volume layout matches plan claim (line 64). `https://ittc.info/` — WebFetch confirmed real top-level page, but procedure-number prefixes (`7.5-02-*`, `7.5-03-*`) NOT independently verified from the landing page (downloads index linked but not fetched).

---

## MAJOR findings

### M1 — Three of the ten new pages duplicate scope already present in `concepts/resistance-propulsion.md`

The plan acknowledges this risk on line 49 ("strong false-gap risk for a 'propulsors' or 'ship-resistance-components' subdivision") and on line 290 (boundary-page mitigation), but the mitigation is narrative only. It does NOT commit to (a) shrinking the existing page, (b) moving content out, or (c) defining a verifiable scope-disjointness test.

Concrete overlap (verified by reading `concepts/resistance-propulsion.md` lines 14–31):

| Existing bullet on resistance-propulsion.md | Proposed new page | Overlap severity |
|---|---|---|
| "Frictional / Residuary / Air / Appendage / Froude-number regime" (lines 16–20) | `concepts/ship-resistance-components.md` ("Frictional/wave-making/form/appendage/air decomposition; Froude scaling; ITTC 1957", line 221) | **near-total** — five of five bullets reappear |
| "Propeller theory — momentum + blade element theories" + "KT, KQ, eta vs J curves" + "Propeller-hull interaction — wake fraction, thrust deduction" (lines 24–26) | `concepts/propeller-theory.md` ("Momentum + blade-element theories, KT/KQ/J open-water, hull-propeller coefficients", line 223) | **near-total** — three of three bullets reappear |
| "FPP/CPP / Azimuth thrusters / Waterjets / Podded propulsion / Rudder-propellers" (lines 27–31) | `concepts/marine-propulsors.md` ("FPP/CPP/podded/waterjet/azimuth/contra-rotating overview", line 222) | **total** — five of five propulsor types reappear; plan adds only "contra-rotating" as net-new |

Why this matters: the plan currently treats `resistance-propulsion.md` as a "broad page" to be subdivided (line 49) but proposes only to ADD three new pages WITHOUT amending the existing one. The post-implementation state is two parallel descriptions of the same five propulsor types, two parallel descriptions of the same five resistance components, etc. — a textbook anti-pattern for wiki rot.

**Required fix:** the plan must either (a) explicitly move the five resistance-component bullets and the five propulsor-type bullets OUT of `resistance-propulsion.md` and into the new pages (then convert `resistance-propulsion.md` into an index/router page), OR (b) drop `ship-resistance-components.md`, `propeller-theory.md`, and `marine-propulsors.md` from this batch and re-scope the "broad-page" remediation to a separate plan. The TDD test list (lines 237–248) currently has NO test that detects redundant content between old and new pages — that test is missing and needed.

### M2 — Two more proposed pages duplicate scope present on `concepts/stability.md`

Verified by reading `concepts/stability.md` lines 19–20:

> "**Intact stability criteria** — IMO, SOLAS requirements for minimum stability"
> "**Damage stability** — stability after compartment flooding; SOLAS subdivision requirements"

Plan proposes new `concepts/intact-stability-criteria.md` and `concepts/damage-stability.md` (lines 219–220). The plan's coverage matrix (lines 75–76) marks intact stability as "partial — under stability.md" and damage as "gap (mention only)". That framing is defensible for damage (`stability.md` truly says only one bullet), but the plan does not address how the EXPANDED `intact-stability-criteria.md` page will be reconciled with the existing bullet, nor whether the `stability.md` mention should be retired or downgraded to a stub.

**Required fix:** add an explicit Files-to-Change row that AMENDS `concepts/stability.md` (e.g., reduces the intact-stability and damage-stability bullets to one-line pointers to the new pages). Without that, post-implementation state is again two-source-of-truth for IMO IS Code criteria.

### M3 — Reserved-phrase regex test will fail closed against `concepts/maneuvering-validation-metrics.md`, which already contains the reserved phrases

The plan's TDD test `test_no_reservation_overlap` (line 243) regex matches `\b(turning circle|tactical diameter|Nomoto)\b` against new page bodies and asserts zero matches. That is correct for **new** pages. But the plan's coverage table (line 82) says "Ship maneuvering basics" is "covered (#2564 pack)" with reservation "rate of turn, yaw, rudder", and "Turning circle / tactical diameter" (line 83) "**EXCLUDE**" with "**YES — #2568 reserves**".

Reading `concepts/maneuvering-validation-metrics.md` lines 18–25 reveals the existing page ALREADY contains:

> "**advance**: longitudinal displacement after rudder-command initiation"
> "**transfer**: lateral displacement"
> "**tactical diameter**: transfer at heading change of 180°"
> "**steady/final turning diameter**: diameter after transient turn stabilizes"

These are exactly the noun-phrases the plan asserts (line 145) #2568 reserves. So one of two things is true: (a) the plan's reservation analysis is wrong and #2568 does NOT exclusively reserve this terminology (because #2564 already used it on 2026-04-30), OR (b) the existing maneuvering-validation-metrics.md is in violation. The plan does not acknowledge or resolve this. The Open Questions section is silent on it.

**Required fix:** the plan must either (a) cite #2568's plan to confirm that pre-existing wiki content under #2564/#2567 is grandfathered (and document where that exemption is recorded), OR (b) acknowledge that "tactical diameter" already lives in the wiki and revise the test scope to "no NEW occurrences in the 10 new pages plus no expansion of existing occurrences in existing pages". As drafted, the test is not load-bearing because it does not test the actual collision surface.

### M4 — The "≥1 standards-body cross-reference per page" acceptance criterion silently risks promoting concept pages into de-facto standards pages

Acceptance criterion (line 255): "Each new page will cite ≥1 standards body (IMO / ITTC / IACS / SNAME) with stable URL or sibling source-page link."

Pseudocode (line 194): "Standards / References — ≥1 bullet citing IMO|ITTC|IACS|SNAME with stable URL or source-page link."

This is fine for "concept" pages that NAME a standard once, but the proposed scope of (e.g.) `intact-stability-criteria.md` is "IMO 2008 IS Code criteria, weather criterion, GZ-curve thresholds" (line 219), and `ship-structural-strength.md` is "longitudinal strength, hull-girder bending, IACS UR S section-modulus rules" (line 225). Reproducing IMO IS Code thresholds or IACS UR S section-modulus formulas inside a `wiki/concepts/` page is in tension with #2471's path-routing principle: codified-standards content belongs at `wiki/standards/<code-id>.md`. The plan acknowledges this on line 32 ("No standards page promotion is in this plan's scope") but the page-scope language on lines 219 and 225 explicitly proposes to write criterion thresholds and rule formulas into concept pages — the very content that #2471 says belongs under `wiki/standards/`.

**Required fix:** clarify the line between "naming the standard" (allowed in concept pages) and "enumerating the standard's specific thresholds/formulas" (must go to a standards page). If the plan writes IMO IS Code thresholds into `intact-stability-criteria.md`, the calc-citation contract (`.claude/rules/calc-citation-contract.md` step 2) requires that those thresholds be cited from a wiki standards page that does not yet exist. Either constrain the concept-page scope (allowed), or add the corresponding standards-page promotion to this batch (which the plan already says is out of scope).

---

## MINOR findings

### m1 — Plan's claim of 36 source pages contradicts the live count of 43

Plan line 25: "Found: 36 source-summary pages under `sources/`". Live count: `find … sources -name "*.md" | wc -l` → 43. The plan also acknowledges 43 elsewhere (line 44 "61 pages, 43 sources"). This is internal inconsistency, likely a copy-paste residue from an earlier draft. Not load-bearing for the 10-page selection but indicates resource-intel was not regenerated against current state.

### m2 — Plan claims `index.md` has 61 pages and bumps to 71, but live `find … wiki -name "*.md" | wc -l` is 62

`index.md` frontmatter (line 5) reads `page_count: 61` while the actual file count under `wiki/` is 62 (per `find` and the issue body itself). The plan inherits the off-by-one and proposes to bump 61 → 71 (line 228). Real terminal state should be 62 + 10 = 72. Either index regeneration is stale, or `page_count` excludes one specific file (overview? log?). Acceptance criterion line 260 says `page_count >= 71` which is loose enough to pass either way, but the plan should call out and resolve the 61-vs-62 discrepancy before implementation.

### m3 — Cited IMO URL `https://www.imo.org/en/OurWork/Safety/Pages/Intact-Stability.aspx` did not return content during verification

WebFetch returned HTTP 500 on the cited Intact-Stability page (twice). Could be transient. Plan should verify the URL is canonical or fall back to the IMO publication-search URL. If the page is permanently dead, every new page's "Standards / References" bullet that points to it will fail link-resolution checks.

### m4 — The "≥2 see_also cross-links" test enforces structure not relevance

Test `test_frontmatter_see_also_min_two` (line 241) checks count, not target validity. A page can satisfy it by listing two arbitrary `see_also` entries (e.g., the same page twice or a placeholder). `test_index_links_resolve` (line 245) covers index links but not in-page `see_also` resolution. Adding a `test_see_also_paths_resolve` would convert the structural shell into an actual relevance check.

### m5 — Word-count cap of 400 is justified by "concept summary, not chapter copy" but flagged as Open Question

Line 297 surfaces the cap as an Open Question for the reviewer. Existing baseline pages average "~150–250 words"; the new pages are positioned to expand the catalogue, so 400 is a soft upper bound. The plan should either pick a default and remove the Open Question, or define a fallback that does not block implementation if the reviewer is silent.

### m6 — The "classification societies aggregated vs per-society" Open Question (line 295) does default to aggregated, but the rationale ("scope budget of 10 pages") is circular

The plan picks aggregated because the batch is 10 pages, and the batch is 10 pages because the plan picks aggregated. If the right answer is per-society (12 IACS members → 12 pages), the 10-page bound is wrong. The plan should either (a) commit to aggregated as a permanent design call independent of batch size, OR (b) acknowledge that batch size and aggregation choice are coupled and re-derive both together.

### m7 — `index.md` regeneration risk is acknowledged but mitigation is incomplete

Risk on line 293 says `index.md` "is regenerated periodically by `llm-wiki` tooling; manual edits may be overwritten" and proposes also editing `knowledge/seeds/naval-architecture-resources.yaml` "if that is the source of truth — to be confirmed during plan review". The conditional ("if … to be confirmed") is exactly the kind of unresolved gate that can land partial work in production. Resolve before approval: which file is the source of truth, and is the plan editing it?

### m8 — Plan's ITTC procedure-number citation is unverified

Plan line 65 cites "ITTC Recommended Procedures: 7.5-02-* … 7.5-02-07-021". WebFetch on `https://ittc.info/` confirmed the site is real and lists a procedure index, but the specific number prefixes (`7.5-02-*`, `7.5-03-*`) and the specific code `7.5-02-07-021` were NOT directly verified — landing page links to a downloads index that was not fetched. If those exact numeric codes are wrong, every new page citing them inherits the error.

---

## Notes (non-finding observations)

- **Source citation count is honest.** Plan claims "9 distinct sources cited" (line 147). Counting: issue body, wiki index, CLAUDE.md, #2566, #2568, #2540, /mnt/ace inventory, WebSearch Tupper, WebSearch PNA+ITTC. That is 9, exceeds the ≥3 minimum.
- **Past-tense drift is genuinely absent.** Acceptance Criteria use "will" throughout (lines 254–265). Adversarial Review Summary (line 270) is empty placeholder ("To be filled in after Step 4"), which is correct draft state.
- **Test list has both shell and substance.** `test_word_count_under_400`, `test_no_pdf_extraction_markers`, `test_no_reservation_overlap` are real heuristics. `test_frontmatter_required_fields`, `test_all_ten_pages_exist`, `test_log_entry_appended` are structural shell, but they ARE tests, not commented placeholders.
- **The `entities/` directory is genuinely empty.** Confirmed by `ls`. Adding the first entity page (`classification-societies.md`) is a real net-new contribution to the wiki, not a duplicate.
- **Cross-review is single-author.** Per `feedback_permission_gate_blocks_cross_review.md`, this review is one of three planned (Claude internal, Codex, Gemini). Treat verdict as one provider's vote, not consensus.

---

## Verdict

**MAJOR** — 4 MAJOR findings, 8 MINOR.

The plan's structural integrity is sound (template followed, future-tense, citations honest, test list real), but the substantive content selection has a defensible-but-uncorrected redundancy problem: 5 of the 10 proposed pages (resistance-components, propeller-theory, marine-propulsors, intact-stability-criteria, damage-stability) restate content already on existing pages, and the plan does not commit to retiring or shrinking the source pages. The reserved-phrase regex test is mis-targeted (M3) and the standards-vs-concept boundary is fuzzy in two specific cases (M4). All four MAJORs are addressable with plan edits — they do not require dropping the issue. None invalidates the strategic case for naval-arch wiki expansion.

**Required before APPROVE:** addresses for M1–M4. MINORs may be deferred to follow-up issues but at least m1, m2, m7, m8 should be resolved in the plan before implementation starts.

---

## Checklist

- [x] Plan read in full (303 lines).
- [x] #2566 and #2568 reserved scope verified against live issue bodies.
- [x] Each of 10 proposed pages assessed for reservation collision: 0 brush against #2566 noun-phrases; 0 brush against #2568 reserved noun-phrases in NEW pages, but reserved phrases ALREADY appear in existing `maneuvering-validation-metrics.md` (M3).
- [x] Naval-arch wiki inventory verified: 13 concept pages (matches), 43 source pages (plan says 36, m1), 1 standards page (matches), 0 entity pages (matches), 62 total markdown files under `wiki/`.
- [x] Sample existing pages read for false-gap detection: hydrostatics.md, seakeeping.md, stability.md, resistance-propulsion.md, maneuvering-validation-metrics.md → M1, M2, M3 surfaced.
- [x] Cited URLs partially verified (sname.org confirmed, ittc.info confirmed but procedure numbers not, IMO URL HTTP 500 — m3, m8).
- [x] Terminology drift checked: plan uses "intact stability" (matches existing `stability.md` line 19), "seakeeping" (matches existing page name), "lines plan" (introduced; existing wiki has no "lines drawing"); plan's own Risks section calls out manoeuvring/maneuvering and scantlings/structural-design — addressed but not fixed.
- [x] Standards-body promotion risk checked against #2471 — M4.
- [x] 10-page count assessed: not scope creep on its own, but coupled to aggregation choice (m6); decomposition risk per page is bounded.
- [x] TDD contract assessed: real heuristics + structural shell, missing redundancy/cross-page-overlap test (M1) and see-also-resolves test (m4).
- [x] Past-tense drift hunt: clean.
- [x] Open Questions assessed for hidden punts: aggregation defaulted (m6), 11th-page deferred (clean), word-cap unresolved (m5).
- [x] Review file written to `scripts/review/results/2026-05-02-plan-2589-claude-internal.md`.
