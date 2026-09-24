---
name: crossprovider codex human-gates-use-stage-specific-artifact-predicat
description: Human gates use stage-specific artifact predicates, not generic signals
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-design, predicate-specificity, lifecycle-gates]
---

Gate 5→6 blocks on 'decision: approved' field in user-review-plan-draft.yaml; Gate 7→8 blocks on 'confirmed_by:' at line-start in lifecycle HTML; Gate 17→18 blocks on 'decision: approved' in user-review-close.yaml. Each gate references a different artifact type with different field names — no single predicate applies. Verifier must know gate→artifact→field mapping explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
