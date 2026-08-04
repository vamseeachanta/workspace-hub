---
name: crossprovider codex durable-state-records-api-mutations-for-queues
description: Durable state records > API mutations for queues
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [dispatch, state-management, architecture]
---

Pull-based dispatch systems should back completion state with git-tracked records (schema: `started_at`, `finished_at`, `returncode`, `audit`), not GitHub label mutations. Label updates fail silently on API errors and carry no evidence; records survive and allow auditing. This pattern is proven in licensed-run queues (`deckhand-licensed-runs-queue/queue/results/`) and should apply to ordinary dispatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
