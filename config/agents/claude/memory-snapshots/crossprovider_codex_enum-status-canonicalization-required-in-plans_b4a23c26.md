---
name: crossprovider codex enum-status-canonicalization-required-in-plans
description: Enum/status canonicalization required in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, correctness, contracts]
---

When a plan defines multiple state values (e.g., gap, covered, domain-mismatch), contradictions across sections block approval. Plans must define one canonical enum and verify all sections reference it consistently. Failure to do so makes implementation ambiguous and acceptance criteria non-verifiable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
