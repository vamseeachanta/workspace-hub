---
name: crossprovider gemini multi-domain-parametric-study-coordination-patte
description: Multi-domain parametric study coordination pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [parametric-studies, orchestration, dataclass-validation]
---

When orchestrating sweeps across multiple engineering domains (wall-thickness, fatigue, solvers), use an enum-based study type selector with per-domain parameter dataclasses that validate their own inputs at `__post_init__`. A single coordinator entry-point dispatches to domain-specific engines and aggregates results.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
