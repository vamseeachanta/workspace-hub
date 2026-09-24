---
name: crossprovider codex validation-commands-must-use-exact-file-paths-ne
description: Validation commands must use exact file paths, never placeholders
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, safety, specificity]
---

Validation commands in plan artifacts must spell out concrete paths (e.g., `docs/governance/sesa-extraction-clearance-checklist.md` not `<target-artifact>`). Placeholder validation is unsafe and blocks plan-review sign-off.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
