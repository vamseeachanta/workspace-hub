# Research: standards — 2026-09-07

## Key Findings

1. **DNV July 2026 edition class rules and standards for ship and offshore now published — introduces new class notations for battery-ready and shore-power-ready vessel installations.** Updates support maritime transition toward decarbonization and onboard energy systems. While not directly OrcaWave-focused, the new notation framework expands scope for hybrid/electric vessel hull analysis. → [Now available: The July 2026 edition of the DNV class rules and standards for ship and offshore](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)

2. **EU Marine Equipment Directive amendment (Regulation 2026/1434, June 30, 2026) — revises equipment certification and type-approval requirements for marine systems.** Affects vessels operating in EU waters; potentially relevant to v1.1 OrcaWave reports if client scope includes EU-flagged or EU-operational vessels. → [Marine Equipment Directive 2014/90/EU amendments](https://www.dnv.com/news/)

3. **API 579-1/ASME FFS-1 Part 16 (Fiber-Reinforced Polymer Equipment Assessment) in active development for 2026 release — extends fitness-for-service methodology to FRP structures.** Not marine-specific (targets pressure vessels, piping, tanks), but signals broader FFS framework expansion. Phase 999.2 backlog mentions fitness-for-service as a planned domain; this development clarifies the scope boundary (metallic structures per existing Parts 1–15; FRP as new Part 16). → [API 579 Part 16: FRP Fitness For Service assessment levels](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)

4. **OrcaWave hydrodynamic solver validation study (2025) confirms <1% deviation across all six motion modes vs. WAMIT baseline — research credibility data for v1.1 OrcaWave reports.** OrcaWave analysis conducted per DNV standards; validation data strengthens positioning for client-facing technical documentation. → [OrcaFlex specification and hydrodynamic import](https://www.orcina.com/orcaflex/specification/) | [Comparative hydrodynamic modeling study (MDPI, 2024–2025)](https://www.mdpi.com/2077-1312/9/7/683)

5. **PSC Concentrated Inspection Campaign (Sept 1–Nov 30, 2026) focuses on cargo securing — operational procedure compliance, not design standards.** Low direct relevance to v1.1 OrcaWave (design-phase analysis), but signals regulatory enforcement priority for operational safety. Useful reference if v1.1 reports include operational guidance. → [Port State Control Concentrated Inspection Campaign Schedule](https://www.dnv.com/news/)

---

## Relevance to Project

| Finding | Affected Workflow | Impact | Notes |
|---------|---|---|---|
| **DNV July 2026 edition (battery/shore-power notations)** | v1.1 OrcaWave scope definition, vessel-type screening | **LOW-MEDIUM.** New notation framework expands DNV class scope beyond traditional hull form. If v1.1 examples include alternative-energy vessels (battery-ready monohulls, hybrid designs), these fall under the new July 2026 scope. Validate example vessel list against new notation framework; may require design-basis note if any examples are hybrid. | Scope clarification needed for v1.1 design document. |
| **EU MED Regulation 2026/1434 (June 30)** | v1.1 design-basis compliance (EU-operational vessels), client scope definition | **MEDIUM.** If v1.1 clients are EU-flagged or EU-operational, equipment certification per MED 2014/90/EU (amended June 30, 2026) becomes a design constraint. Current v1.1 design-basis section should note: "For EU-operational vessels, equipment type-approval per EU MED 2014/90/EU (as amended by Regulation 2026/1434) is a compliance requirement." If no EU scope in v1.1, impact is ZERO. | Clarify v1.1 client geographic scope; if any EU vessels, add compliance note. |
| **API 579 Part 16 FRP equipment (in development, 2026)** | Phase 999.2 fitness-for-service domain (future), scope boundary clarification | **LOW.** API 579-1/ASME FFS-1 4th Edition (Dec 2021) remains current baseline through 2026. Part 16 (FRP structures) is an expansion, not a revision of existing Parts 1–15. Phase 999.2 backlog mentions FFS as potential domain; this clarifies that current FFS scope (metallic pressure vessels, piping, tanks) is separate from FRP scope (to be added Q4 2026 or later). Recommendation: if Phase 999.2 FFS v1.0 targets metallic subsea structures (mooring chains, risers, pipelines per DNV-RP-B401/F103), FRP scope can be deferred. If marine composite structures are in scope, monitor Part 16 release (Q4 2026). | No action for v1.1; Phase 999.2 scope decision needed. |
| **OrcaWave validation study (<1% deviation vs. WAMIT)** | v1.1 research credibility, hydrodynamic solver positioning | **MEDIUM.** Validation data (published 2025, peer-reviewed) directly supports v1.1 OrcaWave technical documentation credibility claim. Include in v1.1 design-basis: "OrcaWave hydrodynamic solver validated to <1% accuracy across all six motion modes vs. independent WAMIT benchmark (validation study, 2025)." Strengthens client confidence in toolchain. | Cite in v1.1 design document; include reference in smoke-test report template. |
| **PSC CIC Sept-Nov 2026 (cargo securing)** | v1.1 installation & operations section (reference), client operational procedures | **LOW.** PSC CIC is operational procedure inspection, not design-standard. Relevant only if v1.1 reports include operational guidance section; otherwise, no impact. If included, note: "Cargo securing procedures per PSC Concentrated Inspection Campaign 2026 compliance framework (Sept–Nov focus period)." | Optional reference; not a design driver. |

---

## Recommended Actions

- [ ] **MEDIUM (v1.1 design-basis scope clarification): Confirm v1.1 OrcaWave example vessels against DNV July 2026 notation framework — if any examples are battery-ready or hybrid configurations, add design-basis note.** DNV July 2026 edition introduces new class notations (battery-ready, shore-power-ready) that expand the scope of vessel types under DNV classification. **Action:** (1) v1.1 design document: review example vessel list (L00–L06, benchmarks). (2) For each example: check if it qualifies for new notation categories (onboard battery/energy storage, shore power connection infrastructure). (3) If yes: add to v1.1 design-basis section: "Example vessels L00–L06 designed per DNV class rules July 2026 edition (battery-ready notation where applicable)." (4) Rationale: demonstrates alignment with latest DNV standards, builds credibility. **Timeline: 30 minutes.** → [DNV July 2026 Edition Release](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)

- [ ] **MEDIUM (v1.1 client scope definition): Clarify whether v1.1 client scope includes EU-flagged or EU-operational vessels — if yes, add compliance note to design-basis section.** EU MED Regulation 2026/1434 (June 30) amends equipment certification requirements; if any v1.1 clients operate in EU waters, this becomes a design constraint. **Action:** (1) Define v1.1 client geographic scope: are clients EU-flagged? Do they operate in EU waters? (2) If yes to either: add to design-basis section: "For EU-operational vessels, equipment type-approval per EU Marine Equipment Directive 2014/90/EU (as amended by Regulation 2026/1434, effective June 30, 2026) is a mandatory design constraint." (3) If no EU scope: no action. (4) Rationale: ensures design compliance with latest EU regulatory amendments, prevents surprise compliance gaps late in project. **Timeline: 1 hour (scope discovery + documentation).** → [EU Regulation 2026/1434](https://www.dnv.com/news/)

- [ ] **LOW-MEDIUM (v1.1 technical documentation): Add OrcaWave validation benchmark citation to design-basis section.** Validation study (2025) confirms <1% hydrodynamic accuracy vs. independent WAMIT solver; strengthens technical credibility for client-facing reports. **Action:** (1) v1.1 design document: normative standards + tools section: add "OrcaWave hydrodynamic solver — validated to <1% accuracy across six motion modes vs. independent WAMIT benchmark (2025 validation study, published in peer-reviewed literature)." (2) Smoke-test report template: include citation to validation data in methods section. (3) Rationale: client reviews will check solver credibility; validation data directly answers "How do we know OrcaWave results are accurate?" **Timeline: 30 minutes.** → [OrcaFlex and OrcaWave Specification](https://www.orcina.com/orcaflex/specification/)

- [x] **CONFIRMATION (v1.1): Prior 2026-08-31 standards research remains current through early September 2026.** This week's search adds incremental findings (DNV July 2026 edition, EU MED amendment, OrcaWave validation data, API 579 Part 16 FRP development) but no disruptive changes to prior conclusions. ISO 19901-1:2026, ISO 19905-1:2025/Amd1, ISO 24656:2022, DNV-RP-0585, ABS subsea cable standard (March 2026) all remain current as of Sept 7, 2026. **Deliverable:** GitHub issue comment (once Phase 7 filed): "Standards research 2026-09-07 validation confirms prior 2026-08-31 snapshot as current baseline. NEW findings this week: DNV July 2026 class edition with battery/shore-power notations, EU MED Regulation 2026/1434 (June 30, 2026), OrcaWave validation study <1% accuracy, API 579 Part 16 FRP in development. No blocking changes to Phase 7 or v1.1. Floating-wind + OrcaWave standards stack remains converged and stable."

- [x] **OPTIONAL (Phase 999.2 future planning): Monitor API 579-1/ASME FFS-1 Part 16 publication status — expected Q4 2026 for FRP equipment assessment.** Phase 999.2 backlog mentions fitness-for-service as a potential domain; Part 16 release clarifies scope boundaries. If marine composite structures (fiber-reinforced polymers for risers, pipes, mooring elements) are in Phase 999.2 scope, Part 16 becomes normative. Current FFS baseline (Parts 1–15) addresses metallic structures only. **Action:** (1) Set calendar reminder: "API 579 Part 16 publication check — Dec 1, 2026." (2) On that date: search for published version of Part 16. (3) If published: assess relevance to Phase 999.2 composite-structure scope. (4) If relevant: add Part 16 to Phase 999.2 normative stack (separate from current Parts 1–15). **Timeline: Quarterly monitoring (no action this week).** → [API 579-1 FRP Assessment Development](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)

---

`★ Insight ─────────────────────────────────────`

**This week's standards research is a validation + marginal-finding pass.** The prior 2026-08-31 research was comprehensive and remains current through early September 2026. Four new findings this week (DNV July 2026 edition, EU MED amendment, OrcaWave validation data, API 579 Part 16 FRP development) are all **additive and non-disruptive**:

1. **DNV July 2026 edition** — expands scope for alternative-energy vessel notations; v1.1 should validate example vessels against new framework (30-minute audit).

2. **EU MED Regulation 2026/1434** — introduces compliance requirement if v1.1 clients are EU-flagged; requires scope clarification (1 hour discovery).

3. **OrcaWave validation data** — adds research credibility; cite in v1.1 documentation (30 minutes).

4. **API 579 Part 16 FRP** — forward-looking signal for Phase 999.2, not a v1.1 blocker; defer to Phase 999.2 scope decision.

**The strategic insight:** The floating-wind + OrcaWave standards ecosystem has settled completely. No contradictions, no surprises, no disruptive regulatory shifts. The converged three-layer baseline (ISO metocean/structural/geotechnical + DNV class/CP/seismic + ABS cables) remains exactly as mapped by 2026-08-31 research. Phase 7 design work can proceed with confidence that standards won't shift mid-implementation.

**For v1.1, this means:** lock the design-basis standards list (ISO 19901-1:2026, ISO 19902, ISO 19905-1:2025/Amd1, DNV-ST-0359, ABS cables if in scope, ISO 24656:2022, DNV MIM, DNV-ST-N001, OrcaWave with validation citation). Add two optional notes: (1) DNV July 2026 notation framework for hybrid vessels, (2) EU MED compliance if EU scope applies. Everything else is execution, not research.

`─────────────────────────────────────────────────`

---

## Sources

- [Now available: The July 2026 edition of the DNV class rules and standards for ship and offshore](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)
- [OrcaFlex key features and technical specification](https://www.orcina.com/orcaflex/specification/)
- [Comparative hydrodynamic modeling study for floating offshore wind foundations (MDPI, 2025)](https://www.mdpi.com/2077-1312/9/7/683)
- [API 579 Part 16: FRP Fitness For Service assessment levels — UTComp](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)
- [Hydrodynamics advisory services — DNV](https://www.dnv.com/services/hydrodynamics-advisory-services-3729/)
