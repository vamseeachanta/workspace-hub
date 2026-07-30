---
name: crossprovider codex exception-handlers-must-catch-specific-subtypes-
description: Exception handlers must catch specific subtypes, not base only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [error-handling, cli-design]
---

Wrapping a persistence layer with a CLI that catches only the base exception class will miss subtype-specific errors (e.g., catches `BootstrapContractError` but misses `BootstrapManifestError`). Tests injecting only the base type false-green. Catch both or enforce full-workflow testing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
