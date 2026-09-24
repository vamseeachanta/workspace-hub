---
name: crossprovider codex environment-differences-across-machines-xdg-path
description: Environment differences across machines (XDG paths, plugin versions, dependencies) create divergent behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, xdg, portability, machine-divergence]
---

Tool behavior varies by installed plugin version, XDG environment variables, and presence of dependencies. Two machines with the same script and config can behave differently because one has `$PYTHONPATH` set, `_PYTHON_SYSCONFIGDATA_NAME` defined, or different plugin versions. Diagnosis must compare live state across machines before concluding the script is broken.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
