---
name: crossprovider codex file-path-loading-importlib-spec-from-file-locat
description: File-path loading (importlib.spec_from_file_location) hides import errors indefinitely
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [import-mechanisms, file-path-loading, latent-defects, packaging-refactors]
---

Modules loaded via file path bypass relative-import validation; one module had persistent `from .csv_parser` ImportError that never surfaced due to this bypass. Converting from ad-hoc file-path loading to real package imports exposes latent breakage—expect failures when refactoring toward proper packaging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
