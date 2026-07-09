---
name: crossprovider codex deterministic-artifact-naming-required-for-valid
description: Deterministic artifact naming required for validator scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [contracts, determinism, naming-conventions]
---

Review artifacts need reproducible names (issue-scoped, format-locked filenames like `2026-07-02-issue-63-review-round-1.md`) not prose suggestions. Validators rely on glob/regex patterns to find and scan artifacts; non-deterministic naming creates scanner gaps and false-negatives.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
