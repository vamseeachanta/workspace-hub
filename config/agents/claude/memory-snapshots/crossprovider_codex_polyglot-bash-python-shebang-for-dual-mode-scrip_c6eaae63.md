---
name: crossprovider codex polyglot-bash-python-shebang-for-dual-mode-scrip
description: Polyglot bash/Python shebang for dual-mode scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [portability, script-patterns, polyglot]
---

Scripts needing both bash (argument parsing, file ops) and Python (structured output, markdown processing) use polyglot shebang pattern: `#!/bin/sh ... python shebang block`. Invoke via `bash <script>` for portability (avoids shebang platform variance). Used in generate-final-review.py and other WRK-624 tools.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
