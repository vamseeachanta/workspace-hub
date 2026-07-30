---
name: crossprovider codex derived-output-rendering-without-bound-calculati
description: Derived output rendering without bound calculation records diverges silently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [evidence-binding, output-integrity, schema-consistency]
---

When calculation.outputs live in one schema but code independently formats HTML (with unspecified precision rules), the two diverge. Render all numeric prose directly from bound records with explicit precision/rounding fields. Never compute display values in formatting code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
