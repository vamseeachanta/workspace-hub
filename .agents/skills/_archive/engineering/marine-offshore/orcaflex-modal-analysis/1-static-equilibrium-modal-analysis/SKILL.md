---
name: orcaflex-modal-analysis-1-static-equilibrium-modal-analysis
description: "Sub-skill of orcaflex-modal-analysis: 1. Static Equilibrium \u2192 Modal\
  \ Analysis."
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Static Equilibrium → Modal Analysis

## 1. Static Equilibrium → Modal Analysis


```
[Load Model] → [Calculate Statics] → [Modal Analysis Specification] → [Extract Modes]
      ↓                                        ↓
  .dat/.yml                              Configure:
                                         - lastMode (number of modes)
                                         - calculateShapes (mode shapes)
                                               ↓
                                     [Mode Details Extraction]
                                               ↓
                                     - Period/Frequency
                                     - Mode shapes (shapeWrtGlobal)
                                     - DOF percentages
```
