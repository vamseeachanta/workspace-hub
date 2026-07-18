---
name: crossprovider codex tdd-bounded-fix-agents-prevent-defect-propagatio
description: TDD-bounded fix agents prevent defect propagation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [defect-fix, tdd, code-review, testing]
---

When adversarial review identifies critical defects, dispatch a FRESH implementer agent with explicit narrow boundaries (e.g., 'no source-data access, no downstream schema/wiki write') rather than ad-hoc patching. Narrow scope ensures regression tests validate the actual fix and prevents defect chains from spreading downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
