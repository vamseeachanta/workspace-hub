---
name: crossprovider gemini github-does-not-support-reserving-issue-numbers-
description: GitHub does not support reserving issue numbers; single counter required
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numbering, github-limitations, architecture]
---

Reserve-range patterns fail because GitHub PRs and issues share the same counter with no reservation mechanism. Single ID source (GitHub for WRK items) avoids cross-machine conflicts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
