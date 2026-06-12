---
name: crossprovider hermes pep-723-inline-script-dependencies-require-direc
description: PEP 723 inline script dependencies require direct script invocation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [uv, dependencies, cron, pep723]
---

`uv run --no-project python file.py` skips PEP 723 metadata; inline dependencies won't install. Call script directly: `uv run --no-project file.py` so uv parses and installs from the `/// script` block.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
