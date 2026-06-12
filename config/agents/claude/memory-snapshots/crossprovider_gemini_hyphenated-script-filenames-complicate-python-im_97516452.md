---
name: crossprovider gemini hyphenated-script-filenames-complicate-python-im
description: Hyphenated script filenames complicate Python imports
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, import-patterns, code-smell]
---

Scripts named `generate-calc-report.py` require `importlib.util.spec_from_file_location()` workarounds to import in tests, breaking natural Python syntax. Use underscores for Python modules instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
