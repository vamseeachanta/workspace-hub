---
name: crossprovider codex wrk-scope-field-target-repos-must-align-with-pla
description: WRK scope field (target_repos) must align with plan execution repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, workflow, scope-management]
---

WRK-1016 declared `target_repos: [workspace-hub]` but proposed edits in assetutilities, digitalmodel, worldenergydata, assethold. This mismatch breaks scope verification. Recurring gate miss: before plan approval, verify target_repos covers all repos touched by execution steps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
