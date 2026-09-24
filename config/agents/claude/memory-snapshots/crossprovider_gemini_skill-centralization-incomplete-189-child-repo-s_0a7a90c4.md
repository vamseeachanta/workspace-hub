---
name: crossprovider gemini skill-centralization-incomplete-189-child-repo-s
description: Skill centralization incomplete: 189 child-repo SKILL.md are local copies, not symlinks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skills-management, centralization, automation]
---

Local skill files in child repos break discoverability and reduce automation reliability. Centralized skills should be symlinked from .claude/skills/, not copied locally. This fragmentation reduces the effectiveness of skill-based routing and validation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
