---
name: doc-extraction-drilling-riser
description: 'Layer 3 domain sub-skill for extracting drilling riser data from API
  RP 16Q, DNV-RP-C205, and riser analysis reports. Provides detection heuristics for
  VIV parameters, kill/choke line specs, and BOP stack configurations. type: reference

  '
version: 1.0.0
updated: 2026-03-12
category: engineering
parent_skill: engineering/doc-extraction
triggers:
- riser extraction
- drilling riser data
- BOP extraction
- riser stack-up extraction
- VIV parameter extraction
related_skills:
- doc-extraction
- viv-analysis
- catenary-riser
capabilities:
- viv-parameter-extraction
- bop-configuration-extraction
- kill-choke-line-extraction
- riser-stack-up-extraction
requires: []
tags: []
scripts_exempt: true
type: reference
---

# Doc Extraction Drilling Riser

## When to Use

- Extracting data from API RP 16Q (Marine Drilling Riser Systems)
- Processing riser analysis reports or stack-up calculations
- Ingesting VIV assessment data from riser studies
- Extracting BOP configuration data from well control documents
- Building riser component databases from manufacturer specs

## Related Skills

- [viv-analysis](../../marine-offshore/viv-analysis/SKILL.md) — VIV assessment
- [catenary-riser](../../marine-offshore/catenary-riser/SKILL.md) — Riser configuration
- [structural-analysis](../../marine-offshore/structural-analysis/SKILL.md) — Stress checks

## Sub-Skills

- [Source Code Alignment](source-code-alignment/SKILL.md)
- [VIV Parameters (+3)](viv-parameters/SKILL.md)
- [Validation Rules](validation-rules/SKILL.md)
- [Standards Reference](standards-reference/SKILL.md)
