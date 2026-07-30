---
name: crossprovider codex sequential-github-mutations-need-single-lane-mod
description: Sequential GitHub mutations need single-lane mode
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [github, workflow, sequential]
---

When closures or mutations are gated on prior merge state (e.g., 'close issues only after PR #1037 merges'), use single-lane mode and verify gate completion before each mutation to avoid race conditions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
