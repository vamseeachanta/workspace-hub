---
name: crossprovider hermes skill-loading-refuses-to-disambiguate-duplicate-
description: Skill loading refuses to disambiguate duplicate paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-management, duplicate-resolution]
---

When same skill exists in both `/home/vamsee/.hermes/skills/` and `/mnt/local-analysis/workspace-hub/.claude/skills/`, skill_view tool refuses to guess and returns ambiguity error. Requires user to resolve duplicates or use full explicit path. Consolidate or remove one copy to unblock.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
