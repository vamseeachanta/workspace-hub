---
name: crossprovider codex reusable-prior-scripts-often-have-unbounded-trav
description: Reusable prior scripts often have unbounded traversal or side effects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [script-reuse, side-effects, scope-isolation]
---

Data inventory/refresh scripts from prior issues (freshness scorecard, audit tools, etc.) often use unbounded os.walk, write outputs by default, or require environment setup. Cannot assume reusability without auditing for read-only mode, bounded-discovery compatibility, and lack of mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
