# Research: engineering-standards — 2026-04-13

## Key Findings

- **DNV 2026 Edition (1 July release) restructures offshore structural standards — new NUI notation for reduced personnel risk, composite floating fish farms, and complete floating offshore wind farm (FOWF) in-service survey overhaul.** The July 2025 edition (effective 1 Jan 2026) introduced 119 documents with structural updates for column-stabilized units (CS-A/B/C platforms), tension-leg platforms (TLP), and deepdraught floating units (DFU) aligned across OS-C103/C105/C106. The planned July 2026 edition (currently in hearing period, 77 documents) adds NUI notation (Normal Use without personnel), new composite/polymer fish farm requirements, and alternative survey methodologies for FOWF assets. This directly impacts digitalmodel's Phase 7 floating vessel analysis scope and future Phase 999.1 (ship/floating platform CAD) domain expansion.

- **API 579-1/ASME FFS-1 Part 16 (FRP composite fitness assessment) nearing publication — three-level assessment framework using Remaining Strength Factor (RSF) and Polymer Damage Status (PDS) for in-service inspection.** The joint ASME/API committee finalized the technical basis using WRC Bulletin 601 (4th edition, May 2023). Three assessment levels: Level 1 (conservative, basic expertise), Level 2 (moderate data precision, improved RSF), Level 3 (expert analysis). This is relevant to Phase 999.2 (Wind Energy, Turbines, FFS Vision) — FRP-wound subsea umbilicals, composite riser components, and corrosion-resistant alloy (CRA) composite hybrid structures now have a standardized FFS methodology. Not yet published (as of April 2026) but expected H1/H2 2026.

- **IEC 61400-1:2019/A1:2026 (wind turbine design amendment) clarifies fatigue assessment (DEL), turbulence treatment (NTM90), and extreme-event modelling (EWM) for improved load calculation accuracy; IEC 61400-3-2:2025 (floating offshore wind turbines) and IEC TS 61400-28:2025 (structural integrity management) establish full floating offshore wind ecosystem.** The A1:2026 amendment improves practical clarity on fatigue methodology alignment between onshore and offshore wind. IEC 61400-3-2:2025 (published Q4 2025) consolidates floating offshore turbine design requirements with self-standing technical content (no longer dependent on IEC 61400-3-1). IEC TS 61400-28:2025 (technical specification, published Q4 2025) addresses wind farm asset structural integrity including aging/fatigue/corrosion management. All three align with Phase 999.2 monopile/jacket foundation analysis and future floating offshore wind (FOWF) expansion.

- **Adaptive cathodic protection system optimization (published 2026) demonstrates 99.1% potential compliance vs. 78.3% conventional systems; reduces energy consumption 22.5%; raises questions on conservative potential assumptions in DNV-RP-B401 and equivalent standards.** Recent CORROSION 2026 research shows machine-learning-based CP optimization can elevate subsea pipeline potential stability by 3.2x under multi-source stray current interference. This challenges long-standing assumptions in DNV-RP-B401 and API RP 65 cathodic protection design — some operators (e.g., Petrobras) have already relaxed CP potential targets based on decades of good performance. This is high relevance to aceengineer's cathodic protection calculator (existing differentiator) — opportunity to implement adaptive CP algorithms and distinguish from commodity CP design tools (SkyCiv, TheNavalArch).

- **DNV-RP-B401 Cathodic Protection Design and emerging HSC-resistant material specifications (2026 development) standardize material selection for subsea service with CP — addresses hydrogen stress cracking risk in high-strength steels.** Standards development bodies are formalizing material selection criteria to prevent hydrogen embrittlement in subsea cathodic protection environments. This is directly relevant to Phase 1 wall thickness module (ASME B31.4-2025 already includes low-temperature materials) and Phase 999.2 FFS domain expansion — CP potential affects material selection, and standards are maturing to include this interaction explicitly.

## Relevance to Project

| Finding | Affected Package / Workflow | Impact |
|---|---|---|
| **DNV 2026 Edition (OS-C103/105/106 restructure + NUI notation + FOWF survey overhaul)** | `digitalmodel` Phase 7 (vessel hull analysis), Phase 999.1 (ship/platform CAD), Phase 999.2 (floating offshore wind) | DNV-OS-C103 restructuring for column-stabilized units affects existing TLP/CS analysis modules. New NUI notation enables lower-cost personnel-free design scenarios (drilling/production automation). FOWF alternative survey methodology affects inspection scheduling and cost drivers. **Action:** Audit digitalmodel's floating vessel module against DNV 2026 edition (effective July 2026); incorporate NUI notation decision tree into OrcaWave analysis workflow (Phase 7 reports); document FOWF survey implications for Phase 999.2. |
| **API 579-1 Part 16 (FRP fitness assessment, Level 1/2/3, RSF/PDS framework)** | `digitalmodel` Phase 999.2 (Wind Energy, Turbines, FFS Vision) | FRP composite riser components, umbilicals, and hybrid CRA-composite structures now have standardized FFS assessment framework (expected publication H1/H2 2026). digitalmodel's existing wall thickness/fatigue modules provide foundation; FRP fitness assessment extends domain to **new materials class**. **Action:** When Part 16 publishes, audit technical requirements, map RSF calculation to existing digitalmodel framework, add Level 1/2/3 assessment modules to Phase 999.2 backlog. |
| **IEC 61400-1:2019/A1:2026 + IEC 61400-3-2:2025 + IEC TS 61400-28:2025** | `digitalmodel` Phase 999.2 (monopile/jacket foundation, FOWF), Phase 999.4+ (structural integrity management automation) | IEC standards now provide complete technical ecosystem for wind turbine structural design (onshore) and floating offshore wind (FOWF). DEL/NTM90/EWM guidance harmonizes with DNV-ST-0126. IEC TS 61400-28:2025 opens future domain: **wind farm asset aging/fatigue/corrosion management**. **Action:** Document IEC 61400-1:A1:2026 + IEC 61400-3-2:2025 alignment with DNV-ST-0126 in Phase 999.2 design inputs; flag IEC TS 61400-28:2025 as prerequisite for Phase 999.7+ (structural integrity management automation). |
| **Adaptive cathodic protection optimization (99.1% potential compliance, 22.5% energy reduction)**  | `digitalmodel` cathodic protection calculator (existing competitive differentiator) | Research demonstrates conventional DNV-RP-B401 design philosophy (conservative potential targets) is optimizable via ML-driven adaptive control. aceengineer's CP calculator can differentiate from commodity tools by implementing adaptive optimization algorithms. Petrobras case study (relaxed potentials, good performance) validates relaxation rationale. **Action:** Create GitHub issue — "Upgrade CP calculator with adaptive optimization model; cite CORROSION 2026 research + Petrobras case study; measure energy savings differential vs. SkyCiv baseline." High competitive differentiation opportunity. |
| **HSC-resistant material selection standards (2026 development)** | `digitalmodel` wall thickness module (Phase 1), Phase 999.2 FFS, cathodic protection interaction | CP potential selection affects high-strength steel (HSC) embrittlement risk — standards are formalizing this coupling. ASME B31.4-2025 low-temperature materials + emerging HSC/CP interaction guidance + API 579-1 FFS assessment create **complete material selection framework**. **Action:** Audit digitalmodel wall thickness module inputs (material grade selection, CP potential interaction); document material-CP coupling in calculation reports (Phase 1.1 calculation report template refinement); flag HSC/CP interaction check in Phase 7 smoke tests. |

## Recommended Actions

- [ ] **Create GitHub issue** — `digitalmodel` Phase 7 (OrcaWave Automation): Audit floating vessel module compatibility with DNV 2026 Edition (OS-C103/105/106 restructure). Verify existing TLP/CS-A/B/C analysis logic against 2026 requirements. Incorporate new NUI notation (personnel-free design) as optional analysis scenario. Document DNV 2026 Edition applicability in Phase 7 calculation reports (effective 1 July 2026).

- [ ] **Create GitHub issue** — `digitalmodel` Phase 999.2 (Wind Energy, Turbines, FFS): When API 579-1 Part 16 publishes (expected H1/H2 2026), audit technical requirements for FRP composite equipment fitness assessment. Design RSF/PDS calculation modules. Add Level 1/2/3 assessment framework to Phase 999.2 implementation roadmap (FRP riser, umbilical, hybrid CRA-composite structures).

- [ ] **Create GitHub issue** — `digitalmodel` Phase 999.2: Confirm IEC 61400-1:2019/A1:2026, IEC 61400-3-2:2025, IEC TS 61400-28:2025 alignment with DNV-ST-0126 in monopile/jacket design input specifications. Document harmonized DEL/NTM90/EWM load calculation methodology. Flag IEC TS 61400-28:2025 (structural integrity management) as prerequisite for future Phase 999.7+ automation.

- [ ] **Promote to PROJECT.md** — Add under Engineering Domains: "DNV 2026 Edition (effective 1 July 2026) restructures offshore structural standards. NUI notation enables personnel-free design scenarios. FOWF alternative survey methodology affects cost/schedule. IEC 61400 2025–2026 amendments establish complete wind turbine structural ecosystem (onshore + floating offshore). API 579-1 Part 16 (expected H1/H2 2026) standardizes FRP composite fitness assessment."

- [ ] **Create GitHub issue** — `digitalmodel` cathodic protection calculator: Implement adaptive optimization model for anodic current distribution (machine-learning or constraint-based). Benchmark against DNV-RP-B401 conventional design philosophy. Cite CORROSION 2026 adaptive CP research (99.1% potential compliance, 22.5% energy savings) + Petrobras field validation in calculator output. Position as **aceengineer competitive differentiator** vs. SkyCiv/TheNavalArch commodity CP tools.

- [ ] **Create GitHub issue** — `digitalmodel` wall thickness module + Phase 7 smoke tests: Add HSC/CP material selection interaction check. Verify material-CP potential coupling logic against emerging 2026 standards development guidance. Document material HSC risk in Phase 1.1 calculation reports. Gate Phase 7 smoke tests with material-potential validation checks.

- [ ] **Ignore (low priority)** — ISO 13628 subsea production systems: no 2026 updates identified (standards remain 2005–2006 editions). Track DNV-OS-E402 (subsea production systems) in July 2026 edition release for updated requirements.

---

## Cross-Domain Connections

**Standards Currency as Competitive Differentiator** (synthesized with 2026-04-10 market research):

The confluence of three forces creates **aceengineer opportunity window (H1/H2 2026)**:

1. **DNV 2026 Edition, IEC 2026 amendments, API 579-1 Part 16 publication** — all three major standard updates land in H1/H2 2026. Competitors (SkyCiv, TheNavalArch, SACS cloud) update on 12-18 month lag; aceengineer can achieve standards currency within 30–60 days of publication.

2. **Market consolidation + margin pressure** (from 2026-04-10 research) — free/low-cost calculators commoditize generic wall thickness/stability. **Standards traceability becomes primary differentiator.** aceengineer's unique value: every calculation traces to current DNV/API/IEC reference with publication date + version clarity.

3. **Adaptive CP optimization** (2026 CORROSION research) + **HSC/CP material coupling** (2026 standards development) + **FRP fitness assessment** (API 579-1 Part 16) = three **specialized domain opportunities** that commodity tools cannot address without custom development.

**Strategic implication:** Phase 7 (OrcaWave solver verification) shipping with DNV 2026 Edition compliance + Phase 1.1 calculation reports citing current standards (DNV-RP-C203:2024, ASME B31.4-2025, IEC 61400-1:A1:2026) + CP calculator with adaptive optimization positions aceengineer as **"standards-current by default"** against competitors. This justifies consultation-based pricing model vs. low-cost alternatives.

---

Sources:
- [DNV July 2025 Edition Release — News](https://www.dnv.com/news/2025/now-available-july-2025-edition-of-dnv-class-rules-and-documents-for-ship-and-offshore/)
- [DNV 2026 Edition — Hearing Period Announcement](https://www.dnv.com/news/2026/dnv-rules-2026-hearing-period-now-open/)
- [DNV Standards and Rules](https://www.dnv.com/rules-standards/)
- [DNV-RP-C203 Fatigue Design of Offshore Steel Structures](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/)
- [DNV-ST-0126 Support Structures for Wind Turbines](https://www.dnv.com/energy/standards-guidelines/dnv-st-0126-support-structures-for-wind-turbines/)
- [API 579-1/ASME FFS-1 Part 16 — FRP Composite Fitness Assessment Overview](https://utcomp.com/category/api-579-1-asme-ffs-1-update/)
- [WRC Bulletin 601 Fourth Edition — Foundation for FRP FFS Standard](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/)
- [IEC 61400-1:2019/A1:2026 Wind Turbine Design Amendment](https://www.standards.iteh.ai/catalog/standards/clc/8007ffa4-bb0c-4cbd-b306-74394bbf66b1/en-iec-61400-1-2019-a1-2026)
- [IEC 61400-3-2:2025 Floating Offshore Wind Turbine Design Requirements](https://webstore.ansi.org/standards/iec/IEC61400Ed2025)
- [IEC TS 61400-28:2025 Wind Energy Structural Integrity Management](https://webstore.iec.ch/en/publication/62236)
- [IEC 61400 Wind Turbine Standards Overview](https://www.datamission.co.uk/iec-61400/)
- [Adaptive Cathodic Protection System Optimization for Submarine Pipelines — CORROSION 2026](https://content.ampp.org/corrosion/article-abstract/doi/10.5006/4912/108003/Adaptive-Cathodic-Protection-System-Optimization)
- [Cathodic Protection of Offshore Structures — ABS Guidance Notes](https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/offshore/306-cathodicprotection-offshore-structures/cathodic-protection-offshore-gn-dec18.pdf)
- [DNV-RP-B401 Cathodic Protection Design](https://www.dnv.com/energy/standards-guidelines/dnv-rp-b401-cathodic-protection-design/)
- [DNV-RP-C205 Environmental Conditions and Environmental Loads](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c205-environmental-conditions-and-environmental-loads/)
- [Commentary on HSC-Resistant Materials in Subsea Service with Cathodic Protection — AMPP Standards](https://content.ampp.org/standards/book/70/Commentary-on-Standards-Development-for-Selection)
