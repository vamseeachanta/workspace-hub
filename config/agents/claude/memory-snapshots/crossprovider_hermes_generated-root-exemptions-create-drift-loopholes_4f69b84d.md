---
name: crossprovider hermes generated-root-exemptions-create-drift-loopholes
description: Generated-root exemptions create drift loopholes if not file-scoped
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, contract-design, generated-artifacts]
---

Exempting an entire directory like `results/` from repo-structure contract allows unlimited new tracked files within it without classification metadata, defeating the contract's goal of preventing new generated drift. File-level or path-pattern exception metadata is needed to whitelist specific tracked files, not entire directories.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
