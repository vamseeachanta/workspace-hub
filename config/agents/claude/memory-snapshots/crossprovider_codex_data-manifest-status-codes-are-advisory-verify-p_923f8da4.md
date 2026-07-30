---
name: crossprovider codex data-manifest-status-codes-are-advisory-verify-p
description: Data-manifest status codes are advisory; verify payload existence independently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [data-provenance, manifest-trust, validation]
---

Acquisition manifests may log `error` for a step that actually completed downstream (e.g., Texas completion ZIP marked failed but exists locally). Don't rely solely on manifest status; validate artifact presence with separate checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
