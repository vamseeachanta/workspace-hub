---
name: crossprovider codex approval-comment-validation-is-token-based-fragi
description: Approval comment validation is token-based, fragile
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [continuous-planning, validation, technical-debt]
---

`continuous-planning-pipeline.py:has_canonical_approval_comment()` requires specific token strings ('approve', 'revise', 'hold', 'execution remains unauthorized') rather than schema validation. Token-matching is brittle; future approval-comment work should prefer schema-backed validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
