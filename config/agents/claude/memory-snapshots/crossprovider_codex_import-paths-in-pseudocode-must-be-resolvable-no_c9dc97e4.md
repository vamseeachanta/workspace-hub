---
name: crossprovider codex import-paths-in-pseudocode-must-be-resolvable-no
description: Import paths in pseudocode must be resolvable, not descriptive
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [import-validation, pseudocode-precision]
---

Plans that name imports in pseudocode (e.g., `solver.report_extractors.extract_report_data_from_owr()`) must use the actual importable path, not a descriptive abbreviation. Running `from <module> import <name>` during review catches mismatches early (e.g., `solver` doesn't exist as a top-level import).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
