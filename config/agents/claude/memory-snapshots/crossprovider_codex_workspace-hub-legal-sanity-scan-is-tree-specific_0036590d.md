---
name: crossprovider codex workspace-hub-legal-sanity-scan-is-tree-specific
description: Workspace-hub legal-sanity-scan is tree-specific, floods on pre-existing hits
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [legal, scan, tooling, scope]
---

The shared legal scan script scans the workspace-hub tree and emits many pre-existing deny-list violations unrelated to your change. For bounded checks (e.g., in llm-wiki), use a scoped changed-file deny-grep or frontmatter probe instead, not the workspace-hub script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
