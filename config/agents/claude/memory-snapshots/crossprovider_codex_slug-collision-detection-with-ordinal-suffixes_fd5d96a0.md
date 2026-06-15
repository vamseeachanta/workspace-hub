---
name: crossprovider codex slug-collision-detection-with-ordinal-suffixes
description: Slug collision detection with ordinal suffixes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [collision-detection, filename-dedup, testing-edge-cases]
---

When deduplicating filenames via ordinal suffixes, ordinal-generated slugs (e.g., plan-2) can collide with real stems that sort earlier. Test with both same-stem pairs (Plan.pptx + Plan.pdf → plan + plan-1) and collision chains (Plan.pdf + Plan-2.pdf + Plan.pdf). Without checking generated slugs against all prior allocations, overwrites persist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
