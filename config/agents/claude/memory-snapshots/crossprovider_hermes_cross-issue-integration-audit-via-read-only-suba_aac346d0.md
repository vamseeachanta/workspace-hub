---
name: crossprovider hermes cross-issue-integration-audit-via-read-only-suba
description: Cross-issue integration audit via read-only subagent waves before parallel execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-issue-audit, integration-risk, parallel-execution]
---

Before dispatching parallel issue execution across workstreams, run read-only subagent waves to audit shared files, dependencies, approval-marker presence, and gate blockers. Example: Hermes audited #2738/#2739/#2741/#2742 vs. #2728/#2729 for contention, dependencies, and approval mismatches before orchestrating execution. **Why:** parallel git/approval conflicts, unresolved dependencies, and approval divergence cause silent failures or reverts. **How to apply:** create subagent audit tasks listing issues to check; gather live GitHub state, local plan/marker, review verdicts; return blockers + integration risks; orchestrator synthesizes results before dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
