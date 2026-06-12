---
name: crossprovider hermes orphaned-inventory-targets-accumulate
description: Orphaned inventory targets accumulate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [maintainability, technical-debt, architecture]
---

Dead/unused rows in fixtures (e.g., target used only for existence assertion, not actual routing) drift over releases. Every fixture target should either be routed by data or explicitly marked deprecated/deprecated-since-version.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
