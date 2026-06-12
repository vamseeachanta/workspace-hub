---
name: crossprovider hermes unresolved-target-allowlisting-in-validators-is-
description: Unresolved target allowlisting in validators is fail-open
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation-design, fail-open-risk, error-handling]
---

`validate()` explicitly allowing unresolved `target_node` values (returning `[]` instead of error) means typos, leaks, and broken links in edge targets go unnoticed. Strict validation should fail on unresolved targets unless explicitly whitelisted as intentional placeholders.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
