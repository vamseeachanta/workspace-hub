---
name: crossprovider codex apply-test-driven-approach-to-validation-lane-fi
description: Apply test-driven approach to validation-lane fixes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, tdd]
---

When validation finds a small concrete issue on a `status:plan-approved` branch, add regression test first (expect red), run to confirm failure, then implement fix to make green. Keeps safety gates active even for follow-up changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
