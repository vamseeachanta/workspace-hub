---
name: orcaflex-installation-analysis-installation-sequence-workflow
description: 'Sub-skill of orcaflex-installation-analysis: Installation Sequence Workflow.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Installation Sequence Workflow

## Installation Sequence Workflow


```
[Reference Model] → [Define Delta Elevations] → [Generate Depth Models]
        ↓                    ↓                           ↓
   Base geometry      [-10m, -20m, -30m, ...]    Model per depth:
   at datum                                       - Update structure Z
                                                  - Update buoy Z
                                                  - Extend crane wire
                                                  - Update sling connections
                                                           ↓
                                               [Orientation Variants]
                                                           ↓
                                               [Batch Simulation]
```
