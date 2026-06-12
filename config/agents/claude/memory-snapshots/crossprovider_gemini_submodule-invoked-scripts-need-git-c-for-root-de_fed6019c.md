---
name: crossprovider gemini submodule-invoked-scripts-need-git-c-for-root-de
description: Submodule-invoked scripts need git -C for root detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-submodules, path-resolution]
---

Script invoked from submodule root: bare `git rev-parse --show-toplevel` returns submodule path, not workspace root. Use `git -C "$(dirname "$0")" rev-parse --show-toplevel` to resolve from script location. Prevents path mismatches when config files live at workspace root.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
