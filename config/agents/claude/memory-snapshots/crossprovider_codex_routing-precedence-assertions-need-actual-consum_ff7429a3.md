---
name: crossprovider codex routing-precedence-assertions-need-actual-consum
description: Routing/precedence assertions need actual consumer code verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, configuration, precedence-chain]
---

Plans claiming 'behavior-contract.yaml > routing-config.yaml > this file' must cite the actual code that reads them in that order. Asserting precedence without verifying the consumer is a logical defect. Check session-analysis.sh, routing smart-router, or other entry points to confirm the read order exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
