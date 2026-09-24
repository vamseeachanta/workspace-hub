---
name: crossprovider gemini optional-dependency-pattern-with-installation-er
description: Optional dependency pattern with installation error guidance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python-patterns, error-handling, dependencies]
---

Guard optional imports with try/except, set module flag (PACKAGE_AVAILABLE), raise RuntimeError with exact pip install command when the module is used without the dependency. Other loaders in the same package continue to function normally despite missing optional dependencies.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
