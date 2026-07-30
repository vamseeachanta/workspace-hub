---
name: crossprovider codex revision-chains-need-explicit-supersession-edges
description: Revision chains need explicit supersession edges, ancestry checks, and upstream manifest binding
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [revision-graphs, manifest-binding, ancestry-verification]
---

Later revisions that depend on immutable baselines must require explicit `supersedes` edges in the schema, bind exact upstream report/result manifest SHAs, and verify that every upstream revision is accepted, freshly reviewed, and non-superseded. Test fixtures should include cases where stale/nonaccepted/unreviewed upstream revisions attempt to authorize downstream use—these must fail. Handoff graphs cannot omit upstream revision manifests from their binding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
