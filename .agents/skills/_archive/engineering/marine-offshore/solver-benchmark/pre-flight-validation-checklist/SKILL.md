---
name: solver-benchmark-pre-flight-validation-checklist
description: 'Sub-skill of solver-benchmark: Pre-Flight Validation Checklist.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Pre-Flight Validation Checklist

## Pre-Flight Validation Checklist


Before running a benchmark, verify ALL of these:

```
[ ] Mesh quality: panels roughly square (aspect ratio < 2:1)
[ ] Mesh density: sufficient panels (700+ for 100m barge)
[ ] All solvers use identical:
    [ ] Frequency range (rad/s)
    [ ] Wave headings (degrees)
    [ ] Water depth
    [ ] Mass properties
    [ ] Centre of gravity
[ ] OrcaWave YAML: QTF settings NOT set when QTF disabled
[ ] AQWA DAT: Elements use QPPL DIFF keyword
[ ] AQWA DAT: ILID AUTO card present after ZLWL
[ ] AQWA DAT: SEAG card has 2 params (non-Workbench mode)
[ ] AQWA DAT: All lines under 80 columns
[ ] Unit consistency:
    [ ] Frequencies in rad/s (not Hz)
    [ ] Rotational RAOs in deg/m (not rad/m)
    [ ] Phases in consistent convention
```
