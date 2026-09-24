---
name: crossprovider codex committed-artifacts-should-be-enforced-determini
description: Committed artifacts should be enforced deterministic via test
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, artifact-sync, determinism]
---

When a script generates committed reports (e.g., JSON/HTML artifacts), add a test that regenerates them and asserts the output matches the committed version byte-for-byte. This prevents drift between generator logic and stale committed artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
