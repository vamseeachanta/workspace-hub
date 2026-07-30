---
name: crossprovider codex artifact-dependency-chains-through-task-producti
description: Artifact dependency chains through task production must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [planning, dependencies, verification]
---

Implementation tasks must explicitly state what they produce (artifact paths) and what prior tasks they depend on. Missing productions or wrong inputs hide as implementation gaps. Verification evidence that reuses partial test suites can invalidate earlier gate results if code changed after the gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
