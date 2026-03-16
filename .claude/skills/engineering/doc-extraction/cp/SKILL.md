---
name: doc-extraction-cp
description: 'Layer 3 domain sub-skill for extracting cathodic protection data from
  DNV-RP-B401, DNV-RP-F103, and related CP standards. Provides CP-specific detection
  heuristics for anode calculations, coating breakdown factors, current density tables,
  and design life parameters.

  '
version: 1.0.0
updated: 2026-03-12
category: engineering
parent_skill: engineering/doc-extraction
triggers:
- CP extraction
- cathodic protection data
- anode calculation extraction
- coating breakdown extraction
- DNV-RP-B401 extraction
related_skills:
- doc-extraction
- cathodic-protection
capabilities:
- cp-constant-extraction
- anode-formula-extraction
- coating-breakdown-extraction
- current-density-extraction
requires: []
tags: []
scripts_exempt: true
see_also:
- doc-extraction-cp-source-code-alignment
- doc-extraction-cp-anode-formulae
- doc-extraction-cp-dnv-rp-f103-extensions
- doc-extraction-cp-validation-rules
- doc-extraction-cp-standards-reference
---

# Doc Extraction Cp

## When to Use

- Extracting data from DNV-RP-B401 (Cathodic Protection Design)
- Extracting data from DNV-RP-F103 (Cathodic Protection of Submarine Pipelines)
- Processing CP design reports or calculations
- Ingesting anode manufacturer datasheets
- Building CP parameter databases

## Sub-Skills

- [Source Code Alignment](source-code-alignment/SKILL.md)
- [Anode Formulae (+3)](anode-formulae/SKILL.md)
- [DNV-RP-F103 Extensions](dnv-rp-f103-extensions/SKILL.md)
- [Validation Rules](validation-rules/SKILL.md)
- [Standards Reference](standards-reference/SKILL.md)
