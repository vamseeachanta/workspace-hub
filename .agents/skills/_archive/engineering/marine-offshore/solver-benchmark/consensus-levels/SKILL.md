---
name: solver-benchmark-consensus-levels
description: 'Sub-skill of solver-benchmark: Consensus Levels.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Consensus Levels

## Consensus Levels


The benchmark framework classifies solver agreement:

| Level | Description | Criteria |
|-------|-------------|----------|
| **FULL** | All solvers agree | All pairs: correlation > 0.99, RMS < tolerance |
| **MAJORITY** | 2 of 3 agree | 2+ pairs meet criteria |
| **SPLIT** | Partial agreement | 1 pair meets criteria |
| **NO_CONSENSUS** | No agreement | No pairs meet criteria |
