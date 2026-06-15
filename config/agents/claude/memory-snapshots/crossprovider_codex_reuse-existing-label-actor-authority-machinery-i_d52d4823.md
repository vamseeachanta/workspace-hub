---
name: crossprovider codex reuse-existing-label-actor-authority-machinery-i
description: Reuse existing label-actor-authority machinery instead of rebuilding
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [reuse, architecture, authority, dry]
---

The #2798 completeness gate already implements `_verified_label_event()` (fetch timeline, return actor+timestamp) and `evaluate_close()` decision logic. Generalize and reuse instead of parallel implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
