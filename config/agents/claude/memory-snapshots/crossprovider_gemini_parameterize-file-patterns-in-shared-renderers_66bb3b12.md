---
name: crossprovider gemini parameterize-file-patterns-in-shared-renderers
description: Parameterize file patterns in shared renderers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [rendering, parameterization, architecture]
---

Reusing rendering logic across stages requires parameterized file glob patterns instead of hardcoded conventions. Hardcoding breaks when the same renderer must match different file naming schemes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
