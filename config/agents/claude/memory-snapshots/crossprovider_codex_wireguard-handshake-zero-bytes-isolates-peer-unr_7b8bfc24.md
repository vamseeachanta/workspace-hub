---
name: crossprovider codex wireguard-handshake-zero-bytes-isolates-peer-unr
description: WireGuard handshake zero-bytes isolates peer unreachability
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [wireguard, network-diagnosis, ssh-debugging]
---

SSH timeouts at the WireGuard layer show: zero bytes received and no 'latest handshake' in `wg show`, despite outbound transmission. This signature reliably isolates peer/endpoint unreachability, distinct from IPv6 routing issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
