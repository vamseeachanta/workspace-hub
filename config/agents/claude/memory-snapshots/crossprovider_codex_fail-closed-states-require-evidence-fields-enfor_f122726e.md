---
name: crossprovider codex fail-closed-states-require-evidence-fields-enfor
description: Fail-closed states require evidence fields enforced at validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, state-machine, blockers]
---

Status enums for fail-closed states (blocked, manual, gated) can pass validation even if evidence/blocker notes are empty. Validators must reject these states without populated evidence fields to prevent silent regressions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
