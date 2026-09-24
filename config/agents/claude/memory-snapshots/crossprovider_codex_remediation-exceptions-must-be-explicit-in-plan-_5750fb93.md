---
name: crossprovider codex remediation-exceptions-must-be-explicit-in-plan-
description: Remediation exceptions must be explicit in plan and acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [remediation, acceptance-criteria, exceptions]
---

When a fix path has a fallback (e.g., version-pinned install unavailable, so use current channel), define the exception explicitly in both the implementation plan and acceptance criteria. Log exceptions and reclassify remaining drift severity accordingly (BLOCK → WARN).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
