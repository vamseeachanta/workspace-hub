---
name: crossprovider gemini python-tooling-migration-three-distinct-patterns
description: Python tooling migration: three distinct patterns require separate fixes
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, uv, tooling, WRK-209, shell-scripting]
---

Migrating from python3/python to uv can't be bulk-sed: (1) availability checks: `command -v python3` → `command -v uv` (check binary name, not full command), (2) inline execution: `python3 -c` → `uv run --no-project python -c`, (3) shebangs: `#!/usr/bin/env python3` → `#!/usr/bin/env -S uv run --no-project python` (need `-S` for multi-arg support). Each requires context-aware fixes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
