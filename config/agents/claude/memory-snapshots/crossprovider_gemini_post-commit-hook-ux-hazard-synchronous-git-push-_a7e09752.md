---
name: crossprovider gemini post-commit-hook-ux-hazard-synchronous-git-push-
description: Post-commit hook UX hazard: synchronous git push blocks terminal
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hooks, ux, network, post-commit]
---

Running `git push` synchronously in a post-commit hook blocks the user's terminal until the network request completes, degrading commit UX. Either background the operation (e.g. `(git push &)`) or accept the blocking behavior; communicate the tradeoff explicitly in documentation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
