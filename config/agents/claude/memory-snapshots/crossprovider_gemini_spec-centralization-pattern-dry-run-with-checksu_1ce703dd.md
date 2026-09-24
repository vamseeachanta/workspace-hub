---
name: crossprovider gemini spec-centralization-pattern-dry-run-with-checksu
description: Spec centralization pattern: dry-run with checksums before apply
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, validation, audit]
---

Large file migrations (100s–1000s of files) require full dry-run with source inventory capture (file list, checksums via sha256sum, spec-root count) before any apply. Dry-run output includes fixed summary lines for audit. Post-apply checksums are compared against pre-apply to verify content integrity. Path collisions and duplicates are detected via Python one-liners before apply proceeds.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
