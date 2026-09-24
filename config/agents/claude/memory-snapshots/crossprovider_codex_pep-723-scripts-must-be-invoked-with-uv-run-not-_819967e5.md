---
name: crossprovider codex pep-723-scripts-must-be-invoked-with-uv-run-not-
description: PEP-723 scripts must be invoked with 'uv run', not bare python3
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, python, uv, pep-723]
---

Scripts declaring inline dependencies via PEP-723 header comments (like `# /// script` blocks with `dependencies` lists) must be invoked with `uv run script.py`, not `python3 script.py`. Bare invocation fails with ModuleNotFoundError for declared dependencies like python-pptx, even though they are properly declared in the script header.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
