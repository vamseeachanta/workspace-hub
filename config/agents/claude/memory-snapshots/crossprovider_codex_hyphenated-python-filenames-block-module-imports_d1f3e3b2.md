---
name: crossprovider codex hyphenated-python-filenames-block-module-imports
description: Hyphenated Python filenames block module imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-hazards, plan-review, code-structure]
---

Files named with hyphens like `ingest-orcina.py` cannot be imported as modules (e.g., `import ingest_orcina` fails). Plans proposing code reuse across scripts with hyphenated names need explicit module-layout decisions: either rename/split into importable modules, or accept duplication. This was a recurring blocker across multiple data-pipeline plans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
