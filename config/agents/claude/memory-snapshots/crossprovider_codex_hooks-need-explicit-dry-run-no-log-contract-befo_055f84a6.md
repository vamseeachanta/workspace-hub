---
name: crossprovider codex hooks-need-explicit-dry-run-no-log-contract-befo
description: Hooks need explicit --dry-run/--no-log contract before invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, dry-run, side-effects]
---

Cannot assume hooks are side-effect-free; before invoking in read-only contexts, must first verify and test the hook's --dry-run and --no-log behavior explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
