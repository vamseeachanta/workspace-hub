---
name: crossprovider gemini parametric-sweeps-must-materialize-engine-output
description: Parametric sweeps must materialize engine outputs, not just metadata
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [parametric-studies, solver-integration, defect-class]
---

Parametric study systems that generate case configurations but skip actual engine execution produce no tangible results despite appearing functional. Parameter variations must flow through to solver execution (OrcaFlex campaign, fatigue analysis, wall-thickness checks) and produce reports/metrics; storing parameter metadata alone masks a silent failure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
