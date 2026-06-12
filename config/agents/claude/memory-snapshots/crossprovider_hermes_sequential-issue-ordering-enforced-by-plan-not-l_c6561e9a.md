---
name: crossprovider hermes sequential-issue-ordering-enforced-by-plan-not-l
description: Sequential issue ordering enforced by plan, not labels
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependencies, sequential, plan-gate, ordering]
---

Issue #2544 depends on #2541 completing first (shared data resource). Plan text or comments must document the ordering; GitHub labels alone don't prevent parallel launches. Check plan for sequential caveats before launching.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
