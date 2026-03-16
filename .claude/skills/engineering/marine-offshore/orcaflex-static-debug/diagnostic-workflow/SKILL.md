---
name: orcaflex-static-debug-diagnostic-workflow
description: 'Sub-skill of orcaflex-static-debug: Diagnostic Workflow.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Diagnostic Workflow

## Diagnostic Workflow


```
[Static Analysis Failed]
         ↓
[1. Check Error Message]
         ↓
[2. Validate Model Structure]
    ├── Connectivity
    ├── Object positions
    └── Line configurations
         ↓
[3. Check Initial Conditions]
    ├── Tensions
    ├── Lengths
    └── Positions
         ↓
[4. Review Environment]
    ├── Water depth
    ├── Current
    └── Waves (should be off for statics)
         ↓
[5. Adjust Solver Settings]
    ├── Damping
    ├── Tolerance
    └── Iteration limits
         ↓
[6. Incremental Testing]
    ├── Simplify model
    ├── Add components one by one
    └── Identify failing element
```
