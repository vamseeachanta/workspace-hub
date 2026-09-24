---
name: crossprovider gemini audit-role-differentiation-before-merging-parall
description: Audit role differentiation before merging parallel hierarchies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring-heuristic, code-audit, role-verification]
---

When two similar-named directories exist, verify their role through evidence (import patterns, loading methods, file formats) before merging. Different purposes justify separation even if naming suggests redundancy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
