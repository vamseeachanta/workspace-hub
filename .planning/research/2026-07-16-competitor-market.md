# Research: competitor-market — 2026-07-16

## Key Findings

- **OrcaFlex v11.6c released June 8, 2026 with wave drift load analysis.** Orcina's latest release adds wave drift load analysis examples and embedded Python support for external functions, post-calculation actions, and user-defined results. FlexNet library updated to v11.19.8 — users on floating licenses must upgrade the license manager before migrating to v11.6. Flexible lease terms (MUS model, 1-month minimum) remain competitive. → [OrcaFlex Release Notes – Orcina](https://www.orcina.com/news/orcaflex-110-released/) | [FlexNet License Manager Upgrade – Orcina](https://www.orcina.com/news/flexnet-license-manager-upgrade/)

- **SACS Cloud Services confirmed 10x+ speedup; pricing locked at $13,328/year per seat (2026).** Azure cloud parallelization of hundreds of load cases for full design code compliance in minutes vs. days. No price shift from prior research (2026-07-09), but cloud lock-in positioning remains the primary competitive vector against local-license models. SACS Offshore Enterprise includes wave loading for floating structures. → [SACS Offshore Structure Pricing 2026 – G2](https://www.g2.com/products/sacs-offshore-structure/pricing) | [Bentley SACS Cloud Analysis – Informed Infrastructure](https://informedinfrastructure.com/post/bentleys-sacs-provides-advanced-analysis-and-workflow-enhancements-for-offshore-structures)

- **ANSYS 2026 R1 stabilized; no R2 announced.** Direct Morphing workflow + GPU-aware resource prediction + Sherlock reliability integration remain the 2026 feature set. Mechanical API accessible via Ansys Developer Portal but specific offshore hydrodynamics API extensions not detailed in public announcements. No 2026 R2 release roadmap found. → [ANSYS 2026 R1 Structural Mechanics – CADFEM](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html) | [Ansys Mechanical API Reference – Developer Portal](https://developer.ansys.com/docs/mechanical-scripting-interface/api/index.md)

- **OpenFAST MoorDyn VIV transient dynamics now live (2026 research funding cycle).** Recent DOE funding expanded OpenFAST marine turbine adaption with KC-dependent platform drag, transient vortex-induced vibration in MoorDyn (lumped-mass formulation), and MAP++ quasi-static mooring coupling. This is the **most recent OSS riser/mooring capability update** — moves OpenFAST beyond wind-aero-hydro coupling into dynamic subsea system modeling. → [OpenFAST for Marine Turbines – NREL](https://www.nlr.gov/water/open-fast) | [Bi-stable Energy Sinks for Subsea Cable VIV – arXiv 2606.22638](https://arxiv.org/pdf/2606.22638)

- **MarineHydro.jl (Cornell) emerging as open-source floating-structure hydrodynamic solver (2025–26).** Julia-based, purpose-built for parametric design exploration of floating offshore platforms (monopiles, spacing, diameter optimization). Not yet domain-specific for subsea/riser work, but demonstrates OSS momentum in structural hydrodynamics as an alternative to proprietary solvers. → [Cornell Software for Offshore Structures – Cornell Chronicle](https://news.cornell.edu/stories/2025/10/cornell-software-advances-design-offshore-structures)

- **Flexcom remains stable, no major 2026 feature announcements.** Continued integration with OpenFAST via Flexcom Wind (aerodynamic coupling) and MoorDyn. No evidence of new capabilities, pricing changes, or competitive repositioning by Wood Group since v8 launch. → [Flexcom – Wood Group](https://www.woodgroup.com/solutions/expertise/flexcom) | [Flexcom Brochure – Wood](https://www.woodplc.com/__data/assets/pdf_file/0020/119441/Flexcom-Brochure.pdf)

---

## Relevance to Project

| Finding | Impact on AceEngineer | Affected Package/Workflow |
|---------|----------------------|--------------------------|
| **OrcaFlex v11.6c Python embedded + wave drift** | **Opportunity:** Python hooks in OrcaFlex enable bidirectional binding with `digitalmodel`. Can now call OrcaFlex analysis from `digitalmodel.orcaflex` wrapper, extract results via Python sidecar, eliminate manual export/re-import friction. FlexNet update is **not** a breaking change for existing license pools. | `digitalmodel.orcaflex` module; v1.1 OrcaWave automation Phase 7 (parametric update → OrcaFlex execution → result extraction) |
| **SACS cloud 10x speedup + $13.3K/seat pricing** | **Threat:** Reinforces SACS as the cloud-first competitive standard. However, pricing is **per-seat** (not per-job), so the attack vector is "eliminate desktop license cost + force cloud payroll" — not a total-cost undercut. **Differentiator remains:** AceEngineer as "standards-transparent, local-execution-friendly, cloud-agnostic." | `aceengineer-website` CTAs emphasizing local/cloud flexibility; positioning against SACS cloud lock-in in marketing material. v1.1 OrcaWave milestone proves this differentiation. |
| **ANSYS 2026 R1 stable, no R2 roadmap** | **Low threat shift.** ANSYS GPU morphing / Sherlock bundling were 2026 R1 novelties; no new 2026 R2 competitive pressure detected. Offshore hydrodynamics API remains undocumented. **Monitor:** If ANSYS releases R2 in H2 2026 with new API surface, re-assess. | `digitalmodel` (ANSYS hydrodynamics coupling is out-of-scope; focus remains OrcaFlex + DNV analytical modules) |
| **OpenFAST MoorDyn VIV (2026 DOE cycle) — HIGHEST OSS THREAT** | **Critical:** MoorDyn transient VIV + MAP++ mooring coupling now puts OpenFAST directly in the **riser/mooring dynamics space** (previously aero-hydro-wind-turbine only). This is the first credible OSS alternative to `digitalmodel.orcaflex` for dynamic riser assessment. **Counter:** (1) Publish 1–2 case studies showing riser-specific insights OpenFAST cannot deliver (jumper bending, cable shielding), (2) cite DNV-RP-F105 (revised) as proof that riser assessment tightens standards annually. | `digitalmodel.orcaflex` (riser VIV, mooring bending, dynamic cable); priority: publish OrcaWave case study vs. OpenFAST before H2 2026 (when OpenFAST funding cycle matures into tutorials). |
| **MarineHydro.jl Julia solver — emerging OSS** | **Low-medium threat (2–3 year horizon).** Current scope is floating-platform hydrodynamics (not subsea risers). However, Julia's performance + OSS momentum means it could expand into riser/mooring by 2027–28. **Opportunity:** MarineHydro.jl solves a different problem (platform design iteration) than `digitalmodel` (standards-traceable riser analysis). Potential partnership/data-exchange use case (platform loads → riser designer). | Potential future connector: export AceEngineer platform designs to MarineHydro.jl for verification (out-of-scope for v1.1; file backlog issue) |
| **Flexcom stagnation (no 2026 updates)** | **Outreach opportunity, not a threat.** Flexcom's stable-but-non-innovating posture suggests user frustration with iteration speed. Existing Flexcom-user relationships (if any at AceEngineer) are warm leads for "parametric batch runs + sensitivity analysis" workflows. | Backlog: Explore Flexcom results-importer (as noted in prior 2026-07-09 synthesis) to offer Flexcom users a faster iteration UI without replacing Flexcom backend. |

---

## Recommended Actions

- [ ] **Promote to PROJECT.md** — Update "Market Position" section with 2026-07-16 data: (1) SACS cloud pricing locked, no new threat (desktop-license defense remains viable), (2) **OpenFAST MoorDyn VIV is the #1 OSS threat — requires immediate counter-artifact (OrcaWave case study)**. (3) ANSYS R1 stable, monitor H2 for R2. (4) MarineHydro.jl is 2–3 year horizon, partnership potential. Cite this research + prior 2026-07-09/2026-07-13 standards research as evidence that **standards consolidation + OpenFAST expansion = AceEngineer must lead on riser/mooring specificity + standards traceability**.

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "OpenFAST MoorDyn VIV case study — publish 1 OrcaWave riser dynamic analysis (jumper bending, cable shielding, dynamic tension) showing riser-specific insights MoorDyn cannot deliver. Timeline: draft by EOW 2026-07-23, publish web case study by 2026-08-06 (before OpenFAST H2 tutorial cycle)." Tag `lane:content-marketing`, `priority:high`.

- [ ] **Create GitHub issue** — `digitalmodel#TBD`: "OrcaFlex v11.6c Python embedded sidecar integration — scope Phase 8 enhancement: parametric update → Python-wrapped OrcFxAPI call → result extraction → report generation. Enables end-to-end automated workflows (v1.1 → v1.2 capability). Depends on licensed-win-1 Phase 7 solver verification gate." Tag `lane:infrastructure`, `status:backlog`.

- [ ] **Monitor** — ANSYS 2026 R2 release (monitor Sept–Oct 2026). If R2 ships with expanded Mechanical API or offshore hydrodynamics surface, re-assess competitive positioning on GPU compute + bundled reliability.

- [ ] **Monitor** — OpenFAST release cycle (NREL). If MoorDyn VIV hits official GA + ships tutorials by August 2026, accelerate case-study publication to September 2026 (stay 30 days ahead of OSS competitive awareness).

- [ ] **Defer** — MarineHydro.jl partnership (2–3 year horizon). File a backlog issue when Cornell publishes v1.0 / reaches production readiness.

- [ ] **Ignore with reason** — Flexcom results-importer as v1.1 priority (Flexcom is stable, not competitive threat; user demand is speculative; reserve engineering time for OpenFAST counter + OrcaWave completion).

---

`★ Insight ─────────────────────────────────────`
**The competitive landscape is bifurcating: cloud-first (SACS) vs. standards-first (AceEngineer).** SACS uses cloud parallelization to commoditize the compute layer — 10x speedup is only achievable if you accept vendor lock-in. Your v1.1 OrcaWave automation accomplishes the opposite: it proves that **deterministic, local, standards-traceable workflows can be faster and more auditable than cloud black-boxes**. This is not a feature; it's a business model thesis worth naming explicitly in marketing.

**OpenFAST's MoorDyn VIV expansion (June 2026 research funding) is the only new competitive threat since the prior research (July 9).** It moves OpenFAST from "wind turbine simulator" to "riser dynamics toolkit," which is `digitalmodel.orcaflex`'s core domain. The counter is not to out-feature OpenFAST (it's free, you can't), but to out-educate it — publish a riser case study showing what OpenFAST *cannot* do (DNV-RP-F105 jumper assessment, cable shielding interaction, dynamic bending stress concentration). This is content marketing + standards traceability working in concert.

**Julia is gaining traction in engineering software.** MarineHydro.jl is the first OSS offshore structural solver I've found. Python is still dominant, but Julia's speed + multiple-dispatch makes it attractive for PDEs and hyperparameter sweeps. This doesn't threaten `digitalmodel` (analytical/standards-based, not PDE-heavy), but if you see 2+ Julia offshore tools emerge by 2027, it signals a language shift worth monitoring for your long-term technical positioning.
`─────────────────────────────────────────────────`

---

Sources:
- [OrcaFlex v11.6c Release – Orcina](https://www.orcina.com/news/orcaflex-110-released/)
- [FlexNet License Manager Upgrade for OrcaFlex 11.6 – Orcina](https://www.orcina.com/news/flexnet-license-manager-upgrade/)
- [OrcaFlex Specification – Orcina](https://www.orcina.com/orcaflex/specification/)
- [SACS Offshore Structure Pricing 2026 – G2](https://www.g2.com/products/sacs-offshore-structure/pricing)
- [SACS Cloud Analysis Enhancements – Informed Infrastructure](https://informedinfrastructure.com/post/bentleys-sacs-provides-advanced-analysis-and-workflow-enhancements-for-offshore-structures)
- [SACS Offshore Structure – Bentley Systems](https://www.bentley.com/software/sacs-offshore-structure/)
- [ANSYS 2026 R1 Structural Mechanics – CADFEM](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html)
- [ANSYS 2026 R1 Webinar – Ansys](https://www.ansys.com/webinars/ansys-2026-r1-structures)
- [Ansys Mechanical API Reference – Developer Portal](https://developer.ansys.com/docs/mechanical-scripting-interface/api/index.md)
- [OpenFAST for Marine Turbines – NREL Water Research](https://www.nlr.gov/water/open-fast)
- [Bi-stable Nonlinear Energy Sinks for Subsea Cable VIV – arXiv](https://arxiv.org/pdf/2606.22638)
- [Floating Offshore Wind Turbine Mooring Optimization – ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0029801824032530)
- [Improved Hydrodynamics Modeling for Marine Turbines – EWTEC](https://submissions.ewtec.org/proc-ewtec/article/view/1094)
- [Cornell Software for Offshore Structures – Cornell Chronicle](https://news.cornell.edu/stories/2025/10/cornell-software-advances-design-offshore-structures)
- [Flexcom – Wood Group](https://www.woodgroup.com/solutions/expertise/flexcom)
- [Flexcom Brochure – Wood](https://www.woodplc.com/__data/assets/pdf_file/0020/119441/Flexcom-Brochure.pdf)
