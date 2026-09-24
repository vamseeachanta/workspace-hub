---
name: crossprovider gemini explicit-not-comparable-vs-silent-defaults-for-m
description: Explicit 'not comparable' vs silent defaults for missing policy inputs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-quality, explicit-handling, design-pattern, policy-inputs]
---

When enrichment requires optional policy inputs, explicitly mark records as 'not comparable' if those inputs are missing rather than applying silent defaults. This prevents silent data degradation and makes the contract explicit to downstream consumers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
