---
name: crossprovider codex approval-marker-location-divergence-between-loca
description: Approval marker location divergence between local files and labels
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, git-local-state, github-sync]
---

`.planning/plan-approved/<n>.md` local approval markers can diverge from GitHub `status:plan-approved` labels without explicit reconciliation rule. Workflows requiring both must state which is authoritative or run periodic sync checks. Relying on labels alone misses stale local markers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
