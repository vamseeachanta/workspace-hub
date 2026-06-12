---
name: crossprovider hermes architecture-issue-decomposition-spans-parent-ch
description: Architecture issue decomposition spans parent + child with coordinated patching
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, issue-decomposition, coordinated-patching, multi-issue]
---

Parent issue (#2726) and child issues (#2727-#2729) for data/execution/report layers must be patched in coordinated fashion before adversarial re-review. Single MAJOR finding in one issue may block approval of entire architecture family.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
