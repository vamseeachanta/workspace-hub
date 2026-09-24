---
name: crossprovider codex test-fixtures-must-be-self-contained-or-explicit
description: Test fixtures must be self-contained or explicitly declared as external
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, acceptance-criteria]
---

Acceptance criteria claiming 'tests pass' when they actually fail due to missing external fixtures (e.g., `user-review-capture.yaml` for WRK IDs) indicates test harness is incomplete. Fixtures should be hermetic or test must document the external dependency and provide setup instructions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
