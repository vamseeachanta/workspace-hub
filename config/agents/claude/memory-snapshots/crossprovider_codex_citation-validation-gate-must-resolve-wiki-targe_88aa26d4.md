---
name: crossprovider codex citation-validation-gate-must-resolve-wiki-targe
description: Citation validation gate must resolve wiki targets, not just assert string keys
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, gate-design, citations]
---

Tests that assert literal `code_id` strings pass while the actual citation sidecar/wiki resolution fails at runtime. Fail-closed validation should construct `Citation` objects and verify wiki frontmatter at calculation time, per the calc-citation-contract rule. A passing test over string assertions masks missing implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
