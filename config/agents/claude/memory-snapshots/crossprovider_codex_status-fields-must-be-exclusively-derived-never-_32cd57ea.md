---
name: crossprovider codex status-fields-must-be-exclusively-derived-never-
description: Status fields must be exclusively derived, never authored
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [state-management, determinism, governance]
---

Infrastructure tracking governance state must compute status deterministically through a closed lattice of operations; prohibit operator-authored status fields. This prevents drift between implementation behavior and governance claims, catching defects that authored status could hide.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
