---
name: crossprovider codex gate-artifact-promotion-on-successful-exit-code
description: Gate artifact promotion on successful exit code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, safety, testing]
---

When promoting structured output from external tools, validate exit code before accepting the artifact. Timeouts (rc=124), kills (rc=137), and errors can emit partial structured headers that appear valid but are incomplete/wrong. Never promote partial/timeout output as authoritative signal. Require nonzero exit → `UNAVAILABLE` stub, not artifact elevation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
