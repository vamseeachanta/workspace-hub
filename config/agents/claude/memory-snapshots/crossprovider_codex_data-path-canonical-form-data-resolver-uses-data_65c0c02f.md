---
name: crossprovider codex data-path-canonical-form-data-resolver-uses-data
description: Data path canonical form: data_resolver uses data/modules/<module>/
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-paths, config, conventions]
---

data_resolver.py normalizes all module data paths to data/modules/<module_name>/ regardless of plan language. Config files, pseudocode, README examples, and tests must use this canonical form to avoid path mismatch bugs; direct path construction fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
