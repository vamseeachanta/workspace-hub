---
name: crossprovider codex live-github-status-labels-are-the-canonical-appl
description: Live GitHub status labels are the canonical apply gate in multi-provider workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, gates, workflow]
---

Local approval markers or files are secondary; GitHub issue status:label is the source of truth for orchestrator apply/implementation gates. Cross-provider dispatches must check live GitHub, not assume local state matches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
