---
name: crossprovider gemini single-source-of-truth-versioned-schema-for-evid
description: Single-source-of-truth versioned schema for evidence artifacts prevents drift
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [evidence-design, schema-management, multi-producer-consistency]
---

When multiple scripts generate evidence (templates, log writers, validators), drift occurs between generated structure, validation rules, and expected fields. Use one canonical versioned schema definition that all producers and consumers call, preventing template/checker/runtime misalignment.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
