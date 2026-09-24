---
name: crossprovider codex host-dependent-test-skipping-with-validation-cov
description: Host-dependent test skipping with validation coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, skipping, host-dependencies]
---

Tests requiring specific binaries (Blender, OrcaFlex) use conditional skip decorators. Test the CLI wrapper and metadata validation even when the runtime is absent, skip only the real-render / license-dependent steps. Ensures validator structure is sound before host deployment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
