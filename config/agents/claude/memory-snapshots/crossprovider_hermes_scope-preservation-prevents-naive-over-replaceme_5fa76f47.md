---
name: crossprovider hermes scope-preservation-prevents-naive-over-replaceme
description: Scope preservation prevents naive over-replacement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [refactoring, scope, safety]
---

When fixing path/reference drift, distinguish between historical evidence, generated artifacts, compatibility fallbacks, and active stale references. Do not naively replace all occurrences; use scoped grep + manual audit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
