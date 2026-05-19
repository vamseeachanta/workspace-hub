---
name: llm-wiki-trends-and-strategies-domain-founded
description: "14th llm-wiki domain founded 2026-05-18 for workforce/forecast/strategic content that doesn't fit any technical-engineering wiki; founding source Nagar (2026) petroleum-engineering workforce crisis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 578c6ffe-2428-405f-9435-a7eebec611a4
---

The `wikis/trends-and-strategies/` domain at `vamseeachanta/llm-wiki` was founded on 2026-05-18 (commit `b6e2342c` pre-rebase, `64db6249` post-rebase). It is the 14th domain wiki in the llm-wiki ecosystem and the **first non-technical-engineering wiki** — it holds workforce demographics, industry forecasts, strategic vulnerabilities, technology-adoption framing, regulatory-strategic exposures, and market-structure changes.

**Why:** Founded in response to a LinkedIn ingest (Ankesh Nagar petroleum-engineering workforce crisis citing BLS / GETI 2026 / 83% US graduation drop) that did not fit any of the 12 prior technical-engineering wikis. The three options surfaced via AskUserQuestion were (a) skip the post out of scope, (b) force-fit into production-engineering as source-only, (c) found a new domain. User picked the new-domain path with explicit name "trends and strategies."

**How to apply:**
- Route here when a post / paper / report makes **workforce-demographic, industry-forecast, strategic-vulnerability, or market-structure** claims that don't fit a technical-engineering wiki. Examples: BLS / IEA / EIA / OPEC / DNV / Rystad / Wood Mackenzie / SPE Talent Council outlooks; corporate FID announcements at the strategic-framing level; technology-adoption-curve essays; merger / divestment / regulatory-restructuring analysis.
- **Scope-protection clause:** any technical engineering claim embedded in a `trends-and-strategies/` post stays at the framing level only — the technical content must also be captured in the relevant technical wiki via cross-link. Do NOT absorb technical content here via drift. The Lint Workflow's "Cross-wiki scope leak" check enforces this.
- **Forecast staleness:** the wiki's frontmatter schema adds `forecast_date` and `forecast_horizon` fields for forecast-type sources. Lint flags forecasts more than 2 years old without a refreshing ingest.
- Founding source: `wikis/trends-and-strategies/wiki/sources/nagar-2026-petroleum-engineering-workforce-crisis.md`. Founding seed roadmap in `wikis/trends-and-strategies/wiki/overview.md` targets BLS Occupational Outlook Handbook, IEA World Energy Employment, GETI 2026, SPE Talent Council, IADC benchmarking, and DNV Energy Transition Outlook as primary sources.

**Related:** [[project_llm_wiki_geotechnical_engineering_founded]] (sibling founding, same session); [[project_llm_wiki_external_post_ingest_workflow]] (workflow used); [[project_llm_wiki_strategic_role]] (broader llm-wiki strategic framing).
