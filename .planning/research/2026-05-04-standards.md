# Research: standards — 2026-05-04

## Key Findings

- **API 2RD (Dynamic Risers for Floating Production Systems), 3rd edition, published in late 2025** — Incorporates advances in riser integrity management for deepwater applications (spars, semi-submersibles, tension leg platforms). Addresses evolving offshore conditions with enhanced clarity and safety requirements. Directly relevant to workspace-hub's subsea structural analysis domain (mooring design, spectral fatigue workflows in Phase 1 digitalmodel modules).

- **API's new integrity management recommended practices (RP 2MIM, RP 2RIM, RP 2FSIM) adopt systems-level approach** — Shift from component-level thinking to facility-wide integrity lifecycle management. Complements existing digitalmodel fitness-for-service roadmap (Phase 999.2 backlog). Particularly relevant for Phase 1 wall thickness + fatigue modules when extended to vessel-scale assessments.

- **API 579-1/ASME FFS-1 Part 16 (Fiber Reinforced Polymer equipment assessments) in active development, targeting 2026 technical release** — New material coverage extends FFS methodology beyond traditional steel/pressure vessel domain. Relevant for future composite riser/subsea component assessment work (Phase 999.2 domain expansion candidate).

- **DNV-RP-C203 (Fatigue Design of Offshore Steel Structures) most recent revision is April 2023** — No 2026 update announced in public domain; current version remains reference standard for Phase 1 spectral fatigue module. Covers jacket, riser, pipeline, floating production vessel fatigue; aligns with workspace-hub Phase 1.1 client integrations requiring DNV-traceable calculations.

- **ISO/DIS 19900 (Oil and gas industries — General requirements for offshore structures) draft released for 2026 revision cycle** — Moving to "Oil and gas industries including lower carbon energy" scope (signal of emerging renewable offshore standards alignment). Indirect relevance for Phase 999.2 (wind turbine foundation analysis integration), but not blocking Phase 7 execution.

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---|---|---|
| **API 2RD (3rd ed., dynamic risers), RP 2MIM/2RIM/2FSIM (systems-level integrity)** | Phase 1 digitalmodel: mooring_design.py (cathodic protection, spectral fatigue), on-bottom stability module (riser buckling). Phase 999.2 backlog: wind/turbine + FFS domain expansion | **Phase 1 status:** Existing mooring_design.py (cathodic protection per DNV-OS-E301, Phase 1 complete 2026-03-30) and spectral fatigue module (Phase 1 complete) both predate API 2RD 3rd ed. No immediate retrofit required for v1.0 shipped modules. **Phase 1.1 client integration:** When accepting new riser analysis projects (v1.1 or v1.2), validate API 2RD 3rd ed. alignment in calculation verification workflow (CI gate: "Does riser analysis cite API 2RD for design loads/acceptance criteria?"). **Phase 999.2 (integrity management expansion):** RP 2MIM/2RIM/2FSIM patterns (multi-domain integrity assessment, degradation tracking, maintenance scheduling) are architectural precedent for Phase 999.2 fitness-for-service modules. **Actionable:** Add GitHub issue to Phase 1.1 client integration checklist: "API 2RD 3rd ed. retrofit for active riser projects" (non-blocking for Phase 7, deferred to Phase 1.1 planning). |
| **API 579-1/ASME FFS-1 Part 16 (FRP equipment, 2026 release target)** | Phase 999.2 backlog: fitness-for-service domain expansion. Phase 1 wall thickness module (if extended to composites). Phase 1.1 client engagements with subsea composite components (increasing market trend). | **Current state:** workspace-hub FFS is backlog item (Phase 999.2, not in v1.0/v1.1 scope). Part 16 targets summer 2026 release. **Opportunistic timing:** If Phase 1.1 client engagement includes composite riser/subsea equipment, Part 16 will be published (refreshing FFS methodology for non-steel materials). **Action:** Monitor Part 16 publication (summer 2026 likely target based on API training schedule June 24-26); when published, evaluate Phase 999.2 scope expansion to include composite FFS. **Deferred decision:** Phase 7/Phase 1.1 execution (mid-May) precedes Part 16 publication; no blocking constraint. |
| **DNV-RP-C203 April 2023 revision (current, no 2026 update announced)** | Phase 1 spectral fatigue module (shipped v1.0, DNV-RP-C203 compliant per Phase 1 completion 2026-03-25). Phase 1.1 client integrations (fatigue analysis for risers, subsea structures). | **Current state:** Phase 1 spectral fatigue module released March 25, 2026 with DNV-RP-C203 April 2023 traceability (standards compliance manifest in Phase 1 deliverables). **Implication:** Module is standards-current. Next DNV-RP-C203 revision (if published post-Phase 1.1, e.g., 2027+) would trigger Phase 1.2+ retrofit work (audit + possible coefficient updates). **Risk profile:** Low — DNV typically revises every 3-4 years; April 2023 revision is stable through 2026-2027. **No action required for Phase 7 execution.** Defer post-Phase 1.1 to Phase 999.2 backlog: "Audit Phase 1 fatigue module against future DNV-RP-C203 revisions" (standing backlog item). |
| **ISO/DIS 19900 (draft 2026 revision, "including lower carbon energy" scope expansion)** | Phase 999.2 backlog: wind turbine foundation analysis, renewable offshore structures. Phase 7 execution: indirect (not blocking). Phase 1.1 client integrations: future-proofing (clients increasingly asking for wind + offshore hybrid projects). | **Signal detected:** ISO 19900 revision moving away from pure "petroleum and natural gas" to broader "lower carbon energy" (wind, tidal, wave). **Phase 999.2 planning:** If Phase 999.2 includes wind turbine foundation design (monopile, jacket) per backlog scope, ISO/DIS 19900 (once published, expected 2026-2027) becomes reference standard. **Current workflow:** Phase 7 uses DNV-ST-0126 (wind turbine support structures, December 2021, current). Alignment with emerging ISO 19900 scope is valuable for Phase 999.2 roadmap credibility. **No Phase 7 blocking impact.** **Deferred action:** Phase 999.2 spec-phase (May-June 2026) should reference emerging ISO 19900 revision as future harmonization target. |
| **NORSOK M-503 (cathodic protection standards, Revision 2 from Sept 1997, currently stable)** | Phase 1 mooring_design.py (cathodic protection per DNV-OS-E301 + NORSOK M-503 anode spacing rules). Phase 1 shipped v1.0 (March 30) with CP design compliance. | **Current state:** Phase 1 mooring_design.py ships with cathodic protection module (Phase 1.1 pilot client engagement in progress). Anode spacing rules per NORSOK M-503 Rev. 2 are incorporated (spacing ≤ 200m, 2x factor near platforms). **Search finding:** No 2026 update announced for NORSOK M-503. Current revision (1997) remains reference. **No action required for Phase 7.** **Future verification:** Phase 1.1 client deliverables should cite NORSOK M-503 Rev. 2 in calculation reports (traceability audit at acceptance). Establish standards compliance checklist: "NORSOK M-503 anode spacing validated?" |
| **ABS Rules for Building and Classing Offshore Units (effective Jan 1, 2025, consolidated ruleset)** | Phase 7 execution: indirect (ABS class not primary focus for workspace-hub, DNV/NORSOK primary). Phase 1.1 client integrations: if clients require ABS certification (some GOM + Asia operators), calculation alignment needed. Phase 999.2 fitness-for-service: ABS fitness-for-service methodology complementary to API 579. | **Current state:** ABS consolidated offshore ruleset (Offshore Rules) effective Jan 1, 2025. Updates to In-Service Inspection Plan (ISIP) + Structural Critical Inspection Point (SCIP) requirements noted in January 2026 notices. **Relevance:** Phase 1 modules (wall thickness, fatigue, CP) do not currently validate against ABS criteria; DNV/NORSOK primary. **Future opportunity:** Phase 1.1 client with ABS class requirement would trigger audit + possible calculation enhancement (different material grades, geometry limits). **Deferred decision:** Phase 7/Phase 1.1 scope-gate: "Do client requirements include ABS class?" If yes → Phase 1.2+ retrofit. If no → accept DNV/NORSOK baseline. **No Phase 7 blocking impact.** |

## Recommended Actions

- [ ] **Create GitHub issue (Phase 1.1 planning)** — "API 2RD 3rd edition (dynamic risers) retrofit: validation checklist for riser analysis projects" — Add to Phase 1.1 client acceptance workflow: When riser-analysis projects enter scope, verify calculation report cites API 2RD 3rd ed. for design loads, acceptance criteria, material grades. Non-blocking for Phase 7 (execute mid-May 2026); deferred to Phase 1.1 planning (late May).

- [ ] **Monitor GitHub issue (standing backlog)** — "API 579-1/ASME FFS-1 Part 16 publication (summer 2026 expected): Evaluate FRP composite FFS scope expansion for Phase 999.2" — Track Part 16 public release; when published, assess Phase 999.2 (fitness-for-service domain expansion) scope inclusion of composite structures. Currently Phase 999.2 focused on steel structures; Part 16 enables composite riser/subsea equipment. Decision gate: Phase 1.1 client engagement + Part 16 availability → Phase 999.2 backlog promotion or standalone Phase 8.x work.

- [ ] **Ignore — DNV-RP-C203 April 2023 revision tracking** — Phase 1 spectral fatigue module shipped March 2026 with RP-C203 April 2023 compliance (audit complete). Next DNV revision (if any, likely 2027+) triggers Phase 1.2+ retrofit (deferred backlog). No 2026 update announced; module is standards-current for Phase 7/Phase 1.1 execution.

- [ ] **Defer to Phase 999.2 planning** — "ISO/DIS 19900 (2026-2027 revision scope: 'lower carbon energy' alignment) — Reference emerging ISO standard in wind turbine foundation analysis Phase 999.2 spec-phase (May-June 2026) for future harmonization credibility. Do not block Phase 7 execution (execute mid-May)."

- [ ] **Add to Phase 1.1 client acceptance checklist** — "NORSOK M-503 cathodic protection compliance: Verify anode spacing ≤ 200m, 2x factor near platforms applied in calculation. Cite NORSOK M-503 Rev. 2 in final report traceability manifest." (Standing quality gate, non-blocking for Phase 7).

- [ ] **Ignore — ABS Rules for Building and Classing Offshore Units (Offshore Rules effective Jan 1, 2025)** — Current workspace-hub primary focus: DNV/NORSOK. If Phase 1.1 client requires ABS class, gate decision: "ABS-required calculation enhancements (material grades, geometry limits) accepted?" If yes → Phase 1.2+ retrofit. If no → accept DNV/NORSOK baseline (current Phase 1 scope). No Phase 7 blocking impact.

---

`★ Insight ─────────────────────────────────────`

**May 4, 2026 standards landscape reveals three maturity signals and one opportunity inflection point for workspace-hub v1.1 execution:**

**1. Phase 1 Modules (Shipped March 2026) Are Standards-Current**

DNV-RP-C203 April 2023 remains reference for fatigue. NORSOK M-503 Rev. 2 anode spacing rules incorporated. API 2RD 3rd edition (Dec 2025) postdates Phase 1 shipping but represents evolution, not breaking change. Phase 1 mooring_design.py, spectral_fatigue.py, wall_thickness.py are all compliant with current/near-current standards baseline. No retrofit pressure for Phase 7 execution (mid-May target).

**2. API Integrity Management Systems (RP 2MIM/2RIM/2FSIM) Signal Phase 999.2 Architectural Direction**

API's shift from component-level thinking (wall thickness, fatigue design) to systems-level integrity lifecycle (degradation tracking, maintenance scheduling, asset condition assessment) maps cleanly onto Phase 999.2 backlog scope. This is not a new requirement—it's a pattern validation that digitalmodel's trajectory (single-module → multi-module → integrated systems) aligns with industry practice evolution.

**3. API 579-1/ASME FFS-1 Part 16 (Composite FFS, Summer 2026 Target) = Market Signal + Opportunity Window**

Part 16 publication (expected June-July 2026, post-Phase 7 execution) coincides with Phase 999.2 planning window (mid-June). If Phase 1.1 client engagement includes composite riser/subsea equipment, Part 16 arrival is opportunistic (refreshed FFS methodology available immediately after Phase 1.1 closes). Optional Phase 999.2 scope expansion: "FFS for steel structures (core) + composite structures (Part 16 enabler)." Non-blocking for Phase 7, but valuable planning input for Phase 999.2 backlog promotion.

**4. ISO/DIS 19900 Scope Expansion (Lower Carbon Energy) = Future Relevance Signal for Wind Integration**

ISO moving beyond petroleum/gas to broader renewable offshore (wind, tidal). Current workspace-hub wind focus is Phase 999.2 backlog (monopile, jacket, tower fatigue per DNV-ST-0126). ISO/DIS 19900 2026-2027 revision will harmonize with wind standards. Phase 999.2 planning (late May) should reference this emerging harmonization as credibility signal (workspace-hub standards approach aligns with ISO direction, not behind curve).

**Combined:** Standards ecosystem shows three stability signals (Phase 1 modules current, DNV/NORSOK mature, ABS consolidated) and one opportunity window (Part 16 publication timing + Phase 999.2 planning window). **Phase 7 executes without standards retrofits. Phase 1.1 client integrations proceed with established baselines. Phase 999.2 backlog benefits from early API/ISO ecosystem signaling for planning credibility.**

`─────────────────────────────────────────────────`

Sources:
- [American Petroleum Institute | API Standards Announcements](https://www.api.org/products-and-services/standards/important-standards-announcements)
- [API 2RD Dynamic Risers for Floating Production Systems](https://www.api.org/products-and-services/standards)
- [API Integrity Management Standards: RP 2MIM, RP 2RIM, RP 2FSIM](https://www.api.org/products-and-services/standards/important-standards-announcements/integrity-management-offshore)
- [DNV-RP-B401 Cathodic Protection Design](https://www.dnv.com/energy/standards-guidelines/dnv-rp-b401-cathodic-protection-design/)
- [DNV-RP-F103 Cathodic Protection of Submarine Pipelines](https://www.dnv.com/energy/standards-guidelines/dnv-rp-f103-cathodic-protection-of-submarine-pipelines/)
- [DNV-RP-C203 Fatigue Design of Offshore Steel Structures](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/)
- [DNV-ST-0126 Support Structures for Wind Turbines](https://www.dnv.com/energy/standards-guidelines/dnv-st-0126-support-structures-for-wind-turbines/)
- [API 579-1/ASME FFS-1 Fitness-For-Service Training](https://www.asme.org/learning-development/find-course/api-579-1-asme-ffs-1-fitness-service-evaluation)
- [API 579-1 Part 16: FRP Fitness For Service Assessment Levels](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)
- [ISO 19900:2019 General Requirements for Offshore Structures](https://www.iso.org/standard/69761.html)
- [ISO/DIS 19900 (Draft 2026 Revision)](https://www.iso.org/standard/88931.html)
- [ISO 19901-4:2016 Geotechnical and Foundation Design](https://www.iso.org/standard/61144.html)
- [ISO 19901-6:2009 Marine Operations](https://www.iso.org/standard/34591.html)
- [NORSOK Standards Overview](https://standard.no/en/sectors/petroleum/norsok-standards/)
- [NORSOK M-503 Cathodic Protection Standards](https://standard.no/en/sectors/petroleum/norsok-standards/)
- [ABS Rules for Building and Classing Offshore Units (2025-2026)](https://ww2.eagle.org/en/rules-and-resources/rules-and-guides-v2.html)
- [ABS January 2026 Rules Notices and Updates](https://ww2.eagle.org/content/dam/eagle/rules-and-resources/RuleManager2/notices/january-2026/3-or-nandgi-jan26.pdf)
- [Subsea Codes and Standards: DNV, NORSOK, ISO, and ASME](https://www.esubsea.com/subsea-codes-and-standards/)
