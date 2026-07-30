---
name: crossprovider codex immutable-rev-0-artifacts-conflict-with-mutable-
description: Immutable Rev-0 artifacts conflict with mutable pack manifests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [immutability, versioning, design]
---

Cannot simultaneously require Rev-0 files to be byte-identical and allow a shared pack manifest to be rewritten for new revisions. Solution: introduce revision-specific immutable pack manifests (rev-00/, rev-01/) or immutable rev-root with separate mutable registration index.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
