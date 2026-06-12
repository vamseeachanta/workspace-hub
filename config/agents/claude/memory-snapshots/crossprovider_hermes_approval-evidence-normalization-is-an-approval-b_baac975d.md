---
name: crossprovider hermes approval-evidence-normalization-is-an-approval-b
description: Approval evidence normalization is an approval-blocking governance fork
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-design, approval-normalization, blocking-decision]
---

When approval can come from either 'revision-bound comment on PR' OR 'local committed marker' OR 'GitHub label', operators will disagree on which issues are safe. This is not a documentation problem; it's a control-plane correctness hazard. Choose ONE authoritative approval source and enforce it in all gates, hooks, and classifiers. Mixed modes invite split-brain execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
