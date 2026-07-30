---
name: crossprovider codex content-addressed-artifact-trust-beats-metadata-
description: Content-addressed artifact trust beats metadata-only registries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [security, validation, architecture]
---

A registry tracking only metadata (artifact path, commit SHA, comment reference) allows the underlying file to change silently while keeping the same registry entry. Implementation must pin content digest (SHA256 hash) in registry rows and validate re-computation in CI to detect tampering.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
