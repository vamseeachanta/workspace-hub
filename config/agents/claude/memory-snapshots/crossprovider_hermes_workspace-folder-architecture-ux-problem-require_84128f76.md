---
name: crossprovider hermes workspace-folder-architecture-ux-problem-require
description: Workspace folder architecture UX problem requires classified-then-deferred solution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monorepo-organization, agent-ux, architecture-design]
---

Agent/runtime folders mixing canonical source, generated artifacts, local symlinks, adapters, memory, skills, and cache confuse both humans and agents equally. Solution pattern: (1) inventory and classify surfaces by authority tier, (2) define explicit source-vs-runtime-vs-local rules, (3) defer implementation moves to follow-ups after approval. Incremental fixes prevent thrash.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
