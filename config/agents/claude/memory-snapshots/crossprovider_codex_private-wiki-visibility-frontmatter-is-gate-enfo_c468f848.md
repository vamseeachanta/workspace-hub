---
name: crossprovider codex private-wiki-visibility-frontmatter-is-gate-enfo
description: Private-wiki visibility frontmatter is gate-enforced
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki-governance, frontmatter, gate-enforcement]
---

llm-wiki (and similar private wikis) enforce `visibility: private-llm-wiki` as a required YAML frontmatter field. Both content tests and pre-commit gates should check for its presence to prevent accidental public-facing assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
