# Research: competitor-market — 2026-04-02

## Key Findings

- **OrcaFlex 11.6c released Feb 2026 — DirectX 12 graphics rewrite, Python-driven loads, arbitrary radial position results.** The latest version introduces physically-based rendering (PBR) with realistic lighting/shadows, re-implemented 3D model import using Assimp (faithful .obj loading), and applied loads as Python variable functions. Graphics technology significantly upgraded but core cable/riser dynamics unchanged from v11.5. ([OrcaFlex 11.6c](https://www.orcina.com/releases/orcaflex-116/), [OrcaFlex 11.6b release](https://www.orcina.com/news/orcaflex-116b-released/), [OrcaFlex 11.6 release](https://www.orcina.com/news/orcaflex-116-released/))

- **ANSYS 2026 R1 — GPU resource prediction + thermal boundary enhancements for coupled multiphysics.** Machine learning resource estimator now provides GPU recommendations; new thermal load/boundary condition options for thermomechanical coupling; MultiZone/S-ALE mesh workflow improvements. Direct Morphing accelerates mesh-based workflows. No API-breaking changes reported, but ecosystem-wide GPU-aware features indicate shift toward HPC acceleration. ([ANSYS Release Notes 2026 R1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Ansys_Release_Notes.pdf), [ANSYS 2026 Structural Mechanics](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html))

- **Bentley SACS Cloud Services — parallel analysis turnaround 10x faster (days → minutes).** SACS Wind Turbine now offers fully automated 3D modeling + analysis + design via SACS CONNECT Edition with integrated workflows. Parallel cloud execution on Azure enables hundreds of load cases simultaneously. No pricing changes reported, but cloud-first positioning is competitive advantage against perpetual-license incumbents. ([SACS Offshore Structure](https://www.bentley.com/software/sacs-offshore-structure/), [SACS Cloud Services](https://www.chipestimate.com/Newest-Release-of-Bentley-and-rsquos-SACS-Software-for-Offshore-Structures-Improves-Dynamic-Analysis-to-Increase-Operational-Safety-and-Extend-Productive-Lifecycle/))

- **Blue Kenue freely available from NRC Canada — pre/post-processor for TELEMAC hydrodynamic modeling, 20+ year development.** Rectangular/triangular mesh generation, GIS data integration, supports open data formats (ArcINFO, MapInfo, GeoTIFF, SRTM, GRIB). Open-source, cloud-friendly positioning contrasts with licensed SACS/Sesam. Used extensively in coastal/wave modeling but less common in offshore structures. ([Blue Kenue NRC Canada](https://nrc.canada.ca/en/research-development/products-services/software-applications/blue-kenuetm-software-tool-hydraulic-modellers), [Blue Kenue enhancements 2014-2019](https://zenodo.org/records/3611511))

- **Competitor online calculator ecosystem emerging — SkyCiv, TheNavalArch, CalcForge gaining traction against aceengineer.** SkyCiv offers specialized offshore oil/gas calculators; TheNavalArch provides stability, mooring, lifting checks; CalcForge (open-source) and EngineeringToolBox (free general tools) reduce demand for specialized calculators. No aceengineer direct competitors found, but broader ecosystem shift toward free/low-cost web tools threatens consultation-pricing model. ([SkyCiv Offshore](https://skyciv.com/industries/offshore-oil-and-gas/), [TheNavalArch](https://thenavalarch.com/), [CalcForge](https://calcforge.com/))

## Relevance to Project

| Finding | Affected Package / Workflow |
|---|---|
| **OrcaFlex 11.6 graphics + Python loads** | **digitalmodel OrcaWave Phase 1.1** — The Python variable loads feature aligns perfectly with parametric sweep automation planned for Phase 7 (solver verification gate). Graphics rewrite is transparent to VIV/RAO calculation logic; focus remains on calculation report templates (Phase 1.1 active requirement). DirectX 12 PBR may enable higher-fidelity simulation visualizations in future client-facing reports. |
| **ANSYS 2026 GPU acceleration + ML resource prediction** | **digitalmodel** — GPU recommendations indicate industry shift toward HPC. Current Phase 1 modules (VIV, wall thickness, fatigue) are CPU-bound on dev-secondary; future optimization could parallelize across licensed-win-1 GPU if ANSYS Mechanical becomes calculation backend. ML resource predictor helps cost estimation for large batch jobs. |
| **Bentley SACS Cloud Services 10x speedup** | **aceengineer GTM positioning** — SACS Cloud (Azure parallel) is direct threat to consultation-based pricing. Clients can now run thousands of load scenarios in minutes without licensing local seats. Positioning opportunity: emphasize aceengineer's standards-traceability library + parametric design insights (not raw computation). Cloud parity is table-stakes; value must shift to domain expertise. |
| **Blue Kenue open-source mesh generation** | **digitalmodel future domain expansion** — Phase 999.1 (ship plan CAD pipeline) requires mesh generation (FreeCAD lofting). Blue Kenue's Assimp-based import + triangular mesh could reduce dependency on licensed mesh tools. Relevant for Phase 999.2 (fitness-for-service, monopile/jacket foundations) if hydrodynamic loading preprocessing becomes required. |
| **Free/low-cost competitor calculators** | **aceengineer.com positioning threat** — SkyCiv, TheNavalArch, and CalcForge lower barrier to entry for offshore calculations. aceengineer's differentiation must rest on (1) standards traceability (calculation → standard reference chain), (2) domain expertise (consultation, not just tools), (3) specialized domains (VIV, cathodic protection, complex FFS rules). Price compression evident; margin pressure on generic calculators. |

## Recommended Actions

- [ ] **Create GitHub issue** — Monitor OrcaFlex 11.6+ Python loads API for integration with digitalmodel parametric sweep framework (Phase 1.1 sensitivity analysis tooling); document Python API compatibility with Phase 7 automation.

- [ ] **Create GitHub issue** — Research ANSYS 2026 GPU acceleration for wall thickness/fatigue batch jobs; evaluate cost-benefit of GPU-aware refactor for computational bottlenecks on licensed-win-1.

- [ ] **Promote to PROJECT.md** — Add note under "Key Decisions" section: "Cloud-first competitor positioning (SACS Azure cloud, ANSYS HPC) signals market shift away from perpetual licensing. aceengineer value proposition must emphasize standards traceability + domain expertise (VIV, CP, FFS), not raw computation speed. Consultation-based pricing sustainable only with differentiated analysis capabilities."

- [ ] **Create GitHub issue** — Competitive analysis: audit SkyCiv, TheNavalArch, and CalcForge feature parity against aceengineer live calculators (ASME B31.4 wall thickness, DNV-RP-F109 on-bottom stability). Identify gaps and opportunities for differentiation (e.g., VIV calculator unique to aceengineer).

- [ ] **Promote to ROADMAP.md** — Add Phase 999.6 backlog item: "Blue Kenue integration for hydrodynamic mesh preprocessing — evaluate for Phase 999.1 (ship plan CAD pipeline) and Phase 999.2 (monopile/jacket foundation analysis)."

- [ ] **Ignore (low priority)** — Sesam pricing 2026 — no public announcements found. Sesam remains enterprise software with negotiated licensing; track through industry conferences (Offshore Technology Conference, SPE events) if pricing pressure becomes relevant to proposal strategy.

- [ ] **Ignore (low priority)** — Flexcom updates — no 2026 announcements; Wood Group's flexible pipe analysis remains specialized. Relevant only if client demand for flexible riser design appears; currently out of scope.

---

Sources:
- [OrcaFlex 11.6 release](https://www.orcina.com/releases/orcaflex-116/)
- [OrcaFlex 11.6b release announcement](https://www.orcina.com/news/orcaflex-116b-released/)
- [OrcaFlex 11.6c release announcement](https://www.orcina.com/news/orcaflex-116-released/)
- [ANSYS 2026 R1 Release Notes](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Ansys_Release_Notes.pdf)
- [ANSYS 2026 Structural Mechanics Highlights](https://www.cadfem.net/en/cadfem-informs/newsroom/ansys-release/ansys-release-2026-structures.html)
- [SACS Offshore Structure Software](https://www.bentley.com/software/sacs-offshore-structure/)
- [Bentley SACS Dynamic Analysis Enhancements](https://www.chipestimate.com/Newest-Release-of-Bentley-and-rsquos-SACS-Software-for-Offshore-Structures-Improves-Dynamic-Analysis-to-Increase-Operational-Safety-and-Extend-Productive-Lifecycle/)
- [Blue Kenue — National Research Council Canada](https://nrc.canada.ca/en/research-development/products-services/software-applications/blue-kenuetm-software-tool-hydraulic-modellers)
- [Blue Kenue Enhancements 2014-2019](https://zenodo.org/records/3611511)
- [SkyCiv Offshore Oil and Gas Design Analysis](https://skyciv.com/industries/offshore-oil-and-gas/)
- [TheNavalArch Engineering Tools](https://thenavalarch.com/)
- [CalcForge Open Source Calculators](https://calcforge.com/)
