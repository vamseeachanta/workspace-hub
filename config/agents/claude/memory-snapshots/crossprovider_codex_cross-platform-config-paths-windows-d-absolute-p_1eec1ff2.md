---
name: crossprovider codex cross-platform-config-paths-windows-d-absolute-p
description: Cross-platform config paths (Windows D:/ absolute paths) cause Linux loader failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config, cross-platform, agent-roles]
---

When agent role definitions hardcode Windows absolute paths like D:/workspace-hub/... in config_file references, Codex on Linux incorrectly rebases them under .codex/ instead of treating them as absolute. Causes role-loading warnings and skipped agent definitions on Linux environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
