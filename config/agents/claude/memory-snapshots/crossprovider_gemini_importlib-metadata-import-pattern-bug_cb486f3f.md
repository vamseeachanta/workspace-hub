---
name: crossprovider gemini importlib-metadata-import-pattern-bug
description: importlib.metadata import pattern bug
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, importlib, bug-pattern]
---

Using `import importlib` then `importlib.metadata.version()` raises AttributeError; must be `from importlib import metadata` or `import importlib.metadata`. Broad exception handlers (`except Exception`) mask this, causing silent fallback to full module import (WRK-1074).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
