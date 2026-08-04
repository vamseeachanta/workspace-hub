---
name: crossprovider codex codex-native-memories-conflict-with-curated-memo
description: Codex native memories conflict with curated MEMORY.runtime.md; don't fleet-enable yet
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [codex, memory-architecture, architectural-debt]
---

This repo uses a curated `MEMORY.runtime.md` read-back path. Enabling Codex's native memory feature fleet-wide could cause conflicts; defer until the memory architecture is unified or explicitly sequenced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
