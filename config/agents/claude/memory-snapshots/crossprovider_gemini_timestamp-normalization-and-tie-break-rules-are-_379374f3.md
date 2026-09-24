---
name: crossprovider gemini timestamp-normalization-and-tie-break-rules-are-
description: Timestamp normalization and tie-break rules are load-bearing for policy
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [policy-design, correctness, specifications]
---

Event-ordering policies (bypass, rollback, revert) require explicit UTC timestamp contract with source-type derivation, millisecond precision, and tie-break precedence. Missing normalization causes subtle ordering failures spanning multiple review rounds.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
