---
name: crossprovider codex git-submodule-foreach-can-hang-indefinitely-on-b
description: git submodule foreach can hang indefinitely on broken submodules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, automation, reliability]
---

`git submodule foreach` enters and runs a command in each submodule, and can hang indefinitely if a submodule is broken or detached. Prefer `git submodule status` (which lists submodules without entering them) and wrap any submodule iteration in a timeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
