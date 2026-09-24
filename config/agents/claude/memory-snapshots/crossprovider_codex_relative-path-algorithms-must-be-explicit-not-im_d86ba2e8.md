---
name: crossprovider codex relative-path-algorithms-must-be-explicit-not-im
description: Relative path algorithms must be explicit, not implicit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-resolution, plan-clarity, acceptance-criteria]
---

When a plan references relative paths like `fields/<page>.html` from source artifacts, the algorithm must explicitly state the base directory for resolution before containment checks. Prose like 'resolve under the directory' leaves ambiguity that implementations diverge on. Include the exact join order and traversal constraints in acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
