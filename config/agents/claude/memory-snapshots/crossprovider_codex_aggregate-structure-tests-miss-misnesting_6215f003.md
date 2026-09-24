---
name: crossprovider codex aggregate-structure-tests-miss-misnesting
description: Aggregate structure tests miss misnesting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [html-validation, testing, schema-verification]
---

Tests verifying structure by counting opening/closing tags (e.g., checking `<body>`, `<main>`, `<section>` balance) can pass on misnested or out-of-order elements. Maintain a tag stack and validate close order; counting alone is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
