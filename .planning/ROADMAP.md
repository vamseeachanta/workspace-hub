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

### Phase 2: Accelerate worldenergydata pipelines ✓
**Goal:** Wire stub adapters to real data clients, add staleness monitoring and email alerting, curate manufacturer data for digitalmodel
**Why:** Data freshness and reliability is table stakes for credibility with clients; stale data = no trust
**Must-haves:**
- Audit current pipeline reliability (what breaks, how often, how stale)
- Fix or rebuild flaky data ingestion
- Add monitoring/alerting for data freshness
**UAT:** All active data sources updating on schedule with staleness matching each source's publication cadence
**Verified:** 2026-03-26 — 7/7 truths, 56 tests, 17/17 requirements | [02-VERIFICATION.md](phases/02-accelerate-worldenergydata-pipelines/02-VERIFICATION.md)
**Plans:** 6 plans

Plans:
- [x] 02-01-PLAN.md — Foundation fixes + EIA adapter wiring with Parquet output
- [x] 02-02-PLAN.md — BSEE adapter with per-dataset download and Parquet output
- [x] 02-03-PLAN.md — SODIR adapter with updated API URL and Parquet output
- [x] 02-04-PLAN.md — Staleness monitoring and email alerting
- [x] 02-05-PLAN.md — Curated manufacturer data CSVs and Tier 2 adapter scaffolding
- [x] 02-06-PLAN.md — Integration: status enrichment, scheduler wiring, full pipeline test

### Phase 3: GTM and marketing — aceengineer-website
**Goal:** Position aceengineer.com as the go-to platform for offshore engineering calculations
**Why:** Engineering capability without visibility = zero clients
**Must-haves:**
- Landing page that communicates the value prop (timeless engineering, single source of truth)
- Calculation showcase — interactive demos of what digitalmodel can do
- SEO and content strategy targeting offshore/subsea engineering keywords
- Pricing/access model (freemium? subscription? per-calculation?)
**UAT:** Website live with clear value prop, at least 3 calculation demos, and a signup/contact flow
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md — Calculator engines: OBS (DNV-RP-F109) + wall thickness (ASME B31.4) with TDD
- [x] 03-02-PLAN.md — Site-wide updates: nav, landing page value prop, pricing page, footer
- [x] 03-03-PLAN.md — Calculator pages, calculator index update, sitemap, visual verification

### Phase 4: Client acquisition — 3-5 clients + broad individual user base
**Goal:** Working enterprise funnel (calculator -> case study -> contact) with measurable conversion tracking, prospect pipeline management, and case study sales collateral
**Why:** Clients validate commercial value; individual users build community, word-of-mouth, and long-tail revenue
**Must-haves:**
- Case studies paired with calculators as enterprise sales collateral
- Enhanced calculator CTAs linking to specific case studies
- Contact form project type selector for lead qualification
- GA4 enhanced event tracking across enterprise funnel
- GitHub Issues prospect pipeline for manual outreach tracking
**UAT:** 3+ paying clients (or committed pilots), measurable GA4 traffic and calculator usage trending upward
**Plans:** 3 plans

Plans:
- [x] 04-01-PLAN.md — Case studies: OBS assessment + multi-code wall thickness comparison + index/sitemap update
- [x] 04-02-PLAN.md — Contact form project type selector + GA4 enhanced events on calculators and pricing
- [x] 04-03-PLAN.md — Wire calculator CTAs to case studies, scroll depth tracking, GitHub Issues pipeline, visual verification

### Phase 5: Nightly research automation
**Goal:** Keep PROJECT.md and domain context enriched automatically
**Why:** Brownfield project needs continuous context refresh without manual effort
**Must-haves:**
- Scheduled GSD researcher agents running nightly
- Output to `.planning/research/` for periodic review
- Domain-specific research: new standards, competitor tools, industry trends
**UAT:** Nightly job running, research artifacts accumulating, at least one insight actioned

### Phase 6: Update plan and vision for digitalmodel repo
**Goal:** Define the updated roadmap, architecture vision, and development priorities for the digitalmodel repo
**Why:** Phase 1 shipped 3 new calculation modules, but the repo needs a refreshed plan reflecting current capabilities, market direction, and technical debt
**Must-haves:**
- Audit current state: modules, test coverage, architecture, open issues
- Define updated vision: what digitalmodel should become (library vs platform vs API)
- Prioritize next calculation modules based on client demand and aceengineer.com needs
- Document technical debt and architecture improvements needed
- Create actionable roadmap within the digitalmodel repo
**UAT:** Updated README/vision doc and roadmap committed to digitalmodel repo, priorities aligned with aceengineer.com GTM
**Plans:** 2 plans

Plans:
- [ ] 06-01-PLAN.md — Tiered roadmap (ROADMAP.md) + module-registry.yaml maturity refresh
- [ ] 06-02-PLAN.md — Vision direction (CALCULATIONS-VISION.md) + README trim + CHANGELOG update

## Backlog

### Phase 999.1: Ship Plan CAD Pipeline — Curve reconstruction for 3D hull lofting (BACKLOG)

**Goal:** Reconstruct continuous hull curves from fragmented skeleton vectorization, enabling 3D hull surface generation via FreeCAD/Gmsh
**Context:** WRK-5055 Phase 1 complete — 110 SNAME ship plans cataloged, 986 pages scanned, skeleton DXFs generated for all profiles and 3 lines plans (BB-45 USS Colorado, EC2-S-C1 Liberty Ship, SS-563 USS Tang). FreeCAD `Part.makeLoft()` proven functional but current vectorization produces fragmented pixel-edge traces unsuitable for direct lofting.
**Requirements:**
- Region segmentation: separate body plan / half-breadth / sheer plan views by pixel position
- Curve reconstruction: join fragments via directional continuity into continuous B-splines
- Curve classification: distinguish cross-sections from waterlines / buttocks / grid / text
- Coordinate transform: pixel space → real units using known ship dimensions
- 3D placement: position cross-sections at longitudinal stations
- Install FreeCAD Ship Workbench addon (or upgrade to FreeCAD 1.0+)
**Consider:** geomdl/NURBS-Python for pure-Python curve fitting, Gmsh `addThruSections` for direct hull surface lofting
**Prerequisites:** ship-plans-catalog.yaml (110 vessels), skeleton DXFs for 3 lines plans, FreeCAD loft API proven
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)
