---
name: crossprovider hermes provider-urgency-scoring-requires-multi-factor-w
description: Provider urgency scoring requires multi-factor weighted formula
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-operations, weighted-scoring, decision-framework]
---

Single metrics (utilization, debt volume) hide actionability. Use weighted scoring: min(40, 3.0*debt_per_1k) + min(20, debt_reads/50) + min(20, recent_activity) + (8 if corpus_drift) + (min(10, missing_reads/2) if zero_mapped_debt) + python_hygiene_bonus. Sort by descending urgency score; prioritize active-debt cleanup first, then route overflow to idle-clean providers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
