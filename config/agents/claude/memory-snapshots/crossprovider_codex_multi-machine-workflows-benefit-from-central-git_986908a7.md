---
name: crossprovider codex multi-machine-workflows-benefit-from-central-git
description: Multi-machine workflows benefit from central git-synced orchestration
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-machine, git-sync, architecture, distributed-workflows]
---

Rather than P2P state sharing, a single coordinator machine that git-pulls state from contributors and runs centralized analysis (insights, learning, action planning) is simpler and avoids consensus/locking issues. Requires gitignored-exception entries for state dirs and re-derivation guards when analysis scripts change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
