---
name: crossprovider hermes broad-forbidden-pattern-regex-prevents-validatio
description: Broad forbidden-pattern regex prevents validation gaps; don't hardcode single-case checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [regex-validation, pattern-generalization]
---

Initial llm-wiki validator only rejected `/mnt/ace` paths; tests passed but staged code had `/mnt` references outside of `/mnt/ace`. Broadening to `^(/home|/mnt|/tmp|/var|/etc)` caught the whole class. Lesson: avoid validator logic that special-cases one known-bad path; generalize to the class of paths that should never appear.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
