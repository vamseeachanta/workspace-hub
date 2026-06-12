---
name: crossprovider hermes multi-ref-push-behavior-must-be-explicitly-speci
description: Multi-ref push behavior must be explicitly specified
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-semantics, acceptance-criteria, multi-ref-handling]
---

Designs claiming to handle multi-ref pushes without documenting the union/first-only policy create acceptance ambiguity. Acceptance criteria must state: 'union all changed files across refs' or 'fail closed to RUN_ALL' or equivalent explicit policy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
