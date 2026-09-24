---
name: crossprovider codex skill-documentation-edits-don-t-enforce-runtime-
description: Skill documentation edits don't enforce runtime behavior when entrypoint is a hook or script
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-system-gap, enforcement, skill-execution-boundary]
---

Multiple reviews of WRK-691 flagged that editing SKILL.md files alone won't cause intended behaviors to execute if the actual runtime entrypoint is a hook (.claude/settings.json) or script (readiness.sh, comprehensive-learning.sh). Fixes targeting acceptance criteria must change the executable entrypoint, not just procedural guidance docs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
