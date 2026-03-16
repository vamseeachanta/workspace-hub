---
name: bemrosetta-parsing
description: 'Sub-skill of bemrosetta: Parsing (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Parsing (+3)

## Parsing


- Parse AQWA .LIS files extracting RAOs, added mass, damping
- Parse QTF files for second-order wave forces
- Extract solver metadata (version, water depth, frequencies, headings)

## Conversion


- Convert to OrcaFlex vessel type YAML
- Export coefficient CSV files
- Export QTF data in OrcaFlex format

## Mesh Processing


- Read/write WAMIT GDF format
- Read/write AQWA/NEMOH DAT format
- Read/write STL format (ASCII and binary)
- Calculate mesh quality metrics

## Validation


- Coefficient symmetry checks
- Positive definiteness verification
- Physical limits validation
- Kramers-Kronig causality checking
