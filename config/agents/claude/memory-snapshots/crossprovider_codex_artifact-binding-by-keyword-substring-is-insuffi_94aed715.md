---
name: crossprovider codex artifact-binding-by-keyword-substring-is-insuffi
description: Artifact binding by keyword substring is insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [traceability, binding, multi-phase-planning, test-coverage]
---

Accepting references that contain keywords like 'validator' or '.py' doesn't bind to actual files or create wave-specific traceability. Plans claim TDD without validators existing. Instead: validate path existence, require issue-specific uniqueness, fail if referenced files don't exist in the working tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
