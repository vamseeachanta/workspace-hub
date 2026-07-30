---
name: crossprovider codex false-green-monitoring-signals-hide-real-infrast
description: False-green monitoring signals hide real infrastructure defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [monitoring, infrastructure, debugging]
---

Fresh file metadata (e.g., Hermes artifacts) can mask missing heartbeats or broken initialization in monitoring systems, reporting FRESH when liveness checks have actually failed. Independent verification (e.g., heartbeat existence check before metadata read) is required to avoid silent infrastructure gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
