---
name: crossprovider codex frozen-is-a-conditional-skip-not-universal
description: `--frozen` is a conditional skip, not universal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv, dependency-management, ci]
---

Don't add `--frozen` to every `uv sync` call. Skip if: already present in the invocation, no `uv.lock` exists, or the job's purpose is testing dependency resolution. Unconditional application creates false success and prevents detection of new incompatibilities.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
