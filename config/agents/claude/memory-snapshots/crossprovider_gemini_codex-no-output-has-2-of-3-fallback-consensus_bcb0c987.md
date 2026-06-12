---
name: crossprovider gemini codex-no-output-has-2-of-3-fallback-consensus
description: Codex NO_OUTPUT has 2-of-3 fallback consensus
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-review, routing, resilience]
---

Cross-review gate accepts Codex APPROVE/MINOR, but on NO_OUTPUT falls back to 2-of-3: if Claude+Gemini both APPROVE, pass conditionally. Prevents single-provider outage from blocking execution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
