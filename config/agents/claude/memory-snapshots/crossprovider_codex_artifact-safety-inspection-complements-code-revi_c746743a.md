---
name: crossprovider codex artifact-safety-inspection-complements-code-revi
description: Artifact safety inspection complements code review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, security, data-projects]
---

Code review for data projects must inspect generated artifacts themselves (size, embedded absolute paths, source decisions, routing classifications) alongside code logic. Code can look correct while artifacts leak private paths, embedded secrets, or incorrect classifications.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
