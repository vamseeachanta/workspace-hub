---
name: crossprovider gemini bulk-sed-replacement-on-shell-scripts-silently-b
description: Bulk sed replacement on shell scripts silently breaks command detection and venvs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-scripting, python, uv, migration-hazard, tool-substitution]
---

`command -v` accepts only a single command name—replacing `python3` with `uv run --no-project python` causes detection to fail silently even when uv is present. Scripts managing local `.venv/bin/activate` bypass their intended environment when `--no-project` is used. Surgical replacement required: detection pass (`command -v python3` → `command -v uv`) separate from invocation pass.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
