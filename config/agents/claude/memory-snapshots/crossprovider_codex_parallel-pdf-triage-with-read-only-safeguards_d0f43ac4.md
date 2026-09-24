---
name: crossprovider codex parallel-pdf-triage-with-read-only-safeguards
description: Parallel PDF triage with read-only safeguards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational-pattern, parallel-work, safety-gates, worktree-hygiene]
---

Delegate independent PDF inspections (content classification, extractability checks, dedupe searches) to parallel agents while main session handles extraction, but maintain strict read-only state. Immediately clean up accidental scratch artifacts (-.png, -.pgm from PDF tools) to prevent worktree pollution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
