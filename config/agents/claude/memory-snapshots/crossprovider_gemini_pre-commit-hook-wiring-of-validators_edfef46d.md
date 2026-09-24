---
name: crossprovider gemini pre-commit-hook-wiring-of-validators
description: Pre-commit hook wiring of validators
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pre-commit, hooks, validation, automation]
---

Wire validators (structure checks, drift detection, required-file checks) into `.git/hooks/pre-commit` to catch violations before commit, not after. Shifts quality gates left and prevents bad state from entering the repo.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
