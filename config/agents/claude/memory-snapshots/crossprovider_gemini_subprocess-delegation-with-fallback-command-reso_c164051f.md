---
name: crossprovider gemini subprocess-delegation-with-fallback-command-reso
description: Subprocess delegation with fallback command resolution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cli-routing, subprocess, python-modules, delegation]
---

When delegating to submodule tools, try resolution in order: (1) venv-installed script at `<repo>/.venv/bin/<command>`, (2) plain script at `<repo>/<command>`, (3) Python module via `python -m <module>`. This pattern accommodates multiple installation styles without configuration and cleanly separates CLI entrypoints from module invocation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
