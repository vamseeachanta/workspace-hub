---
name: crossprovider codex generator-output-verification-requires-isolation
description: Generator output verification requires isolation to avoid checkout mutation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, generators, isolation]
---

HTML/artifact generators with hard-coded output paths must use an isolation layer or output override; direct execution rewrites the checkout. Symlinked isolation leaks Python bytecode writes into the real tree—copy-based isolation is required.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
