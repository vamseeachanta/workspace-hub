# Research: standards — 2026-09-14

## Key Findings

1. **DNV-RP-F123 Offshore Hydrogen Pipelines published March 2026 — new recommended practice for safe design, operation, and requalification of offshore hydrogen pipeline infrastructure, developed through H2Pipe joint industry project (JIP, 2021–2026).** Addresses hydrogen-specific integrity risks including hydrogen embrittlement. Supplements DNV-ST-F101 (submarine pipeline standard, now 50 years in service). → [DNV hydrogen pipeline recommended practice](https://www.dnv.com/news/2026/new-dnv-recommended-practice-supports-offshore-hydrogen-pipelines-development/)

2. **ISO 25249 Corrosion Protection of Offshore Wind Structures — multi-part standard in development (Committee Draft), addresses paint systems, cathodic protection, corrosion environment assessments, maintenance strategies, and total service life.** Parts 1–5 cover design, thermal spraying/painting, foundations, towers, nacelles; additional parts planned for secondary steel and composites. Significant for subsea cable/riser cathodic protection methodology alignment. → [ISO 25249 Multi-Part Structure](https://www.iso.org/standard/89568.html) | [Corrosion Protection of Offshore Wind Development](https://www.icorr.org/new-iso-standards-on-corrosion-protection-of-offshore-wind-to-be-developed/)

3. **ABS Consolidated Offshore Rules (effective January 1, 2026) — modernized rule consolidation with new format, enhanced graphics, and expanded search. Floating Production Installation (FPI) Rules withdrawn; all floating-platform requirements now under unified Offshore Rules.** Simplifies navigation of ABS requirements for design and classification of offshore structures. → [ABS Offshore Rules Update](https://pressreleases.eagle.org/news/abs-releases-industry-leading-update-to-offshore-rules)

4. **API 579-1/ASME FFS-1 Part 16 (FRP Fitness-For-Service) in active development for composite structures — extends 4th Edition (Dec 2021) baseline to include fiber-reinforced polymer equipment assessment.** Currently only Parts 1–15 (metallic structures) are normative. Part 16 expected Q4 2026, relevant for Phase 999.2 mooring-chain scope clarification (determines boundary between metallic and composite FFS assessment). → [API 579 Part 16 FRP Assessment Levels](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/) | [FFS Fitness-For-Service Evaluation](https://www.asnt.org/me/26/3/api-579-asme-ffs-1-fitness-for-service-evaluation)

5. **ISO 19901-1:2026 Metocean Design and Operating Considerations — current baseline for offshore structural metocean design requirements (wind, wave, current, extreme conditions, long-term statistical distributions).** Used in conjunction with ISO 19902 (fixed steel structures) and ISO 19905-1 (site-specific jack-up assessment). Directly applicable to v1.1 OrcaWave hydrodynamic design-basis documentation. → [ISO 19901-1:2026](https://www.iso.org/standard/19901-1)

## Relevance to Project

| Finding | Affected Workflow | Impact | Notes |
|---------|---|---|---|
| **DNV-RP-F123 Hydrogen Pipelines (March 2026)** | v1.1 scope definition (hydrogen-transport vessels?), Phase 999.2 fitness-for-service (hydrogen-service risers/mooring?), material selection | **MEDIUM.** Signals DNV's expanded scope beyond traditional oil/gas to energy transition (hydrogen networks). If v1.1 examples or client scope includes hydrogen-service subsea infrastructure, DNV-RP-F123 becomes normative. Currently unknown in v1.1 design-basis. Recommend: confirm client scope; if hydrogen is in scope, add DNV-RP-F123 to normative stack with hydrogen-embrittlement assessment requirements. | Scope clarification needed; flag as optional depending on client sector. |
| **ISO 25249 Offshore Wind Corrosion Protection (multi-part, CD stage)** | v1.1 + Phase 7 (if offshore wind clients), cathodic protection design baseline | **MEDIUM.** ISO 25249 is in Committee Draft; not yet normative but signals industry direction for comprehensive corrosion protection frameworks (paint + cathodic + lifecycle). If v1.1 clients include floating offshore wind (FOW) or subsea cable protection scopes, ISO 25249 alignment strengthens positioning. Current API/DNV cathodic protection guidance remains authoritative until ISO 25249 publishes. Recommend: monitor for publication date (expected late 2026/early 2027); preview CD if available to assess compatibility with v1.1 design-basis. | Monitor for publication; defer normative adoption until Final International Standard. |
| **ABS Consolidated Offshore Rules (Jan 2026)** | v1.1 ABS-classed vessel analysis, Phase 7 solver verification (if ABS client examples) | **LOW-MEDIUM.** ABS rules consolidation simplifies navigation but does not change fundamental structural-analysis methodology. If v1.1 examples include ABS-classed floating platforms (MOUs, FSOs, FPSOs), the January 2026 consolidated rules are the current baseline. No breaking changes; primarily format/accessibility improvement. Recommend: confirm v1.1 client platform types; if ABS scope exists, note in design-basis: "ABS Offshore Rules (consolidated January 2026) per [relevant section]." | Standard update, not methodology change; note in design-basis if applicable. |
| **API 579 Part 16 FRP (Q4 2026 expected)** | Phase 999.2 fitness-for-service scope boundary (metallic vs. composite) | **MEDIUM.** Clarifies that current API 579-1/ASME FFS-1 (Parts 1–15, Dec 2021 Edition) addresses metallic structures only. Phase 999.2 backlog mentions FFS as a potential domain; Part 16 publication will determine whether composite risers/mooring are in scope (deferred to v2.0 of FFS module) or out-of-scope (focus v1.0 on metallic per current API 579). Recommend: Phase 999.2 scope sketch should note: "FFS v1.0 targets metallic subsea structures per API 579-1/ASME FFS-1 Parts 1–15 (Dec 2021). FRP structures (Part 16, expected Q4 2026) deferred to v2.0 pending publication." | Scope decision needed for Phase 999.2; defer composite FFS to v2.0. |
| **ISO 19901-1:2026 Metocean Design** | v1.1 OrcaWave hydrodynamic design-basis (normative reference) | **HIGH.** ISO 19901-1:2026 is current for metocean identification and characterization (wind, wave, current, extreme/abnormal conditions, long-term distributions). v1.1 should cite this as normative baseline alongside OrcaWave solver validation. Directly applicable to design-basis section: "Metocean conditions per ISO 19901-1:2026; hydrodynamic analysis per OrcaWave solver (validated <1% vs. WAMIT benchmark, 2025)." | Include in v1.1 normative stack (already confirmed in prior research). |

## Recommended Actions

- [ ] **MEDIUM (v1.1 scope clarification): Confirm whether v1.1 client scope includes hydrogen-transport subsea infrastructure — if yes, add DNV-RP-F123 to normative stack with hydrogen-embrittlement assessment requirements.** DNV-RP-F123 Offshore Hydrogen Pipelines (published March 2026) addresses hydrogen-specific integrity risks including embrittlement. If any v1.1 examples or client projects involve hydrogen-service risers, pipelines, or subsea infrastructure, DNV-RP-F123 becomes mandatory normative reference alongside DNV-ST-F101. **Action:** (1) v1.1 design document: client scope section — clarify whether hydrogen is a candidate application. (2) If yes: add to normative stack: "DNV-RP-F123 Offshore Hydrogen Pipelines (2026) for hydrogen-service subsea infrastructure; hydrogen embrittlement per DNV-RP-F123 §3.2." (3) If no: note exclusion: "Hydrogen-transport applications are out of scope for v1.1 (current scope: conventional oil/gas, renewable energy subsea support). Hydrogen infrastructure assessment (DNV-RP-F123) deferred to v1.2 or Phase 999.x." (4) Rationale: hydrogen-service design constraints differ from conventional; early scope clarity prevents mid-project constraint surprises. **Timeline: 30 minutes.** → [DNV-RP-F123 Hydrogen Pipelines](https://www.dnv.com/news/2026/new-dnv-recommended-practice-supports-offshore-hydrogen-pipelines-development/)

- [ ] **MEDIUM (monitoring task): Track ISO 25249 publication status through late 2026 — multi-part corrosion-protection standard currently in Committee Draft, expected completion late 2026/early 2027.** If v1.1 clients include offshore wind or subsea cable scopes, ISO 25249 (especially Parts 1, 3, 5 for design, foundations, nacelles) will align with v1.1 cathodic protection methodology. **Action:** (1) Set calendar reminder: "ISO 25249 publication check — December 1, 2026." (2) On that date: search ISO website for published ISO 25249:2026 or :2027. (3) If published: assess relevance to v1.1 client scope (offshore wind, cable protection). If relevant: add provisional note to v1.1 design-basis: "Corrosion protection per ISO 25249 (2027) pending publication; interim baseline: API RP 2A, DNV-RP-B401 cathodic protection." (4) If not yet published: defer to v1.1.1 or later refresh. (5) Rationale: ISO 25249 represents industry consensus on comprehensive service-life-aware corrosion strategies; early awareness enables smooth transition when published. **Timeline: Quarterly monitoring (next check: 2026-12-01).** → [ISO 25249 Development Status](https://www.iso.org/standard/89568.html)

- [ ] **LOW-MEDIUM (Phase 999.2 scope sketch): Document fitness-for-service module scope boundary — FFS v1.0 targets metallic subsea structures per API 579-1/ASME FFS-1 Parts 1–15 (Dec 2021); FRP structures (Part 16, expected Q4 2026) deferred to v2.0.** Phase 999.2 has been flagged for six consecutive weeks in research reports without a scope sketch. API 579 Part 16 publication will finalize the boundary. **Action:** (1) Create GitHub issue: `workspace-hub#TBD: "Phase 999.2 Fitness-For-Service scope sketch — metallic subsea structures (API 579-1/ASME FFS-1 Parts 1–15) v1.0; FRP composites (Part 16) v2.0."` Tag `phase:999.2`, `domain:standards`. (2) Issue body: fitness-for-service module scope, normative stack (API 579, BS 7910, DNV-RP-F101), and boundary with Phase 999.3 CAD/CAM pipeline. (3) Link to [#2695 goal-invocation catalog](https://github.com/vamseeachanta/workspace-hub/issues/2695) for routing. (4) Rationale: six-week research carryover without resolution; formal issue pins the decision. **Timeline: 1 hour.** → [API 579-1/ASME FFS-1 Part 16 Development](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/)

- [x] **CONFIRMATION (v1.1 normative stack): ISO 19901-1:2026 Metocean Design + OrcaWave solver validation citation remain current baseline through September 2026.** Both are confirmed by this week's search; recommend promoting to PROJECT.md v1.1 design-basis section alongside DNV July 2026 class edition and EU MED 2026/1434 (conditional on client scope). **Deliverable:** GitHub issue comment (when Phase 7 or v1.1 issue filed): "Standards research 2026-09-14 confirms ISO 19901-1:2026 + OrcaWave <1% WAMIT validation as current v1.1 normative baseline. NEW findings: DNV-RP-F123 hydrogen pipelines (scope-dependent), ISO 25249 corrosion multi-part (monitor for publication late 2026/early 2027), ABS Offshore Rules consolidated (Jan 2026, accessibility improvement only), API 579 Part 16 FRP (expected Q4 2026, scope boundary clarification for Phase 999.2). No blocking changes to v1.1 or Phase 7."

---

`★ Insight ─────────────────────────────────────`

**This week's standards research adds five concrete, traceable findings across four regulatory/standards bodies (DNV, ISO, ABS, API) — all additive and non-disruptive to prior v1.0 and v1.1 work.**

The core pattern: **the substrate standards ecosystem is consolidating and clarifying scope boundaries, not shifting methodologies.**

1. **DNV-RP-F123 (hydrogen pipelines)** signals industry sector expansion (energy transition) but does NOT change OrcaWave solver methodology for conventional oil/gas or renewables infrastructure — scope-dependent decision only.

2. **ISO 25249 (offshore wind corrosion)** is an emerging framework for lifecycle-aware corrosion strategies, currently in draft. Once published, it aligns with existing cathodic-protection guidance but adds service-life optimization layer. Not blocking v1.1; monitoring-track only.

3. **ABS rule consolidation (Jan 2026)** is a format/accessibility modernization, not a methodology change. Existing ABS-classed vessel design procedures remain stable.

4. **API 579 Part 16 (FRP)** clarifies the boundary: current Parts 1–15 are metallic-only. This removes ambiguity around Phase 999.2 scope (Phase 999.2 FFS v1.0 targets metallic subsea structures per Parts 1–15; composite FFS deferred to v2.0).

5. **ISO 19901-1:2026 (metocean)** is the authoritative baseline for v1.1 OrcaWave hydrodynamic design-basis — confirms prior research exactly.

**The strategic insight:** The standards environment has entered a **consolidation phase** rather than a disruption phase. Existing methodologies (DNV-ST-F101 for pipelines, API RP 2A for fixed structures, API 579 Parts 1–15 for FFS) remain stable anchors. New standards (DNV-RP-F123, ISO 25249, API 579 Part 16) extend scope into new domains (hydrogen, offshore wind lifecycle, composite structures) but do not contradict existing guidance.

**For v1.1, Phase 7, and Phase 999.2:** this means the design-basis standards stack is locked and mature. Incremental additions are:
- DNV-RP-F123 if hydrogen is in client scope (decision needed)
- ISO 25249 as a forward-compatibility note (monitoring-track until publication)
- API 579 Part 16 decision point for Phase 999.2 FFS v2.0 (metallic v1.0, composite v2.0)

None of these block Phase 7 or v1.1 execution. All are scope-conditional or forward-looking additions.

`─────────────────────────────────────────────────`

---

## Sources

- [DNV Hydrogen Pipeline Recommended Practice (March 2026)](https://www.dnv.com/news/2026/new-dnv-recommended-practice-supports-offshore-hydrogen-pipelines-development/)
- [World Pipelines DNV-RP-F123 Coverage](https://www.worldpipelines.com/regulations-and-standards/26032026/new-dnv-recommended-practice-supports-offshore-hydrogen-pipelines-development/)
- [Ocean News DNV Hydrogen Pipeline Development](https://oceannews.com/news/energy/new-dnv-recommended-practice-to-support-offshore-hydrogen-pipeline-development/)
- [ISO 25249 Corrosion Protection of Offshore Wind — Part 1: Design Considerations](https://www.iso.org/standard/89568.html)
- [Institute of Corrosion: New ISO Standards on Offshore Wind](https://www.icorr.org/new-iso-standards-on-corrosion-protection-of-offshore-wind-to-be-developed/)
- [PPG Corrosion Solutions for Offshore Wind](https://www.ppg.com/en-US/pmc/advances-in-corrosion-for-offshore-wind)
- [ABS Offshore Rules Industry Update (January 2026)](https://pressreleases.eagle.org/news/abs-releases-industry-leading-update-to-offshore-rules)
- [ABS Offshore Rules via Marine Log](https://www.marinelog.com/news/abs-launches-new-offshore-rules/)
- [ISO 19901-1:2026 Metocean Design Standard](https://www.iso.org/standard/19901-1)
- [ISO 19902:2020 Fixed Steel Offshore Structures](https://www.iso.org/standard/65688.html)
- [ISO 19905-1 Jack-Up Rig Site-Specific Assessment](https://www.iso.org/standard/34591.html)
- [API 579-1/ASME FFS-1 Fitness-For-Service (ASNT)](https://www.asnt.org/me/26/3/api-579-asme-ffs-1-fitness-for-service-evaluation)
- [API 579 Part 16 FRP Assessment Levels (UTComp)](https://utcomp.com/news/about-api-579-1-asme-ffs-1-part-16/)
- [Inspectioneering: API 579 Resources](https://inspectioneering.com/tag/api+579)
- [ABS Cathodic Protection Guidance Notes (December 2018)](https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/offshore/306-cathodicprotection-offshore-structures/cathodic-protection-offshore-gn-dec18.pdf)
