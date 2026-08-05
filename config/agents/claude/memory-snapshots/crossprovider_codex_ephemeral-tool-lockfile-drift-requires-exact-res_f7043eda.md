---
name: crossprovider codex ephemeral-tool-lockfile-drift-requires-exact-res
description: Ephemeral tool lockfile drift requires exact restoration
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [tooling, uv, lockfile]
---

When `uv` resolves ephemeral tools during testing, it updates the tracked lockfile. Restore exact prior content immediately with targeted `git checkout` before committing any work to avoid silent contamination of build configuration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
