---
name: crossprovider codex stale-embedded-evidence-invalidates-draft-plans-
description: Stale embedded evidence invalidates draft plans on resume
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [planning, discovery, anti-pattern, correctness]
---

When a draft plan contains embedded evidence (inventory counts, manifest snapshots, structural assertions), it becomes stale after weeks/months without re-runs. Before resuming review on a stalled plan, run live discovery to confirm the plan's assertions still hold; outdated embedded evidence should trigger plan refresh or invalidate the plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
