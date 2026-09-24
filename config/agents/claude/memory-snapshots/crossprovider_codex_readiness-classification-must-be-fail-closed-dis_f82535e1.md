---
name: crossprovider codex readiness-classification-must-be-fail-closed-dis
description: Readiness classification must be fail-closed—dispatch:ready alone insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, classification-logic, safety]
---

Permissive gate labels like dispatch:ready should not yield 'ready' classification without explicit approval (status:plan-approved). Classification logic must have explicit tests for the case where a row is default-ready but lacks the approval marker—test should verify the row downgrades to needs-human-disposition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
