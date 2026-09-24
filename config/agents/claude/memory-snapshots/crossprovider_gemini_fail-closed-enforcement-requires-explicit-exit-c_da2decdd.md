---
name: crossprovider gemini fail-closed-enforcement-requires-explicit-exit-c
description: Fail-closed enforcement requires explicit exit codes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [enforcement, error-handling, robustness]
---

Enforcement scripts must exit non-zero on invalid state (missing required env vars, unwritable paths, invalid inputs). Fail-closed design prevents silent bypasses. WRK-658 gate+logging contract.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
