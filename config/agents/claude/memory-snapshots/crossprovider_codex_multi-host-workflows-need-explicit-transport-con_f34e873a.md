---
name: crossprovider codex multi-host-workflows-need-explicit-transport-con
description: Multi-host workflows need explicit transport contracts before design
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [architecture, transport, licensed-software, security]
---

Data/result flows between hosts (e.g., Linux→licensed Windows solver→Linux) require pre-design contracts: archive format, extraction rules (symlink rejection), size limits, atomic retrieval, access control, and idempotency guarantees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
