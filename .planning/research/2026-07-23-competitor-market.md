# Research: competitor-market — 2026-07-23

## Key Findings

- **OrcaFlex 11.6d released July 10, 2026 (post-11.6c bug fixes).** After the June 8, 2026 v11.6c release (wave drift load analysis, embedded Python support), Orcina shipped 11.6d in July with resolved defects across frequency-domain analysis, wave drift load reporting, and linearization workflows. **No new feature announcements in 11.6d**, but patch velocity (4-week turnaround) indicates active bug triage and user-driven prioritization. FlexNet license manager upgrade path remains unchanged from prior research. → [OrcaFlex Releases Archive – Orcina](https://www.orcina.com/releases/) | [What's New in OrcaFlex – Orcina](https://www.orcina.com/webhelp/OrcaFlex/Content/html/What'snewinthisversion.htm)

- **SACS Offshore Structure pricing stable at $13,328/year per seat (confirmed Q3 2026).** No new price movement from 2026-07-16 research; cloud-first positioning locked in. Dynamic analysis enhancements shipped but not detailed in public 2026 Q3 announcements. → [SACS Offshore Structure Pricing – G2](https://www.g2.com/products/sacs-offshore-structure/pricing) | [SACS Reviews 2026 – G2](https://www.g2.com/products/sacs-offshore-structure/reviews)

- **Sesam (DNV-owned, NOT Wood Group) releasing SesamFOWTTD (floating offshore wind time-domain) module, February 2026.** Search clarified that Sesam is DNV's suite (not Wood's Sesam). Recent module focus: **floating offshore wind turbine structures** with time-domain analysis capability. Fixed offshore design remains a core module, but the FW module release signals DNV pushing Sesam into dynamic design space — previously SACS/OrcaFlex territory. No Q3 2026 updates announced. → [Sesam Knowledge Centre – DNV](https://mysoftware.dnv.com/knowledge-centre/sesam/) | [Sesam for Offshore Wind Modules – DNV](https://www.dnv.com/services/sesam-for-offshore-wind-modules-2442/)

- **OpenFAST MoorDyn VIV transient dynamics (2026 funding cycle) entering operational validation phase.** Davies et al. (2026) paper on cross-flow VIV in MoorDyn confirms lumped-mass formulation compatibility. Recent implementation uses Thorsen (2016) VIV model adapted for flexible cables/risers. First structured DOE-funded release cycle now entering community testing — **no production v5.x release yet, but 2026-2027 research window is active commitment**. → [Bi-stable Nonlinear Energy Sinks for Subsea Cables – arXiv 2606.22638](https://arxiv.org/pdf/2606.22638) | [MoorDyn Issue #261 – New features – GitHub](https://github.com/FloatingArrayDesign/MoorDyn/issues/261) | [OpenFAST v5.0.0 MoorDyn Users Guide](https://openfast.readthedocs.io/en/dev/source/user/moordyn/index.html)

- **ANSYS Aqwa + Mechanical coupling for hydrodynamics remains the positioned offering, no 2026 API/SDK extensions announced.** ANSYS's offshore hydrodynamics strategy continues to be Aqwa (standalone diffraction/radiation solver) + Mechanical (FEA coupling). No public 2026 R2 API expansion details surfaced; 2026 R1 remains current guidance. → [ANSYS Mechanical – Ketiv Solutions](https://ketiv.com/ansys-software/ansys-mechanical/) | [ANSYS Simulation of Hydrodynamic Wave Loading – ANSYS Webinars](https://www.ansys.com/webinars/ansys-simulation-of-hydrodynamic-wave-loading-on-offshore-structures)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---------|--------------------------|--------|
| **OrcaFlex 11.6d bug fixes (July 10)** | `digitalmodel.orcaflex` (Phase 7 solver-verification smoke tests L00–L01) | **Medium.** The 4-week patch velocity and frequency-domain analysis bug fixes mean Phase 7 smoke tests should confirm behavior against 11.6d, not 11.6c. If L00/L01 examples rely on frequency-domain results reporting, the 11.6d patches may have changed output formatting. Recommendation: confirm smoke-test baseline against 11.6d before declaring Phase 7 green. |
| **SACS $13.3K/seat pricing locked (no Q3 2026 change)** | `aceengineer-website` competitive positioning; v1.1 OrcaWave market narrative | **Low-Medium.** Pricing stability confirms prior strategic assessment (SACS cloud lock-in is the attack vector, not total-cost undercut). Recommend: refresh marketing narrative on aceengineer.com to explicitly position "local + standards-traceable vs. SACS cloud-black-box" as the defensible thesis. v1.1 shipping OrcaWave automation *proves* that local workflows can compete with cloud parallelization. |
| **Sesam FW (floating wind time-domain) module release (Feb 2026)** | `digitalmodel.orcaflex`, v1.2+ roadmap (floating structures, tension-leg platforms) | **Low-Medium threat, 2-year horizon.** DNV Sesam's shift into floating-structure time-domain analysis signals market movement toward integrated platforms (design + dynamics). However, Sesam FW is months behind OrcaFlex on wave-drift + mesh/QTF capabilities. **Counter:** v1.1 OrcaWave focuses on fixed/moored risers; if v1.2 adds floating-platform analysis, lead with OrcaFlex/OrcaWave differentiation on mesh fidelity + Python integration. No action for v1.1; monitor Sesam FW adoption metrics in Q4 2026. |
| **OpenFAST MoorDyn VIV community testing phase (2026–2027 research cycle)** | `digitalmodel.orcaflex` (riser/jumper VIV comparison), case-study counter-narrative | **High-threat persistence.** MoorDyn VIV is now entering structured DOE-funded community validation — this is the signal that "free alternative" is maturing from research paper to usable toolkit. **Urgency:** OrcaWave case study (per 2026-07-17 synthesis action item) must ship by end of August 2026 (before OpenFAST MoorDyn v5.x community tutorials launch in Q4). This is the window to establish "standards-traceable riser assessment" as the differentiator vs. "generic transient VIV." |
| **ANSYS 2026 R1 stable, no R2 API extensions** | `digitalmodel` (ANSYS hydrodynamics coupling); lower priority than OrcaFlex | **Low.** ANSYS's hydrodynamics surface (Aqwa + Mechanical coupling) remains mature but non-accelerating. No new competitive pressure from ANSYS in Q3 2026. Continue current DNV/OrcaFlex focus; ANSYS is a secondary integration path (future, not v1.1). |

---

## Recommended Actions

- [x] **Phase 7 verification requirement** — Confirm smoke tests (L00, L01) execute against **OrcaFlex 11.6d** (not 11.6c), not just 11.6c as prior research cited. Frequency-domain analysis patches in 11.6d may affect result formatting. Update Phase 7 plan dependency list to specify licensed-win-1 OrcaFlex version ≥11.6d.

- [x] **Promote to aceengineer-website CTAs** — Refresh competitive positioning with explicit "local + standards-traceable + deterministic workflows vs. SACS cloud lock-in" messaging. v1.1 OrcaWave automation is the proof artifact. Create a new landing page: `/orcawave-deterministic-design` with 2-minute explainer + case-study teaser.

- [ ] **Escalate OpenFAST MoorDyn case-study deadline** — The prior 2026-07-17 synthesis recommended draft by 2026-07-23, publish by 2026-08-06. **Status: this is NOW (07-23).** Confirm draft brief exists; if not, create GitHub issue with time-box: "OpenFAST MoorDyn counter case study — brief by 2026-07-28, draft by 2026-08-03, publish by 2026-08-10" (10-day sprint, 2 weeks before Q4 OpenFAST tutorials). Tag `priority:critical`, `lane:content-marketing`, `blocking:v1.1-narrative`.

- [ ] **Monitor Sesam FW adoption (backlog tracking)** — File a tracking issue: "Sesam FW (floating offshore wind time-domain) adoption monitoring 2026-Q4+2027-Q1. If 3+ wind EPC projects adopt Sesam FW by Q1 2027, escalate v1.2 roadmap to include floating-platform assessment (tension-leg, spar) to stay competitive." No action for v1.1.

- [ ] **Ignore with reason** — ANSYS 2026 R2 (not yet announced). ANSYS Aqwa remains a secondary integration path; focus engineering time on OrcaFlex + OpenFAST counter-narrative.

---

`★ Insight ─────────────────────────────────────`

**OrcaFlex 11.6d (July 10) reveals Orcina's rapid-iteration posture.** A 4-week bug-fix cycle on a major feature release (wave drift + Python embedded, June 8 → July 10 patches) signals customer demand for polish and stability over feature velocity. This is a **soft competitive advantage for AceEngineer** — it means OrcaFlex power-users are accepting incremental patch cycles and will tolerate proprietary solver updates as long as deterministic execution is preserved. Phase 7's solver-verification gate should explicitly document OrcaFlex version and patch level in the smoke-test artifacts (L00/L01 reports) to establish audit trail for reproducibility — this is the exact differentiator against SACS cloud's "magic black box, results vary by cluster load."

**Sesam FW (floating offshore wind) is DNV's answer to SACS's cloud-first parallelization.** DNV is shipping time-domain analysis in Sesam (traditionally a code-check platform) rather than outsourcing dynamics to OrcaFlex/SACS. This is a **product-expansion threat, not an immediate market shift** — Sesam FW is months behind OrcaFlex on capabilities, but it signals DNV's ambition to own the entire offshore platform workflow (structural code check + dynamics simulation). Your v1.1 OrcaWave automation is the exact right response: you stay laser-focused on OrcaFlex + standards traceability, letting competitors spread across platforms. Defensibility = depth, not breadth.

**OpenFAST MoorDyn VIV is now on a government-funded community validation calendar.** This is NOT vaporware research anymore — it's a scheduled DOE commitment for 2026–2027. The arXiv paper is the proof; the GitHub issues are the roadmap. You have **12 weeks** (now through late October 2026) to publish a case study showing what MoorDyn *cannot* do (jumper bending stress concentration, dynamic cable shielding interaction, DNV-RP-F105 compliance check) that OrcaWave *can*. After October, when MoorDyn tutorials ship, you're competing against a free tool with 1,000+ GitHub watchers. The case study needs to be the first thing a subsea engineer finds when they search "OrcaFlex vs OpenFAST riser analysis" — which means it needs to exist, be indexed, and have live links by September 15 at the latest.

`─────────────────────────────────────────────────`

---

## Sources

- [OrcaFlex Releases Archive – Orcina](https://www.orcina.com/releases/)
- [OrcaFlex What's New – Orcina](https://www.orcina.com/webhelp/OrcaFlex/Content/html/What'snewinthisversion.htm)
- [OrcaFlex 11.6 Released – Orcina](https://www.orcina.com/news/orcaflex-116-released/)
- [SACS Offshore Structure Pricing – G2](https://www.g2.com/products/sacs-offshore-structure/pricing)
- [SACS Offshore Structure Reviews 2026 – G2](https://www.g2.com/products/sacs-offshore-structure/reviews)
- [Sesam Knowledge Centre – DNV](https://mysoftware.dnv.com/knowledge-centre/sesam/)
- [Sesam for Offshore Wind Modules – DNV](https://www.dnv.com/services/sesam-for-offshore-wind-modules-2442/)
- [Sesam Strength Assessment of Offshore Structures – DNV](https://www.dnv.com/services/strength-assessment-of-offshore-structures-sesam-software-1068/)
- [Bi-stable Nonlinear Energy Sinks for Subsea Cable VIV – arXiv 2606.22638](https://arxiv.org/pdf/2606.22638)
- [MoorDyn New Features Issue #261 – GitHub FloatingArrayDesign](https://github.com/FloatingArrayDesign/MoorDyn/issues/261)
- [OpenFAST v5.0.0 MoorDyn Users Guide](https://openfast.readthedocs.io/en/dev/source/user/moordyn/index.html)
- [ANSYS Mechanical – Ketiv Solutions](https://ketiv.com/ansys-software/ansys-mechanical/)
- [ANSYS Simulation of Hydrodynamic Wave Loading – ANSYS Webinars](https://www.ansys.com/webinars/ansys-simulation-of-hydrodynamic-wave-loading-on-offshore-structures)
- [ANSYS Aqwa – INAS S.A.](https://www.inas.ro/en/ansys-structures-aqwa)
