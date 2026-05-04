---
name: diffraction-analysis-diffractionresults-structure
description: 'Sub-skill of diffraction-analysis: DiffractionResults Structure.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# DiffractionResults Structure

## DiffractionResults Structure


```
DiffractionResults
├── vessel_name: str
├── frequencies: FrequencyData
├── headings: HeadingData
├── raos: RAOSet
│   ├── surge: RAOComponent (magnitude, phase)
│   ├── sway: RAOComponent
│   ├── heave: RAOComponent
│   ├── roll: RAOComponent

*See sub-skills for full details.*
