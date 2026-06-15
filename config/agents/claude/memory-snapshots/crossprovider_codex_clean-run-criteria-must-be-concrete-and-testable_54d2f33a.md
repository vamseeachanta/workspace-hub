---
name: crossprovider codex clean-run-criteria-must-be-concrete-and-testable
description: 'Clean run' criteria must be concrete and testable, not aspirational
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [automation-gates, acceptance-criteria, testing]
---

A gate like 'two clean runs before automation' is not actionable without explicit criteria: no extraction errors, no citation gaps, no private-source contamination, deterministic output writes, no duplicate entries, no broken links, successful security/legal scan. Define these as test assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
