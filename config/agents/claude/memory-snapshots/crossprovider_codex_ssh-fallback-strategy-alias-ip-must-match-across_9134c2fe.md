---
name: crossprovider codex ssh-fallback-strategy-alias-ip-must-match-across
description: SSH fallback strategy (alias → IP) must match across audit and remediation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ssh, network-fallback, consistency]
---

If an audit uses alias-first, then Tailscale IP as fallback to reach remote hosts, remediation must use the same strategy. If remediation hard-codes SSH alias only, it can fail to reach targets the audit reached, producing asymmetric results. Both code paths must use identical connection logic or explicitly document where they differ.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
