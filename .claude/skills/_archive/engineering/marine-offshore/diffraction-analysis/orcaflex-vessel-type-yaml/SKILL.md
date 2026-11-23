---
name: diffraction-analysis-orcaflex-vessel-type-yaml
description: 'Sub-skill of diffraction-analysis: OrcaFlex Vessel Type YAML (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex Vessel Type YAML (+2)

## OrcaFlex Vessel Type YAML


```yaml
VesselType:
  Name: FPSO
  Category: Vessel
  PrimaryMotion: Calculated (6 DOF)
  RAOOrigin: [0, 0, 0]
  RAOPhaseConvention: AQWA
```

## Coefficient CSV


```csv
Frequency_rad/s,A11,A12,A13,A14,A15,A16,...
0.3,1.0e7,0.0,0.0,0.0,0.0,0.0,...
0.4,1.1e7,0.0,0.0,0.0,0.0,0.0,...
```

## QTF CSV


```csv
Freq1_rad/s,Freq2_rad/s,Heading_deg,Surge_Re,Surge_Im,...
0.3,0.3,0.0,1.2e5,0.0,...
```
