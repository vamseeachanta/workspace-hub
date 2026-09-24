---
name: crossprovider codex scoped-tdd-boundaries-prevent-contamination-of-d
description: Scoped TDD boundaries prevent contamination of dependent tasks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, task-boundaries, serial-safety]
---

When implementing a fix in TDD, narrow the scope explicitly—no access to upstream data sources, no wiki writes, no scope creep into dependent tasks. Narrow boundaries prevent one task's defects from poisoning the next.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
