---
name: crossprovider codex empty-file-and-missing-file-have-different-seman
description: Empty file and missing file have different semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [file-handling, error-handling, edge-cases]
---

Distinguishing between an existing-but-empty file and a nonexistent file requires explicit checks: `path.exists()` before opening, and handling empty reads separately. These cases often have different meanings (one is valid data, one is an error), and conflating them in error handling masks actual problems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
