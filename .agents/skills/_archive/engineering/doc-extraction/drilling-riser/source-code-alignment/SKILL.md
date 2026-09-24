---
name: doc-extraction-drilling-riser-source-code-alignment
description: 'Sub-skill of doc-extraction-drilling-riser: Source Code Alignment.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Source Code Alignment

## Source Code Alignment


Extracted data should align with existing module structures:

| Module | Path | Relevant data |
|--------|------|---------------|
| Riser stack-up | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/typical_riser_stack_up_calculations.py` | Joint dimensions, weights, stack-up sequence |
| VIV analysis skill | `.claude/skills/engineering/marine-offshore/viv-analysis/SKILL.md` | Strouhal number, reduced velocity, mode shapes |
