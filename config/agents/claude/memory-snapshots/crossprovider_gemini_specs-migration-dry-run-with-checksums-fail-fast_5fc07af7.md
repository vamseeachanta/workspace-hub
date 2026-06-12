---
name: crossprovider gemini specs-migration-dry-run-with-checksums-fail-fast
description: Specs migration: dry-run with checksums, fail-fast collisions, idempotent apply
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration-pattern, specs, governance, WRK-188]
---

Pattern for large-scale spec centralization: (1) dry-run captures file list and checksums, (2) validation gates check for pre-existing target collisions (fail-fast, no overwrites), (3) apply is idempotent (second run produces no diff), (4) pointer templates guide local replacement. Source `README.md` is preserved as content; local copy is replaced by pointer.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
