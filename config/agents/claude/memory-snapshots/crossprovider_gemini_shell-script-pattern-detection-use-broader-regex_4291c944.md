---
name: crossprovider gemini shell-script-pattern-detection-use-broader-regex
description: Shell Script Pattern Detection: Use Broader Regex
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell, auditing, scripts]
---

Script invocation detection in skill audits should use broader regex like `(bash |python |\./)?(scripts/|uv run)` to catch Python scripts and relative paths, not just `bash scripts/` patterns. This prevents undercounting script adoption in skill coverage audits.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
