---
name: fe-analyst-13-common-fea-mistakes-and-remedies
description: 'Sub-skill of fe-analyst: 13. Common FEA Mistakes and Remedies.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 13. Common FEA Mistakes and Remedies

## 13. Common FEA Mistakes and Remedies


| Mistake | Symptom | Remedy |
|---|---|---|
| Too-coarse mesh at TDP | Curvature under-predicted | Refine to ≤ 0.5×OD near TDP |
| Adjacent segment ratio > 3 | Spurious oscillations | Grade mesh gradually |
| Missing ramp in dynamics | Non-physical transients in results | Add 1–2×Tp ramp; exclude from stats |
| Seabed stiffness too high | Divergence / oscillation at TDP | Use kn = 50–200 kN/m/m typically |
| Missing Cm (added mass) | Under-estimated natural period | Ca = 1.0 for circular sections |
| Static only (no dynamics) | Misses resonance effects | Always run dynamic for wave analysis |
| Compression not checked | Upheaval buckling risk missed | Check min(Te) > 0 at all nodes |
| No content weight | Unconservative sag bend tension | Include internal fluid density |
| Wrong sign convention for z | Results appear inverted | Confirm OrcaFlex z-positive-up convention |
