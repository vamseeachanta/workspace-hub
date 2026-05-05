---
title: "DNV-RP-F101: Corroded Pipelines"
tags: [standard, dnv, pipeline, corrosion, integrity, fitness-for-service]
sources: [dnv-rp-f101]
added: 2026-04-08
last_updated: 2026-04-08
---

# DNV-RP-F101: Corroded Pipelines

**Full title:** DNV-RP-F101 "Corroded Pipelines"

## Scope

Assessment of pipelines with metal loss defects caused by corrosion. Provides methods to determine the remaining pressure capacity of a corroded pipeline, enabling continued operation without immediate repair or replacement.

## Structure

The standard is divided into two parts addressing different loading conditions:

| Part | Loading Condition | Use Case |
|------|-------------------|----------|
| **Part A** | Single defects, internal pressure only | Straight pipe sections under hoop stress |
| **Part B** | Combined loading (pressure + external forces) | Bends, spans, areas with axial/bending loads |

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| **d/t ratio** | Defect depth (d) to wall thickness (t) ratio -- primary measure of severity |
| **Defect length** | Axial extent of the metal loss defect |
| **Pipe grade** | Material specification (e.g., X52, X60, X65) |
| **SMTS** | Specified Minimum Tensile Strength |
| **SMYS** | Specified Minimum Yield Strength |
| **D/t** | Pipe outer diameter to wall thickness ratio |

## Assessment Approach

1. **Characterize the defect** -- measure depth, length, and width from ILI (in-line inspection) or direct assessment
2. **Classify interaction** -- determine if multiple defects interact (using interaction rules based on spacing)
3. **Calculate capacity** -- apply the RP-F101 capacity equation to determine safe operating pressure
4. **Apply safety factors** -- based on inspection confidence level

## Safety Factors by Inspection Confidence

The standard applies different partial safety factors depending on the quality of inspection data:

| Confidence Level | Description | Safety Factor (stricter) |
|-----------------|-------------|--------------------------|
| **Excellent** | Accurate, calibrated ILI tools with validation digs | Lowest factors (least conservatism) |
| **Normal** | Standard ILI with typical measurement uncertainty | Moderate factors |
| **Poor** | Limited data, visual inspection, or old ILI tools | Highest factors (most conservatism) |

Higher inspection confidence reduces unnecessary conservatism and may allow continued operation at higher pressures.

## Interaction with Other Standards

- **API 579-1/ASME FFS-1** provides a more general fitness-for-service framework. RP-F101 is specifically optimized for corrosion-type metal loss in pipelines and is generally less conservative for this defect type.
- **DNV-ST-F101** (Submarine Pipeline Systems) defines the pipeline design basis; RP-F101 addresses in-service degradation.
- **ASME B31G** is an older, more conservative alternative for corrosion assessment.

## Typical Workflow

```
ILI Run Data
    |
    v
Defect Characterization (depth, length, width)
    |
    v
Interaction Screening (group nearby defects)
    |
    v
RP-F101 Capacity Calculation (Part A or Part B)
    |
    v
Compare to MAOP --> Fit for service? --> Yes: Continue operation
                                     --> No: Repair / reduce pressure
```

## Related Pages

- [API 579-1/ASME FFS-1: Fitness-for-Service](api-579-ffs.md) -- general FFS framework covering all defect types
- [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md) -- broader context for integrity management programs

## Cross-References

- **Cross-wiki (marine-engineering)**: [Pipeline Integrity Assessment](../../../marine-engineering/wiki/entities/pipeline-integrity.md) -- shared tags: corrosion, dnv, fitness-for-service, integrity, pipeline; shared keywords: api, asme, assessment, ffs-1, key
- **Cross-wiki (engineering-standards)**: [DNV-RP-F101 Corroded Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f101.md) -- similar slugs (100%); similar titles (76%); shared tags: corrosion, dnv; shared keywords: corroded, cross-references, dnv-rp-f101, full, pipelines; shared entities: DNV, DNV-RP-F101, RP-F101
- **Cross-wiki (engineering-standards)**: [DNV-RP-F105 Free Spanning Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f105.md) -- similar slugs (91%); similar titles (55%); shared tags: dnv; shared entities: DNV, RP-F101
- **Cross-wiki (engineering-standards)**: [DNV-RP-F109 On-bottom Stability of Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f109.md) -- similar slugs (91%); shared tags: dnv; shared entities: DNV, RP-F101
- **Cross-wiki (asset-management)**: [DNV-RP-G101 — Risk-Based Inspection of Offshore Topsides Static Mechanical Equipment](../../../asset-management/wiki/standards/dnv-rp-g101.md) -- similar slugs (91%); shared tags: dnv, standard; shared entities: API, DNV
- **Cross-wiki (engineering-standards)**: [DNV-ST-F101 Submarine Pipeline Systems — bounded summary](../../../engineering-standards/wiki/standards/dnv-st-f101.md) -- similar slugs (82%); similar titles (51%); shared tags: dnv; shared entities: DNV, DNV-ST-F101
- **Cross-wiki (engineering-standards)**: [DNV-RP-B401 Cathodic Protection Design — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-b401.md) -- similar slugs (82%); shared tags: corrosion, dnv; shared entities: DNV
- **Cross-wiki (engineering-standards)**: [DNV-RP-F103 Cathodic Protection of Submarine Pipelines by Galvanic Anodes — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f103.md) -- similar slugs (91%); shared tags: corrosion, dnv; shared keywords: by, cross-references, full, key, other; shared entities: DNV, DNV-RP-F101, DNV-ST-F101
