---
name: doc-extraction-naval-architecture
description: 'Layer 3 domain sub-skill for extracting naval architecture data from
  SNAME PNA, IMO stability codes, IACS structural rules, and classification society
  guidelines. Provides detection heuristics for stability constants, resistance equations,
  hull form coefficients, hydrostatic curves, IMO stability criteria, and structural
  scantling tables.

  '
version: 1.0.0
updated: 2026-03-13
category: engineering
parent_skill: engineering/doc-extraction
triggers:
- naval architecture extraction
- stability data extraction
- hull form extraction
- resistance equation extraction
- hydrostatic extraction
- scantling extraction
- IMO criteria extraction
related_skills:
- doc-extraction
- hydrodynamics
- structural-analysis
capabilities:
- stability-constant-extraction
- resistance-equation-extraction
- hull-form-coefficient-extraction
- hydrostatic-curve-extraction
- imo-criteria-extraction
- scantling-table-extraction
requires: []
tags: []
scripts_exempt: true
see_also:
- doc-extraction-naval-architecture-source-code-alignment
- doc-extraction-naval-architecture-stability-constants
- doc-extraction-naval-architecture-structural-scantling-tables
- doc-extraction-naval-architecture-validation-rules
- doc-extraction-naval-architecture-standards-reference
---

# Doc Extraction Naval Architecture

## When to Use

- Extracting data from SNAME Principles of Naval Architecture (PNA)
- Processing IMO intact stability criteria (IS Code, SOLAS Ch. II-1)
- Ingesting classification society structural rules (ABS, DNV, LR, BV)
- Extracting resistance estimation data (Holtrop-Mennen, ITTC)
- Building hull form parameter databases from general arrangement plans
- Processing hydrostatic curves from stability booklets and design documents

## Related Skills

- [hydrodynamics](../../marine-offshore/hydrodynamics/SKILL.md) — Wave spectra, RAO
- [structural-analysis](../../marine-offshore/structural-analysis/SKILL.md) — Stress checks
- [fatigue-analysis](../../marine-offshore/fatigue-analysis/SKILL.md) — S-N curves

## Sub-Skills

- [Source Code Alignment](source-code-alignment/SKILL.md)
- [Stability Constants (+4)](stability-constants/SKILL.md)
- [Structural Scantling Tables](structural-scantling-tables/SKILL.md)
- [Validation Rules](validation-rules/SKILL.md)
- [Standards Reference](standards-reference/SKILL.md)
