---
name: crossprovider codex format-and-lint-gates-must-cover-all-modified-fi
description: Format and lint gates must cover all modified file types
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [linting, validation-gates, file-types]
---

Black/isort gates cover Python code but leave YAML/JSON/config files unchecked. Multi-file-type changes need separate check-yaml/yamllint gates; format validation gaps hide until runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
