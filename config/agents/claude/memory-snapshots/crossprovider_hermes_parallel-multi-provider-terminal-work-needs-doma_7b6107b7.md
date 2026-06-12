---
name: crossprovider hermes parallel-multi-provider-terminal-work-needs-doma
description: Parallel multi-provider terminal work needs domain-based partitioning
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-provider, hermes-workflow, git-contention, parallel-agents]
---

Running 3 concurrent Hermes/Claude/Codex sessions on the same repo works best when each targets a different directory/domain to minimize git lock contention. Recommended split: Terminal 1 = high-context orchestration (scripts/monitoring/, cron/, logs/); Terminal 2 = bounded implementation (scripts/ai/, specific feature); Terminal 3 = audit/cleanup (.claude/skills/, .github/ISSUE_TEMPLATE/, docs/). Each completes independently and pushes without race conditions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
