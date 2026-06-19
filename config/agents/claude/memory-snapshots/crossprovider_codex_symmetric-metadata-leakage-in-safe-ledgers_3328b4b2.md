---
name: crossprovider codex symmetric-metadata-leakage-in-safe-ledgers
description: Symmetric metadata leakage in 'safe' ledgers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, data-handling, ledger-safety]
---

Committed artifacts marked repo-safe can still leak private-derived identity via fields like `filename`, `relative_path`, `source_path`. Existence in a committed repo does not guarantee safe-to-consume; verify field-level privacy before ingesting existing ledgers, or filter explicitly in tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
