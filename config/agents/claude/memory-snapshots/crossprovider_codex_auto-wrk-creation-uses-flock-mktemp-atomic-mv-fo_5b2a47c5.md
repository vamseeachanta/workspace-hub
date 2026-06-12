---
name: crossprovider codex auto-wrk-creation-uses-flock-mktemp-atomic-mv-fo
description: Auto-WRK creation uses flock + mktemp + atomic mv for concurrency
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [wrk-automation, concurrency-safety]
---

Safe concurrent WRK creation serializes via flock on state.yaml, generates next ID via next-id.sh, scaffolds pending/WRK-NNN.md via mktemp, then mv for atomic commit. Pattern prevents race-condition duplicate IDs under parallel agent runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
