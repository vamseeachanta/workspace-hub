---
name: crossprovider codex skill-loader-enforces-64-char-max-on-name-frontm
description: Skill loader enforces 64-char max on `name:` frontmatter field
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [skill-loader, metadata-constraints, workspace-hub]
---

Skill metadata loader rejects skills where the frontmatter `name:` value exceeds 64 characters, causing 16 skills in workspace-hub to fail silent load. Folder names and headings can exceed 64 chars; only the frontmatter `name:` is constrained.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
