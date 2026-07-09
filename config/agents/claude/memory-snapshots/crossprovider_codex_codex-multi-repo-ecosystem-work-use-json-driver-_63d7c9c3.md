---
name: crossprovider codex codex-multi-repo-ecosystem-work-use-json-driver-
description: Codex + multi-repo ecosystem work: use JSON driver output, not broad git status/diff
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [codex-workflow, multi-repo-coordination, performance]
---

The workspace-hub ecosystem-equivalence reconciliation driver (scripts/readiness/reconcile-ecosystem.sh) produces usable JSON reports under Codex. However, broad git status/diff operations hang on multi-repo roots; delegate to the purpose-built JSON driver (which completes cleanly with timeouts) and parse its output with jq instead. This reinforces operator constraints for Codex on large repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
