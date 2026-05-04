---
name: doc-extraction-drilling-riser-validation-rules
description: 'Sub-skill of doc-extraction-drilling-riser: Validation Rules.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Validation Rules

## Validation Rules


When extracting drilling riser data, validate against known ranges:

| Parameter | Valid range | Flag if outside |
|-----------|------------|----------------|
| Strouhal number | 0.1 – 0.3 | Warning |
| Riser joint length | 40 – 90 ft | Warning |
| Kill/choke working pressure | 5,000 – 25,000 psi | Warning |
| BOP stack height | 15 – 60 ft | Warning |
| Riser OD | 18 – 24 inches | Warning |
| Water depth for riser | 100 – 12,000 ft | Warning |
