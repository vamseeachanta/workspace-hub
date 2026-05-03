# Adversarial Review — Plan #2612 (W5-C lng-projects topical expansion)

**Reviewer:** Claude (internal, Opus 4.7 1M)
**Date:** 2026-05-03
**Plan:** `docs/plans/2026-05-03-issue-2612-llm-wiki-W5C-lng-projects-expansion.md`
**Stance:** Adversarial — assume defects exist; cite file:line for each finding.

---

## Verdict

**MAJOR** — 2 P1 findings (entity-routing miscategorization that contradicts CLAUDE.md convention; reservation regex coverage gap with concrete near-term collision risk). Plan is recoverable with focused edits; no rebuild needed.

---

## Verification Run

### 1. Allowlist test
```
$ uv run pytest tests/governance/test_2471_citation_scope.py 2>&1 | tail -3
============================== 6 passed in 0.43s ===============================
```
PASS — governance allowlist is clean. No #2471 scope violation introduced.

### 2. lng-projects current inventory
Confirmed 7 markdown files (plan claims "6 markdown files plus the domain CLAUDE.md" on line 15 — count is 6 if you exclude `CLAUDE.md`, 7 if you include it; matches the plan's `find` output verbatim on lines 18–25). Inventory verified.

### 3. Routing-principle exclusion (memory `project_wiki_standards_path_decision.md`)
Memory confirms the `wiki/standards/<code-id>.md` principle is sanctioned for {marine-engineering, engineering, naval-architecture}. lng-projects is NOT in that list. Plan's "no `wiki/standards/` content" guard (line 152, line 254 test, line 272 acceptance) is correctly load-bearing.

However, the plan's lng-projects `CLAUDE.md` (verified independently) **already declares `wiki/standards/`** in its Directory Structure (line 22 of the schema) and even reserves `code_id`/`publisher`/`revision` fields for that subtree. The auto-generated `llm-wiki init` template baked the standards routing into every wiki regardless of memory-level sanction. This is not a defect of THIS plan — but the plan's "do not create `wiki/standards/`" guard is fighting a template-level pre-commitment, and the test `test_no_standards_directory_created` may still pass while the schema doc on disk advertises a path the plan refuses to populate. Worth a Minor flag.

### 4. SESA / Woodfibre overlap with #2541 / #2544
- #2541 OPEN, status:plan-review, **SOURCE-PAGE scope** confirmed — reserves SESA-specific extraction. Plan's regex `\bSESA\b` blocks collision. PASS.
- #2544 CLOSED, status:plan-approved, **scout/corpus-pointer scope** confirmed — produced the existing `woodfibre-corpus-pointer.md`. Plan's regex `\bWoodfibre\b` blocks collision. PASS.

### 5. Standards URLs
- NFPA 59A — verified canonical: nfpa.org product page, scope = "Production, Storage, and Handling of Liquefied Natural Gas (LNG)", current edition 2023. URL family in plan is correct.
- EN 1473 — verified canonical: CEN/TC 282, current edition 2021, scope = "Design of onshore installations" with >200 t LNG storage. URL family correct.
- Plan-cited URL `https://www.cencenelec.eu/` is the umbrella, not a deep link to EN 1473. Acceptable for NAME-only discipline (plan explicitly forbids enumerating clauses).

### 6. lng-projects directories on disk
**FACTUAL DRIFT:** Plan claims (lines 29–31) that `wiki/concepts/`, `wiki/entities/`, `wiki/standards/` "do not yet exist on disk." Live `ls` shows `wiki/concepts/` and `wiki/entities/` BOTH ALREADY EXIST as empty directories (created 2026-04-28 14:23 by `llm-wiki init`). Only `wiki/standards/` is genuinely missing. The plan's gap-proof excerpt on line 147 (`ls knowledge/wikis/lng-projects/wiki/concepts 2>&1` returning "No such file or directory") is wrong as of 2026-05-03 — the directories were created by the init scaffold but stayed empty.

This is a **Minor** factual error, not a defect — the practical effect (no concept/entity content exists) is identical, and `mkdir -p` is idempotent. But the plan should not assert facts that `ls` contradicts; reviewers will catch this and trust degrades.

---

## Findings

### P1 (MAJOR)

**M1 — `lng-regulatory-framework.md` is mis-routed under `entities/`.**

Lines 89, 103, 169, 229, 266 all place `lng-regulatory-framework.md` under `wiki/entities/`. Per the lng-projects `CLAUDE.md` schema (line 17, verified live): `entities/ # Entity pages (specific things: CALM Buoy, FPSO, etc.)`. The marine-engineering convention example is even stronger: entities = `anode`, `flange`, `gasket`, `lng-carrier-mooring` — i.e., **single tangible artifact pages**.

A "regulatory framework" is an umbrella collection of multiple standards bodies (NFPA + EN + IGC + SIGTTO + OCIMF + IACS). It is the antithesis of a "specific thing." Per convention, this is either:

1. A **concept page** (`concepts/lng-regulatory-framework.md`) — the abstract idea of how multiple standards bodies bind LNG projects.
2. A **set of entity pages**, one per standards body (e.g., `entities/nfpa.md`, `entities/cen.md`, `entities/sigtto.md`) — each NAMING the body, with publisher and scope per `CLAUDE.md` line 39 example pattern.
3. A **set of standards pages** under `wiki/standards/` — but this is blocked by the path-sanction guard, so it cannot land in this plan.

The plan even admits the entity is "first entity page" (line 229) — the plan author noticed this is structurally odd ("one-paragraph publisher-and-scope per body") but routed it as one combined page anyway, which is a category mistake. The reviewers who catch this will reject the entity page on convention grounds; the test `test_at_least_one_standards_body_named` does not catch the routing error because it inspects content, not directory.

**Fix:** Either re-route to `concepts/lng-regulatory-framework.md` (preserves single-page synthesis intent) or split into one entity page per standards body. Recommend option 1 because the plan's stated purpose is a single landing-page synthesis, and the entity-as-tangible-thing convention is load-bearing for lint discipline.

**M2 — Reservation regex incomplete; near-term collision risk concrete.**

Plan line 247 reserves `\b(SESA|Woodfibre|ACMA[- ]?project[- ]?31522|Doris[- ]?project[- ]?62092)\b`. Resource-intel mentions this scope on line 71. But `/mnt/ace/doris/62092_sesa/` and `/mnt/ace/acma-projects/31522-woodfibre-lng/` are inventory paths from the Elements ingest sweep, and the lng-projects wiki is a project-corpus hub. Other LNG project corpora that may land between this plan's approval and merge:

- **KSE / Driftwood / Rio Grande / Magnolia / Plaquemines** — major US Gulf LNG projects with known docket activity; any of these landing as a future scout-issue (sibling to #2541/#2544) would NOT be blocked by the current regex. The plan does not name them but the noun-phrase `Driftwood LNG` or `Rio Grande LNG` could appear in the canonical-projects section of `concepts/lng-project-shapes.md` and trigger no test failure even if a future #26XX scout reserves that name.
- **Woodside / Pluto / Karratha / Wheatstone / Gorgon / Prelude** — Australian LNG names already in use elsewhere in workspace-hub (e.g., `marine-engineering/wiki/entities/lng-carrier-mooring.md` line 19 names "Karratha Gas Plant"; the engineering wiki has a `prelude-flng-mooring.md` entity page).
- **Project-code patterns:** `ACMA[- ]?project[- ]?\d+` and `Doris[- ]?project[- ]?\d+` would have caught both #2541 and #2544 with one-pattern-per-corpus instead of separately enumerating 31522 and 62092. The current regex only matches the two specific codes.

**Fix:** Generalize the regex to `\b(SESA|Woodfibre|ACMA[- ]?project[- ]?\d{4,6}|Doris[- ]?project[- ]?\d{4,6})\b` AND add a positive-list assertion that says "if any future LNG-project noun-phrase is named in a concept page, it must be naming an industry-canonical project (KGP, Pluto, Sabine Pass, Cheniere) and never a workspace-hub-internal corpus identifier." Without the project-code wildcard, the next scout-issue ships with a different ACMA number and the regex silently lets it through.

This is P1 because the failure mode is silent: a concept page mentioning "ACMA project 32100" lands, then a downstream #2645 scout-issue claims that path, and the test never warns. The 2026-04-28 wave already established that ACMA-project-NNNNN is the active naming convention; future ones are nearly certain.

### P2 (MINOR)

**m3 — Index-update count math is off by one.**

Line 207 says "create 'Concepts' table with 7 new rows" and line 230 says "Add 7 concept rows + 1 entity row; bump `page_count` 3 → 9." But the plan creates 7 concept files + 1 entity file = 8 new pages. Existing `index.md` shows `page_count: 3` reflecting the 3 sources (no overview/log/index counted, since index.md auto-generates and overview.md/log.md are scaffolding). Adding 8 wiki pages should bump to **page_count: 11** if the convention counts everything, or **page_count: 8 (7 concepts + 1 entity)** if the convention counts only concept+entity slots — neither math gives 9. The acceptance criterion line 267 reads "≥9" which is permissive enough to pass either interpretation, so the test won't fail, but the in-text math (3 → 9) is wrong.

**Fix:** Recompute using one explicit convention. If the existing index frontmatter (`page_count: 3`) is truly counting the 3 source-pages and not the 3 scaffolding pages (index/log/overview), then 3 + 8 = 11 is the correct target. Inspect the regenerator's counting rule before stating the bump.

**m4 — `wiki/standards/` directory pre-declared in `CLAUDE.md` schema.**

Live `lng-projects/CLAUDE.md` line 22 declares `wiki/standards/` in the directory structure, and lines 39–47 spell out the standards-page frontmatter contract — including `code_id`, `publisher`, `revision`. The plan asserts (line 152) that no `wiki/standards/` content will be added because lng-projects is outside the routing-principle scope. This guard is correct per memory, but the schema document on disk was auto-generated by `llm-wiki init` and pre-commits the path. The plan does not propose to amend `lng-projects/CLAUDE.md` to remove the standards-directory mention. The result is a schema/scope mismatch on disk: the wiki documents a standards subtree it is forbidden to populate.

**Fix:** Either (a) add a one-line note to `lng-projects/CLAUDE.md` clarifying that `wiki/standards/` is template-reserved-but-currently-disabled-for-this-domain pending separate sanction, or (b) accept the mismatch and document it in the Open Questions section of the plan as a known-debt item.

**m5 — Plan claims `concepts/` and `entities/` directories don't exist.**

Already covered in Verification §6. Lines 29–31 are factually wrong as of 2026-05-03; both directories exist (empty). Fix the resource-intel inventory to read "wiki/concepts/ and wiki/entities/ exist as empty directories (scaffolded by `llm-wiki init` 2026-04-28); no content yet."

**m6 — Source count claim discrepancy.**

Resource-intel comment block on line 158 says "Source count: 11 distinct sources cited above" and enumerates 11 items. But the actual line 74 lists `WebSearch — LNG project lifecycle phases` and line 75 lists `WebSearch — FLNG vs onshore LNG`. Items (5)–(8) in the comment are GitHub issues, not "sources" in the retrieval-contract sense — they're cross-references, but the contract usually means standards/papers/articles/docs. Counting issues as sources inflates the claim. Substantive sources: 4 (CLAUDE.md schemas + 1 source-page) + 2 WebSearches + /mnt/ace inventory = ~7, not 11. The minimum-3 contract is met regardless.

**Fix:** Cosmetic — recount and footnote what counts as a "distinct source" vs "cross-reference."

**m7 — Past-tense drift sweep.**

Plan uses future tense throughout; no claims that pages already exist or tests already pass. Memory feedback `feedback_plan_past_tense_artifact_claims.md` is respected. PASS, no fix needed.

**m8 — `lng-marine-transfer-systems.md` includes "tandem mooring" — potential overlap with the OCIMF tandem mooring page just authored.**

Line 226 explicitly mentions the recently authored `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` (visible in repo `git status` `?? knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`). Plan says it cross-links to OCIMF MEG4 by NAME, not the standards page. This boundary is correct in the plan text, but reviewers should verify the live OCIMF tandem page does not get duplicated in `concepts/lng-marine-transfer-systems.md`. Test `test_no_thresholds_or_clauses_enumerated` (line 255) is the only safeguard; it's regex-based and could miss a tandem-mooring narrative reproduction.

**Fix:** Add a positive test that `concepts/lng-marine-transfer-systems.md` body word-count does not exceed N words on the tandem-mooring topic specifically (e.g., `assert len(re.findall(r'tandem mooring', body, re.I)) <= 3`), or simply assert that the page does not contain copy of the engineering tandem-mooring page paragraphs (hash-or-substring check).

### P3 (NIT)

**n1 — Adversarial Review Summary table is empty placeholder (lines 281–287).**
Expected during draft. No fix needed before review approval.

**n2 — Citation contract not invoked.**
Plan correctly notes (line 65) that concept pages don't emit `Citation` instances. This is consistent with `.claude/rules/calc-citation-contract.md` which scopes citation emission to calc modules. PASS.

**n3 — `index.md` hand-edit risk.**
Risks section line 297 acknowledges that without a seed file, `index.md` is hand-edited and a future regenerator could overwrite. The mitigation ("log entry references this plan path so a regenerator can be backfilled") is weak — the regenerator does not consult log.md to reconstruct lost entries. Real mitigation is to file a follow-up issue to add `knowledge/seeds/lng-projects-resources.yaml` after this batch lands. Recommend adding that follow-up as an explicit deliverable line.

---

## Summary

| Severity | Count | Items |
|---|---|---|
| MAJOR (P1) | 2 | M1 entity routing; M2 reservation regex coverage |
| MINOR (P2) | 6 | m3 page-count math; m4 standards-dir schema mismatch; m5 directory-existence claim; m6 source-count inflation; m7 past-tense (PASS); m8 tandem-mooring overlap guard |
| NIT (P3) | 3 | n1 review table; n2 citation contract; n3 seed-file follow-up |

**MAJOR_COUNT: 2**
**MINOR_COUNT: 6** (m7 noted as PASS, not a defect — count of items flagged in MINOR section is 6, of which 5 require action)

The two P1 findings are addressable with targeted edits (re-route one file; broaden one regex). Do not approve until M1 and M2 are addressed.
