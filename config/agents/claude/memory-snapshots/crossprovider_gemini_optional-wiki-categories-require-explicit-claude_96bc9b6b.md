---
name: crossprovider gemini optional-wiki-categories-require-explicit-claude
description: Optional wiki categories require explicit CLAUDE.md schema amendment
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [wiki-management, schema-governance, gitignore-patterns]
---

Creating a new wiki directory (e.g., `marine-engineering/wiki/standards/`) without adding it to the repo's `CLAUDE.md` schema definition silently invents an undocumented taxonomy. Lint and traversal tools may not recognize the new category. Amend schema first.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
