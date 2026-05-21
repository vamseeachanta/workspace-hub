# Public-data corpus routing decision — BSEE / NOAA / USGS / MMS

> **Date:** 2026-05-20
> **Decision authority:** user (vamsee), authorized via [worldenergydata#429](https://github.com/vamseeachanta/worldenergydata/issues/429) `status:plan-approved`
> **Supersedes:** [`docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md`](2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md) D1 matrix row 5 ("regulator records → public llm-wiki" — broken by 2026-05-20 privacy flip)
> **Routing rule update:** [`.claude/rules/codes-standards-data-routing.md`](../../.claude/rules/codes-standards-data-routing.md) §6
> **Plan:** [`docs/plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md`](../plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md)

## Decision

US federal public-domain energy data (BSEE, NOAA, USGS, MMS) routes to a **new public sibling wiki** at [`vamseeachanta/worldenergydata-wiki`](https://github.com/vamseeachanta/worldenergydata-wiki) — CC-BY-4.0 for prose/data, MIT for code.

Vendor-licensed engineering standards content continues to route to the private `vamseeachanta/llm-wiki` per the routing rule §1–§5; nothing changes there.

## Rationale

The 2026-05-20 `vamseeachanta/llm-wiki` privacy flip closed the licensing window for vendor-licensed standards (OCIMF, API, DNV, ABS, IACS, ASCE, ASME, etc.). That posture is correct for those publishers — they're sold by Witherby / Techstreet / IHS Markit and are not freely redistributable.

But the same posture would invert the public-domain status of US federal data, which is the engineering reality for BSEE / NOAA / USGS / MMS corpora. The wiki tier should match the licensing reality of the underlying data, not invert it.

Three options were considered ([plan §Goal](../plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md)):

### Option A (chosen) — new public sibling wiki

- Repo: `vamseeachanta/worldenergydata-wiki`
- Structure: regular repo with `wiki/` directory (NOT GitHub built-in Wiki — supports PR review + CI + `gh issue` cross-references; matches the established llm-wiki pattern)
- License: CC-BY-4.0 (prose/data) + MIT (code)

**Single strongest reason:** the existing GTM consumer surface is *already public*. `vamseeachanta/worldenergydata` is a public MIT repo with 6 ready-to-send client reports rendered from BSEE / NOAA / MMS data. Routing the derived corpus into private llm-wiki would break the public-citation surface clients already use (clients click through to a 404 or auth-gate).

### Option B (rejected) — route into private llm-wiki

Rejected because: breaks the GTM-report citation surface; wastes the public-domain status; conflicts with `worldenergydata`'s MIT posture.

### Option C (rejected as default; preserved as escape hatch) — hybrid per-artifact routing

Rejected as default because per-ingest routing-decision tax compounds; the existing 6-row service-provider matrix already costs decision-time, and adding a hybrid public/private split per artifact compounds it. Cross-wiki linking private→public works (just URLs); the reverse (public→private) creates dead-link clusters in CC-BY-4.0 material.

**Preserved as an explicit escape hatch:** when a derived analysis genuinely mixes public-data substrate with vendor-licensed standards interpretation (e.g., a BSEE production analysis that depends on a vendor coefficient table for interpretation), the page routes to private llm-wiki with a redacted public summary in `worldenergydata-wiki`. Per-page `contribution_status` frontmatter signals this.

## Frontmatter convention

Pages in `worldenergydata-wiki` carry:

```yaml
visibility: public-federal-data
license: public-domain
contribution_status: us_federal_only | mixed_private_contributors
source_authority: "<full agency name>"
last_license_check: YYYY-MM-DD
```

- `visibility: public-federal-data` distinguishes pages in this wiki from `visibility: private-llm-wiki` in the private vendor-licensed wiki.
- `contribution_status: mixed_private_contributors` flags datasets like NDBC ship-of-opportunity reports or wind-farm SCADA contributions; mixed entries route summary public + full data stays at `/mnt/ace/`.
- `last_license_check` supports quarterly license-drift audit per [#429](https://github.com/vamseeachanta/worldenergydata/issues/429) — a follow-on cron is deferred to a separate issue.

## Cross-wiki linking discipline

- **Public→private** (worldenergydata-wiki → llm-wiki): reference by prose ONLY, NOT as Markdown links (would 404 for external readers of the public repo). Example: "For vendor-licensed standards interpretation see the private llm-wiki under `wikis/marine-engineering/wiki/standards/`."
- **Private→public** (llm-wiki → worldenergydata-wiki): use full URLs — they resolve for everyone.

This asymmetry intentionally pushes the friction onto the private side, which has fewer external readers.

## Decision-revision triggers

This decision is revisited if:

1. **A federal data source changes its TOU** to introduce restrictions (e.g., BSEE adds a non-redistribution clause). Mitigation: per-source `last_license_check` frontmatter + quarterly audit.
2. **The maintenance burden of two repos** becomes real at the 6-month mark (2026-11-20 review). If yes, options: (a) absorb worldenergydata-wiki into `worldenergydata/wiki/`, (b) collapse to private and accept the GTM-citation friction.
3. **Client-deliverable patterns** demand a per-deliverable visibility choice that this routing doesn't support. Mitigation: file a sibling routing-decision issue, don't unilaterally amend §6.

## Out of scope

- Vendor-licensed standards routing — settled by routing rule §1–§5 (private llm-wiki).
- Client-project content (B1528, SIROCCO, acma-projects) — separate epic under client-engagement issues.
- License-drift detection cron script — follow-on issue, not built here.
- New public-domain data sources beyond BSEE / NOAA / USGS / MMS (EIA, IEA-public, IRENA, etc.) — applies the same rule once landed; not enumerated.

## Related

- Plan: [`docs/plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md`](../plans/2026-05-20-issue-429-worldenergydata-public-data-routing.md)
- Routing rule (post-amendment): [`.claude/rules/codes-standards-data-routing.md`](../../.claude/rules/codes-standards-data-routing.md) §6
- Origin issue: [`vamseeachanta/worldenergydata#429`](https://github.com/vamseeachanta/worldenergydata/issues/429)
- Umbrella: [`vamseeachanta/workspace-hub#2774`](https://github.com/vamseeachanta/workspace-hub/issues/2774)
- New repo: [`vamseeachanta/worldenergydata-wiki`](https://github.com/vamseeachanta/worldenergydata-wiki)
- Stale predecessor: [`docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md`](2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md) D1 row 5
- Memory: `project_llm_wiki_privacy_flip`, `feedback_codes_standards_data_in_private_wiki`, `project_worldenergydata_gtm_state`
