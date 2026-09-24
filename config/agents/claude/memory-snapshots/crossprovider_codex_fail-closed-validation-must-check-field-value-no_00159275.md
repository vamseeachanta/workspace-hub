---
name: crossprovider codex fail-closed-validation-must-check-field-value-no
description: Fail-closed validation must check field value, not just key presence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, testing, defect-class]
---

Checking key presence is insufficient for fail-closed contracts; null/empty/blank values can pass key-presence checks and bypass validation intent. Especially affects audit/provenance/gate fields where meaningful content is required, not just a key. Issue #2747 r1 and r2 both exposed null-value bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
