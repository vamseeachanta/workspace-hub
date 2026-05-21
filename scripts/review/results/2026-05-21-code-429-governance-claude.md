# Code-stage adversarial review — worldenergydata#429 (governance + cross-wiki linking)

**Reviewer:** Claude (code-stage, governance scope)
**Date:** 2026-05-21
**Commit:** workspace-hub `b0b598e0c`; worldenergydata-wiki `8763eb4`
**Scope:** routing-rule §6 amendment, governance-doc completeness, cross-wiki linking discipline, frontmatter convention, public-domain TOU claims, stale-doc supersession, migration-manifest coverage.

---

## VERDICT: MAJOR

The implementation lands a clean public sibling repo with internally-consistent frontmatter and well-drafted cross-link discipline. But two material defects block: (1) the migration manifest's "no existing wiki pages move from any repo into this one" claim is factually wrong — there is a substantive BSEE source page already in `llm-wiki:wikis/asset-management/wiki/sources/` that the manifest does not even mention; (2) the supersession of "row 5 → public llm-wiki" is incomplete — the llm-wiki repo has its OWN parallel governance doc (`llm-wiki/docs/governance/service-provider-data-routing.md`) still asserting the stale routing, and three llm-wiki pages still cite it. Both undermine the durable-decision posture this commit claims.

---

## FINDINGS

### [MAJOR] Migration manifest factually understates pre-existing BSEE coverage

**File:** `/mnt/local-analysis/worldenergydata-wiki/MIGRATION_MANIFEST.md:16-18`

The manifest asserts:

> No existing wiki pages move from any repo into this one. The reason: there are no existing derived BSEE/NOAA/USGS/MMS wiki pages anywhere in the ecosystem prior to 2026-05-20. The earlier proposal... was never actioned beyond the precedent landing of `wikis/drilling-engineering/wiki/sources/papkov-bsee-citation.md` — and that single page was URL-only metadata (Papkov-style), not derivative analysis.

This is wrong on two counts:

1. **`llm-wiki:wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md` exists** (landed 2026-05-14 per `llm-wiki/wikis/asset-management/wiki/log.md:18-26`). It is a substantive 100+ line derivative analysis of a BSEE Pipeline-Section conference presentation, including paraphrased IMP content, 8-step life-extension procedure summary, and integration with API RP 1160 / 2RIM cross-references. This is exactly the class of content the new routing rule targets (BSEE-derived, public-domain under 17 USC §105), and it explicitly routed under "row 5" of the now-superseded matrix. It is NOT the Papkov page; the Papkov page mentioned in the manifest (`papkov-bsee-citation.md`) does not even appear at the path cited — what exists is `papkov-2026-drilling-tender-ai-agent.md` (drilling-tender topic, not a BSEE-citation page).

2. **The "Papkov-style URL-only metadata" reasoning is therefore arguing against a strawman.** The actual pre-existing BSEE page is substantive derived analysis. The manifest's "What STAYS at its current location" table (lines 22-29) lists the Papkov page as "Pre-flip metadata-only page; URL-only; cross-domain content" but never mentions the asset-management BSEE-2024 page, which is the real precedent and is exactly the kind of artifact that should either (a) move to `worldenergydata-wiki/wiki/bsee/sources/`, or (b) be explicitly justified for staying in llm-wiki.

**Impact:** the manifest's central claim ("no migrations") is unfounded. Future agents will trust this claim, miss the asset-management BSEE page, and either (a) duplicate it in worldenergydata-wiki creating drift between sibling copies, or (b) fail to update its now-stale "row 5" governance pointer. The decision-revisitation triggers at line 49-55 then can't function correctly because the baseline state is misrepresented.

**Fix:** rewrite §"What MOVES" / §"What STAYS" sections to enumerate the actual asset-management BSEE-2024 page, decide whether it migrates or stays, and justify. If staying, explicitly note that pre-flip llm-wiki content under `wikis/asset-management/wiki/sources/bsee-*.md` is grandfathered under the new routing rule with no migration; if migrating, scope the migration here.

---

### [MAJOR] Supersession is incomplete — llm-wiki has its own parallel governance doc still asserting the old routing

**Files:**
- `/mnt/local-analysis/llm-wiki/docs/governance/service-provider-data-routing.md:37` — still asserts "row 5 → public-domain US federal regulator publication, ingest directly into `wikis/drilling-engineering/wiki/sources/`"
- `/mnt/local-analysis/llm-wiki/wikis/asset-management/wiki/index.md:65` — "Public-record per row 5 of the service-provider data routing matrix"
- `/mnt/local-analysis/llm-wiki/wikis/asset-management/wiki/log.md:23` — "routed per llm-wiki/docs/governance/service-provider-data-routing.md row 5"
- `/mnt/local-analysis/llm-wiki/wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md:26,107` — `governance:` frontmatter and body both cite row 5
- `/mnt/local-analysis/workspace-hub/docs/governance/vendor-pdf-inventory.md:42` — "US federal regulator PDFs (BSEE, EPA, USCG technical guidance) — public-domain under 17 U.S.C. § 105; route to public llm-wiki source pages directly"

The commit message claims "Supersedes (partial): docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md D1 matrix row 5". But there are at least TWO governance docs that carry the "row 5 → public" routing in slightly different forms, and the vendor-pdf-inventory doc (which is workspace-hub-tracked, not llm-wiki) explicitly says "route to public llm-wiki source pages directly" — which is exactly the routing that was just invalidated by the 2026-05-20 privacy flip. Future agents reading vendor-pdf-inventory.md will route BSEE PDFs to the now-private llm-wiki, missing the new worldenergydata-wiki target entirely.

**Impact:** the supersession is half-done. Agents using llm-wiki's CLAUDE.md or the llm-wiki-side governance doc will not see the new routing. The "Closes vamseeachanta/worldenergydata#429" claim in the commit message is premature.

**Fix:** either (a) extend this commit to update `llm-wiki/docs/governance/service-provider-data-routing.md` row 5 to point to worldenergydata-wiki, AND update `vendor-pdf-inventory.md:42-44` to say "route to worldenergydata-wiki" instead of "public llm-wiki"; OR (b) file a follow-on issue and document the supersession-cleanup-pending state explicitly in both the governance doc (line 5 "Supersedes" caveat) and the migration manifest.

---

### [MAJOR] Routing rule §6 has internal contradiction with §"Do NOT apply" line 30

**File:** `/mnt/local-analysis/workspace-hub/.claude/rules/codes-standards-data-routing.md:30`

§6 (line 27) was correctly updated to route public-domain energy data to `worldenergydata-wiki`. But the immediately-following "Do NOT apply when:" section line 30 still reads:

> The data is methodology / convention / interpretive content not directly reproducing standard text. That can live in public llm-wiki if a public sibling exists, or in the private llm-wiki under `methodology/` (current location).

The phrase "public llm-wiki" is now incoherent — llm-wiki is private as of 2026-05-20 (the very privacy flip this decision responds to, stated in line 5 of the rule itself). An agent reading this line will be confused: is there a "public llm-wiki" still? Or does "public llm-wiki" mean "the public sibling, i.e., worldenergydata-wiki"? The line was last meaningful pre-flip; post-flip it should be updated to either "the worldenergydata-wiki sibling (or future public siblings)" or simply "a public sibling wiki (e.g., worldenergydata-wiki)".

**Impact:** routing rule contradicts itself within 3 lines. Self-contradicting rules cannot be relied upon as durable governance; future agents will resolve the contradiction by picking whichever interpretation matches their current task.

**Fix:** edit line 30 to remove the stale "public llm-wiki" reference and replace with the post-flip taxonomy.

---

### [MINOR] §6 amendment loses prior list of public-domain examples

**File:** `/mnt/local-analysis/workspace-hub/.claude/rules/codes-standards-data-routing.md:27`

The pre-amendment §6 led with a list of examples ("33 CFR / 46 CFR, NOAA datasets, USCG NVIC pre-2010 issues, IMO MSC circulars after public release, IEC publications past expiry, NIST publications, ASTM withdrawn-and-republished") that established the public-domain heuristic broadly. The amended §6 preserves the list but then names worldenergydata-wiki as the sibling for "US federal public-domain energy data (BSEE / NOAA / USGS / MMS)" only. The reader is left wondering: where do USCG NVIC pre-2010, IEC-past-expiry, or NIST publications route? The pre-amendment "may stay in a public sibling wiki if desired" was vague but applied to all of these; the amendment is specific only for BSEE/NOAA/USGS/MMS and silent on the rest.

**Impact:** routing for non-energy public-domain content (e.g., NIST publications in marine-engineering work) is now under-specified. The natural inference is "do the same thing — create a sibling wiki" but that's a per-domain repo decision the rule doesn't authorize.

**Fix:** add one sentence: "For public-domain content outside the US federal energy scope (NIST, IEC past expiry, etc.), file a routing-decision issue rather than unilaterally extending the worldenergydata-wiki scope or creating a new sibling repo."

---

### [MINOR] Decision doc's "alternative options considered" is non-exhaustive

**File:** `/mnt/local-analysis/workspace-hub/docs/governance/2026-05-20-public-data-corpus-routing-decision.md:21-39`

The doc considers three options: (A) new public sibling wiki, (B) route into private llm-wiki, (C) hybrid per-artifact routing. The list is not exhaustive in a way that matters for the 6-month review trigger. Specifically missing:

1. **Option D: embed in `worldenergydata` library repo** as a `wiki/` subdirectory. The decision-revision trigger at line 69(a) actually names this as a fallback ("absorb worldenergydata-wiki into `worldenergydata/wiki/`"), implying it was the leading fallback but it isn't presented in §Rationale as a considered alternative. Why was a 2-repo decision preferred over a 1-repo `worldenergydata/wiki/` layout from the start? The doc doesn't say. The choice has real costs (sync friction, dual READMEs, two-repo cross-links).
2. **Option E: GitHub Wiki feature** on `worldenergydata`. Explicitly rejected in §Option A line 26 with a parenthetical reason ("supports PR review + CI + `gh issue` cross-references; matches the established llm-wiki pattern") but not surfaced as a numbered alternative. Reader has to read carefully to find the rejection.
3. **Option F: GitLab/Bitbucket mirror** — not relevant here, but the doc claims to be a durable decision artifact; omitting "we considered cross-host mirroring" is fine but worth a one-liner.

**Impact:** the 6-month review at 2026-11-20 (named in line 69) will have to re-investigate Option D from scratch because the current doc doesn't capture why it was rejected on first round. The user (or successor) will burn cycles re-deriving rationale.

**Fix:** add a one-paragraph §"Alternatives not selected" with explicit Options D / E / F rationales (even single-sentence dispositions).

---

### [MINOR] MMS public-domain claim citation is structurally weak

**File:** `/mnt/local-analysis/worldenergydata-wiki/wiki/mms/index.md:40-42`

The MMS page asserts:

> US federal government work, 17 USC §105. Pre-dissolution material retains federal-public-domain status regardless of dissolution. `last_license_check: 2026-05-20`.

The 17 USC §105 claim is correct as a matter of law (federal-employee-authored work is uncopyrightable, and dissolution of the agency does not retroactively copyright pre-existing federal work). BUT the page's `sources:` frontmatter (lines 12-14) cites `https://www.boem.gov/about-boem/reorganization` and `https://www.bsee.gov/about` — neither of which is a TOU document for legacy MMS material. The other three index pages (BSEE, NOAA, USGS) cite actual TOU/disclaimer URLs with quoted text; MMS does not. The MMS "verification" therefore rests on the legal-inheritance argument alone, with no contemporary federal source restating the public-domain status of legacy MMS material.

**Impact:** the `last_license_check` mechanism degrades to a self-attested rubber stamp for MMS. The quarterly audit trigger at decision-doc line 68 cannot meaningfully verify MMS public-domain status against a TOU page that doesn't exist.

**Fix:** either (a) cite a successor-agency statement that legacy MMS publications inherit public-domain (BOEM or BSEE archive pages sometimes carry this); or (b) cite an Archives.gov or GovInfo page that holds legacy MMS publications under the federal-public-domain framework; or (c) explicitly mark MMS as "verification by legal-inheritance argument; no contemporary TOU available — accept reduced audit confidence" and note this in the README's contributing section.

---

### [MINOR] Cross-link discipline rule asymmetry is correct but lacks enforcement

**File:** `/mnt/local-analysis/worldenergydata-wiki/README.md:57-60` and `docs/governance/2026-05-20-public-data-corpus-routing-decision.md:57-62`

The "public→private uses prose only; private→public uses URLs" rule is well-justified. But there is no enforcement mechanism (no pre-commit check, no CI rule). Per `patterns.md` Enforcement Gradient, this is a Level-0 prose rule. The decision doc's line 70(3) acknowledges "cross-link discipline keeps breaking" as a revision trigger but does not propose adding a Level-2 script to prevent it.

**Impact:** the very condition that would trigger a re-evaluation at 6-months is the condition the rule cannot detect automatically. A pre-commit grep for `github.com/vamseeachanta/llm-wiki` in `worldenergydata-wiki/` would be a 3-line script.

**Fix:** file a follow-on issue to add `scripts/enforcement/check-no-private-wiki-links.sh` to worldenergydata-wiki, mirroring the `check-no-abs-paths.sh` pattern named in `coding-style.md`. Reference per `patterns.md` Enforcement Gradient.

---

### [MINOR] Frontmatter consistency check — bsee/noaa/usgs/mms index pages

Spot-checked all four index pages for the five required fields named in README:35-50. Result: all four pages carry `visibility: public-federal-data`, `license: public-domain`, `contribution_status: us_federal_only`, `last_license_check: 2026-05-20`, `source_authority: <full agency>`. Consistent.

However, the four index pages do NOT carry `tags:` consistently with the README contract. The README example (line 38) shows `tags: [domain, topic, concept-class]` as the expected shape. The actual tags:

- bsee:15: `[bsee, regulator, offshore, oil-gas, public-domain]`
- noaa:15: `[noaa, metocean, wave, wind, current, public-domain]`
- usgs:15: `[usgs, geology, reserves, minerals, public-domain]`
- mms:15: `[mms, regulator, offshore, oil-gas, public-domain, legacy]`

Each includes `public-domain` as a tag, which is REDUNDANT with the `license: public-domain` field. The README contract doesn't say tags duplicate license info. Minor housekeeping — but if the wiki later adds non-public-domain pages (mixed-contributor NDBC, joint USGS), the tag stops meaning anything.

**Fix:** drop `public-domain` from all four index-page tags; the `license:` field carries it canonically.

---

### [MINOR] Cross-link to nonexistent file in routing rule

**File:** `/mnt/local-analysis/workspace-hub/.claude/rules/codes-standards-data-routing.md:27`

The §6 amendment links to `[../../docs/governance/2026-05-20-public-data-corpus-routing-decision.md]`. Path is correct, file exists, link works. No defect — noting for completeness because it's the kind of cross-ref that frequently 404s in this kind of cross-doc patch and this one is fine.

---

## Verified non-defects

- No `https://github.com/vamseeachanta/llm-wiki/...` markdown links found in `worldenergydata-wiki/` (grep clean). Cross-link discipline is honored in initial scaffold.
- Frontmatter required-fields (5 fields per the README convention) present consistently across all four index pages.
- Decision doc's `Supersedes` chain (line 5) correctly identifies the 2026-05-14 D1 row 5 as the stale source; the `Related` block (line 86) lists the predecessor explicitly.
- `worldenergydata-wiki` repo carries dual-license (CC-BY-4.0 + MIT) per README:9-10, matching §6 contract.

---

## Summary (200 words)

**VERDICT: MAJOR.** Three blockers prevent merge.

**Top 3 findings:**

1. **Migration manifest is factually wrong (MAJOR)** — claims "no existing BSEE/NOAA/USGS/MMS wiki pages anywhere in the ecosystem prior to 2026-05-20", but `llm-wiki:wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md` is a substantive 100+ line BSEE-derived analysis landed 2026-05-14. The manifest argues against a strawman (the Papkov page, which doesn't exist at the claimed path either).

2. **Supersession is half-done (MAJOR)** — `llm-wiki/docs/governance/service-provider-data-routing.md:37` and `workspace-hub/docs/governance/vendor-pdf-inventory.md:42-44` still route "BSEE/NOAA → public llm-wiki" with no awareness of the new worldenergydata-wiki target. The commit's "Closes #429" is premature.

3. **Routing rule §6 self-contradicts (MAJOR)** — line 27 correctly names worldenergydata-wiki as the public sibling; line 30 still references "public llm-wiki" (which is now private per the very flip this commit responds to).

**Blockers:** all three above. The MINOR findings (alternatives not exhaustively considered, MMS TOU citation weakness, missing enforcement script, tag/license redundancy) can ship as follow-on issues.

**Recommendation:** extend this commit (or land an immediate follow-on) to fix the three MAJORs before treating #429 as closed.
