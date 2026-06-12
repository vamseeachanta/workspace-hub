---
name: crossprovider gemini layered-god-object-refactor-with-deprecationwarn
description: Layered God Object refactor with DeprecationWarning shim
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [refactoring, backward-compat, architecture]
---

Split monolithic modules into semantic layers (data → registry → queries or models → extractors → computations → builders), retain original file as shim with DeprecationWarning imports, update __init__.py to import from new modules. Achieves zero breakage while enabling gradual caller migration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
