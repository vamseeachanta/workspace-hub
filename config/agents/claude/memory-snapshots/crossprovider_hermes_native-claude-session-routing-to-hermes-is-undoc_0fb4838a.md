---
name: crossprovider hermes native-claude-session-routing-to-hermes-is-undoc
description: Native Claude session routing to Hermes is undocumented
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-routing, hermes, documentation]
---

Multiple independent Hermes sessions ask 'does native Claude work flow through Hermes?' with no clear answer from logs alone. Session routing appears to be undocumented; need explicit hook/log evidence (Claude session-logger writes to orchestrator logs) and explicit confirmation rather than assumptions about provider pipelines.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
