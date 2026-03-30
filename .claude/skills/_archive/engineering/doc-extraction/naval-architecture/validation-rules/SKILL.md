---
name: doc-extraction-naval-architecture-validation-rules
description: 'Sub-skill of doc-extraction-naval-architecture: Validation Rules.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Validation Rules

## Validation Rules


When extracting naval architecture data, validate against known ranges:

| Parameter | Valid range | Flag if outside |
|-----------|------------|----------------|
| GM (transverse) | 0.05 – 10.0 m | Warning |
| Cb (block coefficient) | 0.30 – 0.90 | Warning |
| Cp (prismatic) | 0.50 – 0.85 | Warning |
| Cm (midship) | 0.80 – 1.00 | Warning |
| Cwp (waterplane) | 0.60 – 0.95 | Warning |
| GZ_max | 0.05 – 5.0 m | Warning |
| Shell plate thickness | 4 – 50 mm | Warning |
| Frame spacing | 400 – 1000 mm | Warning |
| Froude number (displacement) | 0.0 – 0.5 | Warning |

Note: ranges are non-normative screening heuristics for extraction QA only.
