---
name: crossprovider gemini python-importlib-metapathfinder-for-module-refac
description: Python importlib MetaPathFinder for module refactoring
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [module-refactoring, python-importlib, backward-compat]
---

When flattening module hierarchies (moving worldenergydata.modules.X → worldenergydata.X), use importlib.abc.MetaPathFinder + importlib.machinery.ModuleSpec to redirect old import paths to new ones with DeprecationWarning. Pair with __getattr__ in a modules/__init__.py shim for from-style imports. This preserves backward compatibility without duplicating code.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
