---
name: crossprovider codex queue-manifest-batch-reconciliation-requires-str
description: Queue/manifest batch reconciliation requires structured row counts, not visual inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [batch, reconciliation, verification, llm-wiki#135]
---

llm-wiki batch 158 review: verify manifest/verdict/queue consistency via exact counts (10 verified + 2 deferred match 12 manifest paths). Document-index changes must reconcile to queue deltas via merge-base, not eye-ball review. Pattern: use structured reconciliation scripts with source-of-truth merge-base.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
