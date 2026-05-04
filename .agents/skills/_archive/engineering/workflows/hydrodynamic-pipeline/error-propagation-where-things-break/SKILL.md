---
name: hydrodynamic-pipeline-error-propagation-where-things-break
description: 'Sub-skill of hydrodynamic-pipeline: Error Propagation: Where Things
  Break.'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Error Propagation: Where Things Break

## Error Propagation: Where Things Break


| Stage | Common Failure | Propagation Effect | Detection |
|-------|---------------|-------------------|-----------|
| **Mesh** | Panel normals reversed | All forces inverted in diffraction | Heave RAO → -1.0 at long period |
| **Mesh** | Panel size too large | Missing high-frequency response | RAOs truncated above mesh cutoff |
| **Mesh** | Waterline not closed | Infinite hydrostatic forces | Diffraction solver diverges |
| **Diffraction** | Wrong heading convention | RAO phases off by 180 deg | Vessel moves opposite to waves |
| **Diffraction** | No viscous damping | Unrealistic resonance peaks | Roll RAO > 50 at natural period |
| **OrcaFlex import** | Coordinate system mismatch | Forces applied at wrong location | Vessel spins or drifts wrong way |
| **OrcaFlex** | Missing QTF data | No slow-drift motion | Mean offset too small |
