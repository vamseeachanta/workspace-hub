---
name: crossprovider gemini tool-configuration-formats-vary-by-tool-no-unive
description: Tool configuration formats vary by tool; no universal convention
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tools, configuration, cli]
---

Bandit uses `.bandit` (YAML), radon uses `.radon.cfg`, vulture uses `vulture_whitelist.py`. pyproject.toml `[tool.*]` is not universally supported. Always verify each tool's actual config mechanism before designing a unified pattern (WRK-1081).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
