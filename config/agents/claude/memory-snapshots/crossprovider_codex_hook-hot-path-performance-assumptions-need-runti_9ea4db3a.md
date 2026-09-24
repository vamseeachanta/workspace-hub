---
name: crossprovider codex hook-hot-path-performance-assumptions-need-runti
description: Hook hot-path performance assumptions need runtime verification; 28s lookups break 5s timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, hooks, plan-review]
---

When a plan proposes a lookup that calls expensive functions, measure it in the actual environment. Codex found a 28s skill-enumeration lookup that would violate the configured 5s hook timeout. Run the proposed command against live HEAD before claiming it meets performance requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
