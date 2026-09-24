---
name: crossprovider codex plans-mixing-policy-design-with-implementation-c
description: Plans mixing policy design with implementation contract create scope creep and review failure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, scope-management, review-process]
---

Plans that conflate governance decisions with implementation contract details become too large to review coherently. Parent/child issue scope separation collapses when the parent carries implementation-adjacent decisions (scheduler updates, artifact paths, delta semantics). Separate policy language from implementation contract in distinct sections or split into two issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
