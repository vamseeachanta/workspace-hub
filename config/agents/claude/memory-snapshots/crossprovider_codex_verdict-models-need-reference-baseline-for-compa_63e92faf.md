---
name: crossprovider codex verdict-models-need-reference-baseline-for-compa
description: Verdict models need reference baseline for comparative correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [measurement-semantics, correctness, comparative-systems]
---

In systems that grade a target against a reference (e.g., provider X vs Claude on the same machine), the verdict cannot be determined from target status alone. Verdict PARITY for 'both absent' is false when both are actually broken; verdict ABSENT for 'target absent' is false when collector tool failed. Verdict functions must accept reference state and distinguish ABSENT from MISSING-EVIDENCE.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
