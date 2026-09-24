---
name: crossprovider codex security-contracts-require-re-validation-at-ever
description: Security contracts require re-validation at every mutation boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-contracts, state-mutation, adversarial-review]
---

Single-point validation of forbidden surfaces (Git alternates, replace refs, hooks) before state-mutation operations is insufficient when the target can mutate concurrently. Validation must occur at every critical operation boundary, not just at entry. In the reviewed code, `_reject_git_surfaces()` ran once, then later attestations (`_independent_attestation`) did not re-check those surfaces, creating a window for forbidden Git authority to appear after initial clearance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
