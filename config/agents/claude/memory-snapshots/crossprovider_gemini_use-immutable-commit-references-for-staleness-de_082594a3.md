---
name: crossprovider gemini use-immutable-commit-references-for-staleness-de
description: Use immutable commit references for staleness detection, not timestamps
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [staleness-detection, event-logs, immutable-references]
---

Commit SHAs and append-only event logs provide deterministic staleness checks; file mod times and HEAD pointers can diverge from ground truth. Critical for gate compliance logic where false-fresh or false-stale verdicts cause scope drift or unvalidated work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
