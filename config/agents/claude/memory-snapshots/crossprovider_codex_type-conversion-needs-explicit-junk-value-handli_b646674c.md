---
name: crossprovider codex type-conversion-needs-explicit-junk-value-handli
description: Type conversion needs explicit junk-value handling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, data-validation, robustness]
---

Unsafe _opt_float/_opt_int that don't catch ValueError/TypeError on unparseable strings crash silently on scraped data. Catching both exceptions separately and returning None is the durable pattern for real-world scraped/user data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
