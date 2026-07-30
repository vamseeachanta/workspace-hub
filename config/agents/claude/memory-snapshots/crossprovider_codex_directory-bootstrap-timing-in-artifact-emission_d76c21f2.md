---
name: crossprovider codex directory-bootstrap-timing-in-artifact-emission
description: Directory bootstrap timing in artifact emission
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [file-handling, initialization, artifact-emission]
---

Create parent directories before strict-mode path resolution, not after. Prevents 'directory doesn't exist' blocking first-time artifact emission and storage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
