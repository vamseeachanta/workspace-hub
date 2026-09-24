---
name: crossprovider gemini graceful-cli-flag-deprecation-requires-suppresse
description: Graceful CLI flag deprecation requires suppressed argparse, not hard removal
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cli-design, deprecation, backwards-compatibility]
---

Removing --type flag outright from argparse causes hard crashes on legacy invocations; use argparse.SUPPRESS + deprecation warning message instead. Allows transition period where old commands work with warnings.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
