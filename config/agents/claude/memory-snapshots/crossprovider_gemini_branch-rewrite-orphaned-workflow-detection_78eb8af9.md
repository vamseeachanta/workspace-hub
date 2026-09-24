---
name: crossprovider gemini branch-rewrite-orphaned-workflow-detection
description: Branch rewrite orphaned workflow detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, ci, branch-history]
---

No common ancestor between a CI commit and current main (verified via `git merge-base`) indicates branch rewrite orphaned workflows. Those workflows are unreachable and must be rebuilt rather than restored.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
