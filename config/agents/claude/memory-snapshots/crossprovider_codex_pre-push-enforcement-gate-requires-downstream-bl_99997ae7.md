---
name: crossprovider codex pre-push-enforcement-gate-requires-downstream-bl
description: Pre-push enforcement gate requires downstream blocking to be effective
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [enforcement, ci, pre-push-hooks, process-design]
---

A pre-push hook that exits 0 (warns only) will be ignored in high-volume CI environments with 40+ commits/day. Without hard blocking consequences downstream (e.g., failed PR checks, blocked merge), compliance becomes a guideline rather than a gate. Bypass vectors (SKIP_REVIEW_GATE env, hook disable, --no-verify, different clone) are trivial if the gate is advisory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
