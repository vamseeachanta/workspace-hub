---
name: orcaflex-model-generator-pipeline-builders-order-10-50
description: 'Sub-skill of orcaflex-model-generator: Pipeline Builders (order 10-50)
  (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Pipeline Builders (order 10-50) (+2)

## Pipeline Builders (order 10-50)


| Builder | File | Order | Purpose |
|---------|------|-------|---------|
| GeneralBuilder | `01_general.yml` | 10 | Simulation settings |
| EnvironmentBuilder | `03_environment.yml` | 30 | Water, waves, current, wind |
| VesselTypeBuilder | `04_vessel_types.yml` | 31 | Vessel type definitions |
| LineTypeBuilder | `05_line_types.yml` | 32 | Line type properties |
| ... | ... | ... | ... |


## Riser Builders (order 40-93)


| Builder | File | Order | Condition |
|---------|------|-------|-----------|
| RiserLineTypeBuilder | `06_riser_line_types.yml` | 40 | `spec.is_riser()` |
| RiserVesselBuilder | `06_riser_vessels.yml` | 42 | `spec.is_riser()` |
| RiserClumpTypeBuilder | `06_riser_clump_types.yml` | 50 | `spec.is_riser()` |
| RiserLinesBuilder | `06_riser_lines.yml` | 92 | `spec.is_riser()` |
| RiserLinksBuilder | `06_riser_links.yml` | 93 | `spec.is_riser()` |


## Generic Builder (order 200)


| Builder | File | Order | Condition |
|---------|------|-------|-----------|
| GenericModelBuilder | `20_generic_objects.yml` | 200 | `spec.is_generic()` |

The generic builder handles ALL OrcaFlex object types via schema-driven generation:
- List sections (LineTypes, Vessels, Lines, Shapes, 6DBuoys, etc.)
- Singleton sections (FrictionCoefficients, LineContactData, Groups, etc.)
- VariableData (nested by category)
- General properties overlay
