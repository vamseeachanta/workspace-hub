---
name: crossprovider codex approval-artifacts-need-schema-validation-at-cre
description: Approval artifacts need schema validation at creation time, not audit time
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, approval, schema, integrity]
---

WRK-188 evolved approval matrix to validate approver IDs against registry file with inline regex + sha256-based integrity checks; this pattern enforces policy compliance as artifacts are generated rather than after. Validation gates (identity checks, schema conformance, hash verification) at artifact-creation time prevent invalid/stale artifacts from entering the pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
