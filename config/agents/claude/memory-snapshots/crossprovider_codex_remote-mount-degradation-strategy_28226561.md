---
name: crossprovider codex remote-mount-degradation-strategy
description: Remote mount degradation strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resilience, remote-resources, graceful-degradation]
---

When remote resources become unavailable, degrade gracefully to indexed metadata and cached summaries rather than attempting blind downloads or failing. Record source_unavailable status in the resource manifest and continue with evidence-on-hand.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
