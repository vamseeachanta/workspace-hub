---
name: crossprovider gemini monorepo-cli-routing-via-subprocess-delegation
description: Monorepo CLI routing via subprocess delegation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, cli, monorepo, subprocess]
---

Map CLI prefix (e.g., 'dm', 'ah', 'spm') to repo directory, then resolve command: check venv-installed script, check repo-root script, fallback to python -m. Lightweight pattern for workspace delegation across Python submodules without hardcoded paths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
