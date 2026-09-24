---
name: crossprovider codex three-commit-sequence-pattern-for-infrastructure
description: Three-commit sequence pattern for infrastructure rollout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, infrastructure, change-management]
---

For configuration/CI changes affecting multiple targets: (1) enable features with lowest blast radius, (2) add safety flags conditional on presence, (3) standardize versions. This ordering allows independent verification and staged rollback if needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
