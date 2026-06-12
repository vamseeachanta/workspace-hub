---
name: crossprovider hermes commit-classification-for-review-enforcement-con
description: Commit classification for review enforcement: conventional prefix rule
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-enforcement, commit-classification]
---

Commits starting with chore/docs/style/ci/test/build/revert/merge skip review; feat/fix/perf/refactor/security/untyped require it. Use this rule consistently in both require-review-on-push.sh (push-time gate) and review-audit.sh (daily audit).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
