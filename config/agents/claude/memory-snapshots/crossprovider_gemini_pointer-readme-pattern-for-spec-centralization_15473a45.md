---
name: crossprovider gemini pointer-readme-pattern-for-spec-centralization
description: Pointer README pattern for spec centralization
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, spec-centralization, pointer-pattern]
---

When centralizing distributed specs/configs, copy sources to centralized tree first, then replace local directories with pointer-only READMEs. Enables gradual migration while preserving local discovery and reducing cutover risk.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
