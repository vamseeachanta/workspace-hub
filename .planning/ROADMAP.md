# Workspace Hub — Roadmap v1.0

## Milestone 1: Foundation Sprint

### Phase 1: Accelerate digitalmodel development
**Goal:** Ship 3+ new calculation modules (on-bottom stability, ASME B31.4 wall thickness, spectral scatter fatigue) with full test coverage, standards traceability manifests, and CI validation
**Why:** digitalmodel is the product engine; everything else (website, marketing, client work) depends on it having robust, validated calculations
**Must-haves:**
- Identify highest-value calculation gaps (what clients actually need vs what exists)
- Increase test coverage on existing modules
- Streamline the standard-to-code pipeline (reduce time from reading a standard clause to shipping a validated function)
**UAT:** 3+ new calculation modules shipped with full test coverage and traceability to standards
**Plans:** 5 plans

Plans:
- [x] 01-01-PLAN.md — YAML manifest schema (Pydantic model + CI validation script)
- [x] 01-02-PLAN.md — On-bottom stability module (DNV-RP-F109)
- [x] 01-03-PLAN.md — ASME B31.4 wall thickness code strategy
- [x] 01-04-PLAN.md — Spectral fatigue from sea-state scatter diagrams (DNV-RP-C203)
- [x] 01-05-PLAN.md — Integration: validate manifests, update registry, cross-module tests

### Phase 2: Accelerate worldenergydata pipelines
**Goal:** Wire stub adapters to real data clients, add staleness monitoring and email alerting, curate manufacturer data for digitalmodel
**Why:** Data freshness and reliability is table stakes for credibility with clients; stale data = no trust
**Must-haves:**
- Audit current pipeline reliability (what breaks, how often, how stale)
- Fix or rebuild flaky data ingestion
- Add monitoring/alerting for data freshness
**UAT:** All active data sources updating on schedule with staleness matching each source's publication cadence
**Plans:** 6 plans

Plans:
- [ ] 02-04-PLAN.md — Staleness monitoring and email alerting
- [ ] 02-05-PLAN.md — Curated manufacturer data CSVs and Tier 2 adapter scaffolding
- [ ] 02-06-PLAN.md — Integration: status enrichment, scheduler wiring, full pipeline test

### Phase 3: GTM and marketing — aceengineer-website
**Goal:** Position aceengineer.com as the go-to platform for offshore engineering calculations
**Why:** Engineering capability without visibility = zero clients
**Must-haves:**
- Landing page that communicates the value prop (timeless engineering, single source of truth)
- Calculation showcase — interactive demos of what digitalmodel can do
- SEO and content strategy targeting offshore/subsea engineering keywords
- Pricing/access model (freemium? subscription? per-calculation?)
**UAT:** Website live with clear value prop, at least 3 calculation demos, and a signup/contact flow

### Phase 4: Client acquisition — 3-5 clients + broad individual user base
**Goal:** 3-5 paying clients (consultancies, operators) and a growing base of individual engineers using the platform
**Why:** Clients validate commercial value; individual users build community, word-of-mouth, and long-tail revenue
**Must-haves:**
- Identify target segments: enterprise (small consultancies, operators) + individual (independent engineers, students, training)
- Enterprise outreach (LinkedIn, industry conferences, direct contacts)
- Individual growth (SEO, open-access tier, engineering community engagement)
- Onboarding flow — from signup to first successful calculation
- Feedback loop — capture what users need that doesn't exist yet
**UAT:** 3+ paying clients (or committed pilots), measurable individual user signups trending upward

### Phase 5: Nightly research automation
**Goal:** Keep PROJECT.md and domain context enriched automatically
**Why:** Brownfield project needs continuous context refresh without manual effort
**Must-haves:**
- Scheduled GSD researcher agents running nightly
- Output to `.planning/research/` for periodic review
- Domain-specific research: new standards, competitor tools, industry trends
**UAT:** Nightly job running, research artifacts accumulating, at least one insight actioned
