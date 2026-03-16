---
name: work-queue-canonical-20-stage-lifecycle
description: 'Sub-skill of work-queue: Canonical 20-Stage Lifecycle.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Canonical 20-Stage Lifecycle

## Canonical 20-Stage Lifecycle


```
1  Capture              2  Resource Intelligence   3  Triage
4  Plan Draft (4a: Ideation via EnterPlanMode → 4b: Artifact write)
5  User Review Plan Draft  6  Cross-Review
7  User Review Plan Final  8  Claim/Activation     9  Work-Queue Routing
10 Work Execution       11 Artifact Generation     12 TDD / Eval
13 Agent Cross-Review   14 Verify Gate Evidence    15 Future Work Synthesis
16 Resource Intelligence Update  17 User Review Implementation
18 Reclaim              19 Close                   20 Archive
```

Full stage contracts and gate policy: `scripts/work-queue/stages/stage-NN-*.yaml`
Gate evidence verifier: `scripts/work-queue/verify-gate-evidence.py WRK-NNN`
