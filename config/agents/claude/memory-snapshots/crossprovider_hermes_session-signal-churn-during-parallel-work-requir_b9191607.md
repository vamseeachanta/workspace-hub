---
name: crossprovider hermes session-signal-churn-during-parallel-work-requir
description: Session-signal churn during parallel work requires git history verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-agents, git-verification, post-push-validation]
---

Post-push verification must check git history (origin commit SHAs, reflog) not just file existence, because .claude/state/session-signals/ and similar state files receive churn from parallel agent sessions even after push succeeds. Verify handoff/commit SHA presence on origin, not file stat.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
