---
name: crossprovider codex stale-local-clones-masquerade-as-upstream-defect
description: Stale local clones masquerade as upstream defects
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [verification, measurement, debugging]
---

A local checkout differing from origin is evidence of *clone drift*, not origin defect. Always measure against origin/main, not a working copy. One round of work was wasted chasing a line-count discrepancy that traced to gpu-claw's clone being six lines behind.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
