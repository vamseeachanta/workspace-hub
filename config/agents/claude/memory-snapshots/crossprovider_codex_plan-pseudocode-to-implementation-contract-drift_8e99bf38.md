---
name: crossprovider codex plan-pseudocode-to-implementation-contract-drift
description: Plan pseudocode-to-implementation contract drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, contract-drift, implementation-verification]
---

Pseudocode declaring one filter logic (e.g., content_class AND sensitivity) can diverge from actual implementation arguments (e.g., content_class only), creating silent contract violations invisible to pseudocode-level review. Verify actual CLI args and filter intersection logic against declared intent during plan review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
