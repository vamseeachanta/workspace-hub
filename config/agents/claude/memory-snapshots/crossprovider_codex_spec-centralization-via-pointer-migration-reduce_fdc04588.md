---
name: crossprovider codex spec-centralization-via-pointer-migration-reduce
description: Spec centralization via pointer migration reduces duplication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, data-organization, patterns]
---

Move specs from scattered repo-local dirs to centralized specs/repos/<repo>/... and replace local specs/ with pointer README. Requires fail-fast collision checks and idempotent dry-run+apply pattern.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
