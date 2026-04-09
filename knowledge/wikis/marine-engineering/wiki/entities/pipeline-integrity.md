---
title: "Pipeline Integrity Assessment"
tags: [pipeline, integrity, corrosion, fitness-for-service, DNV, API]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# Pipeline Integrity Assessment

Pipeline integrity assessment evaluates the remaining strength of corroded or damaged pipelines
using established engineering frameworks. The two dominant methodologies are DNV RP-F101 and
API 579-1/ASME FFS-1.

## Assessment Frameworks

### DNV RP-F101

- **Part A**: Internal pressure only — single and interacting defects
- **Part B**: Combined loading (pressure + bending + axial force) — uses stress interaction term (h parameter)
- Partial safety factors vary by inspection confidence level (excellent / normal / poor)

### API 579-1 / ASME FFS-1

- **Level 1**: Conservative bounding-box screening — quick assessment
- **Level 2**: Handles complex defect shapes — detailed remaining strength calculation
- **Level 3**: Full FEA-based assessment for irregular geometries

## Key Input Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| d/t ratio | Defect depth as fraction of wall thickness | Must be < 0.80 for SMTS correction |
| Defect length | Axial extent of corrosion | Measured from ILI or direct inspection |
| Pipe grade | Material strength (SMYS, SMTS) | X52 to X80 |
| Operating pressure | MAOP or current operating pressure | Design-specific |
| Corrosion rate | Wall loss rate from inspection history | mm/yr |

## Design Rules

- Always verify d/t ratio < 0.80 before applying SMTS correction
- DNV Part B requires the combined stress interaction term (h parameter)
- Corrosion allowance = design life x corrosion rate (mm/yr)
- API 579 Level 2 handles complex shapes; Level 1 is conservative bounding-box

## Cross-References

- **Related concept**: [[cathodic-protection-system]]
- **Related concept**: [[corrosion-control]]
- **Related entity**: [[anode]]
- **Cross-wiki (engineering)**: [Pipeline Integrity Assessment](../../../engineering/wiki/concepts/pipeline-integrity-assessment.md) — detailed DNV-RP-F101 and API 579 methodology with partial safety factors and practical guidance
