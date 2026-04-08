---
title: "Career Learnings Seed"
tags: [source, career, expertise, knowledge-seed]
sources:
  - knowledge/seeds/career-learnings.yaml
added: 2026-04-08
last_updated: 2026-04-08
---

# Career Learnings Seed

Source summary of `knowledge/seeds/career-learnings.yaml` — a curated seed file capturing 23 years of engineering expertise across multiple domains.

## Overview

| Property | Value |
|----------|-------|
| File | `knowledge/seeds/career-learnings.yaml` |
| Entries | 11 |
| Format | YAML with structured fields |
| Coverage | 23 years of professional experience |

## Entry Format

Each entry in the seed file follows this structure:

```yaml
- id: unique-identifier
  type: expertise | lesson | pattern
  category: offshore-engineering | software | finance | drilling | energy
  subcategory: specific-subdomain
  title: "Short descriptive title"
  context: "Background and when this applies"
  patterns:
    - "Key pattern or rule 1"
    - "Key pattern or rule 2"
  follow_ons:
    - "Related topic to explore"
    - "Connected knowledge area"
```

## Categories Breakdown

| Category | Count | Subcategories |
|----------|-------|---------------|
| Offshore Engineering | 5 | Pipeline integrity, VIV, FEA, cathodic protection, CFD |
| Software | 3 | Shell scripting, Python, JSONL data formats |
| Finance | 1 | Real estate investment analysis |
| Drilling | 1 | AI-assisted DWOP (Drill Well On Paper) |
| Energy | 1 | Energy economics and transition |

## Key Topics Covered

### Offshore Engineering (5 entries)
- **Pipeline integrity**: Inspection, corrosion assessment, remaining life estimation
- **VIV (Vortex-Induced Vibration)**: Riser and pipeline fatigue from current-induced oscillation
- **FEA (Finite Element Analysis)**: Structural analysis patterns for subsea equipment
- **Cathodic protection**: Anode design, CP survey interpretation, protection life
- **CFD (Computational Fluid Dynamics)**: Hydrodynamic loading, VIV suppression device modeling

### Software (3 entries)
- **Shell scripting**: Automation patterns for engineering workflows
- **Python**: Scientific computing, OrcFxAPI integration, data processing
- **JSONL**: Structured data formats for engineering calculations and logging

### Other Domains (3 entries)
- **Real estate finance**: Investment analysis, cash flow modeling
- **AI DWOP**: AI-assisted drilling planning and optimization
- **Energy economics**: Economic modeling for energy systems and transitions

## Wiki Pages Generated

This seed file informed the following wiki pages:

- [OrcaFlex Solver](../entities/orcaflex-solver.md) — VIV and riser fatigue context
- [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md) — fatigue analysis fundamentals
- [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md) — cross-solver debugging experience
- [Parametric Engineering Reports](../workflows/parametric-engineering-reports.md) — automation pipeline

## Cross-References

- **Related source**: [Dark Intelligence Extractions](../sources/dark-intelligence-extractions.md)
- **Related source**: [Methodology Docs Collection](../sources/methodology-docs.md)
