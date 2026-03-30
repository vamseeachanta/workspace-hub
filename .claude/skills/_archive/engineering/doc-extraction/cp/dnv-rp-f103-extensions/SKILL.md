---
name: doc-extraction-cp-dnv-rp-f103-extensions
description: 'Sub-skill of doc-extraction-cp: DNV-RP-F103 Extensions.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# DNV-RP-F103 Extensions

## DNV-RP-F103 Extensions


For submarine pipelines, additional extraction targets:

- Pipeline-specific anode types (bracelet, half-shell)
- Soil resistivity effects on anode resistance
- Burial depth correction factors
- Pipeline coating systems (FBE, 3LPE, 3LPP)
- Drain point spacing calculations

**Detection heuristics** for F103 content:
- Keywords: "pipeline", "submarine", "burial", "soil resistivity"
- Document reference: "DNV-RP-F103" or "RP-F103"
- Anode geometry: bracelet dimensions, gap width
