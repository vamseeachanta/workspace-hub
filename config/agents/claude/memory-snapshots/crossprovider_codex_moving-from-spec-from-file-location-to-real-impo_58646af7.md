---
name: crossprovider codex moving-from-spec-from-file-location-to-real-impo
description: Moving from spec_from_file_location to real imports exposes latent relative imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, python-imports, testing, package-safety]
---

Modules loaded via importlib.util.spec_from_file_location have their relative imports never exercised. Refactoring to real package imports immediately surfaces intra-package imports that were silently broken (e.g., 'from .csv_parser import CSVParser' that had always failed but was unreachable in file-path loading).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
