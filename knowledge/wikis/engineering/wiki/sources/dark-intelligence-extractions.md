---
title: "Dark Intelligence Extractions"
tags: [source, dark-intelligence, calculations, xlsx, formulas]
sources:
  - knowledge/dark-intelligence/
added: 2026-04-08
last_updated: 2026-04-08
---

# Dark Intelligence Extractions

Source summary of `knowledge/dark-intelligence/` — engineering calculations extracted from legacy Excel spreadsheets into structured YAML format. These represent institutional knowledge that was previously locked inside opaque spreadsheets with no documentation.

## Overview

| Property | Value |
|----------|-------|
| Directory | `knowledge/dark-intelligence/` |
| xlsx-poc extractions | 6 |
| Geotechnical extractions | 1 |
| Format | YAML with metadata, inputs, methodology, equations, outputs |
| Git status | YAML files are **gitignored** (private knowledge); only README tracked |

## xlsx-poc Extractions (6)

Engineering calculations reverse-engineered from Excel spreadsheets:

| Extraction | Domain | Key Content |
|------------|--------|-------------|
| Wellhead SITP | Drilling | Shut-in tubing pressure calculation |
| Conductor Length | Structural | Required conductor length for soil conditions |
| SN Curves | Fatigue | S-N curve parameters and fatigue life computation |
| C-K Flow Rate | Flow assurance | Choke/kill line flow rate estimation |
| Flowback Calculator | Well testing | Flowback volume and rate prediction |
| Spotfire Formulas | Data visualization | Analytical formulas used in TIBCO Spotfire dashboards |

## Geotechnical Extraction (1)

| Extraction | Domain | Standard | Key Content |
|------------|--------|----------|-------------|
| Pile Capacity Alpha Method | Geotechnical | API RP 2GEO Section 7.3 | Alpha factor, unit skin friction, total axial capacity |

## YAML Entry Format

Each extraction follows this structure:

```yaml
metadata:
  source_file: original_spreadsheet.xlsx
  extraction_date: YYYY-MM-DD
  domain: engineering-subdomain
  standard: applicable-code-or-standard

inputs:
  - name: parameter_name
    symbol: X
    units: m
    range: [min, max]
    description: "What this parameter represents"

methodology:
  description: "Step-by-step calculation approach"
  equations:
    - name: "Equation name"
      formula: "mathematical expression"
      notes: "implementation notes"

outputs:
  - name: result_name
    units: kN
    description: "What this result represents"
```

## Why "Dark Intelligence"

The term reflects that this knowledge was:

1. **Hidden** — buried in Excel cells with no documentation
2. **Fragile** — one wrong cell edit could silently break calculations
3. **Inaccessible** — only usable by someone who knew the spreadsheet intimately
4. **Unversioned** — no history of changes, no review process

Extracting to YAML makes this knowledge explicit, versionable, reviewable, and programmatically accessible.

## Wiki Pages Generated

This source informed the following wiki pages:

- [Pile Capacity — Alpha Method](../concepts/pile-capacity-alpha-method.md)
- [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- [OrcaFlex Solver](../entities/orcaflex-solver.md)
- [AQWA Solver](../entities/aqwa-solver.md)
- [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)

## Cross-References

- **Related source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
- **Related source**: [Methodology Docs Collection](../sources/methodology-docs.md)
