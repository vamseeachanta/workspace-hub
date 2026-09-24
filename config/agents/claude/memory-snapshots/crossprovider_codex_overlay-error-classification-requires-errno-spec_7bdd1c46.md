---
name: crossprovider codex overlay-error-classification-requires-errno-spec
description: Overlay error classification requires errno-specific TDD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, error-handling, security]
---

Exit code 4 vs 5 for overlay I/O failures must be tested with exact injected errors (EPERM, EIO, etc.) and verified diagnostics that don't collapse into exit 3 (registry fallback). Generic OSError handling masks this distinction until TDD forces explicit enum coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
