---
name: crossprovider codex fallback-to-known-buggy-code-path-invalidates-co
description: Fallback to known-buggy code path invalidates correctness deliverables and must be rejected
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, plan-review, backward-compatibility, safety-gate]
---

Plans proposing compatibility fallback to a previously-identified buggy code path reintroduce the original defect and fail stated deliverables (e.g., 'reliably dispatch without hanging'). Such fallbacks must be rejected at plan review; they are not acceptable technical debt or deferrable fixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
