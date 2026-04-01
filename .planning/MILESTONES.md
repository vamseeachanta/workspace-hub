# Milestones

## v1.0 Foundation Sprint (Shipped: 2026-03-30)

**Phases completed:** 6 phases, 21 plans, 47 tasks

**Key accomplishments:**

- Pydantic manifest schema (ModuleManifest/FunctionEntry/StandardRef) with 9-test TDD suite and CI validation script for per-module standards traceability
- Pipeline on-bottom stability module with 5 DNV-RP-F109 functions, 20 document-verified tests, and manifest.yaml traceability
- ASME B31.4 liquid pipeline code strategy with Barlow burst (F=0.72), elastic-plastic collapse, and Battelle/AGA propagation checks
- Sea-state scatter diagram fatigue via Dirlik/TB spectral methods, composing existing frequency_domain engine with JONSWAP wave spectra and Miner's-rule accumulation
- All 3 new calculation modules validated, registered, and cross-tested at 90.5% coverage -- phase UAT met
- EIA adapter wired to EIAIngestionSync with incremental JSONL ingestion and Parquet snapshot output via shared write_parquet utility
- BSEE adapter wired to BSEEWebScraper downloading platform, pipeline, and deepwater datasets independently to Parquet via zip-to-CSV extraction
- SODIR adapter wired to factmaps.sodir.no DataService API with Parquet output for blocks, wellbores, and fields
- Staleness detection with per-source cadence thresholds and SMTP email alerting for failures and stale data
- Curated subsea CSVs (rigid jumpers + mooring) with Pydantic BaseModel validation, plus 4 Tier 2 adapter stubs returning skipped status
- TDD-driven OBS (DNV-RP-F109) and wall thickness (ASME B31.4 + Timoshenko) JavaScript calculation engines with 19 passing tests
- Updated site-wide nav with Calculators link and Request Pricing CTA, redesigned landing page hero around 'single source of truth' theme with calculator showcase, and created display-only 3-tier pricing page
- Two interactive calculator HTML pages (OBS + wall thickness) with Plotly charts, GA4 tracking, Schema.org SEO, and updated index listing 5 calculators
- 2 engineering case studies (pipeline OBS + multi-code wall thickness) with Schema.org markup, GA4 tracking, calculator cross-links, and enterprise CTA funnel
- Project type selector on contact form with 7 options, cta_click events on all 5 calculator pages, pricing_cta_click events on pricing page, and input_count session tracking on 3 calculator pages
- Calculator CTAs wired to specific case studies with funnel_step tracking, scroll depth analytics on case study pages, and GitHub Issues prospect pipeline with 8 labels
- Weekday-only 4-domain researcher with Haiku/Sonnet model selection, web search, prior context feeding, output validation, and 90-day pruning
- Independent staleness detection script with 60h threshold, cron registration at 06:00 UTC, and comprehensive research README documenting weekday rotation, action tables, and retention
- Tiered development roadmap with OrcaFlex + CP as Tier 1 priorities, tech debt triage, and module-registry.yaml maturity refresh for Phase 1 deliverables
- Library-first vision direction in CALCULATIONS-VISION.md, README trimmed from 650 to 81 lines, and CHANGELOG [2.1.0] entry for Phase 1 GSD sprint deliverables

---
