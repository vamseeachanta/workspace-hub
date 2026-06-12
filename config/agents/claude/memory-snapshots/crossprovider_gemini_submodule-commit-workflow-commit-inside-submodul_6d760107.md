---
name: crossprovider gemini submodule-commit-workflow-commit-inside-submodul
description: Submodule commit workflow: commit inside submodule first, then git add at workspace level
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, submodules]
---

For submodule changes: `cd <submodule> && git commit && git push`, then `cd <workspace-hub> && git add <submodule> && git commit`. Detached HEAD in workspace-hub submodules is normal and expected (pins to specific commits).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
