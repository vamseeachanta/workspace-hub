---
name: crossprovider codex markdown-validator-scoping-enables-fail-closed-b
description: Markdown validator scoping enables fail-closed bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [validation, security, governance]
---

A validator claiming fail-closed behavior can silently fail if it only validates specific patterns (e.g., shortcodes in 'current capability sentences') while leaving other factual content as raw Markdown (e.g., historical facts, benefit claims, paraphrased capabilities). Either validate all factual content or explicitly restrict input format; don't assume unmandated sections stay manual.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
