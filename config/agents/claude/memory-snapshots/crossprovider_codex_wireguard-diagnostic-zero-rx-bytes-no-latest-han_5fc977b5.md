---
name: crossprovider codex wireguard-diagnostic-zero-rx-bytes-no-latest-han
description: WireGuard diagnostic: zero RX bytes + no latest-handshake = peer unreachable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [networking, vpn, wireguard, diagnostics, layer-isolation]
---

When `wg show` reports 0 B received and absent `latest handshake` timestamp, the WireGuard peer is not responding to connection attempts. This is a network-layer fault (peer down, firewall, or routing) distinct from SSH or authentication issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
