---
name: crossprovider gemini submodule-detached-head-is-intended-design
description: Submodule detached HEAD is intended design
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, submodules]
---

Workspace pins submodules at specific commits intentionally; detached HEAD in submodules is not error. Fix divergence with `git pull --no-rebase` (merge never rebase). Workspace showing submodules as modified after fix is expected.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
