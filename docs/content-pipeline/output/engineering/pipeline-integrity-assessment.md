---
title: "Pipeline Integrity Assessment"
description: "Assessment of corroded or damaged pipelines to determine remaining safe operating life. Two dominant frameworks: DNV RP-F101 (offshore/subsea pipelines) and..."
keywords: "pipeline, integrity, dnv-rp-f101, api-579, corrosion, fitness-for-service"
author: "ACE Engineer"
url: "/knowledge/engineering/pipeline-integrity-assessment"
canonical: "https://aceengineer.com/knowledge/engineering/pipeline-integrity-assessment"
domain: "engineering"
---

# Pipeline Integrity Assessment

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

Assessment of corroded or damaged pipelines to determine remaining safe operating life. Two dominant frameworks: DNV RP-F101 (offshore/subsea pipelines) and API 579-1/ASME FFS-1 (general pressure equipment fitness-for-service). Both translate inspection data into accept/repair/replace decisions.

## Frameworks

### DNV RP-F101 — Corroded Pipelines

DNV RP-F101 is the industry-standard method for assessing corrosion defects in offshore pipelines. It consists of two parts:

| Part | Scope | When to Use |
|------|-------|-------------|
| **Part A** | Single defect under internal pressure only | Most common assessment — isolated metal loss, pressure-only loading |
| **Part B** | Combined loading (pressure + longitudinal stress + bending) | Risers, spans, expansion loops, or any section with significant bending/axial loads |

Part A calculates a reduced pressure capacity based on the defect geometry (depth and length) relative to pipe wall thickness and diameter. Part B introduces the stress interaction parameter **h**, which accounts for the combined effect of hoop stress and longitudinal stress. This is critical at riser bends, free spans, and locations near supports where bending moments are significant.

**Partial safety factors** depend on inspection confidence:

| Inspection Quality | Depth Factor (εd) | Length Factor (εl) | Typical Method |
|--------------------|--------------------|--------------------|----------------|
| Excellent | Low | Low | Caliper pig with calibration |
| Normal | Medium | Medium | MFL pig |
| Poor | High | High | External UT with limited coverage |

### API 579-1 / ASME FFS-1 — Fitness-for-Service

API 579 is a broader framework covering general metal loss, local thin areas, pitting, blisters, weld misalignment, crack-like flaws, and creep damage. It applies to pressure vessels, piping, and tanks — not limited to pipelines.

| Level | Complexity | Inputs Required |
|-------|-----------|-----------------|
| **Level 1** | Screening — simplified charts | Defect dimensions, original design data |
| **Level 2** | Detailed — complex defect shapes, interaction rules | Detailed thickness profiles, material properties |
| **Level 3** | FEA-based — nonlinear analysis | Full 3D model, stress-strain curves, fracture toughness |

Level 2 is most commonly used for pipeline integrity because it handles interacting defects and irregular shapes without requiring full FEA.

## Key Inputs

Every assessment requires these inputs regardless of framework:

- **Defect depth** (d) and **wall thickness** (t) — expressed as d/t ratio
- **Defect length** along the pipe axis
- **Pipe grade** — API 5L grades X42 through X80 (yield strength 290–555 MPa)
- **Operating pressure** and **design pressure**
- **Corrosion rate** (mm/yr) from repeat inspections or CP survey data
- **Pipe diameter** and **wall thickness** (original nominal)

## Key Patterns

1. **d/t threshold**: always verify d/t < 0.80 before applying the SMTS (Specified Minimum Tensile Strength) correction in DNV RP-F101. Beyond 0.80, the remaining ligament is too thin for reliable assessment — the defect should be repaired.

2. **Combined loading (Part B)**: the interaction parameter h couples hoop and longitudinal stress. Ignoring this at riser bends or free spans is non-conservative and has led to integrity failures.

3. **Corrosion allowance**: remaining life = (t_nominal - t_measured - t_min_required) / corrosion_rate. This is the simplest and most important calculation in pipeline integrity.

4. **Interacting defects**: defects within a specified longitudinal and circumferential spacing must be grouped and assessed as a single combined defect. DNV and API 579 have different interaction rules — check which standard governs.

5. **API 579 Level 2 for complex shapes**: when a defect is irregular (not a simple rectangular approximation), Level 2 uses the "effective area" method with a more accurate representation of the remaining thickness profile.

## Practical Guidance

- Always start with the **as-measured** wall thickness from ILI (in-line inspection) data, not nominal. Nominal thickness includes manufacturing tolerance and corrosion allowance that may already be consumed.
- When comparing repeat ILI runs, ensure the tools are compatible (MFL vs. UT) and that the same clock position and distance references are used. Apparent "growth" can be measurement artifact.
- For deepwater pipelines with high D/t ratios, external pressure collapse may govern before burst — check DNV-OS-F101 (now DNV-ST-F101) collapse criteria separately.
- Document the assessment trail: inspection report → defect list → assessment method → acceptance criteria → remaining life estimate. Regulators expect this chain.

## Cross-References

- **Related concept**: fea-structural-analysis — Level 3 FFS assessments require FEA
- **Related concept**: cathodic-protection-design — CP effectiveness directly affects corrosion rate
- **Related concept**: cfd-offshore-hydrodynamics — scour and hydrodynamic loads on pipeline spans
- **Cross-wiki (marine-engineering)**: Corrosion Control — corrosion control strategies that determine pipeline degradation rate
- **Cross-wiki (marine-engineering)**: Sour Service — H2S-induced cracking (SSC, HIC) as a pipeline integrity threat beyond metal loss
- **Cross-wiki (maritime-law)**: Environmental Liability — pipeline failure leading to spills triggers strict liability under CLC/OPA 90
- **Source**: Career Learnings Seed

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

