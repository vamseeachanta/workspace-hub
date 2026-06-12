---
name: crossprovider hermes demo-cache-must-fall-back-on-missing-intermediat
description: Demo cache must fall back on missing intermediate keys
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [caching, fallback, demo]
---

Legacy cache files may omit intermediate calculation keys (e.g., lifecycle_phases, min_wall_thickness, weight_penalty). Cache-regeneration code must fall back to full recalculation on missing keys, not crash. Ensure code-name constants initialized in both calculation and cache-regen paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
