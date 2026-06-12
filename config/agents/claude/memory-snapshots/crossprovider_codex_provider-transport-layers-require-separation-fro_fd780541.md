---
name: crossprovider codex provider-transport-layers-require-separation-fro
description: Provider transport layers require separation from intent for true neutrality
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [provider-neutral, architecture, intent-vs-transport, slash-commands, skills]
---

Claude uses slash commands (/gsd:plan-phase), Codex uses skills (gsd-plan-phase), and MCP uses tool calls. The same intent can have different transports. True provider-neutral workflows need a canonical intent spec and thin per-provider adapters, not three parallel implementations maintained by hand.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
