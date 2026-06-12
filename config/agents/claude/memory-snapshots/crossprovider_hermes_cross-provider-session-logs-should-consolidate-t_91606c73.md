---
name: crossprovider hermes cross-provider-session-logs-should-consolidate-t
description: Cross-provider session logs should consolidate to single canonical backend (Hermes), not diverge
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-provider, memory, session-consolidation]
---

Claude auto-memory, Codex state, and Hermes session logs create parallel silos that desync. Per-provider state files (Codex index = history-only, Hermes `active_agents` ≠ live workers) lead to contradictory ground truth. Consolidate all cross-provider session data to a single canonical backend via headless distillation (`distill-provider-sessions.py`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
