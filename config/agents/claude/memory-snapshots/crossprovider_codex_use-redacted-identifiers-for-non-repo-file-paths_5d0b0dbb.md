---
name: crossprovider codex use-redacted-identifiers-for-non-repo-file-paths
description: Use redacted identifiers for non-repo file paths in generated reports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, security, artifact-generation, path-handling]
---

Embedding absolute local paths for user-supplied or external files into generated provenance reports violates no-leakage posture. Instead use redacted identifiers like basename + digest or explicit `source_id` labels from user config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
