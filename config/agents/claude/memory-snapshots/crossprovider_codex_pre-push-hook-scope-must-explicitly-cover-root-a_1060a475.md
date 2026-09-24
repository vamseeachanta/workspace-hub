---
name: crossprovider codex pre-push-hook-scope-must-explicitly-cover-root-a
description: Pre-push hook scope must explicitly cover root and submodule changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, file-coverage, monorepo-patterns]
---

Limiting drift checks to "hub files only" or adding early-exit patterns can skip intended checks when harness changes are in root or submodules. Gate ordering and path coverage must be explicit; test both root-only and submodule-only change scenarios.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
