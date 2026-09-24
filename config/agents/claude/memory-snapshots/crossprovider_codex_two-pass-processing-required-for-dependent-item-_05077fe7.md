---
name: crossprovider codex two-pass-processing-required-for-dependent-item-
description: Two-pass processing required for dependent item generation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-generation, algorithm, dependency-resolution]
---

When generating items with inter-item dependencies (e.g., child WRKs that depend on each other), a single pass through the input cannot resolve symbolic references to newly allocated IDs. Implement as: pass 1 = allocate IDs and build symbol map, pass 2 = resolve symbolic references using the map.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
