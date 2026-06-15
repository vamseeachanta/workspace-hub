---
name: crossprovider codex module-import-hazard-with-lazy-sub-imports
description: Module-import hazard with lazy sub-imports
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [python, module-imports, lazy-loading]
---

When a module's functions have lazy sub-imports (e.g., fetch_decks imported inside a function), verify those sub-imports work from actual import context, not from script dir. Use importlib.util.spec_from_file_location to side-step sys.path hazards. Test by importing from repo root and calling the function.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
