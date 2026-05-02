# Adversarial Review — Plan #2592 (W2-C maritime-law expansion)

- **Plan:** `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` (384 lines)
- **Issue:** [#2592](https://github.com/vamseeachanta/workspace-hub/issues/2592) — feat(llm-wiki): maritime-law wiki topical expansion
- **Reviewer:** Claude (single-author, internal)
- **Provenance:**
  - Codex UNAVAILABLE — codex-cli 0.124.0 upstream stdin-hang regression per memory `feedback_codex_cli_0_124_upstream_regression.md` (#2479) + sandbox blocks shell-exec/writes per `feedback_codex_sandbox_no_execution.md`.
  - Gemini UNAVAILABLE — sparse-checkout overlay blindness produces false-positive `file-missing` claims per `feedback_gemini_sandbox_overlay_blindness.md`.
  - Single-author rationale: per memory `feedback_permission_gate_blocks_cross_review.md`, planning-only sessions cannot dispatch `cross-review.sh`; transparent fallback is single-author with provenance disclosed.
- **Stance:** adversarial — defects until proven otherwise; cite file/section/quote.
- **Verdict:** **MAJOR**
- **Counts:** MAJOR=2, MINOR=5

---

## MAJOR findings

### MAJOR-1 — Plan extends `wiki/standards/` routing to a wiki the routing memory **explicitly excludes**

**Severity:** MAJOR. Load-bearing path-routing decision; the plan acknowledges it as Open Question #1 but the extension is contradicted by the cited memory itself, not merely unsanctioned.

**Plan claim** (line 63):

> Memory `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` is the sanctioned routing for codified standards. Note: that memory states **#2471 is CSA-Z276-only** — the routing principle generalizes, the codification plan does not. This plan extends the principle to IMO conventions (a forward extension; flagged as Open Question for sanction).

**Memory text (verbatim, `project_wiki_standards_path_decision.md`):**

> The principle applies to: marine-engineering, engineering, naval-architecture. **Maritime-law, personal, health-reports are out of scope.**

The plan reads the memory as "scope of the codification plan" but the quoted memory clause is "scope of the routing principle itself." The plan's framing — "the routing principle generalizes" — is **not what the memory says**. The memory affirmatively names maritime-law as out of scope of the principle. This is not a forward-adoption gap; it is a contradiction.

Compounding evidence:

1. **`knowledge/wikis/maritime-law/CLAUDE.md` does NOT declare a `wiki/standards/` directory.** Verified via Read 2026-05-02. The schema lists no standards-page extra-fields contract; it only inherits from marine-engineering by reference. Naval-architecture's `CLAUDE.md` (verified 2026-05-02) explicitly declares `wiki/standards/` plus the `code_id`/`publisher`/`revision` extra-fields table. Maritime-law is missing both.
2. **The plan's "Files to Change" table at line 304 modifies `index.md` but does NOT modify `knowledge/wikis/maritime-law/CLAUDE.md`.** Creating `wiki/standards/` without first updating CLAUDE.md to declare the schema (a) leaves the wiki schema-inconsistent with what's on disk, and (b) violates the maturity gradient in `.claude/rules/patterns.md` — schema decisions should be Level-1 prose at minimum before Level-3 commits land.
3. **Memory `project_wiki_standards_path_decision.md` "Reconcile note" (verified 2026-05-02):**

   > before recommending the `wiki/standards/` subtree as canonical for any new standard, verify (a) #2471 has actually landed for CSA, (b) aces-#4 Phase 1 hasn't superseded the path with a different decision...

   The plan does not perform check (b) — there is no evidence that aces-#4 Phase 1 has been audited for whether maritime-law should follow CSA's pattern or a different higher-level subtree (the memory explicitly raises that aces-#4 may promote standards to a different home).

**Why this is MAJOR not MINOR-Open-Question:** the plan asks the user to sanction a routing extension that the cited memory rejects in plain text, while presenting the situation as if the memory only restricts the codification plan. A reviewer relying on the plan's reading would approve under a misimpression. The Open Question framing is not sufficient because the question itself is mis-stated.

**Required fix (for plan author):**
- Re-read memory `project_wiki_standards_path_decision.md` and quote the "Maritime-law... out of scope" clause in Open Question #1 verbatim.
- Add a third option: route the 4 IMO/ILO pages to `concepts/` with `code_id`/`publisher`/`revision` frontmatter (a schema-additive change, not a path extension), pending an explicit maritime-law sanction issue.
- Add a precondition step: update `knowledge/wikis/maritime-law/CLAUDE.md` to declare `wiki/standards/` with extra-fields schema BEFORE creating any standards page (or fold this into the `concepts/` fallback).
- Add a check against aces-#4 Phase 1 (cradle-to-grave standards canonical home) so that the maritime-law decision does not pre-empt that audit.

---

### MAJOR-2 — Standards-page `revision` field cannot satisfy the `#2471 frontmatter` contract for IMO conventions; the contract `revision: "Consolidated Edition 2022 (incl. 2020 sulphur cap MARPOL Annex VI)"` proposed in line 179 is not a `revision` in the calc-citation sense

**Severity:** MAJOR. The plan claims (line 60) the 4 standards pages will satisfy the calc-citation contract so future calc modules can resolve them. The proposed `revision` strings cannot fulfill that contract.

**Plan claim** (line 60):
> the 4 new standards pages WILL carry `code_id`/`publisher`/`revision` frontmatter so future calc-module citations (e.g., a marine-insurance calc) can resolve them via the resolver in #2481/#2482.

**Plan exemplar** (lines 175–189, MARPOL standards-page frontmatter):
```yaml
code_id: MARPOL-73-78
publisher: IMO
revision: "Consolidated Edition 2022 (incl. 2020 sulphur cap MARPOL Annex VI)"
```

**Why this fails:**

1. The calc-citation contract per `.claude/rules/calc-citation-contract.md` (Read 2026-05-02) requires `revision` be a value the resolver can match against the calc's `Citation` instance — i.e., the calc emits `Citation(code_id="MARPOL-73-78", revision="...")` and `revision` mismatch raises `CitationResolutionError`. IMO conventions are amended by *amendments adopted at MSC/MEPC sessions*, not by edition-publisher revisions. There is no canonical "Consolidated Edition 2022" — IMO publishes a **Consolidated Edition** approximately every few years bundling adopted amendments to date. A calc emitting `revision="2024 amendments"` cannot match `revision="Consolidated Edition 2022"`.

2. The plan acknowledges this exact problem in the Risk register at line 369 ("convention-lifecycle drift... a page does not silently go stale when the next amendment lands. Tests will not lock numerical values; they will lock structural shape"), but the *frontmatter contract is itself a numerical value lock* — `revision` is exactly the field whose mismatch fails the resolver closed (per #2481 D2). The risk register sidesteps the contradiction by saying "we won't lock thresholds in body text" while the frontmatter does the locking.

3. **MLC 2006 has a different problem:** MLC was adopted by ILO (not IMO), enters force per ratification, and has been amended via the Special Tripartite Committee (STC) most recently in 2022 (in force 2024). MLC has no "Consolidated Edition" publication line analogous to MARPOL. A `revision` field for MLC would have to be something like `"as amended through STC 2022 amendments"` — which again cannot match a calc citation's amendment-set.

4. **ISM Code is an *embedded code in SOLAS Ch IX*, not a standalone publication.** Its `publisher` is IMO, but its `revision` is governed by SOLAS amendments. Treating it as a standalone standards page with its own `revision` decouples it from the SOLAS amendment chain it actually rides on.

**WebFetch verification (2026-05-02):** the IMO `listofconventions.aspx` page lists SOLAS, MARPOL, STCW, COLREG as the headline conventions but **does NOT list MLC** (because MLC is ILO, not IMO) and **does NOT list ISM/ISPS** at the top level (they live under SOLAS chapters). The plan's framing in the gap matrix at line 41 ("ISM Code (incorporated SOLAS Ch IX)") acknowledges this but the standards-page schema (line 261, `tags: [maritime-law, standards, <publisher-tag>, <topic-tag>]`) treats them as standalone publishables anyway.

**Why this is MAJOR:** the plan asserts a calc-citation-resolution capability (line 60: "future calc-module citations... can resolve them") that the `revision` field as specified cannot deliver. If a calc author trusts the plan and emits a `Citation` against `MARPOL-73-78`, the resolver will fail-closed on the first amendment-edition delta. This is the exact failure mode #2481 was designed to prevent.

**Required fix:**
- Either (a) define a maritime-law-specific `revision` semantics (e.g., `revision: "consolidated through MEPC amendments adopted by 2026-05-02"`) AND document in `knowledge/wikis/maritime-law/CLAUDE.md` how a calc citation matches that — OR (b) document explicitly that the 4 standards pages carry forward-adoptable identity but are NOT calc-resolvable in v1, with an issue tracking the matching-semantics decision.
- Address ISM Code as embedded-in-SOLAS (perhaps a sub-page or pointer page, not a standalone standards page).
- Address MLC's ILO publisher chain separately (ILO has its own amendment cadence).

---

## MINOR findings

### MINOR-1 — Past-tense / artifact-as-existing drift: line 7 references review artifacts that have not been written

Plan line 7:
> **Review artifacts:** scripts/review/results/2026-05-02-plan-W2C-maritime-law-claude.md | ...-codex.md | ...-gemini.md

These three paths do not exist on disk (`ls scripts/review/results/ | grep 2592` returned only this review). The plan should either mark them as planned outputs or omit pending-creation paths from the header. Per memory `feedback_plan_past_tense_artifact_claims.md`. The Codex/Gemini paths in particular will not be written (per the provenance disclosed in MAJOR-1 plan-side and in this review's header) and should be deleted.

### MINOR-2 — Top-10 selection narrative leaks drafting state into the final plan

Plan lines 113–117:
```
Concepts (regulatory + commercial-shipping doctrine, 2 more pages — selecting bills-of-lading and charterparties as the most cross-linkable... — deferring `imo-regulatory-framework.md`, `collisions-and-colregs.md`, `charterparties.md` selection rationale below):

Wait — to stay strictly at 10 with the 4 standards pages in, I need exactly 6 concept pages. Adjusting selection:

Final top-10:
```

The "Wait — to stay strictly at 10..." sentence is mid-draft self-correction text. A finalized plan should not contain this; it should present the final 10 cleanly with rationale. Same paragraph also presents charterparties as both deferred (line 114) and selected (line 126). Reads as drafting noise.

### MINOR-3 — `code_id` regex test is too permissive vs. canonical IMO/ILO short codes

Plan TDD line 319:
> `test_standards_code_id_canonical` | `code_id` matches `^[A-Z][A-Z0-9-]+$` and is one of the canonical IMO/ILO short codes

But the proposed `code_id` values (per line 258 example: `MARPOL-73-78`, `SOLAS-1974`, `MLC-2006`, `ISM-Code`) are inconsistent with the naval-architecture wiki's existing convention which uses lowercase hyphenated (per memory `project_wiki_standards_path_decision.md`: "When someone asks where a code/standard overview page should live in an llm-wiki, answer `wiki/standards/<code-id>.md` (lowercase, hyphen-separated)"). Verified against the naval-architecture standards file `steering-gear-rudder-stock-rule-crosswalk.md` whose frontmatter `code_id: steering-gear-rudder-stock-crosswalk` is lowercase. The plan should use lowercase: `marpol-73-78`, `solas-1974`, `mlc-2006`, `ism-code` for consistency, and the regex should be `^[a-z][a-z0-9-]+$`. The mixed-case `ISM-Code` (capital I, capital C) is internally inconsistent with even the plan's own regex `^[A-Z][A-Z0-9-]+$` (which requires *all* segments uppercase or hyphen-uppercase).

### MINOR-4 — `test_no_verbatim_convention_text` heuristic is weak and likely false-positive on legitimate prose

Plan TDD line 324:
> `test_no_verbatim_convention_text` | No new standards page contains a paragraph >80 words AND >5 commas (heuristic for copy-pasted regulatory prose)

Convention scope paragraphs that legitimately list multi-element scope (e.g., "MARPOL applies to ships flying the flag of a Party, ships not flying the flag... operating under its authority, all ships in waters under jurisdiction of a Party...") routinely exceed 80 words with >5 commas without being copy-paste. Conversely, a short verbatim quote (<80 words) escapes the heuristic. The risk-register name #2482 deny-list compliance is real (verified `cat .claude/rules/calc-citation-contract.md`: "Do NOT cite wiki pages under `knowledge/wikis/*/wiki/sources/` — those are vendor-derivative deny-list per the governance doc #2482"), so the test should match the actual deny-list contract, not a length heuristic. Better tests: hash-match against IMO-corpus-PDF text fragments, or a citation-form lint that requires every quoted phrase >10 words to carry an explicit citation-marker.

### MINOR-5 — Index `page_count: 30` claim is internally inconsistent with on-disk count (=32 after this plan)

Plan acknowledges this in Risk register (line 374):
> After this plan: on-disk = 32, catalogued count = 30 (10 new pages added). Same shape as #2589 finding m2.

But the Acceptance Criteria at line 344:
> `index.md` frontmatter `page_count` will read ≥30; `last_updated` will read `2026-05-02`.

`≥30` is satisfied by both 30 (catalogued) and 32 (on-disk). The plan tests at line 326 (`test_index_page_count_bumped`) check `page_count >= 30`. So the test does not actually distinguish the two values. Either fix to `page_count == 32` (true on-disk count post-plan) or commit to the catalogued-count semantics and document it. Risk-register acknowledging the drift is not the same as fixing it.

---

## Affirmative-verification checklist

| Verification step | Status | Evidence |
|---|---|---|
| Plan exists, 384 lines | YES | `wc -l` confirms 384 |
| 22 maritime-law wiki files | YES | `find ... | wc -l` returned 22 |
| `wiki/standards/` does not exist in maritime-law | YES | `find ... -type d -name standards` returned no maritime-law match |
| #2540 OPEN, #2589 OPEN, #2471 CLOSED, #2482 CLOSED | YES | `gh issue view` confirmed |
| #2471 is CSA-Z276 scoped (not general) | YES | `gh issue view 2471` body: "Decide and codify the sanctioned durable-wiki routing/schema for **CSA Z276** pages..." |
| Memory `project_wiki_standards_path_decision.md` excludes maritime-law | YES (KEY) | Memory body: "Maritime-law, personal, health-reports are **out of scope**" |
| `/mnt/ace/acma-codes/IMO/` exists | YES | `ls` confirmed (IMO PDF corpus including SOLAS, MARPOL, ISM materials) |
| `/mnt/ace/acma-codes/ABS Rules/ILO Maritime Labour Convention/` exists | YES | Single PDF: `2006 Guidance Notes on the ILO Maritime Labour Convention.pdf` (note: only one file, not "corpus") |
| IMO `listofconventions.aspx` URL valid | YES | WebFetch returned canonical content; SOLAS, MARPOL, STCW, COLREG listed; **MLC, ISM, ISPS not headline** |
| Existing concept pages do not cover proposed concepts | YES | grep for "general average / york-antwerp / charterparty / salvage / port state / flag state" returned 0 hits across all existing concept pages (only "limitation" matched in `llmc-1996.md` as expected) |
| Naval-architecture wiki has `wiki/standards/` and CLAUDE.md schema | YES | Read confirmed |
| Maritime-law CLAUDE.md does NOT have `wiki/standards/` schema | YES | Read confirmed — only references marine-engineering for conventions |

---

## Verdict & required actions

**Verdict: MAJOR (2)**

**Required before APPROVE:**
1. Address MAJOR-1: re-frame Open Question #1 against the verbatim memory exclusion; require maritime-law CLAUDE.md schema update as a precondition; check aces-#4 Phase 1 audit.
2. Address MAJOR-2: define `revision` semantics for IMO/ILO conventions OR explicitly scope the 4 pages as not-yet-calc-resolvable; address ISM-as-embedded-in-SOLAS and MLC-as-ILO publisher specifically.
3. Sweep MINOR-1 through MINOR-5.

**Not blocking:** the curriculum selection (Mandaraka-Sheppard + Schoenbaum + IMO-active-conventions list) is defensible; the false-gap audit confirms the 6 concept topics are genuinely absent; jurisdictional-bias acknowledgment in the Risk register is appropriate.
