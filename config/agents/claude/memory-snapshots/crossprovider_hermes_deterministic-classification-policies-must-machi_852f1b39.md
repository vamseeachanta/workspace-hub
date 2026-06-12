---
name: crossprovider hermes deterministic-classification-policies-must-machi
description: Deterministic classification policies must machine-checkable: explicit signals + resolution rules + ranking order + escalation predicates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [policy-design, determinism, configuration]
---

Issue #2282 found policies with prose + fixtures can pass while being ambiguous. Need: signal vocabulary (bounded), bucket rules (declarative match_all/exclude_if), ranking sort-order (explicit section + fields), escalation thresholds (predicate-based, not prose like "materially changed").

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
