---
name: crossprovider codex plan-verification-requires-code-inspection
description: Plan verification requires code inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, correctness, code-verification]
---

Plans claiming knowledge of existing code (signatures, module dependencies, constructor patterns) are falsifiable by reading the actual files. Unverified spec gaps and retrieval failures blocking plan inspection are MAJOR blockers, not process annoyances—they prevent correctness verification. Several sessions found false claims about code behavior that file inspection would have caught immediately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
