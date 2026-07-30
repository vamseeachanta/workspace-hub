---
name: crossprovider codex loopback-only-network-binding-does-not-prevent-w
description: Loopback-only network binding does not prevent WebSocket cross-site attacks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, websocket, networking]
---

WebSocket endpoints bound to loopback still require Origin validation; browser CORS rules do not apply to WebSocket handshakes. A trusted local browser can invoke cross-site payloads against a loopback endpoint. Loopback alone does not establish a security boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
