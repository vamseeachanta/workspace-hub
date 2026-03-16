---
name: orcaflex-file-conversion-orcaflex-file-types
description: 'Sub-skill of orcaflex-file-conversion: OrcaFlex File Types (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex File Types (+1)

## OrcaFlex File Types


| Format | Type | Description | Use Case |
|--------|------|-------------|----------|
| **.dat** | Binary | Compressed binary model data | OrcaFlex native format (fast loading) |
| **.yml** | ASCII | YAML text representation | Human-readable, version control, automation |
| **.sim** | Binary | Simulation results + model | Post-processing, result analysis |

## Conversion Capabilities


```
.dat  ⟷  .yml   (Bidirectional)
.sim  →  .dat   (Extract model from simulation)
.sim  →  .yml   (Extract model as YAML)
```
