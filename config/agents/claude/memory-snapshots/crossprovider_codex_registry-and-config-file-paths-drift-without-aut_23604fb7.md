---
name: crossprovider codex registry-and-config-file-paths-drift-without-aut
description: Registry and config-file paths drift without automated reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config, sync, readiness]
---

registry.yaml and harness-config.yaml drifted on workspace_root paths (registry: /mnt/local-analysis/workspace-hub vs harness: /mnt/workspace-hub). Implement a single-source-of-truth policy or automated reconciliation check when two config sources define the same data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
