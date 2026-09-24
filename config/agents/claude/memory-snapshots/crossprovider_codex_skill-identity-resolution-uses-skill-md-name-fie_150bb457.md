---
name: crossprovider codex skill-identity-resolution-uses-skill-md-name-fie
description: Skill identity resolution uses SKILL.md name: field
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skills-architecture, workspace-hub]
---

Canonical skill identity comes from the `name:` field in SKILL.md frontmatter, not the directory name. Directory-name fallback applies only when metadata is absent. This matters for skill-eval ranking and caching when nested skills use different naming conventions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
