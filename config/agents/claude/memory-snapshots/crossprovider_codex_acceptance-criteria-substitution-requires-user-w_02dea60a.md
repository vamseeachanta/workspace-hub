---
name: crossprovider codex acceptance-criteria-substitution-requires-user-w
description: Acceptance criteria substitution requires user waiver
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, test-equivalence, review-blocker]
---

When execution substitutes AC methods (e.g., hook direct-exec for Git integration test, path-isolation for file-count verification), silent substitution blocks review. Test equivalence must be explicitly approved; otherwise, AC remains unsatisfied and plan cannot close.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
