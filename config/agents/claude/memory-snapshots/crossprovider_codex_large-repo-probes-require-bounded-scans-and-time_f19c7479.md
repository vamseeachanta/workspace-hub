---
name: crossprovider codex large-repo-probes-require-bounded-scans-and-time
description: Large-repo probes require bounded scans and timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational-constraint, environment-fact, cost-optimization]
---

Multi-repo workspaces like /mnt/local-analysis require --max-depth limits and timeouts on du/find/git commands; broad scans silently timeout. Sessions 1, 3, 6 repeated the pattern of starting with wide probes and narrowing. Establish bounded queries and max-depth=2-3 from the start.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
