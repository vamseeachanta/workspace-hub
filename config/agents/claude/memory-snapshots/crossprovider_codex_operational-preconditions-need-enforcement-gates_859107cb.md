---
name: crossprovider codex operational-preconditions-need-enforcement-gates
description: Operational preconditions need enforcement gates, not just assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-systems, testing-gaps, safety-gates]
---

Saying "cluster-wide fence must be enabled" is not a gate if code defaults it off and tests only local behavior. One unfenced old leader still yields split-brain. Need machine-level enumeration, fail-closed defaults, or live multi-machine tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
