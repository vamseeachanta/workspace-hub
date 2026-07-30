---
name: crossprovider codex tool-bindings-are-python-version-specific
description: Tool bindings are Python-version-specific
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [tooling, environment, testing]
---

Tools like Gmsh or FreeCAD can be installed for only one Python version. When installed for Python 3.12 but tests run on 3.13, failures are silent if test harness skips on missing import. Prefer explicit failures over skips.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
