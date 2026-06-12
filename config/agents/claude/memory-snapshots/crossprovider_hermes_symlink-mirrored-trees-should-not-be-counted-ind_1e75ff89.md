---
name: crossprovider hermes symlink-mirrored-trees-should-not-be-counted-ind
description: Symlink-mirrored trees should not be counted independently in audits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [auditing, symlinks, deduplication, metrics]
---

`.codex/skills` and `.gemini/skills` are symlink mirrors of `.claude/skills` — counting all three as independent inflates active-skill counts by 3×. Audit tools must detect and skip symlink mirrors, counting only the canonical tree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
