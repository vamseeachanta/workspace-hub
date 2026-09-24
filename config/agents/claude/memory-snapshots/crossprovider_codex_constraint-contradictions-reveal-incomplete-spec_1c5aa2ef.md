---
name: crossprovider codex constraint-contradictions-reveal-incomplete-spec
description: Constraint contradictions reveal incomplete specs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [spec-gaps, privacy, governance, plan-review]
---

Plans that forbid X (e.g., storing exact labels) while requiring Y (e.g., validating against exact source) create a logical gap. This signals an incomplete spec. Solution often involves a non-reversible proxy like keyed HMAC with external key, fail-closed key validation, and synthetic-label-only tests. Use contradiction as a diagnostic flag.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
