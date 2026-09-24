---
name: crossprovider codex read-only-coverage-reporting-must-precede-label-
description: Read-only coverage reporting must precede label mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gating, safety-gates, coverage-first]
---

Gate safety: run a read-only coverage audit (missing/ambiguous/terminal/routable classification) to verify routing config before any label writes. Catches configuration errors (false capability claims, stale mappings) before they propagate to active issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
