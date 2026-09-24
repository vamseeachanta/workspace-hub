---
name: crossprovider gemini function-parameters-must-not-be-shadowed-by-hard
description: Function parameters must not be shadowed by hardcoded paths
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pseudocode, testing, parameter-coupling]
---

Pseudocode `walk([hardcoded_paths])` instead of `walk(signal_roots)` causes test failures because fixtures pass a different root but are ignored. Parameters must actually be used, not shadowed by hard-coded equivalents.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
