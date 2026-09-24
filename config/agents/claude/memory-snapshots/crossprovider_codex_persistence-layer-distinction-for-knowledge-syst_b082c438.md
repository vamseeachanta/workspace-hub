---
name: crossprovider codex persistence-layer-distinction-for-knowledge-syst
description: Persistence layer distinction for knowledge systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, knowledge-systems, persistence]
---

Knowledge-system designs must distinguish three layers: committed institutional seeds (legal-reviewed source of truth, tracked in repo), machine-local runtime (gitignored ephemeral, rebuilt from sources), and auto-memory (out-of-repo, session-scoped). Conflating them causes data loss and concurrency issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
