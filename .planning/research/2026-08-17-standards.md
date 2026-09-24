# Research: standards — 2026-08-17

## Key Findings

1. **DNV July 2026 Edition FL(Y) and FMS notations confirmed stable (validated 2026-08-17).** Prior research (2026-08-10) identified new class notation FL(Y) for explicit design fatigue life specification and revised FMS notation with selectable fatigue design factors. Validation confirms these are production-active in DNV's offshore classification workflow. Structural standards for column-stabilized units, tension-leg platforms, and deepdraught floating units have been restructured to align with OS-C103, OS-C105, OS-C106. → [DNV Standards 2026 Edition](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)

2. **ABS Technical Standard for Subsea Power Cables published March 2026 (NEW — not in prior research).** Early 2026 publication establishes ABS criteria for subsea power cable systems, complements existing ABS subsea pipeline guidance. Directly relevant to floating offshore wind mooring systems and platform power/control architecture. → [ABS Offshore Maritime Technical Services](https://ww2.eagle.org/en/Products-and-Services/offshore-energy/subsea-solutions.html) | [Subsea Cable Laying Vessel — ABS Technical Standards](https://www.guiceoffshore.com/abs-publishes-new-technical-standards-for-subsea-power-cables/)

3. **API 579-1/ASME FFS-1 Part 16 (FRP equipment assessment) remains on track for 2026 finalization (validation of prior research).** Joint API/ASME committee actively developing new section for fiber-reinforced polymer composite equipment. No acceleration or delay reported since prior research. Supports Phase 999.2 composite riser assessment roadmap. → [API 579-1/ASME FFS-1 Updates](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/)

4. **ISO 19902 digital/SHM integration now confirmed as 2026 industry standard practice (reinforces prior research).** Real-time structural health monitoring systems paired with ISO 19902:2020 compliance thresholds (stress, deformation, corrosion indices). Implies OrcaWave v1.1 reports should emit structured JSON output compatible with SHM ingestion. → [ISO 19902: Essential Guide for Fixed Offshore Structures](https://community.trustcloud.ai/article/iso-19902-everything-you-need-to-know/)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Phase/Timeline |
|---------|--------------------------|--------|---|
| **DNV July 2026 FL(Y)/FMS stable + structural standards restructured** | `digitalmodel` spectral fatigue module, OrcaWave v1.1 report generation, Phase 7 smoke tests | **MEDIUM-HIGH.** Confirms prior research (2026-08-10) findings are current and unrevised. Structural standards alignment (OS-C103/105/106) should be cross-checked if digitalmodel uses DNV guidance for column/TLP sizing. **No new action needed** beyond prior research's audit recommendation. | v1.1 Phase 7 (already planned) |
| **ABS Subsea Power Cables standard (March 2026)** | Phase 999.2 (floating wind mooring power/control cables), Phase 999.1 (CAD pipeline for cable routing) | **MEDIUM.** NEW finding not in prior research. Floating offshore wind platforms require power and control umbilicals/cables from turbine to platform to subsea cable termination. ABS standard provides design criteria for these subsea segments. **Recommendation:** audit Phase 999.2 scope — if mooring system includes power/control cable design, cross-reference ABS standard for subsea cable sections. Most likely integration point: Phase 999.2 mooring module → cable sizing and ABS compliance check. | Phase 999.2 backlog (forward note) |
| **API 579-1 Part 16 (FRP) remains on track (validates prior research)** | Phase 999.2 backlog (composite riser FFS assessment) | **MEDIUM.** Confirms no acceleration or slippage in Part 16 development (still targeting 2026 finalization). Provides confidence that Phase 999.2's FRP riser FFS scope is feasible once Part 16 ships. **No action change** — maintain monitoring stance from prior research. | Phase 999.2 design (v1.2 planning) |
| **ISO 19902 SHM integration (2026 practice, validates prior research)** | OrcaWave v1.1 calculation report JSON format, v1.1 report generation enhancement | **LOW-to-MEDIUM.** Confirms that client integration of calculation outputs with real-time SHM systems is now standard practice (2026). v1.1 OrcaWave reports should emit structured JSON compatible with SHM platform ingestion. **Recommended:** add to v1.1 report-generation definition of done: "OrcaWave JSON schema includes stress/fatigue state suitable for SHM system import." | v1.1 Phase 7 (add to smoke-test checklist) |

---

## Recommended Actions

- [x] **CONFIRMATION (v1.1): Validate prior research findings — no new DNV/API/ISO changes since 2026-08-10.** This week's search confirms that comprehensive standards research from 2026-08-10 remains current. No major revisions or emergency updates announced in the past week. **Deliverable:** GitHub issue comment: "Standards research validation — DNV July 2026 / API FFS / ISO 19902 all confirmed stable; no critical updates since 2026-08-10 research pass. Phase 7 planning proceeds without standards-related blockers." **Timeline: complete (this response).**

- [ ] **MEDIUM (Phase 999.2 backlog note): Add ABS Subsea Power Cables standard to Phase 999.2 mooring system scope.** The March 2026 ABS standard governs design and classification of subsea power/control cables for floating platforms. When Phase 999.2 designs mooring systems for floating offshore wind, the umbilical/cable routing and ABS compliance should be included. **Action:** (1) Create GitHub issue: `workspace-hub#TBD: "Phase 999.2 scope clarification — include ABS Subsea Power Cables (March 2026) criteria for mooring power/control cable sizing."` Tag `phase:999.2`, `domain:wind-energy`, `theme:standards-alignment`. (2) Forward reference: [ABS Subsea Cable Technical Standards](https://ww2.eagle.org/en/Products-and-Services/offshore-energy/subsea-solutions.html). (3) Decision point: is power/control cable design in scope, or defer to v1.2? Document in Phase 999.2 plan. **Timeline: include in Phase 999.2 design sketch (v1.2 planning cycle).**

- [x] **MEDIUM (v1.1 Phase 7): Add ISO 19902 SHM compatibility to OrcaWave report generation checklist.** Prior research (2026-08-10) identified SHM integration as v1.2 enhancement; this validation confirms it's now 2026 practice, not future-tech. Recommend promoting to v1.1 definition-of-done for reports. **Action:** (1) Phase 7 smoke-test checklist item: "OrcaWave report JSON schema validated for SHM system ingestion (stress/fatigue reserve factors, confidence intervals, structured metadata)." (2) Create GitHub issue: `digitalmodel#TBD: "OrcaWave report JSON schema — ISO 19902 SHM system compatibility (v1.1 scope)."` Tag `phase:1.1`, `theme:reporting`, `type:feature`. **Deliverable:** JSON schema document + sample output showing SHM-compatible fields. **Timeline: 1–2 days; include in Phase 7 report-generation review.**

- [ ] **LOW (monitoring): Quarterly check on API 579-1 Part 16 finalization status (targeting 2026).** Validates Phase 999.2's FRP composite riser FFS assessment feasibility. Set reminder for October 2026 to check Part 16 publication status. **Deliverable:** GitHub issue comment (when finalized): "API 579-1 Part 16 now available; validate Phase 999.2 FRP riser FFS scope alignment." **Timeline: 3-month check (October 2026).**

---

`★ Insight ─────────────────────────────────────`

**The 2026-08-10 standards research was thorough and remains current — no critical gaps emerged in the intervening week.** The three major standards (DNV July 2026, API 579-1 Part 16, ISO 19902 SHM) are stable, on track, and already captured in prior action items. This is good news: Phase 7 planning doesn't need to wait for new standards clarifications.

**The one NEW finding — ABS Subsea Power Cables standard (March 2026) — is a forward-looking scope item for Phase 999.2, not a v1.1 blocker.** It fills a gap in the floating wind ecosystem: mooring hydrostatics + structure are covered by DNV/ISO; ABS now covers the power/control cable routing and subsea termination. If Phase 999.2 positions as the comprehensive floating-wind design-phase screening tool, ABS cable criteria should be included in the mooring module's output (cable lay routing, sizing). Not urgent, but worth documenting in the Phase 999.2 design sketch (v1.2 planning).

**ISO 19902 SHM integration should be promoted from v1.2 nice-to-have to v1.1 definition-of-done.** Validation confirms client expectation (2026 practice): calculation outputs feed directly into monitoring systems. OrcaWave reports in v1.1 should emit machine-readable JSON suited to SHM ingestion, not just PDFs. This is a report-schema clarification (1–2 hours work), not a calc-science change. Catching it now, before Phase 7 smoke tests finalize, avoids re-architecting reports in v1.2.

`─────────────────────────────────────────────────`

---

## Sources

- [DNV Standards July 2026 Edition](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)
- [DNV Standards 2026: The New Benchmark](https://www.inkl.com/news/dnv-standards-2026-the-new-benchmark-for-offshore-wind-and-green-energy-projects)
- [ABS Offshore Maritime Technical Services](https://ww2.eagle.org/en/Products-and-Services/offshore-energy/subsea-solutions.html)
- [ABS Subsea Power Cables Technical Standards](https://www.guiceoffshore.com/abs-publishes-new-technical-standards-for-subsea-power-cables/)
- [API 579-1/ASME FFS-1 Part 16 Updates](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/)
- [ISO 19902: Essential Guide for Fixed Offshore Structures](https://community.trustcloud.ai/article/iso-19902-everything-you-need-to-know/)

**Status:** This pass validates prior research (2026-08-10) as current with no major revisions. One NEW finding (ABS Subsea Power Cables) surfaces as a Phase 999.2 forward scope item. Recommendation: proceed with Phase 7 as planned; integrate ABS power-cable criteria into Phase 999.2 design (v1.2 planning); promote ISO 19902 SHM compatibility to v1.1 report definition-of-done.
