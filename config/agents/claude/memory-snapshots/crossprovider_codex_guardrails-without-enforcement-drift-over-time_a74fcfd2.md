---
name: crossprovider codex guardrails-without-enforcement-drift-over-time
description: Guardrails without enforcement drift over time
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [code-quality, testing, governance]
---

Documented style limits (file line counts, function lengths) are not automatically enforced and creep over guardrails without active test coverage. Add parametric tests that fail if artifacts exceed stated limits, not just human review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
