---
name: crossprovider codex tailnet-relay-peers-require-explicit-classificat
description: Tailnet relay peers require explicit classification, not disco-layer probes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fleet-reachability, tailscale, network-probing]
---

`tailscale ping` confirms disco-layer connectivity but is not ACL-filtered and doesn't verify application auth. Real reachability for fleet dispatch needs TCP + SSH probes, and the transport path (relay vs direct, DERP vs LAN) must be classified explicitly. Most fleet peers may be DERP-relayed; byte counters disagree between CLI and JSON output for relayed paths—classify from CurAddr/Relay field instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
