---
name: viv-analysis-1-natural-frequency-analysis
description: 'Sub-skill of viv-analysis: 1. Natural Frequency Analysis (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Natural Frequency Analysis (+3)

## 1. Natural Frequency Analysis


Calculate natural frequencies for tubular members.

```yaml
viv_analysis:
  natural_frequency:
    flag: true
    member:
      length: 50.0
      outer_diameter: 0.5
      wall_thickness: 0.025

*See sub-skills for full details.*

## 2. Vortex Shedding Assessment


Evaluate vortex shedding frequencies against natural frequencies.

```yaml
viv_analysis:
  vortex_shedding:
    flag: true
    member:
      outer_diameter: 0.5
      length: 50.0
    current_profile:

*See sub-skills for full details.*

## 3. VIV Susceptibility Screening


Quick screening for VIV susceptibility.

```yaml
viv_analysis:
  screening:
    flag: true
    members:
      - name: "Riser1"
        outer_diameter: 0.273
        length: 1500.0

*See sub-skills for full details.*

## 4. Tubular Member VIV Analysis


Complete VIV analysis for tubular members per design codes.

```yaml
viv_analysis:
  tubular_members:
    flag: true
    members:
      - name: "Brace1"
        geometry:
          outer_diameter: 0.324

*See sub-skills for full details.*
