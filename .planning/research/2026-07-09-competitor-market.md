# Research: competitor-market — 2026-07-09

## Key Findings

- **SACS Cloud Services acceleration model:** Bentley's SACS V12 offers 10x+ speedup via Azure cloud parallelization across hundreds of load cases, enabling full design code compliance in minutes vs. days. This is a direct cloud-first positioning that undermines per-seat, compute-local pricing for legacy platforms. → [SACS Offshore Structure – Bentley](https://www.bentley.com/software/sacs-offshore-structure/) | [Informed Infrastructure feature](https://informedinfrastructure.com/post/bentleys-sacs-provides-advanced-analysis-and-workflow-enhancements-for-offshore-structures)

- **ANSYS 2026 R1 structural mechanics + Direct Morph workflow:** GPU-aware resource prediction and Direct Morphing workflow lower mesh-rebuild friction for iterative design; now integrated with Sherlock PCB reliability tools and LS-DYNA charting. Mechanical API expanded but not detailed; offshore hydrodynamics (SPARs, FPSOs, semi-subs, TLPs) remain a core pitch. → [Ansys 2026 R1 Structures Release](https://www.ansys.com/webinars/ansys-2026-r1-structures) | [CADFEM Release Notes](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html)

- **OpenFAST expanded to marine / floating turbine applications:** NREL's OpenFAST (open-source) now models floating offshore wind + marine energy turbines with buoyant-load assessment. WEIS (Wind Energy Integrated System) co-design framework built on OpenFAST for control optimization. This is the largest credible OSS threat in the structural dynamics space for offshore wind. → [OpenFAST Marine Turbines](https://tethys-engineering.pnnl.gov/publications/openfast-marine-turbines-development-open-source-modeling-tool) | [NREL Water Research](https://www.nrel.gov/water/open-fast)

- **Sesam/DNV consolidation under Sesam Manager:** DNV has replatformed Sesam onto a unified "Sesam Manager" with 30+ modules under a refreshed JavaScript-based UI. Modules for fixed OWT structures and floating structures (HydroD) are positioned as tightly integrated. Pricing model and cloud availability not disclosed in recent announcements. → [DNV Sesam Manager](https://www.dnv.com/services/manage-your-structural-analysis-workflow-with-sesam-manager-4287/) | [Sesam Floating Structures HydroD](https://www.dnv.com/services/floating-structure-design-and-modification-sesam-for-floating-structures-2410/)

- **Flexcom v8 (Wood Group) maintains 30-year track record but no 2026 announcements found:** Flexcom's hybrid Euler–Bernoulli beam-column FEA (risers, moorings, cables) is stable but no recent version announcements or cloud/subscription shifts were found. Wood Group's acquisition of MCS Kenny (Flexcom publisher) signaled consolidation but does not suggest aggressive new capabilities. → [MCS Kenny v8 Release](https://www.offshore-energy.biz/mcs-kenny-launches-flexcom-v8-riser-design-software-ireland/) | [Wood Group Flexcom](https://www.woodgroup.com/solutions/expertise/flexcom)

---

## Relevance to Project

| Finding | Impact on AceEngineer | Affected Package/Workflow |
|---------|----------------------|--------------------------|
| **SACS cloud parallelization** | Direct threat to `digitalmodel` OrcaFlex standalone-license positioning. Cloud parallelism is a **pricing lock-in vector** — customers willing to pay per-job or per-hour cloud costs to avoid re-licensing for parallel runs. **Opportunity:** position `digitalmodel` as cloud-agnostic (both local desktop + cloud-native via OrcFxAPI); standardize on CLI/API entry points, not UI. | `digitalmodel.orcaflex` module; `aceengineer-website` calculator CTAs (emphasize "your compute, your data, no vendor lock-in") |
| **ANSYS GPU morphing + Sherlock integration** | ANSYS is bundling reliability + structural iteration in one workflow. **Opportunity:** `digitalmodel` wall-thickness, fatigue, and FFS modules do NOT require GPU — they are analytical/formulaic. Position **speed, reproducibility, and standards traceability** vs. heavy compute. Emphasize DNV-OS-E301/API 579 citation sidecars as audit-proof. | `digitalmodel.structural` (wall thickness, spectral fatigue); `digitalmodel.citations` (standards binding) |
| **OpenFAST open-source marine expansion** | Largest OSS threat to `digitalmodel` OrcaWave vessel hydrodynamics. **Opportunity:** OpenFAST is aero-hydro-servo-elastic coupled; `digitalmodel` OrcaWave is dynamic-riser-specific. Differentiate on **riser/umbilical/mooring physics** (tension, bending, VIV), not wind turbine mechanics. Publish 1–2 case studies showing riser-specific insights OpenFAST cannot deliver. | `digitalmodel.orcaflex` riser/mooring modules; `digitalmodel.hydrodynamics` (vessel-incident-wave coupling, not turbine control) |
| **Sesam Manager consolidation** | DNV is the #1 structural-analysis vendor for offshore. Sesam Manager's JavaScript UI rebrand signals intent to modernize UX but does NOT threaten standardized calculation outputs. **Opportunity:** Partner with Sesam users (they are your customers) by offering **standards-to-calc traceback** — show exactly which DNV-OS rule drove a calculation, enable Sesam exports → AceEngineer validation. | `digitalmodel` as a **validator/explainer** for Sesam outputs, not a replacement; `llm-wiki` DNV-OS standard pages as audit artifacts for clients |
| **Flexcom stability, no new features** | Flexcom's 30-year heritage + Wood Group backing means it is **not going away**, but lack of visible 2026 innovation suggests Wood Group is consolidating rather than innovating. **Opportunity:** Flexcom users are ripe for targeted outreach — they have deep riser domain knowledge and may want **faster iteration** (`.digitalmodel.flexcom_bridge`? wrapper for parametric bulk runs). | `digitalmodel.flexible_pipe` module (if planned); potential `flexcom_results_importer` for client workflows |

---

## Recommended Actions

- [ ] **Promote to PROJECT.md** — Add competitive-positioning section: "Market: SACS Cloud 10x speedup + OpenFAST OSS threat + Sesam consolidation = **focus AceEngineer on standards traceability + local autonomy + riser/mooring specificity**"

- [ ] **Create GitHub issue** — `digitalmodel#TBD`: "Flexcom wrapper exploration: can we automate Flexcom runs + extract results for validation/sensitivity workflows?" (Probe Flexcom user demand in your existing relationships)

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "Competitive research: publish 1 OrcaWave riser case study vs OpenFAST to show riser-specific insights" (Feeds content marketing + validates differentiation)

- [ ] **Ignore with reason** — OrcaFlex licensing changes (2026-Q3 not yet announced; monitor Q3/Q4 for annual updates; SACS cloud offering does NOT include OrcaFlex equivalency, so pricing parity unlikely to shift soon)

- [ ] **Ignore with reason** — AI offshore software development trends (generic outsourcing commentary, not domain-specific competitors; your 1-person solo model + AI agent orchestration is orthogonal)

---

Sources:
- [Bentley SACS Offshore Structure](https://www.bentley.com/software/sacs-offshore-structure/)
- [SACS Cloud Services and Analysis Enhancements – Informed Infrastructure](https://informedinfrastructure.com/post/bentleys-sacs-provides-advanced-analysis-and-workflow-enhancements-for-offshore-structures/)
- [Ansys 2026 R1 Structures Webinar](https://www.ansys.com/webinars/ansys-2026-r1-structures)
- [CADFEM Ansys 2026 Structures Release](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html)
- [OpenFAST for Marine Turbines – Tethys Engineering](https://tethys-engineering.pnnl.gov/publications/openfast-marine-turbines-development-open-source-modeling-tool)
- [NREL Water Research – OpenFAST](https://www.nrel.gov/water/open-fast)
- [DNV Sesam Manager](https://www.dnv.com/services/manage-your-structural-analysis-workflow-with-sesam-manager-4287/)
- [DNV Sesam Floating Structures – HydroD](https://www.dnv.com/services/floating-structure-design-and-modification-sesam-for-floating-structures-2410/)
- [MCS Kenny Flexcom v8 Launch – Offshore Energy](https://www.offshore-energy.biz/mcs-kenny-launches-flexcom-v8-riser-design-software-ireland/)
- [Wood Group Flexcom Solution](https://www.woodgroup.com/solutions/expertise/flexcom)
