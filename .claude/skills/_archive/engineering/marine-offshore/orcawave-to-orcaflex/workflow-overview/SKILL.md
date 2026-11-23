---
name: orcawave-to-orcaflex-workflow-overview
description: 'Sub-skill of orcawave-to-orcaflex: Workflow Overview.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Workflow Overview

## Workflow Overview


```
OrcaWave Analysis              OrcaFlex Model
┌──────────────────┐          ┌──────────────────┐
│ Panel mesh       │          │ Vessel object    │
│ Diffraction/     │    →     │ Vessel type      │
│ Radiation        │          │ - RAOs           │
│ QTF (optional)   │          │ - Added mass     │
└──────────────────┘          │ - Damping        │
                              │ - QTF (optional) │
                              └──────────────────┘
```
