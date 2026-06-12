---
name: crossprovider hermes memory-bridge-infrastructure-has-no-auto-sync-dr
description: Memory bridge infrastructure has no auto-sync; drift requires manual gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-bridge, hermes, manual-sync, drift-detection]
---

Bridge scripts (bridge-hermes-claude.sh, check-memory-drift.sh) exist and ran during sibling migration, but drift check detected facts in Hermes not yet synced to .claude/memory/agents.md. The bridge is a tool, not a real-time sync; operator must verify end-to-end consistency.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
