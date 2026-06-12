---
name: crossprovider gemini codex-fallback-2-of-3-consensus-when-codex-retur
description: Codex fallback: 2-of-3 consensus when Codex returns NO_OUTPUT
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-review, resilience]
---

When Codex review returns NO_OUTPUT (not REJECT/MAJOR), fall back to 2-of-3 consensus: if both Claude and Gemini APPROVE, grant CONDITIONAL PASS. Otherwise, HARD BLOCK. Prevents complete blocking on Codex transient failures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
