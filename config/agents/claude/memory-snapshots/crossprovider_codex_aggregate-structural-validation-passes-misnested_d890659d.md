---
name: crossprovider codex aggregate-structural-validation-passes-misnested
description: Aggregate structural validation passes misnested violations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, validation, structure, parity-checks]
---

Tests that verify HTML tag balance (e.g., `<body>` open/close counts match) pass tags that are misnested, out-of-order, or missing entirely. Maintain an ordered stack for mandatory elements or explicitly parse and assert presence/order; aggregate counts alone do not guarantee structural correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
