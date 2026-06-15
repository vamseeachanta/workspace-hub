---
name: crossprovider codex pdfplumber-is-an-undeclared-environment-dependen
description: pdfplumber is an undeclared environment dependency for table extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tool-dependency, environment, ingest-tooling]
---

The hardened contract specifies table extraction via pdfplumber, but pdfplumber is not installed in temporary worktrees by default. Installations to /tmp as a disposable dependency work around this, but worktree setup should explicitly include pdfplumber to avoid friction in ingest batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
