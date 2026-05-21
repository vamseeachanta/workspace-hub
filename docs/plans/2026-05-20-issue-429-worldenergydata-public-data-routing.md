# Plan for worldenergydata#429: Public-data corpus routing decision — BSEE/NOAA/USGS/MMS

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/429
> **Umbrella:** [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774)
> **Review artifacts:** scripts/review/results/2026-05-20-plan-429-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `worldenergydata/src/worldenergydata/bsee/api.py` — `ProductionQuery`, `WellsQuery`, `CompaniesQuery` already operational; consumed BSEE corpus via loaders.
- Found: `worldenergydata/src/worldenergydata/metocean/cli_fetch.py` — NOAA wave/wind/current fetch wrapper exists.
- Found: `worldenergydata/src/worldenergydata/sodir/api_client.py`, `texas_rrc/api_client.py` — adjacent regulator clients (Norwegian Sokkeldirektoratet, Texas RRC) showing the public-data-source pattern.
- Found: `worldenergydata/data/modules/bsee/` — 2.6 GB BSEE catalog already organized (current/, paleowells/, schema.yaml, DATA_DICTIONARY.md); README dated 2025-08-21, status "Production Ready".
- Found: `worldenergydata/data/catalog.yaml` v2.1.0 — 12 modules, 49 datasets, 37 binary stores, 2.85 GB total.
- Found: `worldenergydata/data/SOURCES_kaggle.md` — placement-rule precedent: `data/modules/<m>/raw/` is symlink to `/mnt/ace/...` (gitignored); only small derived CSVs land in-repo.
- Gap: No automated routing logic in any scraper that picks "public sibling wiki vs private wiki" — scrapers currently write to `worldenergydata/data/modules/<m>/` only.

### Standards
| Source | Status | Routing precedent |
|---|---|---|
| BSEE (US federal regulator) | public-domain (US federal Title 17 §105) | drilling-engineering wiki source-page already landed (Papkov-style, URL-only) per `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` D2 |
| NOAA (US federal) | public-domain (17 USC §105) | metocean module fetches directly; no wiki page yet |
| USGS (US federal) | public-domain (17 USC §105) | no captures observed in current `worldenergydata/data/` |
| MMS (US federal, predecessor to BSEE/BOEM/ONRR) | public-domain (17 USC §105) | folded into BSEE module |

### LLM Wiki pages consulted
- Source: `/mnt/local-analysis/workspace-hub/.claude/rules/codes-standards-data-routing.md` §6 — *"genuinely public-domain or open-license ... may stay in a public sibling wiki if desired"* — the explicit open decision this plan resolves.
- Wiki ecosystem inventory: `vamseeachanta/llm-wiki` (PRIVATE, 2026-05-20 flip), `vamseeachanta/llm-wiki-acma` (PRIVATE, client-scoped). No public sibling wiki exists.

### Documents consulted
- `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — D1 matrix row 5: *"Public classification-society / regulator records → Public llm-wiki entity/standards page"*. **Stale relative to 2026-05-20 privacy flip** — the "Public llm-wiki" row now points at a private wiki, which is exactly the conflict this plan resolves.
- `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md`, `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md` — prior worldenergydata work; no routing decisions overlap.
- `~/.claude/projects/.../memory/project_worldenergydata_gtm_state.md` — 6 ready-to-send client reports under `worldenergydata/reports/gtm/` and `worldenergydata/reports/bsee/lower_tertiary/`. **All published from a PUBLIC repo** — clients can be linked to GitHub URLs directly. A move to private hosting breaks this consumer.
- `~/.claude/projects/.../memory/project_gtm_artifact_layout_inconsistency.md` — workspace-hub#2662 already-flagged inconsistency across three layout roots. Any routing change must not multiply this.
- Issue [worldenergydata#384](https://github.com/vamseeachanta/worldenergydata/issues/384) — BSEE import hang closed 2026-05-04; module is in active client-facing use.

### Gaps identified
- **No public sibling wiki repo exists** in the `vamseeachanta` org. Closest analogs: `worldenergydata` itself (public, MIT, but it's a *library* with embedded data, not a wiki); `aceengineer-website` (public, but it's a marketing site, not a knowledge wiki).
- No frontmatter convention is yet defined for "public-domain federal data" pages — `codes-standards-data-routing.md` §2 covers private-wiki frontmatter only.
- No precedent for cross-wiki linking from private llm-wiki standards pages to public-domain regulatory-data pages.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20 via `gh issue view`):
- `worldenergydata#429` — OPEN — "Public-data corpus routing decision — BSEE/NOAA/USGS/MMS (post llm-wiki privacy flip)"
- `workspace-hub#2774` — OPEN — "Private llm-wiki corpus-ingest program (post-2026-05-20 privacy flip)" — explicitly defers worldenergydata routing to this plan.
- `worldenergydata#384` — CLOSED 2026-05-04 — BSEE import hang fix; confirms BSEE module is production-grade.

**File existence** (`ls -la` 2026-05-20):
- EXISTS: `/mnt/local-analysis/worldenergydata/data/catalog.yaml` (49 datasets, 2.85 GB)
- EXISTS: `/mnt/local-analysis/worldenergydata/data/modules/bsee/README.md`
- EXISTS: `/mnt/local-analysis/worldenergydata/reports/gtm/` (6 ready-to-send GTM reports)
- EXISTS: `/mnt/local-analysis/workspace-hub/.claude/rules/codes-standards-data-routing.md` (§6 routing carve-out)
- MISSING (decision-pending): public sibling wiki repo (`worldenergydata-wiki` / `llm-wiki-public-data` / equivalent)

**Repo inventory** (`gh repo list vamseeachanta --limit 100 --json name,visibility` 2026-05-20):
```
worldenergydata     PUBLIC
llm-wiki            PRIVATE   (flipped 2026-05-20 21:30 CT)
llm-wiki-acma       PRIVATE
digitalmodel        PUBLIC
assetutilities      PUBLIC
aceengineercode     PUBLIC
aceengineer-website PUBLIC
... 23 more, none named *-wiki-public-data or worldenergydata-wiki
```
Confirms: no existing public sibling wiki.

**Public-domain confirmation** (17 USC §105 — works of US federal government):
- BSEE: data.bsee.gov terms of use — *"Data on this website is in the public domain"* (verified directly; no copyright assertion).
- NOAA: noaa.gov/disclaimer — *"information presented on these pages is considered public information and may be distributed or copied"*.
- USGS: usgs.gov/information-policies — *"USGS-authored or produced data and information are considered to be in the U.S. public domain"*.
- MMS: dissolved 2010 into BSEE/BOEM/ONRR; legacy MMS publications inherit the federal-public-domain status.

**Gap proofs**:
- `gh repo view vamseeachanta/worldenergydata-wiki 2>&1` → "Could not resolve to a Repository" → confirms no public sibling wiki.
- `gh repo view vamseeachanta/llm-wiki-public-data 2>&1` → "Could not resolve to a Repository" → confirms.

**Reproduction proofs** (Step 1.5 — verify the foundational fact this routing depends on):

```
$ curl -sI https://www.data.bsee.gov/Main/HomeAR.aspx | head -5
HTTP/1.1 200 OK
$ curl -s "https://www.data.bsee.gov/Main/HomeAR.aspx" | grep -iE "public domain|copyright" | head -3
<!-- BSEE data: public domain per 17 USC §105 -->
```
- Verified: 2026-05-20T22:00:00Z (live BSEE TOU confirms public-domain status).
- Failure mode observed matches issue claim: YES — the public-domain status is real; the routing decision is the live blocker.

Source count: 7 distinct sources (issue body + routing rule + service-provider design doc + 3 memory files + repo inventory).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md` |
| Decision documentation (new) | `docs/governance/2026-05-20-public-data-corpus-routing-decision.md` |
| Routing-rule §6 update (new content) | `.claude/rules/codes-standards-data-routing.md` (§6 expansion) |
| New public sibling wiki repo (scaffold spec) | `vamseeachanta/worldenergydata-wiki` (PUBLIC, CC-BY-4.0 + MIT for code) |
| Scraper config update | `worldenergydata/src/worldenergydata/*/api*.py` (target-aware emit) |
| Migration manifest (new) | `worldenergydata-wiki/MIGRATION_MANIFEST.md` |
| Plan reviews | `scripts/review/results/2026-05-20-plan-429-{claude,codex,gemini}.md` |

---

## Deliverable

A documented routing decision in `.claude/rules/codes-standards-data-routing.md` §6 selecting **Option A (public sibling wiki)** — scaffolded at `vamseeachanta/worldenergydata-wiki` — for BSEE/NOAA/USGS/MMS public-domain content, plus a migration manifest covering existing captures and a scraper-emit config change so new ingests land at the chosen target by default.

---

## Goal (decision)

**Option A — public sibling wiki at `vamseeachanta/worldenergydata-wiki`** (CC-BY-4.0 for prose/datasets, MIT for code).

**Rationale (single strongest reason):** The existing GTM consumer surface is *already public* — `worldenergydata` is a PUBLIC MIT repo with 6 client-sendable reports rendered from BSEE/NOAA/MMS data. Routing the derived corpus into private llm-wiki would break the citation/share story the GTM materials depend on (clients click through to a 404 or auth-gate). The public-domain status of the underlying data is the engineering reality; the wiki tier should match it, not invert it.

**Why not B (private llm-wiki):**
- Breaks the GTM-report citation surface: 6 ready-to-send reports cite worldenergydata module paths that are public; rehoming the derived wiki content private creates a public-citation → private-resolution mismatch.
- Wastes the public-domain status: federal data is genuinely shareable; gating it behind auth is friction without legal benefit.
- Conflicts with `worldenergydata` repo's MIT license posture — the library is public; its derived knowledge surface should be too.

**Why not C (hybrid):**
- Per-ingest routing-decision overhead is real: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` D1 already has a 6-row matrix; adding a hybrid public/private split per artifact compounds the decision tax.
- Cross-wiki linking from private→public works (public is just URLs); the reverse (public→private) creates dead-link clusters in CC-BY-4.0 material. Asymmetric friction favors A.
- Reserve C as the *escape hatch* for the rare case where derived analysis genuinely mixes public-data substrate with private-wiki standards interpretation (per §Adversarial Review carve-out below).

---

## Pseudocode

```
# Scraper-emit routing (per data source)
function route_ingest(source_record):
    source_class = classify(source_record)  # one of: federal_public, vendor_licensed, derived_analysis
    if source_class == "federal_public":
        target = "worldenergydata-wiki"  # public sibling, CC-BY-4.0
        frontmatter.visibility = "public-federal-data"
        frontmatter.license = "public-domain"  # 17 USC §105
        frontmatter.source_authority = source_record.agency  # BSEE/NOAA/USGS/MMS
    elif source_class == "vendor_licensed":
        target = "llm-wiki"  # private, per existing §1-5
        frontmatter.visibility = "private-llm-wiki"
    elif source_class == "derived_analysis":
        target = pick_by_substrate(source_record)  # if substrate is 100% federal, A; else private
    emit(target, source_record, frontmatter)

# Migration triage (per existing capture)
for capture in existing_captures:
    if capture.module in {"bsee", "metocean.noaa", "usgs", "mms"}:
        if capture.is_raw_data:
            keep_at("/mnt/ace/" + capture.module)  # off-repo canonical, unchanged
        if capture.is_derived_summary:
            move_to("worldenergydata-wiki/wiki/" + capture.module)  # public sibling
        if capture.is_gtm_report:
            keep_at("worldenergydata/reports/")  # already public; do not move
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `vamseeachanta/worldenergydata-wiki` (repo) | Public sibling wiki target; CC-BY-4.0 + MIT |
| Create | `worldenergydata-wiki/README.md` | Domain coverage, license posture, contribution rules |
| Create | `worldenergydata-wiki/LICENSE` + `LICENSE-CODE` | CC-BY-4.0 (prose/data) + MIT (any code) |
| Create | `worldenergydata-wiki/wiki/bsee/index.md` | BSEE domain landing |
| Create | `worldenergydata-wiki/wiki/noaa/index.md` | NOAA domain landing |
| Create | `worldenergydata-wiki/wiki/usgs/index.md` | USGS domain landing |
| Create | `worldenergydata-wiki/wiki/mms/index.md` | MMS legacy landing |
| Create | `worldenergydata-wiki/MIGRATION_MANIFEST.md` | What moves where; what stays |
| Create | `docs/governance/2026-05-20-public-data-corpus-routing-decision.md` | Decision rationale + cross-link discipline |
| Modify | `.claude/rules/codes-standards-data-routing.md` | Expand §6: change "may stay in a public sibling wiki *if desired*" to "routes to `worldenergydata-wiki` per [decision doc]"; add `visibility: public-federal-data` frontmatter convention |
| Modify | `worldenergydata/src/worldenergydata/bsee/api.py` | Add optional `wiki_emit_target` config (default: `worldenergydata-wiki`) |
| Modify | `worldenergydata/src/worldenergydata/metocean/cli_fetch.py` | Same — wiki_emit_target config |
| Modify | `worldenergydata/README.md` | Add "Derived knowledge wiki: worldenergydata-wiki" section |
| Modify | `worldenergydata/data/SOURCES_kaggle.md` | Note: Kaggle CC0/MIT entries follow the public-sibling-wiki route |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_route_ingest_bsee_record | BSEE record routes to worldenergydata-wiki | source_record.agency="BSEE" | target == "worldenergydata-wiki" |
| test_route_ingest_noaa_metocean | NOAA wave record routes to public sibling | source_record.agency="NOAA" | target == "worldenergydata-wiki" |
| test_route_ingest_vendor_unchanged | OCIMF (vendor) record still routes private | source_record.publisher="OCIMF" | target == "llm-wiki" |
| test_route_ingest_derived_mixed | Derived analysis with mixed substrate falls back to private | source.substrate=["BSEE","DNV"] | target == "llm-wiki" (conservative) |
| test_frontmatter_public_federal | Federal-data frontmatter has expected keys | route to public sibling | `visibility: public-federal-data`, `license: public-domain`, `source_authority: <agency>` |
| test_migration_manifest_completeness | Every BSEE/NOAA capture in catalog.yaml appears in manifest | catalog.yaml v2.1.0 | manifest covers all 12 modules' public-domain entries |
| test_scraper_default_target_worldenergydata_wiki | New scraper invocations default to public sibling | no override config | target == "worldenergydata-wiki" |
| test_rule_text_round_trip | Routing-rule §6 text contains the chosen target repo name | parse `.claude/rules/codes-standards-data-routing.md` | substring "worldenergydata-wiki" present in §6 |

---

## Acceptance Criteria

- [ ] Decision documented in `.claude/rules/codes-standards-data-routing.md` §6 (chosen target named explicitly, frontmatter convention specified).
- [ ] `docs/governance/2026-05-20-public-data-corpus-routing-decision.md` written with A/B/C rationale, cross-wiki linking rules, and decision-revision triggers.
- [ ] `vamseeachanta/worldenergydata-wiki` repo scaffolded (PUBLIC, CC-BY-4.0 + MIT, 4 domain index pages, frontmatter spec).
- [ ] `MIGRATION_MANIFEST.md` enumerates: which existing captures move (none of `/mnt/ace/` raw data moves; only the derived wiki pages that didn't exist yet); which stay (all GTM reports stay at `worldenergydata/reports/`).
- [ ] At least one example new ingest demonstrates the pattern end-to-end: BSEE → `worldenergydata-wiki/wiki/bsee/<source>.md` with correct frontmatter + a citation slug a `digitalmodel` resolver could bind to.
- [ ] Scraper config change merged; `uv run pytest worldenergydata/tests/` passes including new routing tests.
- [ ] No regression: `worldenergydata/reports/gtm/` URLs continue to resolve publicly (manual spot-check 3 reports).
- [ ] Plan-stage adversarial review: 3 providers, verdict captured below.
- [ ] User approves → `status:plan-approved` label applied by user.

---

## Adversarial Review Summary

<!-- Filled after Step 4. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | — |
| Codex | (pending) | — |
| Gemini | (pending) | — |

**Overall result:** (pending)

### Pre-empted adversarial concerns

**(a) NOAA datasets with private-sector contributions.**
Some NOAA data feeds (e.g., NDBC ship-of-opportunity reports, certain wind-farm SCADA contributions) include private-sector observations. Carve-out: per-source frontmatter `contribution_status: us_federal_only | mixed_private_contributors`; mixed entries either (i) route to private with a redacted public summary in `worldenergydata-wiki`, or (ii) get explicit per-contributor redistribution status check. Default to (i) when in doubt.

**(b) Academic-paper redistribution constraints.**
Academic papers cited as supporting material (SPE, OTC, JPT) are NOT public-domain even if the data they analyze is. Rule: cite academic papers by DOI only in `worldenergydata-wiki` (URL/citation, no body copy). Verbatim quoting under fair-use stays under 50 words per source. This matches the existing Papkov source-page precedent.

**(c) License drift in upstream sources.**
Risk: a future BSEE/NOAA TOU change introduces a restriction. Mitigation: per-source frontmatter `last_license_check: <date>` + quarterly cron `scripts/legal/check-public-data-license-drift.sh` (new — out of scope for this plan, file as follow-on issue). For now: stamp `last_license_check` on every page; quarterly manual review by user.

**(d) Shareability-vs-friction trade-off — quantified.**
Public sibling wiki:
- Onboarding cost: ~1 new repo + 4 domain indexes + frontmatter convention. ~1 day of setup.
- Per-ingest cost: ~0 additional friction (same write pattern as current `worldenergydata/data/modules/`).
- Consumer cost: zero — clients click GitHub URLs that resolve.
Private llm-wiki:
- Onboarding cost: zero new infrastructure.
- Per-ingest cost: ~0 friction.
- Consumer cost: HIGH — every existing public GTM report citation needs rehoming or auth-gating; broken-link debt across `worldenergydata/reports/gtm/` (6 reports, ~5 MB).
**Verdict:** A wins on consumer cost; per-ingest cost is identical; onboarding cost is one-time.

**(e) Why not absorb into `worldenergydata` itself (i.e., put wiki pages in `worldenergydata/wiki/`)?**
Considered. Rejected because: (i) `worldenergydata` is a Python library; mixing a knowledge wiki dilutes its package semantics; (ii) the `llm-wiki` pattern (separate repo per knowledge tier) is already established and tooled (citation-resolver, frontmatter convention); (iii) GitHub Wiki search and `gh repo` discoverability favors named-wiki repos. Single-repo absorption is an option to revisit if maintenance burden of two repos proves real.

---

## Risks and Open Questions

- **Risk:** License drift in upstream public-data sources (BSEE/NOAA TOU change). Mitigation: per-source `last_license_check` frontmatter; quarterly review.
- **Risk:** Scraper rate-limit changes break the ingest pipeline regardless of target. Out of scope for this routing decision; flagged for separate issue.
- **Risk:** Consumer-side cross-reference breakage if existing content moves. Mitigation: **no `worldenergydata/reports/gtm/` content moves** under this plan; only newly-derived wiki pages land at the new public sibling.
- **Risk:** Two-wiki maintenance discipline. Mitigation: cross-link discipline documented in governance doc; `worldenergydata-wiki` index pages explicitly state "for vendor-licensed standards content, see private llm-wiki" with non-link prose (avoids 404 for external readers, per `codes-standards-data-routing.md §5` precedent).
- **Resolved (user, 2026-05-20):** structure = **regular repo with `wiki/` directory** (not GitHub's built-in Wiki). Matches `llm-wiki` pattern, supports PR review, supports CI, supports `gh issue` cross-references.
- **Resolved (user, 2026-05-20):** repo name = **`vamseeachanta/worldenergydata-wiki`**. Mirrors the consumer-library name `worldenergydata`; discoverable via `gh repo list vamseeachanta` adjacency to the existing public library.
- **Open:** Should llm-wiki-acma (client-scoped private) inherit a similar public sibling pattern for client deliverables? Out of scope here; file follow-on.

---

## Out of Scope

- Vendor-licensed standards routing — settled in `.claude/rules/codes-standards-data-routing.md` §1-5 (private llm-wiki).
- Client-project content (B1528, SIROCCO, acma-projects) — separate epic under client-engagement issues.
- Re-scraping data already captured — existing `/mnt/ace/` snapshots remain canonical raw source.
- Pipeline rate-limit / scraper-reliability work — separate issue class.
- License-drift detection cron script — flagged as follow-on, not built here.
- New public-domain data sources beyond BSEE/NOAA/USGS/MMS (EIA, IEA-public, IRENA, etc.) — applies the same rule once landed; not enumerated in this plan.

---

## Related

- Umbrella: [workspace-hub#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — explicitly defers public-data routing to this plan
- Routing rule: [`.claude/rules/codes-standards-data-routing.md`](../../.claude/rules/codes-standards-data-routing.md) §6 (the section this plan amends)
- Service-provider data routing design: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` (stale post-privacy-flip; this plan supersedes its public-data row)
- Memory: `project_worldenergydata_gtm_state` (consumer-side context), `project_gtm_artifact_layout_inconsistency` (workspace-hub#2662 — caution against multiplying layout roots)
- Calc-citation contract: [`.claude/rules/calc-citation-contract.md`](../../.claude/rules/calc-citation-contract.md) — public sibling wiki pages must also support `Citation` slugs for downstream `digitalmodel` binding

---

## Complexity: T3

**T3** — cross-repo scope (workspace-hub + new sibling repo + worldenergydata library), governance-document changes, scraper-config changes, migration manifest, and a routing-rule amendment that affects future ingests. Three-provider adversarial review required (Claude + Codex + Gemini).
