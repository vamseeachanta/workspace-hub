---
name: crossprovider codex relative-path-handling-in-multi-component-system
description: Relative path handling in multi-component systems creates silent mismatches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-handling, integration-contracts, distributed-scripts]
---

When scheduler writes manifests relative to process CWD and health reads relative to repo root, path resolution diverges if invoked from different directories. Require explicit path resolution contract: all absolute paths or all relative-to-repo-root, plus tests covering non-root invocation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
