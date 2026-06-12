---
name: crossprovider hermes hermes-gateway-shutdown-timing-expectations
description: Hermes gateway shutdown timing expectations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, systemd, operations]
---

Hermes gateway service has TimeoutStopSec=60s but drain timeout is 180s; expect at least 210s for safe shutdown under heavy load. Monitor actual drain behavior before shortening timeouts or risk orphaned worker processes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
