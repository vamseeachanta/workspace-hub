---
name: crossprovider gemini canonical-evidence-predicate-as-single-source-of
description: Canonical evidence predicate as single source of truth
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [code-architecture, gate-enforcement, DRY]
---

Gate logic re-implemented in multiple places (shell scripts, Python validators, skill text) diverges; implement once in a shared helper and call it consistently from all official entrypoints. Define required YAML field sets and validation rules explicitly, not prose-only.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
