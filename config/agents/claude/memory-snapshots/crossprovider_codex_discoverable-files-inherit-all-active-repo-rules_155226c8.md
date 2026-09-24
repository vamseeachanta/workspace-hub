---
name: crossprovider codex discoverable-files-inherit-all-active-repo-rules
description: Discoverable files inherit all active repo rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-scope, rule-inheritance, discovery-hazard]
---

When frontmatter normalization makes a previously-skipped/dormant file discoverable, it becomes immediately subject to all active repo enforcement rules (e.g., Python runtime policy requiring `uv run`, not bare `python3`). Hidden technical debt surfaces at discovery time. Scope a task as "make discoverable" only after the file is rule-compliant.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
