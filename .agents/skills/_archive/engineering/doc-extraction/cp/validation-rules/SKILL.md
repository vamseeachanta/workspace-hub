---
name: doc-extraction-cp-validation-rules
description: 'Sub-skill of doc-extraction-cp: Validation Rules.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Validation Rules

## Validation Rules


When extracting CP data, validate against known ranges:

| Parameter | Valid range | Flag if outside |
|-----------|------------|----------------|
| f_ci | 0.0 – 1.0 | Error |
| k (degradation rate) | 0.0 – 0.1 1/year | Warning |
| Current density | 0.001 – 1.0 A/m² | Warning |
| Anode capacity (Al) | 1500 – 2500 Ah/kg | Warning |
| Anode capacity (Zn) | 700 – 900 Ah/kg | Warning |
| Protection potential (vs Ag/AgCl) | -1.2 to -0.7 V | Warning |
