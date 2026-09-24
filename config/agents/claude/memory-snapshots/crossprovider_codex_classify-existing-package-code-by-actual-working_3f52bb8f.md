---
name: crossprovider codex classify-existing-package-code-by-actual-working
description: Classify existing package code by actual working state, not advertisement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, resource-intelligence, code-inventory]
---

In resource intelligence, treat advertised features as claims to verify, not guaranteed baseline capabilities. When a package advertises a provider or module but the import fails or implementation is incomplete, classify it as broken/unproven and inventory actual working implementations separately. Example: worldenergydata-landman advertises county_records provider but imports a nonexistent module.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
