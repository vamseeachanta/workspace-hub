---
name: crossprovider codex verify-network-vpn-access-before-provisioning-wo
description: Verify network/VPN access before provisioning workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provisioning, network-validation, failure-detection]
---

SSH timeouts on provisioning tasks block entire workflows. Check network reachability (SSH test, traceroute, or ping) early before running long-running provision scripts. Avoids wasting time on provision logic when the underlying network layer fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
