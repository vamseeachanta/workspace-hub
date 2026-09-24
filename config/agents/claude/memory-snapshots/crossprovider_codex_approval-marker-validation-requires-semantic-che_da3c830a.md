---
name: crossprovider codex approval-marker-validation-requires-semantic-che
description: Approval marker validation requires semantic checks, not just existence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, testing, approval]
---

Existence of a `.planning/plan-approved/<issue>.md` file is insufficient for approval gate. Must validate non-empty approver name, valid commit SHA, matching plan path, and required review artifacts present. Empty fields, wrong issue numbers, invalid commits, or missing artifacts should fail validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
