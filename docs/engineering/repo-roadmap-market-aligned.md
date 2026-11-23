# Market-Aligned Repository Roadmap

This document aligns the `digitalmodel` repository's development priorities with job market demand and the ACE Engineer GTM strategy for high-value retainers. It builds upon the detailed, client-driven technical roadmap located at `../../digitalmodel/ROADMAP.md`.

## 1. Current Package Maturity vs. Market Demand

The job market for naval architects and offshore structural engineers consistently demands expertise in a few key areas. The following table maps the maturity of `digitalmodel` packages against these in-demand skills.

| In-Demand Skill Area         | `digitalmodel` Package(s)                                   | Maturity          | Market Alignment                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Subsea Dynamic Analysis**  | `solvers/orcaflex/`, `hydrodynamics/diffraction/`           | Production (Core) | **Excellent.** OrcaFlex is the dominant market tool. Our extensive, production-grade wrapper is a core asset.                                    |
| **Hydrodynamic Analysis**    | `hydrodynamics/` (AQWA, Capytaine)                          | Production        | **Strong.** Hydrodynamic analysis is a foundational skill. While mature, the lack of standards mapping is a gap between capability and provability. |
| **Structural/Fatigue**       | `structural/fatigue/`, `structural/pipe_capacity/`          | Production        | **Strong.** Fatigue is a critical niche. Our library of S-N curves is a significant asset. The gap in Efthymiou SCF is a minor weakness.          |
| **Pipeline Engineering**     | `subsea/pipeline/`, `subsea/on_bottom_stability/`         | Stable            | **Good.** Core capabilities for on-bottom stability and capacity are present. Installation and free-span VIV are key gaps for full-scope projects. |
| **Cathodic Protection (CP)** | `cathodic_protection/`                                      | Development       | **Good.** While still in development, this module addresses a specific, valuable niche. It's a strong differentiator.                           |
| **Mooring Analysis**         | `subsea/mooring_analysis/`                                  | Stable            | **Good.** The module covers preliminary design well. The lack of fatigue and optimization capabilities prevents it from being a complete solution.     |
| **Geotechnical Engineering** | `geotechnical/`                                             | Stub              | **Weak.** Foundational skill area where our library is currently weakest. Significant gaps exist in soil models, anchors, and foundations.      |

## 2. Gaps in Market-Demanded Capabilities

Based on the analysis in `ROADMAP.md`, the most significant gaps between our capabilities and market needs are:

1.  **Geotechnical Analysis:** The `geotechnical/` module is a stub. The market requires expertise in soil modeling, anchor design (API RP 2SK), and foundation design. This is the largest single gap.
2.  **Full-Scope Pipeline Analysis:** We lack capabilities for installation analysis and detailed free-span VIV, which are common requirements for pipeline projects.
3.  **Mooring Fatigue & Optimization:** Our `mooring_analysis/` module is good for static design but lacks the fatigue and optimization capabilities needed for life-extension and advanced system design.
4.  **Advanced Structural Assessment:** The `asset_integrity/` module lacks Level 3 FFS, creep, and fire damage assessment, limiting its use to more basic fitness-for-service studies.

## 3. Recommended 6-Month Priorities

To maximize market alignment and GTM impact, development should focus on solidifying our lead in core areas and strategically filling the most valuable gaps. These priorities mirror the Tiers from the technical roadmap, but are framed by their market impact.

### Priority 1: Solidify "Best-in-Class" Narratives

*   **Action:** Complete the **OrcaFlex Subsea Structural Analysis** work remaining (YAML templates, license-free tests, validation).
*   **Market Rationale:** Positions ACE Engineer as the top-tier provider for OrcaFlex automation and advanced subsea analysis, directly targeting the most common high-end skill requirement.

*   **Action:** Advance the **Cathodic Protection Maturity** to include the ABS Guide and complete implementations of existing standards.
*   **Market Rationale:** Creates a defensible, high-value niche. Offering validated, multi-standard CP design automation is a powerful differentiator that competitors cannot easily match.

### Priority 2: Fill High-Value Gaps

*   **Action:** Implement **Mooring Line Fatigue** within the `subsea/mooring_analysis/` module.
*   **Market Rationale:** Mooring fatigue is a common requirement for asset life extension and OPEX reduction projects. This capability directly unlocks a new stream of high-margin analysis work.

*   **Action:** Implement **Efthymiou SCF Parametric Equations** in the `structural/fatigue` module.
*   **Market Rationale:** This closes a known technical gap in an otherwise production-grade module, strengthening our claim to expertise in structural fatigue analysis.

## 4. Alignment with the $120K Retainer GTM Strategy

The `digitalmodel` repository is the engine that powers the ACE Engineer value proposition. The $120K retainer is justified by providing clients with not just consulting hours, but with continuously improving, validated, and market-aligned engineering software assets.

The development priorities above directly feed this GTM narrative:

*   **Demonstrating Value:** By focusing on high-demand skills like OrcaFlex automation and mooring fatigue, we are building tools that solve our clients' most immediate and expensive problems.
*   **Creating "Sticky" Solutions:** When we deliver a project using a `digitalmodel` workflow, the client receives not just a report, but a repeatable, verifiable calculation kernel. The retainer provides them with updates, new features (like new S-N curves), and the ability to re-run analyses as conditions change.
*   **Powering Web Calculators:** The ACE Engineer web calculators are the "front door" to our capabilities. Prioritizing modules with high calculator potential (like Cathodic Protection and Mooring) creates lead-generation assets that directly showcase our deeper expertise, drawing in potential retainer clients.
*   **Justifying the Investment:** The retainer fee is an investment in a shared engineering platform. We can explicitly show clients how their investment is used to build out capabilities on the roadmap that will benefit their future projects. The `ROADMAP.md` becomes a key sales and client-management document.
