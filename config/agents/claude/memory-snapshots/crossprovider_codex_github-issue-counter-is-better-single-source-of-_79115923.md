---
name: crossprovider codex github-issue-counter-is-better-single-source-of-
description: GitHub-issue counter is better single source of truth than reserved ranges
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [wrk-numbering, github-integration, offline-fallback]
---

GitHub's issue counter cannot be reserved; using ranges per machine creates divergence and confusion. Instead, make GitHub the single ID source: every WRK gets its number from `gh issue create` at capture time. Offline fallback: `WRK-LOCAL-YYYYMMDD-HHMMSS` with a promotion script when connectivity returns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
