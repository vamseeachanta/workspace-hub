---
name: crossprovider codex approval-marker-format-inconsistencies-cause-par
description: Approval marker format inconsistencies cause parser rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-workflow, parser-validation, config-format]
---

When a marker parser expects inline `Key: value` but the configured format uses bullet-list items under `Key:`, the structural parser fails while informal scanning succeeds in CI. This causes valid markers to be rejected by validators while passing workflow scans. Validate format once, document it, and use consistent parser expectations across CLI and workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
