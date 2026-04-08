---
title: "API 579-1/ASME FFS-1: Fitness-for-Service"
tags: [standard, api, asme, fitness-for-service, integrity, assessment]
sources: [api-579-1-asme-ffs-1]
added: 2026-04-08
last_updated: 2026-04-08
---

# API 579-1/ASME FFS-1: Fitness-for-Service

**Full title:** API 579-1/ASME FFS-1 "Fitness-for-Service"

## Scope

A comprehensive fitness-for-service (FFS) assessment standard for pressurized equipment, including pressure vessels, piping, and storage tanks. Provides procedures to evaluate whether equipment with in-service damage can continue to operate safely.

## Assessment Levels

The standard uses a tiered approach, progressing from simple conservative screening to detailed analysis:

| Level | Method | Complexity | Data Required | Conservatism |
|-------|--------|------------|---------------|--------------|
| **Level 1** | Conservative bounding-box screening | Low | Minimal inspection data | High |
| **Level 2** | Handles complex defect shapes and interactions | Medium | Detailed inspection data | Moderate |
| **Level 3** | Detailed FEA-based assessment | High | Full material properties, FE model | Lowest |

### Level 1 -- Screening
Quick pass/fail assessment using simplified equations and conservative assumptions. Can be performed by inspectors in the field. If the component passes Level 1, no further analysis is needed.

### Level 2 -- Detailed Assessment
More accurate calculation methods that account for actual defect geometry, interaction effects, and specific loading. Requires engineering analysis.

### Level 3 -- Advanced Assessment
Finite element analysis (FEA) or other detailed numerical methods. Used when Levels 1 and 2 are insufficient or overly conservative for the specific situation. May include elastic-plastic analysis, fracture mechanics, or creep analysis.

## Damage Mechanisms Covered

| Part | Damage Type | Description |
|------|------------|-------------|
| 4 | **General metal loss** | Uniform corrosion/erosion thinning |
| 5 | **Local thin areas** | Localized metal loss (pitting clusters, groove corrosion) |
| 6 | **Pitting** | Discrete pit-type corrosion |
| 7 | **Blisters and HIC** | Hydrogen-induced cracking and blistering |
| 8 | **Weld misalignment** | Geometric deviations at weld joints |
| 9 | **Crack-like flaws** | Cracks from fatigue, SCC, or fabrication |
| 10 | **Creep damage** | High-temperature service degradation |
| 11 | **Fire damage** | Assessment after fire exposure |
| 12 | **Dent and gouge** | Mechanical damage |
| 13 | **Laminations** | Internal planar separations in plate |

## Assessment Workflow

```
Identify Damage Mechanism
    |
    v
Select Applicable Part (4-13)
    |
    v
Level 1 Screening
    |
    +-- Pass --> Document, continue operation
    |
    +-- Fail --> Level 2 Assessment
                    |
                    +-- Pass --> Document, continue operation
                    |
                    +-- Fail --> Level 3 (FEA)
                                    |
                                    +-- Pass --> Document, set inspection interval
                                    |
                                    +-- Fail --> Repair / replace / de-rate
```

## Relationship to Other Standards

| Standard | Relationship |
|----------|-------------|
| **DNV-RP-F101** | Pipeline-specific corrosion assessment; more optimized for metal loss in pipelines |
| **ASME B31.3/B31.4/B31.8** | Design codes that API 579 references for allowable stresses |
| **BS 7910** | British standard for fracture assessment; overlaps with Part 9 (crack-like flaws) |
| **ASME PCC-2** | Repair methods that may be applied after an FFS assessment identifies needed action |

## Key Considerations

- **Remaining life estimation:** API 579 assessments can be combined with corrosion rate data to estimate remaining service life and set inspection intervals.
- **Material properties:** Level 3 assessments require actual material properties (not just minimum specified values). Material testing may be needed.
- **Multiple damage mechanisms:** When multiple damage types coexist, assess each separately and consider interaction effects.

## Related Pages

- [DNV-RP-F101: Corroded Pipelines](dnv-rp-f101.md) -- specialized pipeline corrosion assessment
- [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md) -- broader integrity management context
