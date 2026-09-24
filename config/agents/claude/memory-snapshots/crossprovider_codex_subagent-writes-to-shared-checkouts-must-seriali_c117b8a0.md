---
name: crossprovider codex subagent-writes-to-shared-checkouts-must-seriali
description: Subagent writes to shared checkouts must serialize through main session
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent-coordination, git-safety, serialization]
---

Parallel subagents writing to the same git checkout will race on lock files, causing undefined merge behavior. All writes must serialize through a single main session; read-only subagent audits can run in parallel safely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
