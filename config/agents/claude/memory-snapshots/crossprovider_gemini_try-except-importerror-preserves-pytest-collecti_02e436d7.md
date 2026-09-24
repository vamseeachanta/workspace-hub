---
name: crossprovider gemini try-except-importerror-preserves-pytest-collecti
description: Try/except ImportError preserves pytest collection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, imports, collection]
---

Modules with failed imports wrapped in `try/except ImportError` are still collected by pytest. This means a test file can exist and be collected even if its dependencies don't exist, complicating failure diagnosis.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
