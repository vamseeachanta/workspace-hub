---
name: crossprovider codex memory-verification-treat-as-hypothesis-against-
description: Memory verification: treat as hypothesis against live state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [memory-management, verification, process]
---

Existing memory records are working hypotheses, not ground truth. Always verify live repository state—issue status via `gh issue view`, file existence, generated artifact dates—before making decisions. Memory decays fast; current state takes precedence in conflicts. Document contradictions; update or remove stale records.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
