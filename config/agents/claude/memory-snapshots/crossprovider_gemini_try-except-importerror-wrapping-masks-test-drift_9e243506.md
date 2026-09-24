---
name: crossprovider gemini try-except-importerror-wrapping-masks-test-drift
description: try/except ImportError wrapping masks test-drift at collection time
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, import-paths, test-collection, module-refactoring]
---

Test modules that import from non-existent paths wrapped in try/except blocks will still be collected and executed by pytest, but fail at runtime. This creates hidden test-drift where module refactorings (legacy paths diverging from current structure) are invisible to static checkers until execution, delaying discovery of import-path debt.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
