---
name: crossprovider hermes unsigned-json-evidence-not-bound-to-workspace-id
description: Unsigned JSON evidence not bound to workspace identity enables path-drift forgery
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, evidence-schema, workspace-identity, path-drift]
---

Readiness evidence schemas that omit workspace root / repo identity allow the same machine with different checkouts to satisfy freshness checks. A stale/wrong clone can generate "pass" evidence for the right host and be accepted remotely. Evidence must include workspace-scoped identity anchors (workspace_root, repo path) and validate them on load.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
