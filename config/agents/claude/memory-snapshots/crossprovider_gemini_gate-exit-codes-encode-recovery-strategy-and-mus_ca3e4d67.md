---
name: crossprovider gemini gate-exit-codes-encode-recovery-strategy-and-mus
description: Gate exit codes encode recovery strategy and must be fail-closed
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gating, shell-conventions, error-handling]
---

Exit 1 = predicate failure (gate blocks, requires user to fix approval evidence). Exit 2 = infrastructure failure (gate blocks, requires operator to repair checker/config). Both are fail-closed; exit 0 is gate pass. WRK-1017 Phase 1B uses this pattern across plan.sh, cross-review.sh, claim-item.sh to prevent silent bypass.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
