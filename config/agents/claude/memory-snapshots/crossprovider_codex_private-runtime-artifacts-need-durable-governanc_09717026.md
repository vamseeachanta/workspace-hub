---
name: crossprovider codex private-runtime-artifacts-need-durable-governanc
description: Private runtime artifacts need durable governance contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [git-safety, auditability, infrastructure]
---

Gitignored paths (e.g., .local/floorhand/) for production artifacts lack versioning and auditability. Define persistent residency contracts outside gitignore so artifacts remain recoverable and version-tracked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
