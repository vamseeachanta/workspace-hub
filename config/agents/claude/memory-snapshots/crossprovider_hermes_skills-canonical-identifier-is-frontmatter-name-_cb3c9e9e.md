---
name: crossprovider hermes skills-canonical-identifier-is-frontmatter-name-
description: Skills canonical identifier is frontmatter name, not filename
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills-ecosystem, governance, canonical-identity]
---

The `name:` field in skill SKILL.md frontmatter is the canonical identifier, not the file path. In v1 weekly audit, `_archive` and `_diverged` directories are excluded from main findings; `_core` and `_internal` are informational-only. v1 kept read-only (no automatic renames/archives) to avoid weekly churn and rename-chasing risk.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
