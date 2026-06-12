---
name: crossprovider hermes validator-coverage-gap-negative-patterns-miss-pr
description: Validator coverage gap: negative patterns miss private-path leakage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validator-design, public-safety, private-path-isolation]
---

Validators checking only for expected-bad patterns (secrets, `/mnt/ace` paths) miss unintended infrastructure leaks (e.g., `.claude/` private context in public artifacts). Use positive allowlist validation (only approved paths/patterns allowed) not just negative exclusion. Combine both for defense-in-depth.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
