---
name: crossprovider codex nested-git-repos-mask-sibling-checkouts
description: Nested git repos mask sibling checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [repo-structure, git, governance]
---

Direct nested git repos under a control-plane root (e.g., `workspace-hub/.../acma-projects`) hide sibling checkouts at the parent level and create ambiguity about whether a repo is managed or abandoned. They must be completely eliminated. #2766 required explicit inventory of 'ghost repos' moved to siblings (acma-projects, client_projects, etc.) to prevent re-nesting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
