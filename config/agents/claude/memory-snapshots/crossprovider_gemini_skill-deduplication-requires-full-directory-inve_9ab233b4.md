---
name: crossprovider gemini skill-deduplication-requires-full-directory-inve
description: Skill deduplication requires full directory inventory and cross-file reference cleanup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, deduplication, safety]
---

Audit tools report skill duplicates based on frontmatter name collisions, but safe deletion requires: (1) full directory inventory to capture auxiliary reference files beyond SKILL.md; (2) cross-file reference scan across .claude/agent-skills-map.yaml, registries, and config files. Deleting without this cleanup leaves orphaned references and abandoned documentation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
