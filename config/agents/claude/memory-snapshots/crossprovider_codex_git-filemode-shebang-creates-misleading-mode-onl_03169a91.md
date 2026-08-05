---
name: crossprovider codex git-filemode-shebang-creates-misleading-mode-onl
description: Git fileMode + shebang creates misleading mode-only deltas
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [git, gotcha, tooling]
---

When a script has a shebang and `core.fileMode=false`, amending commits creates a staged mode-only diff (executable in tree, 100644 in index) that misleads future readers about execution intent. Resolution: remove optional shebang; invoke Python scripts explicitly via `python`, not as executables.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
