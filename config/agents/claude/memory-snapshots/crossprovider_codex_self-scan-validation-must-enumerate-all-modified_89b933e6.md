---
name: crossprovider codex self-scan-validation-must-enumerate-all-modified
description: Self-scan validation must enumerate ALL modified public artifacts, not fixed sets
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [validation, public-artifacts, self-scan, completeness]
---

Plans that modify public documentation and skills need their self-scan validation to dynamically include all potentially-modified files, not static target lists. Conditional edits to public docs miss detection when fixed sets omit sibling plans/skills. Use structural registries (YAML/JSON) parsed by validators instead of prose-derived lists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
