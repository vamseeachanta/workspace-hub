---
name: orcaflex-modeling-domain-expertise
description: 'Sub-skill of orcaflex-modeling: Domain Expertise (+3).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Domain Expertise (+3)

## Domain Expertise


- **Tools**: OrcaFlex, OrcaWave
- **Analysis Types**:
  - Hydrodynamic analysis
  - Mooring system design
  - Riser analysis
  - Installation analysis
  - Fatigue assessment

## Industry Standards


- DNV-ST-F201 (Dynamic Risers)
- API RP 2SK (Stationkeeping)
- ISO 19901-7 (Mooring Systems)

## Critical Production Rules


**NEVER** create mock .sim files or replace production .sim files with test data.

Protected paths (DO NOT MODIFY):
- `*/runtime_test/*.sim`
- `*/production/*.sim`
- Production .sim files are large binary OrcaFlex model files (often GB in size)

## Workflow Automation


- Enhanced specs with auto-update and learning
- Analysis automation with batch processing
- Result extraction and summary generation
