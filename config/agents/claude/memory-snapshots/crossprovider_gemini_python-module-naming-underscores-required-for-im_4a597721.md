---
name: crossprovider gemini python-module-naming-underscores-required-for-im
description: Python module naming: underscores required for imports, hyphens break idiomatic code
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python-conventions, import-friction, naming-consistency]
---

Python files must use underscores for module names to enable natural imports; hyphenated names force workarounds like importlib and are non-idiomatic. Mixing underscore and hyphen conventions in a single codebase (e.g., `doc-intelligence/` vs `doc_intelligence/`) causes import friction. Standardize on underscores for Python files unless strict CLI-naming conventions override.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
