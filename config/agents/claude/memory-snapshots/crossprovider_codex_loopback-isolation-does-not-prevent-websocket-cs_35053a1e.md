---
name: crossprovider codex loopback-isolation-does-not-prevent-websocket-cs
description: Loopback isolation does not prevent WebSocket CSRF; auth and Origin validation are separate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, websocket, csrf, network-isolation]
---

Loopback-only server with WebSocket endpoint lacking authentication and Origin validation can still be exploited for cross-site tool execution, especially with broad agent permissions. Explicit threat boundary required: isolated local dev, no untrusted browsing, no network exposure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
