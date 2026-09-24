---
name: crossprovider codex skill-loader-enforces-64-character-name-limit
description: Skill loader enforces 64-character name limit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skill-loader, system-constraints]
---

The `.claude/skills/` loader rejects `name:` fields in SKILL.md frontmatter exceeding 64 characters, causing silent load failures across the skill tree. Safe fix: drop redundant parent prefixes and abbreviate long terms (`example-1` → `ex1`, `post-processing` → `postproc`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
