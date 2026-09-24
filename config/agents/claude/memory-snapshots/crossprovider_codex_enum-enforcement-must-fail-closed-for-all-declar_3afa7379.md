---
name: crossprovider codex enum-enforcement-must-fail-closed-for-all-declar
description: Enum enforcement must fail-closed for all declared enum fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, schema-enforcement, fail-closed]
---

Only checking enum membership when the field exists (silently allowing missing enum fields) is not real enforcement. Declare which fields are required, check all required fields, and fail if any are missing or invalid. For thresholds, verify the actual count against the threshold, not just that the bucket is non-empty.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
