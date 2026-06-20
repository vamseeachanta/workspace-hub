---
name: crossprovider codex skills-catalog-regeneration-silently-breaks-tool
description: Skills catalog regeneration silently breaks tool discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [skills, tool-discovery, generated-config, validation]
---

Skill catalogs (e.g., `skills-catalog.json`) can shrink from 40 skills (762 lines) to 0 skills (4 lines) on regeneration without warning. An empty catalog breaks downstream tool discovery. Validate catalog content and test coverage before committing regenerated skill registries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
