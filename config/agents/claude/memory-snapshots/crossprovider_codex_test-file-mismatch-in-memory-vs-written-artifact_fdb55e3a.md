---
name: crossprovider codex test-file-mismatch-in-memory-vs-written-artifact
description: Test-file mismatch: in-memory vs written artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, file-output]
---

Tests that assert in-memory payload correctness miss mutations occurring during serialization. Always test the actual written artifact (JSON/CSV/files on disk), not just the pre-serialization object, to catch serialization-time side effects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
