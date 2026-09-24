---
name: crossprovider codex aliases-on-combined-field-factors-cause-silent-m
description: Aliases on combined-field factors cause silent misclassification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [registry, aliases, test-coverage, worldenergydata]
---

When a registry combines multiple fields into a single conversion factor (e.g., Montanazo-Lubina), aliasing individual field names to that combined factor makes separate-field lookups silently use the wrong factor. Tests must separately verify combined-key and individual-key lookups fail or use only the combined key.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
