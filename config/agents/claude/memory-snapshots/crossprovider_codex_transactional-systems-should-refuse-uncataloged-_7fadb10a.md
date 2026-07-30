---
name: crossprovider codex transactional-systems-should-refuse-uncataloged-
description: Transactional systems should refuse uncataloged entries, not override
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [transactional-systems, safety, conflict-detection]
---

When discovering live system entries (e.g., cron lines) not in tracked config, transactional reconcilers should refuse to apply changes rather than silently overwriting. Refusal surfaces the conflict for human investigation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
