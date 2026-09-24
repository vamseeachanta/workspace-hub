---
name: crossprovider codex normalize-tokens-consistently-in-category-alias-
description: Normalize tokens consistently in category/alias detectors to avoid false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [normalization, pattern-matching, false-positives]
---

Alias drift detectors can emit false positives when categories use slashes (e.g., `business/admin`) and are matched against top-level path prefixes (e.g., `business/tax`). Fix: only add raw values to the working set if their normalized form is in the alias family token set. Single canonical spelling is healthy; emit drift only when multiple different spellings of the same canonical form coexist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
