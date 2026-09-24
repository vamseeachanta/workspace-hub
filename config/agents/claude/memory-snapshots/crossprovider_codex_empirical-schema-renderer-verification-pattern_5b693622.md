---
name: crossprovider codex empirical-schema-renderer-verification-pattern
description: Empirical schema-renderer verification pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-verification, testing, documentation]
---

When documenting a schema for code that renders or consumes it (calc report generators, stage YAML parsers, etc.), verify compatibility by running example snippets through the actual implementation (load_and_validate(), render_markdown(), render_html()). WRK-1242 discovered six section schemas incompatible with the calc renderer—the incompatibility was caught empirically, not by inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
