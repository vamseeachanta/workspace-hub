---
name: crossprovider codex internal-contradictions-between-pseudocode-and-f
description: Internal contradictions between pseudocode and Files-to-Change are red flags
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, internal-consistency, defect-class]
---

Plans describing 'remove fallback path' in one section while later saying 'add fallback path' in the implementation section create implementation ambiguity. Cross-check pseudocode, Files to Change, TDD list, and Acceptance sections for contradictory behavior. These become defect sources after implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
