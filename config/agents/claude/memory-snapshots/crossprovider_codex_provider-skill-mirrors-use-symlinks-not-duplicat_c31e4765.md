---
name: crossprovider codex provider-skill-mirrors-use-symlinks-not-duplicat
description: Provider skill mirrors use symlinks, not duplication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skills-system, provider-architecture]
---

.codex/skills and .gemini/skills symlink to ./.claude/skills, not duplicate. Duplication creates sync hazards and cleanup debt during tooling migrations. Any skill-system changes must preserve these symlink relationships.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
