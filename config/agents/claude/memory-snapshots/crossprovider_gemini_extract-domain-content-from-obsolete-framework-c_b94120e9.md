---
name: crossprovider gemini extract-domain-content-from-obsolete-framework-c
description: Extract domain content from obsolete framework configs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, refactoring, framework-deprecation]
---

Legacy framework-specific agent definitions (e.g., agent-os) contain valuable domain knowledge in markdown but obsolete framework configs (agent.yaml). Pattern: extract markdown to SKILL.md in hub, discard framework config. Reapply to any framework migration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
