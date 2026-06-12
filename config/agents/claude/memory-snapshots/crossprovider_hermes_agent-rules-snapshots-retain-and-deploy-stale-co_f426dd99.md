---
name: crossprovider hermes agent-rules-snapshots-retain-and-deploy-stale-co
description: Agent rules snapshots retain and deploy stale code references
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [config-drift, agent-rules, legacy-cleanup]
---

Codex/agent state-snapshots (e.g., config/agents/codex/state-snapshots/default.rules) retain references to deleted code; they're deployed live by sync scripts, creating persistent stale surfaces. Cleanup requires explicit removal from the snapshot, not just code deletion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
