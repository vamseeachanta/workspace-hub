---
name: crossprovider codex missing-repo-local-tooling-can-silently-block-cl
description: Missing repo-local tooling can silently block closeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, tooling, blockers]
---

Completion gates cited as missing may actually exist in a sibling workspace but not in the current checkout. Closeout comments can reference blocking tools that are unavailable locally, creating permanent blockage illusion. Verify whether tools are truly unavailable or just not linked into the checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
