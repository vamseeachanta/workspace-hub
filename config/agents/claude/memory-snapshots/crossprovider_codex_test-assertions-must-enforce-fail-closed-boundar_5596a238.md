---
name: crossprovider codex test-assertions-must-enforce-fail-closed-boundar
description: test assertions must enforce fail-closed boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, review-patterns, fail-closed]
---

Test assertions that only validate happy-path content miss fail-closed constraints required by specs. Example: source-map privacy tests should assert all required phrases are present, not just a subset. This pattern recurs in review findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
